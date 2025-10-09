# Quick Start Guide

Get up and running with the n8n Scraper in 5 minutes!

## 🚀 Installation

```bash
cd /Users/tsvikavagman/Desktop/Code\ Projects/shared-tools/n8n-scraper
npm install
```

## ⚙️ Configuration

```bash
# Copy the example environment file
cp temp-env-example.txt .env

# Edit .env if needed (defaults work for most cases)
```

## 🎯 Your First Scrape

### Option 1: Run All Scrapers
```bash
npm run scrape:all
```

### Option 2: Run Individual Scrapers
```bash
# Scrape workflows
npm run scrape:workflows

# Scrape nodes
npm run scrape:nodes

# Scrape documentation
npm run scrape:docs
```

## 📊 View Results

Scraped data is saved in:
- **Raw data**: `data/raw/`
- **Processed data**: `data/processed/`

## 📚 Documentation

Your documents should go in:
- **Architecture**: `docs/architecture/`
- **Guides**: `docs/guides/`
- **Data schemas**: `docs/scraped-data/`
- **Research**: `docs/research/`

## 🔧 Development

```bash
# Run in development mode
npm run dev

# Run tests
npm test

# Process scraped data
npm run process

# Validate data
npm run validate
```

## 📖 Next Steps

1. **Add your documents** to `docs/` folders
2. **Customize scrapers** in `src/scrapers/`
3. **Review the architecture** in `docs/architecture/README.md`
4. **Read the full README** in `README.md`

## 🎓 Learning Resources

- [Main README](README.md) - Complete documentation
- [Architecture](docs/architecture/README.md) - System design
- [Contributing](CONTRIBUTING.md) - Development guidelines

## 🆘 Troubleshooting

### Common Issues

**"Module not found"**
- Run `npm install` to install dependencies

**"Permission denied"**
- Make sure scripts are executable: `chmod +x scripts/*.js`

**Scraper fails**
- Check your `.env` configuration
- Verify network connectivity
- Review rate limiting settings

## 💡 Tips

- Start with small test runs before full scrapes
- Use `LOG_LEVEL=debug` in `.env` for detailed output
- Enable `SAVE_RAW_HTML=true` for debugging
- Check `data/raw/` for intermediate results

## 🤝 Get Help

- Check `docs/` folder for detailed documentation
- Review example code in scrapers
- Open an issue if you're stuck

Happy scraping! 🎉

