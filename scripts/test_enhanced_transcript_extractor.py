#!/usr/bin/env python3
"""
Test Enhanced Transcript Extractor
Tests the enhanced transcript extractor on previously failing videos.

Author: Dev1
Task: 100% Transcript Reliability Testing
Date: October 16, 2025
"""

import asyncio
import sys
import time
from datetime import datetime
sys.path.append('.')

from src.scrapers.enhanced_transcript_extractor import EnhancedTranscriptExtractor


class EnhancedTranscriptTester:
    """Tests enhanced transcript extractor on failing videos."""
    
    def __init__(self):
        self.test_results = {}
    
    async def test_failing_videos(self):
        """Test the enhanced extractor on previously failing videos."""
        print("🧪 Testing Enhanced Transcript Extractor on Failing Videos")
        print("=" * 60)
        
        # Videos that failed in previous tests
        failing_videos = [
            {
                'video_id': 'ROgf5dVqYPQ',
                'workflow': '8237',
                'url': 'https://youtu.be/ROgf5dVqYPQ',
                'previous_issue': 'No transcript segments found'
            },
            {
                'video_id': 'dKTcAfBfFLU',
                'workflow': '8527',
                'url': 'https://youtu.be/dKTcAfBfFLU',
                'previous_issue': 'UI interaction failure'
            },
            {
                'video_id': 'laHIzhsz12E',
                'workflow': '6270',
                'url': 'https://youtu.be/laHIzhsz12E',
                'previous_issue': 'None (working video for comparison)'
            }
        ]
        
        results = {}
        
        for video in failing_videos:
            print(f"\n🔍 Testing Video {video['video_id']} (Workflow {video['workflow']})")
            print(f"   URL: {video['url']}")
            print(f"   Previous Issue: {video['previous_issue']}")
            
            start_time = time.time()
            
            try:
                async with EnhancedTranscriptExtractor(headless=True, timeout=30000) as extractor:
                    success, transcript, error = await extractor.extract_transcript(
                        video['url'], 
                        video['video_id']
                    )
                
                extraction_time = time.time() - start_time
                
                if success and transcript:
                    print(f"   ✅ SUCCESS in {extraction_time:.2f}s")
                    print(f"   📝 Transcript Length: {len(transcript)} chars")
                    print(f"   📄 Preview: {transcript[:100]}...")
                    results[video['video_id']] = {
                        'success': True,
                        'transcript_length': len(transcript),
                        'extraction_time': extraction_time,
                        'error': None
                    }
                else:
                    print(f"   ❌ FAILED in {extraction_time:.2f}s")
                    print(f"   🚨 Error: {error}")
                    results[video['video_id']] = {
                        'success': False,
                        'transcript_length': 0,
                        'extraction_time': extraction_time,
                        'error': error
                    }
                    
            except Exception as e:
                extraction_time = time.time() - start_time
                print(f"   💥 EXCEPTION in {extraction_time:.2f}s")
                print(f"   🚨 Error: {e}")
                results[video['video_id']] = {
                    'success': False,
                    'transcript_length': 0,
                    'extraction_time': extraction_time,
                    'error': str(e)
                }
        
        return results
    
    def analyze_results(self, results):
        """Analyze test results."""
        print("\n" + "=" * 60)
        print("📊 ENHANCED TRANSCRIPT EXTRACTOR TEST RESULTS")
        print("=" * 60)
        
        total_videos = len(results)
        successful_videos = sum(1 for r in results.values() if r['success'])
        failed_videos = total_videos - successful_videos
        
        print(f"📈 Overall Results:")
        print(f"   Total Videos Tested: {total_videos}")
        print(f"   Successful: {successful_videos}")
        print(f"   Failed: {failed_videos}")
        print(f"   Success Rate: {(successful_videos/total_videos)*100:.1f}%")
        
        if successful_videos > 0:
            avg_time = sum(r['extraction_time'] for r in results.values() if r['success']) / successful_videos
            avg_length = sum(r['transcript_length'] for r in results.values() if r['success']) / successful_videos
            print(f"   Average Extraction Time: {avg_time:.2f}s")
            print(f"   Average Transcript Length: {avg_length:.0f} chars")
        
        print(f"\n📋 Detailed Results:")
        for video_id, result in results.items():
            status = "✅ SUCCESS" if result['success'] else "❌ FAILED"
            print(f"   {video_id}: {status}")
            if result['success']:
                print(f"      Time: {result['extraction_time']:.2f}s, Length: {result['transcript_length']} chars")
            else:
                print(f"      Error: {result['error']}")
        
        # Recommendations
        print(f"\n💡 Recommendations:")
        if successful_videos == total_videos:
            print(f"   🎉 PERFECT! Enhanced extractor achieved 100% success rate!")
            print(f"   ✅ Ready for production deployment")
        elif successful_videos > 0:
            print(f"   ⚠️  Partial success - {failed_videos} videos still failing")
            print(f"   🔧 Need to investigate remaining failures")
        else:
            print(f"   🚨 All videos failed - need to debug enhanced extractor")
            print(f"   🔧 Check browser setup and network connectivity")
        
        return {
            'total_videos': total_videos,
            'successful_videos': successful_videos,
            'failed_videos': failed_videos,
            'success_rate': (successful_videos/total_videos)*100 if total_videos > 0 else 0,
            'results': results
        }
    
    async def run_test(self):
        """Run complete enhanced transcript extractor test."""
        print("🚀 Starting Enhanced Transcript Extractor Test")
        print(f"⏰ Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Test failing videos
        results = await self.test_failing_videos()
        
        # Analyze results
        analysis = self.analyze_results(results)
        
        print(f"\n⏰ Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return analysis


async def main():
    """Main test function."""
    tester = EnhancedTranscriptTester()
    results = await tester.run_test()
    return results


if __name__ == "__main__":
    asyncio.run(main())

