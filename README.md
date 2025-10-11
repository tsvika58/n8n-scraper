# n8n Data Scraper

A comprehensive scraper for collecting workflows, nodes, and other datasets from n8n to enhance the n8n-claude-engine with intelligent automation capabilities.

## 🎯 Project Purpose

This scraper collects structured data from n8n sources to:
- **Workflow Intelligence**: Gather real-world workflow patterns and examples
- **Node Documentation**: Extract detailed node configurations and capabilities
- **Best Practices**: Identify common patterns and anti-patterns
- **Training Data**: Build a rich dataset for AI-powered n8n assistance

## 📁 Project Structure

```
n8n-scraper/
├── docs/                    # Documentation and research notes
│   ├── scraped-data/       # Documentation about scraped datasets
│   ├── architecture/       # System design documents
│   └── guides/             # Usage and development guides
├── src/
│   ├── scrapers/           # Individual scraper modules
│   ├── parsers/            # Data parsing and transformation
│   └── utils/              # Shared utilities
├── data/
│   ├── raw/                # Raw scraped data (JSON, HTML, etc.)
│   └── processed/          # Cleaned and structured data
├── scripts/                # Automation and utility scripts
└── tests/                  # Test files
```

## 🚀 Getting Started

### Installation

```bash
npm install
```

### Configuration

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

### Running Scrapers

```bash
# Run all scrapers
npm run scrape:all

# Run specific scraper
npm run scrape:workflows
npm run scrape:nodes
npm run scrape:docs
```

## 📊 Data Sources

- **n8n Documentation**: Official documentation and API references
- **n8n Community Workflows**: Public workflow templates
- **n8n Node Library**: Complete node catalog with parameters
- **n8n Forum**: Community discussions and solutions
- **GitHub**: n8n repository insights

## 🔧 Scrapers

### Workflow Scraper
- Collects workflow templates from n8n.io
- Extracts node configurations and connections
- Captures workflow metadata and descriptions

### Node Scraper
- Documentation for all available nodes
- Parameter schemas and validation rules
- Input/output data structures
- Authentication requirements

### Documentation Scraper
- API documentation
- Integration guides
- Best practices articles
- Tutorial content

## 📝 Output Format

All scraped data is stored in structured JSON format:

```json
{
  "metadata": {
    "scraped_at": "2025-10-09T...",
    "source": "n8n.io/workflows",
    "version": "1.0.0"
  },
  "data": [...]
}
```

## 🔄 Data Processing Pipeline

1. **Scrape**: Collect raw data from sources
2. **Parse**: Extract structured information
3. **Clean**: Remove duplicates and normalize
4. **Validate**: Ensure data quality and completeness
5. **Store**: Save in organized format

## 🎯 Use Cases for n8n-claude-engine

- **Workflow Recommendations**: Suggest optimal node combinations
- **Auto-completion**: Intelligent parameter suggestions
- **Error Prevention**: Identify potential configuration issues
- **Pattern Recognition**: Learn from successful workflows
- **Documentation Context**: Provide relevant help in-context

## 📚 Documentation

- [Architecture Overview](docs/architecture/README.md)
- [Scraper Development Guide](docs/guides/scraper-development.md)
- [Data Schema Documentation](docs/scraped-data/README.md)

## 🛠️ Development

### Prerequisites

- Node.js 18+
- npm or pnpm
- Git

### Development Workflow

```bash
# Install dependencies
npm install

# Run in development mode
npm run dev

# Run tests
npm test

# Run tests with beautiful dashboard 🎨
make test-dash

# Lint code
npm run lint
```

## 📦 Available Scripts

### JavaScript/Scraping
- `npm run scrape:all` - Run all scrapers sequentially
- `npm run scrape:workflows` - Scrape workflow templates
- `npm run scrape:nodes` - Scrape node documentation
- `npm run scrape:docs` - Scrape general documentation
- `npm run process` - Process and clean raw data
- `npm run validate` - Validate scraped data
- `npm run dev` - Development mode with hot reload

### Python/Testing
- `npm test` / `make test` - Run test suite with coverage
- `make test-dash` - Run tests with beautiful real-time dashboard 🎨
- `make test-dash-fast` - Quick tests without coverage
- `make test-dash-unit` - Run unit tests with dashboard
- `make test-dash-integration` - Run integration tests with dashboard

> **New!** Check out the [Pytest Dashboard](PYTEST_DASHBOARD_QUICKSTART.md) for beautiful real-time test monitoring!

## 🤝 Contributing

1. Add new scrapers in `src/scrapers/`
2. Document data schemas in `docs/scraped-data/`
3. Add tests for new functionality
4. Update this README with new capabilities

## 📄 License

MIT

## 🔗 Related Projects

- [n8n-claude-engine](../../personal-products/n8n-claude-engine) - The main AI engine using this data
- [claude-n8n-integration](../../personal-products/mcp-projects/claude-n8n-integration) - MCP integration layer

## 📞 Support

For questions or issues, please refer to the documentation in the `docs/` folder or create an issue in the repository.




