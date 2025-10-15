"""
Layer 3 Production Scraper - FINAL VERSION

Fast, reliable, comprehensive Layer 3 scraping with:
- Video URL extraction & storage
- Video deduplication
- Transcript extraction
- Complete iframe content
- Resume capability
- Progress monitoring

Author: Developer-2 (Dev2)
Task: SCRAPE-010
Date: October 14, 2025
"""

import asyncio
import sys
import json
import time
import argparse
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import pytz

sys.path.append('/app')

from src.scrapers.layer3_enhanced_v2 import EnhancedLayer3Extractor
from src.storage.global_connection_coordinator import global_coordinator
from sqlalchemy import text
from loguru import logger


class Layer3ProductionRunner:
    """Production runner with progress monitoring"""
    
    def __init__(self, extract_transcripts: bool = True, resume: bool = True, overwrite: bool = False):
        self.extract_transcripts = extract_transcripts
        self.resume = resume
        self.overwrite = overwrite
        self.stats = {
            'total': 0,
            'completed': 0,
            'skipped': 0,
            'failed': 0,
            'total_videos': 0,
            'total_transcripts': 0,
            'start_time': None
        }
    
    async def get_workflows(self, limit: Optional[int] = None) -> List[Dict]:
        """Get workflows to process"""
        with global_coordinator.get_session() as session:
            result = session.execute(text("""
                SELECT workflow_id, url
                FROM workflows
                WHERE url IS NOT NULL
                ORDER BY workflow_id
            """)).fetchall()
            
            workflows = []
            for row in result:
                workflow_id = row[0]
                url = row[1]
                
                # Check if completed
                if self.resume and not self.overwrite:
                    try:
                        completed = session.execute(text("""
                            SELECT layer3_success
                            FROM workflow_content
                            WHERE workflow_id = :workflow_id
                        """), {"workflow_id": workflow_id}).fetchone()
                        
                        if completed and completed[0]:
                            self.stats['skipped'] += 1
                            continue
                    except:
                        pass
                
                workflows.append({'workflow_id': workflow_id, 'url': url})
                
                if limit and len(workflows) >= limit:
                    break
            
            return workflows
    
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
                    'iframe_sources': data['iframe_sources'],
                    'iframe_count': data['iframe_count'],
                    'has_iframes': data['has_iframes'],
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
                        transcripts = EXCLUDED.transcripts,
                        transcript_count = EXCLUDED.transcript_count,
                        content_text = EXCLUDED.content_text,
                        total_text_length = EXCLUDED.total_text_length,
                        quality_score = EXCLUDED.quality_score,
                        layer3_success = EXCLUDED.layer3_success,
                        layer3_extracted_at = EXCLUDED.layer3_extracted_at
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
        
        # Calculate ETA
        if self.stats['start_time'] and current > 0:
            elapsed = time.time() - self.stats['start_time']
            rate = current / elapsed
            remaining = total - current
            eta_seconds = remaining / rate if rate > 0 else 0
            eta_str = str(timedelta(seconds=int(eta_seconds)))
            
            # Jerusalem time
            completion_time = datetime.utcnow() + timedelta(seconds=eta_seconds)
            jerusalem_tz = pytz.timezone('Asia/Jerusalem')
            completion_jst = completion_time.replace(tzinfo=pytz.utc).astimezone(jerusalem_tz)
            eta_jst = completion_jst.strftime('%H:%M:%S')
        else:
            eta_str = "--:--:--"
            eta_jst = "--:--:--"
        
        print(f"\r📊 [{bar}] {current}/{total} ({pct:.1f}%)", end='')
        print(f" | {workflow_id} Q:{quality} V:{videos} T:{transcripts}", end='')
        print(f" | ETA: {eta_str} ({eta_jst} JST)", end='', flush=True)
    
    async def run(self, limit: Optional[int] = None):
        """Run production scraping"""
        
        print('🚀 LAYER 3 PRODUCTION SCRAPER')
        print('=' * 80)
        print()
        
        # Get workflows
        print('📋 Loading workflows...')
        workflows = await self.get_workflows(limit=limit)
        
        self.stats['total'] = len(workflows)
        self.stats['start_time'] = time.time()
        
        print(f'✅ Found {len(workflows)} workflows to process')
        if self.stats['skipped'] > 0:
            print(f'⏭️  Skipped {self.stats["skipped"]} already completed')
        print()
        
        # Process
        async with EnhancedLayer3Extractor(extract_transcripts=self.extract_transcripts) as extractor:
            for i, workflow in enumerate(workflows, 1):
                workflow_id = workflow['workflow_id']
                url = workflow['url']
                
                try:
                    # Extract
                    result = await extractor.extract(workflow_id, url)
                    
                    if result['success']:
                        # Save
                        saved = await self.save_result(result)
                        
                        if saved:
                            self.stats['completed'] += 1
                            self.stats['total_videos'] += result['data']['video_count']
                            self.stats['total_transcripts'] += result['data']['transcript_count']
                            
                            self.print_progress(
                                i, len(workflows), workflow_id,
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
                        
                except Exception as e:
                    self.stats['failed'] += 1
                    print(f"\n❌ Exception: {workflow_id} - {str(e)}")
        
        # Summary
        elapsed = time.time() - self.stats['start_time']
        print(f"\n\n🎉 LAYER 3 SCRAPING COMPLETE!")
        print('=' * 80)
        print(f'✅ Completed:     {self.stats["completed"]}')
        print(f'⏭️  Skipped:       {self.stats["skipped"]}')
        print(f'❌ Failed:        {self.stats["failed"]}')
        print(f'⏱️  Time:          {elapsed/3600:.2f} hours')
        print(f'🎥 Videos:        {self.stats["total_videos"]}')
        print(f'📝 Transcripts:   {self.stats["total_transcripts"]}')
        print()
        
        return self.stats['completed'] > 0


async def main():
    parser = argparse.ArgumentParser(description='Layer 3 Production Scraper')
    parser.add_argument('--limit', type=int, help='Limit number of workflows')
    parser.add_argument('--no-transcripts', action='store_true', help='Skip transcripts (faster)')
    parser.add_argument('--no-resume', action='store_true', help='Do not resume')
    parser.add_argument('--overwrite', action='store_true', help='Overwrite existing L3 data')
    
    args = parser.parse_args()
    
    runner = Layer3ProductionRunner(
        extract_transcripts=not args.no_transcripts,
        resume=not args.no_resume,
        overwrite=args.overwrite
    )
    
    success = await runner.run(limit=args.limit)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())

