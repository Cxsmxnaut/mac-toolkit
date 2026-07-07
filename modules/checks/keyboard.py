"""Keyboard diagnostic check."""

from ..utils.base import BaseCheck, CheckResult, Status
from ..utils.macos import run_command_output


class KeyboardCheck(BaseCheck):
    """Check keyboard device detection."""

    def run(self) -> CheckResult:
        output = run_command_output("ioreg -p IOUSB -l -w 0 | grep -i keyboard | head -5")
        profile = run_command_output("system_profiler SPUSBDataType | grep -i keyboard | head -5")

        if output or profile:
            return CheckResult(
                name="Keyboard",
                status=Status.PASS,
                details="Keyboard device detected",
                recommendation="Verify all keys respond in Keyboard Viewer",
            )

        hid_output = run_command_output("ioreg -l | grep -i 'AppleHIDKeyboard' | head -3")
        if hid_output:
            return CheckResult(
                name="Keyboard",
                status=Status.PASS,
                details="Built-in keyboard detected via HID",
                recommendation="Verify all keys respond in Keyboard Viewer",
            )

        return CheckResult(
            name="Keyboard",
            status=Status.WARNING,
            details="No keyboard detected",
            recommendation="Connect a keyboard or verify built-in keyboard hardware",
        )
