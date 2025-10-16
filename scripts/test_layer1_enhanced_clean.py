"""
Test script for Layer 1 Enhanced Clean Scraper

This script tests the new scraper on diverse workflows and compares
the results with existing Layer 1 and Layer 1.5 data.
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.scrapers.layer1_enhanced_clean import Layer1EnhancedCleanScraper
from n8n_shared.database import create_sync_engine, get_sync_session_maker
from n8n_shared.models import Base
from sqlalchemy import text
from loguru import logger
import os


async def get_current_data(workflow_id: str) -> dict:
    """Get current L1 and L1.5 data for comparison."""
    
    engine = create_sync_engine(os.getenv('DATABASE_URL'))
    SessionMaker = get_sync_session_maker(engine)
    
    with SessionMaker() as session:
        query = text("""
            SELECT 
                wm.title,
                wm.description,
                wm.use_case,
                wm.author_name,
                wm.categories,
                LENGTH(wm.description) as desc_len,
                LENGTH(wm.layer1_5_content_markdown) as l15_len,
                ws.node_count,
                wc.video_count,
                wc.has_videos
            FROM workflows w
            LEFT JOIN workflow_metadata wm ON w.workflow_id = wm.workflow_id
            LEFT JOIN workflow_structure ws ON w.workflow_id = ws.workflow_id
            LEFT JOIN workflow_content wc ON w.workflow_id = wc.workflow_id
            WHERE w.workflow_id = :workflow_id
        """)
        
        result = session.execute(query, {'workflow_id': workflow_id})
        row = result.first()
        
        if not row:
            return None
        
        return {
            "title": row[0],
            "description": row[1],
            "use_case": row[2],
            "author_name": row[3],
            "categories": row[4],
            "desc_len": row[5],
            "l15_len": row[6],
            "node_count": row[7],
            "video_count": row[8],
            "has_videos": row[9],
        }


async def test_workflow(scraper: Layer1EnhancedCleanScraper, workflow_id: str, title_hint: str = ""):
    """Test scraper on a single workflow and compare with existing data."""
    
    print(f"\n{'='*100}")
    print(f"🧪 TESTING WORKFLOW {workflow_id}: {title_hint}")
    print(f"{'='*100}\n")
    
    # Get current data
    current = await get_current_data(workflow_id)
    
    if current:
        print(f"📊 CURRENT DATA (Layer 1 + 1.5):")
        print(f"   Title: {current['title']}")
        print(f"   Author: {current['author_name']}")
        print(f"   Categories: {current['categories']}")
        print(f"   L1 Description: {current['desc_len']} chars")
        print(f"   L1.5 Content: {current['l15_len']} chars")
        print(f"   Nodes: {current['node_count']}")
        print(f"   Videos: {current['video_count'] if current['has_videos'] else 0}")
    
    # Extract with new scraper
    url = f"https://n8n.io/workflows/{workflow_id}"
    result = await scraper.extract(workflow_id, url)
    
    if result["success"]:
        print(f"\n✅ NEW SCRAPER RESULTS:")
        print(f"   Title: {result['metadata'].get('title', 'N/A')}")
        print(f"   Author: {result['metadata'].get('author_name', 'N/A')}")
        print(f"   Categories: {result['metadata'].get('categories', [])}")
        print(f"   Brief Description: {len(result['content']['description_brief'])} chars")
        print(f"   Full Content: {len(result['content']['full_content_markdown'])} chars")
        print(f"   Images: {len(result['content']['images'])}")
        print(f"   Videos: {len(result['content']['videos'])}")
        print(f"   Hyperlinks: {len(result['content']['hyperlinks'])}")
        print(f"   Code Snippets: {len(result['content']['code_snippets'])}")
        
        # Show first 500 chars of content
        print(f"\n📄 CONTENT PREVIEW (first 500 chars):")
        print("-" * 80)
        print(result['content']['full_content_markdown'][:500])
        print("-" * 80)
        
        # Show last 200 chars to verify no junk
        print(f"\n📄 CONTENT END (last 200 chars):")
        print("-" * 80)
        print(result['content']['full_content_markdown'][-200:])
        print("-" * 80)
        
        # Comparison
        if current:
            print(f"\n📊 COMPARISON:")
            print(f"   Content size: {current['l15_len']} → {len(result['content']['full_content_markdown'])} chars")
            reduction = current['l15_len'] - len(result['content']['full_content_markdown'])
            print(f"   Reduction: {reduction} chars ({reduction/current['l15_len']*100:.1f}% smaller)")
            
            # Check for junk in content
            junk_markers = ["cookie", "privacy policy", "there's nothing", "popular integrations"]
            has_junk = any(marker in result['content']['full_content_markdown'].lower() for marker in junk_markers)
            print(f"   Contains junk: {'❌ YES - PROBLEM!' if has_junk else '✅ NO - CLEAN!'}")
        
        return True
    else:
        print(f"\n❌ EXTRACTION FAILED:")
        print(f"   Errors: {result['errors']}")
        return False


async def main():
    """Run comprehensive tests."""
    
    print("\n" + "="*100)
    print("🚀 LAYER 1 ENHANCED CLEAN SCRAPER - COMPREHENSIVE TEST")
    print("="*100)
    
    test_cases = [
        # Format: (workflow_id, description)
        ("694", "Medium content - Google Sheets workflow"),
        ("1381", "MOST content - 75KB of L1.5 data"),
        ("418", "MINIMAL content - Only 4KB"),
        ("2462", "Has VIDEO - Telegram AI Assistant"),
        ("5170", "Has VIDEO - Learn JSON tutorial"),
        ("3725", "COMPLEX - 159 nodes WordPress automation"),
        ("1306", "SIMPLE - 2 nodes static HTML"),
        ("6250", "AI Chatbot - 26 nodes"),
    ]
    
    async with Layer1EnhancedCleanScraper(headless=True) as scraper:
        successful = 0
        failed = 0
        
        for workflow_id, description in test_cases:
            try:
                success = await test_workflow(scraper, workflow_id, description)
                if success:
                    successful += 1
                else:
                    failed += 1
                
                # Delay between tests
                await asyncio.sleep(3)
                
            except Exception as e:
                logger.error(f"Test failed for workflow {workflow_id}: {e}")
                failed += 1
        
        # Summary
        print(f"\n\n{'='*100}")
        print(f"📊 TEST SUMMARY")
        print(f"{'='*100}")
        print(f"   Total Tests: {len(test_cases)}")
        print(f"   ✅ Successful: {successful}")
        print(f"   ❌ Failed: {failed}")
        print(f"   Success Rate: {successful/len(test_cases)*100:.1f}%")
        print(f"{'='*100}\n")


if __name__ == "__main__":
    asyncio.run(main())

