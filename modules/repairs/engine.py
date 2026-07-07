"""Repair engine for running repair operations."""

import importlib
import pkgutil
from pathlib import Path
from typing import List, Optional
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeRemainingColumn
from rich import box

from ..console import get_console
from ..utils.logger import get_logger
from ..utils.base import RepairResult, BaseRepair


class RepairEngine:
    """Engine for running repair operations."""
    
    def __init__(self, repairs_dir: Optional[str] = None):
        """Initialize the repair engine.
        
        Args:
            repairs_dir: Directory containing repair modules
        """
        self.repairs_dir = Path(repairs_dir) if repairs_dir else Path(__file__).resolve().parent
        self.console = get_console()
        self.logger = get_logger()
        self.repairs: List[BaseRepair] = []
        self.results: List[RepairResult] = []
    
    def discover_repairs(self) -> None:
        """Discover all repair modules in the repairs directory."""
        self.logger.info("Discovering repair operations")
        self.repairs = []
        
        if not self.repairs_dir.exists():
            self.logger.warning(f"Repairs directory not found: {self.repairs_dir}")
            return
        
        # Import all modules in the repairs directory
        for finder, name, _ in pkgutil.iter_modules([str(self.repairs_dir)]):
            try:
                module = importlib.import_module(f"modules.repairs.{name}")
                
                # Find all classes that inherit from BaseRepair
                for attr_name in dir(module):
                    if attr_name.startswith('_'):
                        continue
                    attr = getattr(module, attr_name)
                    try:
                        if (isinstance(attr, type) and 
                            issubclass(attr, BaseRepair) and 
                            attr is not BaseRepair):
                            repair_instance = attr()
                            self.repairs.append(repair_instance)
                            self.logger.debug(f"Discovered repair: {repair_instance.name}")
                    except TypeError:
                        continue
            except Exception as e:
                self.logger.error(f"Failed to load repair module {name}: {e}")
        
        self.logger.info(f"Discovered {len(self.repairs)} repair operations")
    
    def run_repair(self, repair: BaseRepair) -> RepairResult:
        """Run a single repair operation.
        
        Args:
            repair: BaseRepair instance to run
            
        Returns:
            RepairResult from the repair
        """
        self.logger.debug(f"Running repair: {repair.name}")
        return repair.execute()
    
    def run_all_repairs(self, show_progress: bool = True, auto_confirm: bool = False) -> List[RepairResult]:
        """Run all discovered repair operations.
        
        Args:
            show_progress: Whether to show progress bar
            auto_confirm: Whether to auto-confirm all repairs
            
        Returns:
            List of RepairResult from all repairs
        """
        self.logger.info(f"Running {len(self.repairs)} repair operations")
        self.results = []
        
        # Set auto-confirm on all repairs if requested
        if auto_confirm:
            for repair in self.repairs:
                repair.require_confirmation = False
        
        if show_progress:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                TimeRemainingColumn(),
                console=self.console.console
            ) as progress:
                task = progress.add_task("Running repairs...", total=len(self.repairs))
                
                for repair in self.repairs:
                    result = self.run_repair(repair)
                    self.results.append(result)
                    progress.update(task, advance=1)
        else:
            for repair in self.repairs:
                result = self.run_repair(repair)
                self.results.append(result)
        
        self.logger.info(f"Completed {len(self.results)} repair operations")
        return self.results

    def run_safe_repairs(self, show_progress: bool = True) -> List[RepairResult]:
        """Run repairs that do not require interactive confirmation."""
        if not self.repairs:
            self.discover_repairs()
        self.repairs = [repair for repair in self.repairs if not repair.require_confirmation]
        return self.run_all_repairs(show_progress=show_progress, auto_confirm=True)
    
    def get_results(self) -> List[RepairResult]:
        """Get the results from the last run.
        
        Returns:
            List of RepairResult
        """
        return self.results
    
    def get_successful_repairs(self) -> List[RepairResult]:
        """Get successful repair results.
        
        Returns:
            List of successful RepairResult
        """
        return [r for r in self.results if r.success]
    
    def get_failed_repairs(self) -> List[RepairResult]:
        """Get failed repair results.
        
        Returns:
            List of failed RepairResult
        """
        return [r for r in self.results if not r.success]
    
    def display_results(self) -> None:
        """Display repair results using Rich console."""
        if not self.results:
            self.console.print_warning("No repair results to display")
            return
        
        successful = len(self.get_successful_repairs())
        failed = len(self.get_failed_repairs())
        
        self.console.print_title("Repair Results")
        self.console.print()
        
        # Summary panel
        self.console.print(Panel.fit(
            f"[green]Successful: {successful}[/green] | [red]Failed: {failed}[/red]",
            title="Summary"
        ))
        self.console.print()
        
        # Results table
        table = Table(title="Repair Operations", box=box.ROUNDED)
        table.add_column("Repair", style="cyan", width=25)
        table.add_column("Status", style="bold", width=10)
        table.add_column("Duration", style="white", width=10)
        table.add_column("Output", style="dim", width=50)
        
        for result in self.results:
            status = "[green]✓ Success[/green]" if result.success else "[red]✗ Failed[/red]"
            duration = f"{result.duration:.2f}s"
            output = result.output[:50] + "..." if len(result.output) > 50 else result.output
            
            table.add_row(
                result.name,
                status,
                duration,
                output
            )
        
        self.console.print(table)
        self.console.print()
        
        # Failed repairs details
        if failed > 0:
            self.console.print_error(f"{failed} repair(s) failed:")
            for result in self.get_failed_repairs():
                if result.error:
                    self.console.print(f"  - {result.name}: {result.error}")
    
    def export_results(self) -> List[dict]:
        """Export results as list of dictionaries.
        
        Returns:
            List of dictionaries representing results
        """
        return [result.to_dict() for result in self.results]


def run_repairs(show_progress: bool = True, auto_confirm: bool = False) -> List[RepairResult]:
    """Convenience function to run repairs and display results.
    
    Args:
        show_progress: Whether to show progress bar
        auto_confirm: Whether to auto-confirm all repairs
        
    Returns:
        List of RepairResult
    """
    engine = RepairEngine()
    engine.discover_repairs()
    engine.run_all_repairs(show_progress=show_progress, auto_confirm=auto_confirm)
    engine.display_results()
    return engine.results


def run_safe_repairs(show_progress: bool = True) -> List[RepairResult]:
    """Run only non-interactive safe repairs and display results."""
    engine = RepairEngine()
    engine.discover_repairs()
    engine.run_safe_repairs(show_progress=show_progress)
    engine.display_results()
    return engine.results
