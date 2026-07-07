"""Mac Toolkit command-line entry point."""

from __future__ import annotations

import argparse
import sys

from modules.auto_service import run_auto_service
from modules.diagnostics_engine import run_diagnostics
from modules.menu import main_menu
from modules.repairs.engine import run_repairs
from modules.report.generator import generate_reports
from modules.system import display_system_info, get_system_info


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser."""
    parser = argparse.ArgumentParser(
        prog="mactoolkit",
        description="One-command macOS diagnostics and OpenCore readiness checks.",
    )
    subparsers = parser.add_subparsers(dest="command")

    run_parser = subparsers.add_parser("run", help="Run full diagnostics and generate reports")
    run_parser.add_argument(
        "--formats",
        nargs="+",
        choices=["txt", "json", "html", "pdf"],
        default=["txt", "json", "html", "pdf"],
        help="Report formats to generate",
    )
    run_parser.add_argument("--repairs", action="store_true", help="Offer repair operations after diagnostics")
    run_parser.add_argument("--auto-confirm-repairs", action="store_true", help="Run repairs without prompting")
    run_parser.add_argument("--no-progress", action="store_true", help="Disable progress bars")

    subparsers.add_parser("diagnostics", help="Run diagnostics only")
    subparsers.add_parser("system", help="Show system information")

    report_parser = subparsers.add_parser("report", help="Run diagnostics and generate reports")
    report_parser.add_argument(
        "--formats",
        nargs="+",
        choices=["txt", "json", "html", "pdf"],
        default=["txt", "json", "html", "pdf"],
    )

    repairs_parser = subparsers.add_parser("repairs", help="Run repair tools")
    repairs_parser.add_argument("--auto-confirm", action="store_true")

    subparsers.add_parser("stress", help="Run stress tests")

    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the CLI or interactive menu."""
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command is None:
        main_menu()
        return 0

    if args.command == "run":
        return run_auto_service(
            formats=args.formats,
            run_repairs_after=args.repairs,
            auto_confirm_repairs=args.auto_confirm_repairs,
            show_progress=not args.no_progress,
        )

    if args.command == "diagnostics":
        run_diagnostics(show_progress=True)
        return 0

    if args.command == "system":
        display_system_info()
        return 0

    if args.command == "report":
        results = run_diagnostics(show_progress=True)
        files = generate_reports(results, get_system_info(), formats=args.formats)
        for format_name, path in files.items():
            print(f"{format_name}: {path}")
        return 0

    if args.command == "repairs":
        run_repairs(show_progress=True, auto_confirm=args.auto_confirm)
        return 0

    if args.command == "stress":
        from modules.stress_engine import run_stress_tests

        run_stress_tests(show_progress=True)
        return 0

    parser.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
