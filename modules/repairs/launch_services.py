"""Launch Services repair operation."""

from datetime import datetime

from ..utils.base import BaseRepair, RepairResult
from ..utils.macos import run_command


class LaunchServicesRepair(BaseRepair):
    """Rebuild Launch Services registration database."""

    def __init__(self, require_confirmation: bool = True):
        super().__init__(require_confirmation)
        self.name = "Repair Launch Services"

    def execute_repair(self) -> RepairResult:
        start = datetime.now()
        command = (
            "/System/Library/Frameworks/CoreServices.framework/Frameworks/"
            "LaunchServices.framework/Support/lsregister -kill -r -domain local "
            "-domain system -domain user"
        )
        ok, stdout, stderr = run_command(command, timeout=120, use_shell=True)
        return RepairResult(
            name=self.name,
            success=ok,
            start_time=start,
            end_time=datetime.now(),
            output=stdout or "Launch Services rebuild completed",
            error=None if ok else stderr,
        )
