"""
Tests for Knowledge Base Management System

Tests CRUD operations, version control, and API endpoints
for knowledge entries and coaching rubrics.
"""
import json
import pytest
from uuid import uuid4

from knowledge_base.loader import KnowledgeBaseManager
from db.models import Product, KnowledgeBaseCategory, CoachingDimension


@pytest.fixture
def kb_manager():
    """Create a KnowledgeBaseManager instance."""
    return KnowledgeBaseManager()


@pytest.fixture
def sample_knowledge_entry():
    """Sample knowledge entry data."""
    return {
        "product": Product.PREFECT,
        "category": KnowledgeBaseCategory.FEATURE,
        "content": "# Prefect Features\n\nPrefect is awesome!",
        "metadata": {"author": "test@example.com"},
    }


@pytest.fixture
def sample_rubric():
    """Sample rubric data."""
    return {
        "name": "Test Rubric",
        "version": "1.0.0",
        "category": "product_knowledge",
        "criteria": {
            "accuracy": "Technical accuracy of statements",
            "depth": "Depth of product knowledge",
        },
        "scoring_guide": {
            "0-30": "Needs improvement",
            "31-70": "Good",
            "71-100": "Excellent",
        },
        "examples": {
            "good": "Detailed explanation with examples",
            "bad": "Vague or incorrect information",
        },
    }


class TestKnowledgeEntryManagement:
    """Tests for knowledge base entry CRUD operations."""

    def test_create_knowledge_entry(self, kb_manager, sample_knowledge_entry):
        """Test creating a new knowledge entry."""
        entry = kb_manager.create_or_update_entry(**sample_knowledge_entry)

        assert entry is not None
        assert entry.product == sample_knowledge_entry["product"]
        assert entry.category == sample_knowledge_entry["category"]
        assert entry.content == sample_knowledge_entry["content"]
        assert entry.metadata is not None
        assert entry.metadata["version"] == 1
        assert "content_hash" in entry.metadata

    def test_update_knowledge_entry(self, kb_manager, sample_knowledge_entry):
        """Test updating an existing knowledge entry."""
        # Create initial entry
        entry1 = kb_manager.create_or_update_entry(**sample_knowledge_entry)
        version1 = entry1.metadata["version"]

        # Update with new content
        updated_content = "# Updated Prefect Features\n\nEven more awesome!"
        entry2 = kb_manager.create_or_update_entry(
            product=sample_knowledge_entry["product"],
            category=sample_knowledge_entry["category"],
            content=updated_content,
        )

        assert entry2.content == updated_content
        assert entry2.metadata["version"] == version1 + 1
        assert len(entry2.metadata["version_history"]) == 1

    def test_no_update_if_content_unchanged(self, kb_manager, sample_knowledge_entry):
        """Test that unchanged content doesn't create a new version."""
        entry1 = kb_manager.create_or_update_entry(**sample_knowledge_entry)
        version1 = entry1.metadata["version"]

        # Try to update with same content
        entry2 = kb_manager.create_or_update_entry(**sample_knowledge_entry)

        assert entry2.metadata["version"] == version1
        assert entry2.metadata["content_hash"] == entry1.metadata["content_hash"]

    def test_get_knowledge_entry(self, kb_manager, sample_knowledge_entry):
        """Test retrieving a knowledge entry."""
        created = kb_manager.create_or_update_entry(**sample_knowledge_entry)

        retrieved = kb_manager.get_entry(
            sample_knowledge_entry["product"], sample_knowledge_entry["category"]
        )

        assert retrieved is not None
        assert str(retrieved.id) == str(created.id)
        assert retrieved.content == created.content

    def test_list_knowledge_entries(self, kb_manager, sample_knowledge_entry):
        """Test listing knowledge entries with filters."""
        # Create multiple entries
        kb_manager.create_or_update_entry(**sample_knowledge_entry)

        kb_manager.create_or_update_entry(
            product=Product.HORIZON,
            category=KnowledgeBaseCategory.FEATURE,
            content="# Horizon Features",
        )

        # List all entries
        all_entries = kb_manager.list_entries()
        assert len(all_entries) >= 2

        # Filter by product
        prefect_entries = kb_manager.list_entries(product=Product.PREFECT)
        assert all(e.product == Product.PREFECT for e in prefect_entries)

        # Filter by category
        feature_entries = kb_manager.list_entries(category=KnowledgeBaseCategory.FEATURE)
        assert all(e.category == KnowledgeBaseCategory.FEATURE for e in feature_entries)

    def test_delete_knowledge_entry(self, kb_manager, sample_knowledge_entry):
        """Test deleting a knowledge entry."""
        # Create entry
        kb_manager.create_or_update_entry(**sample_knowledge_entry)

        # Delete it
        success = kb_manager.delete_entry(
            sample_knowledge_entry["product"], sample_knowledge_entry["category"]
        )
        assert success is True

        # Verify it's gone
        entry = kb_manager.get_entry(
            sample_knowledge_entry["product"], sample_knowledge_entry["category"]
        )
        assert entry is None

    def test_get_entry_history(self, kb_manager, sample_knowledge_entry):
        """Test retrieving version history for an entry."""
        # Create entry
        kb_manager.create_or_update_entry(**sample_knowledge_entry)

        # Update it twice
        for i in range(2):
            kb_manager.create_or_update_entry(
                product=sample_knowledge_entry["product"],
                category=sample_knowledge_entry["category"],
                content=f"# Version {i + 2}",
            )

        # Get history
        history = kb_manager.get_entry_history(
            sample_knowledge_entry["product"], sample_knowledge_entry["category"]
        )

        assert len(history) == 2
        assert all("timestamp" in h for h in history)
        assert all("content_hash" in h for h in history)


