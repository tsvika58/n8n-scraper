#!/usr/bin/env python3
"""
SCRAPE-015: Production Test - 20 Real Workflows
Complete E2E test with database verification
"""

import asyncio
import sys
import os
sys.path.insert(0, '/app')

from src.orchestrator.workflow_orchestrator import WorkflowOrchestrator
from src.storage.repository import WorkflowRepository
from src.storage.database import get_session
from datetime import datetime
import time

# Test workflows (real n8n.io workflows)
TEST_WORKFLOWS = [
    ("2462", "https://n8n.io/workflows/2462"),
    ("499", "https://n8n.io/workflows/499-create-a-user-profile-in-vero"),
    ("498", "https://n8n.io/workflows/498-send-a-private-message-on-zulip"),
    ("497", "https://n8n.io/workflows/497-create-a-contact-in-drift"),
    ("496", "https://n8n.io/workflows/496-create-a-ticket-in-zendesk"),
    ("495", "https://n8n.io/workflows/495-track-an-event-in-segment"),
    ("494", "https://n8n.io/workflows/494-create-a-client-in-harvest"),
    ("493", "https://n8n.io/workflows/493-get-details-of-a-forum-in-disqus"),
    ("491", "https://n8n.io/workflows/491-receive-updates-for-changes-in-the-specified-list-in-trello"),
    ("490", "https://n8n.io/workflows/490-receive-updates-for-all-changes-in-pipedrive"),
    ("489", "https://n8n.io/workflows/489-create-a-deal-in-pipedrive"),
    ("488", "https://n8n.io/workflows/488-receive-updates-when-a-new-account-is-added-by-an-admin-in-activecampaign"),
    ("487", "https://n8n.io/workflows/487-receive-updates-for-events-in-clickup"),
    ("486", "https://n8n.io/workflows/486-receive-updates-for-events-in-chargebee"),
    ("485", "https://n8n.io/workflows/485-create-a-task-in-clickup"),
    ("484", "https://n8n.io/workflows/484-look-up-a-person-using-their-email-in-clearbit"),
    ("483", "https://n8n.io/workflows/483-create-a-new-customer-in-chargebee"),
    ("482", "https://n8n.io/workflows/482-insert-data-into-a-new-row-for-a-table-in-coda"),
    ("481", "https://n8n.io/workflows/481-create-a-new-task-in-todoist"),
    ("479", "https://n8n.io/workflows/479-execute-an-sql-query-in-microsoft-sql"),
]

async def main():
    print("=" * 80)
    print("🧪 SCRAPE-015: PRODUCTION TEST - 20 REAL WORKFLOWS")
    print("=" * 80)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Workflows to process: {len(TEST_WORKFLOWS)}")
    print("=" * 80)
    print()
    
    start_time = time.time()
    
    try:
        # Initialize repository and orchestrator
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
        print("🚀 Starting workflow processing...")
        print()
        
        results = await orchestrator.process_workflows(TEST_WORKFLOWS)
        
        elapsed = time.time() - start_time
        
        # Print results
        print()
        print("=" * 80)
        print("📊 PROCESSING RESULTS")
        print("=" * 80)
        
        successful = sum(1 for r in results if r.get('success', False))
        failed = len(results) - successful
        
        print(f"Total Workflows: {len(results)}")
        print(f"✅ Successful: {successful}")
        print(f"❌ Failed: {failed}")
        print(f"Success Rate: {(successful/len(results)*100):.1f}%")
        print(f"Time Elapsed: {elapsed:.1f}s")
        print(f"Average Time: {(elapsed/len(results)):.1f}s per workflow")
        print()
        
        # Show failed workflows
        if failed > 0:
            print("❌ Failed Workflows:")
            for r in results:
                if not r.get('success', False):
                    print(f"   • {r['workflow_id']}: {r.get('error', 'Unknown error')}")
            print()
        
        # Database verification
        print("=" * 80)
        print("🗄️  DATABASE VERIFICATION")
        print("=" * 80)
        
        with get_session() as session:
            from sqlalchemy import text, func
            
            # Count total workflows
            count = session.execute(text("SELECT COUNT(*) FROM workflows")).scalar()
            print(f"Total workflows in database: {count}")
            
            # Count successful scrapes
            successful_scrapes = session.execute(text(
                "SELECT COUNT(*) FROM workflows WHERE layer1_success AND layer2_success AND layer3_success"
            )).scalar()
            print(f"Fully scraped workflows: {successful_scrapes}")
            
            # Show recent workflows
            recent = session.execute(text(
                "SELECT workflow_id, extracted_at, layer1_success, layer2_success, layer3_success "
                "FROM workflows ORDER BY extracted_at DESC LIMIT 5"
            )).fetchall()
            
            print()
            print("Most recent workflows:")
            for row in recent:
                layers = f"L1:{'✅' if row[2] else '❌'} L2:{'✅' if row[3] else '❌'} L3:{'✅' if row[4] else '❌'}"
                print(f"   • {row[0]} - {layers}")
        
        print()
        print("=" * 80)
        print("✅ TEST COMPLETE - CHECK DATABASE VIEWER")
        print("=" * 80)
        print()
        print("📍 Access Points:")
        print(f"   • Database Viewer: http://localhost:5004")
        print(f"   • API Stats: http://localhost:5004/api/stats")
        print(f"   • Workflow Details: http://localhost:5004/workflow/{{id}}")
        print()
        print("🔍 Verify:")
        print(f"   1. Open http://localhost:5004")
        print(f"   2. Sort by 'Extracted At' (descending)")
        print(f"   3. Click on workflow IDs to see details")
        print(f"   4. Verify {successful} workflows scraped successfully")
        print()
        
        return 0 if successful >= 15 else 1  # Success if 15+ out of 20 scraped
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)


