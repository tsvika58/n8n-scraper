#!/usr/bin/env python3
"""
Test Layer 1.5 on 10 workflows and compare with existing Layer 1 data

This script will:
1. Test Layer 1.5 on 10 different workflows
2. Compare with existing Layer 1 data
3. Analyze overlaps and differences
4. Provide recommendations for scraping architecture
"""

import asyncio
import sys
import json
sys.path.append('/app')

from src.scrapers.layer1_5_page_content import Layer1_5PageContentExtractor
from src.storage.database import get_session
from sqlalchemy import text
from loguru import logger
import time


async def test_layer1_5_on_10_workflows():
    """Test Layer 1.5 on 10 different workflows"""
    
    print("🧪 TESTING LAYER 1.5 ON 10 WORKFLOWS")
    print("=" * 70)
    
    # Get 10 random workflows that have Layer 1 data
    with get_session() as session:
        result = session.execute(text("""
            SELECT w.workflow_id, w.url, wm.title, wm.description
            FROM workflows w
            LEFT JOIN workflow_metadata wm ON w.workflow_id = wm.workflow_id
            WHERE w.layer1_success = true
            AND wm.title IS NOT NULL
            ORDER BY RANDOM()
            LIMIT 10
        """))
        
        workflows = result.fetchall()
        
        if not workflows:
            print("❌ No workflows with Layer 1 data found")
            return
    
    print(f"📋 Selected {len(workflows)} workflows for testing:")
    for i, (wf_id, url, title, desc) in enumerate(workflows, 1):
        title_preview = (title[:50] + "...") if title and len(title) > 50 else title
        print(f"   {i}. {wf_id}: {title_preview}")
    print()
    
    # Test Layer 1.5 on each workflow
    results = []
    
    async with Layer1_5PageContentExtractor() as extractor:
        for i, (workflow_id, url, l1_title, l1_description) in enumerate(workflows, 1):
            print(f"🔍 Testing workflow {i}/10: {workflow_id}")
            print("-" * 50)
            
            # Extract with Layer 1.5
            start_time = time.time()
            result = await extractor.extract_full_page_content(workflow_id, url)
            extraction_time = time.time() - start_time
            
            if result["success"]:
                data = result["data"]
                
                # Analyze the data
                analysis = analyze_workflow_data(
                    workflow_id, 
                    l1_title, 
                    l1_description, 
                    data,
                    extraction_time
                )
                
                results.append(analysis)
                
                print(f"✅ Success: {len(data['all_text_content'])} chars extracted")
                print(f"   L1 description: {len(l1_description or '')} chars")
                print(f"   L1.5 description: {len(data['main_description'])} chars")
                print(f"   L1.5 total content: {len(data['all_text_content'])} chars")
                print(f"   Extraction time: {extraction_time:.2f}s")
                
            else:
                print(f"❌ Failed: {result['errors']}")
                results.append({
                    "workflow_id": workflow_id,
                    "success": False,
                    "errors": result["errors"]
                })
            
            print()
    
    # Generate comprehensive analysis
    generate_comprehensive_analysis(results)
    
    return results


