#!/usr/bin/env python3
"""
Layer 3 Comprehensive Research Script

This script conducts thorough research on Layer 3 to understand:
1. What Layer 3 is designed to extract
2. How well it works in practice
3. Database schema compatibility
4. Overlaps with Layer 1.5 and Layer 2
5. Performance and quality metrics

Output: Comprehensive research report with recommendations
"""

import asyncio
import sys
import json
sys.path.append('/app')

from src.scrapers.layer3_explainer import ExplainerContentExtractor
from src.storage.database import get_session
from sqlalchemy import text
from loguru import logger
import time


async def research_layer3():
    """Main research function"""
    
    print("="*80)
    print("🔬 LAYER 3 COMPREHENSIVE RESEARCH")
    print("="*80)
    print()
    
    # Phase 1: Understand Layer 3 design
    print("📋 PHASE 1: UNDERSTANDING LAYER 3 DESIGN")
    print("-"*80)
    analyze_layer3_design()
    
    # Phase 2: Check database schema
    print("\n📋 PHASE 2: DATABASE SCHEMA ANALYSIS")
    print("-"*80)
    check_database_schema()
    
    # Phase 3: Test Layer 3 extraction
    print("\n📋 PHASE 3: TESTING LAYER 3 EXTRACTION (10 workflows)")
    print("-"*80)
    test_results = await test_layer3_extraction()
    
    # Phase 4: Overlap analysis
    print("\n📋 PHASE 4: OVERLAP ANALYSIS")
    print("-"*80)
    overlap_analysis = await analyze_overlaps(test_results)
    
    # Phase 5: Generate recommendations
    print("\n📋 PHASE 5: GENERATING RECOMMENDATIONS")
    print("-"*80)
    generate_recommendations(test_results, overlap_analysis)
    
    print("\n" + "="*80)
    print("✅ RESEARCH COMPLETE - See generated reports")
    print("="*80)


def analyze_layer3_design():
    """Analyze Layer 3's design and goals"""
    
    print("🎯 LAYER 3 DESIGN ANALYSIS:")
    print()
    print("**Primary Goal:**")
    print("   Extract tutorial and explainer content from n8n workflow pages")
    print("   Claims to provide '80% of NLP training value'")
    print()
    print("**13 Extracted Fields:**")
    fields = [
        "introduction", "overview", "tutorial_text", "tutorial_sections",
        "step_by_step", "best_practices", "common_pitfalls", "image_urls",
        "video_urls", "code_snippets", "conclusion", "troubleshooting",
        "related_workflows"
    ]
    for i, field in enumerate(fields, 1):
        print(f"   {i:2d}. {field}")
    
    print()
    print("**Target Metrics:**")
    print("   - Performance: 10-12 seconds per workflow")
    print("   - Success Rate: 90%+ on diverse workflows")
    print()
    print("**Key Features:**")
    print("   ✓ Iframe navigation for explainer content")
    print("   ✓ Dynamic content loading (5s wait)")
    print("   ✓ Hierarchical tutorial structure")
    print("   ✓ Image and video URL collection")
    print("   ✓ Code snippet extraction")
    print("   ✓ Text aggregation for NLP")
    print()


def check_database_schema():
    """Check Layer 3 database schema"""
    
    with get_session() as session:
        # Check if workflow_content table exists
        result = session.execute(text("""
            SELECT column_name, data_type, character_maximum_length
            FROM information_schema.columns 
            WHERE table_name = 'workflow_content'
            ORDER BY ordinal_position
        """)).fetchall()
        
        print("📊 WORKFLOW_CONTENT TABLE SCHEMA:")
        print()
        if result:
            for col_name, data_type, max_len in result:
                length_str = f"({max_len})" if max_len else ""
                print(f"   {col_name:30s} {data_type}{length_str}")
        else:
            print("   ❌ Table does not exist!")
        
        print()
        
        # Check existing Layer 3 data
        count_result = session.execute(text("""
            SELECT COUNT(*) FROM workflow_content
        """)).fetchone()
        
        print(f"📈 Existing Layer 3 Data: {count_result[0]} workflows")
        
        # Sample one record if exists
        if count_result[0] > 0:
            sample = session.execute(text("""
                SELECT workflow_id, 
                       LENGTH(explainer_text) as explainer_len,
                       LENGTH(setup_instructions) as setup_len,
                       has_videos,
                       video_count
                FROM workflow_content
                LIMIT 1
            """)).fetchone()
            
            print(f"\n📝 Sample Record (workflow {sample[0]}):")
            print(f"   Explainer text: {sample[1]} characters")
            print(f"   Setup instructions: {sample[2]} characters")
            print(f"   Has videos: {sample[3]}")
            print(f"   Video count: {sample[4]}")


