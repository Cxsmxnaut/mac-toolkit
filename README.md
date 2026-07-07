# Mac Toolkit

Professional macOS diagnostics and repair utility for Intel and Apple Silicon Macs running macOS Monterey or newer.

## Features

### Diagnostics
- **CPU**: Processor information and core count
- **RAM**: Memory capacity and health
- **GPU**: Graphics hardware detection
- **Storage**: Disk usage and SMART status
- **APFS**: Filesystem health verification
- **Battery**: Charge level and health (portable Macs)
- **Wi-Fi**: Connection status and power state
- **Bluetooth**: Adapter status and state
- **FileVault**: Encryption status
- **SIP**: System Integrity Protection status
- **Secure Boot**: Boot security status
- **Software Updates**: Available updates detection
- **OpenCore Legacy Patcher**: Custom bootloader detection

### Repairs
- **DNS Flush**: Clear DNS cache to resolve network issues
- **Spotlight Rebuild**: Rebuild search index
- **Cache Clear**: Clean system and user caches

### Reports
- **TXT**: Plain text format
- **JSON**: Machine-readable format
- **HTML**: Professional web-ready format with styling
- **PDF**: Portable report format

### Health Scoring
- Calculates overall system health score (0-100)
- Provides PASS/WARNING/FAIL/READY FOR CUSTOMER/NOT READY status
- Generates actionable recommendations

## Installation

### Prerequisites
- Python 3.11+
- macOS Monterey or newer
- Administrator access (for some operations)

### Setup

1. Clone or download the repository:
```bash
cd mac-toolkit
```

2. Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Install the CLI command:
```bash
python3 -m pip install .
```

After installation:

```bash
mactoolkit
mactoolkit run --no-progress
```

### One-Line Install

From a local checkout:

```bash
cd mac-toolkit && ./install.sh
```

From GitHub after this branch is pushed:

```bash
python3 -m pip install "git+https://github.com/slolakap/mac-toolkit.git"
```

Then run:

```bash
mactoolkit run --no-progress
```

Or open **Mac Toolkit** from `/Applications` after installing the pkg.

### Build a macOS Installer Package

Download the latest installer from:

```text
https://github.com/Cxsmxnaut/mac-toolkit/releases/latest
```

Create a distributable `.pkg` installer:

```bash
./scripts/build_pkg.sh
```

The package is written to `dist/MacToolkit-<version>.pkg`. It installs Mac Toolkit to `/usr/local/lib/mac-toolkit`, creates an isolated virtual environment, places the `mactoolkit` command in `/usr/local/bin`, and installs `/Applications/Mac Toolkit.app`.

The installer bundles Python 3.11 from Python.org plus dependency wheels for offline installation. If the target Mac already has Python 3.11 or newer, the installer uses the existing interpreter. If not, it installs the bundled Python runtime first. If a bundled wheel is not compatible with the target Mac's Python version or CPU architecture, the postinstall script falls back to PyPI.

## Usage

### Run the Application

```bash
python3 main.py
```

If installed as a CLI:

```bash
mactoolkit
```

### Run a Full Service Pass

```bash
python3 main.py run
```

This is the recommended workflow for service intake. It collects system information, runs every diagnostic, can perform configured safe repairs and stress tests, prints action items, and writes TXT, JSON, HTML, and PDF reports to `reports/`.

For automation-friendly output:

```bash
python3 main.py run --no-progress --formats json html
```

### Direct Commands

```bash
python3 main.py diagnostics
python3 main.py repairs
python3 main.py stress
python3 main.py system
python3 main.py report --formats txt json html pdf
```

### Menu Options

1. **Auto Service** - Run full diagnostics and generate reports
2. **Diagnostics** - Run all diagnostic checks
3. **Repair Tools** - Execute repair operations with confirmation
4. **Stress Tests** - Run CPU, RAM, disk, GPU, and combined stress tests
5. **Benchmarks** - Performance benchmarking
6. **System Information** - Display comprehensive system details
7. **Reports** - Generate diagnostic reports
8. **Settings** - Display current toolkit configuration
9. **Exit** - Quit the application

## Project Structure

