"""Stress test command helpers."""

from .stress_engine import run_stress_tests


def stress():
    """Run stress tests from the interactive menu."""
    run_stress_tests(show_progress=True)
