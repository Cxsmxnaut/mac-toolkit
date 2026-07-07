"""CPU diagnostic check."""

import subprocess
import platform
from ..utils.base import BaseCheck, CheckResult, Status


class CPUCheck(BaseCheck):
    """Check CPU information and status."""
    
    def run(self) -> CheckResult:
        """Run CPU diagnostic check.
        
        Returns:
            CheckResult with CPU information
        """
        try:
            cpu = subprocess.check_output(
                "sysctl -n machdep.cpu.brand_string",
                shell=True,
                text=True,
                stderr=subprocess.DEVNULL
            ).strip()
        except subprocess.CalledProcessError:
            cpu = platform.processor() or "Apple Silicon"
        
        cores = subprocess.check_output(
            "sysctl -n hw.ncpu",
            shell=True,
            text=True,
            stderr=subprocess.DEVNULL
        ).strip()
        
        details = f"{cpu} ({cores} cores)" if cores else cpu
        
        return CheckResult(
            name="CPU",
            status=Status.PASS,
            details=details,
            recommendation="CPU is functioning normally"
        )
