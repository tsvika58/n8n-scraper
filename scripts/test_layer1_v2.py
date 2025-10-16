"""
Test Layer 1 Enhanced V2 Scraper

Tests the new clean scraper on diverse workflows and compares with existing data.
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.scrapers.layer1_enhanced_v2 import Layer1EnhancedV2Extractor
from loguru import logger


async def test_single_workflow(workflow_id: str, title_hint: str = ""):
    """Test scraper on a single workflow."""
    
    print(f"\n{'='*100}")
    print(f"🧪 TESTING WORKFLOW {workflow_id}: {title_hint}")
    print(f"{'='*100}\n")
    
    url = f"https://n8n.io/workflows/{workflow_id}"
    
    async with Layer1EnhancedV2Extractor(headless=True) as extractor:
        result = await extractor.extract_full_page_content(workflow_id, url)
        
        if result["success"]:
            markdown = result.get("markdown", "")
            
            print("✅ EXTRACTION SUCCESSFUL")
            print(f"   Extraction time: {result['extraction_time']:.2f}s")
            print(f"   Markdown length: {len(markdown)} chars")
            
            # Check for junk content
            junk_markers = [
                "There's nothing you can't automate",
                "Popular integrations",
                "Trending combinations",
                "cookie",
                "privacy policy",
            ]
            
            has_junk = any(marker.lower() in markdown.lower() for marker in junk_markers)
            
            print(f"   Contains junk: {'❌ YES (PROBLEM!)' if has_junk else '✅ NO (CLEAN!)'}")
            
            # Show content preview
            print(f"\n📄 FIRST 800 CHARACTERS:")
            print("-" * 80)
            print(markdown[:800])
            print("-" * 80)
            
            print(f"\n📄 LAST 500 CHARACTERS:")
            print("-" * 80)
            print(markdown[-500:])
            print("-" * 80)
            
            # Extract metadata for comparison
            metadata = result.get("metadata", {})
            print(f"\n📊 METADATA:")
            print(f"   Page title: {metadata.get('page_title', 'N/A')}")
            print(f"   Content sections: {metadata.get('content_section_count', 0)}")
            print(f"   Total characters: {metadata.get('total_characters', 0)}")
            
            return True
        else:
            print(f"❌ EXTRACTION FAILED")
            print(f"   Errors: {result['errors']}")
            return False


async def main():
    """Run comprehensive test suite."""
    
    print("\n" + "="*100)
    print("🚀 LAYER 1 ENHANCED V2 - COMPREHENSIVE TEST SUITE")
    print("="*100)
    
    # Test cases: diverse workflows
    test_cases = [
        ("694", "Medium content - Google Sheets transformations"),
        ("1381", "Maximum content - 75KB L1.5 data"),
        ("418", "Minimal content - Simple cross-posting"),
        ("2462", "Has video - Telegram AI Assistant"),
        ("3725", "Complex - 159 nodes WordPress automation"),
    ]
    
    results = []
    
    for workflow_id, description in test_cases:
        try:
            success = await test_single_workflow(workflow_id, description)
            results.append((workflow_id, success))
            
            # Delay between tests to be polite
            print("\n⏱️  Waiting 3 seconds before next test...")
            await asyncio.sleep(3)
            
        except Exception as e:
            logger.error(f"Test failed for workflow {workflow_id}: {e}")
            results.append((workflow_id, False))
    
    # Summary
    print(f"\n\n{'='*100}")
    print(f"📊 TEST SUMMARY")
    print(f"{'='*100}")
    
    successful = sum(1 for _, success in results if success)
    total = len(results)
    
    for workflow_id, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"   {status} - Workflow {workflow_id}")
    
    print(f"\n   Success Rate: {successful}/{total} ({successful/total*100:.1f}%)")
    print(f"{'='*100}\n")
    
    return successful == total


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)

