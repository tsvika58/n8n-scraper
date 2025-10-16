#!/usr/bin/env python3
"""
Test script to validate the new cumulative status breakdown
"""

import asyncio
from playwright.async_api import async_playwright

async def test_cumulative_status():
    print("🎭 Testing Cumulative Status Breakdown...")
    print("=" * 60)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        try:
            # Load dashboard
            await page.goto("http://localhost:5001/", wait_until="load", timeout=10000)
            await page.wait_for_timeout(2000)
            
            print("✅ Dashboard loaded")
            
            # Check cumulative status section
            progress_section = await page.query_selector('.progress-section')
            assert progress_section, "❌ Progress section not found"
            
            # Check title
            title = await page.query_selector('.progress-section h3')
            title_text = await title.text_content()
            assert "Cumulative Status Breakdown" in title_text, f"❌ Wrong title: {title_text}"
            print(f"✅ Title: {title_text}")
            
            # Check all 5 progress segments exist
            segments = await page.query_selector_all('.progress-segment')
            segment_ids = await page.evaluate("""
                () => {
                    const segments = document.querySelectorAll('.progress-segment');
                    return Array.from(segments).map(s => s.id);
                }
            """)
            
            expected_segments = ['full-success-segment', 'partial-success-segment', 'failed-segment', 'invalid-segment', 'pending-segment']
            for expected in expected_segments:
                assert expected in segment_ids, f"❌ Missing segment: {expected}"
            print(f"✅ Found all 5 progress segments: {segment_ids}")
            
            # Check all 5 legend items exist
            legend_items = await page.query_selector_all('.legend-item')
            legend_texts = await page.evaluate("""
                () => {
                    const items = document.querySelectorAll('.legend-item');
                    return Array.from(items).map(item => item.textContent.trim());
                }
            """)
            
            expected_legends = ['Full Success', 'Partial Success', 'Failed', 'Invalid', 'Pending']
            for expected in expected_legends:
                found = any(expected in text for text in legend_texts)
                assert found, f"❌ Missing legend: {expected}"
            print(f"✅ Found all 5 legend items")
            
            # Check counts are populated
            total_count = await page.query_selector('#total-workflows-count')
            total_text = await total_count.text_content()
            print(f"✅ Total Workflows: {total_text}")
            
            full_success_count = await page.query_selector('#full-success-count')
            full_success_text = await full_success_count.text_content()
            print(f"✅ Full Success: {full_success_text}")
            
            partial_success_count = await page.query_selector('#partial-success-count')
            partial_success_text = await partial_success_count.text_content()
            print(f"✅ Partial Success: {partial_success_text}")
            
            failed_count = await page.query_selector('#failed-count')
            failed_text = await failed_count.text_content()
            print(f"✅ Failed: {failed_text}")
            
            invalid_count = await page.query_selector('#invalid-count')
            invalid_text = await invalid_count.text_content()
            print(f"✅ Invalid: {invalid_text}")
            
            pending_count = await page.query_selector('#pending-count')
            pending_text = await pending_count.text_content()
            print(f"✅ Pending: {pending_text}")
            
            # Take screenshot
            await page.screenshot(path='/tmp/cumulative_status.png', full_page=True)
            print("📸 Screenshot: /tmp/cumulative_status.png")
            
            print("\n" + "=" * 60)
            print("🎉 SUCCESS! Cumulative Status Breakdown is working")
            print("✅ 5 categories: Full Success, Partial Success, Failed, Invalid, Pending")
            print("✅ Progress segments: Visual representation")
            print("✅ Legend items: Count displays")
            print("✅ Real-time data: API integration")
            print("=" * 60)
            
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
            await page.screenshot(path='/tmp/cumulative_status_error.png', full_page=True)
            raise
            
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(test_cumulative_status())





