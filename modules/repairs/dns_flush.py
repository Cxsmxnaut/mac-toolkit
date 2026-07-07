"""DNS flush repair operation."""

import subprocess
from datetime import datetime
from ..utils.base import BaseRepair, RepairResult


class DNSFlushRepair(BaseRepair):
    """Flush DNS cache to resolve network issues."""
    
    def __init__(self, require_confirmation: bool = True):
        """Initialize the DNS flush repair.
        
        Args:
            require_confirmation: Whether to require user confirmation
        """
        super().__init__(require_confirmation)
        self.name = "DNS Flush"
    
    def execute_repair(self) -> RepairResult:
        """Execute DNS flush repair.
        
        Returns:
            RepairResult with operation status
        """
        start_time = datetime.now()
        
        try:
            # Flush DNS cache
            result = subprocess.run(
                ["sudo", "dscacheutil", "-flushcache"],
                capture_output=True,
                text=True
            )
            
            # Also kill mDNSResponder
            subprocess.run(
                ["sudo", "killall", "-HUP", "mDNSResponder"],
                capture_output=True
            )
            
            output = "DNS cache flushed successfully"
            success = True
            error = None
            
        except subprocess.CalledProcessError as e:
            output = f"DNS flush command failed"
            success = False
            error = str(e)
        except Exception as e:
            output = f"Unexpected error during DNS flush"
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
