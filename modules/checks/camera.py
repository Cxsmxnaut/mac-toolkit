"""Camera diagnostic check."""

from ..utils.base import BaseCheck, CheckResult, Status
from ..utils.macos import run_command_output


class CameraCheck(BaseCheck):
    """Check built-in or connected camera availability."""

    def run(self) -> CheckResult:
        output = run_command_output("system_profiler SPCameraDataType")
        if not output:
            return CheckResult(
                name="Camera",
                status=Status.UNKNOWN,
                details="Camera information unavailable",
                recommendation="Test camera in Photo Booth or FaceTime",
            )

        if "No camera" in output.lower() or "not detected" in output.lower():
            return CheckResult(
                name="Camera",
                status=Status.WARNING,
                details="No camera detected",
                recommendation="Verify camera hardware or external webcam connection",
            )

        model_line = next(
            (line.split(":", 1)[1].strip() for line in output.splitlines() if "Model ID:" in line),
            "Camera detected",
        )

        return CheckResult(
            name="Camera",
            status=Status.PASS,
            details=model_line,
            recommendation="Camera hardware is detected by the system",
        )
