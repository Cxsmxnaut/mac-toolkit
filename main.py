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
from modules.support_bundle import create_support_bundle


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
    subparsers.add_parser("auto", help="Alias for run")
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

    support_parser = subparsers.add_parser("support-bundle", help="Create a support bundle zip")
    support_parser.add_argument("--redact", action="store_true", help="Redact common identifiers")

    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the CLI or interactive menu."""
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command is None:
        main_menu()
        return 0

    if args.command in {"run", "auto"}:
        return run_auto_service(
            formats=getattr(args, "formats", ["txt", "json", "html", "pdf"]),
            run_repairs_after=getattr(args, "repairs", False),
            auto_confirm_repairs=getattr(args, "auto_confirm_repairs", False),
            show_progress=not getattr(args, "no_progress", False),
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

    if args.command == "support-bundle":
        bundle = create_support_bundle(redact=args.redact)
        print(f"Support bundle: {bundle}")
        return 0

    parser.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
