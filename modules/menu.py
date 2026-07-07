"""Main menu module for Mac Toolkit."""

from .system import display_system_info
from .diagnostics import diagnostics
from .console import get_console
from .auto_service import run_auto_service
from .diagnostics_engine import run_diagnostics
from .repairs.engine import run_repairs
from .report.generator import generate_reports
from .system import get_system_info
from .stress_engine import run_stress_tests
from .utils.config import get_config


def main_menu():
    """Display and handle the main menu."""
    console = get_console()
    
    while True:
        console.clear()

        console.print_title("MAC TOOLKIT")
        console.print()

        console.print("1) Auto Service")
        console.print("2) Diagnostics")
        console.print("3) Repair Tools")
        console.print("4) Stress Tests")
        console.print("5) Benchmarks")
        console.print("6) System Information")
        console.print("7) Reports")
        console.print("8) Settings")
        console.print("9) Exit")
        console.print()

        choice = input("Select an option: ")

        if choice == "1":
            console.clear()
            run_auto_service()
            input("\nPress Enter...")

        elif choice == "2":
            console.clear()
            diagnostics()
            input("\nPress Enter...")

        elif choice == "3":
            console.clear()
            run_repairs(show_progress=True)
            input("\nPress Enter...")

        elif choice == "4":
            console.clear()
            run_stress_tests(show_progress=True)
            input("\nPress Enter...")

        elif choice == "5":
            console.clear()
            console.print_info("Benchmarks coming soon...")
            input("\nPress Enter...")

        elif choice == "6":
            console.clear()
            display_system_info()
            input("\nPress Enter to continue...")

        elif choice == "7":
            console.clear()
            results = run_diagnostics(show_progress=True)
            files = generate_reports(results, get_system_info())
            console.print_header("Reports generated")
            for format_name, path in files.items():
                console.print_key_value(format_name.upper(), str(path))
            input("\nPress Enter...")

        elif choice == "8":
            console.clear()
            config = get_config()
            console.print_header("Settings")
            for key, value in config.get_all().items():
                console.print_key_value(key, str(value))
            input("\nPress Enter...")

        elif choice == "9":
            break

        else:
            console.print_warning("Invalid option")
            input("\nPress Enter...")
