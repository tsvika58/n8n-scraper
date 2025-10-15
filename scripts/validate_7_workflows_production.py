#!/usr/bin/env python3
"""
Production Validation Script for 7 Video Workflows

Zero tolerance validation with:
- Database connection management
- Comprehensive error handling
- Real-time monitoring
- End-to-end validation
- DB viewer testing
"""

import os
import sys
import asyncio
import json
import time
import subprocess
from datetime import datetime
from dotenv import load_dotenv

# Add paths
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'n8n-shared'))

# The 7 test workflows with videos
TEST_WORKFLOWS = [
    ('6270', 'https://n8n.io/workflows/6270-build-your-first-ai-agent/'),
    ('8642', 'https://n8n.io/workflows/8642-generate-ai-viral-videos-with-veo-3-and-upload-to-tiktok/'),
    ('8527', 'https://n8n.io/workflows/8527-learn-n8n-basics-in-3-easy-steps/'),
    ('8237', 'https://n8n.io/workflows/8237-personal-life-manager-with-telegram-google-services-and-voice-enabled-ai/'),
    ('7639', 'https://n8n.io/workflows/7639-talk-to-your-google-sheets-using-chatgpt-5/'),
    ('5170', 'https://n8n.io/workflows/5170-learn-json-basics-with-an-interactive-step-by-step-tutorial-for-beginners/'),
    ('2462', 'https://n8n.io/workflows/2462-angie-personal-ai-assistant-with-telegram-voice-and-text/')
]

