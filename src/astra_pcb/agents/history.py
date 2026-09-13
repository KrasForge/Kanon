"""Append-only review history with continuity and repeated-blocker stop policy."""

import fcntl
import json
import os
from pathlib import Path

from astra_pcb.agents.review import reconcile
from astra_pcb.models import CheckResult
from astra_pcb.models.engineering import Review
from astra_pcb.models.provenance import canonical_digest


class ReviewHistory:
    def __init__(self, path: Path, design_author: str, *, maximum_blocked_iterations: int = 3):
        if maximum_blocked_iterations < 1:
            raise ValueError("Positive iteration limit required")
        self.path, self.design_author, self.limit = path, design_author, maximum_blocked_iterations

    def append(self, review: Review) -> CheckResult:
        if review.reviewer == self.design_author:
            raise ValueError("Designer cannot resolve own review")
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a+") as stream:
            fcntl.flock(stream.fileno(), fcntl.LOCK_EX)
            stream.seek(0)
            entries = [json.loads(line) for line in stream if line.strip()]
            previous = "0" * 64
            consecutive = {}
            prior = None
            for entry in entries:
                if entry["previous"] != previous or entry["digest"] != canonical_digest(
                    {k: v for k, v in entry.items() if k != "digest"}
                ):
                    raise ValueError("Review history tampered or out of order")
                prior = Review.model_validate(entry["review"])
                previous = entry["digest"]
                open_ids = {
                    f.id
                    for f in prior.findings
                    if f.severity in {"blocker", "major"} and f.status != "resolved"
                }
                consecutive = {key: consecutive.get(key, 0) + 1 for key in open_ids}
            if prior:
                reconcile(prior, review, self.design_author)
            open_ids = {
                f.id
                for f in review.findings
                if f.severity in {"blocker", "major"} and f.status != "resolved"
            }
            consecutive = {key: consecutive.get(key, 0) + 1 for key in open_ids}
            stopped = any(count >= self.limit for count in consecutive.values())
            entry = {
                "previous": previous,
                "review": review.model_dump(mode="json"),
                "stop": stopped,
            }
            entry["digest"] = canonical_digest(entry)
            stream.write(json.dumps(entry, sort_keys=True) + "\n")
            stream.flush()
            os.fsync(stream.fileno())
        return CheckResult(
            check_id="review.iteration",
            name="Review/remediation iteration policy",
            status="FAIL" if stopped else "WARN" if review.has_blockers else "PASS",
            message="Stop automatic remediation: repeated unresolved blockers require escalation"
            if stopped
            else "Review iteration retained; unresolved findings require remediation"
            if review.has_blockers
            else "Review iteration retained",
            evidence=(entry["digest"], json.dumps(consecutive)),
            affected_objects=tuple(sorted(open_ids)),
        )
