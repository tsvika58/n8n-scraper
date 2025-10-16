#!/usr/bin/env python3
"""
Test 20 workflows with webhook integration for real-time updates
"""
import asyncio
import sys
import requests
import time
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.storage.database import get_session
from src.storage.repository import WorkflowRepository
from src.orchestrator.workflow_orchestrator import WorkflowOrchestrator

def trigger_dashboard_update():
    """Trigger immediate dashboard update via webhook"""
    try:
        response = requests.post('http://localhost:5001/api/trigger-update', timeout=5)
        if response.status_code == 200:
            print("🔔 Dashboard update triggered")
            return True
        else:
            print(f"⚠️  Dashboard update failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Failed to trigger dashboard update: {e}")
        return False

async def main():
    """Run a comprehensive test with 20 fresh workflow IDs and webhook updates."""
    print("🚀 COMPREHENSIVE LIVE DASHBOARD TEST WITH WEBHOOKS")
    print("=" * 60)
    print()
    print("📊 Dashboard: http://localhost:5001")
    print("🔌 WebSocket: ws://localhost:5002")
    print("🔔 Webhook: http://localhost:5001/api/trigger-update")
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
        print("   • Webhook updates: Every workflow completion")
        print("   • Watch dashboard for live updates!")
        print()
        
        # Trigger initial dashboard update
        print("🔔 Triggering initial dashboard update...")
        trigger_dashboard_update()
        time.sleep(2)
        
        # Process workflows in batches with webhook updates
        results = []
        for i in range(0, len(fresh_workflows), 5):
            batch = fresh_workflows[i:i+5]
            print(f"\n📦 Processing batch {i//5 + 1}/4: {len(batch)} workflows")
            
            # Process batch
            batch_results = await orchestrator.process_batch(batch)
            results.extend(batch_results['results'])
            
            # Trigger dashboard update after each batch
            print("🔔 Triggering dashboard update after batch completion...")
            trigger_dashboard_update()
            
            # Small delay to see updates
            time.sleep(2)
        
        print()
        print("=" * 60)
        print("✅ COMPREHENSIVE TEST COMPLETE")
        print("=" * 60)
        print()
        print(f"Total: {len(results)}")
        print(f"Success: {sum(1 for r in results if r.get('success'))}")
        print(f"Failed: {sum(1 for r in results if not r.get('success'))}")
        success_rate = (sum(1 for r in results if r.get('success')) / len(results) * 100) if results else 0
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        print("📊 Check dashboard for final live session stats!")
        print("   • Should show live progress for ~2 minutes")
        print("   • Then return to idle state")
        
        # Final webhook trigger
        print("\n🔔 Final dashboard update...")
        trigger_dashboard_update()

if __name__ == "__main__":
    asyncio.run(main())






