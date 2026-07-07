"""Software update check repair operation."""

from datetime import datetime

from ..utils.base import BaseRepair, RepairResult
from ..utils.macos import run_command


class SoftwareUpdateCheckRepair(BaseRepair):
    """Check available macOS software updates without installing them."""

    def __init__(self, require_confirmation: bool = False):
        super().__init__(require_confirmation)
        self.name = "Check Software Updates"

    def execute_repair(self) -> RepairResult:
        start = datetime.now()
        ok, stdout, stderr = run_command(["softwareupdate", "-l"], timeout=180)
        return RepairResult(
            name=self.name,
            success=ok,
            start_time=start,
            end_time=datetime.now(),
            output=stdout or "No update output returned",
            error=None if ok else stderr,
        )
