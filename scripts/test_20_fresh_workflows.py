#!/usr/bin/env python3
"""
Test with 20 fresh workflow IDs for comprehensive live dashboard testing
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
    """Run a comprehensive test with 20 fresh workflow IDs."""
    print("🚀 COMPREHENSIVE LIVE DASHBOARD TEST")
    print("=" * 60)
    print()
    print("📊 Dashboard URL: http://localhost:5001")
    print("🎯 Watch the 'LIVE SCRAPING STATUS' section!")
    print("⏱️  This test will take approximately 8-10 minutes")
    print()
    
    # Get database session
    with get_session() as session:
        repository = WorkflowRepository(session)
        
        # Initialize orchestrator with lower concurrency for better visibility
        orchestrator = WorkflowOrchestrator(
            repository=repository,
            rate_limit=2.0,
            max_retries=2,
            batch_size=5  # Process 5 at a time for better live updates
        )
        
        # 20 fresh workflow IDs (3003-3022)
        fresh_workflows = [
            {'id': '3003', 'url': 'https://n8n.io/workflows/3003'},
            {'id': '3004', 'url': 'https://n8n.io/workflows/3004'},
            {'id': '3005', 'url': 'https://n8n.io/workflows/3005'},
            {'id': '3006', 'url': 'https://n8n.io/workflows/3006'},
            {'id': '3007', 'url': 'https://n8n.io/workflows/3007'},
            {'id': '3008', 'url': 'https://n8n.io/workflows/3008'},
            {'id': '3009', 'url': 'https://n8n.io/workflows/3009'},
            {'id': '3010', 'url': 'https://n8n.io/workflows/3010'},
            {'id': '3011', 'url': 'https://n8n.io/workflows/3011'},
            {'id': '3012', 'url': 'https://n8n.io/workflows/3012'},
            {'id': '3013', 'url': 'https://n8n.io/workflows/3013'},
            {'id': '3014', 'url': 'https://n8n.io/workflows/3014'},
            {'id': '3015', 'url': 'https://n8n.io/workflows/3015'},
            {'id': '3016', 'url': 'https://n8n.io/workflows/3016'},
            {'id': '3017', 'url': 'https://n8n.io/workflows/3017'},
            {'id': '3018', 'url': 'https://n8n.io/workflows/3018'},
            {'id': '3019', 'url': 'https://n8n.io/workflows/3019'},
            {'id': '3020', 'url': 'https://n8n.io/workflows/3020'},
            {'id': '3021', 'url': 'https://n8n.io/workflows/3021'},
            {'id': '3022', 'url': 'https://n8n.io/workflows/3022'},
        ]
        
        print(f"🔄 Processing {len(fresh_workflows)} FRESH workflows...")
        print("   • Batch size: 5 workflows at a time")
        print("   • Rate limit: 2 requests/second")
        print("   • Watch dashboard for live updates!")
        print()
        
        # Process batch
        results = await orchestrator.process_batch(fresh_workflows)
        
        print()
        print("=" * 60)
        print("✅ COMPREHENSIVE TEST COMPLETE")
        print("=" * 60)
        print()
        print(f"Total: {results['processed']}")
        print(f"Success: {results['successful']}")
        print(f"Failed: {results['failed']}")
        print(f"Success Rate: {results['success_rate']:.1f}%")
        print()
        print("📊 Check dashboard for final live session stats!")
        print("   • Should show live progress for ~2 minutes")
        print("   • Then return to idle state")

if __name__ == "__main__":
    asyncio.run(main())





