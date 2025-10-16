#!/usr/bin/env python3
"""
Test Unified Scraper on 7 Video Workflows
Tests the unified workflow extractor on all 7 video workflows to validate consistency.

Author: Dev1
Task: Test Unified Scraper on 7 Video Workflows
Date: October 16, 2025
"""

import asyncio
import sys
import time
from datetime import datetime
sys.path.append('.')

from src.scrapers.unified_workflow_extractor import extract_workflow_unified

# The 7 actual video workflows we tested earlier
VIDEO_WORKFLOWS = [
    {
        'id': '6270',
        'url': 'https://n8n.io/workflows/6270-build-your-first-ai-agent',
        'expected_nodes': 6,
        'expected_videos': 1
    },
    {
        'id': '8642',
        'url': 'https://n8n.io/workflows/8642-generate-ai-viral-videos-with-veo-3-and-upload-to-tiktok',
        'expected_nodes': 8,
        'expected_videos': 1
    },
    {
        'id': '8527',
        'url': 'https://n8n.io/workflows/8527-learn-n8n-basics-in-3-easy-steps',
        'expected_nodes': 5,
        'expected_videos': 1
    },
    {
        'id': '8237',
        'url': 'https://n8n.io/workflows/8237-personal-life-manager-with-telegram-google-services-and-voice-enabled-ai',
        'expected_nodes': 14,
        'expected_videos': 1
    },
    {
        'id': '7639',
        'url': 'https://n8n.io/workflows/7639-talk-to-your-google-sheets-using-chatgpt-5',
        'expected_nodes': 7,
        'expected_videos': 1
    },
    {
        'id': '5170',
        'url': 'https://n8n.io/workflows/5170-learn-json-basics-with-an-interactive-step-by-step-tutorial-for-beginners',
        'expected_nodes': 10,
        'expected_videos': 1
    },
    {
        'id': '2462',
        'url': 'https://n8n.io/workflows/2462-angie-personal-ai-assistant-with-telegram-voice-and-text',
        'expected_nodes': 9,
        'expected_videos': 1
    }
]


async def test_workflow(workflow_info):
    """Test a single workflow with the unified scraper."""
    workflow_id = workflow_info['id']
    workflow_url = workflow_info['url']
    expected_nodes = workflow_info['expected_nodes']
    expected_videos = workflow_info['expected_videos']
    
    print(f"\n🔍 Testing workflow {workflow_id}")
    print(f"   URL: {workflow_url}")
    print(f"   Expected: {expected_nodes} nodes, {expected_videos} videos")
    
    start_time = time.time()
    
    try:
        result = await extract_workflow_unified(
            workflow_id=workflow_id,
            workflow_url=workflow_url,
            headless=True,
            save_to_db=True
        )
        
        extraction_time = time.time() - start_time
        
        if result['success']:
            data = result['data']
            actual_nodes = data['node_count']
            actual_videos = data['video_count']
            actual_contexts = data['node_context_count']
            actual_standalone = data['standalone_note_count']
            actual_transcripts = data['transcript_count']
            quality_score = result['quality_score']
            
            print(f"   ✅ SUCCESS in {extraction_time:.2f}s")
            print(f"   📊 Results:")
            print(f"      - Nodes: {actual_nodes} (expected: {expected_nodes})")
            print(f"      - Videos: {actual_videos} (expected: {expected_videos})")
            print(f"      - Node contexts: {actual_contexts}")
            print(f"      - Standalone notes: {actual_standalone}")
            print(f"      - Transcripts: {actual_transcripts}")
            print(f"      - Quality score: {quality_score:.2f}")
            
            # Check if results match expectations
            node_match = "✅" if actual_nodes == expected_nodes else "⚠️"
            video_match = "✅" if actual_videos == expected_videos else "⚠️"
            
            print(f"   🎯 Validation:")
            print(f"      - Node count: {node_match}")
            print(f"      - Video count: {video_match}")
            
            return {
                'workflow_id': workflow_id,
                'success': True,
                'extraction_time': extraction_time,
                'nodes': actual_nodes,
                'videos': actual_videos,
                'contexts': actual_contexts,
                'standalone': actual_standalone,
                'transcripts': actual_transcripts,
                'quality_score': quality_score,
                'node_match': actual_nodes == expected_nodes,
                'video_match': actual_videos == expected_videos
            }
        else:
            print(f"   ❌ FAILED: {result['error']}")
            return {
                'workflow_id': workflow_id,
                'success': False,
                'error': result['error'],
                'extraction_time': extraction_time
            }
            
    except Exception as e:
        extraction_time = time.time() - start_time
        print(f"   ❌ EXCEPTION: {e}")
        return {
            'workflow_id': workflow_id,
            'success': False,
            'error': str(e),
            'extraction_time': extraction_time
        }


async def test_all_workflows():
    """Test all 7 video workflows."""
    print("🚀 Testing Unified Scraper on 7 Video Workflows")
    print("=" * 60)
    
    start_time = time.time()
    results = []
    
    for workflow_info in VIDEO_WORKFLOWS:
        result = await test_workflow(workflow_info)
        results.append(result)
    
    total_time = time.time() - start_time
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    
    successful = [r for r in results if r['success']]
    failed = [r for r in results if not r['success']]
    
    print(f"✅ Successful: {len(successful)}/{len(results)}")
    print(f"❌ Failed: {len(failed)}/{len(results)}")
    print(f"⏱️  Total time: {total_time:.2f}s")
    print(f"📈 Average time per workflow: {total_time/len(results):.2f}s")
    
    if successful:
        avg_nodes = sum(r['nodes'] for r in successful) / len(successful)
        avg_videos = sum(r['videos'] for r in successful) / len(successful)
        avg_contexts = sum(r['contexts'] for r in successful) / len(successful)
        avg_standalone = sum(r['standalone'] for r in successful) / len(successful)
        avg_transcripts = sum(r['transcripts'] for r in successful) / len(successful)
        avg_quality = sum(r['quality_score'] for r in successful) / len(successful)
        
        print(f"\n📈 Averages (successful workflows):")
        print(f"   - Nodes: {avg_nodes:.1f}")
        print(f"   - Videos: {avg_videos:.1f}")
        print(f"   - Node contexts: {avg_contexts:.1f}")
        print(f"   - Standalone notes: {avg_standalone:.1f}")
        print(f"   - Transcripts: {avg_transcripts:.1f}")
        print(f"   - Quality score: {avg_quality:.2f}")
        
        # Validation summary
        node_matches = sum(1 for r in successful if r['node_match'])
        video_matches = sum(1 for r in successful if r['video_match'])
        
        print(f"\n🎯 Validation Summary:")
        print(f"   - Node count matches: {node_matches}/{len(successful)}")
        print(f"   - Video count matches: {video_matches}/{len(successful)}")
    
    if failed:
        print(f"\n❌ Failed workflows:")
        for result in failed:
            print(f"   - {result['workflow_id']}: {result['error']}")
    
    print(f"\n🏁 Test completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return results


if __name__ == "__main__":
    asyncio.run(test_all_workflows())
