"""
Layer 3 Comprehensive Production Scraper

Production-ready scraper with:
- Built-in test mode (10 workflows)
- Database validation mode
- Resume capability
- Error recovery
- Progress monitoring
- Quality validation

Author: Developer-2 (Dev2)
Task: SCRAPE-010
Date: October 14, 2025
"""

import asyncio
import sys
import time
import argparse
import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / 'src'))

from scrapers.layer3_comprehensive import ComprehensiveLayer3Extractor
from storage.database import get_session
from sqlalchemy import text
from loguru import logger


class Layer3ProductionScraper:
    """
    Production scraper with test/validation modes.
    
    Modes:
    - Test Mode: Run on 10 workflows, validate everything
    - Validation Mode: Test database save/load
    - Production Mode: Full 6,000+ workflow run
    """
    
    def __init__(
        self,
        resume: bool = True,
        force: bool = False,
        extract_transcripts: bool = True
    ):
        """
        Initialize production scraper.
        
        Args:
            resume: Skip already completed workflows
            force: Force re-scrape even if completed
            extract_transcripts: Extract video transcripts
        """
        self.resume = resume
        self.force = force
        self.extract_transcripts = extract_transcripts
        self.stats = {
            'total': 0,
            'completed': 0,
            'skipped': 0,
            'failed': 0,
            'start_time': None,
            'total_videos': 0,
            'total_transcripts': 0,
            'total_text_length': 0,
            'quality_scores': []
        }
    
    async def get_workflows(self, limit: Optional[int] = None) -> List[Dict]:
        """Get workflows to process"""
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
                        # Table doesn't exist or column missing, continue
                        pass
                
                workflows.append({
                    'workflow_id': workflow_id,
                    'url': url
                })
                
                if limit and len(workflows) >= limit:
                    break
            
            return workflows
    
    async def save_to_database(self, result: Dict) -> bool:
        """
        Save comprehensive extraction results to database.
        
        Args:
            result: Extraction result from ComprehensiveLayer3Extractor
            
        Returns:
            bool: True if saved successfully
        """
        if not result.get('success'):
            return False
        
        workflow_id = result['workflow_id']
        final_data = result['final_data']
        metadata = result['metadata']
        passes = result['extraction_passes']
        
        try:
            with get_session() as session:
                # Prepare data for database
                save_data = {
                    'workflow_id': workflow_id,
                    
                    # Video data
                    'video_urls': final_data.get('video_urls', []),
                    'video_metadata': json.dumps(final_data.get('videos', [])),
                    'video_count': len(final_data.get('videos', [])),
                    'has_videos': len(final_data.get('videos', [])) > 0,
                    
                    # Transcript data
                    'transcripts': json.dumps(final_data.get('transcripts', {})),
                    'transcript_count': len(final_data.get('transcripts', {})),
                    'has_transcripts': len(final_data.get('transcripts', {})) > 0,
                    
                    # Content data
                    'content_text': final_data.get('text_content', ''),
                    'content_html': passes.get('pass2_dom', {}).get('complete_html', ''),
                    'total_text_length': final_data.get('total_text_length', 0),
                    
                    # Media data
                    'image_urls': [img.get('src', '') for img in final_data.get('images', [])],
                    'image_count': len(final_data.get('images', [])),
                    'link_urls': [link.get('href', '') for link in final_data.get('all_links', [])],
                    'link_count': len(final_data.get('all_links', [])),
                    
                    # Iframe data
                    'iframe_sources': [iframe.get('src', '') for iframe in final_data.get('iframes', [])],
                    'iframe_count': len(final_data.get('iframes', [])),
                    'has_iframes': len(final_data.get('iframes', [])) > 0,
                    'iframe_content': json.dumps(passes.get('pass2_dom', {}).get('iframes_complete', [])),
                    
                    # Meta data
                    'meta_tags': json.dumps(final_data.get('meta_tags', {})),
                    
                    # Extraction metadata
                    'extraction_passes': json.dumps(passes),
                    'deduplication_stats': json.dumps(
                        passes.get('pass4_videos', {}).get('deduplication_stats', {})
                    ),
                    'quality_score': result.get('quality_score', 0),
                    
                    # Validation data
                    'content_hash': passes.get('pass5_validation', {}).get('content_hash', ''),
                    'screenshot_path': passes.get('pass5_validation', {}).get('screenshot_path', ''),
                    'validation_data': json.dumps(passes.get('pass5_validation', {})),
                    
                    # Status
                    'layer3_success': True,
                    'layer3_extracted_at': datetime.utcnow(),
                    'layer3_version': metadata.get('extractor_version', '3.0.0-comprehensive')
                }
                
                # Insert or update
                session.execute(text("""
                    INSERT INTO workflow_content (
                        workflow_id, video_urls, video_metadata, video_count, has_videos,
                        transcripts, transcript_count, has_transcripts,
                        content_text, content_html, total_text_length,
                        image_urls, image_count, link_urls, link_count,
                        iframe_sources, iframe_count, has_iframes, iframe_content,
                        meta_tags, extraction_passes, deduplication_stats, quality_score,
                        content_hash, screenshot_path, validation_data,
                        layer3_success, layer3_extracted_at, layer3_version
                    ) VALUES (
                        :workflow_id, :video_urls, :video_metadata, :video_count, :has_videos,
                        :transcripts, :transcript_count, :has_transcripts,
                        :content_text, :content_html, :total_text_length,
                        :image_urls, :image_count, :link_urls, :link_count,
                        :iframe_sources, :iframe_count, :has_iframes, :iframe_content,
                        :meta_tags, :extraction_passes, :deduplication_stats, :quality_score,
                        :content_hash, :screenshot_path, :validation_data,
                        :layer3_success, :layer3_extracted_at, :layer3_version
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
                        content_html = EXCLUDED.content_html,
                        total_text_length = EXCLUDED.total_text_length,
                        image_urls = EXCLUDED.image_urls,
                        image_count = EXCLUDED.image_count,
                        link_urls = EXCLUDED.link_urls,
                        link_count = EXCLUDED.link_count,
                        iframe_sources = EXCLUDED.iframe_sources,
                        iframe_count = EXCLUDED.iframe_count,
                        has_iframes = EXCLUDED.has_iframes,
                        iframe_content = EXCLUDED.iframe_content,
                        meta_tags = EXCLUDED.meta_tags,
                        extraction_passes = EXCLUDED.extraction_passes,
                        deduplication_stats = EXCLUDED.deduplication_stats,
                        quality_score = EXCLUDED.quality_score,
                        content_hash = EXCLUDED.content_hash,
                        screenshot_path = EXCLUDED.screenshot_path,
                        validation_data = EXCLUDED.validation_data,
                        layer3_success = EXCLUDED.layer3_success,
                        layer3_extracted_at = EXCLUDED.layer3_extracted_at,
                        layer3_version = EXCLUDED.layer3_version
                """), save_data)
                
                session.commit()
                
                logger.info(f"Saved Layer 3 data for workflow {workflow_id}")
                return True
                
        except Exception as e:
            logger.error(f"Error saving Layer 3 data for {workflow_id}: {e}")
            return False
    
    async def validate_database_save(self, workflow_id: str, original_result: Dict) -> bool:
        """
        Validate that saved data matches original extraction.
        
        Args:
            workflow_id: Workflow ID to validate
            original_result: Original extraction result
            
        Returns:
            bool: True if validation passed
        """
        try:
            with get_session() as session:
                # Read back from database
                result = session.execute(text("""
                    SELECT 
                        video_urls, video_count, has_videos,
                        transcript_count, has_transcripts,
                        total_text_length, quality_score,
                        layer3_success
                    FROM workflow_content
                    WHERE workflow_id = :workflow_id
                """), {"workflow_id": workflow_id}).fetchone()
                
                if not result:
                    logger.error(f"Validation failed: No data found for {workflow_id}")
                    return False
                
                # Validate key fields
                original_data = original_result['final_data']
                
                validations = {
                    'video_count': len(result[0]) if result[0] else 0 == len(original_data.get('video_urls', [])),
                    'has_videos': result[2] == (len(original_data.get('videos', [])) > 0),
                    'transcript_count': result[3] == len(original_data.get('transcripts', {})),
                    'has_transcripts': result[4] == (len(original_data.get('transcripts', {})) > 0),
                    'total_text_length': result[5] == original_data.get('total_text_length', 0),
                    'quality_score': result[6] == original_result.get('quality_score', 0),
                    'layer3_success': result[7] == True
                }
                
                all_valid = all(validations.values())
                
                if all_valid:
                    logger.info(f"✅ Validation passed for {workflow_id}")
                else:
                    failed = [k for k, v in validations.items() if not v]
                    logger.warning(f"⚠️  Validation failed for {workflow_id}: {failed}")
                
                return all_valid
                
        except Exception as e:
            logger.error(f"Validation error for {workflow_id}: {e}")
            return False
    
    def print_progress(self, current: int, total: int, workflow_id: str, 
                      extraction_time: float, quality_score: int):
        """Print progress with visual progress bar"""
        if total == 0:
            return
        
        pct = (current / total) * 100
        bar_length = 50
        filled_length = int(bar_length * current // total)
        bar = '█' * filled_length + '-' * (bar_length - filled_length)
        
        print(f"\r📊 [{bar}] {current}/{total} ({pct:.1f}%)", end='')
        print(f" | {workflow_id} ({extraction_time:.1f}s, Q:{quality_score}/100)", end='', flush=True)
    
    async def run_test_mode(self) -> bool:
        """
        Run test mode: 10 workflows with full validation.
        
        Returns:
            bool: True if all tests passed
        """
        print('🧪 TEST MODE: Running on 10 workflows with validation')
        print('=' * 80)
        print()
        
        # Get 10 workflows
        workflows = await self.get_workflows(limit=10)
        
        if len(workflows) < 10:
            print(f'⚠️  Only {len(workflows)} workflows available (need 10 for full test)')
        
        print(f'📋 Testing {len(workflows)} workflows')
        print()
        
        test_results = {
            'extraction_passed': 0,
            'save_passed': 0,
            'validation_passed': 0,
            'failed': []
        }
        
        async with ComprehensiveLayer3Extractor(extract_transcripts=self.extract_transcripts) as extractor:
            for i, workflow in enumerate(workflows, 1):
                workflow_id = workflow['workflow_id']
                url = workflow['url']
                
                print(f'\n🔍 Test {i}/{len(workflows)}: Workflow {workflow_id}')
                
                try:
                    # Step 1: Extract
                    print('   Step 1/3: Extracting...')
                    result = await extractor.extract_comprehensive(workflow_id, url)
                    
                    if result['success']:
                        test_results['extraction_passed'] += 1
                        print(f'   ✅ Extraction: {result["quality_score"]}/100 quality')
                    else:
                        print(f'   ❌ Extraction failed: {result.get("error")}')
                        test_results['failed'].append((workflow_id, 'extraction', result.get('error')))
                        continue
                    
                    # Step 2: Save to database
                    print('   Step 2/3: Saving to database...')
                    saved = await self.save_to_database(result)
                    
                    if saved:
                        test_results['save_passed'] += 1
                        print('   ✅ Database save successful')
                    else:
                        print('   ❌ Database save failed')
                        test_results['failed'].append((workflow_id, 'save', 'Database save failed'))
                        continue
                    
                    # Step 3: Validate
                    print('   Step 3/3: Validating...')
                    validated = await self.validate_database_save(workflow_id, result)
                    
                    if validated:
                        test_results['validation_passed'] += 1
                        print('   ✅ Validation passed')
                    else:
                        print('   ⚠️  Validation failed (data mismatch)')
                        test_results['failed'].append((workflow_id, 'validation', 'Data mismatch'))
                    
                except Exception as e:
                    print(f'   ❌ Test failed: {str(e)}')
                    test_results['failed'].append((workflow_id, 'exception', str(e)))
        
        # Print test summary
        print()
        print('=' * 80)
        print('🧪 TEST MODE RESULTS')
        print('=' * 80)
        print()
        print(f'✅ Extraction:  {test_results["extraction_passed"]}/{len(workflows)} passed')
        print(f'✅ Save:        {test_results["save_passed"]}/{len(workflows)} passed')
        print(f'✅ Validation:  {test_results["validation_passed"]}/{len(workflows)} passed')
        print()
        
        if test_results['failed']:
            print(f'❌ Failed:      {len(test_results["failed"])} failures')
            print()
            print('Failed workflows:')
            for wf_id, stage, error in test_results['failed']:
                print(f'   - {wf_id}: {stage} - {error[:50]}...')
            print()
        
        all_passed = (
            test_results['extraction_passed'] == len(workflows) and
            test_results['save_passed'] == len(workflows) and
            test_results['validation_passed'] == len(workflows)
        )
        
        if all_passed:
            print('🎉 ALL TESTS PASSED!')
            print()
            print('✅ Ready for production run!')
            print()
            return True
        else:
            print('❌ SOME TESTS FAILED')
            print()
            print('⚠️  Fix issues before production run')
            print()
            return False
    
    async def run_production(self, limit: Optional[int] = None) -> bool:
        """
        Run production mode: Full workflow scraping.
        
        Args:
            limit: Optional limit on number of workflows
            
        Returns:
            bool: True if completed successfully
        """
        print('🚀 PRODUCTION MODE: Full Layer 3 Comprehensive Scraping')
        print('=' * 80)
        print()
        
        # Get workflows
        print('📋 Loading workflows...')
        workflows = await self.get_workflows(limit=limit)
        
        self.stats['total'] = len(workflows)
        self.stats['start_time'] = time.time()
        
        print(f'📊 Found {self.stats["total"]} workflows to process')
        if self.stats['skipped'] > 0:
            print(f'⏭️  Skipped {self.stats["skipped"]} already completed workflows')
        print()
        
        # Process workflows
        async with ComprehensiveLayer3Extractor(extract_transcripts=self.extract_transcripts) as extractor:
            for i, workflow in enumerate(workflows, 1):
                workflow_id = workflow['workflow_id']
                url = workflow['url']
                
                try:
                    # Extract
                    result = await extractor.extract_comprehensive(workflow_id, url)
                    
                    if result['success']:
                        # Save to database
                        saved = await self.save_to_database(result)
                        
                        if saved:
                            self.stats['completed'] += 1
                            self.stats['total_videos'] += len(result['final_data'].get('videos', []))
                            self.stats['total_transcripts'] += len(result['final_data'].get('transcripts', {}))
                            self.stats['total_text_length'] += result['final_data'].get('total_text_length', 0)
                            self.stats['quality_scores'].append(result.get('quality_score', 0))
                            
                            # Print progress
                            self.print_progress(
                                i, self.stats['total'], workflow_id,
                                result['metadata']['extraction_time'],
                                result['quality_score']
                            )
                        else:
                            self.stats['failed'] += 1
                            print(f"\n❌ Failed to save {workflow_id}")
                    else:
                        self.stats['failed'] += 1
                        print(f"\n❌ Extraction failed for {workflow_id}: {result.get('error')}")
                
                except Exception as e:
                    self.stats['failed'] += 1
                    print(f"\n❌ Exception for {workflow_id}: {str(e)}")
        
        # Final summary
        elapsed_time = time.time() - self.stats['start_time']
        print(f"\n\n🎉 PRODUCTION SCRAPING COMPLETE!")
        print('=' * 80)
        print(f'✅ Completed:        {self.stats["completed"]}')
        print(f'⏭️  Skipped:          {self.stats["skipped"]}')
        print(f'❌ Failed:           {self.stats["failed"]}')
        print(f'⏱️  Total Time:       {elapsed_time/3600:.2f} hours')
        print(f'🎥 Videos Found:     {self.stats["total_videos"]}')
        print(f'📝 Transcripts:      {self.stats["total_transcripts"]}')
        print(f'📊 Text Extracted:   {self.stats["total_text_length"]:,} chars')
        
        if self.stats['quality_scores']:
            avg_quality = sum(self.stats['quality_scores']) / len(self.stats['quality_scores'])
            print(f'📊 Avg Quality:      {avg_quality:.1f}/100')
        
        if self.stats['completed'] > 0:
            avg_time = elapsed_time / self.stats['completed']
            print(f'⚡ Avg Time/WF:      {avg_time:.2f}s')
        
        print()
        
        return self.stats['completed'] > 0


async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Layer 3 Comprehensive Production Scraper',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Test mode (10 workflows with validation)
  python layer3_production_scraper.py --test
  
  # Production mode (limited)
  python layer3_production_scraper.py --limit 100
  
  # Full production run
  python layer3_production_scraper.py
  
  # Force re-scrape
  python layer3_production_scraper.py --force --limit 10
        """
    )
    
    parser.add_argument('--test', action='store_true', 
                       help='Test mode: Run on 10 workflows with validation')
    parser.add_argument('--limit', type=int, 
                       help='Limit number of workflows to process')
    parser.add_argument('--force', action='store_true', 
                       help='Force re-scrape even if already completed')
    parser.add_argument('--no-resume', action='store_true', 
                       help='Do not resume from where left off')
    parser.add_argument('--no-transcripts', action='store_true',
                       help='Skip transcript extraction (faster)')
    
    args = parser.parse_args()
    
    scraper = Layer3ProductionScraper(
        resume=not args.no_resume,
        force=args.force,
        extract_transcripts=not args.no_transcripts
    )
    
    if args.test:
        # Test mode
        success = await scraper.run_test_mode()
    else:
        # Production mode
        success = await scraper.run_production(limit=args.limit)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())
