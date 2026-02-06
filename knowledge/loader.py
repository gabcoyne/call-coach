"""
Knowledge base loader for coaching rubrics and product documentation.
Loads structured content into the database for use in coaching analysis.
"""

import json
import logging
from pathlib import Path
from typing import Any

from db import execute_query, fetch_one
from db.models import CoachingDimension, KnowledgeBaseCategory, Product

logger = logging.getLogger(__name__)

# Paths to knowledge base content
KNOWLEDGE_DIR = Path(__file__).parent
RUBRICS_DIR = KNOWLEDGE_DIR / "rubrics"
PRODUCTS_DIR = KNOWLEDGE_DIR / "products"


def load_rubric_from_file(rubric_path: Path) -> dict[str, Any]:
    """
    Load and validate rubric JSON file.

    Args:
        rubric_path: Path to rubric JSON file

    Returns:
        Parsed rubric data

    Raises:
        ValueError: If rubric is invalid
    """
    logger.info(f"Loading rubric from {rubric_path}")

    with open(rubric_path) as f:
        rubric = json.load(f)

    # Validate required fields
    required_fields = ["name", "version", "category", "criteria", "scoring_guide"]
    missing_fields = [f for f in required_fields if f not in rubric]

    if missing_fields:
        raise ValueError(f"Rubric {rubric_path} missing required fields: {missing_fields}")

    # Validate category is valid CoachingDimension
    category = rubric["category"]
    try:
        CoachingDimension(category)
    except ValueError:
        raise ValueError(
            f"Invalid category '{category}' in {rubric_path}. Must be one of: {[d.value for d in CoachingDimension]}"
        )

    return rubric


def insert_rubric_to_db(rubric: dict[str, Any]) -> str:
    """
    Insert rubric into coaching_rubrics table.

    Args:
        rubric: Parsed rubric data

    Returns:
        UUID of inserted rubric
    """
    # Check if this rubric version already exists
    existing = fetch_one(
        """
        SELECT id FROM coaching_rubrics
        WHERE category = %s AND version = %s
        """,
        (rubric["category"], rubric["version"]),
    )

    if existing:
        logger.info(f"Rubric {rubric['name']} v{rubric['version']} already exists, skipping")
        return str(existing["id"])

    # Deactivate previous versions
    execute_query(
        """
        UPDATE coaching_rubrics
        SET active = false, deprecated_at = NOW()
        WHERE category = %s AND active = true
        """,
        (rubric["category"],),
    )

    # Insert new rubric
    execute_query(
        """
        INSERT INTO coaching_rubrics (
            name, version, category, criteria, scoring_guide, examples, active
        ) VALUES (%s, %s, %s, %s, %s, %s, %s)
        """,
        (
            rubric["name"],
            rubric["version"],
            rubric["category"],
            json.dumps(rubric["criteria"]),
            json.dumps(rubric["scoring_guide"]),
            json.dumps(rubric.get("examples", {})),
            True,  # New rubric is active
        ),
    )

    # Fetch inserted ID
    inserted = fetch_one(
        """
        SELECT id FROM coaching_rubrics
        WHERE category = %s AND version = %s
        """,
        (rubric["category"], rubric["version"]),
    )

    logger.info(f"Inserted rubric {rubric['name']} v{rubric['version']}")
    return str(inserted["id"])


def load_rubrics() -> dict[str, str]:
    """
    Load all rubrics from rubrics/ directory.

    Returns:
        Dict mapping rubric category to inserted UUID
    """
    logger.info("Loading all rubrics from knowledge base")

    # Find all rubric JSON files
    rubric_files = list(RUBRICS_DIR.glob("*_v*.json"))

    if not rubric_files:
        logger.warning(f"No rubric files found in {RUBRICS_DIR}")
        return {}

    logger.info(f"Found {len(rubric_files)} rubric files")

    results = {}
    for rubric_file in rubric_files:
        try:
            rubric = load_rubric_from_file(rubric_file)
            rubric_id = insert_rubric_to_db(rubric)
            results[rubric["category"]] = rubric_id
        except Exception as e:
            logger.error(f"Failed to load rubric {rubric_file}: {e}")
            raise

    logger.info(f"Successfully loaded {len(results)} rubrics")
    return results


