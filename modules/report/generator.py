"""Report generation for Mac Toolkit."""

import json
import html
import io
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from ..utils.base import CheckResult, RepairResult, Status, StressTestResult
from ..utils.health_score import calculate_health_score
from ..utils.macos import reports_dir
from ..system import SystemInfo


class ReportGenerator:
    """Generate diagnostic reports in multiple formats."""
    
    def __init__(self, output_dir: Optional[str] = None):
        """Initialize the report generator.
        
        Args:
            output_dir: Directory to save reports
        """
        self.output_dir = Path(output_dir) if output_dir else reports_dir()
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_filename(self, format: str) -> str:
        """Generate a filename for the report.
        
        Args:
            format: File format (txt, json, html)
            
        Returns:
            Filename with timestamp
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"mactoolkit_report_{timestamp}.{format}"
    
    def generate_txt(
        self,
        results: List[CheckResult],
        system_info: Optional[SystemInfo] = None,
        repairs: Optional[List[RepairResult]] = None,
        stress_results: Optional[List[StressTestResult]] = None,
    ) -> str:
        """Generate a text format report.
        
        Args:
            results: List of CheckResult from diagnostics
            system_info: Optional SystemInfo data
            
        Returns:
            Text report content
        """
        lines = []
        lines.append("=" * 60)
        lines.append("MAC TOOLKIT DIAGNOSTIC REPORT")
        lines.append("=" * 60)
        lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")
        
        # Health score
        health_report = calculate_health_score(results)
        lines.append("HEALTH SCORE")
        lines.append("-" * 60)
        lines.append(f"Score: {health_report['health_score']}/100")
        lines.append(f"Overall Health: {health_report['overall_health']}")
        lines.append("")
        
        # System Information
        if system_info:
            lines.append("SYSTEM INFORMATION")
            lines.append("-" * 60)
            lines.append(f"Model: {system_info.model}")
            lines.append(f"macOS: {system_info.macos_version}")
            lines.append(f"CPU: {system_info.cpu}")
            lines.append(f"RAM: {system_info.ram_gb} GB")
            lines.append("")
        
        # Diagnostic Results
        lines.append("DIAGNOSTIC RESULTS")
        lines.append("-" * 60)
        for result in results:
            status_symbol = {
                Status.PASS: "✓",
                Status.WARNING: "⚠",
                Status.FAIL: "✗",
                Status.UNKNOWN: "?"
            }.get(result.status, "?")
            
            lines.append(f"{status_symbol} {result.name}: {result.status.value}")
            lines.append(f"  Details: {result.details}")
            if result.recommendation:
                lines.append(f"  Recommendation: {result.recommendation}")
            lines.append("")
        
        # Summary
        lines.append("SUMMARY")
        lines.append("-" * 60)
        lines.append(f"Total Checks: {health_report['total_checks']}")
        lines.append(f"PASS: {health_report['status_counts']['pass']}")
        lines.append(f"WARNING: {health_report['status_counts']['warning']}")
        lines.append(f"FAIL: {health_report['status_counts']['fail']}")
        lines.append(f"UNKNOWN: {health_report['status_counts']['unknown']}")
        lines.append("")
        
        # Recommendations
        if health_report['recommendations']:
            lines.append("RECOMMENDATIONS")
            lines.append("-" * 60)
            for rec in health_report['recommendations']:
                lines.append(f"  {rec}")
            lines.append("")

        if repairs:
            lines.append("REPAIRS PERFORMED")
            lines.append("-" * 60)
            for repair in repairs:
                lines.append(f"{repair.name}: {'SUCCESS' if repair.success else 'FAILED'} ({repair.duration:.2f}s)")
                lines.append(f"  Output: {repair.output}")
                if repair.error:
                    lines.append(f"  Error: {repair.error}")
            lines.append("")

        if stress_results:
            lines.append("STRESS RESULTS")
            lines.append("-" * 60)
            for stress in stress_results:
                lines.append(f"{stress.name}: {'PASS' if stress.success else 'FAIL'} ({stress.duration_seconds:.2f}s)")
                lines.append(f"  Metrics: {stress.metrics}")
            lines.append("")
        
        lines.append("=" * 60)
        lines.append("END OF REPORT")
        lines.append("=" * 60)
        
        return "\n".join(lines)
    
    def generate_json(
        self,
        results: List[CheckResult],
        system_info: Optional[SystemInfo] = None,
        repairs: Optional[List[RepairResult]] = None,
        stress_results: Optional[List[StressTestResult]] = None,
    ) -> str:
        """Generate a JSON format report.
        
        Args:
            results: List of CheckResult from diagnostics
            system_info: Optional SystemInfo data
            
        Returns:
            JSON report content
        """
        report = {
            "timestamp": datetime.now().isoformat(),
            "health_score": calculate_health_score(results),
            "system_info": system_info.to_dict() if system_info else None,
            "diagnostics": [result.to_dict() for result in results],
            "repairs": [repair.to_dict() for repair in repairs or []],
            "stress_results": [stress.to_dict() for stress in stress_results or []],
        }
        return json.dumps(report, indent=2)
    
    def generate_html(
        self,
        results: List[CheckResult],
        system_info: Optional[SystemInfo] = None,
        repairs: Optional[List[RepairResult]] = None,
        stress_results: Optional[List[StressTestResult]] = None,
    ) -> str:
        """Generate an HTML format report.
        
        Args:
            results: List of CheckResult from diagnostics
            system_info: Optional SystemInfo data
            
        Returns:
            HTML report content
        """
        health_report = calculate_health_score(results)
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mac Toolkit Diagnostic Report</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f7;
        }}
        .container {{
            background-color: white;
            border-radius: 12px;
            padding: 30px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #1d1d1f;
            border-bottom: 2px solid #007aff;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #1d1d1f;
            margin-top: 30px;
        }}
        .health-score {{
            font-size: 48px;
            font-weight: bold;
            text-align: center;
            margin: 20px 0;
        }}
        .health-score.pass {{ color: #34c759; }}
        .health-score.warning {{ color: #ff9500; }}
        .health-score.fail {{ color: #ff3b30; }}
        .health-score.ready {{ color: #34c759; }}
        .health-score.not-ready {{ color: #ff3b30; }}
        .result {{
            padding: 15px;
            margin: 10px 0;
            border-radius: 8px;
            border-left: 4px solid #ccc;
        }}
        .result.pass {{ background-color: #e8f5e9; border-left-color: #34c759; }}
        .result.warning {{ background-color: #fff3e0; border-left-color: #ff9500; }}
        .result.fail {{ background-color: #ffebee; border-left-color: #ff3b30; }}
        .result.unknown {{ background-color: #f5f5f5; border-left-color: #8e8e93; }}
        .status {{
            font-weight: bold;
            text-transform: uppercase;
        }}
        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        .summary-item {{
            background-color: #f5f5f7;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
        }}
        .summary-item .value {{
            font-size: 32px;
            font-weight: bold;
        }}
        .summary-item .pass .value {{ color: #34c759; }}
        .summary-item .warning .value {{ color: #ff9500; }}
        .summary-item .fail .value {{ color: #ff3b30; }}
        .recommendations {{
            background-color: #fff3e0;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #ff9500;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #e5e5e5;
        }}
        th {{
            background-color: #f5f5f7;
            font-weight: 600;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Mac Toolkit Diagnostic Report</h1>
        <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        
        <h2>Health Score</h2>
        <div class="health-score {self._get_health_class(health_report['overall_health'])}">
            {health_report['health_score']}/100
        </div>
        <p style="text-align: center; font-size: 24px; font-weight: bold;">
            {health_report['overall_health']}
        </p>
        
        <h2>Summary</h2>
        <div class="summary">
            <div class="summary-item pass">
                <div class="value">{health_report['status_counts']['pass']}</div>
                <div>PASS</div>
            </div>
            <div class="summary-item warning">
                <div class="value">{health_report['status_counts']['warning']}</div>
                <div>WARNING</div>
            </div>
            <div class="summary-item fail">
                <div class="value">{health_report['status_counts']['fail']}</div>
                <div>FAIL</div>
            </div>
            <div class="summary-item">
                <div class="value">{health_report['status_counts']['unknown']}</div>
                <div>UNKNOWN</div>
            </div>
        </div>
"""
        
        if system_info:
            html += """
        <h2>System Information</h2>
        <table>
            <tr><th>Property</th><th>Value</th></tr>
"""
            html += f"            <tr><td>Model</td><td>{self._escape(system_info.model)}</td></tr>\n"
            html += f"            <tr><td>macOS</td><td>{self._escape(system_info.macos_version)}</td></tr>\n"
            html += f"            <tr><td>CPU</td><td>{self._escape(system_info.cpu)}</td></tr>\n"
            html += f"            <tr><td>RAM</td><td>{system_info.ram_gb} GB</td></tr>\n"
            html += "        </table>\n"
        
        html += """
        <h2>Diagnostic Results</h2>
"""
        for result in results:
            html += f"""
        <div class="result {result.status.value.lower()}">
            <h3>{self._escape(result.name)}</h3>
            <p><span class="status">Status:</span> {result.status.value}</p>
            <p><strong>Details:</strong> {self._escape(result.details)}</p>
"""
            if result.recommendation:
                html += f"            <p><strong>Recommendation:</strong> {self._escape(result.recommendation)}</p>\n"
            html += "        </div>\n"
        
        if health_report['recommendations']:
            html += """
        <h2>Recommendations</h2>
        <div class="recommendations">
            <ul>
"""
            for rec in health_report['recommendations']:
                html += f"                <li>{self._escape(rec)}</li>\n"
            html += "            </ul>\n        </div>\n"

        if repairs:
            html += "<h2>Repairs Performed</h2>\n"
            for repair in repairs:
                html += (
                    f'<div class="result {"pass" if repair.success else "fail"}">'
                    f"<h3>{self._escape(repair.name)}</h3>"
                    f"<p><strong>Status:</strong> {'SUCCESS' if repair.success else 'FAILED'}</p>"
                    f"<p><strong>Output:</strong> {self._escape(repair.output)}</p>"
                    "</div>\n"
                )

        if stress_results:
            html += "<h2>Stress Results</h2>\n"
            for stress in stress_results:
                html += (
                    f'<div class="result {"pass" if stress.success else "fail"}">'
                    f"<h3>{self._escape(stress.name)}</h3>"
                    f"<p><strong>Duration:</strong> {stress.duration_seconds:.2f}s</p>"
                    f"<p><strong>Metrics:</strong> {self._escape(stress.metrics)}</p>"
                    "</div>\n"
                )
        
        html += """
    </div>
</body>
</html>
"""
        return html

    def generate_pdf(
        self,
        results: List[CheckResult],
        system_info: Optional[SystemInfo] = None,
        repairs: Optional[List[RepairResult]] = None,
        stress_results: Optional[List[StressTestResult]] = None,
    ) -> bytes:
        """Generate a PDF report as bytes."""
        text = self.generate_txt(results, system_info, repairs, stress_results)
        buffer = io.BytesIO()
        pdf = canvas.Canvas(buffer, pagesize=letter)
        _, height = letter
        y = height - 40
        pdf.setFont("Helvetica", 9)
        for line in text.splitlines():
            if y < 40:
                pdf.showPage()
                pdf.setFont("Helvetica", 9)
                y = height - 40
            pdf.drawString(40, y, line[:110])
            y -= 12
        pdf.save()
        return buffer.getvalue()

    def _escape(self, value: Any) -> str:
        """Escape values for HTML reports."""
        return html.escape(str(value), quote=True)
    
    def _get_health_class(self, health: str) -> str:
        """Get CSS class for health status.
        
        Args:
            health: Health status string
            
        Returns:
            CSS class name
        """
        health_lower = health.lower()
        if "ready" in health_lower:
            return "ready"
        elif "pass" in health_lower:
            return "pass"
        elif "warning" in health_lower:
            return "warning"
        elif "fail" in health_lower or "not" in health_lower:
            return "fail"
        return "pass"
    
    def save_report(self, content: str, filename: str) -> Path:
        """Save report to file.
        
        Args:
            content: Report content
            filename: Filename to save
            
        Returns:
            Path to saved file
        """
        filepath = self.output_dir / filename
        with open(filepath, 'w') as f:
            f.write(content)
        return filepath

    def save_binary_report(self, content: bytes, filename: str) -> Path:
        """Save binary report content."""
        filepath = self.output_dir / filename
        with open(filepath, 'wb') as f:
            f.write(content)
        return filepath
    
    def generate_all(
        self,
        results: List[CheckResult],
        system_info: Optional[SystemInfo] = None,
        repairs: Optional[List[RepairResult]] = None,
        stress_results: Optional[List[StressTestResult]] = None,
    ) -> Dict[str, Path]:
        """Generate reports in all formats.
        
        Args:
            results: List of CheckResult from diagnostics
            system_info: Optional SystemInfo data
            
        Returns:
            Dictionary mapping format to filepath
        """
        files = {}
        
        # TXT
        txt_content = self.generate_txt(results, system_info, repairs, stress_results)
        txt_filename = self.generate_filename("txt")
        files["txt"] = self.save_report(txt_content, txt_filename)
        
        # JSON
        json_content = self.generate_json(results, system_info, repairs, stress_results)
        json_filename = self.generate_filename("json")
        files["json"] = self.save_report(json_content, json_filename)
        
        # HTML
        html_content = self.generate_html(results, system_info, repairs, stress_results)
        html_filename = self.generate_filename("html")
        files["html"] = self.save_report(html_content, html_filename)

        pdf_content = self.generate_pdf(results, system_info, repairs, stress_results)
        pdf_filename = self.generate_filename("pdf")
        files["pdf"] = self.save_binary_report(pdf_content, pdf_filename)
        
        return files


