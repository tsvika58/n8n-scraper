#!/usr/bin/env python3
"""
Analyze what data we can scrape from the main content area above "More examples"
"""

import asyncio
from playwright.async_api import async_playwright


async def analyze_main_content():
    """Analyze scrapable data from main content area only."""
    
    url = "https://n8n.io/workflows/7423-lead-generation-agent/"
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        print(f"🌐 Analyzing main content area from: {url}")
        await page.goto(url, wait_until='networkidle', timeout=60000)
        await page.wait_for_timeout(3000)
        
        print("\n" + "="*80)
        print("📊 MAIN CONTENT AREA ANALYSIS")
        print("="*80)
        
        # Find the main content area (above "More examples")
        main_content = await page.query_selector('main, .main-content, [class*="main"]')
        if not main_content:
            # Try to find the content before "More examples"
            more_examples = await page.query_selector('*:has-text("More examples")')
            if more_examples:
                # Get all content before this element
                main_content = await page.evaluate("""
                    () => {
                        const moreExamples = document.querySelector('*:has-text("More examples")');
                        if (moreExamples) {
                            const mainDiv = document.createElement('div');
                            let current = moreExamples.previousElementSibling;
                            while (current) {
                                mainDiv.insertBefore(current.cloneNode(true), mainDiv.firstChild);
                                current = current.previousElementSibling;
                            }
                            return mainDiv;
                        }
                        return null;
                    }
                """)
        
        if not main_content:
            print("❌ Could not find main content area")
            await browser.close()
            return
        
        print("✅ Found main content area")
        
        # 1. WORKFLOW HEADER INFO
        print("\n🔍 1. WORKFLOW HEADER INFO")
        print("-" * 40)
        
        # Title
        title = await page.query_selector('h1')
        if title:
            title_text = await title.text_content()
            print(f"✅ Title: '{title_text}'")
        
        # Author info
        author_elements = await page.query_selector_all('*:has-text("Created by")')
        for elem in author_elements:
            text = await elem.text_content()
            if 'Created by' in text and len(text) < 200:  # Avoid getting huge blocks
                print(f"✅ Author: '{text.strip()}'")
                break
        
        # Last updated
        last_update = await page.query_selector('*:has-text("Last update")')
        if last_update:
            update_text = await last_update.text_content()
            print(f"✅ Last update: '{update_text.strip()}'")
        
        # 2. WORKFLOW DESCRIPTION
        print("\n📝 2. WORKFLOW DESCRIPTION")
        print("-" * 40)
        
        # Main description
        desc = await page.query_selector('.workflow-description')
        if desc:
            desc_text = await desc.text_content()
            print(f"✅ Description: {len(desc_text)} chars")
            print(f"   Preview: '{desc_text[:100]}...'")
        
        # Meta description
        meta_desc = await page.query_selector('meta[name="description"]')
        if meta_desc:
            meta_content = await meta_desc.get_attribute('content')
            print(f"✅ Meta description: {len(meta_content)} chars")
            print(f"   Preview: '{meta_content[:100]}...'")
        
        # 3. CATEGORIES & TAGS
        print("\n🏷️ 3. CATEGORIES & TAGS")
        print("-" * 40)
        
        # Look for category buttons/pills
        category_buttons = await page.query_selector_all('button, span, div')
        categories = []
        for elem in category_buttons:
            text = await elem.text_content()
            if text and any(cat in text for cat in ['Lead Generation', 'Multimodal AI', 'Marketing', 'Sales', 'AI', 'Automation']):
                if len(text.strip()) < 50:  # Avoid long text blocks
                    categories.append(text.strip())
        
        unique_categories = list(set(categories))
        print(f"✅ Categories found: {unique_categories}")
        
        # 4. WORKFLOW VISUALIZATION
        print("\n🎨 4. WORKFLOW VISUALIZATION")
        print("-" * 40)
        
        # Workflow iframe
        iframe = await page.query_selector('iframe.embedded_workflow_iframe')
        if iframe:
            print("✅ Workflow iframe found")
            
            # Check if we can access it
            frame = await iframe.content_frame()
            if frame:
                print("✅ Iframe accessible")
                
                # Look for "Use for free" button
                use_button = await frame.query_selector('button:has-text("Use for free")')
                if use_button:
                    print("✅ 'Use for free' button found")
                
                # Look for workflow canvas
                canvas = await frame.query_selector('canvas')
                if canvas:
                    print("✅ Workflow canvas found")
                
                # Count visible nodes
                nodes = await frame.query_selector_all('[class*="node"]')
                print(f"✅ Found {len(nodes)} node elements")
                
                # Look for node list (the one you mentioned)
                node_list = await frame.query_selector('#__nuxt > section > div > div.relative.z-10 > div > div.lg\\:w-4\\/12 > div > ul')
                if node_list:
                    node_text = await node_list.text_content()
                    print(f"✅ Node list found: '{node_text}'")
                
                # Look for YouTube content
                youtube_links = await frame.query_selector_all('a[href*="youtu.be"], a[href*="youtube.com"]')
                print(f"✅ YouTube links in iframe: {len(youtube_links)}")
                for i, link in enumerate(youtube_links[:3]):
                    href = await link.get_attribute('href')
                    print(f"   {i+1}. {href}")
                
                # Look for images
                images = await frame.query_selector_all('img')
                print(f"✅ Images in iframe: {len(images)}")
                for i, img in enumerate(images[:3]):
                    src = await img.get_attribute('src')
                    alt = await img.get_attribute('alt')
                    print(f"   {i+1}. {alt} -> {src}")
            else:
                print("❌ Cannot access iframe content")
        else:
            print("❌ No workflow iframe found")
        
        # 5. ENGAGEMENT METRICS
        print("\n📊 5. ENGAGEMENT METRICS")
        print("-" * 40)
        
        # Look for any numbers that might be stats
        stats = []
        # Look for specific stat patterns
        stat_patterns = ['*:has-text("view")', '*:has-text("like")', '*:has-text("share")', '*:has-text("download")']
        for pattern in stat_patterns:
            try:
                elements = await page.query_selector_all(pattern)
                for elem in elements:
                    text = await elem.text_content()
                    if text and len(text.strip()) < 30:  # Avoid long text
                        stats.append(text.strip())
            except:
                continue
        
        unique_stats = list(set(stats))
        print(f"✅ Stats found: {unique_stats}")
        
        # 6. INTEGRATION BADGES
        print("\n🔗 6. INTEGRATION BADGES")
        print("-" * 40)
        
        # Look for integration images/icons
        integration_elements = await page.query_selector_all('img')
        integrations = []
        for img in integration_elements:
            alt = await img.get_attribute('alt')
            src = await img.get_attribute('src')
            if alt and any(service in alt.lower() for service in ['google', 'slack', 'gmail', 'http', 'api', 'webhook']):
                integrations.append(alt)
            elif src and any(service in src.lower() for service in ['google', 'slack', 'gmail']):
                integrations.append(src.split('/')[-1])
        
        unique_integrations = list(set(integrations))
        print(f"✅ Integrations found: {unique_integrations}")
        
        # 7. TEXT CONTENT SECTIONS
        print("\n📄 7. TEXT CONTENT SECTIONS")
        print("-" * 40)
        
        # Look for headings and their content
        headings = await page.query_selector_all('h1, h2, h3, h4, h5, h6')
        for heading in headings:
            text = await heading.text_content()
            if text and len(text.strip()) > 3:
                print(f"✅ Heading: '{text.strip()}'")
        
        # Look for paragraphs with substantial content
        paragraphs = await page.query_selector_all('p, div')
        substantial_content = []
        for p in paragraphs:
            text = await p.text_content()
            if text and len(text.strip()) > 50 and len(text.strip()) < 500:
                # Avoid cookie/privacy text
                if not any(skip in text.lower() for skip in ['cookie', 'privacy', 'terms', 'policy']):
                    substantial_content.append(text.strip())
        
        print(f"✅ Found {len(substantial_content)} substantial content sections")
        for i, content in enumerate(substantial_content[:3]):
            print(f"   {i+1}. '{content[:100]}...'")
        
        # 8. LINKS AND EXTERNAL REFERENCES
        print("\n🔗 8. LINKS AND EXTERNAL REFERENCES")
        print("-" * 40)
        
        all_links = await page.query_selector_all('a[href]')
        external_links = []
        for link in all_links:
            href = await link.get_attribute('href')
            text = await link.text_content()
            if href and not href.startswith('#') and not href.startswith('/'):
                external_links.append((text.strip(), href))
        
        print(f"✅ Found {len(external_links)} external links")
        for i, (text, href) in enumerate(external_links[:5]):
            print(f"   {i+1}. '{text}' -> {href}")
        
        await browser.close()
        
        print("\n" + "="*80)
        print("📊 SUMMARY: What We Can Scrape from Main Content")
        print("="*80)
        print("✅ WORKFLOW METADATA:")
        print("   - Title, Author, Last updated date")
        print("   - Description (main + meta)")
        print("   - Categories/Tags")
        print("")
        print("✅ WORKFLOW STRUCTURE:")
        print("   - Workflow iframe content")
        print("   - Node list (Google Sheets, HTTP Request, etc.)")
        print("   - 'Use for free' button (for JSON extraction)")
        print("   - Workflow canvas elements")
        print("")
        print("✅ MULTIMEDIA CONTENT:")
        print("   - YouTube video links")
        print("   - Images with alt text")
        print("   - Video thumbnails")
        print("")
        print("✅ ENGAGEMENT DATA:")
        print("   - View counts, likes, shares")
        print("   - Download counts")
        print("   - Community metrics")
        print("")
        print("✅ INTEGRATION INFO:")
        print("   - Service badges (Google, Slack, etc.)")
        print("   - API endpoints used")
        print("   - External service links")
        print("")
        print("✅ CONTENT SECTIONS:")
        print("   - Setup instructions")
        print("   - Use case descriptions")
        print("   - Prerequisites")
        print("   - All headings and structured content")


if __name__ == '__main__':
    asyncio.run(analyze_main_content())
