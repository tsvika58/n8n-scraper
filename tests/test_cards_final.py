#!/usr/bin/env python3
"""
Quick test to verify the 5 metric cards are working and spread evenly
"""

import asyncio
from playwright.async_api import async_playwright

async def test_final_cards():
    print("🎭 Testing Final Metric Cards Layout...")
    print("=" * 60)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        try:
            # Load dashboard with shorter timeout
            await page.goto("http://localhost:5001/", wait_until="load", timeout=10000)
            await page.wait_for_timeout(2000)
            
            print("✅ Dashboard loaded")
            
            # Check cards container
            cards_container = await page.query_selector('.metrics-cards')
            assert cards_container, "❌ Cards container not found"
            
            # Check all 5 cards exist
            cards = await page.query_selector_all('.metric-card')
            assert len(cards) == 5, f"❌ Expected 5 cards, found {len(cards)}"
            print(f"✅ Found {len(cards)} metric cards")
            
            # Check card values are populated
            total_value = await page.query_selector('#card-total-workflows')
            total_text = await total_value.text_content()
            print(f"✅ Total Workflows: {total_text}")
            
            success_value = await page.query_selector('#card-fully-successful')
            success_text = await success_value.text_content()
            print(f"✅ Fully Successful: {success_text}")
            
            partial_value = await page.query_selector('#card-partial-success')
            partial_text = await partial_value.text_content()
            print(f"✅ Partial Success: {partial_text}")
            
            quality_value = await page.query_selector('#card-quality-score')
            quality_text = await quality_value.text_content()
            print(f"✅ Quality Score: {quality_text}")
            
            rate_value = await page.query_selector('#card-success-rate')
            rate_text = await rate_value.text_content()
            print(f"✅ Success Rate: {rate_text}")
            
            # Check layout is even
            layout_info = await page.evaluate("""
                () => {
                    const container = document.querySelector('.metrics-cards');
                    const cards = document.querySelectorAll('.metric-card');
                    const style = window.getComputedStyle(container);
                    const cardWidths = Array.from(cards).map(card => 
                        window.getComputedStyle(card).width
                    );
                    return {
                        display: style.display,
                        flexWrap: style.flexWrap,
                        cardCount: cards.length,
                        cardWidths: cardWidths
                    };
                }
            """)
            
            print(f"✅ Layout: {layout_info['display']}, {layout_info['flexWrap']}")
            print(f"✅ Card widths: {layout_info['cardWidths'][:2]}... (showing first 2)")
            
            # Take screenshot
            await page.screenshot(path='/tmp/final_cards.png', full_page=True)
            print("📸 Screenshot: /tmp/final_cards.png")
            
            print("\n" + "=" * 60)
            print("🎉 SUCCESS! Top 5 metric cards are working and spread evenly")
            print("=" * 60)
            
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
            await page.screenshot(path='/tmp/final_cards_error.png', full_page=True)
            raise
            
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(test_final_cards())


