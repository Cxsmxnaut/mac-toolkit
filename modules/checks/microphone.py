"""Microphone diagnostic check."""

from ..utils.base import BaseCheck, CheckResult, Status
from ..utils.macos import run_command_output


class MicrophoneCheck(BaseCheck):
    """Check microphone input device availability."""

    def run(self) -> CheckResult:
        output = run_command_output("system_profiler SPAudioDataType")
        if not output:
            return CheckResult(
                name="Microphone",
                status=Status.UNKNOWN,
                details="Audio device information unavailable",
                recommendation="Test microphone in System Settings > Sound",
            )

        has_input = "Input" in output or "Built-in Microphone" in output or "External Microphone" in output
        if not has_input:
            return CheckResult(
                name="Microphone",
                status=Status.WARNING,
                details="No input audio devices detected",
                recommendation="Connect or enable a microphone in System Settings",
            )

        return CheckResult(
            name="Microphone",
            status=Status.PASS,
            details="Input audio device(s) detected",
            recommendation="Test microphone input levels in System Settings",
        )
