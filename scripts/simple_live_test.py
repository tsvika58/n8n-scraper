#!/usr/bin/env python3
"""
Simple Live Scraping Test - Minimal Script to Test Dashboard Updates
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
    """Run a simple 5-workflow scraping test."""
    print("🚀 Starting Simple Live Scraping Test")
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
            batch_size=5
        )
        
        # Test workflows (5 workflows)
        test_workflows = [
            {'id': '2462', 'url': 'https://n8n.io/workflows/2462'},
            {'id': '2463', 'url': 'https://n8n.io/workflows/2463'},
            {'id': '2464', 'url': 'https://n8n.io/workflows/2464'},
            {'id': '2465', 'url': 'https://n8n.io/workflows/2465'},
            {'id': '2466', 'url': 'https://n8n.io/workflows/2466'},
        ]
        
        print(f"🔄 Processing {len(test_workflows)} workflows...")
        print()
        
        # Process batch
        results = await orchestrator.process_batch(test_workflows)
        
        print()
        print("=" * 60)
        print("✅ TEST COMPLETE")
        print()
        print(f"Total: {results['processed']}")
        print(f"Success: {results['successful']}")
        print(f"Failed: {results['failed']}")
        print(f"Success Rate: {results['success_rate']:.1f}%")
        print()
        print("📊 Check dashboard for final stats!")

if __name__ == "__main__":
    asyncio.run(main())

