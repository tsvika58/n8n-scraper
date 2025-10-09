# Getting Started with n8n Scraper

This guide will walk you through setting up and using the n8n scraper for the first time.

## Prerequisites

Before you begin, ensure you have:
- Node.js 18+ installed
- npm or pnpm package manager
- Git (for version control)
- Basic understanding of web scraping concepts

## Installation

### 1. Navigate to the project
```bash
cd /Users/tsvikavagman/Desktop/Code\ Projects/shared-tools/n8n-scraper
```

### 2. Install dependencies
```bash
npm install
```

This will install:
- `axios` - HTTP client for API requests
- `cheerio` - HTML parsing and manipulation
- `puppeteer` - Browser automation
- `playwright` - Advanced browser automation
- `dotenv` - Environment configuration

### 3. Configure environment

Copy the example environment file:
```bash
cp temp-env-example.txt .env
```

Edit `.env` to customize settings:
```env
# Essential settings
N8N_WORKFLOWS_URL=https://n8n.io/workflows
SCRAPE_DELAY_MS=1000
LOG_LEVEL=info
```

## First Run

### Run the main application
```bash
npm start
```

This displays welcome information and available commands.

### Run a specific scraper
```bash
# Workflows
npm run scrape:workflows

# Nodes
npm run scrape:nodes

# Documentation
npm run scrape:docs

# All scrapers
npm run scrape:all
```

## Understanding the Output

### Data Storage Structure

```
data/
├── raw/              # Unprocessed scraped data
│   ├── workflows/
│   ├── nodes/
│   └── documentation/
└── processed/        # Cleaned and structured data
    ├── workflows/
    ├── nodes/
    └── documentation/
```

### Data Format

All data is stored in JSON format:

```json
{
  "metadata": {
    "version": "1.0.0",
    "scraped_at": "2025-10-09T12:00:00Z",
    "source": "n8n.io/workflows",
    "scraper_version": "1.0.0"
  },
  "data": [
    {
      "id": "workflow-123",
      "name": "Example Workflow",
      // ... more fields
    }
  ]
}
```

## Next Steps

### 1. Customize Scrapers

Edit scraper files in `src/scrapers/` to:
- Add new data sources
- Customize parsing logic
- Implement error handling
- Add rate limiting

### 2. Add Documentation

Place your existing documents in:
- `docs/architecture/` - Technical architecture
- `docs/guides/` - Usage guides
- `docs/research/` - Research findings
- `docs/scraped-data/` - Data schemas

### 3. Process Data

After scraping, process the data:
```bash
npm run process
npm run validate
```

### 4. Integration

Use the scraped data in your n8n-claude-engine:
- Import processed JSON files
- Build training datasets
- Create node recommendations
- Generate workflow suggestions

## Common Tasks

### View Scraped Data
```bash
# List raw data
ls -la data/raw/

# View a specific file
cat data/raw/workflows/latest.json | jq
```

### Clean Data
```bash
npm run clean
```

### Validate Data
```bash
npm run validate
```

## Development Workflow

1. **Research** - Understand n8n's structure
2. **Implement** - Write scraper code
3. **Test** - Run small test scrapes
4. **Refine** - Improve parsing and error handling
5. **Document** - Update docs with findings
6. **Scale** - Run full scrapes

## Best Practices

### Rate Limiting
- Respect n8n's servers
- Use delays between requests
- Implement exponential backoff
- Cache responses when possible

### Error Handling
- Log all errors
- Implement retries
- Save progress incrementally
- Validate data immediately

### Data Quality
- Validate against schemas
- Check for duplicates
- Verify required fields
- Document anomalies

## Troubleshooting

### Scraper Times Out
- Increase `BROWSER_TIMEOUT` in `.env`
- Reduce `MAX_CONCURRENT_REQUESTS`
- Add more delays

### Invalid Data
- Check parsing logic
- Validate HTML structure hasn't changed
- Review error logs
- Test with single items first

### Out of Memory
- Process data in batches
- Enable `COMPRESS_OUTPUT`
- Clean up temporary files
- Increase Node.js memory limit

## Getting Help

- Review documentation in `docs/`
- Check example scrapers
- Review n8n's robots.txt
- Open an issue for bugs

## What's Next?

- [Scraper Development Guide](./scraper-development.md)
- [Data Processing Guide](./data-processing.md)
- [Integration Guide](./integration-guide.md)
- [Architecture Overview](../architecture/README.md)

Happy scraping! 🚀

