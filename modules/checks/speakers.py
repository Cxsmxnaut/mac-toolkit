"""Speaker diagnostic check."""

from ..utils.base import BaseCheck, CheckResult, Status
from ..utils.macos import run_command_output


class SpeakersCheck(BaseCheck):
    """Check speaker/output audio device availability."""

    def run(self) -> CheckResult:
        output = run_command_output("system_profiler SPAudioDataType")
        if not output:
            return CheckResult(
                name="Speakers",
                status=Status.UNKNOWN,
                details="Audio output information unavailable",
                recommendation="Test speakers in System Settings > Sound",
            )

        has_output = "Output" in output or "Built-in Output" in output or "External" in output
        if not has_output:
            return CheckResult(
                name="Speakers",
                status=Status.WARNING,
                details="No output audio devices detected",
                recommendation="Connect speakers or headphones and retest",
            )

        return CheckResult(
            name="Speakers",
            status=Status.PASS,
            details="Output audio device(s) detected",
            recommendation="Play test tone in System Settings to verify audio output",
        )