def analyze_workflow_data(workflow_id, l1_title, l1_description, l1_5_data, extraction_time):
    """Analyze data from Layer 1 vs Layer 1.5"""
    
    l1_desc_len = len(l1_description or "")
    l1_5_desc_len = len(l1_5_data.get("main_description", ""))
    l1_5_total_len = len(l1_5_data.get("all_text_content", ""))
    
    # Check for content overlap
    overlap_analysis = {}
    if l1_description and l1_5_data.get("main_description"):
        # Simple overlap check
        l1_desc_clean = l1_description.lower().strip()
        l1_5_desc_clean = l1_5_data["main_description"].lower().strip()
        
        if l1_desc_clean in l1_5_desc_clean:
            overlap_analysis["l1_in_l1_5"] = True
            overlap_analysis["overlap_type"] = "L1 description contained in L1.5"
        elif l1_5_desc_clean in l1_desc_clean:
            overlap_analysis["l1_in_l1_5"] = True
            overlap_analysis["overlap_type"] = "L1.5 description contained in L1"
        else:
            # Check for partial overlap (first 100 chars)
            l1_start = l1_desc_clean[:100]
            l1_5_start = l1_5_desc_clean[:100]
            if l1_start == l1_5_start:
                overlap_analysis["partial_overlap"] = True
                overlap_analysis["overlap_type"] = "Partial overlap (first 100 chars)"
            else:
                overlap_analysis["no_overlap"] = True
                overlap_analysis["overlap_type"] = "No significant overlap"
    
    return {
        "workflow_id": workflow_id,
        "success": True,
        "extraction_time": extraction_time,
        "l1_data": {
            "title": l1_title,
            "description_length": l1_desc_len,
            "description_preview": (l1_description[:100] + "...") if l1_description and len(l1_description) > 100 else l1_description
        },
        "l1_5_data": {
            "main_description_length": l1_5_desc_len,
            "total_content_length": l1_5_total_len,
            "examples_count": len(l1_5_data.get("examples", [])),
            "has_how_it_works": bool(l1_5_data.get("how_it_works")),
            "has_setup_instructions": bool(l1_5_data.get("setup_instructions")),
            "page_title": l1_5_data.get("page_title"),
            "author": l1_5_data.get("author"),
            "description_preview": (l1_5_data.get("main_description", "")[:100] + "...") if len(l1_5_data.get("main_description", "")) > 100 else l1_5_data.get("main_description", "")
        },
        "overlap_analysis": overlap_analysis,
        "content_ratio": l1_5_total_len / max(l1_desc_len, 1),  # How much more content L1.5 has
        "description_ratio": l1_5_desc_len / max(l1_desc_len, 1)  # Description comparison
    }


def generate_comprehensive_analysis(results):
    """Generate comprehensive analysis of all results"""
    
    print("📊 COMPREHENSIVE ANALYSIS")
    print("=" * 70)
    
    successful_results = [r for r in results if r.get("success")]
    failed_results = [r for r in results if not r.get("success")]
    
    print(f"✅ Successful extractions: {len(successful_results)}/10")
    print(f"❌ Failed extractions: {len(failed_results)}/10")
    
    if not successful_results:
        print("❌ No successful extractions to analyze")
        return
    
    print()
    print("🔍 CONTENT ANALYSIS:")
    print("-" * 50)
    
    # Content statistics
    total_content_lengths = [r["l1_5_data"]["total_content_length"] for r in successful_results]
    desc_lengths_l1 = [r["l1_data"]["description_length"] for r in successful_results]
    desc_lengths_l1_5 = [r["l1_5_data"]["main_description_length"] for r in successful_results]
    content_ratios = [r["content_ratio"] for r in successful_results]
    extraction_times = [r["extraction_time"] for r in successful_results]
    
    print(f"📈 Layer 1.5 Total Content:")
    print(f"   Average: {sum(total_content_lengths) / len(total_content_lengths):,.0f} characters")
    print(f"   Min: {min(total_content_lengths):,} characters")
    print(f"   Max: {max(total_content_lengths):,} characters")
    
    print(f"📈 Layer 1 vs Layer 1.5 Description Lengths:")
    print(f"   L1 Average: {sum(desc_lengths_l1) / len(desc_lengths_l1):,.0f} characters")
    print(f"   L1.5 Average: {sum(desc_lengths_l1_5) / len(desc_lengths_l1_5):,.0f} characters")
    
    print(f"📈 Content Improvement Ratio:")
    print(f"   Average: {sum(content_ratios) / len(content_ratios):.1f}x more content")
    print(f"   Min: {min(content_ratios):.1f}x")
    print(f"   Max: {max(content_ratios):.1f}x")
    
    print(f"⏱️ Extraction Performance:")
    print(f"   Average time: {sum(extraction_times) / len(extraction_times):.2f}s")
    print(f"   Min time: {min(extraction_times):.2f}s")
    print(f"   Max time: {max(extraction_times):.2f}s")
    
    print()
    print("🔄 OVERLAP ANALYSIS:")
    print("-" * 50)
    
    # Overlap statistics
    overlap_types = {}
    for result in successful_results:
        overlap_type = result["overlap_analysis"].get("overlap_type", "Unknown")
        overlap_types[overlap_type] = overlap_types.get(overlap_type, 0) + 1
    
    for overlap_type, count in overlap_types.items():
        print(f"   {overlap_type}: {count} workflows")
    
    print()
    print("📋 DETAILED WORKFLOW COMPARISON:")
    print("-" * 50)
    
    for i, result in enumerate(successful_results, 1):
        wf_id = result["workflow_id"]
        l1_desc_len = result["l1_data"]["description_length"]
        l1_5_desc_len = result["l1_5_data"]["main_description_length"]
        l1_5_total_len = result["l1_5_data"]["total_content_length"]
        ratio = result["content_ratio"]
        overlap = result["overlap_analysis"].get("overlap_type", "Unknown")
        
        print(f"   {i}. Workflow {wf_id}:")
        print(f"      L1 description: {l1_desc_len} chars")
        print(f"      L1.5 description: {l1_5_desc_len} chars")
        print(f"      L1.5 total: {l1_5_total_len:,} chars ({ratio:.1f}x improvement)")
        print(f"      Overlap: {overlap}")
        print(f"      Examples: {result['l1_5_data']['examples_count']}")
        print(f"      Author: {result['l1_5_data']['author'] or 'Not found'}")
        print()
    
    # Generate recommendations
    generate_recommendations(successful_results)


