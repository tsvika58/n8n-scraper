"""
Test Layer 1 Enhanced V2 on 30 Edge Case Workflows

Covers all edge cases found in the database to ensure robust scraping.
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.scrapers.layer1_enhanced_v2 import Layer1EnhancedV2Extractor
from loguru import logger


# 30 Edge case workflows
EDGE_CASE_WORKFLOWS = [
    # Category 1: NO/MINIMAL description
    ("9268", "No description - YouTube monitor"),
    ("8978", "No description - Generic workflow"),
    ("6033", "No description - Voice expense tracker"),
    
    # Category 2: MASSIVE content
    ("1381", "Maximum content - 75KB original"),
    ("3799", "Huge content - 59KB Google Drive ingestion"),
    
    # Category 3: MANY nodes (complex workflows)
    ("2772", "246 nodes - Notion Todoist sync"),
    ("3683", "244 nodes - AI Petshop assistant"),
    ("3585", "239 nodes - AI Restaurant assistant"),
    
    # Category 4: FEW nodes (1-2 nodes - minimal)
    ("490", "1 node - Pipedrive trigger"),
    ("435", "1 node - DigitalOcean droplet"),
    ("1306", "2 nodes - Static HTML server"),
    
    # Category 5: HAS videos
    ("2462", "1 video - Telegram AI"),
    ("5170", "1 video - JSON tutorial"),
    
    # Category 6: Special characters in title
    ("101", "Special chars - JSON (Binary)"),
    ("1021", "Parentheses in title"),
    ("1041", "Comma in title"),
    
    # Category 7: Different categories
    ("694", "Document Extraction category"),
    ("3725", "AI + WordPress category"),
    ("6250", "AI Chatbot category"),
    
    # Category 8: Varying content structures
    ("418", "Minimal - Blog cross-post"),
    ("4376", "Medium - Invoice extraction"),
    ("9036", "HubSpot automation"),
    ("9245", "Image processing"),
    ("3960", "Financial tracker"),
    
    # Category 9: Different authors
    ("1474", "Different author pattern 1"),
    ("1822", "Different author pattern 2"),
    ("1891", "Different author pattern 3"),
    
    # Category 10: Edge cases from various positions in DB
    ("100", "Very low ID"),
    ("5000", "Mid-range ID"),
    ("9000", "High ID"),
]


async def test_workflow_quick(extractor: Layer1EnhancedV2Extractor, workflow_id: str, description: str):
    """Quick test of a single workflow."""
    
    url = f"https://n8n.io/workflows/{workflow_id}"
    
    try:
        result = await extractor.extract_full_page_content(workflow_id, url)
        
        if result["success"]:
            md = result.get("markdown", "")
            
            # Check for junk
            junk_markers = [
                "there's nothing you can't automate",
                "popular integrations",
                "trending combinations",
                "more templates by",
                "our customer's words",
                "show more integrations",
                "explore more categories",
            ]
            
            has_junk = any(marker in md.lower() for marker in junk_markers)
            junk_status = "❌ HAS JUNK" if has_junk else "✅ CLEAN"
            
            # Check content length
            size_status = "⚠️ HUGE" if len(md) > 30000 else ("⚠️ TINY" if len(md) < 100 else "✅ OK")
            
            print(f"   {workflow_id:<6} | {description[:40]:<42} | {len(md):>6} chars | {size_status} | {junk_status}")
            
            return {
                "workflow_id": workflow_id,
                "success": True,
                "length": len(md),
                "has_junk": has_junk,
                "description": description
            }
        else:
            print(f"   {workflow_id:<6} | {description[:40]:<42} | FAILED: {result.get('errors', [])}")
            return {
                "workflow_id": workflow_id,
                "success": False,
                "error": result.get("errors", []),
                "description": description
            }
            
    except Exception as e:
        print(f"   {workflow_id:<6} | {description[:40]:<42} | EXCEPTION: {str(e)[:30]}")
        return {
            "workflow_id": workflow_id,
            "success": False,
            "error": str(e),
            "description": description
        }


async def main():
    """Test all 30 edge cases."""
    
    print("\n" + "="*100)
    print("🧪 LAYER 1 ENHANCED V2 - 30 EDGE CASE TESTS")
    print("="*100)
    print(f"\n{'ID':<8} | {'Description':<42} | {'Size':>6}      | Size   | Junk")
    print("-" * 100)
    
    results = []
    
    async with Layer1EnhancedV2Extractor(headless=True) as extractor:
        for workflow_id, description in EDGE_CASE_WORKFLOWS:
            result = await test_workflow_quick(extractor, workflow_id, description)
            results.append(result)
            
            # Small delay between requests
            await asyncio.sleep(2)
    
    # Final statistics
    print("\n" + "="*100)
    print("📊 FINAL STATISTICS")
    print("="*100)
    
    total = len(results)
    successful = sum(1 for r in results if r["success"])
    failed = total - successful
    
    clean_workflows = sum(1 for r in results if r.get("success") and not r.get("has_junk"))
    junk_workflows = sum(1 for r in results if r.get("success") and r.get("has_junk"))
    
    print(f"   Total Tested: {total}")
    print(f"   ✅ Successful: {successful} ({successful/total*100:.1f}%)")
    print(f"   ❌ Failed: {failed} ({failed/total*100:.1f}%)")
    print(f"   🧹 Clean (no junk): {clean_workflows} ({clean_workflows/successful*100:.1f}% of successful)")
    print(f"   ⚠️  Has junk: {junk_workflows}")
    
    # List failures
    if failed > 0:
        print(f"\n❌ FAILED WORKFLOWS:")
        for r in results:
            if not r["success"]:
                print(f"   {r['workflow_id']}: {r.get('error', 'Unknown error')}")
    
    # List junk workflows
    if junk_workflows > 0:
        print(f"\n⚠️  WORKFLOWS WITH JUNK CONTENT:")
        for r in results:
            if r.get("success") and r.get("has_junk"):
                print(f"   {r['workflow_id']}: {r['description']}")
    
    # Size distribution
    successful_results = [r for r in results if r["success"]]
    if successful_results:
        sizes = [r["length"] for r in successful_results]
        avg_size = sum(sizes) / len(sizes)
        min_size = min(sizes)
        max_size = max(sizes)
        
        print(f"\n📊 SIZE DISTRIBUTION:")
        print(f"   Average: {avg_size:.0f} chars")
        print(f"   Min: {min_size} chars")
        print(f"   Max: {max_size} chars")
    
    print("="*100)
    
    # Overall verdict
    if clean_workflows == successful and successful >= total * 0.9:
        print("\n🎉 ✅ EXCELLENT! Ready for production deployment!")
    elif clean_workflows >= successful * 0.95:
        print("\n👍 ✅ GOOD! Minor issues but production-ready.")
    else:
        print("\n⚠️  ❌ NEEDS WORK! Too many issues for production.")
    
    print("="*100 + "\n")


if __name__ == "__main__":
    asyncio.run(main())

