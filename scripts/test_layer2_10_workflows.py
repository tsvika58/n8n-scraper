#!/usr/bin/env python3
"""
Test Layer 2 Enhanced on 10 workflows with full monitoring.
"""

import asyncio
import sys
import os
import psycopg2
import json
from datetime import datetime, timedelta
from time import time
from loguru import logger

sys.path.insert(0, '/Users/tsvikavagman/Desktop/Code Projects/shared-tools/n8n-scraper')

from src.scrapers.layer2_enhanced import EnhancedLayer2Extractor

# Configure logger (clean format like Layer 1)
logger.remove()
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
    level="INFO"
)

# Database credentials
DB_HOST = "aws-1-eu-north-1.pooler.supabase.com"
DB_PORT = "5432"
DB_NAME = "postgres"
DB_USER = "postgres.skduopoakfeaurttcaip"
DB_PASSWORD = "crg3pjm8ych4ctu@KXT"


class Layer2TestRunner:
    """Test runner for 10 workflows."""
    
    def __init__(self):
        self.start_time = None
        self.processed = 0
        self.successful = 0
        self.failed = 0
        self.total_workflows = 10
        self.extraction_times = []
        self.errors = []
    
    def get_test_workflows(self):
        """Get 10 workflows for testing."""
        
        try:
            conn = psycopg2.connect(
                host=DB_HOST,
                port=DB_PORT,
                database=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD,
                sslmode='require'
            )
            
            cursor = conn.cursor()
            
            # Get 10 workflows that need Layer 2
            cursor.execute("""
                SELECT w.workflow_id, w.url
                FROM workflows w
                WHERE (w.layer2_success IS NULL OR w.layer2_success = false)
                ORDER BY w.workflow_id::integer ASC
                LIMIT 10;
            """)
            
            workflows = cursor.fetchall()
            
            cursor.close()
            conn.close()
            
            return workflows
            
        except Exception as e:
            logger.error(f"Error fetching workflows: {e}")
            return []
    
    def store_to_database(self, workflow_id, result):
        """Store extraction result to Supabase."""
        
        try:
            conn = psycopg2.connect(
                host=DB_HOST,
                port=DB_PORT,
                database=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD,
                sslmode='require'
            )
            
            cursor = conn.cursor()
            
            # Prepare data
            api_data = result['sources']['api']
            iframe_data = result['sources']['iframe']
            
            # Extract node types
            nodes = api_data.get('data', {}).get('workflow', {}).get('nodes', [])
            node_types = list(set(node.get('type') for node in nodes if node.get('type')))
            
            # Insert/Update workflow_structure
            cursor.execute("""
                INSERT INTO workflow_structure (
                    workflow_id, node_count, connection_count, node_types,
                    extraction_type, fallback_used, workflow_json,
                    iframe_data, visual_layout, enhanced_content, media_content,
                    extraction_sources, completeness_metrics, extracted_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (workflow_id) DO UPDATE SET
                    node_count = EXCLUDED.node_count,
                    connection_count = EXCLUDED.connection_count,
                    node_types = EXCLUDED.node_types,
                    extraction_type = EXCLUDED.extraction_type,
                    fallback_used = EXCLUDED.fallback_used,
                    workflow_json = EXCLUDED.workflow_json,
                    iframe_data = EXCLUDED.iframe_data,
                    visual_layout = EXCLUDED.visual_layout,
                    enhanced_content = EXCLUDED.enhanced_content,
                    media_content = EXCLUDED.media_content,
                    extraction_sources = EXCLUDED.extraction_sources,
                    completeness_metrics = EXCLUDED.completeness_metrics,
                    extracted_at = EXCLUDED.extracted_at;
            """, (
                workflow_id,
                api_data.get('node_count'),
                api_data.get('connection_count'),
                json.dumps(node_types),
                api_data.get('extraction_type', 'full'),
                api_data.get('fallback_used', False),
                json.dumps(api_data.get('data')),
                json.dumps(iframe_data.get('nodes')),
                json.dumps(iframe_data.get('visual_layout')),
                json.dumps(iframe_data.get('enhanced_content')),
                json.dumps(iframe_data.get('media_content')),
                json.dumps({'api': api_data.get('success'), 'iframe': iframe_data.get('success')}),
                json.dumps(result.get('completeness')),
                datetime.utcnow()
            ))
            
            # Update layer2_success flag in workflows table
            cursor.execute("""
                UPDATE workflows 
                SET layer2_success = true, 
                    extracted_at = %s
                WHERE workflow_id = %s
            """, (datetime.utcnow(), workflow_id))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            return True
            
        except Exception as e:
            logger.error(f"Storage error: {e}")
            return False
    
    def print_progress(self):
        """Print progress dashboard."""
        
        elapsed = time() - self.start_time
        progress_pct = (self.processed / self.total_workflows) * 100
        
        # Calculate ETA
        if self.processed > 0:
            avg_time = elapsed / self.processed
            remaining = self.total_workflows - self.processed
            eta_seconds = remaining * avg_time
            eta_minutes = int(eta_seconds // 60)
            eta_seconds = int(eta_seconds % 60)
            eta = f"{eta_minutes}m {eta_seconds}s"
        else:
            eta = "calculating..."
        
        # Progress bar
        bar_length = 50
        filled = int(bar_length * self.processed / self.total_workflows)
        bar = '█' * filled + '░' * (bar_length - filled)
        
        # Format elapsed time
        elapsed_minutes = int(elapsed // 60)
        elapsed_seconds = int(elapsed % 60)
        elapsed_str = f"{elapsed_minutes}m {elapsed_seconds}s"
        
        # Average extraction time
        avg_extraction = sum(self.extraction_times) / len(self.extraction_times) if self.extraction_times else 0
        
        logger.info("="*80)
        logger.info(f"📊 PROGRESS: {self.processed}/{self.total_workflows} ({progress_pct:.1f}%)")
        logger.info(f"[{bar}]")
        logger.info(f"✅ Success: {self.successful} | ❌ Failed: {self.failed}")
        logger.info(f"⏱️  Elapsed: {elapsed_str} | ETA: {eta}")
        logger.info(f"⚡ Speed: {avg_extraction:.1f}s per workflow")
        logger.info("="*80)
    
    async def process_workflow(self, extractor, workflow_id, url, index):
        """Process a single workflow."""
        
        try:
            # Extract
            result = await extractor.extract_complete(workflow_id, url)
            
            # Store
            stored = self.store_to_database(workflow_id, result)
            
            # Track
            self.processed += 1
            if result['completeness']['merged'] == 100.0 and stored:
                self.successful += 1
                self.extraction_times.append(result['extraction_time'])
            else:
                self.failed += 1
                self.errors.append({
                    'workflow_id': workflow_id,
                    'error': 'Storage failed' if not stored else 'Incomplete extraction'
                })
            
            # Print progress after EVERY workflow
            self.print_progress()
            
            return True
            
        except Exception as e:
            self.processed += 1
            self.failed += 1
            self.errors.append({
                'workflow_id': workflow_id,
                'error': str(e)
            })
            logger.error(f"Error: {e}")
            
            # Still print progress
            self.print_progress()
            
            return False
    
    async def run(self):
        """Run test on 10 workflows."""
        
        logger.info("="*80)
        logger.info("🧪 LAYER 2 ENHANCED - TEST RUN (10 WORKFLOWS)")
        logger.info("="*80)
        
        # Get workflows
        workflows = self.get_test_workflows()
        
        if not workflows:
            logger.warning("⚠️  No workflows found to test!")
            return
        
        logger.info(f"✅ Found {len(workflows)} workflows to test")
        logger.info("")
        
        self.total_workflows = len(workflows)
        self.start_time = time()
        
        # Process workflows
        async with EnhancedLayer2Extractor() as extractor:
            for i, (workflow_id, url) in enumerate(workflows, 1):
                await self.process_workflow(extractor, workflow_id, url, i)
                
                # Rate limiting
                if i < len(workflows):
                    await asyncio.sleep(2)
        
        # Final summary
        elapsed = time() - self.start_time
        elapsed_minutes = int(elapsed // 60)
        elapsed_seconds = int(elapsed % 60)
        elapsed_str = f"{elapsed_minutes}m {elapsed_seconds}s"
        
        logger.info("")
        logger.info("="*80)
        logger.info("📊 TEST COMPLETE")
        logger.info("="*80)
        logger.info(f"Total: {self.total_workflows} | Success: {self.successful} | Failed: {self.failed}")
        logger.info(f"Time: {elapsed_str} | Avg: {sum(self.extraction_times)/len(self.extraction_times):.1f}s per workflow" if self.extraction_times else f"Time: {elapsed_str}")
        logger.info("="*80)


async def main():
    """Main entry point."""
    runner = Layer2TestRunner()
    await runner.run()


if __name__ == "__main__":
    asyncio.run(main())




