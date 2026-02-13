"""
Test script for opportunities source.

Tests the DLT opportunities source by running a small sync locally.
"""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from dlt_pipeline.sources.opportunities import gong_opportunities_source


def test_opportunities_source():
    """Test that opportunities source initializes and returns resources."""
    print("Testing opportunities source initialization...")

    # Initialize source
    source = gong_opportunities_source()

    print(f"✓ Source initialized: {source.name}")
    print(f"  Resources: {[r.name for r in source.resources.values()]}")

    # Check resources exist
    assert "opportunities" in source.resources
    assert "call_opportunities" in source.resources

    print("\n✓ All resources present (opportunities, call_opportunities)")
    print(
        "\nNote: Full pipeline test requires BigQuery credentials, Salesforce tables, and DATABASE_URL"
    )
    print("Run: python dlt_pipeline/bigquery_to_postgres.py")


if __name__ == "__main__":
    test_opportunities_source()
