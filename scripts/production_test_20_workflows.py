#!/usr/bin/env python3
"""
SCRAPE-015: Production Validation - 20 Real Workflows
Complete E2E test matching production behavior exactly
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime
import time

sys.path.insert(0, '/app')

from src.orchestrator.workflow_orchestrator import WorkflowOrchestrator
from src.storage.repository import WorkflowRepository
from src.storage.database import get_session
from sqlalchemy import text

# 20 real n8n.io workflows for production testing
TEST_WORKFLOWS = [
    {"id": "2462", "url": "https://n8n.io/workflows/2462"},
    {"id": "499", "url": "https://n8n.io/workflows/499-create-a-user-profile-in-vero"},
    {"id": "498", "url": "https://n8n.io/workflows/498-send-a-private-message-on-zulip"},
    {"id": "497", "url": "https://n8n.io/workflows/497-create-a-contact-in-drift"},
    {"id": "496", "url": "https://n8n.io/workflows/496-create-a-ticket-in-zendesk"},
    {"id": "495", "url": "https://n8n.io/workflows/495-track-an-event-in-segment"},
    {"id": "494", "url": "https://n8n.io/workflows/494-create-a-client-in-harvest"},
    {"id": "493", "url": "https://n8n.io/workflows/493-get-details-of-a-forum-in-disqus"},
    {"id": "491", "url": "https://n8n.io/workflows/491-receive-updates-for-changes-in-the-specified-list-in-trello"},
    {"id": "490", "url": "https://n8n.io/workflows/490-receive-updates-for-all-changes-in-pipedrive"},
    {"id": "489", "url": "https://n8n.io/workflows/489-create-a-deal-in-pipedrive"},
    {"id": "488", "url": "https://n8n.io/workflows/488-receive-updates-when-a-new-account-is-added-by-an-admin-in-activecampaign"},
    {"id": "487", "url": "https://n8n.io/workflows/487-receive-updates-for-events-in-clickup"},
    {"id": "486", "url": "https://n8n.io/workflows/486-receive-updates-for-events-in-chargebee"},
    {"id": "485", "url": "https://n8n.io/workflows/485-create-a-task-in-clickup"},
    {"id": "484", "url": "https://n8n.io/workflows/484-look-up-a-person-using-their-email-in-clearbit"},
    {"id": "483", "url": "https://n8n.io/workflows/483-create-a-new-customer-in-chargebee"},
    {"id": "482", "url": "https://n8n.io/workflows/482-insert-data-into-a-new-row-for-a-table-in-coda"},
    {"id": "481", "url": "https://n8n.io/workflows/481-create-a-new-task-in-todoist"},
    {"id": "479", "url": "https://n8n.io/workflows/479-execute-an-sql-query-in-microsoft-sql"},
]

async def main():
    print("=" * 80)
    print("🧪 SCRAPE-015: PRODUCTION VALIDATION - 20 REAL WORKFLOWS")
    print("=" * 80)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Workflows: {len(TEST_WORKFLOWS)}")
    print("=" * 80)
    print()
    
    start_time = time.time()
    
    try:
        # Initialize
        repository = WorkflowRepository()
        orchestrator = WorkflowOrchestrator(
            repository=repository,
            rate_limit=2.0,
            max_retries=2,
            batch_size=5
        )
        
        print("✅ Orchestrator initialized")
        print(f"   Rate limit: 2.0 req/s")
        print(f"   Batch size: 5")
        print(f"   Max retries: 2")
        print()
        
        # Process workflows
        print("🚀 Processing 20 workflows...")
        print(f"📊 Monitor: http://localhost:5001 (Real-time Dashboard)")
        print(f"🗄️  Database: http://localhost:5004 (Database Viewer)")
        print()
        
        results = await orchestrator.process_batch(
            workflows=TEST_WORKFLOWS,
            concurrent_limit=3
        )
        
        elapsed = time.time() - start_time
        
        # Print results
        print()
        print("=" * 80)
        print("📊 PROCESSING RESULTS")
        print("=" * 80)
        
        total = results.get('total', 0)
        successful = results.get('successful', 0)
        failed = results.get('failed', 0)
        
        print(f"Total Workflows: {total}")
        print(f"✅ Successful: {successful}")
        print(f"❌ Failed: {failed}")
        print(f"Success Rate: {(successful/total*100) if total > 0 else 0:.1f}%")
        print(f"⏱️  Total Time: {elapsed:.1f}s")
        print(f"⏱️  Avg Time/Workflow: {(elapsed/total):.1f}s")
        print()
        
        # Database verification
        print("=" * 80)
        print("🗄️  DATABASE VERIFICATION")
        print("=" * 80)
        
        with get_session() as session:
            # Total count
            total_in_db = session.execute(text("SELECT COUNT(*) FROM workflows")).scalar()
            print(f"📊 Total in database: {total_in_db}")
            
            # Successful scrapes
            fully_scraped = session.execute(text(
                "SELECT COUNT(*) FROM workflows "
                "WHERE layer1_success AND layer2_success AND layer3_success"
            )).scalar()
            print(f"✅ Fully scraped: {fully_scraped}")
            
            # Partial scrapes
            partial = session.execute(text(
                "SELECT COUNT(*) FROM workflows "
                "WHERE (layer1_success OR layer2_success OR layer3_success) "
                "AND NOT (layer1_success AND layer2_success AND layer3_success)"
            )).scalar()
            print(f"⚠️  Partially scraped: {partial}")
            
            # Show recent 5
            recent = session.execute(text(
                "SELECT workflow_id, layer1_success, layer2_success, layer3_success, processing_time "
                "FROM workflows "
                "ORDER BY extracted_at DESC LIMIT 5"
            )).fetchall()
            
            print()
            print("📋 Most Recent Workflows:")
            for row in recent:
                layers = f"L1:{'✅' if row[1] else '❌'} L2:{'✅' if row[2] else '❌'} L3:{'✅' if row[3] else '❌'}"
                time_str = f"{row[4]:.1f}s" if row[4] else "N/A"
                print(f"   • {row[0]:>4} - {layers} - {time_str}")
        
        print()
        print("=" * 80)
        print("✅ TEST COMPLETE")
        print("=" * 80)
        print()
        print("📍 Verification Steps:")
        print(f"   1. Open http://localhost:5004")
        print(f"   2. Click 'Extracted At' to sort by newest")
        print(f"   3. Verify {successful} workflows appear at top")
        print(f"   4. Click workflow IDs to see full details")
        print(f"   5. Verify numerical sorting works (click 'Workflow ID')")
        print()
        
        # Success criteria: 15+ out of 20 successful
        if successful >= 15:
            print("🎉 SUCCESS: 15+ workflows scraped - Production ready!")
            return 0
        else:
            print(f"⚠️  WARNING: Only {successful}/20 scraped - Investigate failures")
            return 1
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)

