"""Private worker process; no model-supplied code or source file operations."""

import json
import sys


def main():
    try:
        import resource

        resource.setrlimit(resource.RLIMIT_CPU, (10, 10))
        resource.setrlimit(resource.RLIMIT_AS, (512 * 1024 * 1024, 512 * 1024 * 1024))
    except ImportError:
        pass  # Parent timeout/output limits still apply on non-POSIX platforms.
    from astra_pcb.verifier.catalog import execute

    request = json.loads(sys.stdin.read(1024 * 1024 + 1))
    try:
        report = execute(request["name"], request["arguments"])
        print(report.model_dump_json())
    except Exception as exc:
        from astra_pcb.models import CheckResult, VerificationReport

        print(
            VerificationReport(
                results=(
                    CheckResult(
                        check_id="verifier.error",
                        name="Input/check error",
                        status="ERROR",
                        message=type(exc).__name__ + ": " + str(exc)[:1000],
                    ),
                )
            ).model_dump_json()
        )


if __name__ == "__main__":
    main()
