#!/usr/bin/env python3
"""
Run Metadata Scraper for 500 N8N Workflows

This script runs Layer 1 (metadata) extraction for 500 workflows using the
production-grade orchestrator with:
- Rate limiting (2 req/sec for n8n.io)
- Retry logic (3 attempts with exponential backoff)
- Progress tracking (checkpoint/resume capability)
- Database storage (PostgreSQL)
- Real-time monitoring dashboards

Usage:
    python scripts/run_500_workflows_metadata.py

    # With custom workflow range:
    python scripts/run_500_workflows_metadata.py --start 2400 --count 500

    # Resume from checkpoint:
    python scripts/run_500_workflows_metadata.py --resume

Author: User
Date: October 12, 2025
"""

import asyncio
import sys
import argparse
import json
import time
from pathlib import Path
from datetime import datetime
from typing import List, Dict

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.orchestrator.workflow_orchestrator import WorkflowOrchestrator
from src.storage.database import get_session, init_database
from src.storage.repository import WorkflowRepository
from loguru import logger


def generate_workflow_list(start_id: int = 2400, count: int = 500) -> List[Dict[str, str]]:
    """
    Generate list of workflow IDs to scrape.
    
    Args:
        start_id: Starting workflow ID
        count: Number of workflows to generate
        
    Returns:
        List of workflow dicts with 'id' and 'url' keys
    """
    workflows = []
    
    # Start with some known good workflows
    known_good = ['2462', '2463', '2464', '2465', '2466', '2467', '2468', '2469', '2470']
    
    for wf_id in known_good[:min(len(known_good), count)]:
        workflows.append({
            'id': wf_id,
            'url': f'https://n8n.io/workflows/{wf_id}'
        })
    
    # Generate remaining workflow IDs in the specified range
    remaining = count - len(workflows)
    for i in range(start_id, start_id + remaining):
        workflows.append({
            'id': str(i),
            'url': f'https://n8n.io/workflows/{i}'
        })
    
    return workflows