def generate_recommendations(results):
    """Generate architecture recommendations based on analysis"""
    
    print("💡 ARCHITECTURE RECOMMENDATIONS")
    print("=" * 70)
    
    avg_content_ratio = sum(r["content_ratio"] for r in results) / len(results)
    avg_extraction_time = sum(r["extraction_time"] for r in results) / len(results)
    
    # Analyze overlap patterns
    has_overlap = sum(1 for r in results if not r["overlap_analysis"].get("no_overlap")) / len(results)
    
    print("🎯 FINDINGS:")
    print(f"   • Layer 1.5 extracts {avg_content_ratio:.1f}x more content on average")
    print(f"   • Average extraction time: {avg_extraction_time:.2f}s per workflow")
    print(f"   • {has_overlap*100:.0f}% of workflows have some content overlap")
    print()
    
    print("🏗️ RECOMMENDED ARCHITECTURE:")
    print()
    
    if avg_content_ratio > 10:  # Significant improvement
        print("   OPTION A: REPLACE LAYER 1 WITH LAYER 1.5")
        print("   ✅ Pros:")
        print("      - Eliminates data overlap")
        print("      - Much more comprehensive content")
        print("      - Single extraction per workflow")
        print("      - Cleaner architecture")
        print("   ❌ Cons:")
        print("      - Slightly slower extraction")
        print("      - Need to migrate existing data")
        print()
        
        print("   OPTION B: KEEP BOTH LAYERS (COMPLEMENTARY)")
        print("   ✅ Pros:")
        print("      - Layer 1 for quick metadata")
        print("      - Layer 1.5 for full content")
        print("      - Flexible extraction options")
        print("   ❌ Cons:")
        print("      - Data overlap and redundancy")
        print("      - More complex architecture")
        print("      - Higher storage costs")
        print()
        
        print("   OPTION C: HYBRID APPROACH")
        print("   ✅ Pros:")
        print("      - Fix Layer 1 to extract basic page content")
        print("      - Use Layer 1.5 for enhanced content")
        print("      - Clear separation of concerns")
        print("   ❌ Cons:")
        print("      - Requires Layer 1 rewrite")
        print("      - Still some potential overlap")
        print()
    
    print("🎯 RECOMMENDED SOLUTION:")
    if avg_content_ratio > 20:
        print("   → OPTION A: Replace Layer 1 with Layer 1.5")
        print("     The content improvement is too significant to ignore.")
        print("     Layer 1.5 should become the new Layer 1.")
    elif has_overlap < 0.5:
        print("   → OPTION B: Keep both layers")
        print("     Low overlap suggests they serve different purposes.")
    else:
        print("   → OPTION C: Hybrid approach")
        print("     Redesign the scraping pipeline to eliminate overlaps.")
    
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(test_layer1_5_on_10_workflows())



