"""RAM diagnostic check."""

import subprocess
from ..utils.base import BaseCheck, CheckResult, Status


class RAMCheck(BaseCheck):
    """Check RAM information and status."""
    
    def run(self) -> CheckResult:
        """Run RAM diagnostic check.
        
        Returns:
            CheckResult with RAM information
        """
        try:
            ram = subprocess.check_output(
                "sysctl -n hw.memsize",
                shell=True,
                text=True,
                stderr=subprocess.DEVNULL
            ).strip()
            ram_gb = round(int(ram) / 1024 / 1024 / 1024)
            
            return CheckResult(
                name="RAM",
                status=Status.PASS,
                details=f"{ram_gb} GB",
                recommendation="RAM is functioning normally"
            )
        except (subprocess.CalledProcessError, ValueError) as e:
            return CheckResult(
                name="RAM",
                status=Status.WARNING,
                details="Unknown",
                recommendation=f"Could not determine RAM size: {str(e)}"
            )
