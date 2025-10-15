#!/usr/bin/env python3
"""
SCRAPE-016: Layer 1 Metadata ONLY - 500 Workflows

Extracts ONLY Layer 1 page metadata (19 fields):
- title, description, author, use_case
- primary_category, secondary_categories, node_tags, general_tags
- difficulty_level, views, upvotes
- created_date, updated_date
- setup_instructions, prerequisites, estimated_setup_time
- industry

Performance Target:
- 8-10 seconds per workflow
- 500 workflows in ~70-83 minutes
- Rate limited to 2 req/sec

This is METADATA ONLY - no JSON extraction, no content, no other layers.

Usage:
    python scripts/run_layer1_metadata_only.py

    # With custom range:
    python scripts/run_layer1_metadata_only.py --start 2400 --count 500

Author: User
Task: SCRAPE-016
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
from loguru import logger

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.scrapers.layer1_metadata import PageMetadataExtractor
from src.storage.database import get_session
from sqlalchemy import text


def generate_workflow_list(start_id: int = 2400, count: int = 500) -> List[Dict[str, str]]:
    """Generate list of workflow IDs to scrape."""
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


async def rate_limited_sleep(last_request_time: float, rate_limit: float = 2.0) -> float:
    """
    Sleep to maintain rate limit.
    
    Args:
        last_request_time: Timestamp of last request
        rate_limit: Requests per second (default: 2.0)
        
    Returns:
        Current time after sleeping
    """
    min_interval = 1.0 / rate_limit
    elapsed = time.time() - last_request_time
    if elapsed < min_interval:
        sleep_time = min_interval - elapsed
        await asyncio.sleep(sleep_time)
    return time.time()


async def store_metadata(session, workflow_id: str, url: str, metadata: Dict) -> bool:
    """
    Store Layer 1 metadata in database.
    
    Args:
        session: Database session
        workflow_id: Workflow ID
        url: Workflow URL
        metadata: Extracted metadata dict
        
    Returns:
        True if stored successfully
    """
    try:
        # Store in workflow_metadata table
        insert_sql = text("""
            INSERT INTO workflow_metadata (
                workflow_id, 
                title, description, use_case,
                author_name,
                views, shares,
                categories, tags,
                workflow_created_at, workflow_updated_at,
                extracted_at,
                raw_metadata
            ) VALUES (
                :workflow_id,
                :title, :description, :use_case,
                :author_name,
                :views, :shares,
                :categories, :tags,
                :workflow_created_at, :workflow_updated_at,
                :extracted_at,
                :raw_metadata
            )
            ON CONFLICT (workflow_id) DO UPDATE SET
                title = EXCLUDED.title,
                description = EXCLUDED.description,
                use_case = EXCLUDED.use_case,
                author_name = EXCLUDED.author_name,
                views = EXCLUDED.views,
                shares = EXCLUDED.shares,
                categories = EXCLUDED.categories,
                tags = EXCLUDED.tags,
                workflow_updated_at = EXCLUDED.workflow_updated_at,
                extracted_at = EXCLUDED.extracted_at,
                raw_metadata = EXCLUDED.raw_metadata
        """)
        
        # Prepare categories and tags as JSON arrays
        categories = metadata.get('secondary_categories', [])
        if metadata.get('primary_category'):
            categories.insert(0, metadata['primary_category'])
            
        all_tags = metadata.get('node_tags', []) + metadata.get('general_tags', [])
        
        session.execute(insert_sql, {
            'workflow_id': workflow_id,
            'title': metadata.get('title', 'Unknown'),
            'description': metadata.get('description', ''),
            'use_case': metadata.get('use_case', ''),
            'author_name': metadata.get('author', 'Unknown'),
            'views': metadata.get('views', 0),
            'shares': metadata.get('upvotes', 0),  # Map upvotes to shares
            'categories': json.dumps(categories),
            'tags': json.dumps(all_tags),
            'workflow_created_at': metadata.get('created_date'),
            'workflow_updated_at': metadata.get('updated_date'),
            'extracted_at': datetime.now(),
            'raw_metadata': json.dumps(metadata)
        })
        
        session.commit()
        return True
        
    except Exception as e:
        logger.error(f"Failed to store metadata for {workflow_id}: {e}")
        session.rollback()
        return False


async def main():
    """Main execution."""
    
    parser = argparse.ArgumentParser(description='Run Layer 1 metadata scraper ONLY on 500 workflows')
    parser.add_argument('--start', type=int, default=2400, help='Starting workflow ID (default: 2400)')
    parser.add_argument('--count', type=int, default=500, help='Number of workflows (default: 500)')
    parser.add_argument('--rate-limit', type=float, default=2.0, help='Rate limit in req/sec (default: 2.0)')
    
    args = parser.parse_args()
    
    # Print banner
    print("\n" + "="*80)
    print("🚀 SCRAPE-016: LAYER 1 METADATA ONLY - 500 WORKFLOWS")
    print("="*80)
    print(f"\n⚙️  Configuration:")
    print(f"   • Workflow Range: {args.start} to {args.start + args.count - 1}")
    print(f"   • Total Workflows: {args.count}")
    print(f"   • Rate Limit: {args.rate_limit} req/sec")
    print(f"   • Extraction: Layer 1 ONLY (19 metadata fields)")
    print(f"   • Estimated Time: ~{(args.count * 9) / 60:.0f} minutes (9 sec/workflow)")
    print()
    
    # Generate workflow list
    logger.info(f"Generating workflow list...")
    workflows = generate_workflow_list(start_id=args.start, count=args.count)
    logger.info(f"Generated {len(workflows)} workflow IDs")
    
    # Initialize extractor
    extractor = PageMetadataExtractor()
    
    # Statistics
    stats = {
        'total': len(workflows),
        'successful': 0,
        'failed': 0,
        'stored': 0,
        'total_extraction_time': 0.0,
        'failed_workflows': []
    }
    
    # Print monitoring info
    print("\n📊 Real-time Monitoring:")
    print("   • Database Viewer: http://localhost:5004")
    print("   • Progress will be displayed below")
    print("\n" + "="*80)
    print()
    
    # Start processing
    start_time = time.time()
    last_request_time = 0.0
    
    logger.info("🔄 Starting Layer 1 metadata extraction...")
    print()
    
    for i, workflow in enumerate(workflows, 1):
        workflow_id = workflow['id']
        url = workflow['url']
        
        try:
            # Rate limiting
            if last_request_time > 0:
                last_request_time = await rate_limited_sleep(last_request_time, args.rate_limit)
            else:
                last_request_time = time.time()
            
            # Extract metadata
            logger.info(f"[{i}/{len(workflows)}] Extracting metadata for workflow {workflow_id}...")
            result = await extractor.extract(workflow_id, url)
            
            if result['success']:
                stats['successful'] += 1
                stats['total_extraction_time'] += result['extraction_time']
                
                # Store in database
                with get_session() as session:
                    if await store_metadata(session, workflow_id, url, result['data']):
                        stats['stored'] += 1
                        logger.success(f"✅ [{i}/{len(workflows)}] {workflow_id}: {result['data'].get('title', 'N/A')} ({result['extraction_time']:.1f}s)")
                    else:
                        logger.warning(f"⚠️  [{i}/{len(workflows)}] {workflow_id}: Extracted but failed to store")
            else:
                stats['failed'] += 1
                stats['failed_workflows'].append(workflow_id)
                logger.error(f"❌ [{i}/{len(workflows)}] {workflow_id}: Extraction failed")
            
            # Progress update every 10 workflows
            if i % 10 == 0:
                elapsed = time.time() - start_time
                avg_time = elapsed / i
                remaining = (len(workflows) - i) * avg_time
                print(f"\n📊 Progress: {i}/{len(workflows)} ({i/len(workflows)*100:.1f}%)")
                print(f"   • Successful: {stats['successful']}")
                print(f"   • Failed: {stats['failed']}")
                print(f"   • Avg Time: {avg_time:.1f}s per workflow")
                print(f"   • Est. Remaining: {remaining/60:.1f} minutes")
                print()
                
        except KeyboardInterrupt:
            print("\n\n⚠️  Process interrupted by user")
            break
        except Exception as e:
            stats['failed'] += 1
            stats['failed_workflows'].append(workflow_id)
            logger.error(f"❌ [{i}/{len(workflows)}] {workflow_id}: Unexpected error: {e}")
    
    # Calculate final metrics
    elapsed_time = time.time() - start_time
    elapsed_minutes = elapsed_time / 60
    avg_time_per_workflow = elapsed_time / stats['total'] if stats['total'] > 0 else 0
    success_rate = (stats['successful'] / stats['total'] * 100) if stats['total'] > 0 else 0
    
    # Print results
    print("\n" + "="*80)
    print("🎉 LAYER 1 METADATA EXTRACTION COMPLETE!")
    print("="*80)
    
    print(f"\n📈 Processing Summary:")
    print(f"   Total Workflows: {stats['total']}")
    print(f"   Successful: {stats['successful']} ({success_rate:.2f}%)")
    print(f"   Failed: {stats['failed']}")
    print(f"   Stored in DB: {stats['stored']}")
    
    print(f"\n⏱️  Performance:")
    print(f"   Total Time: {elapsed_minutes:.2f} minutes ({elapsed_time/3600:.2f} hours)")
    print(f"   Avg Time/Workflow: {avg_time_per_workflow:.2f} seconds")
    print(f"   Throughput: {stats['total']/(elapsed_time/3600):.1f} workflows/hour")
    
    if stats['failed_workflows']:
        print(f"\n❌ Failed Workflows ({len(stats['failed_workflows'])}):")
        for wf_id in stats['failed_workflows'][:10]:
            print(f"   • {wf_id}")
        if len(stats['failed_workflows']) > 10:
            print(f"   ... and {len(stats['failed_workflows']) - 10} more")
    
    # Save results
    results_dir = Path("data/results")
    results_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = results_dir / f"scrape_016_layer1_metadata_{timestamp}.json"
    
    with open(results_file, 'w') as f:
        json.dump({
            'task': 'SCRAPE-016',
            'layer': 'Layer 1 - Metadata Only',
            'timestamp': timestamp,
            'configuration': {
                'start_id': args.start,
                'count': args.count,
                'rate_limit': args.rate_limit,
            },
            'results': {
                'total_workflows': stats['total'],
                'successful': stats['successful'],
                'failed': stats['failed'],
                'stored': stats['stored'],
                'success_rate': success_rate,
                'elapsed_time_seconds': elapsed_time,
                'elapsed_time_minutes': elapsed_minutes,
                'avg_time_per_workflow': avg_time_per_workflow,
                'workflows_per_hour': stats['total']/(elapsed_time/3600),
                'failed_workflows': stats['failed_workflows']
            },
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


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted")
        sys.exit(130)






