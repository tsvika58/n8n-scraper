"""
Test Enhanced Video Discovery

Tests the enhanced L3 extractor on workflows that were missing videos.

Author: AI Assistant
Date: October 15, 2025
"""

import asyncio
import sys
import json
from typing import Dict, List

sys.path.append('/app')

from src.scrapers.layer3_enhanced_v2 import EnhancedLayer3Extractor
from src.storage.global_connection_coordinator import global_coordinator
from sqlalchemy import text
from loguru import logger

# Test the two workflows that were missing videos
TEST_CASES = [
    {
        'workflow_id': '7639',
        'url': 'https://n8n.io/workflows/7639-talk-to-your-google-sheets-using-chatgpt-5/',
        'expected_videos': ['qsrVPdo6svc']
    },
    {
        'workflow_id': '8527', 
        'url': 'https://n8n.io/workflows/8527-learn-n8n-basics-in-3-easy-steps/',
        'expected_videos': ['dKTcAfBfFLU', '5CBUXMO_L2Y', 'LdE0KnhRtsY']
    }
]

async def test_enhanced_discovery():
    """Test enhanced video discovery on missing video workflows"""
    
    print('🧪 TESTING ENHANCED VIDEO DISCOVERY')
    print('=' * 80)
    
    async with EnhancedLayer3Extractor(extract_transcripts=False) as extractor:
        for test_case in TEST_CASES:
            workflow_id = test_case['workflow_id']
            url = test_case['url']
            expected_videos = test_case['expected_videos']
            
            print(f'\n🔍 Testing {workflow_id}')
            print(f'URL: {url}')
            print(f'Expected: {expected_videos}')
            
            try:
                # Extract with enhanced discovery
                result = await extractor.extract(workflow_id, url)
                
                if result['success']:
                    found_videos = result['data']['video_urls']
                    found_count = result['data']['video_count']
                    
                    print(f'✅ Found {found_count} videos:')
                    for video_url in found_videos:
                        print(f'   🎥 {video_url}')
                    
                    # Check if we found all expected videos
                    found_video_ids = []
                    for video_url in found_videos:
                        if 'youtu.be/' in video_url:
                            video_id = video_url.split('youtu.be/')[-1]
                            found_video_ids.append(video_id)
                    
                    missing_videos = []
                    for expected_id in expected_videos:
                        if expected_id not in found_video_ids:
                            missing_videos.append(expected_id)
                    
                    if missing_videos:
                        print(f'❌ Still missing: {missing_videos}')
                    else:
                        print(f'🎉 All expected videos found!')
                    
                    print(f'Quality Score: {result["quality_score"]}/100')
                    
                else:
                    print(f'❌ Extraction failed: {result.get("error", "Unknown error")}')
                    
            except Exception as e:
                print(f'❌ Exception: {e}')
    
    print('\n🎉 ENHANCED DISCOVERY TEST COMPLETE!')

if __name__ == "__main__":
    asyncio.run(test_enhanced_discovery())
