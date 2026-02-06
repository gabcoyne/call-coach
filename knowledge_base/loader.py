"""
Knowledge Base Management with Version Control

Manages loading, updating, and versioning of knowledge base entries
including product documentation and coaching rubrics.
"""
import hashlib
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any
from uuid import UUID

from db import execute_query, fetch_all, fetch_one
from db.models import (
    CoachingDimension,
    CoachingRubric,
    KnowledgeBaseCategory,
    KnowledgeBaseEntry,
    Product,
)

logger = logging.getLogger(__name__)


class KnowledgeBaseManager:
    """Manages knowledge base entries with version control."""

    def __init__(self):
        self.knowledge_dir = Path(__file__).parent.parent / "knowledge"

    def _compute_content_hash(self, content: str) -> str:
        """Compute SHA256 hash of content for change detection."""
        return hashlib.sha256(content.encode()).hexdigest()

    # ========================================================================
    # KNOWLEDGE BASE ENTRIES
    # ========================================================================

    def get_entry(
        self, product: Product, category: KnowledgeBaseCategory
    ) -> KnowledgeBaseEntry | None:
        """Get current knowledge base entry."""
        result = fetch_one(
            """
            SELECT id, product, category, content, metadata, last_updated
            FROM knowledge_base
            WHERE product = %s AND category = %s
            """,
            (product.value, category.value),
        )

        if not result:
            return None

        return KnowledgeBaseEntry(
            id=result["id"],
            product=Product(result["product"]),
            category=KnowledgeBaseCategory(result["category"]),
            content=result["content"],
            metadata=result["metadata"],
            last_updated=result["last_updated"],
        )

    def list_entries(
        self, product: Product | None = None, category: KnowledgeBaseCategory | None = None
    ) -> list[KnowledgeBaseEntry]:
        """List knowledge base entries with optional filters."""
        query = "SELECT id, product, category, content, metadata, last_updated FROM knowledge_base"
        params = []
        conditions = []

        if product:
            conditions.append("product = %s")
            params.append(product.value)

        if category:
            conditions.append("category = %s")
            params.append(category.value)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += " ORDER BY product, category"

        results = fetch_all(query, tuple(params) if params else None)

        return [
            KnowledgeBaseEntry(
                id=row["id"],
                product=Product(row["product"]),
                category=KnowledgeBaseCategory(row["category"]),
                content=row["content"],
                metadata=row["metadata"],
                last_updated=row["last_updated"],
            )
            for row in results
        ]

    def create_or_update_entry(
        self,
        product: Product,
        category: KnowledgeBaseCategory,
        content: str,
        metadata: dict[str, Any] | None = None,
    ) -> KnowledgeBaseEntry:
        """
        Create or update knowledge base entry.

        Tracks version history in metadata.
        """
        content_hash = self._compute_content_hash(content)

        # Check if entry exists
        existing = self.get_entry(product, category)

        if existing:
            # Update existing entry
            existing_hash = existing.metadata.get("content_hash") if existing.metadata else None

            if existing_hash == content_hash:
                logger.info(f"No changes detected for {product.value}/{category.value}")
                return existing

            # Track version history
            new_metadata = existing.metadata or {}
            if "version_history" not in new_metadata:
                new_metadata["version_history"] = []

            new_metadata["version_history"].append(
                {
                    "timestamp": datetime.now().isoformat(),
                    "content_hash": existing_hash,
                    "updated_by": new_metadata.get("updated_by", "system"),
                }
            )
            new_metadata["content_hash"] = content_hash
            new_metadata["version"] = len(new_metadata["version_history"]) + 1

            if metadata:
                new_metadata.update(metadata)

            execute_query(
                """
                UPDATE knowledge_base
                SET content = %s, metadata = %s, last_updated = NOW()
                WHERE product = %s AND category = %s
                """,
                (content, json.dumps(new_metadata), product.value, category.value),
            )

            logger.info(
                f"Updated {product.value}/{category.value} - version {new_metadata['version']}"
            )

            return self.get_entry(product, category)
        else:
            # Create new entry
            new_metadata = metadata or {}
            new_metadata["content_hash"] = content_hash
            new_metadata["version"] = 1
            new_metadata["created_at"] = datetime.now().isoformat()

            execute_query(
                """
                INSERT INTO knowledge_base (product, category, content, metadata)
                VALUES (%s, %s, %s, %s)
                """,
                (product.value, category.value, content, json.dumps(new_metadata)),
            )

            logger.info(f"Created {product.value}/{category.value} - version 1")

            return self.get_entry(product, category)

    def delete_entry(self, product: Product, category: KnowledgeBaseCategory) -> bool:
        """Delete knowledge base entry."""
        result = execute_query(
            "DELETE FROM knowledge_base WHERE product = %s AND category = %s",
            (product.value, category.value),
        )

        if result:
            logger.info(f"Deleted {product.value}/{category.value}")
            return True

        return False

    def get_entry_history(
        self, product: Product, category: KnowledgeBaseCategory
    ) -> list[dict[str, Any]]:
        """Get version history for an entry."""
        entry = self.get_entry(product, category)
        if not entry or not entry.metadata:
            return []

        return entry.metadata.get("version_history", [])

    # ========================================================================
    # COACHING RUBRICS
    # ========================================================================

    def get_rubric(
        self, category: CoachingDimension, version: str | None = None, active_only: bool = True
    ) -> CoachingRubric | None:
        """Get coaching rubric by category and optional version."""
        if version:
            query = """
                SELECT id, name, version, category, criteria, scoring_guide, examples,
                       active, created_at, deprecated_at
                FROM coaching_rubrics
                WHERE category = %s AND version = %s
            """
            params = (category.value, version)
        elif active_only:
            query = """
                SELECT id, name, version, category, criteria, scoring_guide, examples,
                       active, created_at, deprecated_at
                FROM coaching_rubrics
                WHERE category = %s AND active = true
                ORDER BY created_at DESC
                LIMIT 1
            """
            params = (category.value,)
        else:
            query = """
                SELECT id, name, version, category, criteria, scoring_guide, examples,
                       active, created_at, deprecated_at
                FROM coaching_rubrics
                WHERE category = %s
                ORDER BY created_at DESC
                LIMIT 1
            """
            params = (category.value,)

        result = fetch_one(query, params)

        if not result:
            return None

        return CoachingRubric(
            id=result["id"],
            name=result["name"],
            version=result["version"],
            category=CoachingDimension(result["category"]),
            criteria=result["criteria"],
            scoring_guide=result["scoring_guide"],
            examples=result["examples"],
            active=result["active"],
            created_at=result["created_at"],
            deprecated_at=result["deprecated_at"],
        )

    def list_rubrics(
        self, active_only: bool = True, category: CoachingDimension | None = None
    ) -> list[CoachingRubric]:
        """List coaching rubrics."""
        query = """
            SELECT id, name, version, category, criteria, scoring_guide, examples,
                   active, created_at, deprecated_at
            FROM coaching_rubrics
        """
        params = []
        conditions = []

        if active_only:
            conditions.append("active = true")

        if category:
            conditions.append("category = %s")
            params.append(category.value)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += " ORDER BY category, created_at DESC"

        results = fetch_all(query, tuple(params) if params else None)

        return [
            CoachingRubric(
                id=row["id"],
                name=row["name"],
                version=row["version"],
                category=CoachingDimension(row["category"]),
                criteria=row["criteria"],
                scoring_guide=row["scoring_guide"],
                examples=row["examples"],
                active=row["active"],
                created_at=row["created_at"],
                deprecated_at=row["deprecated_at"],
            )
            for row in results
        ]

    def create_rubric(self, rubric_data: dict[str, Any]) -> CoachingRubric:
        """
        Create new coaching rubric version.

        Automatically deprecates previous active version.
        """
        # Validate required fields
        required_fields = ["name", "version", "category", "criteria", "scoring_guide"]
        missing = [f for f in required_fields if f not in rubric_data]
        if missing:
            raise ValueError(f"Missing required fields: {missing}")

        category = CoachingDimension(rubric_data["category"])

        # Check if version already exists
        existing = self.get_rubric(category, rubric_data["version"], active_only=False)
        if existing:
            raise ValueError(
                f"Rubric {category.value} v{rubric_data['version']} already exists"
            )

        # Deprecate previous active version
        execute_query(
            """
            UPDATE coaching_rubrics
            SET active = false, deprecated_at = NOW()
            WHERE category = %s AND active = true
            """,
            (category.value,),
        )

        # Insert new rubric
        execute_query(
            """
            INSERT INTO coaching_rubrics (
                name, version, category, criteria, scoring_guide, examples, active
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (
                rubric_data["name"],
                rubric_data["version"],
                category.value,
                json.dumps(rubric_data["criteria"]),
                json.dumps(rubric_data["scoring_guide"]),
                json.dumps(rubric_data.get("examples", {})),
                True,
            ),
        )

        logger.info(f"Created rubric {category.value} v{rubric_data['version']}")

        return self.get_rubric(category)

    def update_rubric(
        self, rubric_id: UUID | str, updates: dict[str, Any]
    ) -> CoachingRubric | None:
        """
        Update rubric metadata (does not change version).

        For content changes, create a new version instead.
        """
        allowed_fields = ["examples", "active"]
        update_fields = {k: v for k, v in updates.items() if k in allowed_fields}

        if not update_fields:
            logger.warning("No valid fields to update")
            return None

        set_clause = ", ".join([f"{k} = %s" for k in update_fields.keys()])
        params = list(update_fields.values())
        params.append(str(rubric_id))

        execute_query(
            f"UPDATE coaching_rubrics SET {set_clause} WHERE id = %s", tuple(params)
        )

        logger.info(f"Updated rubric {rubric_id}")

        # Fetch and return updated rubric
        result = fetch_one(
            """
            SELECT id, name, version, category, criteria, scoring_guide, examples,
                   active, created_at, deprecated_at
            FROM coaching_rubrics
            WHERE id = %s
            """,
            (str(rubric_id),),
        )

        if result:
            return CoachingRubric(**result)

        return None

    def get_rubric_versions(self, category: CoachingDimension) -> list[CoachingRubric]:
        """Get all versions of a rubric category."""
        results = fetch_all(
            """
            SELECT id, name, version, category, criteria, scoring_guide, examples,
                   active, created_at, deprecated_at
            FROM coaching_rubrics
            WHERE category = %s
            ORDER BY created_at DESC
            """,
            (category.value,),
        )

        return [
            CoachingRubric(
                id=row["id"],
                name=row["name"],
                version=row["version"],
                category=CoachingDimension(row["category"]),
                criteria=row["criteria"],
                scoring_guide=row["scoring_guide"],
                examples=row["examples"],
                active=row["active"],
                created_at=row["created_at"],
                deprecated_at=row["deprecated_at"],
            )
            for row in results
        ]

    # ========================================================================
    # BULK OPERATIONS
    # ========================================================================

    def load_from_filesystem(self) -> dict[str, Any]:
        """Load all knowledge base content from filesystem."""
        from knowledge.loader import load_all

        logger.info("Loading knowledge base from filesystem")
        return load_all()

    def export_to_json(self, output_dir: Path) -> None:
        """Export all knowledge base content to JSON files."""
        output_dir.mkdir(parents=True, exist_ok=True)

        # Export knowledge base entries
        entries = self.list_entries()
        for entry in entries:
            filename = f"{entry.product.value}_{entry.category.value}.json"
            filepath = output_dir / filename

            with open(filepath, "w") as f:
                json.dump(
                    {
                        "product": entry.product.value,
                        "category": entry.category.value,
                        "content": entry.content,
                        "metadata": entry.metadata,
                    },
                    f,
                    indent=2,
                )

            logger.info(f"Exported {filename}")

        # Export rubrics
        rubrics = self.list_rubrics(active_only=False)
        for rubric in rubrics:
            filename = f"rubric_{rubric.category.value}_v{rubric.version}.json"
            filepath = output_dir / filename

            with open(filepath, "w") as f:
                json.dump(
                    {
                        "name": rubric.name,
                        "version": rubric.version,
                        "category": rubric.category.value,
                        "criteria": rubric.criteria,
                        "scoring_guide": rubric.scoring_guide,
                        "examples": rubric.examples,
                        "active": rubric.active,
                    },
                    f,
                    indent=2,
                )

            logger.info(f"Exported {filename}")

        logger.info(f"Export complete: {output_dir}")

    def get_stats(self) -> dict[str, Any]:
        """Get knowledge base statistics."""
        kb_count = fetch_one("SELECT COUNT(*) as count FROM knowledge_base")
        rubric_count = fetch_one(
            "SELECT COUNT(*) as count FROM coaching_rubrics WHERE active = true"
        )
        total_rubrics = fetch_one("SELECT COUNT(*) as count FROM coaching_rubrics")

        entries_by_product = fetch_all(
            """
            SELECT product, COUNT(*) as count
            FROM knowledge_base
            GROUP BY product
            ORDER BY product
            """
        )

        rubrics_by_category = fetch_all(
            """
            SELECT category, COUNT(*) as count
            FROM coaching_rubrics
            WHERE active = true
            GROUP BY category
            ORDER BY category
            """
        )

        return {
            "knowledge_base_entries": kb_count["count"] if kb_count else 0,
            "active_rubrics": rubric_count["count"] if rubric_count else 0,
            "total_rubric_versions": total_rubrics["count"] if total_rubrics else 0,
            "entries_by_product": {
                row["product"]: row["count"] for row in entries_by_product
            },
            "rubrics_by_category": {
                row["category"]: row["count"] for row in rubrics_by_category
            },
        }


if __name__ == "__main__":
    import sys

    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    manager = KnowledgeBaseManager()

    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "stats":
            stats = manager.get_stats()
            print(json.dumps(stats, indent=2))
        elif command == "export":
            output_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("./kb_export")
            manager.export_to_json(output_dir)
        elif command == "load":
            result = manager.load_from_filesystem()
            print(json.dumps(result, indent=2))
        else:
            print(f"Unknown command: {command}")
            print("Usage: python -m knowledge_base.loader [stats|export|load]")
            sys.exit(1)
    else:
        # Default: show stats
        stats = manager.get_stats()
        print(json.dumps(stats, indent=2))
