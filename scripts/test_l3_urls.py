"""
Layer 3 Test Runner for 7 Specific URLs

Tests the enhanced Layer 3 extractor on the 7 provided workflow URLs
with video content to validate deep context extraction.

Author: AI Assistant
Date: October 15, 2025
Version: 1.0.0
"""

import asyncio
import sys
import json
import time
from typing import Dict, List, Optional
from datetime import datetime

sys.path.append('/app')

from src.scrapers.layer3_enhanced_v2 import EnhancedLayer3Extractor
from src.storage.global_connection_coordinator import global_coordinator
from sqlalchemy import text
from loguru import logger


# The 7 test URLs provided by the user
TEST_URLS = [
    "https://n8n.io/workflows/6270-build-your-first-ai-agent/",  # Has video
    "https://n8n.io/workflows/8642-generate-ai-viral-videos-with-veo-3-and-upload-to-tiktok/",  # Has videos
    "https://n8n.io/workflows/8527-learn-n8n-basics-in-3-easy-steps/",
    "https://n8n.io/workflows/8237-personal-life-manager-with-telegram-google-services-and-voice-enabled-ai/",
    "https://n8n.io/workflows/7639-talk-to-your-google-sheets-using-chatgpt-5/",
    "https://n8n.io/workflows/5170-learn-json-basics-with-an-interactive-step-by-step-tutorial-for-beginners/",
    "https://n8n.io/workflows/2462-angie-personal-ai-assistant-with-telegram-voice-and-text/"
]


