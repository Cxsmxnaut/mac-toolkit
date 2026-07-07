"""OpenCore post-install readiness checks."""

from __future__ import annotations

from pathlib import Path

from ..utils.base import BaseCheck, CheckResult, Status
from ..utils.macos import get_kernel_panic_count, run_command_output


class OpenCoreReadinessCheck(BaseCheck):
    """Check common newly OpenCore'd Mac readiness issues."""

    def run(self) -> CheckResult:
        findings: list[str] = []
        actions: list[str] = []
        metadata: dict[str, object] = {}

        model = run_command_output("sysctl -n hw.model") or "Unknown model"
        metadata["model"] = model

        boot_args = run_command_output("nvram boot-args 2>/dev/null") or ""
        if boot_args:
            metadata["boot_args"] = boot_args

        oclp_paths = [
            Path("/Applications/OpenCore-Patcher.app"),
            Path("/Library/Application Support/Dortania/OpenCore-Patcher"),
            Path("/usr/local/bin/opencore-legacy-patcher"),
        ]
        oclp_installed = any(path.exists() for path in oclp_paths)
        metadata["oclp_installed"] = oclp_installed
        if not oclp_installed:
            findings.append("OCLP app/CLI not found")
            actions.append("Install or keep OpenCore Legacy Patcher available for future root patching")

        csr = run_command_output("csrutil status") or ""
        metadata["sip"] = csr
        if "disabled" in csr.lower():
            findings.append("SIP is fully disabled")
            actions.append("Use the OCLP-recommended SIP/security profile rather than leaving SIP fully disabled")

        secure_boot = run_command_output("bputil -d 2>/dev/null") or ""
        metadata["secure_boot"] = secure_boot
        if "no security" in secure_boot.lower() or "disabled" in secure_boot.lower():
            findings.append("Secure Boot is reduced or disabled")

        snapshot = run_command_output("mount | grep ' / '") or ""
        metadata["root_mount"] = snapshot
        if snapshot and "sealed" not in snapshot.lower() and "read-only" not in snapshot.lower():
            findings.append("Root volume does not appear sealed/read-only")
            actions.append("Verify post-install root patches and APFS snapshot state")

        graphics = run_command_output(
            "system_profiler SPDisplaysDataType | grep -E 'Metal|Displays|Chipset Model|VRAM'"
        ) or ""
        metadata["graphics_summary"] = graphics
        if "metal" not in graphics.lower():
            findings.append("Metal support was not confirmed")
            actions.append("Run OCLP post-install root patches for graphics acceleration if this model requires them")

        audio = run_command_output(
            "system_profiler SPAudioDataType | grep -E 'Output|Input|Built-in|External' | head -10"
        ) or ""
        metadata["audio_summary"] = audio
        if not audio:
            findings.append("Audio devices were not detected")
            actions.append("Verify OCLP audio/root patches and test input/output devices")

        wifi = run_command_output("networksetup -listallhardwareports | grep -A2 -E 'Wi-Fi|AirPort'") or ""
        metadata["wifi_summary"] = wifi
        if not wifi:
            findings.append("Wi-Fi hardware port was not detected")
            actions.append("Verify Wi-Fi/Bluetooth hardware support and OCLP root patches")

        panic_count = get_kernel_panic_count()
        metadata["kernel_panics_30d"] = panic_count
        if panic_count >= 3:
            findings.append(f"{panic_count} panic log entries in the last 30 days")
            actions.append("Review panic logs before returning the Mac to service")

        if not findings:
            return CheckResult(
                name="OpenCore Readiness",
                status=Status.PASS,
                details=f"{model}: OpenCore post-install readiness checks passed",
                recommendation="Mac is ready for customer validation",
                metadata=metadata,
            )

        critical_terms = ("Metal", "Audio", "Wi-Fi")
        status = Status.FAIL if any(term in item for term in critical_terms for item in findings) else Status.WARNING
        return CheckResult(
            name="OpenCore Readiness",
            status=status,
            details="; ".join(findings),
            recommendation="; ".join(dict.fromkeys(actions)) or "Review OpenCore configuration",
            metadata=metadata,
        )