async def test_layer3_extraction():
    """Test Layer 3 on 10 diverse workflows"""
    
    # Get 10 test workflows
    test_workflows = get_test_workflows()
    
    print(f"🧪 Testing Layer 3 on {len(test_workflows)} workflows:")
    for i, (wf_id, url, title) in enumerate(test_workflows, 1):
        title_short = (title[:50] + "...") if title and len(title) > 50 else title
        print(f"   {i}. {wf_id}: {title_short}")
    print()
    
    results = []
    
    async with ExplainerContentExtractor() as extractor:
        for i, (workflow_id, url, title) in enumerate(test_workflows, 1):
            print(f"\n🔍 [{i}/10] Testing workflow {workflow_id}")
            print("-" * 60)
            
            try:
                # Extract with Layer 3
                result = await extractor.extract(workflow_id, url)
                
                # Analyze the result
                analysis = analyze_extraction_result(workflow_id, result)
                results.append(analysis)
                
                # Print summary
                print(f"   Status: {'✅ SUCCESS' if result['success'] else '❌ FAILED'}")
                print(f"   Time: {result['extraction_time']:.2f}s")
                print(f"   Tutorial text: {len(result['data']['tutorial_text'])} chars")
                print(f"   Sections: {len(result['data']['tutorial_sections'])}")
                print(f"   Steps: {len(result['data']['step_by_step'])}")
                print(f"   Images: {len(result['data']['image_urls'])}")
                print(f"   Videos: {len(result['data']['video_urls'])}")
                print(f"   Code snippets: {len(result['data']['code_snippets'])}")
                
                if result['errors']:
                    print(f"   Errors: {result['errors']}")
                
            except Exception as e:
                print(f"   ❌ ERROR: {e}")
                results.append({
                    "workflow_id": workflow_id,
                    "success": False,
                    "error": str(e)
                })
    
    # Print summary
    print_test_summary(results)
    
    return results


def get_test_workflows():
    """Get 10 diverse workflows for testing"""
    
    with get_session() as session:
        # Get diverse workflows including 8040
        result = session.execute(text("""
            SELECT w.workflow_id, w.url, wm.title
            FROM workflows w
            LEFT JOIN workflow_metadata wm ON w.workflow_id = wm.workflow_id
            WHERE w.workflow_id IN ('8040', '8779', '8686', '8383', '2014', '6433', '474', '2980', '2818', '354')
            ORDER BY w.workflow_id
        """)).fetchall()
        
        return [(row[0], row[1], row[2]) for row in result]


def analyze_extraction_result(workflow_id, result):
    """Analyze a single extraction result"""
    
    data = result['data']
    
    # Count populated fields
    fields_populated = []
    fields_empty = []
    content_lengths = {}
    
    field_checks = {
        "introduction": data.get("introduction", ""),
        "overview": data.get("overview", ""),
        "tutorial_text": data.get("tutorial_text", ""),
        "tutorial_sections": data.get("tutorial_sections", []),
        "step_by_step": data.get("step_by_step", []),
        "best_practices": data.get("best_practices", []),
        "common_pitfalls": data.get("common_pitfalls", []),
        "image_urls": data.get("image_urls", []),
        "video_urls": data.get("video_urls", []),
        "code_snippets": data.get("code_snippets", []),
        "conclusion": data.get("conclusion", ""),
    }
    
    for field_name, value in field_checks.items():
        if isinstance(value, str):
            if value:
                fields_populated.append(field_name)
                content_lengths[field_name] = len(value)
            else:
                fields_empty.append(field_name)
        elif isinstance(value, list):
            if len(value) > 0:
                fields_populated.append(field_name)
                content_lengths[field_name] = len(value)
            else:
                fields_empty.append(field_name)
    
    return {
        "workflow_id": workflow_id,
        "success": result["success"],
        "extraction_time": result["extraction_time"],
        "fields_populated": fields_populated,
        "fields_empty": fields_empty,
        "content_lengths": content_lengths,
        "total_fields": len(field_checks),
        "populated_count": len(fields_populated),
        "populated_pct": (len(fields_populated) / len(field_checks) * 100),
        "errors": result.get("errors", [])
    }


