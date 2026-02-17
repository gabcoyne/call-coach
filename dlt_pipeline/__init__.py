"""
DLT Pipeline for BigQuery to Postgres sync.

This package provides:
- Data sources for calls, emails, and opportunities from BigQuery
- Main pipeline orchestration with parallel execution
- Monitoring and observability (Task 7)
"""

from dlt_pipeline.bigquery_to_postgres import run_pipeline
from dlt_pipeline.monitoring import (
    DataQualityChecker,
    PipelineMetrics,
    SourceMetrics,
    configure_dlt_logging,
    create_pipeline_metrics,
)

__all__ = [
    "run_pipeline",
    "DataQualityChecker",
    "PipelineMetrics",
    "SourceMetrics",
    "configure_dlt_logging",
    "create_pipeline_metrics",
]
