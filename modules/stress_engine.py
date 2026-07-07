"""Stress test engine and built-in stress tests."""

from __future__ import annotations

import math
import os
import tempfile
import time
from datetime import datetime
from pathlib import Path
from typing import List

from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn, TimeRemainingColumn
from rich.table import Table

from .console import get_console
from .utils.base import BaseStressTest, StressTestResult
from .utils.config import get_config
from .utils.macos import get_cpu_temperature, get_fan_speeds, get_memory_pressure, run_command


class CPUStressTest(BaseStressTest):
    """Run a CPU-bound workload for a bounded duration."""

    def run_test(self) -> StressTestResult:
        start = datetime.now()
        end_at = time.monotonic() + self.duration_seconds
        iterations = 0
        peak_temp = 0.0

        while time.monotonic() < end_at and not self._abort_flag:
            for value in range(1, 8000):
                math.sqrt(value * value)
            iterations += 1
            temp = get_cpu_temperature()
            if temp is not None:
                peak_temp = max(peak_temp, temp)
                if self.temperature_limit and temp >= self.temperature_limit:
                    self.abort(f"CPU temperature reached {temp:.1f}C")

        finish = datetime.now()
        return StressTestResult(
            name="CPU Stress",
            success=not self._abort_flag,
            start_time=start,
            end_time=finish,
            duration_seconds=(finish - start).total_seconds(),
            metrics={"iterations": iterations, "peak_cpu_celsius": peak_temp or None},
            aborted=self._abort_flag,
            abort_reason=getattr(self, "_abort_reason", None),
        )


