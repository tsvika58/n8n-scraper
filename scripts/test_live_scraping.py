#!/usr/bin/env python3
"""
Test Live Scraping Script
Demonstrates the real-time dashboard during active scraping
"""

import asyncio
import time
import requests
from datetime import datetime
from src.orchestrator.workflow_orchestrator import WorkflowOrchestrator
from src.storage.repository import WorkflowRepository

async def test_live_scraping():
    """Test live scraping with real workflows"""
    print("🚀 Starting Live Scraping Test...")
    print("=" * 60)
    
    # Initialize components
    repository = WorkflowRepository()
    orchestrator = WorkflowOrchestrator(
        repository=repository,
        batch_size=2,  # Small batch for testing
        max_retries=1,
        rate_limit=1.0  # Slower rate for visibility
    )
    
    # Get some workflows that failed (quality_score = 0 or NULL)
    test_workflows = []
    
    # Add some test workflows
    test_workflows = [
        {"id": "1000", "url": "https://n8n.io/workflows/1000"},
        {"id": "1001", "url": "https://n8n.io/workflows/1001"},
        {"id": "1002", "url": "https://n8n.io/workflows/1002"},
    ]
    
    print(f"📋 Testing with {len(test_workflows)} workflows:")
    for wf in test_workflows:
        print(f"   #{wf['id']}: {wf['url']}")
    
    print(f"\n🌐 Dashboard URL: http://localhost:5001")
    print(f"📊 Watch the LIVE SCRAPING STATUS section!")
    print(f"⏰ Starting in 3 seconds...")
    
    for i in range(3, 0, -1):
        print(f"   {i}...")
        time.sleep(1)
    
    print(f"\n🔥 STARTING LIVE SCRAPING...")
    print("=" * 60)
    
    # Process workflows one by one to show live updates
    for i, workflow in enumerate(test_workflows, 1):
        print(f"\n📝 Processing Workflow {i}/{len(test_workflows)}: #{workflow['id']}")
        
        try:
            # Process single workflow
            result = await orchestrator.process_workflow(workflow)
            
            if result:
                print(f"   ✅ Success: Quality {result.get('quality', {}).get('overall_score', 0):.1f}")
            else:
                print(f"   ❌ Failed")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # Wait a bit to see live updates
        print(f"   ⏳ Waiting 5 seconds for dashboard updates...")
        time.sleep(5)
    
    print(f"\n🎉 Live Scraping Test Complete!")
    print(f"📊 Check dashboard: http://localhost:5001")

if __name__ == "__main__":
    asyncio.run(test_live_scraping())

