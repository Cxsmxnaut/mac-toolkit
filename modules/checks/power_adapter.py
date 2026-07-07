"""Power adapter diagnostic check."""

from ..utils.base import BaseCheck, CheckResult, Status
from ..utils.macos import device_has_battery, get_power_adapter_status


class PowerAdapterCheck(BaseCheck):
    """Check power adapter and AC power status."""

    def run(self) -> CheckResult:
        output = get_power_adapter_status()
        if not output:
            return CheckResult(
                name="Power Adapter",
                status=Status.UNKNOWN,
                details="Could not read power adapter status",
                recommendation="Verify power connection manually",
            )

        has_battery = device_has_battery()
        connected = "connected" in output.lower() or "drawing from" in output.lower()

        if not has_battery:
            return CheckResult(
                name="Power Adapter",
                status=Status.PASS,
                details=output,
                recommendation="Desktop Mac — AC power assumed",
            )

        if connected:
            status = Status.PASS
            recommendation = "Power adapter is connected"
        else:
            status = Status.WARNING
            recommendation = "Power adapter not detected — connect AC power for diagnostics"

        return CheckResult(
            name="Power Adapter",
            status=status,
            details=output,
            recommendation=recommendation,
        )
