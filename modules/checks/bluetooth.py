"""Bluetooth diagnostic check."""

import subprocess
from ..utils.base import BaseCheck, CheckResult, Status


class BluetoothCheck(BaseCheck):
    """Check Bluetooth status."""
    
    def run(self) -> CheckResult:
        """Run Bluetooth diagnostic check.
        
        Returns:
            CheckResult with Bluetooth information
        """
        try:
            bluetooth_status = subprocess.check_output(
                "system_profiler SPBluetoothDataType | grep 'State:'",
                shell=True,
                text=True,
                stderr=subprocess.DEVNULL
            ).strip()
            
            if bluetooth_status:
                state = bluetooth_status.split(':')[-1].strip().lower()
                
                if "powered on" in state or "on" in state:
                    return CheckResult(
                        name="Bluetooth",
                        status=Status.PASS,
                        details="Bluetooth is powered on",
                        recommendation="Bluetooth is functioning normally"
                    )
                elif "powered off" in state or "off" in state:
                    return CheckResult(
                        name="Bluetooth",
                        status=Status.WARNING,
                        details="Bluetooth is powered off",
                        recommendation="Enable Bluetooth if needed"
                    )
                else:
                    return CheckResult(
                        name="Bluetooth",
                        status=Status.PASS,
                        details=bluetooth_status,
                        recommendation="Bluetooth is functioning normally"
                    )
            else:
                return CheckResult(
                    name="Bluetooth",
                    status=Status.WARNING,
                    details="Could not determine Bluetooth status",
                    recommendation="Check Bluetooth settings manually"
                )
        except subprocess.CalledProcessError:
            return CheckResult(
                name="Bluetooth",
                status=Status.WARNING,
                details="Unknown",
                recommendation="Could not retrieve Bluetooth information"
            )
