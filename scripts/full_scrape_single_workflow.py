#!/usr/bin/env python3
"""
Full 7-Layer Scrape for Single Workflow
Performs complete extraction and saves to database
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.storage.database import get_session
from src.storage.models import Workflow
from src.storage.repository import WorkflowRepository
from src.orchestrator.workflow_orchestrator import WorkflowOrchestrator
from loguru import logger

async def full_scrape_workflow(workflow_id: str, url: str):
    """
    Perform complete 7-layer scrape on a single workflow
    """
    print("=" * 80)
    print(f"🚀 FULL 7-LAYER SCRAPE")
    print("=" * 80)
    print(f"Workflow ID: {workflow_id}")
    print(f"URL: {url}")
    print("=" * 80)
    print()
    
    try:
        # Create database session and repository
        with get_session() as session:
            repository = WorkflowRepository(session)
            
            # Create orchestrator
            orchestrator = WorkflowOrchestrator(
                repository=repository,
                rate_limit=2.0,
                max_retries=3
            )
            
            # Run full scrape
            print("🔄 Starting 7-layer extraction...")
            print()
            
            result = await orchestrator.process_workflow(workflow_id, url)
        
        print()
        print("=" * 80)
        print("📊 SCRAPE RESULTS")
        print("=" * 80)
        
        if result.get('success'):
            print("✅ SCRAPE SUCCESSFUL")
            print()
            
            # Show layer results
            for layer in range(1, 8):
                layer_key = f'layer{layer}_success'
                if layer_key in result:
                    status = "✅" if result[layer_key] else "❌"
                    print(f"   Layer {layer}: {status}")
            
            print()
            print(f"Total time: {result.get('total_time', 0):.2f}s")
            
            # Show extracted data summary
            if 'metadata' in result:
                meta = result['metadata']
                print()
                print("📝 EXTRACTED METADATA:")
                print(f"   Title: {meta.get('title', 'N/A')}")
                print(f"   Author: {meta.get('author', 'N/A')}")
                print(f"   Views: {meta.get('views', 'N/A')}")
                print(f"   Description: {meta.get('description', 'N/A')[:100]}...")
            
            if 'json_data' in result:
                json_data = result['json_data']
                print()
                print("🔧 WORKFLOW STRUCTURE:")
                print(f"   Nodes: {len(json_data.get('nodes', []))}")
                print(f"   Connections: {len(json_data.get('connections', []))}")
            
        else:
            print("❌ SCRAPE FAILED")
            print(f"   Error: {result.get('error', 'Unknown error')}")
        
        print("=" * 80)
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Full scrape failed: {e}")
        import traceback
        traceback.print_exc()
        return {'success': False, 'error': str(e)}

async def main():
    if len(sys.argv) < 3:
        print("Usage: python full_scrape_single_workflow.py <workflow_id> <url>")
        sys.exit(1)
    
    workflow_id = sys.argv[1]
    url = sys.argv[2]
    
    await full_scrape_workflow(workflow_id, url)

if __name__ == '__main__':
    asyncio.run(main())

