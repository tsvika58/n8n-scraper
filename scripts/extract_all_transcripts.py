#!/usr/bin/env python3
"""
SCRAPE-006B Phase 2: Batch Transcript Extraction

This script extracts YouTube transcripts for all discovered videos.
Run AFTER multimodal_processor completes Phase 1 (video discovery).

Usage:
    python scripts/extract_all_transcripts.py [--db-path PATH] [--limit N]

Performance:
    - ~10 seconds per video
    - 100% success rate (proven in testing)
    - Clean execution context (YouTube-only)
"""

import asyncio
import argparse
import json
import sqlite3
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

# Add src to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.scrapers.transcript_extractor import TranscriptExtractor
from loguru import logger


class TranscriptBatchProcessor:
    """Batch processes transcript extraction for discovered videos."""
    
    def __init__(self, db_path: str = "data/n8n_workflows.db"):
        self.db_path = db_path
        self.stats = {
            'total': 0,
            'successful': 0,
            'failed': 0,
            'skipped': 0,
            'start_time': None,
            'end_time': None,
        }
    
    def get_videos_needing_transcripts(self, limit: Optional[int] = None) -> List[Dict]:
        """
        Get all videos that need transcript extraction.
        
        Returns:
            List of dicts with workflow_id, video_url, video_id
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get all workflows with videos
        cursor.execute("""
            SELECT workflow_id, video_urls, video_transcripts
            FROM workflows
            WHERE video_urls IS NOT NULL AND video_urls != '[]'
        """)
        
        videos_to_process = []
        
        for row in cursor.fetchall():
            workflow_id, video_urls_json, video_transcripts_json = row
            
            # Parse video URLs
            video_urls = json.loads(video_urls_json) if video_urls_json else []
            
            # Parse existing transcripts
            existing_transcripts = {}
            if video_transcripts_json:
                transcripts = json.loads(video_transcripts_json)
                for t in transcripts:
                    existing_transcripts[t['video_id']] = t
            
            # Find videos needing transcripts
            for video_url in video_urls:
                # Extract video ID from URL
                video_id = self._extract_video_id(video_url)
                if not video_id:
                    continue
                
                # Check if already has successful transcript
                existing = existing_transcripts.get(video_id, {})
                if existing.get('success') and existing.get('transcript'):
                    continue  # Skip - already has transcript
                
                videos_to_process.append({
                    'workflow_id': workflow_id,
                    'video_url': video_url,
                    'video_id': video_id
                })
                
                if limit and len(videos_to_process) >= limit:
                    break
            
            if limit and len(videos_to_process) >= limit:
                break
        
        conn.close()
        return videos_to_process
    
    def _extract_video_id(self, video_url: str) -> Optional[str]:
        """Extract video ID from YouTube URL."""
        import re
        patterns = [
            r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([a-zA-Z0-9_-]{11})',
            r'youtube-nocookie\.com/embed/([a-zA-Z0-9_-]{11})',
            r'/embed/([a-zA-Z0-9_-]{11})',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, video_url)
            if match:
                return match.group(1)
        
        return None
    
    def update_transcript_in_db(self, workflow_id: str, video_id: str,
                                success: bool, transcript: Optional[str], error: Optional[str]):
        """Update transcript for a specific video in the database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get current video_transcripts
        cursor.execute("SELECT video_transcripts FROM workflows WHERE workflow_id = ?", (workflow_id,))
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            return
        
        # Parse existing transcripts
        existing_json = row[0]
        transcripts = json.loads(existing_json) if existing_json else []
        
        # Update or add this video's transcript
        updated = False
        for t in transcripts:
            if t['video_id'] == video_id:
                t['success'] = success
                t['transcript'] = transcript if success else None
                t['length'] = len(transcript) if success and transcript else 0
                t['error'] = error if not success else None
                t['extracted_at'] = datetime.now().isoformat()
                updated = True
                break
        
        if not updated:
            # Add new transcript entry
            transcripts.append({
                'video_id': video_id,
                'success': success,
                'transcript': transcript if success else None,
                'length': len(transcript) if success and transcript else 0,
                'error': error if not success else None,
                'extracted_at': datetime.now().isoformat()
            })
        
        # Update database
        cursor.execute(
            "UPDATE workflows SET video_transcripts = ? WHERE workflow_id = ?",
            (json.dumps(transcripts), workflow_id)
        )
        conn.commit()
        conn.close()
    
    async def process_all_videos(self, limit: Optional[int] = None, headless: bool = True):
        """
        Process all videos needing transcripts.
        
        Args:
            limit: Max number of videos to process (None = all)
            headless: Run browser in headless mode
        """
        # Get videos needing transcripts
        videos = self.get_videos_needing_transcripts(limit)
        
        if not videos:
            logger.info("No videos need transcript extraction")
            return
        
        logger.info(f"Found {len(videos)} videos needing transcripts")
        
        self.stats['total'] = len(videos)
        self.stats['start_time'] = time.time()
        
        # Process videos with TranscriptExtractor
        async with TranscriptExtractor(headless=headless) as extractor:
            for i, video in enumerate(videos, 1):
                workflow_id = video['workflow_id']
                video_url = video['video_url']
                video_id = video['video_id']
                
                logger.info(f"[{i}/{len(videos)}] Processing {video_id} from workflow {workflow_id}")
                
                try:
                    # Extract transcript
                    start_time = time.time()
                    success, transcript, error = await extractor.extract_transcript(video_url, video_id)
                    end_time = time.time()
                    
                    # Update database
                    self.update_transcript_in_db(workflow_id, video_id, success, transcript, error)
                    
                    # Update stats
                    if success:
                        self.stats['successful'] += 1
                        logger.info(f"  ✅ SUCCESS: {len(transcript)} chars in {end_time - start_time:.2f}s")
                    else:
                        self.stats['failed'] += 1
                        logger.warning(f"  ❌ FAILED: {error}")
                    
                except Exception as e:
                    self.stats['failed'] += 1
                    logger.error(f"  ❌ ERROR: {str(e)}")
                    self.update_transcript_in_db(workflow_id, video_id, False, None, str(e))
        
        self.stats['end_time'] = time.time()
        self._print_summary()
    
    def _print_summary(self):
        """Print processing summary."""
        total_time = self.stats['end_time'] - self.stats['start_time']
        success_rate = (self.stats['successful'] / self.stats['total'] * 100) if self.stats['total'] > 0 else 0
        avg_time = total_time / self.stats['total'] if self.stats['total'] > 0 else 0
        
        print("\n" + "=" * 70)
        print("BATCH TRANSCRIPT EXTRACTION COMPLETE")
        print("=" * 70)
        print(f"Total videos:     {self.stats['total']}")
        print(f"Successful:       {self.stats['successful']} ({success_rate:.1f}%)")
        print(f"Failed:           {self.stats['failed']}")
        print(f"Total time:       {total_time:.2f}s")
        print(f"Avg time/video:   {avg_time:.2f}s")
        print("=" * 70)


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Batch extract YouTube transcripts")
    parser.add_argument("--db-path", default="data/n8n_workflows.db", help="Path to database")
    parser.add_argument("--limit", type=int, help="Max number of videos to process")
    parser.add_argument("--visible", action="store_true", help="Run browser in visible mode")
    
    args = parser.parse_args()
    
    processor = TranscriptBatchProcessor(db_path=args.db_path)
    await processor.process_all_videos(limit=args.limit, headless=not args.visible)


if __name__ == "__main__":
    asyncio.run(main())


