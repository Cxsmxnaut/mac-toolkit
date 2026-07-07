"""Privilege and installation context diagnostic check."""

from __future__ import annotations

import os
import shutil

from ..utils.base import BaseCheck, CheckResult, Status


class PrivilegeCheck(BaseCheck):
    """Report whether Mac Toolkit is running with administrative privileges."""

    def run(self) -> CheckResult:
        is_root = os.geteuid() == 0
        sudo_available = shutil.which("sudo") is not None
        if is_root:
            return CheckResult(
                name="Privilege Level",
                status=Status.PASS,
                details="Running as root",
                recommendation="Privileged checks and repairs can run when needed",
                metadata={"is_root": True, "sudo_available": sudo_available},
            )

        return CheckResult(
            name="Privilege Level",
            status=Status.WARNING,
            details="Running as a standard user",
            recommendation="Some thermal, EFI, security, and repair checks may require administrator approval",
            metadata={"is_root": False, "sudo_available": sudo_available},
        )
