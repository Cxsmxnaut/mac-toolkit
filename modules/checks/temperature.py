"""Temperature diagnostic check."""

from ..utils.base import BaseCheck, CheckResult, Status
from ..utils.macos import get_cpu_temperature, get_gpu_temperature


class TemperatureCheck(BaseCheck):
    """Check CPU and GPU temperature readings."""

    def run(self) -> CheckResult:
        cpu_temp = get_cpu_temperature()
        gpu_temp = get_gpu_temperature()

        parts = []
        status = Status.PASS
        recommendation = "Temperatures are within normal range"

        if cpu_temp is not None:
            parts.append(f"CPU: {cpu_temp:.1f}°C")
            if cpu_temp >= 95:
                status = Status.FAIL
                recommendation = "CPU temperature is critically high"
            elif cpu_temp >= 85:
                status = Status.WARNING
                recommendation = "CPU temperature is elevated"
        else:
            parts.append("CPU: unavailable without elevated permissions")

        if gpu_temp is not None:
            parts.append(f"GPU: {gpu_temp:.1f}°C")
            if gpu_temp >= 95 and status != Status.FAIL:
                status = Status.FAIL
                recommendation = "GPU temperature is critically high"
            elif gpu_temp >= 85 and status == Status.PASS:
                status = Status.WARNING
                recommendation = "GPU temperature is elevated"

        if not cpu_temp and not gpu_temp:
            return CheckResult(
                name="Temperature",
                status=Status.UNKNOWN,
                details="Temperature sensors unavailable (try with sudo for powermetrics)",
                recommendation="Run stress tests with monitoring for thermal validation",
            )

        return CheckResult(
            name="Temperature",
            status=status,
            details=" | ".join(parts),
            recommendation=recommendation,
            metadata={"cpu_celsius": cpu_temp, "gpu_celsius": gpu_temp},
        )
