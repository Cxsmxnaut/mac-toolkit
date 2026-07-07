"""FileVault diagnostic check."""

import subprocess
from ..utils.base import BaseCheck, CheckResult, Status


class FileVaultCheck(BaseCheck):
    """Check FileVault encryption status."""
    
    def run(self) -> CheckResult:
        """Run FileVault diagnostic check.
        
        Returns:
            CheckResult with FileVault information
        """
        try:
            filevault_status = subprocess.check_output(
                "fdesetup status",
                shell=True,
                text=True,
                stderr=subprocess.DEVNULL
            ).strip()
            
            if filevault_status:
                status_lower = filevault_status.lower()
                
                if "on" in status_lower or "encrypted" in status_lower:
                    return CheckResult(
                        name="FileVault",
                        status=Status.PASS,
                        details="FileVault is enabled",
                        recommendation="FileVault encryption is active"
                    )
                elif "off" in status_lower or "not encrypted" in status_lower:
                    return CheckResult(
                        name="FileVault",
                        status=Status.WARNING,
                        details="FileVault is disabled",
                        recommendation="Consider enabling FileVault for security"
                    )
                else:
                    return CheckResult(
                        name="FileVault",
                        status=Status.PASS,
                        details=filevault_status,
                        recommendation="FileVault status verified"
                    )
            else:
                return CheckResult(
                    name="FileVault",
                    status=Status.WARNING,
                    details="Unknown",
                    recommendation="Could not determine FileVault status"
                )
        except subprocess.CalledProcessError:
            return CheckResult(
                name="FileVault",
                status=Status.WARNING,
                details="Unknown",
                recommendation="Could not retrieve FileVault information"
            )
