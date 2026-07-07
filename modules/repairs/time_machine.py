"""Time Machine verification repair operation."""

from datetime import datetime

from ..utils.base import BaseRepair, RepairResult
from ..utils.macos import run_command


class VerifyTimeMachineRepair(BaseRepair):
    """Verify Time Machine destination/status without changing configuration."""

    def __init__(self, require_confirmation: bool = False):
        super().__init__(require_confirmation)
        self.name = "Verify Time Machine"

    def execute_repair(self) -> RepairResult:
        start = datetime.now()
        ok, stdout, stderr = run_command(["tmutil", "destinationinfo"], timeout=30)
        return RepairResult(
            name=self.name,
            success=ok,
            start_time=start,
            end_time=datetime.now(),
            output=stdout or "No Time Machine destination configured",
            error=None if ok else stderr,
        )
