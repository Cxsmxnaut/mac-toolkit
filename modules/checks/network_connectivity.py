"""Network connectivity diagnostic check."""

from ..utils.base import BaseCheck, CheckResult, Status
from ..utils.macos import run_command


class NetworkConnectivityCheck(BaseCheck):
    """Verify default gateway and internet reachability."""

    def run(self) -> CheckResult:
        gateway_ok, gateway, _ = run_command("route -n get default | awk '/gateway/ {print $2}'", use_shell=True)
        internet_ok, _, _ = run_command(["ping", "-c", "2", "-W", "1000", "1.1.1.1"], timeout=5)

        if internet_ok:
            return CheckResult(
                name="Network Connectivity",
                status=Status.PASS,
                details=f"Internet reachable; gateway: {gateway if gateway_ok else 'unknown'}",
                recommendation="Network connectivity is functioning normally",
            )

        return CheckResult(
            name="Network Connectivity",
            status=Status.FAIL if gateway_ok else Status.WARNING,
            details=f"Internet ping failed; gateway: {gateway if gateway_ok else 'not detected'}",
            recommendation="Verify Wi-Fi/Ethernet, DHCP, DNS, and captive portal status",
        )
