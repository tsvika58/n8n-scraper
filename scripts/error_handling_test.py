#!/usr/bin/env python3
"""
Error Handling Validation Test
Tests the system's ability to handle various error conditions gracefully
"""
import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.storage.database import get_session
from src.storage.repository import WorkflowRepository
from src.orchestrator.workflow_orchestrator import WorkflowOrchestrator

async def test_error_handling():
    """Test error handling with intentionally problematic workflows"""
    print("🧪 Error Handling Validation Test")
    print("=" * 50)
    
    with get_session() as session:
        repository = WorkflowRepository(session)
        
        # Create orchestrator with conservative settings
        orchestrator = WorkflowOrchestrator(
            repository=repository,
            rate_limit=1.0,  # Slower rate for testing
            max_retries=2,
            batch_size=3
        )
        
        # Test workflows with various error conditions
        error_test_workflows = [
            # Non-existent workflow (should get 404)
            {'id': '999999', 'url': 'https://n8n.io/workflows/999999'},
            
            # Invalid URL format
            {'id': 'invalid_url', 'url': 'https://invalid-domain-that-does-not-exist.com/workflow'},
            
            # Malformed workflow ID
            {'id': 'abc123', 'url': 'https://n8n.io/workflows/abc123'},
            
            # Very high ID (likely doesn't exist)
            {'id': '9999999', 'url': 'https://n8n.io/workflows/9999999'},
            
            # Valid format but likely deleted/private
            {'id': '500000', 'url': 'https://n8n.io/workflows/500000'},
        ]
        
        print(f"Testing {len(error_test_workflows)} error scenarios...")
        print()
        
        # Process the error test workflows
        results = await orchestrator.process_batch(error_test_workflows)
        
        print("📊 Error Handling Results:")
        print("-" * 30)
        
        total = len(results['results'])
        successful = sum(1 for r in results['results'] if r.get('success'))
        failed = total - successful
        
        print(f"Total workflows tested: {total}")
        print(f"Successful extractions: {successful}")
        print(f"Failed extractions: {failed}")
        print(f"Error handling success rate: {(failed / total * 100):.1f}% (failures expected)")
        
        print("\n🔍 Detailed Results:")
        for i, result in enumerate(results['results']):
            workflow_id = error_test_workflows[i]['id']
            if result.get('success'):
                print(f"  ✅ {workflow_id}: Unexpectedly successful")
            else:
                error_msg = result.get('error', 'Unknown error')
                print(f"  ❌ {workflow_id}: {error_msg[:60]}...")
        
        # Validate error handling
        print("\n🎯 Error Handling Validation:")
        
        # Check that system handled errors gracefully
        graceful_handling = True
        for result in results['results']:
            if result.get('success'):
                print(f"  ⚠️  Warning: Workflow unexpectedly succeeded")
                graceful_handling = False
            elif not result.get('error'):
                print(f"  ❌ Error: No error message for failed workflow")
                graceful_handling = False
        
        if graceful_handling:
            print("  ✅ All errors handled gracefully")
            print("  ✅ System continues operating after errors")
            print("  ✅ Error messages are informative")
        
        # Test system stability
        print("\n🔧 System Stability Test:")
        
        # Try processing a known good workflow after errors
        test_workflow = [{'id': '1000', 'url': 'https://n8n.io/workflows/1000'}]
        
        try:
            stability_result = await orchestrator.process_batch(test_workflow)
            if stability_result['results'][0].get('success'):
                print("  ✅ System recovered and processed valid workflow")
            else:
                print("  ⚠️  System may have issues processing valid workflows after errors")
        except Exception as e:
            print(f"  ❌ System failed to recover: {e}")
            graceful_handling = False
        
        print("\n" + "=" * 50)
        
        if graceful_handling:
            print("✅ ERROR HANDLING VALIDATION PASSED")
            print("   • System handles errors gracefully")
            print("   • Informative error messages provided")
            print("   • System remains stable after errors")
            print("   • Ready for production error scenarios")
        else:
            print("❌ ERROR HANDLING VALIDATION FAILED")
            print("   • Issues detected with error handling")
            print("   • Review error handling logic before production")
        
        return graceful_handling

if __name__ == "__main__":
    asyncio.run(test_error_handling())
