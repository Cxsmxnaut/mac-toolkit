"""EFI mount and unmount helper repairs."""

from datetime import datetime

from ..utils.base import BaseRepair, RepairResult
from ..utils.macos import get_efi_identifier, run_command


def _efi_identifier() -> str:
    return get_efi_identifier()


class MountEFIRepair(BaseRepair):
    """Mount the internal EFI partition."""

    def __init__(self, require_confirmation: bool = True):
        super().__init__(require_confirmation)
        self.name = "Mount EFI"

    def execute_repair(self) -> RepairResult:
        start = datetime.now()
        efi = _efi_identifier()
        ok, stdout, stderr = run_command(["diskutil", "mount", efi], timeout=30)
        return RepairResult(self.name, ok, start, datetime.now(), stdout, None if ok else stderr, {"efi": efi})


class UnmountEFIRepair(BaseRepair):
    """Unmount the internal EFI partition."""

    def __init__(self, require_confirmation: bool = True):
        super().__init__(require_confirmation)
        self.name = "Unmount EFI"

    def execute_repair(self) -> RepairResult:
        start = datetime.now()
        efi = _efi_identifier()
        ok, stdout, stderr = run_command(["diskutil", "unmount", efi], timeout=30)
        return RepairResult(self.name, ok, start, datetime.now(), stdout, None if ok else stderr, {"efi": efi})