class TestCoachingRubricManagement:
    """Tests for coaching rubric CRUD operations."""

    def test_create_rubric(self, kb_manager, sample_rubric):
        """Test creating a new coaching rubric."""
        rubric = kb_manager.create_rubric(sample_rubric)

        assert rubric is not None
        assert rubric.name == sample_rubric["name"]
        assert rubric.version == sample_rubric["version"]
        assert rubric.category == CoachingDimension(sample_rubric["category"])
        assert rubric.active is True

    def test_create_rubric_deprecates_previous(self, kb_manager, sample_rubric):
        """Test that creating a new rubric version deprecates the previous one."""
        # Create version 1.0.0
        rubric1 = kb_manager.create_rubric(sample_rubric)

        # Create version 2.0.0
        sample_rubric["version"] = "2.0.0"
        rubric2 = kb_manager.create_rubric(sample_rubric)

        # Version 2 should be active
        assert rubric2.active is True

        # Version 1 should be deprecated
        rubric1_updated = kb_manager.get_rubric(
            CoachingDimension(sample_rubric["category"]),
            version="1.0.0",
            active_only=False,
        )
        assert rubric1_updated.active is False
        assert rubric1_updated.deprecated_at is not None

    def test_get_active_rubric(self, kb_manager, sample_rubric):
        """Test retrieving the active rubric for a category."""
        # Create rubric
        kb_manager.create_rubric(sample_rubric)

        # Get active rubric
        rubric = kb_manager.get_rubric(CoachingDimension(sample_rubric["category"]))

        assert rubric is not None
        assert rubric.version == sample_rubric["version"]
        assert rubric.active is True

    def test_get_rubric_by_version(self, kb_manager, sample_rubric):
        """Test retrieving a specific rubric version."""
        # Create rubric
        kb_manager.create_rubric(sample_rubric)

        # Get by version
        rubric = kb_manager.get_rubric(
            CoachingDimension(sample_rubric["category"]),
            version=sample_rubric["version"],
        )

        assert rubric is not None
        assert rubric.version == sample_rubric["version"]

    def test_list_rubrics(self, kb_manager, sample_rubric):
        """Test listing rubrics with filters."""
        # Create rubrics for different categories
        kb_manager.create_rubric(sample_rubric)

        sample_rubric["category"] = "discovery"
        sample_rubric["version"] = "1.0.1"
        kb_manager.create_rubric(sample_rubric)

        # List all active rubrics
        active_rubrics = kb_manager.list_rubrics(active_only=True)
        assert len(active_rubrics) >= 2
        assert all(r.active for r in active_rubrics)

        # List all rubrics (including deprecated)
        all_rubrics = kb_manager.list_rubrics(active_only=False)
        assert len(all_rubrics) >= len(active_rubrics)

        # Filter by category
        discovery_rubrics = kb_manager.list_rubrics(
            category=CoachingDimension.DISCOVERY
        )
        assert all(r.category == CoachingDimension.DISCOVERY for r in discovery_rubrics)

    def test_get_rubric_versions(self, kb_manager, sample_rubric):
        """Test retrieving all versions of a rubric category."""
        category = CoachingDimension(sample_rubric["category"])

        # Create multiple versions
        for version in ["1.0.0", "1.1.0", "2.0.0"]:
            sample_rubric["version"] = version
            kb_manager.create_rubric(sample_rubric)

        # Get all versions
        versions = kb_manager.get_rubric_versions(category)

        assert len(versions) >= 3
        assert versions[0].version == "2.0.0"  # Should be sorted by created_at DESC
        assert versions[0].active is True
        assert all(not v.active for v in versions[1:])  # Others are deprecated

    def test_update_rubric(self, kb_manager, sample_rubric):
        """Test updating rubric metadata."""
        # Create rubric
        rubric = kb_manager.create_rubric(sample_rubric)

        # Update examples
        new_examples = {"additional": "More examples"}
        updated = kb_manager.update_rubric(
            rubric.id, {"examples": new_examples}
        )

        assert updated is not None
        assert updated.examples == new_examples

    def test_duplicate_version_raises_error(self, kb_manager, sample_rubric):
        """Test that creating a duplicate version raises an error."""
        # Create rubric
        kb_manager.create_rubric(sample_rubric)

        # Try to create same version again
        with pytest.raises(ValueError, match="already exists"):
            kb_manager.create_rubric(sample_rubric)


