#!/usr/bin/env python3
"""
Test with fresh workflow IDs that haven't been scraped yet
"""
import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.storage.database import get_session
from src.storage.repository import WorkflowRepository
from src.orchestrator.workflow_orchestrator import WorkflowOrchestrator

async def main():
    """Run a test with fresh workflow IDs."""
    print("🚀 Starting FRESH Workflow Scraping Test")
    print("=" * 60)
    print()
    print("📊 Dashboard URL: http://localhost:5001")
    print("🎯 Watch the 'LIVE SCRAPING STATUS' section!")
    print()
    
    # Get database session
    with get_session() as session:
        repository = WorkflowRepository(session)
        
        # Initialize orchestrator
        orchestrator = WorkflowOrchestrator(
            repository=repository,
            rate_limit=2.0,
            max_retries=2,
            batch_size=3
        )
        
        # Fresh workflow IDs that haven't been scraped yet
        fresh_workflows = [
            {'id': '3000', 'url': 'https://n8n.io/workflows/3000'},
            {'id': '3001', 'url': 'https://n8n.io/workflows/3001'},
            {'id': '3002', 'url': 'https://n8n.io/workflows/3002'},
        ]
        
        print(f"🔄 Processing {len(fresh_workflows)} FRESH workflows...")
        print()
        
        # Process batch
        results = await orchestrator.process_batch(fresh_workflows)
        
        print()
        print("=" * 60)
        print("✅ FRESH TEST COMPLETE")
        print()
        print(f"Total: {results['processed']}")
        print(f"Success: {results['successful']}")
        print(f"Failed: {results['failed']}")
        print(f"Success Rate: {results['success_rate']:.1f}%")
        print()
        print("📊 Check dashboard for NEW live session stats!")

if __name__ == "__main__":
    asyncio.run(main())






