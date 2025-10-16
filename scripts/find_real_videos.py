"""
Find Real Video URLs Using Multimodal Processor

Uses the existing multimodal processor to find ACTUAL embedded videos.

Author: Developer-2 (Dev2)
Date: October 14, 2025
"""

import asyncio
import sys

sys.path.append('/app')

from src.scrapers.multimodal_processor import MultimodalProcessor


async def find_real_videos():
    """Find actual embedded videos using multimodal processor"""
    
    test_workflows = [
        ('6270', 'https://n8n.io/workflows/6270-build-your-first-ai-agent/'),
        ('8527', 'https://n8n.io/workflows/8527-learn-n8n-basics-in-3-easy-steps/'),
        ('8237', 'https://n8n.io/workflows/8237-personal-life-manager-with-telegram-google-services-and-voice-enabled-ai/'),
        ('7639', 'https://n8n.io/workflows/7639-talk-to-your-google-sheets-using-chatgpt-5/'),
    ]
    
    print('🎥 FINDING REAL EMBEDDED VIDEOS')
    print('=' * 80)
    print()
    
    async with MultimodalProcessor(headless=True) as processor:
        for wf_id, url in test_workflows:
            print(f'🔍 WORKFLOW {wf_id}')
            print(f'URL: {url}')
            print('-' * 80)
            
            try:
                # Use multimodal processor to discover n8n workflow content
                page = await processor.browser.new_page()
                
                result = await processor.discover_n8n_workflow_content(page, url)
                
                print(f'YouTube Videos Found: {len(result["youtube_videos"])}')
                
                if result["youtube_videos"]:
                    print('Video URLs:')
                    for i, video_url in enumerate(result["youtube_videos"], 1):
                        print(f'  {i}. {video_url}')
                        print(f'     (Check this URL manually: {video_url})')
                else:
                    print('  ❌ No YouTube videos found')
                
                print(f'Text Content Blocks: {len(result["text_content"])}')
                print(f'Images: {len(result["images"])}')
                print()
                
                await page.close()
                
            except Exception as e:
                print(f'❌ Error: {e}')
                print()
    
    print('=' * 80)
    print('✅ Video discovery complete!')
    print()
    print('Please check the URLs above manually to verify they are actual videos.')


if __name__ == "__main__":
    asyncio.run(find_real_videos())




