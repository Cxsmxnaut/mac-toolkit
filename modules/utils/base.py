"""Base classes for diagnostics, repairs, and stress tests."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Dict, Any, Optional, List


class Status(Enum):
    """Status enumeration for check results."""
    PASS = "PASS"
    WARNING = "WARNING"
    FAIL = "FAIL"
    UNKNOWN = "UNKNOWN"


@dataclass
class CheckResult:
    """Result of a diagnostic check."""
    name: str
    status: Status
    details: str
    recommendation: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "name": self.name,
            "status": self.status.value,
            "details": self.details,
            "recommendation": self.recommendation,
            "metadata": self.metadata or {}
        }


@dataclass
class RepairResult:
    """Result of a repair operation."""
    name: str
    success: bool
    start_time: datetime
    end_time: datetime
    output: str
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    
    @property
    def duration(self) -> float:
        """Duration of repair in seconds."""
        return (self.end_time - self.start_time).total_seconds()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "name": self.name,
            "success": self.success,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat(),
            "duration": self.duration,
            "output": self.output,
            "error": self.error,
            "metadata": self.metadata or {}
        }


@dataclass
class StressTestResult:
    """Result of a stress test."""
    name: str
    success: bool
    start_time: datetime
    end_time: datetime
    duration_seconds: float
    metrics: Dict[str, Any]
    aborted: bool = False
    abort_reason: Optional[str] = None
    output: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "name": self.name,
            "success": self.success,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat(),
            "duration_seconds": self.duration_seconds,
            "metrics": self.metrics,
            "aborted": self.aborted,
            "abort_reason": self.abort_reason,
            "output": self.output
        }


class BaseCheck(ABC):
    """Base class for all diagnostic checks."""
    
    def __init__(self):
        """Initialize the check."""
        self.name = self.__class__.__name__
    
    @abstractmethod
    def run(self) -> CheckResult:
        """Run the diagnostic check.
        
        Returns:
            CheckResult with status, details, and recommendation
        """
        pass
    
    def execute(self) -> CheckResult:
        """Execute the check with error handling.
        
        Returns:
            CheckResult with error handling applied
        """
        try:
            return self.run()
        except Exception as e:
            return CheckResult(
                name=self.name,
                status=Status.FAIL,
                details=f"Check failed with error: {str(e)}",
                recommendation="Check system logs for details"
            )


class BaseRepair(ABC):
    """Base class for all repair operations."""
    
    def __init__(self, require_confirmation: bool = True):
        """Initialize the repair.
        
        Args:
            require_confirmation: Whether to require user confirmation
        """
        self.name = self.__class__.__name__
        self.require_confirmation = require_confirmation
    
    @abstractmethod
    def execute_repair(self) -> RepairResult:
        """Execute the repair operation.
        
        Returns:
            RepairResult with success status and output
        """
        pass
    
    def confirm(self) -> bool:
        """Request user confirmation.
        
        Returns:
            True if user confirms, False otherwise
        """
        if not self.require_confirmation:
            return True
        
        response = input(f"Execute repair '{self.name}'? [y/N]: ")
        return response.lower() in ['y', 'yes']
    
    def execute(self) -> RepairResult:
        """Execute the repair with confirmation and error handling.
        
        Returns:
            RepairResult with confirmation and error handling applied
        """
        start_time = datetime.now()
        
        if not self.confirm():
            return RepairResult(
                name=self.name,
                success=False,
                start_time=start_time,
                end_time=datetime.now(),
                output="Repair cancelled by user",
                error="User cancelled"
            )
        
        try:
            result = self.execute_repair()
            result.start_time = start_time
            return result
        except Exception as e:
            return RepairResult(
                name=self.name,
                success=False,
                start_time=start_time,
                end_time=datetime.now(),
                output="",
                error=str(e)
            )


class BaseStressTest(ABC):
    """Base class for all stress tests."""
    
    def __init__(self, duration_seconds: int = 300, temperature_limit: Optional[float] = None):
        """Initialize the stress test.
        
        Args:
            duration_seconds: Duration of the test in seconds
            temperature_limit: Maximum temperature before abort (Celsius)
        """
        self.name = self.__class__.__name__
        self.duration_seconds = duration_seconds
        self.temperature_limit = temperature_limit
        self._abort_flag = False
    
    @abstractmethod
    def run_test(self) -> StressTestResult:
        """Run the stress test.
        
        Returns:
            StressTestResult with metrics and status
        """
        pass
    
    def abort(self, reason: str = "Manual abort") -> None:
        """Abort the stress test.
        
        Args:
            reason: Reason for aborting
        """
        self._abort_flag = True
        self._abort_reason = reason
    
    def execute(self) -> StressTestResult:
        """Execute the stress test with abort handling.
        
        Returns:
            StressTestResult with abort handling applied
        """
        try:
            result = self.run_test()
            result.aborted = self._abort_flag
            if self._abort_flag:
                result.abort_reason = getattr(self, '_abort_reason', 'Unknown')
            return result
        except Exception as e:
            return StressTestResult(
                name=self.name,
                success=False,
                start_time=datetime.now(),
                end_time=datetime.now(),
                duration_seconds=0,
                metrics={},
                aborted=True,
                abort_reason=str(e),
                output=f"Test failed with error: {str(e)}"
            )
