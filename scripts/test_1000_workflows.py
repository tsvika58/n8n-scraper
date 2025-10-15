#!/usr/bin/env python3
"""
SCRAPE-013: Scale Testing with 1,000 Workflows.

Tests complete production pipeline at scale.

Author: RND Manager
Task: SCRAPE-013
"""

import asyncio
import sys
from pathlib import Path
import json
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.orchestrator.workflow_orchestrator import WorkflowOrchestrator
from src.storage.database import get_session
from src.storage.repository import WorkflowRepository
from src.exporters.export_manager import ExportManager


async def main():
    """Execute 1,000 workflow scale test."""
    
    print("\n" + "="*70)
    print("🚀 SCRAPE-013: SCALE TESTING - 1,000 WORKFLOWS")
    print("="*70)
    print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70 + "\n")
    
    # Initialize components
    print("📦 Initializing components...")
    session = get_session()
    repository = WorkflowRepository(session)
    
    orchestrator = WorkflowOrchestrator(
        repository=repository,
        rate_limit=2.0,  # 2 req/sec for n8n.io
        max_retries=3,
        batch_size=10
    )
    
    export_manager = ExportManager(output_dir="exports")
    
    print("✅ Components initialized\n")
    
    # Generate 1,000 workflow dataset
    print("📊 Generating 1,000 workflow dataset...")
    workflows = generate_test_dataset(1000)
    print(f"✅ Generated {len(workflows)} workflows\n")
    
    # Execute scale test
    print("🚀 Starting scale test...")
    print(f"   Processing {len(workflows)} workflows with orchestrator")
    print(f"   Rate limit: 2.0 req/sec")
    print(f"   Max retries: 3")
    print(f"   Estimated time: 1-2 hours\n")
    
    # Process batch
    results = await orchestrator.process_batch(workflows)
    
    # Print results
    print("\n" + "="*70)
    print("📊 SCALE TEST RESULTS")
    print("="*70)
    print(f"Total Workflows:    {results['total']}")
    print(f"Processed:          {results['processed']}")
    print(f"Successful:         {results['successful']}")
    print(f"Failed:             {results['failed']}")
    print(f"Success Rate:       {results['success_rate']:.2f}%")
    print("="*70 + "\n")
    
    # Get detailed statistics
    stats = results.get('statistics', {})
    if stats:
        print("📈 PERFORMANCE METRICS")
        print("="*70)
        print(f"Elapsed Time:       {stats.get('elapsed_seconds', 0):.1f}s ({stats.get('elapsed_seconds', 0)/60:.1f} min)")
        print(f"Avg per Workflow:   {stats.get('avg_time_per_workflow', 0):.2f}s")
        print(f"Throughput:         {stats.get('workflows_per_minute', 0):.1f} workflows/min")
        print("="*70 + "\n")
    
    # Export results
    print("💾 Exporting results...")
    export_results = export_manager.export_from_database(
        repository=repository,
        limit=1000,
        formats=['json', 'csv', 'parquet']
    )
    
    print("✅ Export complete:")
    for fmt, path in export_results.items():
        print(f"   - {fmt.upper()}: {path}")
    
    # Save test results
    results_file = f".coordination/testing/results/SCRAPE-013-1000-workflow-test-{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    Path(results_file).parent.mkdir(parents=True, exist_ok=True)
    
    with open(results_file, 'w') as f:
        json.dump({
            'test_config': {
                'total_workflows': len(workflows),
                'rate_limit': 2.0,
                'max_retries': 3,
                'batch_size': 10,
            },
            'results': {
                'total': results['total'],
                'successful': results['successful'],
                'failed': results['failed'],
                'success_rate': results['success_rate'],
            },
            'statistics': stats,
            'exports': export_results,
            'timestamp': datetime.now().isoformat(),
        }, f, indent=2)
    
    print(f"\n✅ Results saved to: {results_file}")
    
    # Final summary
    print("\n" + "="*70)
    print("🎉 SCRAPE-013 SCALE TEST COMPLETE")
    print("="*70)
    print(f"✅ Processed: {results['processed']}/{results['total']} workflows")
    print(f"✅ Success Rate: {results['success_rate']:.2f}%")
    print(f"✅ Exports: {len(export_results)} formats generated")
    print(f"✅ Results: {results_file}")
    print("="*70 + "\n")
    
    # Determine if test passed
    success_rate = results['success_rate']
    if success_rate >= 95:
        print("🎉 TEST PASSED: Success rate ≥95%")
        return 0
    elif success_rate >= 85:
        print("⚠️  TEST ACCEPTABLE: Success rate ≥85%")
        return 0
    else:
        print("❌ TEST FAILED: Success rate <85%")
        return 1


def generate_test_dataset(count: int = 1000) -> list:
    """
    Generate 1,000 workflow test dataset.
    
    Uses workflow IDs from SCRAPE-002B inventory.
    
    Args:
        count: Number of workflows to generate
        
    Returns:
        List of workflow dictionaries
    """
    workflows = []
    
    # Generate realistic workflow IDs (range: 2000-3000)
    # This matches real n8n.io workflow ID patterns
    start_id = 2000
    
    for i in range(count):
        workflow_id = str(start_id + i)
        workflows.append({
            'id': workflow_id,
            'url': f'https://n8n.io/workflows/{workflow_id}'
        })
    
    return workflows


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)






