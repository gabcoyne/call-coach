#!/usr/bin/env python3
"""
Load Initial Knowledge Base Content

This script loads all product documentation and coaching rubrics
from the knowledge/ directory into the database.

Usage:
    python scripts/load_initial_knowledge.py [--verify-only] [--export]
"""
import argparse
import json
import logging
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from knowledge.loader import load_all, verify_knowledge_base
from knowledge_base.loader import KnowledgeBaseManager

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(
        description="Load initial knowledge base content"
    )
    parser.add_argument(
        "--verify-only",
        action="store_true",
        help="Only verify the knowledge base, don't load",
    )
    parser.add_argument(
        "--export",
        type=str,
        help="Export knowledge base to directory",
    )
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Show knowledge base statistics",
    )

    args = parser.parse_args()

    manager = KnowledgeBaseManager()

    try:
        if args.verify_only:
            logger.info("Verifying knowledge base...")
            results = verify_knowledge_base()
            print(json.dumps(results, indent=2))

            if results["valid"]:
                logger.info("✓ Knowledge base verification passed")
                return 0
            else:
                logger.error("✗ Knowledge base verification failed")
                return 1

        elif args.export:
            logger.info(f"Exporting knowledge base to {args.export}...")
            manager.export_to_json(Path(args.export))
            logger.info("✓ Export complete")
            return 0

        elif args.stats:
            logger.info("Fetching knowledge base statistics...")
            stats = manager.get_stats()
            print(json.dumps(stats, indent=2))
            return 0

        else:
            # Load all knowledge base content
            logger.info("=" * 60)
            logger.info("LOADING INITIAL KNOWLEDGE BASE")
            logger.info("=" * 60)

            # Load using existing loader from knowledge/ directory
            logger.info("\n[1/3] Loading rubrics and product docs from filesystem...")
            summary = load_all()
            logger.info(f"✓ Loaded {summary['rubrics_loaded']} rubrics")
            logger.info(f"✓ Loaded {summary['product_docs_loaded']} product docs")

            # Verify what was loaded
            logger.info("\n[2/3] Verifying loaded content...")
            verification = verify_knowledge_base()

            if verification["valid"]:
                logger.info("✓ Verification passed")
            else:
                logger.warning("⚠ Verification found issues")
                logger.warning(json.dumps(verification, indent=2))

            # Show statistics
            logger.info("\n[3/3] Knowledge base statistics:")
            stats = manager.get_stats()
            print(json.dumps(stats, indent=2))

            logger.info("\n" + "=" * 60)
            logger.info("KNOWLEDGE BASE LOADED SUCCESSFULLY")
            logger.info("=" * 60)

            # Provide next steps
            logger.info("\nNext steps:")
            logger.info("1. Access admin UI: http://localhost:3000/admin/knowledge")
            logger.info("2. Test API: curl http://localhost:8000/knowledge/stats")
            logger.info("3. Verify rubrics: python -m knowledge.loader verify")

            return 0

    except Exception as e:
        logger.error(f"Error loading knowledge base: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