def print_test_summary(results):
    """Print summary of test results"""
    
    print("\n" + "="*80)
    print("📊 TEST SUMMARY")
    print("="*80)
    
    successful = [r for r in results if r.get("success")]
    failed = [r for r in results if not r.get("success")]
    
    print(f"✅ Successful: {len(successful)}/10 ({len(successful)/10*100:.0f}%)")
    print(f"❌ Failed: {len(failed)}/10")
    
    if successful:
        avg_time = sum(r["extraction_time"] for r in successful) / len(successful)
        avg_populated = sum(r["populated_count"] for r in successful) / len(successful)
        avg_pct = sum(r["populated_pct"] for r in successful) / len(successful)
        
        print(f"\n⏱️  Average extraction time: {avg_time:.2f}s")
        print(f"📊 Average fields populated: {avg_populated:.1f}/11 ({avg_pct:.1f}%)")
        
        # Field population statistics
        field_counts = {}
        for r in successful:
            for field in r["fields_populated"]:
                field_counts[field] = field_counts.get(field, 0) + 1
        
        print(f"\n📋 Field Population Frequency:")
        for field, count in sorted(field_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"   {field:20s}: {count}/10 ({count/10*100:.0f}%)")


async def analyze_overlaps(layer3_results):
    """Analyze overlaps with Layer 1.5 and Layer 2"""
    
    print("🔍 Comparing Layer 3 with Layer 1.5 and Layer 2...")
    print()
    
    overlap_data = []
    
    for result in layer3_results:
        if not result.get("success"):
            continue
            
        wf_id = result["workflow_id"]
        
        # Get Layer 1.5 data
        with get_session() as session:
            l1_5_data = session.execute(text("""
                SELECT 
                    layer1_5_content_markdown,
                    layer1_5_metadata
                FROM workflow_metadata
                WHERE workflow_id = :wf_id
            """), {"wf_id": wf_id}).fetchone()
            
            # Get Layer 2 data
            l2_data = session.execute(text("""
                SELECT 
                    node_count,
                    LENGTH(workflow_json::text) as json_len,
                    LENGTH(additional_text_content) as text_len
                FROM workflow_structure
                WHERE workflow_id = :wf_id
            """), {"wf_id": wf_id}).fetchone()
        
        overlap = {
            "workflow_id": wf_id,
            "layer3": {
                "fields_populated": result["fields_populated"],
                "content_lengths": result["content_lengths"]
            },
            "layer1_5": {
                "exists": l1_5_data is not None and l1_5_data[0] is not None,
                "content_length": len(l1_5_data[0]) if l1_5_data and l1_5_data[0] else 0
            },
            "layer2": {
                "exists": l2_data is not None,
                "node_count": l2_data[0] if l2_data else 0,
                "json_length": l2_data[1] if l2_data and l2_data[1] else 0,
                "text_length": l2_data[2] if l2_data and l2_data[2] else 0
            }
        }
        
        overlap_data.append(overlap)
        
        print(f"Workflow {wf_id}:")
        print(f"   L3 fields: {len(result['fields_populated'])}/11")
        print(f"   L1.5: {'✓' if overlap['layer1_5']['exists'] else '✗'} ({overlap['layer1_5']['content_length']:,} chars)")
        print(f"   L2: {'✓' if overlap['layer2']['exists'] else '✗'} ({overlap['layer2']['text_length']:,} chars)")
        print()
    
    return overlap_data


def generate_recommendations(test_results, overlap_analysis):
    """Generate recommendations based on research"""
    
    successful = [r for r in test_results if r.get("success")]
    
    print("💡 RECOMMENDATIONS:")
    print()
    
    if len(successful) >= 9:  # 90%+ success
        print("✅ Layer 3 is working well (90%+ success rate)")
        print("   Recommendation: Deploy Layer 3 production scraper")
    else:
        print(f"⚠️  Layer 3 has {len(successful)}/10 success rate")
        print("   Recommendation: Fix issues before production rollout")
    
    print()
    print("📊 Next steps will be documented in research report")


if __name__ == "__main__":
    asyncio.run(research_layer3())

