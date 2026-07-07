"""USB device diagnostic check."""

from ..utils.base import BaseCheck, CheckResult, Status
from ..utils.macos import run_command_output


class USBCheck(BaseCheck):
    """Check USB bus and connected devices."""

    def run(self) -> CheckResult:
        output = run_command_output("system_profiler SPUSBDataType")
        if not output:
            return CheckResult(
                name="USB",
                status=Status.WARNING,
                details="USB information unavailable",
                recommendation="Check USB controller in System Information",
            )

        devices = [
            line.split(":", 1)[1].strip()
            for line in output.splitlines()
            if line.strip().startswith("Product ID:")
        ]
        device_count = len(devices)

        status = Status.PASS
        recommendation = "USB subsystem is responding"
        if "No USB device" in output or device_count == 0:
            status = Status.PASS
            recommendation = "No USB devices connected — bus appears healthy"

        return CheckResult(
            name="USB",
            status=status,
            details=f"{device_count} USB device(s) detected",
            recommendation=recommendation,
            metadata={"device_count": device_count},
        )