```
mac-toolkit/
├── main.py                 # Application entry point
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── venv/                  # Virtual environment (created during setup)
├── modules/
│   ├── __init__.py
│   ├── console.py          # Rich console utilities
│   ├── system.py          # System information collection
│   ├── diagnostics.py     # Diagnostics interface
│   ├── diagnostics_engine.py  # Diagnostic execution engine
│   ├── menu.py            # Main menu interface
│   ├── checks/            # Diagnostic check modules
│   │   ├── __init__.py
│   │   ├── cpu.py
│   │   ├── ram.py
│   │   ├── battery.py
│   │   ├── gpu.py
│   │   ├── storage.py
│   │   ├── apfs.py
│   │   ├── wifi.py
│   │   ├── bluetooth.py
│   │   ├── filevault.py
│   │   ├── sip.py
│   │   ├── secure_boot.py
│   │   ├── software_update.py
│   │   └── oclp.py
│   ├── repairs/           # Repair operation modules
│   │   ├── __init__.py
│   │   ├── engine.py
│   │   ├── dns_flush.py
│   │   ├── spotlight_rebuild.py
│   │   └── cache_clear.py
│   ├── report/            # Report generation
│   │   ├── __init__.py
│   │   └── generator.py
│   ├── stress_engine.py   # Stress test execution engine
│   ├── stress/            # Stress test package namespace
│   │   └── __init__.py
│   └── utils/             # Utility modules
│       ├── __init__.py
│       ├── base.py        # Base classes
│       ├── logger.py      # Logging system
│       ├── config.py      # Configuration management
│       └── health_score.py # Health scoring
├── reports/              # Generated reports
├── logs/                 # Application logs
└── assets/              # Static assets
```

## Configuration

Configuration is stored in `~/.mactoolkit/config.json`. Default settings include:

```json
{
  "stress": {
    "duration_seconds": 300,
    "temperature_limit_cpu": 90,
    "temperature_limit_gpu": 85,
    "abort_on_threshold": true
  },
  "reports": {
    "formats": ["txt", "json"],
    "auto_generate": true,
    "save_location": "reports"
  },
  "auto_service": {
    "auto_repair": false,
    "require_confirmation": true,
    "run_stress_tests": false,
    "verify_repairs": true
  },
  "logging": {
    "verbosity": "INFO",
    "log_to_file": true,
    "log_location": "logs"
  },
  "ui": {
    "color_scheme": "default",
    "show_progress_bars": true,
    "live_updates": true
  }
}
```

## Extending the Toolkit

### Adding a New Diagnostic Check

Create a new file in `modules/checks/`:

```python
"""Custom diagnostic check."""

import subprocess
from ..utils.base import BaseCheck, CheckResult, Status

class CustomCheck(BaseCheck):
    """Check custom component."""
    
    def run(self) -> CheckResult:
        """Run custom diagnostic check."""
        try:
            # Your diagnostic logic here
            result = subprocess.check_output(
                "your_command",
                shell=True,
                text=True,
                stderr=subprocess.DEVNULL
            ).strip()
            
            return CheckResult(
                name="Custom Check",
                status=Status.PASS,
                details=result,
                recommendation="Component is functioning normally"
            )
        except Exception as e:
            return CheckResult(
                name="Custom Check",
                status=Status.FAIL,
                details="Check failed",
                recommendation=str(e)
            )
```

The check will be automatically discovered and included in diagnostics.

### Adding a New Repair Operation

Create a new file in `modules/repairs/`:

```python
"""Custom repair operation."""

import subprocess
from datetime import datetime
from ..utils.base import BaseRepair, RepairResult

class CustomRepair(BaseRepair):
    """Perform custom repair."""
    
    def __init__(self, require_confirmation: bool = True):
        super().__init__(require_confirmation)
        self.name = "Custom Repair"
    
    def execute_repair(self) -> RepairResult:
        """Execute custom repair operation."""
        start_time = datetime.now()
        
        try:
            # Your repair logic here
            subprocess.run(
                ["sudo", "your_command"],
                capture_output=True
            )
            
            return RepairResult(
                name=self.name,
                success=True,
                start_time=start_time,
                end_time=datetime.now(),
                output="Repair completed successfully",
                error=None
            )
        except Exception as e:
            return RepairResult(
                name=self.name,
                success=False,
                start_time=start_time,
                end_time=datetime.now(),
                output="",
                error=str(e)
            )
```

## Health Scoring

The health scoring system evaluates diagnostic results and assigns a score (0-100):

- **90-100**: READY FOR CUSTOMER - System is in excellent condition
- **70-89**: PASS - System is healthy with minor issues
- **50-69**: WARNING - System has issues that should be addressed
- **0-49**: NOT READY - System has critical issues

Deductions are applied for:
- Battery below 80%, 50%, or 20%
- SMART failures
- High temperatures
- Storage nearly full (>80%) or critically full (>90%)
- Network issues
- Kernel panics
- Disabled security features (SIP, FileVault, Secure Boot)
- Pending software updates
- APFS errors
- Custom boot loaders (OpenCore)

## Logging

Logs are stored in `logs/mactoolkit_YYYYMMDD.log` with timestamps. Enable debug mode by modifying the configuration or passing debug flags.

## Requirements

- Python 3.11+
- rich==15.0.0

## License

This project is provided as-is for Mac repair professionals.

## Contributing

This toolkit is designed to be modular and extensible. Add new checks and repairs by following the patterns in existing modules.

## Support

For issues or questions, please refer to the diagnostic logs in the `logs/` directory.
# mac-toolkit
