"""Diagnostics module using the diagnostic engine."""

from .diagnostics_engine import run_diagnostics


def diagnostics():
    """Run diagnostics and display results using the diagnostic engine."""
    run_diagnostics(show_progress=True)