def generate_reports(results: List[CheckResult], system_info: Optional[SystemInfo] = None, 
                    formats: Optional[List[str]] = None,
                    repairs: Optional[List[RepairResult]] = None,
                    stress_results: Optional[List[StressTestResult]] = None) -> Dict[str, Path]:
    """Convenience function to generate reports.
    
    Args:
        results: List of CheckResult from diagnostics
        system_info: Optional SystemInfo data
        formats: List of formats to generate (default: all)
        
    Returns:
        Dictionary mapping format to filepath
    """
    generator = ReportGenerator()
    
    if formats is None:
        return generator.generate_all(results, system_info, repairs, stress_results)
    
    files = {}
    for format in formats:
        if format == "txt":
            content = generator.generate_txt(results, system_info, repairs, stress_results)
            filename = generator.generate_filename("txt")
            files["txt"] = generator.save_report(content, filename)
        elif format == "json":
            content = generator.generate_json(results, system_info, repairs, stress_results)
            filename = generator.generate_filename("json")
            files["json"] = generator.save_report(content, filename)
        elif format == "html":
            content = generator.generate_html(results, system_info, repairs, stress_results)
            filename = generator.generate_filename("html")
            files["html"] = generator.save_report(content, filename)
        elif format == "pdf":
            content = generator.generate_pdf(results, system_info, repairs, stress_results)
            filename = generator.generate_filename("pdf")
            files["pdf"] = generator.save_binary_report(content, filename)
    
    return files
