#!/usr/bin/env node

/**
 * Run All Scrapers
 * 
 * Executes all scraper modules in sequence
 */

import 'dotenv/config';
import { scrapeWorkflows } from '../src/scrapers/workflow-scraper.js';
import { scrapeNodes } from '../src/scrapers/node-scraper.js';
import { scrapeDocumentation } from '../src/scrapers/documentation-scraper.js';

console.log('🚀 Running All Scrapers\n');

async function runAllScrapers() {
  const startTime = Date.now();
  
  try {
    console.log('1️⃣  Scraping Workflows...');
    await scrapeWorkflows();
    console.log('');
    
    console.log('2️⃣  Scraping Nodes...');
    await scrapeNodes();
    console.log('');
    
    console.log('3️⃣  Scraping Documentation...');
    await scrapeDocumentation();
    console.log('');
    
    const duration = ((Date.now() - startTime) / 1000).toFixed(2);
    console.log(`✅ All scrapers completed in ${duration}s`);
    
  } catch (error) {
    console.error('❌ Scraping failed:', error.message);
    process.exit(1);
  }
}

runAllScrapers();




