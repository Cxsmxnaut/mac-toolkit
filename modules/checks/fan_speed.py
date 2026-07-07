"""Fan speed diagnostic check."""

from ..utils.base import BaseCheck, CheckResult, Status
from ..utils.macos import get_fan_speeds


class FanSpeedCheck(BaseCheck):
    """Check fan speed readings."""

    def run(self) -> CheckResult:
        fans = get_fan_speeds()
        if not fans:
            return CheckResult(
                name="Fan Speed",
                status=Status.UNKNOWN,
                details="No fan speed data available (fanless Mac or sensors unavailable)",
                recommendation="Verify cooling manually if system feels hot",
            )

        speeds = [fan["speed_rpm"] for fan in fans]
        avg_speed = sum(speeds) / len(speeds)
        details = ", ".join(f"Fan {index + 1}: {speed} RPM" for index, speed in enumerate(speeds))

        status = Status.PASS
        recommendation = "Fans are reporting normally"
        if avg_speed >= 6000:
            status = Status.WARNING
            recommendation = "Fans running at high speed — check thermal load"
        elif avg_speed == 0:
            status = Status.WARNING
            recommendation = "Fan speed reads zero — verify cooling hardware"

        return CheckResult(
            name="Fan Speed",
            status=status,
            details=details,
            recommendation=recommendation,
            metadata={"fan_speeds_rpm": speeds},
        )
