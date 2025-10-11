"""
Test multiple workflows to gather empirical data for SCRAPE-006
"""

import asyncio
import sys
from pathlib import Path
import json
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.scrapers.multimodal_processor import MultimodalProcessor


async def test_multiple_workflows():
    """Test multiple workflows to gather empirical success rates"""
    
    workflows = [
        {
            'id': '6270',
            'url': 'https://n8n.io/workflows/6270-build-your-first-ai-agent/',
            'description': 'Build Your First AI Agent (known working)'
        },
        {
            'id': '8527', 
            'url': 'https://n8n.io/workflows/8527-learn-n8n-basics-in-3-easy-steps/',
            'description': 'Learn n8n Basics in 3 Easy Steps'
        },
        {
            'id': '8237',
            'url': 'https://n8n.io/workflows/8237-personal-life-manager-with-telegram-google-services-and-voice-enabled-ai/',
            'description': 'Personal Life Manager with Telegram, Google Services & Voice-Enabled AI'
        }
    ]
    
    results = []
    total_start_time = datetime.now()
    
    print("\n" + "="*80)
    print("🧪 TESTING MULTIPLE WORKFLOWS FOR SCRAPE-006 EMPIRICAL DATA")
    print("="*80 + "\n")
    
    async with MultimodalProcessor() as processor:
        for i, workflow in enumerate(workflows, 1):
            print(f"\n{'='*60}")
            print(f"TEST {i}/3: {workflow['description']}")
            print(f"Workflow ID: {workflow['id']}")
            print(f"URL: {workflow['url']}")
            print(f"{'='*60}")
            
            start_time = datetime.now()
            result = await processor.process_workflow(workflow['id'], workflow['url'])
            end_time = datetime.now()
            
            result['workflow_info'] = workflow
            result['test_duration'] = (end_time - start_time).total_seconds()
            results.append(result)
            
            # Print immediate results
            print(f"\n📊 IMMEDIATE RESULTS:")
            print(f"  Iframes Found: {result['iframes_found']}")
            print(f"  Text Elements: {result['images_processed']} processed, {result['images_success']} successful")
            print(f"  Videos Found: {result['videos_found']} found, {result['videos_success']} successful")
            print(f"  Processing Time: {result['processing_time']:.2f}s")
            print(f"  Overall Success: {result['success']}")
            
            if result['images_processed'] > 0:
                text_rate = (result['images_success'] / result['images_processed']) * 100
                print(f"  Text Success Rate: {text_rate:.1f}%")
            
            if result['videos_found'] > 0:
                video_rate = (result['videos_success'] / result['videos_found']) * 100
                print(f"  Video Success Rate: {video_rate:.1f}%")
            
            if result['errors']:
                print(f"  Errors: {len(result['errors'])} errors encountered")
    
    total_end_time = datetime.now()
    total_duration = (total_end_time - total_start_time).total_seconds()
    
    # Calculate aggregate statistics
    total_iframes = sum(r['iframes_found'] for r in results)
    total_text_processed = sum(r['images_processed'] for r in results)
    total_text_successful = sum(r['images_success'] for r in results)
    total_videos_found = sum(r['videos_found'] for r in results)
    total_videos_successful = sum(r['videos_success'] for r in results)
    
    print(f"\n{'='*80}")
    print("📈 AGGREGATE RESULTS")
    print(f"{'='*80}")
    print(f"Workflows Tested: {len(results)}")
    print(f"Total Iframes: {total_iframes}")
    print(f"Text Elements: {total_text_processed} processed, {total_text_successful} successful")
    print(f"Videos: {total_videos_found} found, {total_videos_successful} successful")
    print(f"Total Processing Time: {total_duration:.2f}s")
    
    if total_text_processed > 0:
        overall_text_rate = (total_text_successful / total_text_processed) * 100
        print(f"Overall Text Success Rate: {overall_text_rate:.1f}%")
    
    if total_videos_found > 0:
        overall_video_rate = (total_videos_successful / total_videos_found) * 100
        print(f"Overall Video Success Rate: {overall_video_rate:.1f}%")
    
    # Check against SCRAPE-006 targets
    print(f"\n🎯 SCRAPE-006 TARGET COMPARISON:")
    if total_text_processed > 0:
        text_target_met = overall_text_rate >= 85
        print(f"Text Success Rate: {overall_text_rate:.1f}% {'✅' if text_target_met else '❌'} (Target: ≥85%)")
    
    if total_videos_found > 0:
        video_target_met = overall_video_rate >= 80
        print(f"Video Success Rate: {overall_video_rate:.1f}% {'✅' if video_target_met else '❌'} (Target: ≥80%)")
    
    # Save detailed results
    results_file = f"SCRAPE-006-multi-workflow-results-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n💾 Detailed results saved to: {results_file}")
    print(f"{'='*80}\n")
    
    return results


if __name__ == "__main__":
    asyncio.run(test_multiple_workflows())