#!/usr/bin/env python3
"""
Test scraping 10 workflows end-to-end with global connection coordination.

Verifies:
1. Workflows are scraped with Layer 1.5
2. Data is saved to Supabase
3. Data can be retrieved
4. Connection pooling works correctly
"""

import asyncio
import sys
sys.path.append('/app')

from src.scrapers.layer1_5_page_content import Layer1_5PageContentExtractor
from src.storage.global_connection_coordinator import global_coordinator
from sqlalchemy import text
from loguru import logger
import time
import json


async def test_10_workflows():
    """Test scraping 10 workflows"""
    
    logger.info("="*80)
    logger.info("🧪 TESTING 10 WORKFLOWS WITH GLOBAL CONNECTION COORDINATION")
    logger.info("="*80)
    
    # Get connection status
    status = global_coordinator.get_global_status()
    logger.info(f"📊 Connection Pool Status:")
    logger.info(f"   - Supabase Plan: {status['supabase_plan']}")
    logger.info(f"   - Max Connections: {status['max_connections']}")
    logger.info(f"   - Available: {status['remaining']}")
    logger.info(f"   - Current Utilization: {status['utilization_pct']:.1f}%")
    logger.info("")
    
    # Get 10 workflows that need scraping
    logger.info("📥 Fetching 10 workflows to test...")
    with global_coordinator.get_session() as session:
        result = session.execute(text("""
            SELECT 
                w.id,
                w.workflow_id,
                w.url,
                COALESCE(w.layer1_5_scraped, false) as already_scraped
            FROM workflows w
            WHERE w.url IS NOT NULL
            ORDER BY 
                COALESCE(w.layer1_5_scraped, false) ASC,
                w.id ASC
            LIMIT 10
        """))
        workflows = result.fetchall()
    
    if not workflows:
        logger.error("❌ No workflows found to test!")
        return False
    
    logger.info(f"✅ Found {len(workflows)} workflows to test")
    logger.info("")
    
    # Initialize Layer 1.5 extractor
    extractor = Layer1_5PageContentExtractor()
    
    # Stats tracking
    stats = {
        'total': len(workflows),
        'processed': 0,
        'successful': 0,
        'failed': 0,
        'already_scraped': 0,
        'newly_scraped': 0
    }
    
    start_time = time.time()
    
    # Process each workflow
    for idx, wf in enumerate(workflows, 1):
        workflow_id = wf[1]
        url = wf[2]
        already_scraped = wf[3]
        
        if already_scraped:
            stats['already_scraped'] += 1
            logger.info(f"⏭️  [{idx}/{stats['total']}] {workflow_id}: Already scraped, skipping")
            continue
        
        logger.info(f"🔄 [{idx}/{stats['total']}] Processing: {workflow_id}")
        logger.info(f"   URL: {url}")
        
        try:
            # Scrape the workflow
            result = await extractor.extract_page_content(url)
            
            if result.get('success'):
                # Save to database
                with global_coordinator.get_session() as session:
                    # Update workflow with Layer 1.5 data
                    session.execute(text("""
                        UPDATE workflows SET
                            layer1_5_scraped = true,
                            layer1_5_scraped_at = NOW(),
                            layer1_5_full_text = :full_text,
                            layer1_5_markdown = :markdown,
                            layer1_5_html = :html,
                            layer1_5_headings = :headings,
                            layer1_5_code_blocks = :code_blocks,
                            layer1_5_metadata = :metadata
                        WHERE workflow_id = :workflow_id
                    """), {
                        'workflow_id': workflow_id,
                        'full_text': result.get('full_text', ''),
                        'markdown': result.get('markdown', ''),
                        'html': result.get('html', ''),
                        'headings': json.dumps(result.get('headings', [])),
                        'code_blocks': json.dumps(result.get('code_blocks', [])),
                        'metadata': json.dumps(result.get('metadata', {}))
                    })
                    session.commit()
                
                # Verify save
                with global_coordinator.get_session() as session:
                    verify = session.execute(text("""
                        SELECT 
                            layer1_5_scraped,
                            LENGTH(layer1_5_full_text) as text_length,
                            LENGTH(layer1_5_markdown) as markdown_length
                        FROM workflows
                        WHERE workflow_id = :workflow_id
                    """), {'workflow_id': workflow_id})
                    saved = verify.fetchone()
                
                if saved and saved[0]:
                    stats['successful'] += 1
                    stats['newly_scraped'] += 1
                    logger.info(f"   ✅ Saved! Text: {saved[1]} chars, Markdown: {saved[2]} chars")
                else:
                    stats['failed'] += 1
                    logger.error(f"   ❌ Save verification failed!")
            else:
                stats['failed'] += 1
                logger.error(f"   ❌ Scraping failed: {result.get('error', 'Unknown error')}")
        
        except Exception as e:
            stats['failed'] += 1
            logger.error(f"   ❌ Error: {e}")
        
        stats['processed'] += 1
        
        # Small delay between requests
        await asyncio.sleep(2)
    
    # Close extractor
    await extractor.close()
    
    # Final stats
    elapsed = time.time() - start_time
    logger.info("")
    logger.info("="*80)
    logger.info("📊 FINAL RESULTS")
    logger.info("="*80)
    logger.info(f"Total Workflows: {stats['total']}")
    logger.info(f"Already Scraped: {stats['already_scraped']}")
    logger.info(f"Newly Scraped: {stats['newly_scraped']}")
    logger.info(f"Successful: {stats['successful']}")
    logger.info(f"Failed: {stats['failed']}")
    logger.info(f"Time Elapsed: {elapsed:.1f}s")
    logger.info(f"Avg Time/Workflow: {elapsed/stats['total']:.1f}s")
    
    # Final connection status
    final_status = global_coordinator.get_global_status()
    logger.info("")
    logger.info("📊 Final Connection Pool Status:")
    logger.info(f"   - Total Allocated: {final_status['total_allocated']}")
    logger.info(f"   - Utilization: {final_status['utilization_pct']:.1f}%")
    logger.info("="*80)
    
    # Verify retrieval
    logger.info("")
    logger.info("🔍 Testing data retrieval...")
    with global_coordinator.get_session() as session:
        result = session.execute(text("""
            SELECT 
                workflow_id,
                layer1_5_scraped,
                LENGTH(layer1_5_full_text) as text_length
            FROM workflows
            WHERE layer1_5_scraped = true
            ORDER BY layer1_5_scraped_at DESC
            LIMIT 5
        """))
        recent = result.fetchall()
    
    logger.info(f"✅ Retrieved {len(recent)} recently scraped workflows:")
    for wf in recent:
        logger.info(f"   - {wf[0]}: scraped={wf[1]} ({wf[2]} chars)")
    
    return stats['successful'] > 0


if __name__ == "__main__":
    success = asyncio.run(test_10_workflows())
    sys.exit(0 if success else 1)

