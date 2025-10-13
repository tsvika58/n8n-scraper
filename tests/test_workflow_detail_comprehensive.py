#!/usr/bin/env python3
"""
Test comprehensive workflow detail page implementation
"""

import asyncio
from playwright.async_api import async_playwright
import sys

async def test_workflow_detail_page():
    """Test the comprehensive workflow detail page"""
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        try:
            print("🧪 Testing Comprehensive Workflow Detail Page...")
            print("=" * 60)
            
            # Navigate to main database viewer
            print("\n1️⃣ Loading database viewer...")
            await page.goto('http://localhost:5004/', timeout=10000)
            await page.wait_for_load_state('networkidle', timeout=10000)
            print("   ✅ Database viewer loaded")
            
            # Find first workflow link
            print("\n2️⃣ Finding workflow to test...")
            workflow_links = await page.query_selector_all('a[href^="/workflow/"]')
            
            if not workflow_links:
                print("   ❌ No workflow links found")
                await page.screenshot(path='tests/screenshots/no_workflows.png')
                return False
            
            workflow_id = await workflow_links[0].get_attribute('href')
            workflow_id = workflow_id.split('/')[-1]
            print(f"   ✅ Found workflow: {workflow_id}")
            
            # Navigate to workflow detail page
            print(f"\n3️⃣ Loading workflow detail page...")
            await page.goto(f'http://localhost:5004/workflow/{workflow_id}', timeout=10000)
            await page.wait_for_load_state('networkidle', timeout=10000)
            print("   ✅ Workflow detail page loaded")
            
            # Take screenshot
            await page.screenshot(path='tests/screenshots/workflow_detail_full.png', full_page=True)
            print("   📸 Full page screenshot saved")
            
            # Test Section 1: Business Context
            print("\n4️⃣ Testing Business Context section...")
            business_context = await page.query_selector('.business-context')
            if business_context:
                print("   ✅ Business Context section found")
                
                # Check for categories
                categories = await page.query_selector('.context-label:has-text("Categories")')
                if categories:
                    print("   ✅ Categories field present")
                
                # Check for use case
                use_case = await page.query_selector('.context-label:has-text("Use Case")')
                if use_case:
                    print("   ✅ Use Case field present")
                
                # Check for description
                description = await page.query_selector('.description-box')
                if description:
                    print("   ✅ Description box present")
            else:
                print("   ❌ Business Context section not found")
            
            # Test Section 2: Technical Statistics
            print("\n5️⃣ Testing Technical Statistics section...")
            tech_stats = await page.query_selector('.tech-stats')
            if tech_stats:
                print("   ✅ Technical Statistics section found")
                
                # Check for stat cards
                stat_cards = await page.query_selector_all('.stat-card')
                print(f"   ✅ Found {len(stat_cards)} stat cards")
                
                # Check for specific stats
                nodes_stat = await page.query_selector('.stat-label:has-text("Nodes")')
                if nodes_stat:
                    nodes_value = await page.query_selector('.stat-card:has(.stat-label:has-text("Nodes")) .stat-value-large')
                    if nodes_value:
                        value = await nodes_value.inner_text()
                        print(f"   ✅ Nodes: {value}")
                
                connections_stat = await page.query_selector('.stat-label:has-text("Connections")')
                if connections_stat:
                    connections_value = await page.query_selector('.stat-card:has(.stat-label:has-text("Connections")) .stat-value-large')
                    if connections_value:
                        value = await connections_value.inner_text()
                        print(f"   ✅ Connections: {value}")
                
                forks_stat = await page.query_selector('.stat-label:has-text("Forks")')
                if forks_stat:
                    forks_value = await page.query_selector('.stat-card:has(.stat-label:has-text("Forks")) .stat-value-large')
                    if forks_value:
                        value = await forks_value.inner_text()
                        print(f"   ✅ Forks: {value}")
            else:
                print("   ❌ Technical Statistics section not found")
            
            # Test Section 3: Node Types
            print("\n6️⃣ Testing Node Types section...")
            node_types = await page.query_selector('.node-types')
            if node_types:
                print("   ✅ Node Types section found")
                
                # Check for node type items
                node_type_items = await page.query_selector_all('.node-type-item')
                if node_type_items:
                    print(f"   ✅ Found {len(node_type_items)} node types")
                    
                    # Get first few node types
                    for i, item in enumerate(node_type_items[:3]):
                        name = await item.query_selector('.node-type-name')
                        count = await item.query_selector('.node-type-count')
                        if name and count:
                            name_text = await name.inner_text()
                            count_text = await count.inner_text()
                            print(f"   ✅ {name_text}: {count_text}")
                else:
                    print("   ℹ️ No node type data available")
            else:
                print("   ❌ Node Types section not found")
            
            # Test Section 4: Node Details
            print("\n7️⃣ Testing Node Details section...")
            workflow_structure = await page.query_selector('.workflow-structure')
            if workflow_structure:
                print("   ✅ Node Details section found")
                
                # Check for node detail items
                node_items = await page.query_selector_all('.node-detail-item')
                if node_items:
                    print(f"   ✅ Found {len(node_items)} node details")
                    
                    # Get first node detail
                    if node_items:
                        first_node = node_items[0]
                        node_name = await first_node.query_selector('.node-name')
                        node_type = await first_node.query_selector('.node-type-badge')
                        if node_name and node_type:
                            name_text = await node_name.inner_text()
                            type_text = await node_type.inner_text()
                            print(f"   ✅ First node: {name_text} ({type_text})")
                else:
                    print("   ℹ️ No node detail data available")
            else:
                print("   ❌ Node Details section not found")
            
            # Test Section 5: Content & Media
            print("\n8️⃣ Testing Content & Media section...")
            content_media = await page.query_selector('.content-media')
            if content_media:
                print("   ✅ Content & Media section found")
                
                # Check for content cards
                content_cards = await page.query_selector_all('.content-card')
                print(f"   ✅ Found {len(content_cards)} content cards")
            else:
                print("   ❌ Content & Media section not found")
            
            # Test Section 6: Transcription
            print("\n9️⃣ Testing Transcription section...")
            transcript = await page.query_selector('.transcript')
            if transcript:
                print("   ✅ Transcription section found")
                
                # Check for transcript text
                transcript_text = await page.query_selector('.transcript-text')
                if transcript_text:
                    text_content = await transcript_text.inner_text()
                    print(f"   ✅ Transcript text found ({len(text_content)} characters)")
                else:
                    print("   ℹ️ No transcript data available")
            else:
                print("   ❌ Transcription section not found")
            
            # Test Section 7: Documentation
            print("\n🔟 Testing Documentation section...")
            text_content = await page.query_selector('.text-content')
            if text_content:
                print("   ✅ Documentation section found")
                
                # Check for text sections
                text_sections = await page.query_selector_all('.text-section')
                if text_sections:
                    print(f"   ✅ Found {len(text_sections)} documentation sections")
            else:
                print("   ℹ️ No documentation data available")
            
            # Test navigation
            print("\n1️⃣1️⃣ Testing navigation...")
            back_link = await page.query_selector('.back-link')
            if back_link:
                print("   ✅ Back link found")
            else:
                print("   ❌ Back link not found")
            
            # Take final screenshot
            await page.screenshot(path='tests/screenshots/workflow_detail_final.png', full_page=True)
            print("\n📸 Final screenshot saved")
            
            print("\n" + "=" * 60)
            print("✅ COMPREHENSIVE WORKFLOW DETAIL PAGE TEST COMPLETE")
            print("=" * 60)
            
            return True
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
            await page.screenshot(path='tests/screenshots/workflow_detail_error.png')
            return False
        
        finally:
            await browser.close()

if __name__ == "__main__":
    result = asyncio.run(test_workflow_detail_page())
    sys.exit(0 if result else 1)