class Layer3TestRunner:
    """Test runner for the 7 specific URLs"""
    
    def __init__(self, extract_transcripts: bool = True, overwrite: bool = True):
        self.extract_transcripts = extract_transcripts
        self.overwrite = overwrite
        self.results = []
        self.stats = {
            'total': len(TEST_URLS),
            'completed': 0,
            'failed': 0,
            'total_videos': 0,
            'total_transcripts': 0,
            'start_time': None
        }
    
    async def get_workflow_id_from_url(self, url: str) -> Optional[str]:
        """Extract workflow ID from URL"""
        try:
            # Extract ID from URL pattern: /workflows/{id}-
            import re
            match = re.search(r'/workflows/(\d+)', url)
            return match.group(1) if match else None
        except Exception as e:
            logger.error(f"Error extracting workflow ID from {url}: {e}")
            return None
    
    async def save_result(self, result: Dict) -> bool:
        """Save extraction result to database"""
        if not result.get('success'):
            return False
        
        workflow_id = result['workflow_id']
        data = result['data']
        
        try:
            with global_coordinator.get_session() as session:
                save_data = {
                    'workflow_id': workflow_id,
                    'video_urls': data['video_urls'],
                    'video_metadata': json.dumps(data['videos']),
                    'video_count': data['video_count'],
                    'has_videos': data['has_videos'],
                    'transcripts': json.dumps(data['transcripts']),
                    'transcript_count': data['transcript_count'],
                    'has_transcripts': data['has_transcripts'],
                    'content_text': data['content_text'],
                    'total_text_length': data['total_text_length'],
                    'image_urls': data['image_urls'],
                    'image_count': data['image_count'],
                    'iframe_sources': data.get('iframe_sources', []),
                    'iframe_count': data.get('iframe_count', 0),
                    'has_iframes': data.get('has_iframes', False),
                    'quality_score': result['quality_score'],
                    'layer3_success': True,
                    'layer3_extracted_at': datetime.utcnow(),
                    'layer3_version': result['metadata']['extractor_version']
                }
                
                session.execute(text("""
                    INSERT INTO workflow_content (
                        workflow_id, video_urls, video_metadata, video_count, has_videos,
                        transcripts, transcript_count, has_transcripts,
                        content_text, total_text_length,
                        image_urls, image_count,
                        iframe_sources, iframe_count, has_iframes,
                        quality_score, layer3_success, layer3_extracted_at, layer3_version
                    ) VALUES (
                        :workflow_id, :video_urls, :video_metadata, :video_count, :has_videos,
                        :transcripts, :transcript_count, :has_transcripts,
                        :content_text, :total_text_length,
                        :image_urls, :image_count,
                        :iframe_sources, :iframe_count, :has_iframes,
                        :quality_score, :layer3_success, :layer3_extracted_at, :layer3_version
                    )
                    ON CONFLICT (workflow_id) DO UPDATE SET
                        video_urls = EXCLUDED.video_urls,
                        video_metadata = EXCLUDED.video_metadata,
                        video_count = EXCLUDED.video_count,
                        has_videos = EXCLUDED.has_videos,
                        transcripts = EXCLUDED.transcripts,
                        transcript_count = EXCLUDED.transcript_count,
                        has_transcripts = EXCLUDED.has_transcripts,
                        content_text = EXCLUDED.content_text,
                        total_text_length = EXCLUDED.total_text_length,
                        image_urls = EXCLUDED.image_urls,
                        image_count = EXCLUDED.image_count,
                        iframe_sources = EXCLUDED.iframe_sources,
                        iframe_count = EXCLUDED.iframe_count,
                        has_iframes = EXCLUDED.has_iframes,
                        quality_score = EXCLUDED.quality_score,
                        layer3_success = EXCLUDED.layer3_success,
                        layer3_extracted_at = EXCLUDED.layer3_extracted_at,
                        layer3_version = EXCLUDED.layer3_version
                """), save_data)
                
                session.commit()
                return True
                
        except Exception as e:
            logger.error(f"Save failed for {workflow_id}: {e}")
            return False
    
    def print_progress(self, current: int, total: int, workflow_id: str, quality: int, videos: int, transcripts: int):
        """Print progress bar"""
        pct = (current / total) * 100
        bar_length = 50
        filled = int(bar_length * current // total)
        bar = '█' * filled + '-' * (bar_length - filled)
        
        print(f"\r📊 [{bar}] {current}/{total} ({pct:.1f}%)", end='')
        print(f" | {workflow_id} Q:{quality} V:{videos} T:{transcripts}", end='', flush=True)
    
    async def run(self):
        """Run tests on all 7 URLs"""
        
        print('🧪 LAYER 3 TEST RUNNER - 7 SPECIFIC URLS')
        print('=' * 80)
        print()
        
        self.stats['start_time'] = time.time()
        
        # Process each URL
        async with EnhancedLayer3Extractor(extract_transcripts=self.extract_transcripts) as extractor:
            for i, url in enumerate(TEST_URLS, 1):
                workflow_id = await self.get_workflow_id_from_url(url)
                
                if not workflow_id:
                    logger.error(f"❌ Could not extract workflow ID from: {url}")
                    self.stats['failed'] += 1
                    continue
                
                try:
                    print(f"\n🔍 Testing {i}/7: {workflow_id}")
                    print(f"   URL: {url}")
                    
                    # Extract
                    result = await extractor.extract(workflow_id, url)
                    
                    if result['success']:
                        # Save
                        saved = await self.save_result(result)
                        
                        if saved:
                            self.stats['completed'] += 1
                            self.stats['total_videos'] += result['data']['video_count']
                            self.stats['total_transcripts'] += result['data']['transcript_count']
                            
                            # Store result for summary
                            self.results.append({
                                'workflow_id': workflow_id,
                                'url': url,
                                'success': True,
                                'videos': result['data']['video_count'],
                                'transcripts': result['data']['transcript_count'],
                                'quality': result['quality_score'],
                                'primary_explainers': len(result['data']['primary_explainer_videos']),
                                'text_length': result['data']['total_text_length']
                            })
                            
                            self.print_progress(
                                i, len(TEST_URLS), workflow_id,
                                result['quality_score'],
                                result['data']['video_count'],
                                result['data']['transcript_count']
                            )
                        else:
                            self.stats['failed'] += 1
                            print(f"\n❌ Save failed: {workflow_id}")
                    else:
                        self.stats['failed'] += 1
                        print(f"\n❌ Extraction failed: {workflow_id}")
                        print(f"   Error: {result.get('error', 'Unknown error')}")
                        
                except Exception as e:
                    self.stats['failed'] += 1
                    print(f"\n❌ Exception: {workflow_id} - {str(e)}")
        
        # Summary
        elapsed = time.time() - self.stats['start_time']
        print(f"\n\n🎉 LAYER 3 TEST COMPLETE!")
        print('=' * 80)
        print(f'✅ Completed:     {self.stats["completed"]}')
        print(f'❌ Failed:        {self.stats["failed"]}')
        print(f'⏱️  Time:          {elapsed/60:.1f} minutes')
        print(f'🎥 Videos:        {self.stats["total_videos"]}')
        print(f'📝 Transcripts:   {self.stats["total_transcripts"]}')
        print()
        
        # Detailed results
        if self.results:
            print('📋 DETAILED RESULTS:')
            print('-' * 80)
            for result in self.results:
                print(f"✅ {result['workflow_id']}: {result['videos']} videos "
                      f"({result['primary_explainers']} primary), "
                      f"{result['transcripts']} transcripts, "
                      f"{result['text_length']:,} chars, Q:{result['quality']}")
            print()
        
        # Save results to file
        results_file = f'/app/test_results_l3_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(results_file, 'w') as f:
            json.dump({
                'timestamp': datetime.utcnow().isoformat(),
                'stats': self.stats,
                'results': self.results,
                'urls_tested': TEST_URLS
            }, f, indent=2)
        
        print(f'💾 Results saved to: {results_file}')
        
        return self.stats['completed'] > 0


async def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Layer 3 Test Runner for 7 URLs')
    parser.add_argument('--no-transcripts', action='store_true', help='Skip transcripts (faster)')
    parser.add_argument('--no-overwrite', action='store_true', help='Do not overwrite existing data')
    
    args = parser.parse_args()
    
    runner = Layer3TestRunner(
        extract_transcripts=not args.no_transcripts,
        overwrite=not args.no_overwrite
    )
    
    success = await runner.run()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())
