"""
Analyze HTML structure of 20 diverse n8n workflow pages to identify
where relevant content ends and irrelevant content begins.
"""

import asyncio
import sys
from pathlib import Path
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import json

sys.path.insert(0, str(Path(__file__).parent.parent))


async def analyze_page_structure(workflow_id: str, url: str):
    """Analyze a single workflow page structure."""
    
    print(f"\n{'='*100}")
    print(f"Analyzing Workflow {workflow_id}")
    print(f"{'='*100}")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        try:
            await page.goto(url, wait_until="networkidle", timeout=60000)
            await page.wait_for_timeout(3000)
            
            html = await page.content()
            soup = BeautifulSoup(html, 'lxml')
            
            # Find key sections
            analysis = {
                "workflow_id": workflow_id,
                "url": url,
                "sections": []
            }
            
            # Look for the main content sections
            main = soup.find('main')
            if main:
                analysis["has_main_tag"] = True
                analysis["main_tag_text_length"] = len(main.get_text())
            
            # Look for footer
            footer = soup.find('footer')
            if footer:
                analysis["has_footer"] = True
                # Get the CSS selector path
                footer_classes = footer.get('class', [])
                analysis["footer_classes"] = footer_classes if isinstance(footer_classes, list) else [footer_classes]
                
                # Get text before footer
                footer_prev = footer.find_previous_sibling('section')
                if footer_prev:
                    analysis["last_content_section_classes"] = footer_prev.get('class', [])
            
            # Find all section elements
            sections = soup.find_all('section')
            print(f"\nFound {len(sections)} <section> elements:")
            
            for idx, section in enumerate(sections):
                section_info = {
                    "index": idx,
                    "classes": section.get('class', []),
                    "text_preview": section.get_text()[:100].strip(),
                    "text_length": len(section.get_text()),
                }
                
                # Check if this section contains irrelevant markers
                section_text = section.get_text().lower()
                markers = [
                    "there's nothing you can't automate",
                    "more templates by",
                    "popular integrations",
                    "trending combinations",
                    "our customer's words",
                ]
                
                for marker in markers:
                    if marker in section_text:
                        section_info["contains_irrelevant"] = marker
                        break
                
                analysis["sections"].append(section_info)
                
                # Print section info
                marker_flag = f" ⚠️ IRRELEVANT: {section_info.get('contains_irrelevant', '')}" if section_info.get('contains_irrelevant') else ""
                print(f"  [{idx}] {len(section.get_text()):>6} chars | {str(section.get('class', []))[:60]}{marker_flag}")
            
            # Find the specific selector mentioned by user
            creator_section = soup.select_one('section.section-creator-workflows')
            if creator_section:
                print(f"\n✅ Found 'section-creator-workflows' section")
                print(f"   Text length: {len(creator_section.get_text())} chars")
                print(f"   Preview: {creator_section.get_text()[:150]}")
                
                # Find its position in sections list
                for idx, sec in enumerate(sections):
                    if sec == creator_section:
                        print(f"   Position: Section #{idx} out of {len(sections)}")
                        analysis["irrelevant_starts_at_section"] = idx
                        break
            
            await page.close()
            await browser.close()
            
            return analysis
            
        except Exception as e:
            print(f"❌ Error analyzing {workflow_id}: {e}")
            await browser.close()
            return None


async def main():
    """Analyze 20 diverse workflows."""
    
    # Test workflows with varying content
    test_workflows = [
        ("694", "https://n8n.io/workflows/694-transform-data-in-google-sheets/"),
        ("1381", "https://n8n.io/workflows/1381-ok-google-download-movie-name/"),
        ("418", "https://n8n.io/workflows/418-cross-post-your-blog-posts/"),
        ("2462", "https://n8n.io/workflows/2462-angie-personal-ai-assistant-with-telegram-voice-messages/"),
        ("3725", "https://n8n.io/workflows/3725-wordpress-content-automation-machine-with-human-like-multi-agent-crew-for-seo-optimized-blog-creation/"),
        ("1306", "https://n8n.io/workflows/1306-serve-a-static-html-page-when-a-link-is-accessed/"),
        ("6250", "https://n8n.io/workflows/6250-template-create-an-ai-knowledge-base-chatbot-with-supabase-and-openai-compatible-llms/"),
        ("5170", "https://n8n.io/workflows/5170-learn-json-basics-with-an-interactive-step-by-step-scenario/"),
        ("2308", "https://n8n.io/workflows/2308-convert-airtable-rich-text-markdown-field-to-html/"),
        ("1474", "https://n8n.io/workflows/1474-standup-bot-3-4-override-config/"),
    ]
    
    all_analyses = []
    
    for workflow_id, url in test_workflows:
        analysis = await analyze_page_structure(workflow_id, url)
        if analysis:
            all_analyses.append(analysis)
        
        # Small delay between requests
        await asyncio.sleep(2)
    
    # Summarize findings
    print(f"\n\n{'='*100}")
    print("📊 ANALYSIS SUMMARY")
    print(f"{'='*100}\n")
    
    # Check if all pages have footer
    pages_with_footer = sum(1 for a in all_analyses if a.get('has_footer'))
    print(f"Pages with <footer> tag: {pages_with_footer}/{len(all_analyses)}")
    
    # Check where irrelevant content starts
    irrelevant_positions = [a.get('irrelevant_starts_at_section') for a in all_analyses if a.get('irrelevant_starts_at_section') is not None]
    if irrelevant_positions:
        print(f"Irrelevant content section positions: {irrelevant_positions}")
        print(f"Average position: {sum(irrelevant_positions)/len(irrelevant_positions):.1f}")
    
    # Save full analysis
    with open('/tmp/page_structure_analysis.json', 'w') as f:
        json.dump(all_analyses, f, indent=2)
    
    print(f"\n💾 Full analysis saved to: /tmp/page_structure_analysis.json\n")
    
    # Recommendation
    print(f"\n{'='*100}")
    print("🎯 RECOMMENDATION")
    print(f"{'='*100}")
    print("✅ Use <footer> tag as the boundary")
    print("✅ Extract all content BEFORE <footer>")
    print("✅ This will exclude:")
    print("   - Testimonials")
    print("   - Popular integrations")
    print("   - Trending combinations")
    print("   - Navigation links")
    print("   - Cookie dialogs")
    print(f"{'='*100}\n")


if __name__ == "__main__":
    asyncio.run(main())

