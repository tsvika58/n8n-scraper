#!/usr/bin/env node

/**
 * n8n Scraper - Main Entry Point
 * 
 * This is the main entry point for the n8n scraper application.
 * It orchestrates the scraping process and manages the overall workflow.
 */

import 'dotenv/config';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

console.log('🚀 n8n Scraper Starting...\n');

// Configuration
const config = {
  dataDir: process.env.DATA_DIR || './data',
  rawDataDir: process.env.RAW_DATA_DIR || './data/raw',
  processedDataDir: process.env.PROCESSED_DATA_DIR || './data/processed',
  logLevel: process.env.LOG_LEVEL || 'info',
};

console.log('📋 Configuration:', config);
console.log('\n');

// Main function
async function main() {
  console.log('👋 Welcome to the n8n Scraper!');
  console.log('');
  console.log('This tool helps you collect workflows, nodes, and documentation from n8n');
  console.log('to enhance the intelligence of your n8n-claude-engine.');
  console.log('');
  console.log('📚 Available Commands:');
  console.log('  npm run scrape:workflows  - Scrape workflow templates');
  console.log('  npm run scrape:nodes      - Scrape node documentation');
  console.log('  npm run scrape:docs       - Scrape general documentation');
  console.log('  npm run scrape:all        - Run all scrapers');
  console.log('');
  console.log('📖 Documentation: docs/README.md');
  console.log('🛠️  Start developing: src/scrapers/');
  console.log('');
  console.log('✨ Ready to build intelligent automation!');
}

main().catch((error) => {
  console.error('❌ Error:', error.message);
  process.exit(1);
});




