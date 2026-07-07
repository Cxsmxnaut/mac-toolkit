"""OpenCore Legacy Patcher detection diagnostic check."""

from pathlib import Path

from ..utils.base import BaseCheck, CheckResult, Status
from ..utils.macos import run_command_output


class OCLPCheck(BaseCheck):
    """Check for OpenCore Legacy Patcher installation."""
    
    def run(self) -> CheckResult:
        """Run OCLP detection check.
        
        Returns:
            CheckResult with OCLP information
        """
        oclp_paths = [
            Path("/Applications/OpenCore-Patcher.app"),
            Path("/Library/Application Support/Dortania/OpenCore-Patcher"),
            Path("/usr/local/bin/opencore-legacy-patcher"),
        ]
        installed_paths = [str(path) for path in oclp_paths if path.exists()]

        cli = Path("/usr/local/bin/opencore-legacy-patcher")
        if cli.exists():
            version = run_command_output(f"{cli} --version")
            details = f"Installed: {version}" if version else "Installed but version unknown"
            return CheckResult(
                name="OpenCore Legacy Patcher",
                status=Status.PASS if version else Status.WARNING,
                details=details,
                recommendation="OCLP is installed - ensure it is kept up to date",
                metadata={"paths": installed_paths},
            )

        if installed_paths:
            return CheckResult(
                name="OpenCore Legacy Patcher",
                status=Status.PASS,
                details="OCLP app/support files detected",
                recommendation="OCLP is installed - ensure it is kept up to date",
                metadata={"paths": installed_paths},
            )

        nvram = run_command_output("nvram 4D1FDA02-38C7-4A6A-9CC6-4BCCA8B38C14:boot-path 2>/dev/null") or ""
        if "EFI\\OC" in nvram or "EFI/OC" in nvram:
            return CheckResult(
                name="OpenCore Legacy Patcher",
                status=Status.WARNING,
                details="OpenCore boot path detected in NVRAM",
                recommendation="Verify OpenCore/OCLP configuration",
                metadata={"nvram_boot_path": nvram},
            )

        return CheckResult(
            name="OpenCore Legacy Patcher",
            status=Status.PASS,
            details="Not installed",
            recommendation="OCLP not detected - running stock macOS",
        )
