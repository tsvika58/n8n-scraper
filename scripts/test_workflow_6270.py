"""
Test workflow 6270 (Build Your First AI Agent) which has text and video in iframe
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.scrapers.multimodal_processor import MultimodalProcessor


async def test_workflow_6270():
    """Test workflow 6270 with text and video content"""
    
    workflow_id = '6270'
    workflow_url = 'https://n8n.io/workflows/6270-build-your-first-ai-agent/'
    
    print("\n" + "="*70)
    print(f"TESTING WORKFLOW: {workflow_id}")
    print(f"URL: {workflow_url}")
    print("="*70 + "\n")
    
    async with MultimodalProcessor() as processor:
        result = await processor.process_workflow(workflow_id, workflow_url)
        
        print("\n" + "="*70)
        print("RESULTS:")
        print("="*70)
        print(f"Iframes Found: {result['iframes_found']}")
        print(f"Images Processed: {result['images_processed']}")
        print(f"Images Successful: {result['images_success']}")
        print(f"Videos Found: {result['videos_found']}")
        print(f"Videos Successful: {result['videos_success']}")
        print(f"Processing Time: {result['processing_time']:.2f}s")
        print(f"Overall Success: {result['success']}")
        
        if result['errors']:
            print(f"\nErrors encountered:")
            for error in result['errors']:
                print(f"  - {error}")
        
        print("="*70 + "\n")
        
        # Calculate success rates
        if result['images_processed'] > 0:
            ocr_rate = (result['images_success'] / result['images_processed']) * 100
            print(f"OCR Success Rate: {ocr_rate:.1f}%")
        
        if result['videos_found'] > 0:
            video_rate = (result['videos_success'] / result['videos_found']) * 100
            print(f"Video Success Rate: {video_rate:.1f}%")
        
        print()


if __name__ == "__main__":
    asyncio.run(test_workflow_6270())


