"""Tests for knowledge base loader."""
import json
from pathlib import Path

import pytest

from knowledge.loader import (
    load_rubric_from_file,
    RUBRICS_DIR,
    PRODUCTS_DIR,
)


def test_rubrics_directory_exists():
    """Test that rubrics directory exists and contains files."""
    assert RUBRICS_DIR.exists()
    rubric_files = list(RUBRICS_DIR.glob("*.json"))
    assert len(rubric_files) >= 4, "Should have at least 4 rubric files"


def test_products_directory_exists():
    """Test that products directory exists and contains files."""
    assert PRODUCTS_DIR.exists()
    product_files = list(PRODUCTS_DIR.glob("*.md"))
    assert len(product_files) >= 3, "Should have at least 3 product doc files"


def test_discovery_rubric_structure():
    """Test discovery rubric has correct structure."""
    rubric_path = RUBRICS_DIR / "discovery_v1.0.0.json"
    assert rubric_path.exists(), "Discovery rubric file should exist"

    rubric = load_rubric_from_file(rubric_path)

    # Check required fields
    assert "name" in rubric
    assert "version" in rubric
    assert "category" in rubric
    assert "criteria" in rubric
    assert "scoring_guide" in rubric

    # Validate structure
    assert rubric["version"] == "1.0.0"
    assert rubric["category"] == "discovery"
    assert isinstance(rubric["criteria"], dict)
    assert isinstance(rubric["scoring_guide"], dict)


def test_product_knowledge_rubric_structure():
    """Test product knowledge rubric has correct structure."""
    rubric_path = RUBRICS_DIR / "product_knowledge_v1.0.0.json"
    assert rubric_path.exists()

    rubric = load_rubric_from_file(rubric_path)

    assert rubric["category"] == "product_knowledge"
    assert "technical_accuracy" in rubric["criteria"]
    assert "feature_to_value_connection" in rubric["criteria"]
    assert "product_specifics" in rubric


def test_objection_handling_rubric_structure():
    """Test objection handling rubric has correct structure."""
    rubric_path = RUBRICS_DIR / "objection_handling_v1.0.0.json"
    assert rubric_path.exists()

    rubric = load_rubric_from_file(rubric_path)

    assert rubric["category"] == "objection_handling"
    assert "common_objections" in rubric
    assert "pricing" in rubric["common_objections"]
    assert "timing" in rubric["common_objections"]


def test_engagement_rubric_structure():
    """Test engagement rubric has correct structure."""
    rubric_path = RUBRICS_DIR / "engagement_v1.0.0.json"
    assert rubric_path.exists()

    rubric = load_rubric_from_file(rubric_path)

    assert rubric["category"] == "engagement"
    assert "talk_listen_ratio" in rubric["criteria"]
    assert "rapport_building" in rubric["criteria"]


def test_all_rubrics_valid_json():
    """Test all rubric files are valid JSON."""
    rubric_files = list(RUBRICS_DIR.glob("*.json"))

    for rubric_file in rubric_files:
        with open(rubric_file) as f:
            rubric = json.load(f)  # Will raise if invalid JSON

        # Check required fields exist
        assert "name" in rubric, f"{rubric_file} missing 'name'"
        assert "version" in rubric, f"{rubric_file} missing 'version'"
        assert "category" in rubric, f"{rubric_file} missing 'category'"


def test_prefect_features_doc_exists():
    """Test Prefect features documentation exists."""
    doc_path = PRODUCTS_DIR / "prefect_features.md"
    assert doc_path.exists()

    content = doc_path.read_text()
    assert len(content) > 1000, "Doc should have substantial content"
    assert "Prefect" in content
    assert "workflow" in content.lower()


def test_horizon_features_doc_exists():
    """Test Horizon features documentation exists."""
    doc_path = PRODUCTS_DIR / "horizon_features.md"
    assert doc_path.exists()

    content = doc_path.read_text()
    assert len(content) > 1000
    assert "Horizon" in content
    assert "managed" in content.lower()


def test_competitive_positioning_doc_exists():
    """Test competitive positioning documentation exists."""
    doc_path = PRODUCTS_DIR / "competitive_positioning.md"
    assert doc_path.exists()

    content = doc_path.read_text()
    assert "Airflow" in content
    assert "Temporal" in content
    assert "Dagster" in content


def test_rubric_versions_consistent():
    """Test all rubrics have consistent version format."""
    rubric_files = list(RUBRICS_DIR.glob("*_v*.json"))

    for rubric_file in rubric_files:
        # Check filename format
        assert "_v" in rubric_file.name, f"{rubric_file} should have version in filename"

        rubric = load_rubric_from_file(rubric_file)

        # Check version format (semantic versioning)
        version = rubric["version"]
        parts = version.split(".")
        assert len(parts) == 3, f"Version should be semver (x.y.z): {version}"
        assert all(part.isdigit() for part in parts), f"Version parts should be numbers: {version}"
