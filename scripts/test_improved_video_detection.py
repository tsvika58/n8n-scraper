#!/usr/bin/env python3
"""
Test Improved Video Detection Algorithm
Tests the improved video detection algorithm with iframe extraction on workflow 7639.

Author: Dev1
Task: Test Edge Case Fix
Date: October 16, 2025
"""

import asyncio
import sys
import time
from datetime import datetime
sys.path.append('.')

from src.scrapers.unified_workflow_extractor import UnifiedWorkflowExtractor


class ImprovedVideoDetectionTester:
    """Tests the improved video detection algorithm."""
    
    def __init__(self):
        self.workflow_id = "7639"
        self.workflow_url = "https://n8n.io/workflows/7639-talk-to-your-google-sheets-using-chatgpt-5"
        self.expected_video_id = "qsrVPdo6svc"
        self.expected_video_url = "https://youtu.be/qsrVPdo6svc"
    
    async def test_improved_algorithm(self):
        """Test the improved video detection algorithm."""
        print("🧪 Testing Improved Video Detection Algorithm")
        print("=" * 60)
        
        print(f"📹 Test Information:")
        print(f"   Workflow ID: {self.workflow_id}")
        print(f"   Workflow URL: {self.workflow_url}")
        print(f"   Expected Video ID: {self.expected_video_id}")
        print(f"   Expected Video URL: {self.expected_video_url}")
        
        start_time = time.time()
        
        try:
            # Initialize unified extractor
            extractor = UnifiedWorkflowExtractor(
                headless=True,
                timeout=30000,
                extract_transcripts=True
            )
            
            # Extract workflow data
            result = await extractor.extract(
                self.workflow_id,
                self.workflow_url
            )
            
            extraction_time = time.time() - start_time
            
            if result['success']:
                print(f"\n✅ EXTRACTION SUCCESSFUL in {extraction_time:.2f}s")
                
                # Analyze results
                data = result.get('data', {})
                videos = data.get('videos', [])
                transcripts = data.get('transcripts', {})
                
                print(f"\n📊 Results Analysis:")
                print(f"   Videos Found: {len(videos)}")
                print(f"   Transcripts Extracted: {len(transcripts)}")
                
                # Check if expected video was found
                expected_video_found = False
                for video in videos:
                    if video.get('youtube_id') == self.expected_video_id:
                        expected_video_found = True
                        print(f"   ✅ Expected video found!")
                        print(f"      Video ID: {video.get('youtube_id')}")
                        print(f"      Video URL: {video.get('url')}")
                        print(f"      Type: {video.get('type')}")
                        print(f"      Context: {video.get('context', {}).get('location', 'unknown')}")
                        
                        # Check if transcript was extracted
                        video_url = video.get('url', '')
                        if video_url in transcripts:
                            transcript = transcripts[video_url]
                            print(f"      ✅ Transcript extracted: {len(transcript)} chars")
                            print(f"      📄 Preview: {transcript[:100]}...")
                        else:
                            print(f"      ❌ No transcript extracted")
                        break
                
                if not expected_video_found:
                    print(f"   ❌ Expected video NOT found")
                    print(f"   📋 Found videos:")
                    for i, video in enumerate(videos):
                        print(f"      {i+1}. {video.get('youtube_id')} - {video.get('type')}")
                
                # Overall assessment
                print(f"\n🎯 Overall Assessment:")
                if expected_video_found:
                    print(f"   🎉 SUCCESS: Edge case fixed!")
                    print(f"   ✅ Algorithm now finds videos in iframe content")
                    print(f"   ✅ Video detection is now comprehensive")
                else:
                    print(f"   🚨 FAILURE: Edge case not fixed")
                    print(f"   ❌ Algorithm still missing iframe videos")
                
                return {
                    'success': True,
                    'expected_video_found': expected_video_found,
                    'videos_found': len(videos),
                    'transcripts_extracted': len(transcripts),
                    'extraction_time': extraction_time,
                    'result': result
                }
                
            else:
                print(f"\n❌ EXTRACTION FAILED in {extraction_time:.2f}s")
                print(f"   Error: {result.get('error', 'Unknown error')}")
                return {
                    'success': False,
                    'expected_video_found': False,
                    'videos_found': 0,
                    'transcripts_extracted': 0,
                    'extraction_time': extraction_time,
                    'error': result.get('error', 'Unknown error')
                }
                
        except Exception as e:
            extraction_time = time.time() - start_time
            print(f"\n💥 EXCEPTION in {extraction_time:.2f}s")
            print(f"   Error: {e}")
            return {
                'success': False,
                'expected_video_found': False,
                'videos_found': 0,
                'transcripts_extracted': 0,
                'extraction_time': extraction_time,
                'error': str(e)
            }
    
    async def run_test(self):
        """Run the improved video detection test."""
        print("🚀 Starting Improved Video Detection Test")
        print(f"⏰ Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Test improved algorithm
        results = await self.test_improved_algorithm()
        
        print(f"\n⏰ Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return results


async def main():
    """Main test function."""
    tester = ImprovedVideoDetectionTester()
    results = await tester.run_test()
    return results


if __name__ == "__main__":
    asyncio.run(main())
