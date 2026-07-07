"""Comprehensive system information collection for Mac Toolkit."""

import platform
import subprocess
from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from .console import get_console
from .utils.logger import get_logger
from .utils.macos import get_efi_identifier, get_wifi_interface


@dataclass
class SystemInfo:
    """Comprehensive system information data structure."""
    model: str
    board_id: Optional[str]
    serial_number: str
    cpu: str
    cpu_cores: int
    gpu: List[str]
    ram_gb: int
    storage_devices: List[Dict[str, Any]]
    disk_usage: Dict[str, Any]
    battery: Optional[Dict[str, Any]]
    wifi: Optional[Dict[str, Any]]
    bluetooth: Optional[Dict[str, Any]]
    ethernet: Optional[Dict[str, Any]]
    thunderbolt: List[str]
    usb_devices: List[str]
    macos_version: str
    kernel_version: str
    filevault_status: str
    sip_status: str
    secure_boot_status: str
    apfs_info: Optional[Dict[str, Any]]
    oclp_version: Optional[str]
    efi_info: Optional[Dict[str, Any]]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "model": self.model,
            "board_id": self.board_id,
            "serial_number": self.serial_number,
            "cpu": self.cpu,
            "cpu_cores": self.cpu_cores,
            "gpu": self.gpu,
            "ram_gb": self.ram_gb,
            "storage_devices": self.storage_devices,
            "disk_usage": self.disk_usage,
            "battery": self.battery,
            "wifi": self.wifi,
            "bluetooth": self.bluetooth,
            "ethernet": self.ethernet,
            "thunderbolt": self.thunderbolt,
            "usb_devices": self.usb_devices,
            "macos_version": self.macos_version,
            "kernel_version": self.kernel_version,
            "filevault_status": self.filevault_status,
            "sip_status": self.sip_status,
            "secure_boot_status": self.secure_boot_status,
            "apfs_info": self.apfs_info,
            "oclp_version": self.oclp_version,
            "efi_info": self.efi_info
        }