class RAMStressTest(BaseStressTest):
    """Allocate and touch memory in chunks to validate memory pressure behavior."""

    def run_test(self) -> StressTestResult:
        start = datetime.now()
        chunks: list[bytearray] = []
        target_mb = min(512, max(64, (os.sysconf("SC_PAGE_SIZE") * os.sysconf("SC_PHYS_PAGES")) // 1024 // 1024 // 16))
        allocated = 0

        try:
            while allocated < target_mb and not self._abort_flag:
                chunk = bytearray(8 * 1024 * 1024)
                chunk[0] = 1
                chunk[-1] = 1
                chunks.append(chunk)
                allocated += 8
                if get_memory_pressure() == "critical":
                    self.abort("Memory pressure became critical")
                time.sleep(0.05)
        finally:
            chunks.clear()

        finish = datetime.now()
        return StressTestResult(
            name="RAM Stress",
            success=not self._abort_flag,
            start_time=start,
            end_time=finish,
            duration_seconds=(finish - start).total_seconds(),
            metrics={"allocated_mb": allocated, "memory_pressure": get_memory_pressure()},
            aborted=self._abort_flag,
            abort_reason=getattr(self, "_abort_reason", None),
        )


class DiskBenchmarkTest(BaseStressTest):
    """Perform a small sequential disk write/read benchmark in /tmp."""

    def run_test(self) -> StressTestResult:
        start = datetime.now()
        size_mb = 128
        data = os.urandom(1024 * 1024)
        path = Path(tempfile.gettempdir()) / f"mactoolkit_disk_{os.getpid()}.bin"

        try:
            write_start = time.monotonic()
            with open(path, "wb") as handle:
                for _ in range(size_mb):
                    handle.write(data)
                handle.flush()
                os.fsync(handle.fileno())
            write_seconds = max(time.monotonic() - write_start, 0.001)

            read_start = time.monotonic()
            with open(path, "rb") as handle:
                while handle.read(1024 * 1024):
                    pass
            read_seconds = max(time.monotonic() - read_start, 0.001)
        finally:
            path.unlink(missing_ok=True)

        finish = datetime.now()
        return StressTestResult(
            name="Disk Benchmark",
            success=True,
            start_time=start,
            end_time=finish,
            duration_seconds=(finish - start).total_seconds(),
            metrics={
                "size_mb": size_mb,
                "write_mb_s": round(size_mb / write_seconds, 2),
                "read_mb_s": round(size_mb / read_seconds, 2),
            },
        )


class GPUStressTest(BaseStressTest):
    """Run a best-effort GPU/Metal capability probe."""

    def run_test(self) -> StressTestResult:
        start = datetime.now()
        ok, stdout, stderr = run_command("system_profiler SPDisplaysDataType | grep -E 'Metal|Chipset Model'", use_shell=True)
        finish = datetime.now()
        return StressTestResult(
            name="GPU Stress",
            success=ok and "metal" in stdout.lower(),
            start_time=start,
            end_time=finish,
            duration_seconds=(finish - start).total_seconds(),
            metrics={"graphics": stdout, "error": stderr},
            output="Metal capability probe completed",
        )


class CombinedStressTest(BaseStressTest):
    """Run a short combined CPU, RAM, and disk validation."""

    def run_test(self) -> StressTestResult:
        start = datetime.now()
        cpu = CPUStressTest(duration_seconds=min(10, self.duration_seconds), temperature_limit=self.temperature_limit).execute()
        ram = RAMStressTest(duration_seconds=min(10, self.duration_seconds), temperature_limit=self.temperature_limit).execute()
        disk = DiskBenchmarkTest(duration_seconds=min(10, self.duration_seconds), temperature_limit=self.temperature_limit).execute()
        finish = datetime.now()
        success = cpu.success and ram.success and disk.success
        return StressTestResult(
            name="Combined Stress",
            success=success,
            start_time=start,
            end_time=finish,
            duration_seconds=(finish - start).total_seconds(),
            metrics={
                "cpu": cpu.to_dict(),
                "ram": ram.to_dict(),
                "disk": disk.to_dict(),
                "fan_speeds": get_fan_speeds(),
            },
            aborted=cpu.aborted or ram.aborted or disk.aborted,
            abort_reason=cpu.abort_reason or ram.abort_reason or disk.abort_reason,
        )


class StressEngine:
    """Coordinate stress tests and display results."""

    def __init__(self) -> None:
        self.console = get_console()
        config = get_config()
        duration = int(config.get("stress.duration_seconds", 300))
        cpu_limit = float(config.get("stress.temperature_limit_cpu", 90))
        self.tests: List[BaseStressTest] = [
            CPUStressTest(duration_seconds=min(duration, 60), temperature_limit=cpu_limit),
            RAMStressTest(duration_seconds=min(duration, 60), temperature_limit=cpu_limit),
            DiskBenchmarkTest(duration_seconds=duration, temperature_limit=cpu_limit),
            GPUStressTest(duration_seconds=duration, temperature_limit=cpu_limit),
            CombinedStressTest(duration_seconds=min(duration, 30), temperature_limit=cpu_limit),
        ]
        self.results: List[StressTestResult] = []

    def run_all(self, show_progress: bool = True) -> List[StressTestResult]:
        """Run all built-in stress tests."""
        self.results = []
        if show_progress:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TimeRemainingColumn(),
                console=self.console.console,
            ) as progress:
                task = progress.add_task("Running stress tests...", total=len(self.tests))
                for test in self.tests:
                    self.results.append(test.execute())
                    progress.update(task, advance=1)
        else:
            for test in self.tests:
                self.results.append(test.execute())
        return self.results

    def display_results(self) -> None:
        """Display stress test results."""
        table = Table(title="Stress Test Results")
        table.add_column("Test")
        table.add_column("Status")
        table.add_column("Duration")
        table.add_column("Metrics")
        for result in self.results:
            status = "[green]PASS[/green]" if result.success else "[red]FAIL[/red]"
            table.add_row(result.name, status, f"{result.duration_seconds:.1f}s", str(result.metrics)[:90])
        self.console.print(table)


def run_stress_tests(show_progress: bool = True) -> List[StressTestResult]:
    """Run and display all stress tests."""
    engine = StressEngine()
    results = engine.run_all(show_progress=show_progress)
    engine.display_results()
    return results
