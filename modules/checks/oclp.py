"""OpenCore Legacy Patcher detection diagnostic check."""

import subprocess
from pathlib import Path
from ..utils.base import BaseCheck, CheckResult, Status


class OCLPCheck(BaseCheck):
    """Check for OpenCore Legacy Patcher installation."""
    
    def run(self) -> CheckResult:
        """Run OCLP detection check.
        
        Returns:
            CheckResult with OCLP information
        """
        # Check for OCLP installation
        oclp_path = Path("/usr/local/bin/opencore-legacy-patcher")
        
        if oclp_path.exists():
            try:
                version = subprocess.check_output(
                    "/usr/local/bin/opencore-legacy-patcher --version",
                    shell=True,
                    text=True,
                    stderr=subprocess.DEVNULL
                ).strip()
                
                return CheckResult(
                    name="OpenCore Legacy Patcher",
                    status=Status.PASS,
                    details=f"Installed: {version}",
                    recommendation="OCLP is installed - ensure it is kept up to date"
                )
            except subprocess.CalledProcessError:
                return CheckResult(
                    name="OpenCore Legacy Patcher",
                    status=Status.WARNING,
                    details="Installed but version unknown",
                    recommendation="OCLP is installed but version could not be determined"
                )
        else:
            # Check for EFI partition (indicator of OCLP or similar boot loader)
            try:
                efi_check = subprocess.check_output(
                    "diskutil info disk0 | grep EFI",
                    shell=True,
                    text=True,
                    stderr=subprocess.DEVNULL
                ).strip()
                
                if efi_check:
                    return CheckResult(
                        name="OpenCore Legacy Patcher",
                        status=Status.WARNING,
                        details="EFI partition detected",
                        recommendation="Custom boot loader may be in use - verify configuration"
                    )
            except subprocess.CalledProcessError:
                pass
            
            return CheckResult(
                name="OpenCore Legacy Patcher",
                status=Status.PASS,
                details="Not installed",
                recommendation="OCLP not detected - running stock macOS"
            )
