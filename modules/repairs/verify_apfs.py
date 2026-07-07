"""APFS verification repair operation."""

from datetime import datetime

from ..utils.base import BaseRepair, RepairResult
from ..utils.macos import run_command


class VerifyAPFSRepair(BaseRepair):
    """Verify APFS container health without modifying data."""

    def __init__(self, require_confirmation: bool = False):
        super().__init__(require_confirmation)
        self.name = "Verify APFS"

    def execute_repair(self) -> RepairResult:
        start = datetime.now()
        ok, stdout, stderr = run_command("diskutil verifyVolume /", timeout=120, use_shell=True)
        return RepairResult(
            name=self.name,
            success=ok,
            start_time=start,
            end_time=datetime.now(),
            output=stdout,
            error=None if ok else stderr,
        )
