"""
Debug Failed Workflows: Investigate 1870 and 2019

Deep investigation to understand why these workflows extracted 0 characters.

Author: Developer-2 (Dev2)
Task: SCRAPE-005 Rework - Failure Analysis
Date: October 9, 2025
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.scrapers.layer3_explainer import ExplainerContentExtractor
from playwright.async_api import async_playwright
from loguru import logger

logger.remove()
logger.add(sys.stdout, format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | {message}")


async def deep_debug_workflow(workflow_id: str, url: str):
    """Deep debugging of a single workflow"""
    
    logger.info(f"="*70)
    logger.info(f"DEEP DEBUG: Workflow {workflow_id}")
    logger.info(f"URL: {url}")
    logger.info(f"="*70)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # Non-headless to see what's happening
        page = await browser.new_page()
        
        try:
            logger.info(f"1. Navigating to page...")
            await page.goto(url, wait_until="domcontentloaded")
            await page.wait_for_timeout(5000)
            
            # Get page title
            title = await page.title()
            logger.info(f"   Page title: {title}")
            
            # Check if page loaded
            content = await page.content()
            logger.info(f"   HTML content length: {len(content)} bytes")
            
            # Look for description
            logger.info(f"\n2. Looking for workflow description...")
            desc_selectors = ['.workflow-description', '.description', 'article p']
            for selector in desc_selectors:
                try:
                    elem = await page.query_selector(selector)
                    if elem:
                        text = await elem.inner_text()
                        logger.info(f"   Found with {selector}: {text[:100]}...")
                        break
                except:
                    logger.debug(f"   {selector} not found")
            
            # Look for iframes
            logger.info(f"\n3. Looking for iframes...")
            frames = page.frames
            logger.info(f"   Total frames: {len(frames)}")
            for i, frame in enumerate(frames):
                logger.info(f"   Frame {i}: {frame.url}")
            
            # Try to find explainer iframe
            logger.info(f"\n4. Looking for explainer iframe...")
            iframe_selectors = [
                'iframe[title*="explainer"]',
                'iframe[title*="tutorial"]',
                'iframe[name="explainer"]',
                'iframe'
            ]
            
            for selector in iframe_selectors:
                try:
                    iframe_count = await page.locator(selector).count()
                    if iframe_count > 0:
                        logger.info(f"   Found {iframe_count} iframe(s) with selector: {selector}")
                        
                        # Try to get content
                        iframe = page.frame_locator(selector).first
                        try:
                            iframe_content = await iframe.locator('body').inner_text()
                            logger.info(f"   Iframe content length: {len(iframe_content)} chars")
                            logger.info(f"   Sample: {iframe_content[:200]}...")
                        except:
                            logger.warning(f"   Could not extract content from iframe")
                except Exception as e:
                    logger.debug(f"   {selector} search failed: {str(e)}")
            
            # Check for article/main content
            logger.info(f"\n5. Looking for main article content...")
            article_selectors = ['article', 'main', '.content', '.workflow-content']
            for selector in article_selectors:
                try:
                    elem = await page.query_selector(selector)
                    if elem:
                        text = await elem.inner_text()
                        logger.info(f"   Found {selector}: {len(text)} chars")
                        if len(text) > 100:
                            logger.info(f"   Sample: {text[:200]}...")
                except:
                    pass
            
            # Look for images
            logger.info(f"\n6. Looking for images...")
            img_count = await page.locator('img').count()
            logger.info(f"   Total images found: {img_count}")
            
            # Manual inspection pause
            logger.info(f"\n7. Manual inspection window (10 seconds)...")
            logger.info(f"   Check the browser window to see the page")
            await page.wait_for_timeout(10000)
            
        finally:
            await browser.close()
    
    logger.info(f"\n" + "="*70)
    logger.info(f"DEBUG COMPLETE for workflow {workflow_id}")
    logger.info(f"="*70)


async def main():
    """Debug both failed workflows"""
    
    failed_workflows = [
        {"id": "1870", "url": "https://n8n.io/workflows/1870", "name": "GitHub Issues Tracker"},
        {"id": "2019", "url": "https://n8n.io/workflows/2019", "name": "CRM Integration"},
    ]
    
    for workflow in failed_workflows:
        logger.info(f"\n\n{'#'*70}")
        logger.info(f"# INVESTIGATING: {workflow['name']}")
        logger.info(f"{'#'*70}\n")
        
        await deep_debug_workflow(workflow['id'], workflow['url'])
        
        logger.info(f"\n⏸️  Pausing 3 seconds before next workflow...\n")
        await asyncio.sleep(3)
    
    logger.success("\n✅ Debugging complete for both failed workflows")
    logger.info("\nNext steps:")
    logger.info("1. Analyze the findings above")
    logger.info("2. Identify root cause of 0 character extractions")
    logger.info("3. Implement fixes in layer3_explainer.py")
    logger.info("4. Retest to achieve 90%+ success rate")


if __name__ == "__main__":
    asyncio.run(main())





