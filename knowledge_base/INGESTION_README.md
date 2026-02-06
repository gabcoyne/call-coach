# Documentation Ingestion System

Product documentation ingestion system for the Call Coach application. Automatically scrapes, processes, validates, and stores product documentation for use in AI coaching analysis.

## Overview

The ingestion system consists of several components:

1. **Web Scrapers** - Respectfully crawl product documentation sites
2. **Content Processor** - Convert HTML to structured markdown
3. **Database Loader** - Store documents and metadata
4. **Validator** - Check links, structure, and compliance
5. **Prefect Flow** - Orchestrate weekly updates

## Architecture

```
Scrapers (Prefect, Horizon docs)
    ↓
Content Processor (HTML → Markdown)
    ↓
Database Loader (Store + Version)
    ↓
Validator (Links, Structure, Compliance)
    ↓
Knowledge Base Table
```

## Components

### Web Scrapers

#### PrefectDocsScraper
Scrapes https://docs.prefect.io with:
- Pagination and depth limiting (max 500 pages)
- Rate limiting (2 second delay between requests)
- Respectful User-Agent header
- Automatic retry with exponential backoff
- Link following from sidebar navigation

```python
from knowledge_base.scrapers.prefect_docs import PrefectDocsScraper

async with PrefectDocsScraper() as scraper:
    documents = await scraper.scrape()
```

#### HorizonDocsScraper
Scrapes Prefect Horizon documentation with similar capabilities, focused on:
- Account management
- Configuration and deployment
- Authentication and security
- API reference
- Integration docs

### Content Processor

Converts raw HTML into structured markdown:
- Extracts titles and main content
- Identifies code examples (auto-detects language)
- Builds section hierarchy
- Removes navigation, footers, spam
- Validates content length

```python
from knowledge_base.processor import ContentProcessor

processor = ContentProcessor()
processed_docs = processor.process_batch(raw_documents)
```

Output includes:
- Clean markdown content
- Extracted code examples
- Section structure
- Product and category classification

### Database Integration

Store documents with versioning for change detection:

```python
from knowledge_base.db_loader import KnowledgeBaseDBLoader

loader = KnowledgeBaseDBLoader()
doc_id = loader.store_document({
    "title": "...",
    "url": "...",
    "product": "prefect",
    "category": "guide",
    "markdown_content": "...",
})
```

Features:
- Automatic duplicate detection (upsert)
- Content hashing for change detection
- Version tracking in `knowledge_base_versions`
- Ingestion job tracking
- Link extraction and validation

### Validation

Three validation levels:

#### Structure Validation
```python
validator = DocumentationValidator()
result = validator.validate_structure(document)
# Checks required fields, content length, URL format, etc.
```

#### Link Validation
```python
async with DocumentationValidator() as validator:
    results = await validator.validate_links_batch(urls)
    # Returns HTTP status for each link
```

#### Compliance Validation
```python
compliance = ComplianceValidator()
seo = compliance.validate_seo_metadata(document)
a11y = compliance.validate_accessibility(document)
```

## Usage

### Command Line

Run the ingestion pipeline:

```bash
# Ingest all sources
python scripts/ingest_docs.py

# Ingest specific sources
python scripts/ingest_docs.py --prefect --skip-horizon --skip-competitive

# Custom output directory
python scripts/ingest_docs.py --output /path/to/output
```

### As Prefect Flow

Deploy and schedule weekly updates:

```bash
prefect deploy flows/update_knowledge.py
prefect work-pool create -t process default
prefect worker start -p default
```

The flow automatically:
- Scrapes documentation
- Processes content
- Stores in database
- Validates links
- Notifies admins of changes

### Python API

```python
import asyncio
from scripts.ingest_docs import DocumentationIngestionPipeline

async def main():
    pipeline = DocumentationIngestionPipeline()
    count = await pipeline.run(
        prefect=True,
        horizon=True,
        competitive=True
    )
    print(f"Ingested {count} documents")

asyncio.run(main())
```

## Output

Documents are saved to `knowledge_base/ingested/`:

```
knowledge_base/ingested/
├── manifest.json              # Metadata about all ingested docs
├── 0001_prefect_basics.json
├── 0002_horizon_deployment.json
└── ...
```

Each document includes:
- Markdown content
- Original URL and source
- Product and category
- Extracted code examples
- Section structure
- Metadata (timestamps, hashes, etc.)

## Database Schema

### knowledge_base (main table)
- `id` - UUID
- `product` - 'prefect', 'horizon'
- `category` - feature, guide, api, tutorial, etc.
- `content` - Full markdown content
- `metadata` - JSONB with URL, sections, etc.
- `last_updated` - Automatic timestamp

### knowledge_base_versions
- `id` - UUID
- `knowledge_base_id` - FK to knowledge_base
- `version_number` - Sequential
- `content_hash` - SHA256 for change detection
- `detected_changes` - Boolean flag
- `ingestion_timestamp` - When ingested

