"""
Performance Report Generator

Generates HTML reports with:
- Response time percentiles (p50, p95, p99)
- Memory usage over time
- Database query performance
- Cache hit rates
- Comparison to baseline
"""
import json
from datetime import datetime
from typing import Dict, List, Any
from pathlib import Path
import statistics


class PerformanceReport:
    """Generates performance test reports."""

    def __init__(self, output_dir: str = "benchmarks/reports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.timestamp = datetime.now()

    def load_benchmark_results(self, results_file: str) -> Dict[str, Any]:
        """Load benchmark results from JSON file."""
        try:
            with open(results_file, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def calculate_percentiles(self, response_times: List[float]) -> Dict[str, float]:
        """Calculate response time percentiles."""
        if not response_times:
            return {"p50": 0, "p95": 0, "p99": 0}

        sorted_times = sorted(response_times)
        return {
            "p50": statistics.median(sorted_times),
            "p95": sorted_times[int(len(sorted_times) * 0.95)],
            "p99": sorted_times[int(len(sorted_times) * 0.99)],
            "min": min(sorted_times),
            "max": max(sorted_times),
            "mean": statistics.mean(sorted_times),
            "stdev": statistics.stdev(sorted_times) if len(sorted_times) > 1 else 0,
        }

    def generate_html_report(
        self,
        title: str,
        sections: Dict[str, Dict[str, Any]],
    ) -> str:
        """Generate HTML report with performance data."""
        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            padding: 20px;
            min-height: 100vh;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            padding: 40px;
        }}

        h1 {{
            color: #333;
            margin-bottom: 10px;
            border-bottom: 3px solid #4CAF50;
            padding-bottom: 15px;
        }}

        .metadata {{
            color: #666;
            font-size: 14px;
            margin-bottom: 30px;
        }}

        h2 {{
            color: #4CAF50;
            margin-top: 40px;
            margin-bottom: 20px;
            border-left: 4px solid #4CAF50;
            padding-left: 15px;
        }}

        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}

        .metric-card {{
            background: #f9f9f9;
            border: 1px solid #e0e0e0;
            border-radius: 6px;
            padding: 20px;
            transition: transform 0.2s, box-shadow 0.2s;
        }}

        .metric-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }}

        .metric-name {{
            color: #666;
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 8px;
        }}

        .metric-value {{
            color: #333;
            font-size: 28px;
            font-weight: 600;
            margin-bottom: 5px;
        }}

        .metric-unit {{
            color: #999;
            font-size: 12px;
        }}

        .metric-trend {{
            margin-top: 10px;
            padding-top: 10px;
            border-top: 1px solid #e0e0e0;
            font-size: 12px;
        }}

        .trend-up {{
            color: #f44336;
        }}

        .trend-down {{
            color: #4CAF50;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}

        th {{
            background: #f5f5f5;
            color: #333;
            padding: 12px;
            text-align: left;
            font-weight: 600;
            border-bottom: 2px solid #ddd;
        }}

        td {{
            padding: 12px;
            border-bottom: 1px solid #eee;
        }}

        tr:hover {{
            background: #f9f9f9;
        }}

        .good {{
            color: #4CAF50;
            font-weight: 500;
        }}

        .warning {{
            color: #ff9800;
            font-weight: 500;
        }}

        .bad {{
            color: #f44336;
            font-weight: 500;
        }}

        .chart {{
            margin: 30px 0;
            padding: 20px;
            background: #f9f9f9;
            border-radius: 6px;
        }}

        .chart-title {{
            font-weight: 600;
            color: #333;
            margin-bottom: 15px;
        }}

        .bar {{
            height: 20px;
            margin: 8px 0;
            background: linear-gradient(90deg, #4CAF50, #8BC34A);
            border-radius: 3px;
            display: flex;
            align-items: center;
            padding: 0 8px;
            color: white;
            font-size: 12px;
        }}

        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #eee;
            color: #999;
            font-size: 12px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{title}</h1>
        <div class="metadata">
            Generated: {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}
        </div>
"""

        # Add sections
        for section_name, section_data in sections.items():
            html += self._generate_section(section_name, section_data)

        html += """
        <div class="footer">
            <p>This report was automatically generated by the Call Coaching performance testing suite.</p>
        </div>
    </div>
</body>
</html>
"""
        return html

    def _generate_section(self, title: str, data: Dict[str, Any]) -> str:
        """Generate a report section."""
        html = f"<h2>{title}</h2>\n"

        if "metrics" in data:
            html += self._generate_metrics_grid(data["metrics"])

        if "endpoints" in data:
            html += self._generate_endpoints_table(data["endpoints"])

        if "queries" in data:
            html += self._generate_queries_table(data["queries"])

        if "description" in data:
            html += f'<p>{data["description"]}</p>\n'

        return html

    def _generate_metrics_grid(self, metrics: Dict[str, Any]) -> str:
        """Generate metrics grid."""
        html = '<div class="metrics-grid">\n'

        for metric_name, metric_value in metrics.items():
            if isinstance(metric_value, dict):
                html += f"""
    <div class="metric-card">
        <div class="metric-name">{metric_name}</div>
        <div class="metric-value">{metric_value.get('value', 'N/A')}</div>
        <div class="metric-unit">{metric_value.get('unit', '')}</div>
"""
                if "trend" in metric_value:
                    trend_class = "trend-up" if metric_value.get("trend_up") else "trend-down"
                    html += f'        <div class="metric-trend {trend_class}">{metric_value["trend"]}</div>\n'

                html += "    </div>\n"
            else:
                html += f"""
    <div class="metric-card">
        <div class="metric-name">{metric_name}</div>
        <div class="metric-value">{metric_value}</div>
    </div>
"""

        html += "</div>\n"
        return html

    def _generate_endpoints_table(self, endpoints: List[Dict[str, Any]]) -> str:
        """Generate endpoints performance table."""
        html = """
<table>
    <thead>
        <tr>
            <th>Endpoint</th>
            <th>Requests</th>
            <th>Success Rate</th>
            <th>P50 (ms)</th>
            <th>P95 (ms)</th>
            <th>P99 (ms)</th>
            <th>Status</th>
        </tr>
    </thead>
    <tbody>
"""

        for endpoint in endpoints:
            status_class = "good" if endpoint.get("p99", 0) < 1000 else "warning"
            html += f"""
        <tr>
            <td><code>{endpoint['name']}</code></td>
            <td>{endpoint.get('requests', 0)}</td>
            <td>{endpoint.get('success_rate', 0):.1f}%</td>
            <td>{endpoint.get('p50', 0):.1f}</td>
            <td>{endpoint.get('p95', 0):.1f}</td>
            <td>{endpoint.get('p99', 0):.1f}</td>
            <td><span class="{status_class}">{'✓' if endpoint.get('p99', 0) < 1000 else '⚠'}</span></td>
        </tr>
"""

        html += """
    </tbody>
</table>
"""
        return html

    def _generate_queries_table(self, queries: List[Dict[str, Any]]) -> str:
        """Generate database queries performance table."""
        html = """
<table>
    <thead>
        <tr>
            <th>Query</th>
            <th>Executions</th>
            <th>Avg Time (ms)</th>
            <th>Max Time (ms)</th>
            <th>Status</th>
        </tr>
    </thead>
    <tbody>
"""

        for query in queries:
            status_class = "good" if query.get("max_time", 0) < 1000 else "warning"
            html += f"""
        <tr>
            <td><code>{query['name']}</code></td>
            <td>{query.get('executions', 0)}</td>
            <td>{query.get('avg_time', 0):.1f}</td>
            <td>{query.get('max_time', 0):.1f}</td>
            <td><span class="{status_class}">{'✓' if query.get('max_time', 0) < 1000 else '⚠'}</span></td>
        </tr>
"""

        html += """
    </tbody>
</table>
"""
        return html

    def save_report(self, filename: str, content: str):
        """Save report to file."""
        filepath = self.output_dir / filename
        with open(filepath, "w") as f:
            f.write(content)
        print(f"Report saved: {filepath}")
        return filepath

    def generate_summary_report(self, results: Dict[str, Any]) -> str:
        """Generate summary performance report."""
        sections = {
            "API Performance": {
                "metrics": {
                    "Avg Response Time": {
                        "value": f"{results.get('api_avg_response', 0):.2f}",
                        "unit": "ms",
                    },
                    "P95 Response Time": {
                        "value": f"{results.get('api_p95_response', 0):.2f}",
                        "unit": "ms",
                    },
                    "P99 Response Time": {
                        "value": f"{results.get('api_p99_response', 0):.2f}",
                        "unit": "ms",
                    },
                    "Throughput": {
                        "value": f"{results.get('api_throughput', 0):.2f}",
                        "unit": "req/s",
                    },
                    "Error Rate": {
                        "value": f"{results.get('error_rate', 0):.2f}",
                        "unit": "%",
                    },
                },
                "endpoints": results.get("endpoints", []),
            },
            "Database Performance": {
                "metrics": {
                    "Avg Query Time": {
                        "value": f"{results.get('db_avg_query', 0):.2f}",
                        "unit": "ms",
                    },
                    "Max Query Time": {
                        "value": f"{results.get('db_max_query', 0):.2f}",
                        "unit": "ms",
                    },
                    "Connection Pool Size": {
                        "value": f"{results.get('db_pool_size', 0)}",
                        "unit": "connections",
                    },
                },
                "queries": results.get("queries", []),
            },
            "Cache Performance": {
                "metrics": {
                    "Cache Hit Rate": {
                        "value": f"{results.get('cache_hit_rate', 0):.1f}",
                        "unit": "%",
                    },
                    "Avg Cache Get": {
                        "value": f"{results.get('cache_avg_get', 0):.3f}",
                        "unit": "ms",
                    },
                    "Memory Used": {
                        "value": f"{results.get('cache_memory', 0):.1f}",
                        "unit": "MB",
                    },
                },
            },
        }

        return self.generate_html_report("Call Coaching - Performance Report", sections)


def main():
    """Generate sample performance report."""
    report = PerformanceReport()

    sample_results = {
        "api_avg_response": 250.5,
        "api_p95_response": 850.3,
        "api_p99_response": 1200.1,
        "api_throughput": 45.2,
        "error_rate": 0.5,
        "db_avg_query": 45.2,
        "db_max_query": 500.0,
        "db_pool_size": 10,
        "cache_hit_rate": 85.5,
        "cache_avg_get": 2.3,
        "cache_memory": 256.0,
        "endpoints": [
            {
                "name": "/tools/analyze_call",
                "requests": 1000,
                "success_rate": 99.5,
                "p50": 200.0,
                "p95": 800.0,
                "p99": 1200.0,
            },
            {
                "name": "/tools/search_calls",
                "requests": 500,
                "success_rate": 99.8,
                "p50": 150.0,
                "p95": 600.0,
                "p99": 950.0,
            },
            {
                "name": "/tools/get_rep_insights",
                "requests": 750,
                "success_rate": 99.2,
                "p50": 300.0,
                "p95": 1000.0,
                "p99": 1500.0,
            },
        ],
        "queries": [
            {
                "name": "search_calls",
                "executions": 500,
                "avg_time": 45.2,
                "max_time": 250.0,
            },
            {
                "name": "get_rep_stats",
                "executions": 750,
                "avg_time": 30.5,
                "max_time": 150.0,
            },
        ],
    }

    html = report.generate_summary_report(sample_results)
    filepath = report.save_report("performance_report.html", html)
    print(f"Report generated: {filepath}")


if __name__ == "__main__":
    main()
