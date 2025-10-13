#!/usr/bin/env python3
"""
Test Layer 2 Enhanced on first 20 workflows with full visible output.
Safe to run while Layer 1 is scraping.
"""

import asyncio
import sys
import os
import psycopg2
from datetime import datetime

sys.path.insert(0, '/Users/tsvikavagman/Desktop/Code Projects/shared-tools/n8n-scraper')

from src.scrapers.layer2_enhanced import EnhancedLayer2Extractor

# Database credentials
DB_HOST = "aws-1-eu-north-1.pooler.supabase.com"
DB_PORT = "5432"
DB_NAME = "postgres"
DB_USER = "postgres.skduopoakfeaurttcaip"
DB_PASSWORD = "crg3pjm8ych4ctu@KXT"


def get_workflows_for_layer2(limit=20):
    """Get workflows that passed Layer 1 but haven't been processed by Layer 2."""
    
    print("\n" + "="*80)
    print("📊 FETCHING WORKFLOWS FROM LAYER 1")
    print("="*80)
    
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
        
        # Get workflows that passed Layer 1 but not yet processed by Layer 2
        print(f"\nQuerying for {limit} workflows...")
        cursor.execute("""
            SELECT w.workflow_id, w.url
            FROM workflows w
            LEFT JOIN workflow_structure ws ON w.workflow_id = ws.workflow_id
            WHERE ws.workflow_id IS NULL
            ORDER BY w.extracted_at ASC
            LIMIT %s;
        """, (limit,))
        
        workflows = cursor.fetchall()
        
        print(f"✅ Found {len(workflows)} workflows ready for Layer 2\n")
        
        if workflows:
            print("First 10 workflows:")
            for i, (wf_id, url) in enumerate(workflows[:10], 1):
                print(f"  {i}. {wf_id}: {url}")
            if len(workflows) > 10:
                print(f"  ... and {len(workflows) - 10} more")
        
        cursor.close()
        conn.close()
        
        return workflows
        
    except Exception as e:
        print(f"❌ Error fetching workflows: {e}")
        return []


def store_to_database(workflow_id, result):
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
        
        import json
        
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
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"      ❌ Storage error: {e}")
        return False


async def process_workflow(extractor, workflow_id, url, index, total):
    """Process a single workflow."""
    
    print(f"\n{'='*80}")
    print(f"[{index}/{total}] PROCESSING WORKFLOW #{workflow_id}")
    print(f"{'='*80}")
    print(f"URL: {url}")
    print(f"Started: {datetime.now().strftime('%H:%M:%S')}\n")
    
    try:
        # Extract
        print("📊 Extracting (API + Iframe - All 4 Phases)...")
        result = await extractor.extract_complete(workflow_id, url)
        
        # Show results
        api_data = result['sources']['api']
        iframe_data = result['sources']['iframe']
        
        print(f"\n✅ EXTRACTION COMPLETE")
        print(f"   Time: {result['extraction_time']:.2f}s")
        print(f"   Completeness: {result['completeness']['merged']:.1f}%")
        
        print(f"\n   API: {api_data.get('node_count', 0)} nodes, {api_data.get('connection_count', 0)} connections")
        print(f"   Iframe: {iframe_data.get('node_count', 0)} elements")
        
        if iframe_data.get('visual_layout'):
            layout = iframe_data['visual_layout']
            print(f"   Phase 2: {len(layout.get('node_positions', []))} positions")
        
        if iframe_data.get('enhanced_content'):
            content = iframe_data['enhanced_content']
            print(f"   Phase 3: {len(content.get('all_text_blocks', []))} text blocks ({content.get('total_text_length', 0):,} chars)")
        
        if iframe_data.get('media_content'):
            media = iframe_data['media_content']
            print(f"   Phase 4: {media.get('video_count', 0)} videos, {media.get('image_count', 0)} images, {media.get('svg_count', 0)} SVGs")
        
        # Store
        print(f"\n💾 Storing to Supabase...")
        success = store_to_database(workflow_id, result)
        
        if success:
            print(f"   ✅ Stored successfully")
        else:
            print(f"   ❌ Storage failed")
        
        print(f"\nCompleted: {datetime.now().strftime('%H:%M:%S')}")
        
        return {
            'workflow_id': workflow_id,
            'success': result['completeness']['merged'] == 100.0 and success,
            'extraction_time': result['extraction_time'],
            'stored': success
        }
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        
        return {
            'workflow_id': workflow_id,
            'success': False,
            'error': str(e),
            'stored': False
        }


async def main():
    """Run Layer 2 Enhanced on first 20 workflows."""
    
    print("\n" + "="*80)
    print("🚀 LAYER 2 ENHANCED - TEST BATCH (20 WORKFLOWS)")
    print("="*80)
    print(f"\nStarted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\nThis will:")
    print("  1. Fetch 20 workflows from Layer 1")
    print("  2. Extract complete data (API + Iframe - All 4 Phases)")
    print("  3. Store to Supabase")
    print("  4. Show full progress (visible output)")
    print("\nLayer 1 will continue running normally in parallel.\n")
    
    # Get workflows
    workflows = get_workflows_for_layer2(limit=20)
    
    if not workflows:
        print("\n⚠️  No workflows found!")
        print("Either:")
        print("  • Layer 1 hasn't discovered any workflows yet")
        print("  • All workflows already processed by Layer 2")
        return
    
    print(f"\n{'='*80}")
    print(f"🔄 PROCESSING {len(workflows)} WORKFLOWS")
    print(f"{'='*80}\n")
    
    results = []
    
    async with EnhancedLayer2Extractor() as extractor:
        for i, (workflow_id, url) in enumerate(workflows, 1):
            result = await process_workflow(extractor, workflow_id, url, i, len(workflows))
            results.append(result)
            
            # Rate limiting (be nice to n8n.io)
            if i < len(workflows):
                print(f"\n⏸️  Waiting 3 seconds before next workflow...")
                await asyncio.sleep(3)
    
    # Summary
    print(f"\n\n{'='*80}")
    print("📊 BATCH SUMMARY")
    print(f"{'='*80}\n")
    
    successful = sum(1 for r in results if r.get('success'))
    stored = sum(1 for r in results if r.get('stored'))
    failed = len(results) - successful
    
    print(f"Total Workflows: {len(results)}")
    print(f"Successful Extractions: {successful}")
    print(f"Successfully Stored: {stored}")
    print(f"Failed: {failed}")
    print(f"Success Rate: {successful/len(results)*100:.1f}%")
    
    if successful > 0:
        avg_time = sum(r.get('extraction_time', 0) for r in results if r.get('success')) / successful
        print(f"Average Extraction Time: {avg_time:.2f}s")
    
    # Show any failures
    failures = [r for r in results if not r.get('success')]
    if failures:
        print(f"\n⚠️  Failed Workflows:")
        for f in failures:
            print(f"   • {f['workflow_id']}: {f.get('error', 'Unknown error')}")
    
    print(f"\nCompleted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n✅ Test batch complete!")
    print("\nIf all looks good, you can run on more workflows:")
    print("  python scripts/run_layer2_enhanced_batch.py --limit 100")
    print("\n")


if __name__ == "__main__":
    asyncio.run(main())


