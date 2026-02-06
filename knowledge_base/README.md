# Knowledge Base Management System

A comprehensive system for managing product documentation, coaching rubrics, and competitive intelligence with full version control.

## Features

- **Product Documentation Management**: Upload and maintain Prefect and Horizon feature docs, use cases, and competitive battlecards
- **Coaching Rubrics with Versioning**: Create and manage coaching evaluation rubrics with semantic versioning
- **Version Control**: Automatic tracking of content changes with history
- **Admin UI**: Web interface for managing all knowledge base content
- **REST API**: Full CRUD operations via HTTP endpoints
- **Search & Filter**: Find knowledge entries by product, category, or version

## Architecture

```
knowledge_base/
├── __init__.py           # Module exports
├── loader.py             # Core management class
└── README.md             # This file

frontend/app/api/knowledge/
├── route.ts              # Knowledge entries API
├── history/route.ts      # Version history API
└── rubrics/route.ts      # Rubrics management API

frontend/app/admin/knowledge/
└── page.tsx              # Admin UI

api/rest_server.py        # Backend REST endpoints

scripts/
└── load_initial_knowledge.py  # Migration script
```

## Usage

### Command Line

**Load initial knowledge base:**
```bash
python scripts/load_initial_knowledge.py
```

**Verify knowledge base:**
```bash
python scripts/load_initial_knowledge.py --verify-only
```

**Export to JSON:**
```bash
python scripts/load_initial_knowledge.py --export ./export
```

**Show statistics:**
```bash
python scripts/load_initial_knowledge.py --stats
```

### Python API

```python
from knowledge_base.loader import KnowledgeBaseManager
from db.models import Product, KnowledgeBaseCategory

manager = KnowledgeBaseManager()

# Create/update knowledge entry
entry = manager.create_or_update_entry(
    product=Product.PREFECT,
    category=KnowledgeBaseCategory.FEATURE,
    content="# Prefect Features\n\n...",
    metadata={"author": "user@example.com"}
)

# Get entry with version history
entry = manager.get_entry(Product.PREFECT, KnowledgeBaseCategory.FEATURE)
history = manager.get_entry_history(Product.PREFECT, KnowledgeBaseCategory.FEATURE)

# List all entries
entries = manager.list_entries(product=Product.PREFECT)

# Delete entry
success = manager.delete_entry(Product.PREFECT, KnowledgeBaseCategory.FEATURE)

# Create coaching rubric
rubric = manager.create_rubric({
    "name": "Discovery Rubric",
    "version": "2.0.0",
    "category": "discovery",
    "criteria": {...},
    "scoring_guide": {...}
})

# Get active rubric
rubric = manager.get_rubric(CoachingDimension.DISCOVERY)

# Get all versions
versions = manager.get_rubric_versions(CoachingDimension.DISCOVERY)

# Statistics
stats = manager.get_stats()
```

### REST API

**List knowledge entries:**
```bash
GET /knowledge?product=prefect&category=feature
```

**Create/update entry:**
```bash
POST /knowledge
{
  "product": "prefect",
  "category": "feature",
  "content": "# Content here",
  "metadata": {"author": "user@example.com"}
}
```

**Get version history:**
```bash
GET /knowledge/history?product=prefect&category=feature
```

**List rubrics:**
```bash
GET /knowledge/rubrics?category=discovery&active_only=true
```

**Create rubric:**
```bash
POST /knowledge/rubrics
{
  "name": "Discovery Rubric",
  "version": "2.0.0",
  "category": "discovery",
  "criteria": {...},
  "scoring_guide": {...}
}
```

**Update rubric metadata:**
```bash
PATCH /knowledge/rubrics/{rubric_id}
{
  "active": false,
  "examples": {...}
}
```

**Get statistics:**
```bash
GET /knowledge/stats
```

### Admin UI

Access the admin interface at: `http://localhost:3000/admin/knowledge`

Features:
- Upload/edit product documentation
- Create new rubric versions
- View version history
- Delete entries
- See statistics

## Version Control

### Knowledge Entries

Each knowledge entry automatically tracks:
- **Content hash**: SHA256 of content for change detection
- **Version number**: Auto-incremented with each change
- **Version history**: List of previous versions with timestamps
- **Metadata**: Custom metadata including author and timestamps