### ingestion_jobs
- `id` - UUID
- `source` - 'prefect_docs', 'horizon_docs', etc.
- `status` - pending, running, completed, failed
- `documents_scraped` - Count
- `documents_processed` - Count
- `documents_stored` - Count
- `documents_updated` - Count

### document_sections
- For indexed search of document sections
- Links to `knowledge_base` records
- Supports vector embeddings (pgvector)

### knowledge_base_links
- Tracks all links in documents
- Stores validation results (valid, broken, timeout)
- Supports regular link checking

## Rate Limiting & Respect

The scrapers implement respectful crawling:

1. **Rate Limiting** - 2 second delay between requests
2. **User-Agent** - Identifies as bot: `Call-Coach-Documentation-Bot/1.0`
3. **Max Depth** - 500 pages for Prefect, 300 for Horizon
4. **Retry Logic** - Exponential backoff (2, 4, 8 seconds)
5. **Session Management** - Async session pooling

## Change Detection

Documents are versioned with change detection:

```python
loader = KnowledgeBaseDBLoader()

# Automatically detects if content has changed
# via SHA256 hash in database trigger
# Sets detected_changes = TRUE if new content differs
```

Changes are:
- Tracked in `knowledge_base_versions` table
- Summarized in ingestion job metadata
- Reported to admins via Prefect artifacts

## Link Validation

Validate all links in documentation:

```python
async with DocumentationValidator() as validator:
    # Batch validation (concurrent)
    results = await validator.validate_links_batch([
        'https://docs.prefect.io/...',
        'https://github.com/...',
    ])

    # Returns: status (valid/broken/timeout/error)
```

Validation results stored in `knowledge_base_links` table.

## Competitive Analysis

Load pre-written competitive analysis from `knowledge/competitive/`:

```yaml
---
title: "Prefect vs Airflow"
product: "prefect"
---

# Prefect Advantages
- Lower latency...
```

Loaded as knowledge base documents with:
- Category: 'competitor'
- Source: 'competitive_analysis'
- YAML frontmatter for metadata

## Configuration

### Scraper Settings

Edit scraper classes to adjust:

```python
class PrefectDocsScraper(BaseScraper):
    def __init__(self):
        super().__init__(
            base_url="https://docs.prefect.io",
            rate_limit_delay=2.0,    # Seconds between requests
            timeout=30,               # Request timeout
            max_retries=3,           # Retry attempts
        )
        self.max_pages = 500        # Crawl limit
```

### Content Processing

```python
processor = ContentProcessor()
processor.min_content_length = 100      # Minimum chars
processor.max_content_length = 50000    # Maximum chars
```

## Monitoring

### Recent Ingestions

```python
loader = KnowledgeBaseDBLoader()
summary = loader.get_ingestion_summary()
# Returns: total_jobs, successful_jobs, failed_jobs,
#          total_stored, total_updated, last_ingestion
```

### Ingestion Jobs

Query ingestion job status:

```sql
SELECT source, status, documents_stored, completed_at
FROM ingestion_jobs
ORDER BY completed_at DESC
LIMIT 10;
```

### Link Health

Check broken links:

```sql
SELECT link_url, validation_error
FROM knowledge_base_links
WHERE validation_status = 'broken'
ORDER BY last_validated DESC;
```

## Troubleshooting

### Scraper hangs
- Check network connectivity
- Increase timeout: `PrefectDocsScraper(timeout=60)`
- Reduce max_pages to limit crawl

### Missing content
- Verify scraper selectors for target site
- Check if site uses JavaScript (scrapers only get static HTML)
- Ensure robots.txt allows crawling

### Database errors
- Run migrations: `python db/migrations/...`
- Check database connection in `.env`
- Verify knowledge_base table exists

### Link validation failures
- Some links may be behind auth walls
- Timeouts are normal (set tolerance)
- Check `knowledge_base_links` table for details

## Performance

Typical ingestion times:
- Prefect docs: 5-10 minutes (500 pages)
- Horizon docs: 3-5 minutes (300 pages)
- Competitive: < 1 minute
- Processing: 1-2 minutes
- Database storage: < 1 minute

Total: ~10-20 minutes per full run

## Next Steps

After ingestion:

1. **Search Integration** - Add vector embeddings for semantic search
2. **Relevance Ranking** - Use ingestion metadata to rank results
3. **Real-time Updates** - Monitor docs sites for changes
4. **A/B Testing** - Measure impact of fresh docs on coaching quality
5. **Competitive Intelligence** - Extract competitor mentions automatically

## Future Enhancements

- [ ] Video content scraping (YouTube transcripts)
- [ ] Interactive demo detection and linking
- [ ] Customer case study extraction
- [ ] Pricing page parsing
- [ ] API schema auto-documentation
- [ ] Multi-language support
- [ ] PDF document handling
- [ ] Real-time indexing with webhooks
