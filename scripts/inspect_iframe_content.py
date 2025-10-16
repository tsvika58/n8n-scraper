#!/usr/bin/env python3
"""
Deep inspection of iframe content to identify ALL data sources.
Focus on technical information, text boxes, videos, and explanatory content.
"""

import asyncio
from playwright.async_api import async_playwright
import json
from datetime import datetime


async def deep_inspect_iframe_content(workflow_id='1954'):
    """Deep inspection of iframe to extract ALL content types."""
    
    url = f'https://n8n.io/workflows/{workflow_id}'
    
    print(f"\n{'='*80}")
    print(f"🔬 DEEP IFRAME CONTENT INSPECTION: Workflow #{workflow_id}")
    print(f"{'='*80}\n")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        
        try:
            print("📄 Loading page...")
            await page.goto(url, wait_until='networkidle', timeout=30000)
            print("✅ Page loaded\n")
            
            # Wait for iframe to load
            await asyncio.sleep(5)
            
            # Get all frames
            frames = page.frames
            print(f"Total frames: {len(frames)}\n")
            
            # Find the n8n workflow iframe
            workflow_frame = None
            for frame in frames:
                if 'n8n-preview' in frame.url or 'demo' in frame.url:
                    workflow_frame = frame
                    print(f"✅ Found workflow iframe: {frame.url}\n")
                    break
            
            if not workflow_frame:
                print("❌ No workflow iframe found!")
                return
            
            # === EXTRACT ALL CONTENT FROM IFRAME ===
            print("🔍 EXTRACTING IFRAME CONTENT")
            print("="*80)
            
            # 1. Get full HTML
            print("\n1. HTML STRUCTURE")
            print("-"*40)
            html = await workflow_frame.content()
            print(f"HTML Size: {len(html):,} bytes")
            
            # Save HTML for analysis
            with open(f'iframe_html_{workflow_id}.html', 'w', encoding='utf-8') as f:
                f.write(html)
            print(f"💾 Saved: iframe_html_{workflow_id}.html")
            
            # 2. Extract all text content
            print("\n2. TEXT CONTENT")
            print("-"*40)
            
            # Get all text nodes
            all_text = await workflow_frame.evaluate('''
                () => {
                    return document.body.innerText;
                }
            ''')
            print(f"Total text length: {len(all_text):,} chars")
            print(f"Preview:\n{all_text[:500]}...\n")
            
            # Save text
            with open(f'iframe_text_{workflow_id}.txt', 'w', encoding='utf-8') as f:
                f.write(all_text)
            print(f"💾 Saved: iframe_text_{workflow_id}.txt")
            
            # 3. Find all text boxes / input fields
            print("\n3. TEXT BOXES / INPUT FIELDS")
            print("-"*40)
            
            text_inputs = await workflow_frame.locator('input[type="text"], textarea, [contenteditable="true"]').all()
            print(f"Found {len(text_inputs)} text input elements")
            
            for i, input_el in enumerate(text_inputs[:10], 1):
                try:
                    value = await input_el.input_value() if await input_el.get_attribute('type') != 'contenteditable' else await input_el.text_content()
                    placeholder = await input_el.get_attribute('placeholder')
                    print(f"\nInput #{i}:")
                    print(f"  Value: {value[:100] if value else 'N/A'}...")
                    print(f"  Placeholder: {placeholder or 'N/A'}")
                except Exception as e:
                    print(f"  Error: {e}")
            
            # 4. Find all videos
            print("\n4. VIDEOS")
            print("-"*40)
            
            videos = await workflow_frame.locator('video, iframe[src*="youtube"], iframe[src*="vimeo"]').all()
            print(f"Found {len(videos)} video elements")
            
            for i, video in enumerate(videos, 1):
                try:
                    tag = await video.evaluate('el => el.tagName')
                    src = await video.get_attribute('src')
                    print(f"\nVideo #{i}:")
                    print(f"  Type: {tag}")
                    print(f"  Source: {src or 'N/A'}")
                except Exception as e:
                    print(f"  Error: {e}")
            
            # 5. Find all images
            print("\n5. IMAGES")
            print("-"*40)
            
            images = await workflow_frame.locator('img').all()
            print(f"Found {len(images)} image elements")
            
            for i, img in enumerate(images[:10], 1):
                try:
                    src = await img.get_attribute('src')
                    alt = await img.get_attribute('alt')
                    print(f"\nImage #{i}:")
                    print(f"  Source: {src[:80] if src else 'N/A'}...")
                    print(f"  Alt: {alt or 'N/A'}")
                except Exception as e:
                    print(f"  Error: {e}")
            
            # 6. Find workflow nodes
            print("\n6. WORKFLOW NODES")
            print("-"*40)
            
            # Try multiple selectors for nodes
            node_selectors = [
                '[class*="node"]',
                '[data-node]',
                '[data-node-name]',
                '.node',
                '[role="button"]'
            ]
            
            for selector in node_selectors:
                try:
                    nodes = await workflow_frame.locator(selector).all()
                    if nodes:
                        print(f"\nSelector '{selector}': {len(nodes)} elements")
                        
                        # Get details from first few nodes
                        for i, node in enumerate(nodes[:5], 1):
                            try:
                                text = await node.text_content()
                                classes = await node.get_attribute('class')
                                data_attrs = await node.evaluate('''
                                    el => {
                                        const attrs = {};
                                        for (let attr of el.attributes) {
                                            if (attr.name.startsWith('data-')) {
                                                attrs[attr.name] = attr.value;
                                            }
                                        }
                                        return attrs;
                                    }
                                ''')
                                print(f"\n  Node #{i}:")
                                print(f"    Text: {text[:50] if text else 'N/A'}...")
                                print(f"    Classes: {classes[:80] if classes else 'N/A'}...")
                                print(f"    Data attrs: {data_attrs}")
                            except:
                                pass
                except Exception as e:
                    print(f"Selector '{selector}' error: {e}")
            
            # 7. Find explanatory text / descriptions
            print("\n7. EXPLANATORY TEXT / DESCRIPTIONS")
            print("-"*40)
            
            text_elements = await workflow_frame.locator('p, span, div[class*="description"], div[class*="text"]').all()
            print(f"Found {len(text_elements)} text elements")
            
            # Get substantial text blocks
            substantial_texts = []
            for el in text_elements[:50]:
                try:
                    text = await el.text_content()
                    if text and len(text.strip()) > 50:
                        substantial_texts.append(text.strip())
                except:
                    pass
            
            print(f"\nSubstantial text blocks: {len(substantial_texts)}")
            for i, text in enumerate(substantial_texts[:5], 1):
                print(f"\nText #{i}:")
                print(f"  {text[:200]}...")
            
            # 8. Extract structured data
            print("\n8. STRUCTURED DATA (JSON/Objects)")
            print("-"*40)
            
            try:
                structured_data = await workflow_frame.evaluate('''
                    () => {
                        const data = {
                            scripts: [],
                            jsonData: [],
                            windowKeys: Object.keys(window).filter(k => 
                                !k.startsWith('webkit') && 
                                !k.startsWith('chrome') &&
                                typeof window[k] === 'object' &&
                                window[k] !== null
                            ).slice(0, 20)
                        };
                        
                        // Look for JSON in script tags
                        document.querySelectorAll('script[type="application/json"]').forEach(script => {
                            try {
                                data.jsonData.push(JSON.parse(script.textContent));
                            } catch(e) {}
                        });
                        
                        return data;
                    }
                ''')
                
                print(f"Window object keys: {structured_data['windowKeys']}")
                print(f"JSON data blocks: {len(structured_data['jsonData'])}")
                
                if structured_data['jsonData']:
                    with open(f'iframe_json_data_{workflow_id}.json', 'w') as f:
                        json.dump(structured_data['jsonData'], f, indent=2)
                    print(f"💾 Saved: iframe_json_data_{workflow_id}.json")
                
            except Exception as e:
                print(f"Error extracting structured data: {e}")
            
            # 9. Get all links
            print("\n9. LINKS")
            print("-"*40)
            
            links = await workflow_frame.locator('a[href]').all()
            print(f"Found {len(links)} links")
            
            link_data = []
            for link in links[:10]:
                try:
                    href = await link.get_attribute('href')
                    text = await link.text_content()
                    link_data.append({'href': href, 'text': text})
                except:
                    pass
            
            for i, link in enumerate(link_data, 1):
                print(f"\nLink #{i}:")
                print(f"  Text: {link['text'][:50] if link['text'] else 'N/A'}...")
                print(f"  URL: {link['href'][:80] if link['href'] else 'N/A'}...")
            
            # 10. Take detailed screenshots
            print("\n10. SCREENSHOTS")
            print("-"*40)
            
            # Full page screenshot
            await page.screenshot(path=f'iframe_fullpage_{workflow_id}.png', full_page=True)
            print(f"📸 Saved: iframe_fullpage_{workflow_id}.png")
            
            # Iframe-specific screenshot
            iframe_element = page.locator('iframe[src*="n8n-preview"]').first
            if await iframe_element.count() > 0:
                await iframe_element.screenshot(path=f'iframe_only_{workflow_id}.png')
                print(f"📸 Saved: iframe_only_{workflow_id}.png")
            
            # Keep browser open for manual inspection
            print(f"\n⏸️  Keeping browser open for 15 seconds for manual inspection...")
            await asyncio.sleep(15)
            
        except Exception as e:
            print(f"\n❌ ERROR: {e}\n")
            import traceback
            traceback.print_exc()
        
        finally:
            await browser.close()
    
    print(f"\n{'='*80}")
    print(f"✅ DEEP IFRAME INSPECTION COMPLETE")
    print(f"{'='*80}\n")


async def main():
    """Run deep iframe inspection."""
    
    print("\n" + "="*80)
    print("🔬 DEEP IFRAME CONTENT INSPECTION")
    print("="*80)
    print("\nThis will extract ALL content from the iframe:")
    print("  • HTML structure")
    print("  • Text content")
    print("  • Text boxes / input fields")
    print("  • Videos")
    print("  • Images")
    print("  • Workflow nodes")
    print("  • Explanatory text")
    print("  • Structured data (JSON)")
    print("  • Links")
    print("  • Screenshots")
    print("\n")
    
    await deep_inspect_iframe_content('1954')
    
    print("\nFiles created:")
    print("  • iframe_html_1954.html - Full HTML")
    print("  • iframe_text_1954.txt - All text content")
    print("  • iframe_json_data_1954.json - Structured data")
    print("  • iframe_fullpage_1954.png - Full page screenshot")
    print("  • iframe_only_1954.png - Iframe screenshot")
    print("\n")


if __name__ == "__main__":
    asyncio.run(main())





