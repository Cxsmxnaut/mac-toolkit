"""Cache clearing repair operation."""

import subprocess
import shutil
from datetime import datetime
from pathlib import Path
from ..utils.base import BaseRepair, RepairResult


class CacheClearRepair(BaseRepair):
    """Clear system and user caches to free up space and fix issues."""
    
    def __init__(self, require_confirmation: bool = True):
        """Initialize the cache clear repair.
        
        Args:
            require_confirmation: Whether to require user confirmation
        """
        super().__init__(require_confirmation)
        self.name = "Cache Clear"
    
    def execute_repair(self) -> RepairResult:
        """Execute cache clear repair.
        
        Returns:
            RepairResult with operation status
        """
        start_time = datetime.now()
        
        cache_dirs = [
            Path("~/Library/Caches").expanduser(),
            Path("/private/tmp"),
        ]
        
        cleared_count = 0
        errors = []
        
        try:
            for cache_dir in cache_dirs:
                if cache_dir.exists():
                    try:
                        # Remove cache contents
                        for item in cache_dir.iterdir():
                            if item.is_dir():
                                shutil.rmtree(item, ignore_errors=True)
                                cleared_count += 1
                            elif item.is_file():
                                item.unlink()
                                cleared_count += 1
                    except Exception as e:
                        errors.append(f"Error clearing {cache_dir}: {str(e)}")
            
            if errors:
                output = f"Cache partially cleared. Cleared {cleared_count} items. Errors: {len(errors)}"
                success = len(errors) < 3  # Allow some errors
                error = "; ".join(errors[:3])  # Include first few errors
            else:
                output = f"Cache cleared successfully. Cleared {cleared_count} items."
                success = True
                error = None
            
        except Exception as e:
            output = "Unexpected error during cache clear"
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
