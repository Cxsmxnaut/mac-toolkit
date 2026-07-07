"""Health scoring system for Mac Toolkit."""

from typing import List, Dict, Any
from enum import Enum

from .base import CheckResult, Status


class OverallHealth(Enum):
    """Overall health status."""
    PASS = "PASS"
    WARNING = "WARNING"
    FAIL = "FAIL"
    READY_FOR_CUSTOMER = "READY FOR CUSTOMER"
    NOT_READY = "NOT READY"


class HealthScorer:
    """Calculate health scores based on diagnostic results."""
    
    def __init__(self):
        """Initialize the health scorer."""
        self.deductions = {
            "battery_below_80": 10,
            "battery_below_50": 25,
            "battery_below_20": 40,
            "smart_failing": 50,
            "high_temperature": 20,
            "storage_nearly_full": 15,
            "storage_critically_full": 30,
            "network_issues": 10,
            "kernel_panics": 30,
            "sip_disabled": 15,
            "filevault_disabled": 10,
            "secure_boot_disabled": 15,
            "software_updates_pending": 5,
            "apfs_errors": 50,
            "custom_boot_loader": 10
        }
    
    def calculate_score(self, results: List[CheckResult]) -> int:
        """Calculate health score out of 100.
        
        Args:
            results: List of CheckResult from diagnostics
            
        Returns:
            Health score (0-100)
        """
        score = 100
        
        for result in results:
            if result.status == Status.FAIL:
                score -= 20
            elif result.status == Status.WARNING:
                score -= 5
            
            # Specific deductions based on check details
            if result.name == "Battery":
                if "battery" in result.details.lower():
                    import re
                    match = re.search(r'(\d+)%', result.details)
                    if match:
                        percentage = int(match.group(1))
                        if percentage < 20:
                            score -= self.deductions["battery_below_20"]
                        elif percentage < 50:
                            score -= self.deductions["battery_below_50"]
                        elif percentage < 80:
                            score -= self.deductions["battery_below_80"]
            
            elif result.name == "Storage":
                if "90%" in result.details or "95%" in result.details or "98%" in result.details:
                    score -= self.deductions["storage_critically_full"]
                elif "80%" in result.details or "85%" in result.details:
                    score -= self.deductions["storage_nearly_full"]
            
            elif result.name == "APFS":
                if "error" in result.details.lower() or "corrupt" in result.details.lower():
                    score -= self.deductions["apfs_errors"]
            
            elif result.name == "SIP":
                if "disabled" in result.details.lower():
                    score -= self.deductions["sip_disabled"]
            
            elif result.name == "FileVault":
                if "disabled" in result.details.lower():
                    score -= self.deductions["filevault_disabled"]
            
            elif result.name == "Secure Boot":
                if "disabled" in result.details.lower():
                    score -= self.deductions["secure_boot_disabled"]
            
            elif result.name == "Software Updates":
                if "available" in result.details.lower():
                    score -= self.deductions["software_updates_pending"]
            
            elif result.name == "OpenCore Legacy Patcher":
                details = result.details.lower()
                if ("installed" in details and "not installed" not in details) or "custom boot loader" in details:
                    score -= self.deductions["custom_boot_loader"]

            elif result.name == "OpenCore Readiness":
                if result.status == Status.FAIL:
                    score -= 25
                elif result.status == Status.WARNING:
                    score -= 5
        
        # Ensure score doesn't go below 0
        return max(0, score)
    
    def get_overall_health(self, score: int) -> OverallHealth:
        """Determine overall health status from score.
        
        Args:
            score: Health score (0-100)
            
        Returns:
            OverallHealth status
        """
        if score >= 90:
            return OverallHealth.READY_FOR_CUSTOMER
        elif score >= 70:
            return OverallHealth.PASS
        elif score >= 50:
            return OverallHealth.WARNING
        else:
            return OverallHealth.NOT_READY
    
    def get_recommendations(self, results: List[CheckResult]) -> List[str]:
        """Generate recommendations based on diagnostic results.
        
        Args:
            results: List of CheckResult from diagnostics
            
        Returns:
            List of recommendation strings
        """
        recommendations = []
        
        for result in results:
            if result.recommendation:
                if result.status == Status.FAIL:
                    recommendations.append(f"[CRITICAL] {result.recommendation}")
                elif result.status == Status.WARNING:
                    recommendations.append(f"[WARNING] {result.recommendation}")
        
        return recommendations
    
    def generate_report(self, results: List[CheckResult]) -> Dict[str, Any]:
        """Generate a comprehensive health report.
        
        Args:
            results: List of CheckResult from diagnostics
            
        Returns:
            Dictionary with health report data
        """
        score = self.calculate_score(results)
        overall_health = self.get_overall_health(score)
        recommendations = self.get_recommendations(results)
        
        # Count by status
        pass_count = sum(1 for r in results if r.status == Status.PASS)
        warning_count = sum(1 for r in results if r.status == Status.WARNING)
        fail_count = sum(1 for r in results if r.status == Status.FAIL)
        unknown_count = sum(1 for r in results if r.status == Status.UNKNOWN)
        
        return {
            "health_score": score,
            "overall_health": overall_health.value,
            "status_counts": {
                "pass": pass_count,
                "warning": warning_count,
                "fail": fail_count,
                "unknown": unknown_count
            },
            "recommendations": recommendations,
            "total_checks": len(results)
        }


def calculate_health_score(results: List[CheckResult]) -> Dict[str, Any]:
    """Convenience function to calculate health score.
    
    Args:
        results: List of CheckResult from diagnostics
        
    Returns:
        Dictionary with health report data
    """
    scorer = HealthScorer()
    return scorer.generate_report(results)
