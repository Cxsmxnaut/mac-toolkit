"""Installed environment validation."""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

from rich.table import Table

from .console import get_console
from .diagnostics_engine import DiagnosticsEngine
from .repairs.engine import RepairEngine
from .utils.macos import logs_dir, reports_dir


def validate_install() -> int:
    """Validate that Mac Toolkit can run from the installed environment."""
    console = get_console()
    table = Table(title="Mac Toolkit Install Validation")
    table.add_column("Check")
    table.add_column("Result")
    table.add_column("Details")

    failures = 0

    def add(name: str, ok: bool, details: str) -> None:
        nonlocal failures
        if not ok:
            failures += 1
        table.add_row(name, "[green]PASS[/green]" if ok else "[red]FAIL[/red]", details)

    add("Python", sys.version_info >= (3, 11), sys.version.split()[0])
    add("CLI wrapper", shutil.which("mactoolkit") is not None, shutil.which("mactoolkit") or "not found")
    add("Log directory", logs_dir().is_dir(), str(logs_dir()))
    add("Report directory", reports_dir().is_dir(), str(reports_dir()))

    checks = DiagnosticsEngine()
    checks.discover_checks()
    add("Diagnostics discovery", len(checks.checks) >= 20, f"{len(checks.checks)} checks")

    repairs = RepairEngine()
    repairs.discover_repairs()
    add("Repair discovery", len(repairs.repairs) >= 5, f"{len(repairs.repairs)} repairs")

    app_path = Path("/Applications/Mac Toolkit.app")
    add("GUI app", app_path.exists(), str(app_path))

    console.print(table)
    return 1 if failures else 0
