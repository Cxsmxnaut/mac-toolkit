"""APFS diagnostic check."""

import subprocess
from ..utils.base import BaseCheck, CheckResult, Status


class APFSCheck(BaseCheck):
    """Check APFS filesystem status."""
    
    def run(self) -> CheckResult:
        """Run APFS diagnostic check.
        
        Returns:
            CheckResult with APFS information
        """
        try:
            apfs_info = subprocess.check_output(
                "diskutil apfs list",
                shell=True,
                text=True,
                stderr=subprocess.DEVNULL
            ).strip()
            
            if apfs_info:
                # Check for any error indicators in the output
                if "error" in apfs_info.lower() or "corrupt" in apfs_info.lower():
                    return CheckResult(
                        name="APFS",
                        status=Status.FAIL,
                        details="APFS errors detected",
                        recommendation="Run Disk Utility First Aid immediately"
                    )
                
                return CheckResult(
                    name="APFS",
                    status=Status.PASS,
                    details="APFS filesystem is healthy",
                    recommendation="APFS is functioning normally"
                )
            else:
                return CheckResult(
                    name="APFS",
                    status=Status.WARNING,
                    details="Could not retrieve APFS information",
                    recommendation="APFS information not available"
                )
        except subprocess.CalledProcessError:
            return CheckResult(
                name="APFS",
                status=Status.WARNING,
                details="Unknown",
                recommendation="Could not retrieve APFS information"
            )
