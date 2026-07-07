"""Time synchronization diagnostic check."""

from ..utils.base import BaseCheck, CheckResult, Status
from ..utils.macos import run_command_output


class TimeSyncCheck(BaseCheck):
    """Check macOS network time configuration."""

    def run(self) -> CheckResult:
        enabled = run_command_output("systemsetup -getusingnetworktime 2>/dev/null") or ""
        server = run_command_output("systemsetup -getnetworktimeserver 2>/dev/null") or ""

        if "on" in enabled.lower():
            return CheckResult(
                name="Time Sync",
                status=Status.PASS,
                details=f"{enabled}; {server}",
                recommendation="Network time is enabled",
            )

        return CheckResult(
            name="Time Sync",
            status=Status.WARNING,
            details=enabled or "Network time status unavailable",
            recommendation="Enable network time to avoid certificate and update issues",
        )