def load_product_doc(doc_path: Path, product: Product, category: KnowledgeBaseCategory) -> None:
    """
    Load product documentation into knowledge_base table.

    Args:
        doc_path: Path to markdown file
        product: Product (prefect or horizon)
        category: Knowledge base category
    """
    logger.info(f"Loading {product.value} {category.value} from {doc_path}")

    with open(doc_path) as f:
        content = f.read()

    # Check if already exists
    existing = fetch_one(
        """
        SELECT id FROM knowledge_base
        WHERE product = %s AND category = %s
        """,
        (product.value, category.value),
    )

    if existing:
        # Update existing
        execute_query(
            """
            UPDATE knowledge_base
            SET content = %s, last_updated = NOW()
            WHERE product = %s AND category = %s
            """,
            (content, product.value, category.value),
        )
        logger.info(f"Updated {product.value} {category.value}")
    else:
        # Insert new
        execute_query(
            """
            INSERT INTO knowledge_base (product, category, content, metadata)
            VALUES (%s, %s, %s, %s)
            """,
            (product.value, category.value, content, json.dumps({"source_file": doc_path.name})),
        )
        logger.info(f"Inserted {product.value} {category.value}")


def load_product_docs() -> None:
    """Load all product documentation into knowledge base."""
    logger.info("Loading product documentation")

    # Map files to product/category
    docs_to_load = [
        # Prefect Platform & Features
        (PRODUCTS_DIR / "prefect_platform_2024.md", Product.PREFECT, KnowledgeBaseCategory.FEATURE),
        (PRODUCTS_DIR / "prefect_features.md", Product.PREFECT, KnowledgeBaseCategory.FEATURE),
        (PRODUCTS_DIR / "horizon_features.md", Product.HORIZON, KnowledgeBaseCategory.FEATURE),
        # Competitive Battlecards
        (PRODUCTS_DIR / "battlecard_airflow.md", Product.PREFECT, KnowledgeBaseCategory.COMPETITOR),
        (PRODUCTS_DIR / "battlecard_dagster.md", Product.PREFECT, KnowledgeBaseCategory.COMPETITOR),
        (
            PRODUCTS_DIR / "battlecard_temporal.md",
            Product.PREFECT,
            KnowledgeBaseCategory.COMPETITOR,
        ),
        (
            PRODUCTS_DIR / "competitive_positioning.md",
            Product.PREFECT,
            KnowledgeBaseCategory.COMPETITOR,
        ),
    ]

    for doc_path, product, category in docs_to_load:
        if not doc_path.exists():
            logger.warning(f"Doc file not found: {doc_path}")
            continue

        try:
            load_product_doc(doc_path, product, category)
        except Exception as e:
            logger.error(f"Failed to load {doc_path}: {e}")
            raise

    logger.info(f"Successfully loaded {len(docs_to_load)} product docs")


def load_all() -> dict[str, Any]:
    """
    Load all knowledge base content (rubrics + docs).

    Returns:
        Summary of loaded content
    """
    logger.info("Loading complete knowledge base")

    rubrics = load_rubrics()
    load_product_docs()

    summary = {
        "rubrics_loaded": len(rubrics),
        "rubric_categories": list(rubrics.keys()),
        "product_docs_loaded": 3,  # prefect_features, horizon_features, competitive
    }

    logger.info(f"Knowledge base loaded successfully: {summary}")
    return summary


def verify_knowledge_base() -> dict[str, Any]:
    """
    Verify knowledge base is loaded correctly.

    Returns:
        Verification results
    """
    logger.info("Verifying knowledge base")

    # Count active rubrics
    rubrics_count = fetch_one("SELECT COUNT(*) as count FROM coaching_rubrics WHERE active = true")

    # Count knowledge base entries
    kb_count = fetch_one("SELECT COUNT(*) as count FROM knowledge_base")

    # Get rubric versions
    rubrics = fetch_one(
        """
        SELECT
            category,
            version,
            name
        FROM coaching_rubrics
        WHERE active = true
        ORDER BY category
        """
    )

    results = {
        "active_rubrics": rubrics_count["count"] if rubrics_count else 0,
        "knowledge_base_entries": kb_count["count"] if kb_count else 0,
        "expected_rubrics": 4,  # discovery, product_knowledge, objection_handling, engagement
        "expected_kb_entries": 3,  # 2 feature docs + 1 competitive
    }

    # Validate
    results["valid"] = (
        results["active_rubrics"] == results["expected_rubrics"]
        and results["knowledge_base_entries"] == results["expected_kb_entries"]
    )

    if results["valid"]:
        logger.info("✓ Knowledge base verification passed")
    else:
        logger.warning(f"✗ Knowledge base verification failed: {results}")

    return results


if __name__ == "__main__":
    import sys

    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "rubrics":
            load_rubrics()
        elif command == "docs":
            load_product_docs()
        elif command == "verify":
            results = verify_knowledge_base()
            print(json.dumps(results, indent=2))
            sys.exit(0 if results["valid"] else 1)
        elif command == "all":
            load_all()
        else:
            print(f"Unknown command: {command}")
            print("Usage: python -m knowledge.loader [rubrics|docs|verify|all]")
            sys.exit(1)
    else:
        # Default: load everything
        load_all()
        verify_knowledge_base()