async def main():
    """Main execution."""
    
    parser = argparse.ArgumentParser(description='Run metadata scraper on 500 workflows')
    parser.add_argument('--start', type=int, default=2400, help='Starting workflow ID (default: 2400)')
    parser.add_argument('--count', type=int, default=500, help='Number of workflows (default: 500)')
    parser.add_argument('--resume', action='store_true', help='Resume from last checkpoint')
    parser.add_argument('--batch-size', type=int, default=10, help='Concurrent batch size (default: 10)')
    parser.add_argument('--rate-limit', type=float, default=2.0, help='Rate limit in req/sec (default: 2.0)')
    
    args = parser.parse_args()
    
    # Print banner
    print("\n" + "="*80)
    print("🚀 N8N METADATA SCRAPER - 500 WORKFLOW BATCH")
    print("="*80)
    print(f"\n⚙️  Configuration:")
    print(f"   • Workflow Range: {args.start} to {args.start + args.count - 1}")
    print(f"   • Total Workflows: {args.count}")
    print(f"   • Batch Size: {args.batch_size} (concurrent)")
    print(f"   • Rate Limit: {args.rate_limit} req/sec")
    print(f"   • Resume Mode: {'Yes' if args.resume else 'No'}")
    print()
    
    # Initialize database
    logger.info("Initializing database...")
    init_database()
    
    # Create repository
    with get_session() as session:
        repository = WorkflowRepository(session)
        
        # Initialize orchestrator
        logger.info("Initializing orchestrator...")
        orchestrator = WorkflowOrchestrator(
            repository=repository,
            rate_limit=args.rate_limit,
            max_retries=3,
            batch_size=args.batch_size,
            checkpoint_dir=".checkpoints"
        )
        
        # Generate workflow list
        logger.info(f"Generating workflow list...")
        workflows = generate_workflow_list(start_id=args.start, count=args.count)
        logger.info(f"Generated {len(workflows)} workflow IDs")
        
        # Print monitoring info
        print("\n📊 Real-time Monitoring:")
        print("   • Realtime Dashboard: http://localhost:5001")
        print("   • Database Viewer: http://localhost:5004")
        print("   • Progress will be displayed below")
        print("\n" + "="*80)
        print()
        
        # Start processing
        start_time = time.time()
        
        logger.info("🔄 Starting batch processing...")
        logger.info(f"   Estimated time: {args.count / (args.rate_limit * 60):.1f} - {args.count / (args.rate_limit * 30):.1f} minutes")
        logger.info(f"   (Depends on page load times and retries)")
        print()
        
        try:
            # Process workflows
            results = await orchestrator.process_batch(
                workflows=workflows,
                concurrent_limit=args.batch_size
            )
            
            # Calculate metrics
            elapsed_time = time.time() - start_time
            elapsed_minutes = elapsed_time / 60
            elapsed_hours = elapsed_time / 3600
            
            successful = results['successful']
            failed = results['failed']
            total = results['total_workflows']
            success_rate = results['success_rate']
            
            # Performance metrics
            workflows_per_minute = total / elapsed_minutes if elapsed_minutes > 0 else 0
            workflows_per_hour = workflows_per_minute * 60
            avg_time_per_workflow = elapsed_time / total if total > 0 else 0
            
            # Get detailed statistics
            stats = orchestrator.get_statistics()
            
            # Print results
            print("\n" + "="*80)
            print("🎉 BATCH PROCESSING COMPLETE!")
            print("="*80)
            
            print(f"\n📈 Processing Summary:")
            print(f"   Total Workflows: {total}")
            print(f"   Successful: {successful} ({success_rate:.2f}%)")
            print(f"   Failed: {failed}")
            
            print(f"\n⏱️  Performance:")
            print(f"   Total Time: {elapsed_minutes:.2f} minutes ({elapsed_hours:.2f} hours)")
            print(f"   Throughput: {workflows_per_hour:.1f} workflows/hour")
            print(f"   Avg Time/Workflow: {avg_time_per_workflow:.2f} seconds")
            
            if stats.get('rate_limiter'):
                rate_stats = stats['rate_limiter']
                print(f"\n🚦 Rate Limiting:")
                print(f"   Total Requests: {rate_stats['total_requests']}")
                print(f"   Total Waits: {rate_stats['total_waits']}")
                print(f"   Total Wait Time: {rate_stats['total_wait_time']:.2f}s")
            
            if stats.get('retry_handler'):
                retry_stats = stats['retry_handler']
                print(f"\n🔄 Retry Statistics:")
                print(f"   Total Retries: {retry_stats['total_retries']}")
                print(f"   Successful Retries: {retry_stats['successful_retries']}")
                print(f"   Failed Retries: {retry_stats['failed_retries']}")
            
            # Save results
            results_dir = Path("data/results")
            results_dir.mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            results_file = results_dir / f"scrape_500_workflows_{timestamp}.json"
            
            with open(results_file, 'w') as f:
                json.dump({
                    'timestamp': timestamp,
                    'configuration': {
                        'start_id': args.start,
                        'count': args.count,
                        'batch_size': args.batch_size,
                        'rate_limit': args.rate_limit,
                    },
                    'results': {
                        'total_workflows': total,
                        'successful': successful,
                        'failed': failed,
                        'success_rate': success_rate,
                        'elapsed_time_seconds': elapsed_time,
                        'elapsed_time_minutes': elapsed_minutes,
                        'workflows_per_hour': workflows_per_hour,
                        'avg_time_per_workflow': avg_time_per_workflow,
                    },
                    'statistics': stats,
                }, f, indent=2)
            
            print(f"\n📄 Results saved to: {results_file}")
            
            print("\n" + "="*80)
            print("✅ View your scraped data:")
            print(f"   • Database Viewer: http://localhost:5004")
            print(f"   • Results File: {results_file}")
            print("="*80 + "\n")
            
            # Exit code based on success rate
            if success_rate >= 95.0:
                logger.info("✅ SUCCESS: Met 95% success rate threshold")
                return 0
            elif success_rate >= 80.0:
                logger.warning("⚠️  WARNING: Success rate below 95% but above 80%")
                return 0
            else:
                logger.error("❌ ERROR: Success rate below 80%")
                return 1
                
        except KeyboardInterrupt:
            print("\n\n⚠️  Process interrupted by user")
            print("   Checkpoint saved - you can resume with --resume flag")
            return 130
            
        except Exception as e:
            logger.error(f"❌ Fatal error: {e}")
            import traceback
            traceback.print_exc()
            return 1


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted")
        sys.exit(130)







