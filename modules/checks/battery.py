"""Battery diagnostic check."""

import subprocess
import re
from ..utils.base import BaseCheck, CheckResult, Status


class BatteryCheck(BaseCheck):
    """Check battery information and health."""
    
    def run(self) -> CheckResult:
        """Run battery diagnostic check.
        
        Returns:
            CheckResult with battery information
        """
        try:
            battery = subprocess.check_output(
                "pmset -g batt",
                shell=True,
                text=True,
                stderr=subprocess.DEVNULL
            ).strip()
            
            # Extract battery percentage and health
            match = re.search(r'(\d+)%', battery)
            if match:
                percentage = int(match.group(1))
                status = Status.PASS
                recommendation = "Battery is functioning normally"
                
                if percentage < 10:
                    status = Status.FAIL
                    recommendation = "Battery charge is critically low"
                elif percentage < 20:
                    status = Status.WARNING
                    recommendation = "Battery charge is low"
            else:
                status = Status.WARNING
                recommendation = "Could not determine battery percentage"
            
            return CheckResult(
                name="Battery",
                status=status,
                details=battery,
                recommendation=recommendation
            )
        except subprocess.CalledProcessError:
            return CheckResult(
                name="Battery",
                status=Status.WARNING,
                details="Unavailable",
                recommendation="Battery information not available (desktop Mac?)"
            )
