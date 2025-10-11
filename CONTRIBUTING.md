# Contributing to n8n Scraper

Thank you for your interest in contributing to the n8n Scraper project!

## Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd n8n-scraper
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Configure environment**
   ```bash
   cp temp-env-example.txt .env
   # Edit .env with your settings
   ```

4. **Run the scraper**
   ```bash
   npm start
   ```

## Project Structure

```
n8n-scraper/
├── docs/           # Documentation
├── src/
│   ├── scrapers/   # Individual scraper modules
│   ├── parsers/    # Data transformation
│   └── utils/      # Shared utilities
├── data/           # Scraped data storage
├── scripts/        # Utility scripts
└── tests/          # Test files
```

## Adding a New Scraper

1. **Create scraper file** in `src/scrapers/your-scraper.js`
2. **Follow the template**:
   ```javascript
   async function scrapeYourData() {
     // Implementation
   }
   
   export { scrapeYourData };
   ```
3. **Document it** in `docs/guides/`
4. **Add tests** in `tests/`
5. **Update README** with new functionality

## Code Style

- Use ES6+ modern JavaScript
- Add JSDoc comments for functions
- Use descriptive variable names
- Keep functions small and focused
- Handle errors gracefully

## Testing

```bash
npm test
```

## Documentation

- Document all public APIs
- Add examples to guides
- Update schemas when data structure changes
- Keep README.md current

## Submitting Changes

1. Create a feature branch
2. Make your changes
3. Add tests
4. Update documentation
5. Submit a pull request

## Questions?

Check the `docs/` folder or open an issue.




