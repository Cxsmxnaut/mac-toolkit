"""Full one-shot service workflow."""

from __future__ import annotations

from typing import Iterable

from rich.panel import Panel
from rich.table import Table

from .console import get_console
from .diagnostics_engine import DiagnosticsEngine
from .repairs.engine import run_repairs, run_safe_repairs
from .report.generator import generate_reports
from .stress_engine import run_stress_tests
from .system import get_system_info
from .utils.base import Status
from .utils.config import get_config
from .utils.health_score import calculate_health_score


def run_auto_service(
    *,
    formats: Iterable[str] | None = None,
    run_repairs_after: bool = False,
    auto_confirm_repairs: bool = False,
    show_progress: bool = True,
) -> int:
    """Run diagnostics, generate reports, and optionally run repairs."""
    console = get_console()
    console.print_title("Mac Toolkit Service Run")
    console.print()

    config = get_config()
    system_info = get_system_info()
    engine = DiagnosticsEngine()
    results = engine.run_and_display(show_progress=show_progress)
    health = calculate_health_score(results)

    repair_results = []
    stress_results = []

    console.print()
    if run_repairs_after or bool(config.get("auto_service.auto_repair", False)):
        repair_results = run_repairs(
            show_progress=show_progress,
            auto_confirm=auto_confirm_repairs or not bool(config.get("auto_service.require_confirmation", True)),
        )
    else:
        repair_results = run_safe_repairs(show_progress=show_progress)

    if bool(config.get("auto_service.run_stress_tests", False)):
        console.print()
        stress_results = run_stress_tests(show_progress=show_progress)

    report_formats = list(formats) if formats else None
    files = generate_reports(
        results,
        system_info,
        formats=report_formats,
        repairs=repair_results,
        stress_results=stress_results,
    )

    console.print()
    console.print(Panel.fit(
        f"[bold]Readiness:[/bold] {health['overall_health']}  "
        f"[bold]Score:[/bold] {health['health_score']}/100",
        title="Service Summary",
    ))

    if health["recommendations"]:
        table = Table(title="Action Items")
        table.add_column("Priority", style="bold")
        table.add_column("Recommendation")
        for item in health["recommendations"]:
            priority = "Critical" if item.startswith("[CRITICAL]") else "Warning"
            table.add_row(priority, item.split("] ", 1)[-1])
        console.print(table)

    console.print()
    console.print_header("Reports")
    for format_name, path in files.items():
        console.print_key_value(format_name.upper(), str(path))

    if any(result.status == Status.FAIL for result in results):
        return 2
    if any(result.status == Status.WARNING for result in results):
        return 1
    return 0
