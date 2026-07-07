"""Stability diagnostic check."""

from __future__ import annotations

from pathlib import Path

from ..utils.base import BaseCheck, CheckResult, Status


class StabilityCheck(BaseCheck):
    """Check recent panic, crash, and hang reports."""

    def _count_reports(self, pattern: str, days: int) -> list[str]:
        roots = [
            Path("/Library/Logs/DiagnosticReports"),
            Path.home() / "Library" / "Logs" / "DiagnosticReports",
        ]
        reports: list[str] = []
        for root in roots:
            if not root.exists():
                continue
            for path in root.glob(pattern):
                try:
                    age_seconds = max(0.0, __import__("time").time() - path.stat().st_mtime)
                except OSError:
                    continue
                if age_seconds <= days * 86400:
                    reports.append(path.name)
        return sorted(reports)

    def run(self) -> CheckResult:
        panic_reports = self._count_reports("*panic*", 7) + self._count_reports("*.panic", 7)
        crash_reports = self._count_reports("*.crash", 1)
        hang_reports = self._count_reports("*.hang", 1)

        details = (
            f"panic_7d={len(panic_reports)}, "
            f"crash_24h={len(crash_reports)}, hang_24h={len(hang_reports)}"
        )
        metadata = {
            "panic_reports": panic_reports[:10],
            "crash_reports": crash_reports[:10],
            "hang_reports": hang_reports[:10],
        }

        if panic_reports:
            return CheckResult(
                name="Stability",
                status=Status.FAIL,
                details=details,
                recommendation="Review recent panic reports before returning the Mac to service",
                metadata=metadata,
            )

        if len(crash_reports) >= 5 or len(hang_reports) >= 5:
            return CheckResult(
                name="Stability",
                status=Status.WARNING,
                details=details,
                recommendation="Review recent crash or hang reports for repeating app/system failures",
                metadata=metadata,
            )

        return CheckResult(
            name="Stability",
            status=Status.PASS,
            details=details,
            recommendation="No recent panic or high-volume crash/hang pattern found",
            metadata=metadata,
        )
