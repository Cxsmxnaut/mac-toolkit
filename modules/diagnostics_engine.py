"""Diagnostic engine for running and collecting check results."""

import importlib
import pkgutil
from pathlib import Path
from typing import List, Dict, Any, Optional
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeRemainingColumn
from rich import box

from .console import get_console
from .utils.logger import get_logger
from .utils.base import CheckResult, Status, BaseCheck


class DiagnosticsEngine:
    """Engine for running diagnostic checks and collecting results."""
    
    def __init__(self, checks_dir: Optional[str] = None):
        """Initialize the diagnostics engine.
        
        Args:
            checks_dir: Directory containing diagnostic check modules
        """
        self.checks_dir = Path(checks_dir) if checks_dir else Path(__file__).resolve().parent / "checks"
        self.console = get_console()
        self.logger = get_logger()
        self.checks: List[BaseCheck] = []
        self.results: List[CheckResult] = []
    
    def discover_checks(self) -> None:
        """Discover all diagnostic check modules in the checks directory."""
        self.logger.info("Discovering diagnostic checks")
        self.checks = []
        
        if not self.checks_dir.exists():
            self.logger.warning(f"Checks directory not found: {self.checks_dir}")
            return
        
        # Import all modules in the checks directory
        for finder, name, _ in pkgutil.iter_modules([str(self.checks_dir)]):
            try:
                module = importlib.import_module(f"modules.checks.{name}")
                
                # Find all classes that inherit from BaseCheck
                for attr_name in dir(module):
                    if attr_name.startswith('_'):
                        continue
                    attr = getattr(module, attr_name)
                    try:
                        if (isinstance(attr, type) and 
                            issubclass(attr, BaseCheck) and 
                            attr is not BaseCheck):
                            check_instance = attr()
                            self.checks.append(check_instance)
                            self.logger.debug(f"Discovered check: {check_instance.name}")
                    except TypeError:
                        # Skip attributes that can't be instantiated
                        continue
            except Exception as e:
                self.logger.error(f"Failed to load check module {name}: {e}")
        
        self.logger.info(f"Discovered {len(self.checks)} diagnostic checks")
    
    def run_check(self, check: BaseCheck) -> CheckResult:
        """Run a single diagnostic check.
        
        Args:
            check: BaseCheck instance to run
            
        Returns:
            CheckResult from the check
        """
        self.logger.debug(f"Running check: {check.name}")
        return check.execute()
    
    def run_all_checks(self, show_progress: bool = True) -> List[CheckResult]:
        """Run all discovered diagnostic checks.
        
        Args:
            show_progress: Whether to show progress bar
            
        Returns:
            List of CheckResult from all checks
        """
        self.logger.info(f"Running {len(self.checks)} diagnostic checks")
        self.results = []
        
        if show_progress:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                TimeRemainingColumn(),
                console=self.console.console
            ) as progress:
                task = progress.add_task("Running diagnostics...", total=len(self.checks))
                
                for check in self.checks:
                    result = self.run_check(check)
                    self.results.append(result)
                    progress.update(task, advance=1)
        else:
            for check in self.checks:
                result = self.run_check(check)
                self.results.append(result)
        
        self.logger.info(f"Completed {len(self.results)} diagnostic checks")
        return self.results
    
    def get_results(self) -> List[CheckResult]:
        """Get the results from the last run.
        
        Returns:
            List of CheckResult
        """
        return self.results
    
    def get_results_by_status(self, status: Status) -> List[CheckResult]:
        """Get results filtered by status.
        
        Args:
            status: Status to filter by
            
        Returns:
            List of CheckResult with matching status
        """
        return [r for r in self.results if r.status == status]
    
    def get_overall_status(self) -> Status:
        """Determine overall system health status.
        
        Returns:
            Overall Status (PASS if all pass, WARNING if any warnings, FAIL if any failures)
        """
        if self.get_results_by_status(Status.FAIL):
            return Status.FAIL
        elif self.get_results_by_status(Status.WARNING):
            return Status.WARNING
        elif self.get_results_by_status(Status.PASS):
            return Status.PASS
        else:
            return Status.UNKNOWN
    
    def display_results(self) -> None:
        """Display diagnostic results using Rich console."""
        if not self.results:
            self.console.print_warning("No diagnostic results to display")
            return
        
        overall_status = self.get_overall_status()
        status_text = {
            Status.PASS: "PASS",
            Status.WARNING: "WARNING",
            Status.FAIL: "FAIL",
            Status.UNKNOWN: "UNKNOWN"
        }.get(overall_status, "UNKNOWN")
        
        status_color = {
            Status.PASS: "green",
            Status.WARNING: "yellow",
            Status.FAIL: "red",
            Status.UNKNOWN: "white"
        }.get(overall_status, "white")
        
        self.console.print_title("Diagnostic Results")
        self.console.print()
        
        # Overall status panel
        self.console.print(Panel.fit(
            f"[bold {status_color}]Overall Health: {status_text}[/bold {status_color}]",
            title="Summary"
        ))
        self.console.print()
        
        # Results table
        table = Table(title="Check Results", box=box.ROUNDED)
        table.add_column("Check", style="cyan", width=25)
        table.add_column("Status", style="bold", width=10)
        table.add_column("Details", style="white", width=50)
        table.add_column("Recommendation", style="dim", width=30)
        
        for result in self.results:
            status_color = {
                Status.PASS: "green",
                Status.WARNING: "yellow",
                Status.FAIL: "red",
                Status.UNKNOWN: "white"
            }.get(result.status, "white")
            
            table.add_row(
                result.name,
                f"[{status_color}]{result.status.value}[/{status_color}]",
                result.details,
                result.recommendation or ""
            )
        
        self.console.print(table)
        self.console.print()
        
        # Summary counts
        pass_count = len(self.get_results_by_status(Status.PASS))
        warning_count = len(self.get_results_by_status(Status.WARNING))
        fail_count = len(self.get_results_by_status(Status.FAIL))
        unknown_count = len(self.get_results_by_status(Status.UNKNOWN))
        
        summary_table = Table(box=box.SIMPLE)
        summary_table.add_column("Status", style="cyan")
        summary_table.add_column("Count", style="white")
        
        summary_table.add_row("PASS", f"[green]{pass_count}[/green]")
        summary_table.add_row("WARNING", f"[yellow]{warning_count}[/yellow]")
        summary_table.add_row("FAIL", f"[red]{fail_count}[/red]")
        summary_table.add_row("UNKNOWN", f"[white]{unknown_count}[/white]")
        
        self.console.print(summary_table)
    
    def export_results(self) -> List[Dict[str, Any]]:
        """Export results as list of dictionaries.
        
        Returns:
            List of dictionaries representing results
        """
        return [result.to_dict() for result in self.results]
    
    def run_and_display(self, show_progress: bool = True) -> List[CheckResult]:
        """Run all checks and display results.
        
        Args:
            show_progress: Whether to show progress bar
            
        Returns:
            List of CheckResult
        """
        self.discover_checks()
        self.run_all_checks(show_progress=show_progress)
        self.display_results()
        return self.results


def run_diagnostics(show_progress: bool = True) -> List[CheckResult]:
    """Convenience function to run diagnostics and display results.
    
    Args:
        show_progress: Whether to show progress bar
        
    Returns:
        List of CheckResult
    """
    engine = DiagnosticsEngine()
    return engine.run_and_display(show_progress=show_progress)
