#!/usr/bin/env python3
"""
Test script to validate separated status bars in realtime dashboard
- Scraping Status Bar (IDLE/SCRAPING status)
- Infrastructure Monitoring Bar (DB, CPU, Memory, Uptime)
"""

import asyncio
from playwright.async_api import async_playwright
import json

async def test_separated_status_bars():
    print("🎭 Testing Separated Status Bars...")
    print("=" * 80)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # Enable console logging
        page.on("console", lambda msg: print(f"🌐 Browser Console [{msg.type}]: {msg.text}"))
        
        try:
            print("\n📍 Step 1: Load realtime dashboard")
            print("-" * 80)
            
            # Load the dashboard with a shorter timeout
            await page.goto("http://localhost:5001/", wait_until="domcontentloaded", timeout=15000)
            await page.wait_for_timeout(3000)  # Wait for initial load
            
            print("✅ Dashboard loaded successfully")
            
            print("\n📍 Step 2: Check Scraping Status Bar")
            print("-" * 80)
            
            # Check scraping status bar exists
            scraping_status_bar = await page.query_selector('.scraping-status-bar')
            assert scraping_status_bar, "❌ Scraping status bar not found"
            print("✅ Scraping status bar found")
            
            # Check status indicator
            status_indicator = await page.query_selector('#global-status-indicator')
            assert status_indicator, "❌ Global status indicator not found"
            print("✅ Global status indicator found")
            
            # Check status text
            status_text = await page.query_selector('.status-text')
            status_text_content = await status_text.text_content()
            print(f"✅ Status text: '{status_text_content}'")
            
            # Check status message
            status_message = await page.query_selector('#global-status-message')
            assert status_message, "❌ Global status message not found"
            print("✅ Global status message found")
            
            print("\n📍 Step 3: Check Infrastructure Monitoring Bar")
            print("-" * 80)
            
            # Check infrastructure bar exists
            infra_bar = await page.query_selector('.infrastructure-bar')
            assert infra_bar, "❌ Infrastructure bar not found"
            print("✅ Infrastructure monitoring bar found")
            
            # Check infra title
            infra_title = await page.query_selector('.infra-title')
            infra_title_text = await infra_title.text_content()
            assert "Infrastructure Status" in infra_title_text, f"❌ Wrong infra title: {infra_title_text}"
            print(f"✅ Infrastructure title: '{infra_title_text}'")
            
            # Check monitoring grid
            monitoring_grid = await page.query_selector('.monitoring-grid')
            assert monitoring_grid, "❌ Monitoring grid not found"
            print("✅ Monitoring grid found")
            
            # Check individual monitor items
            monitor_items = await page.query_selector_all('.monitor-item')
            assert len(monitor_items) == 4, f"❌ Expected 4 monitor items, found {len(monitor_items)}"
            print(f"✅ Found {len(monitor_items)} monitor items")
            
            # Check specific monitor items
            expected_monitors = ['Database', 'CPU', 'Memory', 'Uptime']
            for i, expected in enumerate(expected_monitors):
                monitor_item = monitor_items[i]
                monitor_label = await monitor_item.query_selector('.monitor-label')
                label_text = await monitor_label.text_content()
                assert expected in label_text, f"❌ Monitor {i} expected '{expected}', got '{label_text}'"
                print(f"✅ Monitor {i}: {label_text}")
            
            print("\n📍 Step 4: Check API Response")
            print("-" * 80)
            
            # Test API endpoint
            api_response = await page.evaluate("""
                async () => {
                    const response = await fetch('/api/stats');
                    return await response.json();
                }
            """)
            
            print("✅ API response received")
            
            # Check infrastructure metrics are present
            infra_metrics = ['db_status', 'cpu_usage', 'memory_usage', 'uptime']
            for metric in infra_metrics:
                assert metric in api_response, f"❌ Missing infrastructure metric: {metric}"
                print(f"✅ {metric}: {api_response[metric]}")
            
            print("\n📍 Step 5: Validate Separation")
            print("-" * 80)
            
            # Ensure IDLE status is in scraping bar, not infrastructure bar
            scraping_status = await page.evaluate("""
                () => {
                    const scrapingBar = document.querySelector('.scraping-status-bar');
                    const infraBar = document.querySelector('.infrastructure-bar');
                    const statusText = document.querySelector('.status-text');
                    
                    return {
                        scrapingBarExists: !!scrapingBar,
                        infraBarExists: !!infraBar,
                        statusTextInScrapingBar: scrapingBar && scrapingBar.contains(statusText),
                        statusTextInInfraBar: infraBar && infraBar.contains(statusText)
                    };
                }
            """)
            
            assert scraping_status['scrapingBarExists'], "❌ Scraping bar missing"
            assert scraping_status['infraBarExists'], "❌ Infrastructure bar missing"
            assert scraping_status['statusTextInScrapingBar'], "❌ Status text not in scraping bar"
            assert not scraping_status['statusTextInInfraBar'], "❌ Status text incorrectly in infrastructure bar"
            
            print("✅ Status text correctly in scraping bar")
            print("✅ Status text NOT in infrastructure bar")
            print("✅ Proper separation confirmed")
            
            print("\n📍 Step 6: Take Screenshot")
            print("-" * 80)
            
            await page.screenshot(path='/tmp/separated_status_bars.png', full_page=True)
            print("📸 Screenshot saved: /tmp/separated_status_bars.png")
            
            print("\n" + "=" * 80)
            print("🎉 ALL TESTS PASSED!")
            print("✅ Scraping Status Bar: Working")
            print("✅ Infrastructure Monitoring Bar: Working") 
            print("✅ Proper Separation: Confirmed")
            print("✅ API Integration: Working")
            print("=" * 80)
            
        except Exception as e:
            print(f"\n❌ ERROR: {str(e)}")
            await page.screenshot(path='/tmp/separated_status_bars_error.png', full_page=True)
            print("📸 Error screenshot: /tmp/separated_status_bars_error.png")
            raise
            
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(test_separated_status_bars())





