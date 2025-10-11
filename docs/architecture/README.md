# Architecture Documentation

## System Overview

The n8n scraper is designed with modularity and extensibility in mind. Each scraper component is independent but follows a common interface pattern.

## Core Components

### 1. Scrapers (`/src/scrapers`)
Individual scraper modules that collect data from specific sources:
- `workflow-scraper.js` - Collects workflow templates
- `node-scraper.js` - Collects node documentation
- `documentation-scraper.js` - Collects general documentation

### 2. Parsers (`/src/parsers`)
Transform raw data into structured formats:
- Extract meaningful information
- Normalize data structures
- Handle edge cases

### 3. Utils (`/src/utils`)
Shared utilities:
- HTTP client with rate limiting
- Data validation
- File system operations
- Logging

### 4. Data Storage (`/data`)
Two-tier storage:
- **Raw**: Unprocessed data as received from sources
- **Processed**: Cleaned, validated, structured data

## Design Principles

1. **Modularity**: Each scraper is independent
2. **Robustness**: Handle errors gracefully
3. **Efficiency**: Rate limiting and caching
4. **Maintainability**: Clear code structure and documentation

## Data Flow

```
Source → Scraper → Raw Data → Parser → Processed Data → n8n-claude-engine
```

## Future Enhancements

- Real-time scraping with webhooks
- Incremental updates
- Distributed scraping
- Advanced caching strategies

Place detailed architecture documents in this directory.




