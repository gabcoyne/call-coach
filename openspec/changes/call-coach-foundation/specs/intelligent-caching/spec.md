## ADDED Requirements

### Requirement: Transcript hashing

The system SHALL generate SHA256 hash of transcript content for cache key generation.

#### Scenario: Hash generation

- **WHEN** transcript is received
- **THEN** system generates deterministic SHA256 hash of full text

#### Scenario: Identical transcripts

- **WHEN** two calls have identical transcripts
- **THEN** both generate the same transcript_hash value

### Requirement: Cache key composition

The system SHALL generate unique cache keys using dimension, transcript hash, and rubric version.

#### Scenario: Cache key uniqueness

- **WHEN** analysis is requested for dimension and rubric version
- **THEN** cache_key = SHA256(f"{dimension}:{transcript_hash}:{rubric_version}")

#### Scenario: Different dimensions

- **WHEN** same transcript analyzed for different dimensions
- **THEN** each dimension has unique cache key

### Requirement: Cache lookup

The system SHALL check cache before calling Claude API.

#### Scenario: Cache hit

- **WHEN** matching cache entry exists within TTL
- **THEN** system returns cached analysis without API call

#### Scenario: Cache miss

- **WHEN** no matching cache entry exists or entry expired
- **THEN** system calls Claude API and stores result with cache metadata

### Requirement: Rubric versioning

The system SHALL invalidate cache when rubric version changes.

#### Scenario: Rubric update

- **WHEN** rubric version increments from 1.0.0 to 1.1.0
- **THEN** all analyses using old version are cache misses
- **AND** new analyses use rubric version 1.1.0 in cache key

### Requirement: Cache TTL

The system SHALL respect configurable cache TTL (default 90 days).

#### Scenario: Within TTL

- **WHEN** cached analysis is 30 days old and TTL is 90 days
- **THEN** system returns cached result

#### Scenario: Expired TTL

- **WHEN** cached analysis is 100 days old and TTL is 90 days
- **THEN** system treats as cache miss and re-analyzes

### Requirement: Force reanalysis

The system SHALL support bypassing cache via force_reanalysis parameter.

#### Scenario: Forced reanalysis

- **WHEN** user requests analysis with force_reanalysis=true
- **THEN** system bypasses cache and calls Claude API
- **AND** stores new result replacing cached version

### Requirement: Cache statistics

The system SHALL track cache hit rate and cost savings metrics.

#### Scenario: Hit rate calculation

- **WHEN** querying cache statistics for time period
- **THEN** system returns total_analyses, cache_hits, hit_rate_percentage, estimated_cost_savings

#### Scenario: Cost savings

- **WHEN** cache hit occurs
- **THEN** system records tokens_saved (avg 30K tokens per analysis)
- **AND** calculates cost_savings = (tokens_saved / 1000) × $0.003
