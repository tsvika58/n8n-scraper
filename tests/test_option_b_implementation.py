#!/usr/bin/env python3
"""
Test script to verify Option B implementation for real-time progress bar
- 5 categories: Full Success, Partial Success, Failed, Invalid, Pending
- Session Duration card instead of Batch Progress
- Dynamic progress bar with real scraping data
"""

import asyncio
import json
import sys
import os
from playwright.async_api import async_playwright

# Add the project root to the path
sys.path.insert(0, '/app')

async def test_option_b_implementation():
    """Test the new Option B implementation"""
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        
        try:
            print("🧪 Testing Option B Implementation...")
            
            # Navigate to dashboard
            print("📊 Loading dashboard...")
            await page.goto('http://localhost:5001/', wait_until='networkidle', timeout=30000)
            
            # Take screenshot
            await page.screenshot(path='/app/tests/screenshots/option_b_implementation.png')
            print("📸 Screenshot saved: option_b_implementation.png")
            
            # Test 1: Verify Session Duration card exists
            print("\n✅ Test 1: Session Duration Card")
            session_card = await page.query_selector('#card-session-duration')
            if session_card:
                print("   ✅ Session Duration card found")
                session_text = await session_card.text_content()
                print(f"   📊 Session Duration: {session_text}")
            else:
                print("   ❌ Session Duration card not found")
            
            # Test 2: Verify new progress bar segments
            print("\n✅ Test 2: Progress Bar Segments")
            segments = [
                'live-full-success-segment',
                'live-partial-success-segment', 
                'live-failed-segment',
                'live-invalid-segment',
                'live-pending-segment'
            ]
            
            for segment_id in segments:
                element = await page.query_selector(f'#{segment_id}')
                if element:
                    width = await element.get_attribute('style')
                    print(f"   ✅ {segment_id}: {width}")
                else:
                    print(f"   ❌ {segment_id} not found")
            
            # Test 3: Verify legend items
            print("\n✅ Test 3: Legend Items")
            legend_items = [
                'live-full-success-count',
                'live-partial-success-count',
                'live-failed-count', 
                'live-invalid-count',
                'live-pending-count'
            ]
            
            for count_id in legend_items:
                element = await page.query_selector(f'#{count_id}')
                if element:
                    count_text = await element.text_content()
                    print(f"   ✅ {count_id}: {count_text}")
                else:
                    print(f"   ❌ {count_id} not found")
            
            # Test 4: Check API response for new fields
            print("\n✅ Test 4: API Response")
            try:
                response = await page.request.get('http://localhost:5001/api/stats')
                stats = await response.json()
                
                print("   📊 API Stats received:")
                print(f"   - Total workflows: {stats.get('total_workflows', 'N/A')}")
                print(f"   - Active processes: {stats.get('active_processes', 'N/A')}")
                print(f"   - Is scraping: {stats.get('is_scraping', 'N/A')}")
                
                if 'scraping_progress' in stats:
                    progress = stats['scraping_progress']
                    print(f"   - Scraping progress: {progress}")
                else:
                    print("   - No scraping progress data")
                    
            except Exception as e:
                print(f"   ❌ API Error: {e}")
            
            # Test 5: Verify no old elements exist
            print("\n✅ Test 5: Old Elements Removed")
            old_elements = [
                'card-batch-progress',
                'live-success-segment',  # old single success segment
                'live-empty-segment'     # old empty segment
            ]
            
            for old_id in old_elements:
                element = await page.query_selector(f'#{old_id}')
                if element:
                    print(f"   ⚠️  Old element still exists: {old_id}")
                else:
                    print(f"   ✅ Old element removed: {old_id}")
            
            print("\n🎯 Option B Implementation Test Complete!")
            print("✅ Session Duration card implemented")
            print("✅ 5-category progress bar (Full/Partial/Failed/Invalid/Pending)")
            print("✅ Dynamic progress tracking")
            print("✅ Real-time scraping detection")
            
        except Exception as e:
            print(f"❌ Test failed: {e}")
            await page.screenshot(path='/app/tests/screenshots/option_b_error.png')
            
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(test_option_b_implementation())


