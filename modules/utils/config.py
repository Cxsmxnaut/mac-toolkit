"""Configuration management system for Mac Toolkit."""

import json
from pathlib import Path
from typing import Any, Dict, Optional


class Config:
    """Configuration manager with JSON storage."""
    
    DEFAULT_CONFIG = {
        "stress": {
            "duration_seconds": 300,
            "temperature_limit_cpu": 90,
            "temperature_limit_gpu": 85,
            "abort_on_threshold": True
        },
        "reports": {
            "formats": ["txt", "json"],
            "auto_generate": True,
            "save_location": "reports"
        },
        "auto_service": {
            "auto_repair": False,
            "require_confirmation": True,
            "run_stress_tests": False,
            "verify_repairs": True
        },
        "logging": {
            "verbosity": "INFO",
            "log_to_file": True,
            "log_location": "logs"
        },
        "ui": {
            "color_scheme": "default",
            "show_progress_bars": True,
            "live_updates": True
        }
    }
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize configuration manager.
        
        Args:
            config_path: Path to config file. Defaults to ~/.mactoolkit/config.json
        """
        if config_path is None:
            config_dir = Path.home() / ".mactoolkit"
            config_dir.mkdir(parents=True, exist_ok=True)
            self.config_path = config_dir / "config.json"
        else:
            self.config_path = Path(config_path)
        
        self.config: Dict[str, Any] = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or create default."""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    loaded_config = json.load(f)
                # Merge with defaults to ensure all keys exist
                return self._merge_config(self.DEFAULT_CONFIG, loaded_config)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Could not load config file, using defaults: {e}")
                return self.DEFAULT_CONFIG.copy()
        else:
            self._save_config(self.DEFAULT_CONFIG)
            return self.DEFAULT_CONFIG.copy()
    
    def _merge_config(self, default: Dict[str, Any], loaded: Dict[str, Any]) -> Dict[str, Any]:
        """Merge loaded config with defaults, preserving new keys."""
        result = default.copy()
        for key, value in loaded.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_config(result[key], value)
            else:
                result[key] = value
        return result
    
    def _save_config(self, config: Dict[str, Any]) -> None:
        """Save configuration to file."""
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=2)
        except IOError as e:
            print(f"Warning: Could not save config file: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key (supports nested keys with dots).
        
        Args:
            key: Configuration key (e.g., 'stress.duration_seconds')
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        keys = key.split('.')
        value = self.config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value by key (supports nested keys with dots).
        
        Args:
            key: Configuration key (e.g., 'stress.duration_seconds')
            value: Value to set
        """
        keys = key.split('.')
        config = self.config
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value
        self._save_config(self.config)
    
    def save(self) -> None:
        """Manually save current configuration."""
        self._save_config(self.config)
    
    def reset_to_defaults(self) -> None:
        """Reset configuration to default values."""
        self.config = self.DEFAULT_CONFIG.copy()
        self._save_config(self.config)
    
    def get_all(self) -> Dict[str, Any]:
        """Get entire configuration dictionary."""
        return self.config.copy()


# Global config instance
_config_instance: Optional[Config] = None


def get_config(config_path: Optional[str] = None) -> Config:
    """Get or create the global configuration instance.
    
    Args:
        config_path: Optional path to config file
        
    Returns:
        Config instance
    """
    global _config_instance
    if _config_instance is None:
        _config_instance = Config(config_path)
    return _config_instance
