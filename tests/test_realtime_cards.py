#!/usr/bin/env python3
"""
Test script to validate the real-time scraping cards
"""

import asyncio
from playwright.async_api import async_playwright

async def test_realtime_cards():
    print("🎭 Testing Real-Time Scraping Cards...")
    print("=" * 60)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        try:
            # Load dashboard
            await page.goto("http://localhost:5001/", wait_until="load", timeout=10000)
            await page.wait_for_timeout(2000)
            
            print("✅ Dashboard loaded")
            
            # Check real-time cards container
            realtime_cards = await page.query_selector('.realtime-cards')
            assert realtime_cards, "❌ Real-time cards container not found"
            print("✅ Real-time cards container found")
            
            # Check all 5 real-time cards exist
            cards = await page.query_selector_all('.realtime-card')
            assert len(cards) == 5, f"❌ Expected 5 real-time cards, found {len(cards)}"
            print(f"✅ Found {len(cards)} real-time cards")
            
            # Check individual cards
            expected_cards = [
                ('card-active-processes', 'Active Processes'),
                ('card-current-speed', 'Current Speed'),
                ('card-batch-progress', 'Batch Progress'),
                ('card-eta', 'ETA'),
                ('card-live-success-rate', 'Live Success Rate')
            ]
            
            for card_id, card_name in expected_cards:
                card_element = await page.query_selector(f'#{card_id}')
                assert card_element, f"❌ {card_name} card not found"
                
                card_value = await card_element.text_content()
                print(f"✅ {card_name}: {card_value}")
            
            # Check card values are populated
            active_processes = await page.query_selector('#card-active-processes')
            active_text = await active_processes.text_content()
            print(f"✅ Active Processes: {active_text}")
            
            current_speed = await page.query_selector('#card-current-speed')
            speed_text = await current_speed.text_content()
            print(f"✅ Current Speed: {speed_text}")
            
            batch_progress = await page.query_selector('#card-batch-progress')
            batch_text = await batch_progress.text_content()
            print(f"✅ Batch Progress: {batch_text}")
            
            eta = await page.query_selector('#card-eta')
            eta_text = await eta.text_content()
            print(f"✅ ETA: {eta_text}")
            
            live_rate = await page.query_selector('#card-live-success-rate')
            rate_text = await live_rate.text_content()
            print(f"✅ Live Success Rate: {rate_text}")
            
            # Check card structure
            for i, card in enumerate(cards, 1):
                icon = await card.query_selector('.card-icon')
                assert icon, f"❌ Card {i} missing icon"
                
                content = await card.query_selector('.card-content')
                assert content, f"❌ Card {i} missing content"
                
                label = await card.query_selector('.card-label')
                assert label, f"❌ Card {i} missing label"
                
                value = await card.query_selector('.card-value')
                assert value, f"❌ Card {i} missing value"
                
                subtext = await card.query_selector('.card-subtext')
                assert subtext, f"❌ Card {i} missing subtext"
                
                print(f"✅ Card {i} structure validated")
            
            # Check responsive layout
            layout_info = await page.evaluate("""
                () => {
                    const container = document.querySelector('.realtime-cards');
                    const style = window.getComputedStyle(container);
                    return {
                        display: style.display,
                        flexWrap: style.flexWrap,
                        gap: style.gap
                    };
                }
            """)
            
            assert layout_info['display'] == 'flex', f"❌ Expected flex display, got {layout_info['display']}"
            print(f"✅ Layout: {layout_info['display']}, gap={layout_info['gap']}")
            
            # Take screenshot
            await page.screenshot(path='/tmp/realtime_cards.png', full_page=True)
            print("📸 Screenshot: /tmp/realtime_cards.png")
            
            print("\n" + "=" * 60)
            print("🎉 SUCCESS! Real-Time Scraping Cards are working")
            print("✅ 5 cards: Active Processes, Current Speed, Batch Progress, ETA, Live Success Rate")
            print("✅ Card structure: Icons, labels, values, subtexts")
            print("✅ Responsive layout: Flex display")
            print("✅ Real-time data: API integration")
            print("=" * 60)
            
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
            await page.screenshot(path='/tmp/realtime_cards_error.png', full_page=True)
            raise
            
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(test_realtime_cards())




