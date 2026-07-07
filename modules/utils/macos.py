"""Shared macOS command helpers for Mac Toolkit."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

def run_command(
    command: str | List[str],
    *,
    timeout: int = 30,
    use_shell: bool = False,
) -> Tuple[bool, str, str]:
    """Run a command and return success, stdout, stderr."""
    try:
        shell = use_shell
        if isinstance(command, str) and not use_shell:
            command = command.split()
        elif isinstance(command, str):
            shell = True
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout,
            shell=shell,
        )
        return result.returncode == 0, result.stdout.strip(), result.stderr.strip()
    except subprocess.TimeoutExpired:
        return False, "", "Command timed out"
    except Exception as exc:
        return False, "", str(exc)


def run_command_output(command: str, *, timeout: int = 30) -> Optional[str]:
    """Run a shell command and return stdout or None."""
    ok, stdout, _ = run_command(command, timeout=timeout, use_shell=True)
    return stdout if ok and stdout else None


def app_support_dir() -> Path:
    """Return the per-user application support directory."""
    path = Path.home() / "Library" / "Application Support" / "Mac Toolkit"
    path.mkdir(parents=True, exist_ok=True)
    return path


def logs_dir() -> Path:
    """Return the per-user logs directory."""
    path = Path.home() / "Library" / "Logs" / "Mac Toolkit"
    path.mkdir(parents=True, exist_ok=True)
    return path


def reports_dir() -> Path:
    """Return the per-user reports directory."""
    path = app_support_dir() / "Reports"
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_root_disk_identifier() -> str:
    """Return the whole disk identifier backing the root volume."""
    root_device = run_command_output("df / | awk 'NR==2 {print $1}'") or ""
    match = re.search(r"/dev/(disk\d+)", root_device)
    return match.group(1) if match else "disk0"


def get_efi_identifier() -> str:
    """Return the expected EFI partition identifier for the root disk."""
    return f"{get_root_disk_identifier()}s1"


def get_cpu_temperature() -> Optional[float]:
    """Read CPU temperature in Celsius when available."""
    ok, stdout, _ = run_command(
        "powermetrics --samplers smc -n1 -i1000 2>/dev/null",
        timeout=8,
        use_shell=True,
    )
    if ok and stdout:
        match = re.search(r"CPU die temperature:\s*([\d.]+)", stdout)
        if match:
            return float(match.group(1))

    output = run_command_output(
        "ioreg -l | grep -E 'CPU_Proximity|CPU Die|Temperature' | head -20"
    )
    if output:
        for match in re.finditer(r'"?([\d.]+)"?\s*$', output, re.MULTILINE):
            value = float(match.group(1))
            if 20 <= value <= 120:
                return value
    return None


def get_gpu_temperature() -> Optional[float]:
    """Read GPU temperature in Celsius when available."""
    ok, stdout, _ = run_command(
        "powermetrics --samplers smc -n1 -i1000 2>/dev/null",
        timeout=8,
        use_shell=True,
    )
    if ok and stdout:
        match = re.search(r"GPU die temperature:\s*([\d.]+)", stdout)
        if match:
            return float(match.group(1))

    output = run_command_output("ioreg -l | grep -i 'GPU' | grep -i temperature | head -5")
    if output:
        match = re.search(r"([\d.]+)", output)
        if match:
            value = float(match.group(1))
            if 20 <= value <= 120:
                return value
    return None


def get_fan_speeds() -> List[Dict[str, Any]]:
    """Return fan speed readings from IORegistry."""
    output = run_command_output("ioreg -l -w0 | grep -E 'Fan.*Speed|Actual.*Speed' | head -20")
    fans: List[Dict[str, Any]] = []
    if not output:
        return fans

    for line in output.splitlines():
        match = re.search(r'"Actual[^"]*" = (\d+)', line)
        if match:
            fans.append({"speed_rpm": int(match.group(1)), "raw": line.strip()})
    return fans


def get_memory_pressure() -> Optional[str]:
    """Return memory pressure label from memory_pressure tool."""
    output = run_command_output("memory_pressure 2>/dev/null | head -5")
    if output:
        match = re.search(r"System-wide memory free percentage:\s*(\d+)%", output)
        if match:
            pct = int(match.group(1))
            if pct >= 50:
                return "normal"
            if pct >= 25:
                return "warn"
            return "critical"
    return None


def get_power_adapter_status() -> Optional[str]:
    """Return power adapter status from pmset."""
    return run_command_output("pmset -g ac")


def device_has_battery() -> bool:
    """Return True if the Mac has an internal battery."""
    output = run_command_output("pmset -g batt")
    return bool(output and "InternalBattery" in output)


def get_wifi_interface() -> str:
    """Return the primary Wi-Fi interface name."""
    output = run_command_output("networksetup -listallhardwareports")
    if not output:
        return "en0"
    lines = output.splitlines()
    for index, line in enumerate(lines):
        if "Wi-Fi" in line or "AirPort" in line:
            for next_line in lines[index + 1 : index + 4]:
                if "Device:" in next_line:
                    return next_line.split(":", 1)[1].strip()
    return "en0"


def get_kernel_panic_count() -> int:
    """Count recent kernel panic log entries."""
    output = run_command_output(
        "log show --predicate 'eventMessage CONTAINS \"panic\"' "
        "--last 30d 2>/dev/null | grep -c panic || true"
    )
    if output and output.isdigit():
        return int(output)
    return 0