class SystemInfoCollector:
    """Collector for comprehensive system information."""
    
    def __init__(self):
        """Initialize the system information collector."""
        self.console = get_console()
        self.logger = get_logger()
    
    def _run_command(self, command: str) -> Optional[str]:
        """Run a shell command and return output.
        
        Args:
            command: Shell command to execute
            
        Returns:
            Command output or None if failed
        """
        try:
            result = subprocess.check_output(
                command,
                shell=True,
                text=True,
                stderr=subprocess.DEVNULL
            ).strip()
            return result if result else None
        except subprocess.CalledProcessError:
            return None
        except Exception as e:
            self.logger.debug(f"Command failed: {command} - {e}")
            return None
    
    def _get_model(self) -> str:
        """Get Mac model identifier."""
        return self._run_command("sysctl -n hw.model") or "Unknown"
    
    def _get_board_id(self) -> Optional[str]:
        """Get board ID."""
        return self._run_command("sysctl -n hw.targettype")
    
    def _get_serial_number(self) -> str:
        """Get serial number."""
        return self._run_command("system_profiler SPHardwareDataType | grep 'Serial Number' | awk '{print $4}'") or "Unknown"
    
    def _get_cpu(self) -> tuple[str, int]:
        """Get CPU information and core count."""
        cpu = self._run_command("sysctl -n machdep.cpu.brand_string")
        if not cpu:
            cpu = platform.processor() or "Apple Silicon"
        
        cores = self._run_command("sysctl -n hw.ncpu")
        core_count = int(cores) if cores else 0
        
        return cpu, core_count
    
    def _get_gpu(self) -> List[str]:
        """Get GPU information."""
        gpus = []
        output = self._run_command("system_profiler SPDisplaysDataType | grep 'Chipset Model'")
        if output:
            for line in output.split('\n'):
                gpu = line.split(':')[-1].strip()
                if gpu:
                    gpus.append(gpu)
        return gpus if gpus else ["Unknown"]
    
    def _get_ram(self) -> int:
        """Get RAM in GB."""
        ram = self._run_command("sysctl -n hw.memsize")
        if ram:
            try:
                return int(ram) // (1024 ** 3)
            except ValueError:
                pass
        return 0
    
    def _get_storage_devices(self) -> List[Dict[str, Any]]:
        """Get storage device information."""
        devices = []
        output = self._run_command("diskutil list")
        if output:
            lines = output.split('\n')
            for line in lines:
                if '/dev/disk' in line:
                    device_info = line.strip()
                    devices.append({"device": device_info})
        return devices
    
    def _get_disk_usage(self) -> Dict[str, Any]:
        """Get disk usage information."""
        output = self._run_command("df -h /")
        if output:
            lines = output.split('\n')
            if len(lines) > 1:
                parts = lines[1].split()
                if len(parts) >= 5:
                    return {
                        "filesystem": parts[0],
                        "size": parts[1],
                        "used": parts[2],
                        "available": parts[3],
                        "capacity_percent": parts[4],
                        "mount_point": parts[5] if len(parts) > 5 else "/"
                    }
        return {}
    
    def _get_battery(self) -> Optional[Dict[str, Any]]:
        """Get battery information."""
        output = self._run_command("pmset -g batt")
        if output:
            return {"status": output}
        return None
    
    def _get_wifi(self) -> Optional[Dict[str, Any]]:
        """Get Wi-Fi information."""
        interface = get_wifi_interface()
        output = self._run_command(f"networksetup -getairportpower {interface}")
        if output:
            return {"interface": interface, "power_status": output}
        return None
    
    def _get_bluetooth(self) -> Optional[Dict[str, Any]]:
        """Get Bluetooth information."""
        output = self._run_command("system_profiler SPBluetoothDataType | grep 'State:'")
        if output:
            return {"state": output.split(':')[-1].strip()}
        return None
    
    def _get_ethernet(self) -> Optional[Dict[str, Any]]:
        """Get Ethernet information."""
        hardware_ports = self._run_command("networksetup -listallhardwareports") or ""
        lines = hardware_ports.splitlines()
        for index, line in enumerate(lines):
            if "Ethernet" not in line and "LAN" not in line:
                continue
            interface = None
            for next_line in lines[index + 1 : index + 4]:
                if "Device:" in next_line:
                    interface = next_line.split(":", 1)[1].strip()
                    break
            if not interface:
                continue
            output = self._run_command(f"ifconfig {interface}")
            if output and "status: active" in output.lower():
                return {"interface": interface, "status": "active"}
        return None
    
    def _get_thunderbolt(self) -> List[str]:
        """Get Thunderbolt device information."""
        output = self._run_command("system_profiler SPThunderboltDataType")
        if output:
            devices = []
            for line in output.split('\n'):
                if 'Device Name:' in line or 'Vendor Name:' in line:
                    devices.append(line.strip())
            return devices
        return []
    
    def _get_usb_devices(self) -> List[str]:
        """Get USB device information."""
        output = self._run_command("system_profiler SPUSBDataType")
        if output:
            devices = []
            for line in output.split('\n'):
                if 'Product ID:' in line or 'Vendor ID:' in line:
                    devices.append(line.strip())
            return devices
        return []
    
    def _get_macos_version(self) -> str:
        """Get macOS version."""
        return self._run_command("sw_vers -productVersion") or "Unknown"
    
    def _get_kernel_version(self) -> str:
        """Get kernel version."""
        return self._run_command("uname -r") or "Unknown"
    
    def _get_filevault_status(self) -> str:
        """Get FileVault status."""
        output = self._run_command("fdesetup status")
        return output or "Unknown"
    
    def _get_sip_status(self) -> str:
        """Get System Integrity Protection status."""
        output = self._run_command("csrutil status")
        return output or "Unknown"
    
    def _get_secure_boot_status(self) -> str:
        """Get Secure Boot status."""
        output = self._run_command("bputil -d")
        return output or "Unknown"
    
    def _get_apfs_info(self) -> Optional[Dict[str, Any]]:
        """Get APFS information."""
        output = self._run_command("diskutil apfs list")
        if output:
            return {"info": output[:500]}  # Truncate for brevity
        return None
    
    def _get_oclp_version(self) -> Optional[str]:
        """Get OpenCore Legacy Patcher version if installed."""
        output = self._run_command("/usr/local/bin/opencore-legacy-patcher --version 2>/dev/null")
        return output
    
    def _get_efi_info(self) -> Optional[Dict[str, Any]]:
        """Get EFI information."""
        efi = get_efi_identifier()
        output = self._run_command(f"diskutil info {efi}")
        if output:
            return {"identifier": efi, "info": output}
        return None
    
    def collect(self) -> SystemInfo:
        """Collect all system information.
        
        Returns:
            SystemInfo dataclass with all collected information
        """
        self.logger.info("Collecting system information")
        
        return SystemInfo(
            model=self._get_model(),
            board_id=self._get_board_id(),
            serial_number=self._get_serial_number(),
            cpu=self._get_cpu()[0],
            cpu_cores=self._get_cpu()[1],
            gpu=self._get_gpu(),
            ram_gb=self._get_ram(),
            storage_devices=self._get_storage_devices(),
            disk_usage=self._get_disk_usage(),
            battery=self._get_battery(),
            wifi=self._get_wifi(),
            bluetooth=self._get_bluetooth(),
            ethernet=self._get_ethernet(),
            thunderbolt=self._get_thunderbolt(),
            usb_devices=self._get_usb_devices(),
            macos_version=self._get_macos_version(),
            kernel_version=self._get_kernel_version(),
            filevault_status=self._get_filevault_status(),
            sip_status=self._get_sip_status(),
            secure_boot_status=self._get_secure_boot_status(),
            apfs_info=self._get_apfs_info(),
            oclp_version=self._get_oclp_version(),
            efi_info=self._get_efi_info()
        )
    
    def display(self, info: SystemInfo) -> None:
        """Display system information using Rich console.
        
        Args:
            info: SystemInfo to display
        """
        from rich.table import Table
        from rich.panel import Panel
        from rich import box
        
        self.console.print_title("System Information")
        self.console.print()
        
        # Hardware table
        hardware_table = Table(title="Hardware", box=box.ROUNDED)
        hardware_table.add_column("Property", style="cyan")
        hardware_table.add_column("Value", style="white")
        
        hardware_table.add_row("Model", info.model)
        if info.board_id:
            hardware_table.add_row("Board ID", info.board_id)
        hardware_table.add_row("Serial Number", info.serial_number)
        hardware_table.add_row("CPU", info.cpu)
        hardware_table.add_row("CPU Cores", str(info.cpu_cores))
        hardware_table.add_row("GPU", ", ".join(info.gpu))
        hardware_table.add_row("RAM", f"{info.ram_gb} GB")
        
        self.console.print(hardware_table)
        self.console.print()
        
        # Software table
        software_table = Table(title="Software", box=box.ROUNDED)
        software_table.add_column("Property", style="cyan")
        software_table.add_column("Value", style="white")
        
        software_table.add_row("macOS Version", info.macos_version)
        software_table.add_row("Kernel Version", info.kernel_version)
        software_table.add_row("FileVault", info.filevault_status)
        software_table.add_row("SIP", info.sip_status)
        software_table.add_row("Secure Boot", info.secure_boot_status)
        
        if info.oclp_version:
            software_table.add_row("OCLP Version", info.oclp_version)
        
        self.console.print(software_table)
        self.console.print()
        
        # Storage table
        if info.disk_usage:
            storage_table = Table(title="Storage", box=box.ROUNDED)
            storage_table.add_column("Property", style="cyan")
            storage_table.add_column("Value", style="white")
            
            for key, value in info.disk_usage.items():
                storage_table.add_row(key.replace('_', ' ').title(), str(value))
            
            self.console.print(storage_table)
            self.console.print()
        
        # Network table
        network_table = Table(title="Network", box=box.ROUNDED)
        network_table.add_column("Interface", style="cyan")
        network_table.add_column("Status", style="white")
        
        if info.wifi:
            network_table.add_row("Wi-Fi", info.wifi.get("power_status", "Unknown"))
        if info.bluetooth:
            network_table.add_row("Bluetooth", info.bluetooth.get("state", "Unknown"))
        if info.ethernet:
            network_table.add_row("Ethernet", info.ethernet.get("status", "Unknown"))
        
        self.console.print(network_table)


def get_system_info() -> SystemInfo:
    """Get comprehensive system information.
    
    Returns:
        SystemInfo dataclass
    """
    collector = SystemInfoCollector()
    return collector.collect()


def display_system_info() -> None:
    """Display system information to the console."""
    collector = SystemInfoCollector()
    info = collector.collect()
    collector.display(info)