class TestKnowledgeBaseStatistics:
    """Tests for knowledge base statistics."""

    def test_get_stats(self, kb_manager, sample_knowledge_entry, sample_rubric):
        """Test retrieving knowledge base statistics."""
        # Create some data
        kb_manager.create_or_update_entry(**sample_knowledge_entry)
        kb_manager.create_rubric(sample_rubric)

        # Get stats
        stats = kb_manager.get_stats()

        assert "knowledge_base_entries" in stats
        assert "active_rubrics" in stats
        assert "total_rubric_versions" in stats
        assert "entries_by_product" in stats
        assert "rubrics_by_category" in stats

        assert stats["knowledge_base_entries"] > 0
        assert stats["active_rubrics"] > 0


class TestVersionControl:
    """Tests for version control functionality."""

    def test_content_hash_generation(self, kb_manager, sample_knowledge_entry):
        """Test that content hashes are generated correctly."""
        entry1 = kb_manager.create_or_update_entry(**sample_knowledge_entry)
        hash1 = entry1.metadata["content_hash"]

        # Same content should produce same hash
        entry2 = kb_manager.create_or_update_entry(**sample_knowledge_entry)
        hash2 = entry2.metadata["content_hash"]

        assert hash1 == hash2

        # Different content should produce different hash
        sample_knowledge_entry["content"] = "Different content"
        entry3 = kb_manager.create_or_update_entry(**sample_knowledge_entry)
        hash3 = entry3.metadata["content_hash"]

        assert hash3 != hash1

    def test_version_increment(self, kb_manager, sample_knowledge_entry):
        """Test that versions increment correctly."""
        entry1 = kb_manager.create_or_update_entry(**sample_knowledge_entry)
        assert entry1.metadata["version"] == 1

        sample_knowledge_entry["content"] = "Updated"
        entry2 = kb_manager.create_or_update_entry(**sample_knowledge_entry)
        assert entry2.metadata["version"] == 2

        sample_knowledge_entry["content"] = "Updated again"
        entry3 = kb_manager.create_or_update_entry(**sample_knowledge_entry)
        assert entry3.metadata["version"] == 3

    def test_version_history_tracking(self, kb_manager, sample_knowledge_entry):
        """Test that version history is tracked correctly."""
        # Create initial version
        entry1 = kb_manager.create_or_update_entry(**sample_knowledge_entry)
        hash1 = entry1.metadata["content_hash"]

        # Update
        sample_knowledge_entry["content"] = "Updated"
        entry2 = kb_manager.create_or_update_entry(**sample_knowledge_entry)

        # Check history
        history = entry2.metadata["version_history"]
        assert len(history) == 1
        assert history[0]["content_hash"] == hash1
        assert "timestamp" in history[0]


class TestBulkOperations:
    """Tests for bulk operations."""

    def test_export_to_json(self, kb_manager, sample_knowledge_entry, sample_rubric, tmp_path):
        """Test exporting knowledge base to JSON."""
        # Create some data
        kb_manager.create_or_update_entry(**sample_knowledge_entry)
        kb_manager.create_rubric(sample_rubric)

        # Export
        output_dir = tmp_path / "export"
        kb_manager.export_to_json(output_dir)

        # Verify files were created
        assert output_dir.exists()
        files = list(output_dir.glob("*.json"))
        assert len(files) > 0

        # Verify content
        for file in files:
            with open(file) as f:
                data = json.load(f)
                assert data is not None
                if "product" in data:
                    assert "category" in data
                    assert "content" in data
                elif "category" in data and "version" in data:
                    assert "criteria" in data
                    assert "scoring_guide" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
