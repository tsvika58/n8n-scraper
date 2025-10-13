#!/usr/bin/env python3
"""
Layer 2 Enhanced - Production Scraper
Processes all workflows from Layer 1 with full monitoring.
"""

import asyncio
import sys
import os
import psycopg2
import json
from datetime import datetime, timedelta
from time import time

sys.path.insert(0, '/Users/tsvikavagman/Desktop/Code Projects/shared-tools/n8n-scraper')

from src.scrapers.layer2_enhanced import EnhancedLayer2Extractor

# Database credentials
DB_HOST = "aws-1-eu-north-1.pooler.supabase.com"
DB_PORT = "5432"
DB_NAME = "postgres"
DB_USER = "postgres.skduopoakfeaurttcaip"
DB_PASSWORD = "crg3pjm8ych4ctu@KXT"


class Layer2ProductionRunner:
    """Production runner for Layer 2 Enhanced with monitoring."""
    
    def __init__(self):
        self.start_time = None
        self.processed = 0
        self.successful = 0
        self.failed = 0
        self.total_workflows = 0
        self.extraction_times = []
        self.errors = []
    
    def get_workflows_to_process(self):
        """Get workflows that need Layer 2 processing."""
        
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
            
            # Get workflows from Layer 1 that don't have Layer 2 Enhanced data yet
            cursor.execute("""
                SELECT w.workflow_id, w.url
                FROM workflows w
                LEFT JOIN workflow_structure ws ON w.workflow_id = ws.workflow_id
                WHERE ws.iframe_data IS NULL
                ORDER BY w.extracted_at ASC;
            """)
            
            workflows = cursor.fetchall()
            
            cursor.close()
            conn.close()
            
            return workflows
            
        except Exception as e:
            print(f"❌ Error fetching workflows: {e}")
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
            
            # Insert/Update
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
                SET layer2_success = true, extracted_at = %s
                WHERE workflow_id = %s
            """, (datetime.utcnow(), workflow_id))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            return True
            
        except Exception as e:
            print(f"      ❌ Storage error: {e}")
            return False
    
    def print_progress(self):
        """Print progress bar (Layer 1 style)."""
        
        if self.total_workflows == 0:
            return
        
        elapsed = time() - self.start_time
        progress_pct = (self.processed / self.total_workflows) * 100
        
        # Calculate ETA
        if self.processed > 0:
            avg_time = elapsed / self.processed
            remaining = self.total_workflows - self.processed
            eta_seconds = remaining * avg_time
            eta = str(timedelta(seconds=int(eta_seconds)))
        else:
            eta = "calculating..."
        
        # Progress bar
        bar_length = 50
        filled = int(bar_length * self.processed / self.total_workflows)
        bar = '█' * filled + '░' * (bar_length - filled)
        
        # Format elapsed time
        elapsed_str = str(timedelta(seconds=int(elapsed)))
        
        # Average extraction time
        avg_extraction = sum(self.extraction_times) / len(self.extraction_times) if self.extraction_times else 0
        
        print("\n" + "="*80)
        print(f"📊 PROGRESS: {self.processed}/{self.total_workflows} ({progress_pct:.1f}%)")
        print(f"[{bar}]")
        print(f"✅ Success: {self.successful} | ❌ Failed: {self.failed}")
        print(f"⏱️  Elapsed: {elapsed_str} | ETA: {eta}")
        print(f"⚡ Speed: {avg_extraction:.1f}s per workflow")
        print("="*80)
    
    async def process_workflow(self, extractor, workflow_id, url):
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
            
            # Print progress every 10 workflows
            if self.processed % 10 == 0:
                self.print_progress()
            
            return True
            
        except Exception as e:
            self.processed += 1
            self.failed += 1
            self.errors.append({
                'workflow_id': workflow_id,
                'error': str(e)
            })
            print(f"      ❌ Error: {e}")
            return False
    
    async def run(self):
        """Run Layer 2 Enhanced on all workflows."""
        
        print("\n" + "="*80)
        print("🚀 LAYER 2 ENHANCED - PRODUCTION SCRAPER")
        print("="*80)
        print(f"\nStarted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("\nThis will:")
        print("  • Process all workflows from Layer 1")
        print("  • Extract complete data (API + Iframe - All 4 Phases)")
        print("  • Store to Supabase")
        print("  • Show progress monitoring (Layer 1 style)")
        print("\nLayer 1 will continue running normally in parallel.\n")
        
        # Get workflows
        print("📊 Fetching workflows from Layer 1...")
        workflows = self.get_workflows_to_process()
        
        if not workflows:
            print("\n⚠️  No workflows found to process!")
            print("Either:")
            print("  • All workflows already processed")
            print("  • Layer 1 hasn't discovered any workflows yet")
            return
        
        self.total_workflows = len(workflows)
        self.start_time = time()
        
        print(f"✅ Found {self.total_workflows} workflows to process\n")
        print("="*80)
        print("🔄 STARTING EXTRACTION")
        print("="*80)
        
        # Process workflows
        async with EnhancedLayer2Extractor() as extractor:
            for workflow_id, url in workflows:
                await self.process_workflow(extractor, workflow_id, url)
                
                # Rate limiting (be nice to n8n.io)
                await asyncio.sleep(2)
        
        # Final summary
        self.print_final_summary()
    
    def print_final_summary(self):
        """Print final summary."""
        
        elapsed = time() - self.start_time
        elapsed_str = str(timedelta(seconds=int(elapsed)))
        
        print("\n\n" + "="*80)
        print("📊 FINAL SUMMARY")
        print("="*80)
        
        print(f"\nTotal Workflows: {self.total_workflows}")
        print(f"✅ Successful: {self.successful} ({self.successful/self.total_workflows*100:.1f}%)")
        print(f"❌ Failed: {self.failed} ({self.failed/self.total_workflows*100:.1f}%)")
        
        if self.extraction_times:
            avg_time = sum(self.extraction_times) / len(self.extraction_times)
            min_time = min(self.extraction_times)
            max_time = max(self.extraction_times)
            
            print(f"\n⏱️  Extraction Times:")
            print(f"   Average: {avg_time:.2f}s")
            print(f"   Fastest: {min_time:.2f}s")
            print(f"   Slowest: {max_time:.2f}s")
        
        print(f"\n⏱️  Total Time: {elapsed_str}")
        
        if self.errors:
            print(f"\n⚠️  Errors ({len(self.errors)}):")
            for error in self.errors[:10]:
                print(f"   • Workflow {error['workflow_id']}: {error['error']}")
            if len(self.errors) > 10:
                print(f"   ... and {len(self.errors) - 10} more")
        
        print(f"\nCompleted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("\n✅ Layer 2 Enhanced production scraping complete!")
        print("\nNext steps:")
        print("  • Verify data in Supabase")
        print("  • Export for AI training")
        print("  • Begin model training")
        print("\n")


async def main():
    """Main entry point."""
    runner = Layer2ProductionRunner()
    await runner.run()


if __name__ == "__main__":
    asyncio.run(main())

