"""GPU diagnostic check."""

import subprocess
from ..utils.base import BaseCheck, CheckResult, Status


class GPUCheck(BaseCheck):
    """Check GPU information and status."""
    
    def run(self) -> CheckResult:
        """Run GPU diagnostic check.
        
        Returns:
            CheckResult with GPU information
        """
        try:
            gpu_info = subprocess.check_output(
                "system_profiler SPDisplaysDataType | grep 'Chipset Model'",
                shell=True,
                text=True,
                stderr=subprocess.DEVNULL
            ).strip()
            
            if gpu_info:
                gpus = []
                for line in gpu_info.split('\n'):
                    gpu = line.split(':')[-1].strip()
                    if gpu:
                        gpus.append(gpu)
                
                details = ", ".join(gpus) if gpus else "Unknown"
                
                return CheckResult(
                    name="GPU",
                    status=Status.PASS,
                    details=details,
                    recommendation="GPU is functioning normally"
                )
            else:
                return CheckResult(
                    name="GPU",
                    status=Status.WARNING,
                    details="No GPU detected",
                    recommendation="Could not detect GPU information"
                )
        except subprocess.CalledProcessError:
            return CheckResult(
                name="GPU",
                status=Status.WARNING,
                details="Unknown",
                recommendation="Could not retrieve GPU information"
            )
