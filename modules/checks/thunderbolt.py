"""Thunderbolt diagnostic check."""

from ..utils.base import BaseCheck, CheckResult, Status
from ..utils.macos import run_command_output


class ThunderboltCheck(BaseCheck):
    """Check Thunderbolt controller and devices."""

    def run(self) -> CheckResult:
        output = run_command_output("system_profiler SPThunderboltDataType")
        if not output:
            return CheckResult(
                name="Thunderbolt",
                status=Status.UNKNOWN,
                details="Thunderbolt information unavailable",
                recommendation="This Mac may not have Thunderbolt",
            )

        if "No Thunderbolt" in output or "not connected" in output.lower():
            return CheckResult(
                name="Thunderbolt",
                status=Status.PASS,
                details="Thunderbolt controller present, no devices connected",
                recommendation="Thunderbolt bus is healthy",
            )

        devices = [
            line.split(":", 1)[1].strip()
            for line in output.splitlines()
            if "Device Name:" in line or "Vendor Name:" in line
        ]

        return CheckResult(
            name="Thunderbolt",
            status=Status.PASS,
            details=f"{len(devices)} Thunderbolt device(s) detected",
            recommendation="Thunderbolt subsystem is responding",
            metadata={"devices": devices},
        )
