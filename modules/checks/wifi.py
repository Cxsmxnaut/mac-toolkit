"""Wi-Fi diagnostic check."""

from ..utils.base import BaseCheck, CheckResult, Status
from ..utils.macos import get_wifi_interface, run_command_output


class WiFiCheck(BaseCheck):
    """Check Wi-Fi status and connectivity."""
    
    def run(self) -> CheckResult:
        """Run Wi-Fi diagnostic check.
        
        Returns:
            CheckResult with Wi-Fi information
        """
        interface = get_wifi_interface()
        wifi_power = run_command_output(f"networksetup -getairportpower {interface}")

        if not wifi_power:
            return CheckResult(
                name="Wi-Fi",
                status=Status.WARNING,
                details=f"Could not read Wi-Fi power on {interface}",
                recommendation="Verify Wi-Fi hardware and post-install root patches"
            )

        if "on" in wifi_power.lower():
            wifi_info = run_command_output(f"networksetup -getairportnetwork {interface}") or ""
            if wifi_info and "not associated" not in wifi_info.lower():
                return CheckResult(
                    name="Wi-Fi",
                    status=Status.PASS,
                    details=f"{interface}: {wifi_info}",
                    recommendation="Wi-Fi is functioning normally"
                )
            return CheckResult(
                name="Wi-Fi",
                status=Status.WARNING,
                details=f"{interface}: Wi-Fi is on but not connected",
                recommendation="Connect to a Wi-Fi network and verify continuity features if needed"
            )

        return CheckResult(
            name="Wi-Fi",
            status=Status.WARNING,
            details=f"{interface}: Wi-Fi is turned off",
            recommendation="Enable Wi-Fi if needed"
        )
