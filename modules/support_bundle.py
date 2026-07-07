"""Support bundle generation."""

from __future__ import annotations

import json
import re
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Any

from .diagnostics_engine import DiagnosticsEngine
from .report.generator import generate_reports
from .system import get_system_info
from .utils.macos import app_support_dir, logs_dir


def _redact_text(value: str, replacements: dict[str, str]) -> str:
    """Redact sensitive values from text."""
    redacted = value
    for source, replacement in replacements.items():
        if source:
            redacted = redacted.replace(source, replacement)
    redacted = re.sub(r"\b([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}\b", "<mac-address>", redacted)
    redacted = re.sub(r"\b\d{1,3}(?:\.\d{1,3}){3}\b", "<ip-address>", redacted)
    return redacted


def _redact_obj(value: Any, replacements: dict[str, str]) -> Any:
    """Recursively redact text values in JSON-like objects."""
    if isinstance(value, str):
        return _redact_text(value, replacements)
    if isinstance(value, list):
        return [_redact_obj(item, replacements) for item in value]
    if isinstance(value, dict):
        return {key: _redact_obj(item, replacements) for key, item in value.items()}
    return value


def create_support_bundle(*, redact: bool = False) -> Path:
    """Create a zip support bundle with diagnostics, reports, and logs."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    bundle_dir = app_support_dir() / "Support Bundles"
    bundle_dir.mkdir(parents=True, exist_ok=True)
    bundle_path = bundle_dir / f"mactoolkit_support_{timestamp}.zip"

    system_info = get_system_info()
    engine = DiagnosticsEngine()
    results = engine.run_and_display(show_progress=False)
    report_files = generate_reports(results, system_info, formats=["txt", "json", "html"])

    replacements: dict[str, str] = {}
    if redact:
        replacements = {
            str(Path.home()): "~",
            Path.home().name: "<user>",
            system_info.serial_number: "<serial-number>",
        }

    diagnostics = [result.to_dict() for result in results]
    system_payload = system_info.to_dict()
    if redact:
        diagnostics = _redact_obj(diagnostics, replacements)
        system_payload = _redact_obj(system_payload, replacements)

    with zipfile.ZipFile(bundle_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("system_info.json", json.dumps(system_payload, indent=2))
        archive.writestr("diagnostics.json", json.dumps(diagnostics, indent=2))

        for report_type, path in report_files.items():
            content = path.read_text(errors="replace")
            if redact:
                content = _redact_text(content, replacements)
            archive.writestr(f"reports/{path.name}", content)

        for log_file in sorted(logs_dir().glob("mactoolkit_*.log"))[-5:]:
            content = log_file.read_text(errors="replace")
            if redact:
                content = _redact_text(content, replacements)
            archive.writestr(f"logs/{log_file.name}", content)

        archive.writestr(
            "README.txt",
            "Mac Toolkit support bundle. Review contents before sharing externally.\n"
            f"Redaction enabled: {redact}\n",
        )

    return bundle_path
