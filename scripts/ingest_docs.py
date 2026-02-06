#!/usr/bin/env python3
"""
Main ingestion pipeline for product documentation.

Orchestrates scraping, processing, and storage of documentation.
Supports incremental updates and change detection.
"""
import asyncio
import hashlib
import json
import logging
import sys
from datetime import datetime
from pathlib import Path

from knowledge_base.processor import CompetitiveAnalysisLoader, ContentProcessor
from knowledge_base.scrapers.horizon_docs import HorizonDocsScraper
from knowledge_base.scrapers.prefect_docs import PrefectDocsScraper

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class DocumentationIngestionPipeline:
    """Main pipeline for ingesting product documentation."""

    def __init__(self, output_dir: str = "knowledge_base/ingested"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.processor = ContentProcessor()
        self.competitive_loader = CompetitiveAnalysisLoader()
        self.manifest_file = self.output_dir / "manifest.json"
        self.manifest = self._load_manifest()

    def _load_manifest(self) -> dict:
        """Load existing manifest for change detection."""
        if self.manifest_file.exists():
            try:
                with open(self.manifest_file) as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Could not load manifest: {e}")
        return {"documents": {}, "ingestion_time": None, "version": "1.0"}

    def _save_manifest(self):
        """Save manifest for future runs."""
        self.manifest["ingestion_time"] = datetime.now().isoformat()
        with open(self.manifest_file, "w") as f:
            json.dump(self.manifest, f, indent=2)

    def _compute_hash(self, content: str) -> str:
        """Compute SHA256 hash of content."""
        return hashlib.sha256(content.encode()).hexdigest()

    def _document_changed(self, url: str, content_hash: str) -> bool:
        """Check if document has changed since last ingestion."""
        if url not in self.manifest["documents"]:
            return True
        return self.manifest["documents"][url].get("content_hash") != content_hash

    async def ingest_prefect_docs(self) -> list[dict]:
        """Ingest Prefect documentation."""
        logger.info("Starting Prefect documentation ingestion...")
        async with PrefectDocsScraper() as scraper:
            documents = await scraper.scrape()
        logger.info(f"Scraped {len(documents)} Prefect docs pages")

        # Process documents
        processed = self.processor.process_batch(documents)
        logger.info(f"Processed {len(processed)} Prefect documents")

        return processed

    async def ingest_horizon_docs(self) -> list[dict]:
        """Ingest Horizon documentation."""
        logger.info("Starting Horizon documentation ingestion...")
        async with HorizonDocsScraper() as scraper:
            documents = await scraper.scrape()
        logger.info(f"Scraped {len(documents)} Horizon docs pages")

        # Process documents
        processed = self.processor.process_batch(documents)
        logger.info(f"Processed {len(processed)} Horizon documents")

        return processed

    def ingest_competitive_analysis(self) -> list[dict]:
        """Load competitive analysis documents."""
        logger.info("Loading competitive analysis...")
        competitive_dir = Path("knowledge/competitive")
        documents = []

        if not competitive_dir.exists():
            logger.warning(f"Competitive analysis directory not found: {competitive_dir}")
            return documents

        for md_file in competitive_dir.glob("*.md"):
            doc = self.competitive_loader.load_analysis(str(md_file))
            if doc:
                documents.append(doc)

        logger.info(f"Loaded {len(documents)} competitive analysis documents")
        return documents

    def _save_document(self, doc: dict, index: int) -> bool:
        """Save processed document to disk."""
        try:
            # Create file with safe naming
            safe_title = doc["title"].lower().replace(" ", "_").replace("/", "_")[:50]
            filename = f"{index:04d}_{safe_title}.json"
            filepath = self.output_dir / filename

            # Save document
            with open(filepath, "w") as f:
                json.dump(doc, f, indent=2)

            # Update manifest
            content_hash = self._compute_hash(doc.get("markdown_content", ""))
            self.manifest["documents"][doc["url"]] = {
                "file": filename,
                "content_hash": content_hash,
                "timestamp": datetime.now().isoformat(),
                "product": doc.get("product", "unknown"),
                "category": doc.get("category", "unknown"),
                "source": doc.get("source", "unknown"),
            }

            return True

        except Exception as e:
            logger.error(f"Error saving document {doc.get('url')}: {e}")
            return False

    async def run(self, prefect: bool = True, horizon: bool = True, competitive: bool = True):
        """
        Run the complete ingestion pipeline.

        Args:
            prefect: Whether to ingest Prefect docs
            horizon: Whether to ingest Horizon docs
            competitive: Whether to load competitive analysis
        """
        all_documents = []

        try:
            if prefect:
                docs = await self.ingest_prefect_docs()
                all_documents.extend(docs)

            if horizon:
                docs = await self.ingest_horizon_docs()
                all_documents.extend(docs)

            if competitive:
                docs = self.ingest_competitive_analysis()
                all_documents.extend(docs)

            # Save documents
            logger.info(f"Saving {len(all_documents)} documents...")
            saved_count = 0
            for i, doc in enumerate(all_documents):
                if self._save_document(doc, i):
                    saved_count += 1

            self._save_manifest()

            logger.info(f"Successfully ingested and saved {saved_count} documents")
            return saved_count

        except Exception as e:
            logger.error(f"Error during ingestion pipeline: {e}", exc_info=True)
            return 0


async def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Product Documentation Ingestion Pipeline")
    parser.add_argument(
        "--output",
        default="knowledge_base/ingested",
        help="Output directory for ingested documents",
    )
    parser.add_argument(
        "--prefect",
        action="store_true",
        default=True,
        help="Ingest Prefect documentation",
    )
    parser.add_argument(
        "--horizon", action="store_true", default=True, help="Ingest Horizon documentation"
    )
    parser.add_argument(
        "--competitive",
        action="store_true",
        default=True,
        help="Load competitive analysis",
    )
    parser.add_argument(
        "--skip-prefect", action="store_false", dest="prefect", help="Skip Prefect docs"
    )
    parser.add_argument(
        "--skip-horizon", action="store_false", dest="horizon", help="Skip Horizon docs"
    )
    parser.add_argument(
        "--skip-competitive",
        action="store_false",
        dest="competitive",
        help="Skip competitive analysis",
    )

    args = parser.parse_args()

    pipeline = DocumentationIngestionPipeline(output_dir=args.output)
    count = await pipeline.run(
        prefect=args.prefect, horizon=args.horizon, competitive=args.competitive
    )

    sys.exit(0 if count > 0 else 1)


if __name__ == "__main__":
    asyncio.run(main())
