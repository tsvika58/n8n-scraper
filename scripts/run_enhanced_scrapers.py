#!/usr/bin/env python3
"""
Enhanced Scrapers Runner with Resume Capability
Runs Layer 2 V2 and Layer 3 V3 scrapers with resume functionality.

Author: Dev1
Task: Enhanced L2 L3 Node Context Extraction
Date: October 15, 2025
"""

import asyncio
import sys
import os
import signal
import json
from datetime import datetime
from typing import List, Dict, Any, Optional

# Add project paths
sys.path.append('.')
sys.path.append('../n8n-shared')

from src.storage.database import get_session
from src.scrapers.layer2_enhanced_v2 import extract_workflow_node_contexts
from src.scrapers.layer3_enhanced_v3 import extract_workflow_standalone_docs
from sqlalchemy import text


class EnhancedScrapersRunner:
    """Runner for enhanced scrapers with resume capability."""
    
    def __init__(self, batch_size: int = 10, delay_between_batches: int = 30):
        self.batch_size = batch_size
        self.delay_between_batches = delay_between_batches
        self.running = True
        self.stats = {
            'start_time': datetime.now(),
            'workflows_processed': 0,
            'layer2_v2_success': 0,
            'layer3_v3_success': 0,
            'layer2_v2_errors': 0,
            'layer3_v3_errors': 0,
            'total_node_contexts': 0,
            'total_standalone_docs': 0
        }
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully."""
        print(f"\n🛑 Received signal {signum}, shutting down gracefully...")
        self.running = False
    
    def get_workflows_to_process(self, layer: str) -> List[Dict[str, str]]:
        """Get workflows that need processing for the specified layer."""
        try:
            with get_session() as session:
                if layer == 'layer2_v2':
                    # Get workflows without Layer 2 V2 data
                    query = text("""
                        SELECT w.workflow_id, w.url 
                        FROM workflows w
                        LEFT JOIN workflow_node_contexts wnc ON w.workflow_id = wnc.workflow_id
                        WHERE wnc.workflow_id IS NULL
                        ORDER BY w.workflow_id
                    """)
                elif layer == 'layer3_v3':
                    # Get workflows without Layer 3 V3 data
                    query = text("""
                        SELECT w.workflow_id, w.url 
                        FROM workflows w
                        LEFT JOIN workflow_standalone_docs wsd ON w.workflow_id = wsd.workflow_id
                        WHERE wsd.workflow_id IS NULL
                        ORDER BY w.workflow_id
                    """)
                else:
                    return []
                
                result = session.execute(query)
                workflows = []
                for row in result.fetchall():
                    workflows.append({
                        'workflow_id': row[0],
                        'url': row[1]
                    })
                
                return workflows
                
        except Exception as e:
            print(f"❌ Error getting workflows to process: {e}")
            return []
    
    async def process_workflow_batch(self, workflows: List[Dict[str, str]], layer: str) -> Dict[str, Any]:
        """Process a batch of workflows."""
        batch_stats = {
            'processed': 0,
            'success': 0,
            'errors': 0,
            'node_contexts': 0,
            'standalone_docs': 0
        }
        
        for workflow in workflows:
            if not self.running:
                break
                
            workflow_id = workflow['workflow_id']
            workflow_url = workflow['url']
            
            try:
                print(f"   🔍 Processing {workflow_id} ({layer})...")
                
                if layer == 'layer2_v2':
                    result = await extract_workflow_node_contexts(
                        workflow_id, workflow_url, headless=True, save_to_db=True
                    )
                    if result['success']:
                        batch_stats['node_contexts'] += len(result['node_contexts'])
                        batch_stats['success'] += 1
                        self.stats['layer2_v2_success'] += 1
                        self.stats['total_node_contexts'] += len(result['node_contexts'])
                    else:
                        batch_stats['errors'] += 1
                        self.stats['layer2_v2_errors'] += 1
                        print(f"      ❌ Layer 2 V2 failed: {result.get('error', 'Unknown error')}")
                
                elif layer == 'layer3_v3':
                    result = await extract_workflow_standalone_docs(
                        workflow_id, workflow_url, headless=True, save_to_db=True
                    )
                    if result['success']:
                        batch_stats['standalone_docs'] += len(result['standalone_docs'])
                        batch_stats['success'] += 1
                        self.stats['layer3_v3_success'] += 1
                        self.stats['total_standalone_docs'] += len(result['standalone_docs'])
                    else:
                        batch_stats['errors'] += 1
                        self.stats['layer3_v3_errors'] += 1
                        print(f"      ❌ Layer 3 V3 failed: {result.get('error', 'Unknown error')}")
                
                batch_stats['processed'] += 1
                self.stats['workflows_processed'] += 1
                
                # Small delay between workflows
                await asyncio.sleep(2)
                
            except Exception as e:
                print(f"      ❌ Error processing {workflow_id}: {e}")
                batch_stats['errors'] += 1
                if layer == 'layer2_v2':
                    self.stats['layer2_v2_errors'] += 1
                else:
                    self.stats['layer3_v3_errors'] += 1
        
        return batch_stats
    
    def display_progress(self):
        """Display current progress."""
        current_time = datetime.now()
        elapsed = current_time - self.stats['start_time']
        
        print(f"\n📊 PROGRESS UPDATE - {current_time.strftime('%H:%M:%S')}")
        print(f"⏱️  Elapsed: {elapsed}")
        print(f"🔢 Workflows Processed: {self.stats['workflows_processed']}")
        print(f"📍 Layer 2 V2: {self.stats['layer2_v2_success']} success, {self.stats['layer2_v2_errors']} errors")
        print(f"📄 Layer 3 V3: {self.stats['layer3_v3_success']} success, {self.stats['layer3_v3_errors']} errors")
        print(f"📈 Total Node Contexts: {self.stats['total_node_contexts']}")
        print(f"📈 Total Standalone Docs: {self.stats['total_standalone_docs']}")
        
        if self.stats['workflows_processed'] > 0:
            rate = self.stats['workflows_processed'] / elapsed.total_seconds() * 3600
            print(f"🚀 Processing Rate: {rate:.1f} workflows/hour")
    
    async def run_layer(self, layer: str):
        """Run a specific layer scraper."""
        print(f"\n🚀 Starting {layer} scraper...")
        
        workflows = self.get_workflows_to_process(layer)
        total_workflows = len(workflows)
        
        if total_workflows == 0:
            print(f"✅ No workflows need {layer} processing")
            return
        
        print(f"📋 Found {total_workflows} workflows to process for {layer}")
        
        # Process in batches
        for i in range(0, total_workflows, self.batch_size):
            if not self.running:
                break
                
            batch = workflows[i:i + self.batch_size]
            batch_num = i // self.batch_size + 1
            total_batches = (total_workflows + self.batch_size - 1) // self.batch_size
            
            print(f"\n📦 Processing batch {batch_num}/{total_batches} ({len(batch)} workflows)")
            
            batch_stats = await self.process_workflow_batch(batch, layer)
            
            print(f"   ✅ Batch complete: {batch_stats['success']} success, {batch_stats['errors']} errors")
            if layer == 'layer2_v2':
                print(f"   📍 Node contexts extracted: {batch_stats['node_contexts']}")
            else:
                print(f"   📄 Standalone docs extracted: {batch_stats['standalone_docs']}")
            
            self.display_progress()
            
            # Delay between batches (except for the last batch)
            if i + self.batch_size < total_workflows and self.running:
                print(f"   ⏳ Waiting {self.delay_between_batches}s before next batch...")
                await asyncio.sleep(self.delay_between_batches)
        
        print(f"\n✅ {layer} scraper completed")
    
    async def run_both_layers(self):
        """Run both Layer 2 V2 and Layer 3 V3 scrapers."""
        print("🚀 Enhanced Scrapers Runner Starting...")
        print(f"📦 Batch size: {self.batch_size}")
        print(f"⏳ Delay between batches: {self.delay_between_batches}s")
        print(f"🕒 Start time: {self.stats['start_time'].strftime('%Y-%m-%d %H:%M:%S')}")
        
        try:
            # Run Layer 2 V2 first
            await self.run_layer('layer2_v2')
            
            if not self.running:
                print("🛑 Stopping due to shutdown signal")
                return
            
            # Run Layer 3 V3
            await self.run_layer('layer3_v3')
            
        except Exception as e:
            print(f"❌ Runner error: {e}")
        
        finally:
            # Final statistics
            end_time = datetime.now()
            total_time = end_time - self.stats['start_time']
            
            print(f"\n🏁 ENHANCED SCRAPERS RUNNER COMPLETED")
            print("=" * 60)
            print(f"⏱️  Total time: {total_time}")
            print(f"🔢 Workflows processed: {self.stats['workflows_processed']}")
            print(f"📍 Layer 2 V2: {self.stats['layer2_v2_success']} success, {self.stats['layer2_v2_errors']} errors")
            print(f"📄 Layer 3 V3: {self.stats['layer3_v3_success']} success, {self.stats['layer3_v3_errors']} errors")
            print(f"📈 Total node contexts: {self.stats['total_node_contexts']}")
            print(f"📈 Total standalone docs: {self.stats['total_standalone_docs']}")
            
            if self.stats['workflows_processed'] > 0:
                rate = self.stats['workflows_processed'] / total_time.total_seconds() * 3600
                print(f"🚀 Average rate: {rate:.1f} workflows/hour")


def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Enhanced Scrapers Runner with Resume Capability')
    parser.add_argument('--batch-size', '-b', type=int, default=10,
                       help='Number of workflows to process per batch (default: 10)')
    parser.add_argument('--delay', '-d', type=int, default=30,
                       help='Delay between batches in seconds (default: 30)')
    parser.add_argument('--layer', '-l', choices=['layer2_v2', 'layer3_v3', 'both'], default='both',
                       help='Which layer to run (default: both)')
    
    args = parser.parse_args()
    
    runner = EnhancedScrapersRunner(
        batch_size=args.batch_size,
        delay_between_batches=args.delay
    )
    
    if args.layer == 'both':
        asyncio.run(runner.run_both_layers())
    else:
        asyncio.run(runner.run_layer(args.layer))


if __name__ == "__main__":
    main()

