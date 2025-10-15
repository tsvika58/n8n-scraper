#!/usr/bin/env python3
"""
Validate Remaining Workflows (5170, 2462)

Focus on the workflows that failed or weren't tested yet.
"""

import os
import sys
import asyncio
from datetime import datetime
from dotenv import load_dotenv

# Add paths
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'n8n-shared'))

# Remaining workflows to test
REMAINING_WORKFLOWS = [
    ('5170', 'https://n8n.io/workflows/5170-learn-json-basics-with-an-interactive-step-by-step-tutorial-for-beginners/'),
    ('2462', 'https://n8n.io/workflows/2462-angie-personal-ai-assistant-with-telegram-voice-and-text/')
]

async def validate_remaining():
    """Validate the remaining workflows."""
    print("🎯 VALIDATING REMAINING WORKFLOWS")
    print("=" * 50)
    print(f"⏰ Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        from src.scrapers.layer3_enhanced_v2 import EnhancedLayer3Extractor
        
        async with EnhancedLayer3Extractor(headless=True, extract_transcripts=True) as extractor:
            for workflow_id, url in REMAINING_WORKFLOWS:
                print(f"📥 Processing {workflow_id}...")
                print(f"   URL: {url}")
                
                try:
                    result = await extractor.extract(workflow_id, url)
                    
                    if result['success']:
                        data = result['data']
                        video_count = data.get('video_count', 0)
                        transcript_count = data.get('transcript_count', 0)
                        content_length = data.get('content_length', 0)
                        quality_score = data.get('quality_score', 0)
                        
                        print(f"   ✅ SUCCESS: {video_count} videos, {transcript_count} transcripts, {content_length} chars, Q:{quality_score}")
                    else:
                        print(f"   ❌ FAILED: {result.get('error', 'Unknown error')}")
                        return False
                        
                except Exception as e:
                    print(f"   ❌ EXCEPTION: {e}")
                    return False
                
                print()
                await asyncio.sleep(3)
        
        print("🎉 ALL REMAINING WORKFLOWS VALIDATED SUCCESSFULLY!")
        return True
        
    except Exception as e:
        print(f"❌ CRITICAL ERROR: {e}")
        return False

async def main():
    """Main function."""
    success = await validate_remaining()
    if success:
        print("\n✅ REMAINING WORKFLOWS VALIDATION COMPLETE")
        sys.exit(0)
    else:
        print("\n❌ REMAINING WORKFLOWS VALIDATION FAILED")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
