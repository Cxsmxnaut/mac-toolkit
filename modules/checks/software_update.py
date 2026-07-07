"""Software Update diagnostic check."""

import subprocess
from ..utils.base import BaseCheck, CheckResult, Status


class SoftwareUpdateCheck(BaseCheck):
    """Check for available software updates."""
    
    def run(self) -> CheckResult:
        """Run software update diagnostic check.
        
        Returns:
            CheckResult with software update information
        """
        try:
            update_status = subprocess.check_output(
                "softwareupdate -l",
                shell=True,
                text=True,
                stderr=subprocess.DEVNULL
            ).strip()
            
            if update_status:
                if "No new updates available" in update_status or "found" not in update_status.lower():
                    return CheckResult(
                        name="Software Updates",
                        status=Status.PASS,
                        details="System is up to date",
                        recommendation="No software updates available"
                    )
                else:
                    # Count available updates
                    update_count = update_status.count("*")
                    return CheckResult(
                        name="Software Updates",
                        status=Status.WARNING,
                        details=f"{update_count} update(s) available",
                        recommendation="Install available software updates for security and performance"
                    )
            else:
                return CheckResult(
                    name="Software Updates",
                    status=Status.PASS,
                    details="System is up to date",
                    recommendation="No software updates available"
                )
        except subprocess.CalledProcessError:
            return CheckResult(
                name="Software Updates",
                status=Status.WARNING,
                details="Unknown",
                recommendation="Could not check for software updates"
            )
