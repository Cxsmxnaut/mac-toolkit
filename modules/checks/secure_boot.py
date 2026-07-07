"""Secure Boot diagnostic check."""

import subprocess
from ..utils.base import BaseCheck, CheckResult, Status


class SecureBootCheck(BaseCheck):
    """Check Secure Boot status."""
    
    def run(self) -> CheckResult:
        """Run Secure Boot diagnostic check.
        
        Returns:
            CheckResult with Secure Boot information
        """
        try:
            secure_boot_status = subprocess.check_output(
                "bputil -d",
                shell=True,
                text=True,
                stderr=subprocess.DEVNULL
            ).strip()
            
            if secure_boot_status:
                status_lower = secure_boot_status.lower()
                
                if "enabled" in status_lower or "full" in status_lower:
                    return CheckResult(
                        name="Secure Boot",
                        status=Status.PASS,
                        details="Secure Boot is enabled",
                        recommendation="Secure Boot is properly configured for security"
                    )
                elif "disabled" in status_lower or "no security" in status_lower:
                    return CheckResult(
                        name="Secure Boot",
                        status=Status.WARNING,
                        details="Secure Boot is disabled",
                        recommendation="Consider enabling Secure Boot for security"
                    )
                else:
                    return CheckResult(
                        name="Secure Boot",
                        status=Status.PASS,
                        details=secure_boot_status,
                        recommendation="Secure Boot status verified"
                    )
            else:
                return CheckResult(
                    name="Secure Boot",
                    status=Status.WARNING,
                    details="Unknown",
                    recommendation="Could not determine Secure Boot status (may not be supported on this Mac)"
                )
        except subprocess.CalledProcessError:
            return CheckResult(
                name="Secure Boot",
                status=Status.WARNING,
                details="Unknown",
                recommendation="Could not retrieve Secure Boot information (may not be supported on this Mac)"
            )
