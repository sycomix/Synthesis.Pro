"""
Error Trend Analysis Dashboard for Detective Mode
Analyzes error patterns over time and generates insights
"""

import sqlite3
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict, Counter


class ErrorTrendDashboard:
    """
    Analyzes error trends from Knowledge Base and generates dashboard reports.
    """

    def __init__(self, kb_path: Optional[str] = None):
        """
        Initialize Error Trend Dashboard.

        Args:
            kb_path: Optional path to knowledge_base.db
        """
        if kb_path:
            self.db_path = kb_path
        else:
            # Auto-detect KB path
            project_root = Path(__file__).parent.parent.parent
            self.db_path = project_root / "KnowledgeBase" / "nightblade.db"

        self.enabled = Path(self.db_path).exists()

        if not self.enabled:
            print(f"Warning: Knowledge Base not found at {self.db_path}")
            print("Error trend analysis will not be available")

    def get_error_history(self, days: int = 30) -> List[Dict]:
        """
        Get error history from Knowledge Base.

        Args:
            days: Number of days of history to retrieve

        Returns:
            List of error solution dicts
        """
        if not self.enabled:
            return []

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Get errors from the last N days
            cutoff_date = datetime.now() - timedelta(days=days)

            cursor.execute('''
                SELECT
                    error_type,
                    file_path,
                    line_number,
                    error_message,
                    timestamp,
                    times_occurred
                FROM error_solutions
                WHERE timestamp >= ?
                ORDER BY timestamp DESC
            ''', (cutoff_date.isoformat(),))

            rows = cursor.fetchall()
            conn.close()

            errors = []
            for row in rows:
                errors.append({
                    'error_type': row[0],
                    'file_path': row[1],
                    'line_number': row[2],
                    'error_message': row[3],
                    'timestamp': row[4],
                    'times_occurred': row[5]
                })

            return errors

        except Exception as e:
            print(f"Error querying error history: {e}")
            return []

    def analyze_trends_by_time(self, errors: List[Dict]) -> Dict:
        """
        Analyze error trends by time period.

        Args:
            errors: List of error dicts

        Returns:
            Dict with trend analysis
        """
        now = datetime.now()

        # Group errors by time period
        last_hour = []
        last_day = []
        last_week = []
        last_month = []

        for error in errors:
            try:
                error_time = datetime.fromisoformat(error['timestamp'])
                time_diff = now - error_time

                if time_diff <= timedelta(hours=1):
                    last_hour.append(error)
                if time_diff <= timedelta(days=1):
                    last_day.append(error)
                if time_diff <= timedelta(days=7):
                    last_week.append(error)
                if time_diff <= timedelta(days=30):
                    last_month.append(error)
            except:
                continue

        return {
            'last_hour': len(last_hour),
            'last_day': len(last_day),
            'last_week': len(last_week),
            'last_month': len(last_month),
            'hourly_rate': len(last_hour),
            'daily_rate': len(last_day) / max(1, (now - (now - timedelta(days=1))).days),
            'weekly_rate': len(last_week) / 7.0
        }

    def find_error_hotspots(self, errors: List[Dict], top_n: int = 10) -> Dict:
        """
        Find error hotspots (files/types with most errors).

        Args:
            errors: List of error dicts
            top_n: Number of top items to return

        Returns:
            Dict with hotspot analysis
        """
        error_types = Counter()
        file_paths = Counter()
        error_combinations = Counter()

        for error in errors:
            error_type = error.get('error_type', 'Unknown')
            file_path = error.get('file_path', 'Unknown')
            times = error.get('times_occurred', 1)

            error_types[error_type] += times
            file_paths[file_path] += times
            error_combinations[f"{error_type} in {Path(file_path).name}"] += times

        return {
            'top_error_types': error_types.most_common(top_n),
            'top_files': file_paths.most_common(top_n),
            'top_combinations': error_combinations.most_common(top_n)
        }

    def detect_trends(self, errors: List[Dict]) -> Dict:
        """
        Detect if errors are increasing or decreasing.

        Args:
            errors: List of error dicts

        Returns:
            Dict with trend detection
        """
        now = datetime.now()

        # Split errors into two halves (first half vs second half of time period)
        if not errors:
            return {'trend': 'stable', 'direction': 'none'}

        # Sort by timestamp
        sorted_errors = sorted(errors, key=lambda e: e.get('timestamp', ''))

        if len(sorted_errors) < 2:
            return {'trend': 'insufficient_data', 'direction': 'none'}

        # Split into halves
        mid_point = len(sorted_errors) // 2
        first_half = sorted_errors[:mid_point]
        second_half = sorted_errors[mid_point:]

        first_count = sum(e.get('times_occurred', 1) for e in first_half)
        second_count = sum(e.get('times_occurred', 1) for e in second_half)

        # Calculate trend
        if second_count > first_count * 1.5:
            trend = 'increasing'
            direction = 'worsening'
        elif second_count < first_count * 0.5:
            trend = 'decreasing'
            direction = 'improving'
        else:
            trend = 'stable'
            direction = 'steady'

        change_pct = ((second_count - first_count) / max(1, first_count)) * 100

        return {
            'trend': trend,
            'direction': direction,
            'first_half_count': first_count,
            'second_half_count': second_count,
            'change_percent': change_pct
        }

    def generate_insights(self, errors: List[Dict], trends: Dict, hotspots: Dict, trend_detection: Dict) -> List[str]:
        """
        Generate actionable insights from the analysis.

        Args:
            errors: List of error dicts
            trends: Time-based trend analysis
            hotspots: Hotspot analysis
            trend_detection: Trend detection results

        Returns:
            List of insight strings
        """
        insights = []

        # Total errors insight
        total_errors = sum(e.get('times_occurred', 1) for e in errors)
        insights.append(f"Total errors in period: {total_errors}")

        # Trend insight
        if trend_detection['direction'] == 'worsening':
            insights.append(f"⚠️  ALERT: Errors are INCREASING by {trend_detection['change_percent']:.1f}%")
        elif trend_detection['direction'] == 'improving':
            insights.append(f"✓ Good news: Errors are DECREASING by {abs(trend_detection['change_percent']):.1f}%")
        else:
            insights.append("Errors are stable (no significant change)")

        # Hotspot insights
        if hotspots['top_error_types']:
            top_error = hotspots['top_error_types'][0]
            insights.append(f"Most common error: {top_error[0]} ({top_error[1]} occurrences)")

        if hotspots['top_files']:
            top_file = hotspots['top_files'][0]
            insights.append(f"Problem file: {Path(top_file[0]).name} ({top_file[1]} errors)")

        # Activity insight
        if trends['last_hour'] > 5:
            insights.append(f"⚠️  High activity: {trends['last_hour']} errors in the last hour!")

        # Pattern insight
        if len(hotspots['top_error_types']) > 0:
            error_diversity = len([e for e in hotspots['top_error_types'] if e[1] >= 2])
            if error_diversity > 5:
                insights.append("Multiple recurring issues detected - consider refactoring")

        return insights

    def generate_dashboard(self, days: int = 30) -> str:
        """
        Generate a text-based dashboard report.

        Args:
            days: Number of days of history to analyze

        Returns:
            Dashboard report as string
        """
        if not self.enabled:
            return "Error Trend Dashboard unavailable - Knowledge Base not found"

        # Get data
        errors = self.get_error_history(days)

        if not errors:
            return "No error data available in the Knowledge Base"

        # Analyze
        trends = self.analyze_trends_by_time(errors)
        hotspots = self.find_error_hotspots(errors)
        trend_detection = self.detect_trends(errors)
        insights = self.generate_insights(errors, trends, hotspots, trend_detection)

        # Build dashboard
        dashboard = []
        dashboard.append("=" * 70)
        dashboard.append("ERROR TREND ANALYSIS DASHBOARD")
        dashboard.append("=" * 70)
        dashboard.append(f"Period: Last {days} days")
        dashboard.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        dashboard.append("")

        # Key Insights
        dashboard.append("🔍 KEY INSIGHTS")
        dashboard.append("-" * 70)
        for insight in insights:
            dashboard.append(f"  • {insight}")
        dashboard.append("")

        # Time-based trends
        dashboard.append("📊 ERROR ACTIVITY")
        dashboard.append("-" * 70)
        dashboard.append(f"  Last Hour:   {trends['last_hour']} errors")
        dashboard.append(f"  Last Day:    {trends['last_day']} errors")
        dashboard.append(f"  Last Week:   {trends['last_week']} errors")
        dashboard.append(f"  Last Month:  {trends['last_month']} errors")
        dashboard.append("")

        # Trend direction
        dashboard.append("📈 TREND ANALYSIS")
        dashboard.append("-" * 70)
        dashboard.append(f"  Direction: {trend_detection['direction'].upper()}")
        dashboard.append(f"  Trend: {trend_detection['trend']}")
        dashboard.append(f"  Change: {trend_detection['change_percent']:+.1f}%")
        dashboard.append("")

        # Top error types
        dashboard.append("🔥 TOP ERROR TYPES")
        dashboard.append("-" * 70)
        for i, (error_type, count) in enumerate(hotspots['top_error_types'][:5], 1):
            dashboard.append(f"  {i}. {error_type}: {count} occurrences")
        dashboard.append("")

        # Top files
        dashboard.append("📁 PROBLEM FILES")
        dashboard.append("-" * 70)
        for i, (file_path, count) in enumerate(hotspots['top_files'][:5], 1):
            dashboard.append(f"  {i}. {Path(file_path).name}: {count} errors")
        dashboard.append("")

        # Top combinations
        dashboard.append("⚠️  COMMON ERROR PATTERNS")
        dashboard.append("-" * 70)
        for i, (combo, count) in enumerate(hotspots['top_combinations'][:5], 1):
            dashboard.append(f"  {i}. {combo}: {count} times")
        dashboard.append("")

        dashboard.append("=" * 70)

        return "\n".join(dashboard)

    def export_dashboard_html(self, output_path: str, days: int = 30) -> bool:
        """
        Export dashboard as HTML file.

        Args:
            output_path: Path to save HTML file
            days: Number of days of history to analyze

        Returns:
            True if successful
        """
        if not self.enabled:
            return False

        # Get data
        errors = self.get_error_history(days)
        if not errors:
            return False

        trends = self.analyze_trends_by_time(errors)
        hotspots = self.find_error_hotspots(errors)
        trend_detection = self.detect_trends(errors)
        insights = self.generate_insights(errors, trends, hotspots, trend_detection)

        # Generate HTML
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Error Trend Dashboard</title>
    <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 20px; background: #1e1e1e; color: #d4d4d4; }}
        .header {{ background: #2d2d30; padding: 20px; border-radius: 5px; margin-bottom: 20px; }}
        .section {{ background: #252526; padding: 15px; border-radius: 5px; margin-bottom: 15px; }}
        .insight {{ color: #4ec9b0; margin: 5px 0; }}
        .alert {{ color: #f48771; }}
        .good {{ color: #608b4e; }}
        .metric {{ font-size: 24px; font-weight: bold; color: #4fc1ff; }}
        .chart-bar {{ background: #007acc; height: 20px; margin: 5px 0; border-radius: 3px; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #3e3e42; }}
        th {{ background: #2d2d30; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🔍 Error Trend Analysis Dashboard</h1>
        <p>Period: Last {days} days | Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>

    <div class="section">
        <h2>🔍 Key Insights</h2>
        {''.join(f'<p class="insight">{insight}</p>' for insight in insights)}
    </div>

    <div class="section">
        <h2>📊 Error Activity</h2>
        <p>Last Hour: <span class="metric">{trends['last_hour']}</span></p>
        <p>Last Day: <span class="metric">{trends['last_day']}</span></p>
        <p>Last Week: <span class="metric">{trends['last_week']}</span></p>
        <p>Last Month: <span class="metric">{trends['last_month']}</span></p>
    </div>

    <div class="section">
        <h2>🔥 Top Error Types</h2>
        <table>
            <tr><th>Error Type</th><th>Count</th></tr>
            {''.join(f'<tr><td>{et}</td><td>{count}</td></tr>' for et, count in hotspots['top_error_types'][:10])}
        </table>
    </div>

    <div class="section">
        <h2>📁 Problem Files</h2>
        <table>
            <tr><th>File</th><th>Errors</th></tr>
            {''.join(f'<tr><td>{Path(fp).name}</td><td>{count}</td></tr>' for fp, count in hotspots['top_files'][:10])}
        </table>
    </div>
</body>
</html>
"""

        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html)
            return True
        except Exception as e:
            print(f"Error exporting HTML dashboard: {e}")
            return False


# CLI Interface
def main():
    """CLI for error trend dashboard."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Error Trend Analysis Dashboard',
        epilog='Analyze error patterns and trends from Detective Mode history'
    )

    parser.add_argument(
        '--days',
        type=int,
        default=30,
        help='Number of days of history to analyze (default: 30)'
    )

    parser.add_argument(
        '--export-html',
        type=str,
        help='Export dashboard as HTML file'
    )

    parser.add_argument(
        '--kb-path',
        type=str,
        default=None,
        help='Path to knowledge_base.db'
    )

    args = parser.parse_args()

    # Create dashboard
    dashboard = ErrorTrendDashboard(kb_path=args.kb_path)

    # Generate report
    report = dashboard.generate_dashboard(days=args.days)
    print(report)

    # Export HTML if requested
    if args.export_html:
        if dashboard.export_dashboard_html(args.export_html, days=args.days):
            print(f"\n✓ HTML dashboard exported to: {args.export_html}")
        else:
            print(f"\n✗ Failed to export HTML dashboard")


if __name__ == "__main__":
    main()
