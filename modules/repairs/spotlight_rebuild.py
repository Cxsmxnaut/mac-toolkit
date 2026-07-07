"""Spotlight rebuild repair operation."""

import subprocess
from datetime import datetime
from ..utils.base import BaseRepair, RepairResult


class SpotlightRebuildRepair(BaseRepair):
    """Rebuild Spotlight index to fix search issues."""
    
    def __init__(self, require_confirmation: bool = True):
        """Initialize the Spotlight rebuild repair.
        
        Args:
            require_confirmation: Whether to require user confirmation
        """
        super().__init__(require_confirmation)
        self.name = "Spotlight Rebuild"
    
    def execute_repair(self) -> RepairResult:
        """Execute Spotlight rebuild repair.
        
        Returns:
            RepairResult with operation status
        """
        start_time = datetime.now()
        
        try:
            # Disable Spotlight indexing
            subprocess.run(
                ["sudo", "mdutil", "-i", "off", "/"],
                capture_output=True
            )
            
            # Enable Spotlight indexing (this triggers rebuild)
            subprocess.run(
                ["sudo", "mdutil", "-i", "on", "/"],
                capture_output=True
            )
            
            # Erase and rebuild index
            subprocess.run(
                ["sudo", "mdutil", "-E", "/"],
                capture_output=True
            )
            
            output = "Spotlight index rebuild initiated. This may take some time to complete."
            success = True
            error = None
            
        except subprocess.CalledProcessError as e:
            output = f"Spotlight rebuild command failed"
            success = False
            error = str(e)
        except Exception as e:
            output = f"Unexpected error during Spotlight rebuild"
            success = False
            error = str(e)
        
        end_time = datetime.now()
        
        return RepairResult(
            name=self.name,
            success=success,
            start_time=start_time,
            end_time=end_time,
            output=output,
            error=error
        )
