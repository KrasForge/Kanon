"""Verification utilities; domain checks must register real implementations."""

from astra_pcb.models import CheckResult, CheckStatus


def unavailable(check_id: str) -> CheckResult:
    return CheckResult(
        check_id=check_id,
        name=check_id,
        status=CheckStatus.SKIP,
        message="Not implemented; no engineering conclusion available",
        remediation="Implement and validate the corresponding backlog issue",
    )
