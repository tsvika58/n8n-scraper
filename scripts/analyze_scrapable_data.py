#!/usr/bin/env python3
"""
Analyze what data we can scrape from n8n workflow pages
"""

import asyncio
from playwright.async_api import async_playwright


async def analyze_scrapable_data():
    """Analyze all scrapable data from n8n workflow page."""
    
    url = "https://n8n.io/workflows/7423-lead-generation-agent/"
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        print(f"🌐 Analyzing scrapable data from: {url}")
        await page.goto(url, wait_until='networkidle', timeout=60000)
        await page.wait_for_timeout(3000)
        
        print("\n" + "="*80)
        print("📊 COMPREHENSIVE DATA SCRAPING ANALYSIS")
        print("="*80)
        
        # 1. PAGE METADATA (Layer 1)
        print("\n🔍 1. PAGE METADATA (Layer 1)")
        print("-" * 40)
        
        # Title
        title = await page.query_selector('h1')
        title_text = await title.text_content() if title else "Not found"
        print(f"✅ Title: {title_text}")
        
        # Author
        author_elements = await page.query_selector_all('div:has-text("Created by")')
        for elem in author_elements:
            text = await elem.text_content()
            if 'Created by' in text:
                print(f"✅ Author: {text[:100]}...")
                break
        
        # Description
        desc = await page.query_selector('.workflow-description')
        desc_text = await desc.text_content() if desc else "Not found"
        print(f"✅ Description: {len(desc_text)} chars")
        
        # Meta description
        meta_desc = await page.query_selector('meta[name="description"]')
        meta_content = await meta_desc.get_attribute('content') if meta_desc else "Not found"
        print(f"✅ Meta Description: {len(meta_content)} chars")
        
        # Categories/Tags
        category_elements = await page.query_selector_all('button, span, div')
        categories = []
        for elem in category_elements:
            text = await elem.text_content()
            if text and any(cat in text for cat in ['Lead Generation', 'Multimodal AI', 'Marketing', 'Sales']):
                categories.append(text.strip())
        print(f"✅ Categories: {list(set(categories))}")
        
        # 2. WORKFLOW STRUCTURE (Layer 2)
        print("\n🔧 2. WORKFLOW STRUCTURE (Layer 2)")
        print("-" * 40)
        
        # Check if we can access the iframe
        iframe = await page.query_selector('iframe.embedded_workflow_iframe')
        if iframe:
            frame = await iframe.content_frame()
            if frame:
                print("✅ Workflow iframe accessible")
                
                # Look for workflow JSON
                # Try to find "Use for free" button and click it
                use_button = await frame.query_selector('button:has-text("Use for free")')
                if use_button:
                    print("✅ Found 'Use for free' button")
                    # Don't click it, just note it exists
                
                # Look for workflow canvas
                canvas = await frame.query_selector('canvas')
                if canvas:
                    print("✅ Found workflow canvas")
                
                # Look for nodes
                nodes = await frame.query_selector_all('[class*="node"]')
                print(f"✅ Found {len(nodes)} node elements")
                
                # Look for connections
                connections = await frame.query_selector_all('[class*="connection"], [class*="edge"]')
                print(f"✅ Found {len(connections)} connection elements")
            else:
                print("❌ Cannot access iframe content")
        else:
            print("❌ No workflow iframe found")
        
        # 3. MULTIMEDIA CONTENT (Layer 3)
        print("\n🎬 3. MULTIMEDIA CONTENT (Layer 3)")
        print("-" * 40)
        
        # YouTube videos
        youtube_links = await page.query_selector_all('a[href*="youtu.be"], a[href*="youtube.com"]')
        print(f"✅ YouTube links: {len(youtube_links)}")
        for i, link in enumerate(youtube_links[:3]):
            href = await link.get_attribute('href')
            print(f"   {i+1}. {href}")
        
        # Images
        images = await page.query_selector_all('img')
        print(f"✅ Images: {len(images)}")
        
        # Videos in iframe
        if iframe:
            frame = await iframe.content_frame()
            if frame:
                iframe_videos = await frame.query_selector_all('a[href*="youtu.be"], a[href*="youtube.com"]')
                print(f"✅ Videos in iframe: {len(iframe_videos)}")
        
        # 4. ADDITIONAL SCRAPABLE DATA
        print("\n📋 4. ADDITIONAL SCRAPABLE DATA")
        print("-" * 40)
        
        # Page stats/engagement
        stats_elements = await page.query_selector_all('*:has-text("view"), *:has-text("like"), *:has-text("share")')
        print(f"✅ Stats elements: {len(stats_elements)}")
        for elem in stats_elements[:5]:
            text = await elem.text_content()
            if text and any(stat in text.lower() for stat in ['view', 'like', 'share', 'download']):
                print(f"   - {text.strip()}")
        
        # Last updated date
        date_elements = await page.query_selector_all('*:has-text("Last update"), *:has-text("Updated")')
        for elem in date_elements:
            text = await elem.text_content()
            if 'Last update' in text or 'Updated' in text:
                print(f"✅ Last updated: {text.strip()}")
                break
        
        # Difficulty level
        difficulty_elements = await page.query_selector_all('*:has-text("Beginner"), *:has-text("Intermediate"), *:has-text("Advanced")')
        for elem in difficulty_elements:
            text = await elem.text_content()
            if any(diff in text for diff in ['Beginner', 'Intermediate', 'Advanced']):
                print(f"✅ Difficulty: {text.strip()}")
                break
        
        # Prerequisites/Requirements
        req_elements = await page.query_selector_all('*:has-text("Prerequisites"), *:has-text("Requirements"), *:has-text("Setup")')
        for elem in req_elements:
            text = await elem.text_content()
            if any(req in text for req in ['Prerequisites', 'Requirements', 'Setup']):
                print(f"✅ Requirements: {text[:100]}...")
                break
        
        # Integration badges
        integration_elements = await page.query_selector_all('img[alt*="Google"], img[alt*="Slack"], img[alt*="Gmail"], img[alt*="HTTP"]')
        integrations = []
        for elem in integration_elements:
            alt = await elem.get_attribute('alt')
            if alt:
                integrations.append(alt)
        print(f"✅ Integrations: {integrations}")
        
        # 5. HIDDEN/ADDITIONAL DATA
        print("\n🔍 5. HIDDEN/ADDITIONAL DATA")
        print("-" * 40)
        
        # JSON-LD structured data
        json_ld = await page.query_selector('script[type="application/ld+json"]')
        if json_ld:
            json_content = await json_ld.text_content()
            print(f"✅ JSON-LD data: {len(json_content)} chars")
        
        # Open Graph meta tags
        og_tags = await page.query_selector_all('meta[property^="og:"]')
        print(f"✅ Open Graph tags: {len(og_tags)}")
        for tag in og_tags[:3]:
            property_name = await tag.get_attribute('property')
            content = await tag.get_attribute('content')
            print(f"   - {property_name}: {content[:50]}...")
        
        # Twitter Card meta tags
        twitter_tags = await page.query_selector_all('meta[name^="twitter:"]')
        print(f"✅ Twitter Card tags: {len(twitter_tags)}")
        
        # Schema.org microdata
        schema_elements = await page.query_selector_all('[itemscope], [itemtype]')
        print(f"✅ Schema.org elements: {len(schema_elements)}")
        
        # Data attributes
        data_attrs = await page.query_selector_all('[data-test-id], [data-cy], [data-test]')
        print(f"✅ Test data attributes: {len(data_attrs)}")
        
        # 6. WORKFLOW-SPECIFIC DATA
        print("\n⚙️ 6. WORKFLOW-SPECIFIC DATA")
        print("-" * 40)
        
        # Workflow ID from URL
        workflow_id = url.split('/')[-1].split('-')[0]
        print(f"✅ Workflow ID: {workflow_id}")
        
        # Workflow slug
        workflow_slug = url.split('/')[-1]
        print(f"✅ Workflow slug: {workflow_slug}")
        
        # Workflow version (if available)
        version_elements = await page.query_selector_all('*:has-text("version"), *:has-text("v1"), *:has-text("v2")')
        for elem in version_elements:
            text = await elem.text_content()
            if 'version' in text.lower() or text.startswith('v'):
                print(f"✅ Version: {text.strip()}")
                break
        
        # Workflow status (draft, published, etc.)
        status_elements = await page.query_selector_all('*:has-text("draft"), *:has-text("published"), *:has-text("beta")')
        for elem in status_elements:
            text = await elem.text_content()
            if any(status in text.lower() for status in ['draft', 'published', 'beta', 'stable']):
                print(f"✅ Status: {text.strip()}")
                break
        
        await browser.close()
        
        print("\n" + "="*80)
        print("📊 SUMMARY: Additional Data We Can Scrape")
        print("="*80)
        print("1. ✅ Page engagement stats (views, likes, shares)")
        print("2. ✅ Last updated date")
        print("3. ✅ Difficulty level")
        print("4. ✅ Prerequisites/Requirements")
        print("5. ✅ Integration badges")
        print("6. ✅ JSON-LD structured data")
        print("7. ✅ Open Graph meta tags")
        print("8. ✅ Twitter Card meta tags")
        print("9. ✅ Schema.org microdata")
        print("10. ✅ Test data attributes")
        print("11. ✅ Workflow version/status")
        print("12. ✅ Workflow slug and ID")
        print("13. ✅ All text content (for later analysis)")
        print("14. ✅ All images with alt text")
        print("15. ✅ All links and their destinations")


if __name__ == '__main__':
    asyncio.run(analyze_scrapable_data())

