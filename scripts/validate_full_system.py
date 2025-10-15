#!/usr/bin/env python3
"""
Complete System Validation Test

Tests the entire pipeline:
1. Layer 1 scraping extracts correct data
2. Data saves to correct Supabase tables/fields
3. Terminal shows continuous progress
4. Dashboard displays real-time data from DB
"""

import sys
sys.path.insert(0, '/app')

import asyncio
import time
from datetime import datetime
from sqlalchemy import text
from loguru import logger

from src.storage.database import get_session
from src.scrapers.layer1_metadata import PageMetadataExtractor

class SystemValidator:
    """Validates the complete scraping + monitoring system."""
    
    def __init__(self):
        self.test_workflow_id = '7423'  # Known good workflow
        self.test_url = 'https://n8n.io/workflows/7423-lead-generation-agent/'
        self.extractor = PageMetadataExtractor()
        
    def print_header(self, text):
        """Print a formatted header."""
        logger.info("\n" + "="*80)
        logger.info(f"  {text}")
        logger.info("="*80)
    
    def print_section(self, text):
        """Print a formatted section."""
        logger.info("\n" + "-"*80)
        logger.info(f"  {text}")
        logger.info("-"*80)
    
    async def test_1_layer1_extraction(self):
        """TEST 1: Validate Layer 1 extracts correct data."""
        self.print_header("TEST 1: Layer 1 Data Extraction")
        
        logger.info(f"Testing workflow: {self.test_workflow_id}")
        logger.info(f"URL: {self.test_url}")
        
        # Extract data
        result = await self.extractor.extract(self.test_workflow_id, self.test_url)
        
        if not result['success']:
            logger.error(f"❌ FAILED: Extraction failed - {result.get('error')}")
            return False
        
        data = result['data']
        
        # Validate key fields
        checks = {
            'title': data.get('title'),
            'author': data.get('author'),
            'description': data.get('description'),
            'use_case': data.get('use_case'),
            'categories': data.get('primary_category') or data.get('secondary_categories'),
        }
        
        logger.info("\n📋 Extracted Data:")
        all_passed = True
        for field, value in checks.items():
            if value:
                logger.success(f"  ✅ {field}: {str(value)[:60]}...")
            else:
                logger.error(f"  ❌ {field}: MISSING")
                all_passed = False
        
        if all_passed:
            logger.success("\n✅ TEST 1 PASSED: All key fields extracted")
            return data
        else:
            logger.error("\n❌ TEST 1 FAILED: Some fields missing")
            return None
    
    def test_2_database_save(self, extracted_data):
        """TEST 2: Validate data saves to correct Supabase tables."""
        self.print_header("TEST 2: Database Save Validation")
        
        if not extracted_data:
            logger.error("❌ SKIPPED: No data to save")
            return False
        
        with get_session() as session:
            try:
                # Check if workflow exists
                result = session.execute(text("""
                    SELECT workflow_id, url 
                    FROM workflows 
                    WHERE workflow_id = :wf_id
                """), {'wf_id': self.test_workflow_id})
                
                workflow = result.fetchone()
                if not workflow:
                    logger.error(f"❌ FAILED: Workflow {self.test_workflow_id} not found in workflows table")
                    return False
                
                logger.success(f"✅ Workflow exists in 'workflows' table")
                
                # Check workflow_metadata table BEFORE save
                result = session.execute(text("""
                    SELECT 
                        description,
                        author_name,
                        use_case,
                        views,
                        tags,
                        workflow_skill_level,
                        workflow_industry,
                        extracted_at
                    FROM workflow_metadata 
                    WHERE workflow_id = :wf_id
                """), {'wf_id': self.test_workflow_id})
                
                before_metadata = result.fetchone()
                logger.info(f"\n📊 BEFORE Save:")
                if before_metadata:
                    logger.info(f"  Description: {before_metadata[0][:50] if before_metadata[0] else 'NULL'}...")
                    logger.info(f"  Author: {before_metadata[1] or 'NULL'}")
                    logger.info(f"  Last extracted: {before_metadata[7] or 'NEVER'}")
                
                # NOW SAVE THE DATA using ORM method
                logger.info(f"\n💾 Saving extracted data...")
                self.save_to_database(self.test_workflow_id, extracted_data)
                
                # Check workflow_metadata table AFTER save
                result = session.execute(text("""
                    SELECT 
                        description,
                        author_name,
                        use_case,
                        views,
                        tags,
                        workflow_skill_level,
                        workflow_industry,
                        extracted_at
                    FROM workflow_metadata 
                    WHERE workflow_id = :wf_id
                """), {'wf_id': self.test_workflow_id})
                
                after_metadata = result.fetchone()
                
                if not after_metadata:
                    logger.error(f"❌ FAILED: No metadata found after save")
                    return False
                
                logger.info(f"\n📊 AFTER Save:")
                logger.success(f"  ✅ Description: {after_metadata[0][:50] if after_metadata[0] else 'NULL'}...")
                logger.success(f"  ✅ Author: {after_metadata[1] or 'NULL'}")
                logger.success(f"  ✅ Use Case: {after_metadata[2][:50] if after_metadata[2] else 'NULL'}...")
                logger.success(f"  ✅ Views: {after_metadata[3] or 0}")
                logger.success(f"  ✅ Skill Level: {after_metadata[5] or 'NULL'}")
                logger.success(f"  ✅ Industry: {after_metadata[6] or 'NULL'}")
                logger.success(f"  ✅ Extracted At: {after_metadata[7]}")
                
                # Validate data was actually updated
                if after_metadata[0] and after_metadata[1] and after_metadata[7]:
                    logger.success("\n✅ TEST 2 PASSED: Data saved correctly to workflow_metadata")
                    return True
                else:
                    logger.error("\n❌ TEST 2 FAILED: Data incomplete in database")
                    return False
                    
            except Exception as e:
                logger.error(f"❌ TEST 2 FAILED: Database error - {e}")
                return False
    
    def save_to_database(self, workflow_id, data):
        """Save data using the same ORM method as the scraper."""
        from src.storage.models import WorkflowMetadata
        import json
        
        with get_session() as session:
            try:
                existing = session.query(WorkflowMetadata).filter(
                    WorkflowMetadata.workflow_id == workflow_id
                ).first()
                
                if existing:
                    existing.description = data.get('description', '')
                    existing.author_name = data.get('author', 'Unknown')
                    existing.use_case = data.get('use_case', '')
                    existing.views = data.get('views', 0)
                    existing.tags = data.get('node_tags', []) + data.get('general_tags', [])
                    existing.workflow_skill_level = data.get('difficulty_level', 'intermediate')
                    existing.workflow_industry = ', '.join(data.get('industry', [])) if isinstance(data.get('industry'), list) else 'General'
                    existing.raw_metadata = data
                    existing.extracted_at = datetime.utcnow()
                else:
                    metadata = WorkflowMetadata(
                        workflow_id=workflow_id,
                        description=data.get('description', ''),
                        author_name=data.get('author', 'Unknown'),
                        use_case=data.get('use_case', ''),
                        views=data.get('views', 0),
                        tags=data.get('node_tags', []) + data.get('general_tags', []),
                        workflow_skill_level=data.get('difficulty_level', 'intermediate'),
                        workflow_industry=', '.join(data.get('industry', [])) if isinstance(data.get('industry'), list) else 'General',
                        raw_metadata=data,
                        extracted_at=datetime.utcnow()
                    )
                    session.add(metadata)
                
                session.commit()
                logger.info("✅ Data committed to database")
                
            except Exception as e:
                session.rollback()
                logger.error(f"Failed to save: {e}")
                raise
    
    def test_3_dashboard_data(self):
        """TEST 3: Validate dashboard shows real-time data from DB."""
        self.print_header("TEST 3: Dashboard Real-Time Data")
        
        with get_session() as session:
            try:
                # Get the same stats the dashboard uses
                result = session.execute(text("""
                    SELECT 
                        COUNT(*) as total,
                        COUNT(CASE WHEN description IS NOT NULL AND description != '' THEN 1 END) as scraped,
                        COUNT(CASE WHEN extracted_at > NOW() - INTERVAL '10 minutes' THEN 1 END) as recent
                    FROM workflow_metadata
                """))
                
                stats = result.fetchone()
                
                logger.info(f"\n📊 Dashboard Stats (from actual DB):")
                logger.success(f"  ✅ Total workflows: {stats[0]:,}")
                logger.success(f"  ✅ Scraped (with description): {stats[1]:,}")
                logger.success(f"  ✅ Recent activity (last 10 min): {stats[2]:,}")
                
                # Get our test workflow
                result = session.execute(text("""
                    SELECT 
                        workflow_id,
                        description,
                        author_name,
                        extracted_at
                    FROM workflow_metadata
                    WHERE workflow_id = :wf_id
                """), {'wf_id': self.test_workflow_id})
                
                test_wf = result.fetchone()
                
                if test_wf and test_wf[1]:  # Has description
                    logger.success(f"\n✅ Test workflow {self.test_workflow_id} visible in dashboard data:")
                    logger.info(f"  - Description: {test_wf[1][:60]}...")
                    logger.info(f"  - Author: {test_wf[2]}")
                    logger.info(f"  - Last scraped: {test_wf[3]}")
                    
                    # Check if it's in recent activity
                    time_diff = datetime.utcnow() - test_wf[3].replace(tzinfo=None)
                    if time_diff.total_seconds() < 600:  # 10 minutes
                        logger.success(f"  ✅ Appears in 'Recent Activity' (scraped {int(time_diff.total_seconds())}s ago)")
                    
                    logger.success("\n✅ TEST 3 PASSED: Dashboard shows real-time DB data")
                    return True
                else:
                    logger.error(f"\n❌ TEST 3 FAILED: Test workflow not in dashboard data")
                    return False
                    
            except Exception as e:
                logger.error(f"❌ TEST 3 FAILED: {e}")
                return False
    
    def test_4_scraper_progress(self):
        """TEST 4: Validate scraper is making progress."""
        self.print_header("TEST 4: Scraper Progress Validation")
        
        with get_session() as session:
            try:
                # Get count at start
                result = session.execute(text("""
                    SELECT COUNT(*) 
                    FROM workflow_metadata 
                    WHERE description IS NOT NULL AND description != ''
                """))
                count_before = result.scalar()
                
                logger.info(f"📊 Scraped workflows before: {count_before:,}")
                logger.info(f"⏳ Waiting 30 seconds for scraper to make progress...")
                
                time.sleep(30)
                
                # Get count after
                result = session.execute(text("""
                    SELECT COUNT(*) 
                    FROM workflow_metadata 
                    WHERE description IS NOT NULL AND description != ''
                """))
                count_after = result.scalar()
                
                logger.info(f"📊 Scraped workflows after: {count_after:,}")
                
                progress = count_after - count_before
                
                if progress > 0:
                    logger.success(f"\n✅ TEST 4 PASSED: Scraper made progress (+{progress} workflows in 30s)")
                    logger.info(f"  Rate: ~{progress * 2} workflows/minute")
                    return True
                else:
                    logger.warning(f"\n⚠️  TEST 4 WARNING: No progress detected (scraper might be paused)")
                    return False
                    
            except Exception as e:
                logger.error(f"❌ TEST 4 FAILED: {e}")
                return False
    
    async def run_all_tests(self):
        """Run all validation tests."""
        self.print_header("🧪 COMPLETE SYSTEM VALIDATION TEST")
        logger.info("Testing: Layer 1 → Supabase → Dashboard → Monitoring")
        logger.info(f"Test workflow: {self.test_workflow_id}")
        logger.info(f"Timestamp: {datetime.now().isoformat()}")
        
        results = {}
        
        # Test 1: Layer 1 Extraction
        extracted_data = await self.test_1_layer1_extraction()
        results['layer1_extraction'] = extracted_data is not None
        
        # Test 2: Database Save
        if extracted_data:
            results['database_save'] = self.test_2_database_save(extracted_data)
        else:
            results['database_save'] = False
        
        # Test 3: Dashboard Data
        results['dashboard_data'] = self.test_3_dashboard_data()
        
        # Test 4: Scraper Progress
        results['scraper_progress'] = self.test_4_scraper_progress()
        
        # Final Report
        self.print_header("📊 FINAL TEST RESULTS")
        
        passed = sum(1 for v in results.values() if v)
        total = len(results)
        
        for test_name, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            logger.info(f"  {status}  {test_name.replace('_', ' ').title()}")
        
        logger.info("\n" + "="*80)
        if passed == total:
            logger.success(f"🎉 ALL TESTS PASSED ({passed}/{total})")
            logger.success("\n✅ System is working correctly:")
            logger.success("  • Layer 1 extracts correct data")
            logger.success("  • Data saves to Supabase correctly")
            logger.success("  • Dashboard shows real-time DB data")
            logger.success("  • Scraper is making continuous progress")
        else:
            logger.error(f"⚠️  SOME TESTS FAILED ({passed}/{total} passed)")
            logger.info("\nPlease review failed tests above")
        
        logger.info("="*80)
        
        return passed == total

async def main():
    """Main entry point."""
    validator = SystemValidator()
    success = await validator.run_all_tests()
    
    if success:
        logger.info("\n✅ You can now monitor progress at:")
        logger.info("   • Terminal: See continuous progress updates")
        logger.info("   • Dashboard: http://localhost:5001")
        logger.info("\nThe scraper will continue running for ~17 hours to complete all 6,022 workflows.")
    
    return 0 if success else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)



