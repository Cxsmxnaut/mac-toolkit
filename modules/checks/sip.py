"""SIP (System Integrity Protection) diagnostic check."""

import subprocess
from ..utils.base import BaseCheck, CheckResult, Status


class SIPCheck(BaseCheck):
    """Check System Integrity Protection status."""
    
    def run(self) -> CheckResult:
        """Run SIP diagnostic check.
        
        Returns:
            CheckResult with SIP information
        """
        try:
            sip_status = subprocess.check_output(
                "csrutil status",
                shell=True,
                text=True,
                stderr=subprocess.DEVNULL
            ).strip()
            
            if sip_status:
                status_lower = sip_status.lower()
                
                if "enabled" in status_lower:
                    return CheckResult(
                        name="SIP",
                        status=Status.PASS,
                        details="System Integrity Protection is enabled",
                        recommendation="SIP is properly configured for security"
                    )
                elif "disabled" in status_lower:
                    return CheckResult(
                        name="SIP",
                        status=Status.WARNING,
                        details="System Integrity Protection is disabled",
                        recommendation="Consider re-enabling SIP for security unless required for specific software"
                    )
                else:
                    return CheckResult(
                        name="SIP",
                        status=Status.PASS,
                        details=sip_status,
                        recommendation="SIP status verified"
                    )
            else:
                return CheckResult(
                    name="SIP",
                    status=Status.WARNING,
                    details="Unknown",
                    recommendation="Could not determine SIP status"
                )
        except subprocess.CalledProcessError:
            return CheckResult(
                name="SIP",
                status=Status.WARNING,
                details="Unknown",
                recommendation="Could not retrieve SIP information"
            )
