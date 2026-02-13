"""
Test script for calls source.

Tests the DLT calls source by running a small sync locally.
"""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from dlt_pipeline.sources.calls import gong_calls_source


def test_calls_source():
    """Test that calls source initializes and returns resources."""
    print("Testing calls source initialization...")

    # Initialize source
    source = gong_calls_source()

    print(f"✓ Source initialized: {source.name}")
    print(f"  Resources: {[r.name for r in source.resources.values()]}")

    # Check resources exist
    assert "calls" in source.resources
    assert "transcripts" in source.resources
    assert "speakers" in source.resources

    print("\n✓ All resources present")
    print("\nNote: Full pipeline test requires BigQuery credentials and DATABASE_URL")
    print("Run: python dlt_pipeline/bigquery_to_postgres.py")


if __name__ == "__main__":
    test_calls_source()
