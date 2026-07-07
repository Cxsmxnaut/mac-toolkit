"""Basic internet latency diagnostic check."""

from ..utils.base import BaseCheck, CheckResult, Status
from ..utils.macos import run_command


class InternetSpeedCheck(BaseCheck):
    """Estimate internet quality using latency, avoiding external dependencies."""

    def run(self) -> CheckResult:
        ok, stdout, _ = run_command("ping -c 5 -q apple.com", timeout=10, use_shell=True)
        if not ok:
            return CheckResult(
                name="Internet Speed",
                status=Status.WARNING,
                details="Latency probe failed",
                recommendation="Verify internet access before running updates or downloads",
            )

        summary = next((line for line in stdout.splitlines() if "round-trip" in line), stdout)
        return CheckResult(
            name="Internet Speed",
            status=Status.PASS,
            details=summary,
            recommendation="Latency probe completed successfully",
        )
