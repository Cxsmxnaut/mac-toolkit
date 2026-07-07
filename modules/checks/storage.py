"""Storage/SMART diagnostic check."""

import re
from ..utils.base import BaseCheck, CheckResult, Status
from ..utils.macos import run_command_output


class StorageCheck(BaseCheck):
    """Check storage devices and SMART status."""
    
    def run(self) -> CheckResult:
        """Run storage diagnostic check.
        
        Returns:
            CheckResult with storage information
        """
        disk_usage = run_command_output("df -h /")
        root_device = run_command_output("df / | awk 'NR==2 {print $1}'") or ""
        disk_match = re.search(r"(/dev/disk\d+)", root_device)
        disk = disk_match.group(1).replace("/dev/", "") if disk_match else "disk0"
        smart_status = run_command_output(f"diskutil info {disk} | grep SMART") or ""

        if disk_usage:
            lines = disk_usage.split('\n')
            if len(lines) > 1:
                parts = lines[1].split()
                if len(parts) >= 5:
                    capacity = parts[4]
                    capacity_num = int(re.sub(r'[^0-9]', '', capacity))

                    status = Status.PASS
                    recommendation = "Storage is functioning normally"

                    if "failing" in smart_status.lower():
                        status = Status.FAIL
                        recommendation = "SMART reports a storage failure - back up and replace drive"
                    elif capacity_num >= 90:
                        status = Status.FAIL
                        recommendation = "Storage is critically full - free up space immediately"
                    elif capacity_num >= 80:
                        status = Status.WARNING
                        recommendation = "Storage is nearly full - consider freeing up space"

                    details = f"Root capacity: {capacity} on {disk}"
                    if smart_status:
                        details += f" | {smart_status}"

                    return CheckResult(
                        name="Storage",
                        status=status,
                        details=details,
                        recommendation=recommendation
                    )

        return CheckResult(
            name="Storage",
            status=Status.WARNING,
            details="Could not determine disk usage",
            recommendation="Check disk manually"
        )
