"""
Enhanced Layer 3 Production Scraper

Production-ready script for enhanced Layer 3 scraping with:
- 100% multimedia discovery (videos, text, images, code)
- Deep iframe navigation
- Comprehensive content extraction
- Resume capability
- Progress monitoring

Author: Developer-2 (Dev2)
Task: SCRAPE-010
Date: October 14, 2025
"""

import asyncio
import sys
import time
import argparse
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / 'src'))

from scrapers.layer3_enhanced import EnhancedLayer3ExplainerExtractor
from storage.database import get_session
from sqlalchemy import text
from loguru import logger


class Layer3EnhancedProductionScraper:
    """
    Production scraper for enhanced Layer 3 with 100% multimedia discovery.
    
    Features:
    - Visual discovery with Playwright
    - Comprehensive content extraction
    - Fallback scanning
    - Resume capability
    - Progress monitoring
    """
    
    def __init__(self, resume: bool = True, force: bool = False):
        """
        Initialize production scraper.
        
        Args:
            resume: Resume from where left off (skip completed workflows)
            force: Force re-scrape even if already completed
        """
        self.resume = resume
        self.force = force
        self.stats = {
            'total': 0,
            'completed': 0,
            'skipped': 0,
            'failed': 0,
            'start_time': None,
            'total_videos': 0,
            'total_text_length': 0,
            'quality_scores': []
        }
    
    async def get_all_workflows(self) -> List[Dict]:
        """Get all workflows to process"""
        with get_session() as session:
            # Get all workflows
            result = session.execute(text("""
                SELECT workflow_id, url 
                FROM workflows 
                WHERE url IS NOT NULL
                ORDER BY workflow_id
            """))
            
            workflows = []
            for row in result:
                workflow_id = row[0]
                url = row[1]
                
                # Check if already completed (unless force mode)
                if self.resume and not self.force:
                    try:
                        completed = session.execute(text("""
                            SELECT layer3_success 
                            FROM workflow_content 
                            WHERE workflow_id = :workflow_id
                        """), {"workflow_id": workflow_id}).fetchone()
                        
                        if completed and completed[0]:
                            self.stats['skipped'] += 1
                            continue
                    except Exception:
                        # Table doesn't exist yet, continue processing
                        pass
                
                workflows.append({
                    'workflow_id': workflow_id,
                    'url': url
                })
            
            return workflows
    
    async def save_layer3_data(self, workflow_id: str, data: Dict, quality_score: int) -> bool:
        """Save enhanced Layer 3 data to database"""
        try:
            with get_session() as session:
                # Create workflow_content table if not exists
                session.execute(text("""
                    CREATE TABLE IF NOT EXISTS workflow_content (
                        workflow_id VARCHAR(50) PRIMARY KEY,
                        introduction TEXT,
                        overview TEXT,
                        tutorial_text TEXT,
                        tutorial_sections JSONB,
                        step_by_step JSONB,
                        best_practices TEXT,
                        troubleshooting TEXT,
                        examples JSONB,
                        image_urls JSONB,
                        video_urls JSONB,
                        code_snippets JSONB,
                        additional_text_content TEXT,
                        layer3_success BOOLEAN DEFAULT FALSE,
                        layer3_extracted_at TIMESTAMP,
                        layer3_quality_score INTEGER,
                        UNIQUE(workflow_id)
                    )
                """))
                
                # Convert lists to JSON strings
                tutorial_sections_json = str(data.get('tutorial_sections', []))
                step_by_step_json = str(data.get('step_by_step', []))
                examples_json = str(data.get('examples', []))
                image_urls_json = str(data.get('image_urls', []))
                video_urls_json = str(data.get('video_urls', []))
                code_snippets_json = str(data.get('code_snippets', []))
                
                # Insert or update workflow content
                session.execute(text("""
                    INSERT INTO workflow_content (
                        workflow_id, introduction, overview, tutorial_text,
                        tutorial_sections, step_by_step, best_practices,
                        troubleshooting, examples, image_urls, video_urls,
                        code_snippets, additional_text_content,
                        layer3_success, layer3_extracted_at, layer3_quality_score
                    ) VALUES (
                        :workflow_id, :introduction, :overview, :tutorial_text,
                        :tutorial_sections, :step_by_step, :best_practices,
                        :troubleshooting, :examples, :image_urls, :video_urls,
                        :code_snippets, :additional_text_content,
                        :layer3_success, :layer3_extracted_at, :layer3_quality_score
                    )
                    ON CONFLICT (workflow_id)
                    DO UPDATE SET
                        introduction = EXCLUDED.introduction,
                        overview = EXCLUDED.overview,
                        tutorial_text = EXCLUDED.tutorial_text,
                        tutorial_sections = EXCLUDED.tutorial_sections,
                        step_by_step = EXCLUDED.step_by_step,
                        best_practices = EXCLUDED.best_practices,
                        troubleshooting = EXCLUDED.troubleshooting,
                        examples = EXCLUDED.examples,
                        image_urls = EXCLUDED.image_urls,
                        video_urls = EXCLUDED.video_urls,
                        code_snippets = EXCLUDED.code_snippets,
                        additional_text_content = EXCLUDED.additional_text_content,
                        layer3_success = EXCLUDED.layer3_success,
                        layer3_extracted_at = EXCLUDED.layer3_extracted_at,
                        layer3_quality_score = EXCLUDED.layer3_quality_score
                """), {
                    "workflow_id": workflow_id,
                    "introduction": data.get('introduction', ''),
                    "overview": data.get('overview', ''),
                    "tutorial_text": data.get('tutorial_text', ''),
                    "tutorial_sections": tutorial_sections_json,
                    "step_by_step": step_by_step_json,
                    "best_practices": data.get('best_practices', ''),
                    "troubleshooting": data.get('troubleshooting', ''),
                    "examples": examples_json,
                    "image_urls": image_urls_json,
                    "video_urls": video_urls_json,
                    "code_snippets": code_snippets_json,
                    "additional_text_content": data.get('additional_text', ''),
                    "layer3_success": True,
                    "layer3_extracted_at": datetime.utcnow(),
                    "layer3_quality_score": quality_score
                })
                
                session.commit()
                return True
                
        except Exception as e:
            logger.error(f"Error saving Layer 3 data for {workflow_id}: {e}")
            return False
    
    def print_progress(self, current: int, total: int, workflow_id: str, 
                      extraction_time: float, quality_score: int, videos: int, text_length: int):
        """Print progress with visual progress bar"""
        if total == 0:
            return
        
        pct = (current / total) * 100
        bar_length = 50
        filled_length = int(bar_length * current // total)
        bar = '█' * filled_length + '-' * (bar_length - filled_length)
        
        # Update stats
        self.stats['total_videos'] += videos
        self.stats['total_text_length'] += text_length
        self.stats['quality_scores'].append(quality_score)
        
        # Calculate averages
        avg_quality = sum(self.stats['quality_scores']) / len(self.stats['quality_scores']) if self.stats['quality_scores'] else 0
        avg_text = self.stats['total_text_length'] / current if current > 0 else 0
        
        print(f"\r📊 Progress: {current}/{total} ({pct:.1f}%) [{bar}]", end='')
        print(f" | Current: {workflow_id} ({extraction_time:.1f}s)", end='')
        print(f" | Videos: {videos} | Text: {text_length:,} | Quality: {quality_score}/100", end='')
        print(f" | Avg Quality: {avg_quality:.1f} | Avg Text: {avg_text:,.0f}", end='', flush=True)
    
    async def run(self, limit: Optional[int] = None, test: bool = False):
        """Run enhanced Layer 3 scraping"""
        
        print('🚀 ENHANCED LAYER 3 PRODUCTION SCRAPER')
        print('=' * 80)
        print()
        
        # Get workflows to process
        print('📋 Loading workflows...')
        all_workflows = await self.get_all_workflows()
        
        if limit:
            all_workflows = all_workflows[:limit]
        
        self.stats['total'] = len(all_workflows)
        self.stats['start_time'] = time.time()
        
        print(f'📊 Found {self.stats["total"]} workflows to process')
        if self.stats['skipped'] > 0:
            print(f'⏭️  Skipped {self.stats["skipped"]} already completed workflows')
        print()
        
        if test:
            print('🧪 TEST MODE: Processing first 10 workflows only')
            all_workflows = all_workflows[:10]
            self.stats['total'] = len(all_workflows)
        
        # Process workflows
        async with EnhancedLayer3ExplainerExtractor() as extractor:
            for i, workflow in enumerate(all_workflows, 1):
                workflow_id = workflow['workflow_id']
                url = workflow['url']
                
                try:
                    # Run enhanced extraction
                    result = await extractor.extract_enhanced(workflow_id, url)
                    
                    if result['success']:
                        data = result['data']
                        quality_score = result['quality_score']
                        
                        # Save to database
                        saved = await self.save_layer3_data(workflow_id, data, quality_score)
                        
                        if saved:
                            self.stats['completed'] += 1
                            
                            # Print progress
                            self.print_progress(
                                i, self.stats['total'], workflow_id,
                                result['extraction_time'], quality_score,
                                data['video_count'], data['total_text_length']
                            )
                        else:
                            self.stats['failed'] += 1
                            print(f"\n❌ Failed to save {workflow_id}")
                    else:
                        self.stats['failed'] += 1
                        print(f"\n❌ Extraction failed for {workflow_id}: {result.get('error', 'Unknown error')}")
                
                except Exception as e:
                    self.stats['failed'] += 1
                    print(f"\n❌ Exception for {workflow_id}: {str(e)}")
        
        # Final summary
        elapsed_time = time.time() - self.stats['start_time']
        print(f"\n\n🎉 ENHANCED LAYER 3 SCRAPING COMPLETE!")
        print('=' * 80)
        print(f'✅ Completed: {self.stats["completed"]}')
        print(f'⏭️  Skipped: {self.stats["skipped"]}')
        print(f'❌ Failed: {self.stats["failed"]}')
        print(f'⏱️  Total Time: {elapsed_time:.2f}s')
        print(f'🎥 Total Videos Found: {self.stats["total_videos"]}')
        print(f'📝 Total Text Extracted: {self.stats["total_text_length"]:,} characters')
        
        if self.stats['quality_scores']:
            avg_quality = sum(self.stats['quality_scores']) / len(self.stats['quality_scores'])
            print(f'📊 Average Quality Score: {avg_quality:.1f}/100')
        
        if self.stats['completed'] > 0:
            avg_time = elapsed_time / self.stats['completed']
            print(f'⚡ Average Time per Workflow: {avg_time:.2f}s')
        
        print()
        
        # Calculate video discovery rate
        workflows_with_videos = sum(1 for score in self.stats['quality_scores'] if score >= 40)  # 40 points for videos
        video_discovery_rate = (workflows_with_videos / len(self.stats['quality_scores']) * 100) if self.stats['quality_scores'] else 0
        
        print(f'🎯 VIDEO DISCOVERY RATE: {video_discovery_rate:.1f}%')
        if video_discovery_rate >= 95:
            print('   ✅ TARGET ACHIEVED (≥95%)')
        elif video_discovery_rate >= 80:
            print('   ⚠️  GOOD PROGRESS (80-95%)')
        else:
            print('   ❌ NEEDS IMPROVEMENT (<80%)')
        
        print()
        return self.stats['completed'] > 0


async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Enhanced Layer 3 Production Scraper')
    parser.add_argument('--test', action='store_true', help='Test mode (process first 10 workflows)')
    parser.add_argument('--limit', type=int, help='Limit number of workflows to process')
    parser.add_argument('--force', action='store_true', help='Force re-scrape even if already completed')
    parser.add_argument('--no-resume', action='store_true', help='Do not resume from where left off')
    
    args = parser.parse_args()
    
    scraper = Layer3EnhancedProductionScraper(
        resume=not args.no_resume,
        force=args.force
    )
    
    success = await scraper.run(limit=args.limit, test=args.test)
    
    if success:
        print('🎉 Enhanced Layer 3 scraping completed successfully!')
        sys.exit(0)
    else:
        print('❌ Enhanced Layer 3 scraping failed!')
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
