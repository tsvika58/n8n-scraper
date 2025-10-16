#!/usr/bin/env python3
"""
Debug Video 7639 Transcript Extraction
Debug specific video transcript extraction issues for workflow 7639.

Author: Dev1
Task: Debug Video 7639 Transcript Issues
Date: October 16, 2025
"""

import asyncio
import sys
import time
from datetime import datetime
sys.path.append('.')

from src.scrapers.transcript_extractor import TranscriptExtractor


class Video7639Debugger:
    """Debug transcript extraction for workflow 7639 video."""
    
    def __init__(self):
        self.video_info = {
            'video_id': 'qsrVPdo6svc',
            'workflow': '7639',
            'url': 'https://youtu.be/qsrVPdo6svc',
            'selectors': {
                'movie_player': '#movie_player',
                'movie_player_xpath': '//*[@id="movie_player"]'
            }
        }
    
    async def debug_video_extraction(self):
        """Debug the specific video extraction process."""
        print("🔍 Debugging Video 7639 Transcript Extraction")
        print("=" * 60)
        
        print(f"📹 Video Information:")
        print(f"   Video ID: {self.video_info['video_id']}")
        print(f"   Workflow: {self.video_info['workflow']}")
        print(f"   URL: {self.video_info['url']}")
        print(f"   Selectors: {self.video_info['selectors']}")
        
        # Test with different configurations
        test_configs = [
            {'headless': True, 'timeout': 30000, 'name': 'Headless Standard'},
            {'headless': False, 'timeout': 30000, 'name': 'Non-Headless Standard'},
            {'headless': True, 'timeout': 60000, 'name': 'Headless Extended Timeout'},
            {'headless': False, 'timeout': 60000, 'name': 'Non-Headless Extended Timeout'}
        ]
        
        results = {}
        
        for config in test_configs:
            print(f"\n🧪 Testing Configuration: {config['name']}")
            print(f"   Headless: {config['headless']}, Timeout: {config['timeout']}ms")
            
            start_time = time.time()
            
            try:
                async with TranscriptExtractor(
                    headless=config['headless'], 
                    timeout=config['timeout']
                ) as extractor:
                    success, transcript, error = await extractor.extract_transcript(
                        self.video_info['url'], 
                        self.video_info['video_id']
                    )
                
                extraction_time = time.time() - start_time
                
                if success and transcript:
                    print(f"   ✅ SUCCESS in {extraction_time:.2f}s")
                    print(f"   📝 Transcript Length: {len(transcript)} chars")
                    print(f"   📄 Preview: {transcript[:100]}...")
                    results[config['name']] = {
                        'success': True,
                        'transcript_length': len(transcript),
                        'extraction_time': extraction_time,
                        'error': None,
                        'transcript_preview': transcript[:200]
                    }
                else:
                    print(f"   ❌ FAILED in {extraction_time:.2f}s")
                    print(f"   🚨 Error: {error}")
                    results[config['name']] = {
                        'success': False,
                        'transcript_length': 0,
                        'extraction_time': extraction_time,
                        'error': error,
                        'transcript_preview': None
                    }
                    
            except Exception as e:
                extraction_time = time.time() - start_time
                print(f"   💥 EXCEPTION in {extraction_time:.2f}s")
                print(f"   🚨 Error: {e}")
                results[config['name']] = {
                    'success': False,
                    'transcript_length': 0,
                    'extraction_time': extraction_time,
                    'error': str(e),
                    'transcript_preview': None
                }
        
        return results
    
    def analyze_results(self, results):
        """Analyze the debug results."""
        print("\n" + "=" * 60)
        print("📊 VIDEO 7639 DEBUG ANALYSIS")
        print("=" * 60)
        
        successful_configs = [name for name, result in results.items() if result['success']]
        failed_configs = [name for name, result in results.items() if not result['success']]
        
        print(f"📈 Results Summary:")
        print(f"   Total Configurations Tested: {len(results)}")
        print(f"   Successful: {len(successful_configs)}")
        print(f"   Failed: {len(failed_configs)}")
        print(f"   Success Rate: {(len(successful_configs)/len(results))*100:.1f}%")
        
        if successful_configs:
            print(f"\n✅ Successful Configurations:")
            for config_name in successful_configs:
                result = results[config_name]
                print(f"   - {config_name}: {result['transcript_length']} chars in {result['extraction_time']:.2f}s")
        
        if failed_configs:
            print(f"\n❌ Failed Configurations:")
            for config_name in failed_configs:
                result = results[config_name]
                print(f"   - {config_name}: {result['error']}")
        
        # Recommendations
        print(f"\n💡 Recommendations:")
        if successful_configs:
            best_config = max(successful_configs, key=lambda x: results[x]['transcript_length'])
            print(f"   🎯 Best Configuration: {best_config}")
            print(f"   📝 Transcript Length: {results[best_config]['transcript_length']} chars")
            print(f"   ⏱️  Extraction Time: {results[best_config]['extraction_time']:.2f}s")
            
            if results[best_config]['transcript_preview']:
                print(f"   📄 Transcript Preview:")
                print(f"      {results[best_config]['transcript_preview']}...")
        else:
            print(f"   🚨 All configurations failed - need to investigate further")
            print(f"   🔧 Possible issues:")
            print(f"      - Video has no transcript available")
            print(f"      - YouTube UI changes")
            print(f"      - Network connectivity issues")
            print(f"      - Browser compatibility problems")
        
        return {
            'successful_configs': successful_configs,
            'failed_configs': failed_configs,
            'best_config': best_config if successful_configs else None,
            'results': results
        }
    
    async def run_debug(self):
        """Run complete debug analysis."""
        print("🚀 Starting Video 7639 Debug Analysis")
        print(f"⏰ Debug started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Debug video extraction
        results = await self.debug_video_extraction()
        
        # Analyze results
        analysis = self.analyze_results(results)
        
        print(f"\n⏰ Debug completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return analysis


async def main():
    """Main debug function."""
    debugger = Video7639Debugger()
    results = await debugger.run_debug()
    return results


if __name__ == "__main__":
    asyncio.run(main())