class ProductionValidator:
    def __init__(self):
        self.results = {
            'start_time': datetime.now().isoformat(),
            'database_connection': False,
            'scraping_results': {},
            'db_viewer_main': False,
            'db_viewer_details': {},
            'errors': [],
            'validation_passed': False
        }
    
    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime('%H:%M:%S')
        print(f"[{timestamp}] {level}: {message}")
    
    def error(self, message, exception=None):
        self.log(f"❌ {message}", "ERROR")
        if exception:
            self.log(f"   Exception: {str(exception)}", "ERROR")
        self.results['errors'].append({
            'message': message,
            'exception': str(exception) if exception else None,
            'timestamp': datetime.now().isoformat()
        })
    
    def success(self, message):
        self.log(f"✅ {message}", "SUCCESS")
    
    def validate_database_connection(self):
        """Validate database connection with zero tolerance."""
        self.log("🔍 Validating database connection...")
        try:
            from src.storage.database import get_session
            from n8n_shared.models import Workflow
            
            with get_session() as session:
                # Test basic connection
                count = session.query(Workflow).count()
                self.success(f"Database connected - {count} workflows found")
                
                # Test specific workflow queries
                for workflow_id, url in TEST_WORKFLOWS:
                    workflow = session.query(Workflow).filter_by(workflow_id=workflow_id).first()
                    if not workflow:
                        self.error(f"Workflow {workflow_id} not found in database")
                        return False
                
                self.results['database_connection'] = True
                return True
                
        except Exception as e:
            self.error("Database connection failed", e)
            return False
    
    async def validate_scraping(self):
        """Validate scraping with zero tolerance."""
        self.log("🎬 Validating scraping on 7 video workflows...")
        
        try:
            from src.scrapers.layer3_enhanced_v2 import EnhancedLayer3Extractor
            
            async with EnhancedLayer3Extractor(headless=True, extract_transcripts=True) as extractor:
                for workflow_id, url in TEST_WORKFLOWS:
                    self.log(f"📥 Processing {workflow_id}...")
                    
                    try:
                        result = await extractor.extract(workflow_id, url)
                        
                        if not result['success']:
                            self.error(f"Scraping failed for {workflow_id}: {result.get('error')}")
                            return False
                        
                        data = result['data']
                        video_count = data.get('video_count', 0)
                        transcript_count = data.get('transcript_count', 0)
                        content_length = data.get('content_length', 0)
                        quality_score = data.get('quality_score', 0)
                        
                        self.success(f"{workflow_id}: {video_count} videos, {transcript_count} transcripts, {content_length} chars, Q:{quality_score}")
                        
                        self.results['scraping_results'][workflow_id] = {
                            'success': True,
                            'video_count': video_count,
                            'transcript_count': transcript_count,
                            'content_length': content_length,
                            'quality_score': quality_score
                        }
                        
                        # Small delay between workflows
                        await asyncio.sleep(2)
                        
                    except Exception as e:
                        self.error(f"Exception during scraping of {workflow_id}", e)
                        return False
            
            return True
            
        except Exception as e:
            self.error("Scraping validation failed", e)
            return False
    
    def validate_database_save(self):
        """Validate data was saved to database."""
        self.log("💾 Validating database save...")
        
        try:
            from src.storage.database import get_session
            from n8n_shared.models import Workflow, WorkflowContent
            
            with get_session() as session:
                for workflow_id, url in TEST_WORKFLOWS:
                    # Check workflow table
                    workflow = session.query(Workflow).filter_by(workflow_id=workflow_id).first()
                    if not workflow or not workflow.layer3_success:
                        self.error(f"Workflow {workflow_id} not marked as L3 success in database")
                        return False
                    
                    # Check content table
                    content = session.query(WorkflowContent).filter_by(workflow_id=workflow_id).first()
                    if not content or not content.layer3_success:
                        self.error(f"WorkflowContent {workflow_id} not marked as L3 success in database")
                        return False
                    
                    # Validate content data
                    if not content.video_urls and not content.transcripts:
                        self.error(f"WorkflowContent {workflow_id} has no video URLs or transcripts")
                        return False
                    
                    self.success(f"Database save validated for {workflow_id}")
            
            return True
            
        except Exception as e:
            self.error("Database save validation failed", e)
            return False
    
    def validate_db_viewer_main(self):
        """Validate DB viewer main page."""
        self.log("🌐 Validating DB viewer main page...")
        
        try:
            # Test if DB viewer is running
            result = subprocess.run(['curl', '-s', '-o', '/dev/null', '-w', '%{http_code}', 'http://localhost:8080/workflows'], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode != 0 or result.stdout != '200':
                self.error(f"DB viewer not accessible: HTTP {result.stdout}")
                return False
            
            # Test specific workflow search
            for workflow_id, url in TEST_WORKFLOWS:
                search_result = subprocess.run(['curl', '-s', f'http://localhost:8080/workflows?search={workflow_id}'], 
                                             capture_output=True, text=True, timeout=10)
                
                if workflow_id not in search_result.stdout:
                    self.error(f"Workflow {workflow_id} not found on main page")
                    return False
            
            self.success("DB viewer main page validated")
            self.results['db_viewer_main'] = True
            return True
            
        except Exception as e:
            self.error("DB viewer main page validation failed", e)
            return False
    
    def validate_db_viewer_details(self):
        """Validate DB viewer detail pages."""
        self.log("📄 Validating DB viewer detail pages...")
        
        try:
            for workflow_id, url in TEST_WORKFLOWS:
                detail_result = subprocess.run(['curl', '-s', f'http://localhost:8080/workflow/{workflow_id}'], 
                                             capture_output=True, text=True, timeout=10)
                
                if detail_result.returncode != 0:
                    self.error(f"Detail page for {workflow_id} not accessible")
                    return False
                
                # Check for key content
                if 'Quality:' not in detail_result.stdout:
                    self.error(f"Quality score not displayed for {workflow_id}")
                    return False
                
                if 'Videos Found:' not in detail_result.stdout:
                    self.error(f"Video count not displayed for {workflow_id}")
                    return False
                
                self.success(f"Detail page validated for {workflow_id}")
                self.results['db_viewer_details'][workflow_id] = True
            
            return True
            
        except Exception as e:
            self.error("DB viewer detail pages validation failed", e)
            return False
    
    def generate_report(self):
        """Generate comprehensive validation report."""
        self.results['end_time'] = datetime.now().isoformat()
        self.results['validation_passed'] = len(self.results['errors']) == 0
        
        report = f"""
🎯 PRODUCTION VALIDATION REPORT
{'='*60}
Start Time: {self.results['start_time']}
End Time: {self.results['end_time']}
Validation Passed: {'✅ YES' if self.results['validation_passed'] else '❌ NO'}

📊 RESULTS:
- Database Connection: {'✅' if self.results['database_connection'] else '❌'}
- Scraping Results: {len(self.results['scraping_results'])}/{len(TEST_WORKFLOWS)} workflows
- DB Viewer Main: {'✅' if self.results['db_viewer_main'] else '❌'}
- DB Viewer Details: {len(self.results['db_viewer_details'])}/{len(TEST_WORKFLOWS)} workflows

📈 SCRAPING RESULTS:"""
        
        for workflow_id, result in self.results['scraping_results'].items():
            report += f"""
  {workflow_id}: {result['video_count']} videos, {result['transcript_count']} transcripts, Q:{result['quality_score']}"""
        
        if self.results['errors']:
            report += f"\n\n❌ ERRORS ({len(self.results['errors'])}):"
            for error in self.results['errors']:
                report += f"\n  - {error['message']}"
        
        report += f"\n\n{'='*60}"
        return report
    
    async def run_validation(self):
        """Run complete validation with zero tolerance."""
        self.log("🚀 Starting Production Validation with Zero Tolerance")
        self.log("="*60)
        
        # Step 1: Database Connection
        if not self.validate_database_connection():
            self.log("❌ VALIDATION FAILED: Database connection")
            return False
        
        # Step 2: Scraping
        if not await self.validate_scraping():
            self.log("❌ VALIDATION FAILED: Scraping")
            return False
        
        # Step 3: Database Save
        if not self.validate_database_save():
            self.log("❌ VALIDATION FAILED: Database save")
            return False
        
        # Step 4: DB Viewer Main
        if not self.validate_db_viewer_main():
            self.log("❌ VALIDATION FAILED: DB viewer main page")
            return False
        
        # Step 5: DB Viewer Details
        if not self.validate_db_viewer_details():
            self.log("❌ VALIDATION FAILED: DB viewer detail pages")
            return False
        
        # All validations passed
        self.log("🎉 ALL VALIDATIONS PASSED - PRODUCTION READY!")
        return True

async def main():
    """Main validation function."""
    validator = ProductionValidator()
    
    try:
        success = await validator.run_validation()
        
        # Generate and save report
        report = validator.generate_report()
        print(report)
        
        # Save report to file
        with open('validation_report.json', 'w') as f:
            json.dump(validator.results, f, indent=2)
        
        with open('validation_report.txt', 'w') as f:
            f.write(report)
        
        if success:
            print("\n✅ PRODUCTION VALIDATION COMPLETE - READY FOR FULL SCRAPING")
            sys.exit(0)
        else:
            print("\n❌ PRODUCTION VALIDATION FAILED - FIX ISSUES BEFORE PROCEEDING")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n💥 CRITICAL ERROR: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
