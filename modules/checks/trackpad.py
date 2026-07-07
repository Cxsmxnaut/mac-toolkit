"""Trackpad diagnostic check."""

from ..utils.base import BaseCheck, CheckResult, Status
from ..utils.macos import run_command_output


class TrackpadCheck(BaseCheck):
    """Check built-in or connected trackpad detection."""

    def run(self) -> CheckResult:
        output = run_command_output("ioreg -l | grep -Ei 'Trackpad|Multitouch' | head -10") or ""
        if output:
            return CheckResult(
                name="Trackpad",
                status=Status.PASS,
                details="Trackpad or multitouch device detected",
                recommendation="Verify gestures and click response in System Settings",
                metadata={"raw": output},
            )

        return CheckResult(
            name="Trackpad",
            status=Status.UNKNOWN,
            details="No trackpad device detected",
            recommendation="Expected on desktops; verify hardware on portable Macs",
        )