Example version history:
```json
{
  "version": 3,
  "content_hash": "abc123...",
  "version_history": [
    {
      "timestamp": "2024-01-15T10:00:00Z",
      "content_hash": "def456...",
      "updated_by": "user1@example.com"
    },
    {
      "timestamp": "2024-01-10T09:00:00Z",
      "content_hash": "ghi789...",
      "updated_by": "user2@example.com"
    }
  ]
}
```

### Coaching Rubrics

Rubrics use semantic versioning (MAJOR.MINOR.PATCH):
- **MAJOR**: Breaking changes to evaluation criteria
- **MINOR**: Backward-compatible additions
- **PATCH**: Bug fixes or clarifications

When a new version is created:
1. Previous active version is automatically deprecated
2. New version becomes active
3. All versions remain in database for historical analysis
4. Coaching sessions reference the rubric version used

## Data Model

### Knowledge Entry
```python
{
  "id": "uuid",
  "product": "prefect" | "horizon" | "both",
  "category": "feature" | "differentiation" | "use_case" | "pricing" | "competitor",
  "content": "markdown content",
  "metadata": {
    "version": 1,
    "content_hash": "sha256",
    "version_history": [...],
    "author": "email"
  },
  "last_updated": "2024-01-15T10:00:00Z"
}
```

### Coaching Rubric
```python
{
  "id": "uuid",
  "name": "Discovery Rubric",
  "version": "2.0.0",
  "category": "product_knowledge" | "discovery" | "objection_handling" | "engagement",
  "criteria": {
    "technical_depth": "Evaluation criteria",
    "accuracy": "Evaluation criteria"
  },
  "scoring_guide": {
    "0-30": "Needs Improvement",
    "31-70": "Good",
    "71-100": "Excellent"
  },
  "examples": {...},
  "active": true,
  "created_at": "2024-01-15T10:00:00Z",
  "deprecated_at": null
}
```

## Categories

### Knowledge Base Categories
- **feature**: Product features and capabilities
- **differentiation**: How we differ from competitors
- **use_case**: Customer use cases and success stories
- **pricing**: Pricing models and packaging
- **competitor**: Competitive battlecards and positioning

### Coaching Dimensions
- **product_knowledge**: Technical accuracy and product expertise
- **discovery**: Discovery question quality and customer understanding
- **objection_handling**: Objection identification and resolution
- **engagement**: Customer engagement and relationship building

## Migration from Legacy System

If migrating from the old `knowledge/` directory:

1. Run migration script:
```bash
python scripts/load_initial_knowledge.py
```

2. Verify data:
```bash
python scripts/load_initial_knowledge.py --verify-only
```

3. Export for backup:
```bash
python scripts/load_initial_knowledge.py --export ./backup
```

4. Legacy files remain in `knowledge/` for reference

## Testing

```bash
# Test knowledge base operations
pytest tests/test_knowledge_base.py

# Test API endpoints
pytest tests/test_api/test_knowledge_routes.py

# Test admin UI
npm test -- frontend/app/admin/knowledge
```

## Troubleshooting

**Issue**: Rubric version already exists
```
Solution: Increment version number (e.g., 1.0.0 → 1.0.1)
```

**Issue**: Invalid category
```
Solution: Use valid categories from db.models enums
```

**Issue**: JSON parse error in rubric
```
Solution: Validate JSON syntax in criteria and scoring_guide
```

**Issue**: Version history not showing
```
Solution: Content must change for new version to be tracked
```

## Best Practices

1. **Semantic Versioning**: Use meaningful version numbers for rubrics
2. **Markdown Format**: Write knowledge entries in Markdown for consistency
3. **Regular Updates**: Keep competitive intel and features up-to-date
4. **Test Changes**: Review in admin UI before deploying to production
5. **Backup**: Export knowledge base periodically
6. **Document Changes**: Include meaningful commit messages and metadata

## Support

For issues or questions:
- Check logs: `logs/knowledge_base.log`
- Review API docs: `http://localhost:8000/docs`
- Contact: engineering@prefect.io
