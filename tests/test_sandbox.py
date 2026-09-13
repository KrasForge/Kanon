import json
import shutil

import pytest

from astra_pcb.agents.sandbox import isolated_call


@pytest.mark.integration
def test_reviewer_os_denies_writes_credentials_network_and_exec(tmp_path, monkeypatch):
    if not shutil.which("bwrap"):
        pytest.skip("Required Linux bubblewrap unavailable")
    evidence = tmp_path / "evidence"
    evidence.mkdir()
    (evidence / "board.txt").write_text("Frozen source")
    worker = tmp_path / "review.py"
    worker.write_text("""import json,os,socket,subprocess
from pathlib import Path
checks={"secret_absent": "KANON_TEST_SECRET" not in os.environ,
"read": Path("/evidence/board.txt").read_text()=="Frozen source"}
for name, operation in {
"write": lambda: Path("/evidence/board.txt").write_text("mutated"),
"network": lambda: socket.socket(),
"exec": lambda: subprocess.run(["/runtime/bin/python", "-c", "print(1)"]),
"home": lambda: Path("/home/ik/.ssh").iterdir().__next__(),
}.items():
 try: operation(); checks[name]=False
 except OSError: checks[name]=True
print(json.dumps(checks))
""")
    monkeypatch.setenv("KANON_TEST_SECRET", "must not reach reviewer")
    result = isolated_call(worker, {}, evidence=evidence)
    assert result.exit_code == 0, result.stderr
    assert all(json.loads(result.stdout).values())
    assert (evidence / "board.txt").read_text() == "Frozen source"


def test_reviewer_missing_isolation_has_no_fallback(tmp_path, monkeypatch):
    monkeypatch.setattr("astra_pcb.agents.sandbox.shutil.which", lambda _: None)
    result = isolated_call(tmp_path / "absent.py", {})
    assert result.error and result.exit_code is None


def test_unreadable_mutation_preserves_structured_failure(tmp_path):
    from pathlib import Path

    from astra_pcb.kicad.workflow import mutate_verify

    source = tmp_path / "board.kicad_pcb"
    source.write_text("(kicad_pcb (version 20260101))")
    result = mutate_verify(tmp_path, (Path(source.name),), "test", source.unlink, tmp_path / "out")
    assert result.after is None and result.prior_evidence_invalidated
    assert result.verification.exit_code == 1
    assert (tmp_path / "out/verification.json").is_file()
    source.write_text("(kicad_pcb)")
    result = mutate_verify(
        tmp_path,
        (Path(source.name),),
        "test",
        lambda: source.write_text("(broken"),
        tmp_path / "out2",
    )
    assert result.after is None and result.verification.results[0].status == "ERROR"
