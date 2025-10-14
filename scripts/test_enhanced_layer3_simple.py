"""
Simple Enhanced Layer 3 Test (No Database)

Tests the enhanced Layer 3 extractor on a few workflows to validate
the extraction capabilities without database complications.

Author: Developer-2 (Dev2)
Task: SCRAPE-010
Date: October 14, 2025
"""

import asyncio
import sys
import json
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / 'src'))

from scrapers.layer3_enhanced import EnhancedLayer3ExplainerExtractor


async def test_enhanced_layer3_simple():
    """Simple test of enhanced Layer 3 without database"""
    
    print('🎥 SIMPLE ENHANCED LAYER 3 TEST (NO DATABASE)')
    print('=' * 80)
    print()
    
    # Test a few specific workflows
    test_workflows = [
        ('6270', 'https://n8n.io/workflows/6270-build-your-first-ai-agent/'),
        ('8527', 'https://n8n.io/workflows/8527-learn-n8n-basics-in-3-easy-steps/'),
        ('8237', 'https://n8n.io/workflows/8237-personal-life-manager-with-telegram-google-services-and-voice-enabled-ai/'),
        ('7639', 'https://n8n.io/workflows/7639-talk-to-your-google-sheets-using-chatgpt-5/')
    ]
    
    results = []
    
    async with EnhancedLayer3ExplainerExtractor() as extractor:
        for wf_id, url in test_workflows:
            print(f'🔍 TESTING WORKFLOW {wf_id}')
            print(f'   URL: {url}')
            
            try:
                # Run enhanced extraction
                result = await extractor.extract_enhanced(wf_id, url)
                
                # Display results
                if result['success']:
                    data = result['data']
                    print(f'   ✅ Success: {result["success"]}')
                    print(f'   ⏱️  Time: {result["extraction_time"]:.2f}s')
                    print(f'   🎥 Videos Found: {data["video_count"]}')
                    print(f'   📝 Text Length: {data["total_text_length"]:,} chars')
                    print(f'   🖼️  Images: {len(data["images"])}')
                    print(f'   💻 Code Snippets: {len(data["code_snippets"])}')
                    print(f'   📊 Quality Score: {result["quality_score"]}/100')
                    
                    # Show video details
                    if data['video_count'] > 0:
                        print(f'   📹 Video Details:')
                        for i, video in enumerate(data['videos'][:3]):  # Show first 3
                            video_url = video.get('url', video.get('src', 'N/A'))
                            video_type = video.get('type', 'unknown')
                            print(f'      Video {i+1}: {video_type} - {video_url}')
                    
                    # Show discovery metadata
                    metadata = data['discovery_metadata']
                    print(f'   🔍 Discovery: {metadata["iframes_found"]} iframes, '
                          f'{metadata["videos_discovered"]} videos found, '
                          f'{metadata["fallback_videos"]} fallback videos')
                    
                    results.append({
                        'workflow_id': wf_id,
                        'success': True,
                        'extraction_time': result['extraction_time'],
                        'video_count': data['video_count'],
                        'text_length': data['total_text_length'],
                        'quality_score': result['quality_score'],
                        'videos': data['videos'],
                        'discovery_metadata': metadata
                    })
                else:
                    print(f'   ❌ Failed: {result.get("error", "Unknown error")}')
                    results.append({
                        'workflow_id': wf_id,
                        'success': False,
                        'error': result.get('error', 'Unknown error')
                    })
                
                print()
                
            except Exception as e:
                print(f'   ❌ Exception: {str(e)}')
                results.append({
                    'workflow_id': wf_id,
                    'success': False,
                    'error': str(e)
                })
                print()
    
    # Summary analysis
    print('📊 ENHANCED LAYER 3 TEST RESULTS SUMMARY')
    print('=' * 80)
    print()
    
    successful_tests = [r for r in results if r['success']]
    total_videos = sum(r.get('video_count', 0) for r in successful_tests)
    total_text = sum(r.get('text_length', 0) for r in successful_tests)
    avg_quality = sum(r.get('quality_score', 0) for r in successful_tests) / len(successful_tests) if successful_tests else 0
    
    print(f'✅ Successful Tests: {len(successful_tests)}/{len(results)}')
    print(f'🎥 Total Videos Found: {total_videos}')
    print(f'📝 Total Text Extracted: {total_text:,} characters')
    print(f'📊 Average Quality Score: {avg_quality:.1f}/100')
    
    if successful_tests:
        avg_time = sum(r.get('extraction_time', 0) for r in successful_tests) / len(successful_tests)
        print(f'⏱️  Average Time: {avg_time:.2f}s')
    print()
    
    # Video discovery analysis
    workflows_with_videos = [r for r in successful_tests if r.get('video_count', 0) > 0]
    video_discovery_rate = len(workflows_with_videos) / len(successful_tests) * 100 if successful_tests else 0
    
    print(f'🎯 VIDEO DISCOVERY ANALYSIS:')
    print(f'   Workflows with videos: {len(workflows_with_videos)}/{len(successful_tests)}')
    print(f'   Video discovery rate: {video_discovery_rate:.1f}%')
    print(f'   Target: ≥95% (vs current ~50%)')
    
    if video_discovery_rate >= 95:
        print('   ✅ TARGET ACHIEVED!')
    elif video_discovery_rate >= 80:
        print('   ⚠️  GOOD PROGRESS (80-95%)')
    else:
        print('   ❌ NEEDS IMPROVEMENT (<80%)')
    
    print()
    
    # Content completeness analysis
    high_text_workflows = [r for r in successful_tests if r.get('text_length', 0) > 1000]
    content_completeness = len(high_text_workflows) / len(successful_tests) * 100 if successful_tests else 0
    
    print(f'📝 CONTENT COMPLETENESS ANALYSIS:')
    print(f'   Workflows with rich content (>1000 chars): {len(high_text_workflows)}/{len(successful_tests)}')
    print(f'   Content completeness rate: {content_completeness:.1f}%')
    print(f'   Target: ≥90%')
    
    if content_completeness >= 90:
        print('   ✅ TARGET ACHIEVED!')
    elif content_completeness >= 70:
        print('   ⚠️  GOOD PROGRESS (70-90%)')
    else:
        print('   ❌ NEEDS IMPROVEMENT (<70%)')
    
    print()
    
    # Quality score analysis
    high_quality_workflows = [r for r in successful_tests if r.get('quality_score', 0) >= 85]
    quality_rate = len(high_quality_workflows) / len(successful_tests) * 100 if successful_tests else 0
    
    print(f'📊 QUALITY SCORE ANALYSIS:')
    print(f'   High quality workflows (≥85): {len(high_quality_workflows)}/{len(successful_tests)}')
    print(f'   Quality achievement rate: {quality_rate:.1f}%')
    print(f'   Target: ≥85% average')
    
    if avg_quality >= 85:
        print('   ✅ TARGET ACHIEVED!')
    elif avg_quality >= 70:
        print('   ⚠️  GOOD PROGRESS (70-85)')
    else:
        print('   ❌ NEEDS IMPROVEMENT (<70)')
    
    print()
    
    # Save detailed results
    results_file = Path(__file__).parent / 'enhanced_layer3_simple_test_results.json'
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f'💾 Detailed results saved to: {results_file}')
    print()
    
    # Overall assessment
    print('🎯 OVERALL ASSESSMENT:')
    
    targets_met = 0
    total_targets = 3
    
    if video_discovery_rate >= 95:
        targets_met += 1
        print('   ✅ Video Discovery: TARGET MET (≥95%)')
    else:
        print(f'   ❌ Video Discovery: {video_discovery_rate:.1f}% (target: ≥95%)')
    
    if content_completeness >= 90:
        targets_met += 1
        print('   ✅ Content Completeness: TARGET MET (≥90%)')
    else:
        print(f'   ❌ Content Completeness: {content_completeness:.1f}% (target: ≥90%)')
    
    if avg_quality >= 85:
        targets_met += 1
        print('   ✅ Quality Score: TARGET MET (≥85)')
    else:
        print(f'   ❌ Quality Score: {avg_quality:.1f} (target: ≥85)')
    
    print()
    
    if targets_met == total_targets:
        print('🎉 ALL TARGETS ACHIEVED! Enhanced Layer 3 is ready for production!')
        return True
    elif targets_met >= 2:
        print('⚠️  MOSTLY READY - Minor improvements needed')
        return True
    else:
        print('❌ NEEDS SIGNIFICANT IMPROVEMENTS before production')
        return False


if __name__ == "__main__":
    success = asyncio.run(test_enhanced_layer3_simple())
    sys.exit(0 if success else 1)
