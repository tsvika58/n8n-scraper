# Scraped Data Documentation

This directory contains documentation about the structure, schema, and format of all scraped data.

## Data Categories

### 1. Workflows
Workflow templates and examples from n8n.io

**Schema**: [workflow-schema.json](./schemas/workflow-schema.json)

**Fields**:
- `id` - Unique workflow identifier
- `name` - Workflow name
- `description` - Workflow description
- `nodes` - Array of node configurations
- `connections` - Node connection map
- `settings` - Workflow settings
- `tags` - Categorization tags
- `author` - Creator information
- `created_at` - Creation timestamp
- `updated_at` - Last update timestamp

### 2. Nodes
Node documentation and specifications

**Schema**: [node-schema.json](./schemas/node-schema.json)

**Fields**:
- `name` - Node name
- `displayName` - Human-readable name
- `description` - Node description
- `icon` - Icon reference
- `group` - Node category
- `version` - Node version
- `inputs` - Input parameters
- `outputs` - Output structure
- `credentials` - Required authentication
- `properties` - Configuration properties

### 3. Documentation
General documentation and guides

**Schema**: [documentation-schema.json](./schemas/documentation-schema.json)

**Fields**:
- `title` - Document title
- `url` - Source URL
- `content` - Document content
- `category` - Documentation category
- `tags` - Topic tags
- `last_updated` - Last update date

## Data Quality

All data is validated against schemas before being marked as processed.

Quality checks include:
- Schema validation
- Required field presence
- Data type verification
- Referential integrity
- Duplicate detection

## Usage Examples

See the [examples](./examples/) directory for sample data and usage patterns.

## Data Format

All data is stored in JSON format with this structure:

```json
{
  "metadata": {
    "version": "1.0.0",
    "scraped_at": "2025-10-09T...",
    "source": "n8n.io",
    "scraper_version": "1.0.0"
  },
  "data": [
    // Array of items
  ]
}
```

Place detailed data documentation in this directory.

