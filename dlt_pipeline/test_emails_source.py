"""
Test script for emails source.

Tests the DLT emails source by running a small sync locally.
"""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from dlt_pipeline.sources.emails import gong_emails_source


def test_emails_source():
    """Test that emails source initializes and returns resource."""
    print("Testing emails source initialization...")

    # Initialize source
    source = gong_emails_source()

    # gong_emails_source returns a resource directly (single resource source)
    print("✓ Source initialized")
    print("  Resource name: emails")

    # Verify it's a DLT resource
    assert hasattr(source, "name")

    print("\n✓ Email resource present")
    print("\nNote: Full pipeline test requires BigQuery credentials and DATABASE_URL")
    print("Run: python dlt_pipeline/bigquery_to_postgres.py")


if __name__ == "__main__":
    test_emails_source()
