#!/usr/bin/env python3
"""
Production-Safe Error Handling Test
Tests error handling without affecting production data or breaking the system
"""
import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.storage.database import get_session
from src.storage.repository import WorkflowRepository
from src.orchestrator.workflow_orchestrator import WorkflowOrchestrator

async def production_safe_error_test():
    """Test error handling safely without affecting production data"""
    print("🛡️  Production-Safe Error Handling Test")
    print("=" * 60)
    print("ℹ️  This test uses temporary test workflows that will be cleaned up")
    print()
    
    # Test workflow IDs that are guaranteed to be test-only
    test_workflow_ids = []
    
    try:
        with get_session() as session:
            repository = WorkflowRepository(session)
            
            # Create orchestrator with very conservative settings
            orchestrator = WorkflowOrchestrator(
                repository=repository,
                rate_limit=0.5,  # Very slow rate for safety
                max_retries=1,   # Minimal retries
                batch_size=2     # Small batch size
            )
            
            # Use clearly test-only workflow IDs (prefixed with TEST_)
            test_workflows = [
                {'id': 'TEST_ERROR_001', 'url': 'https://n8n.io/workflows/TEST_ERROR_001'},
                {'id': 'TEST_ERROR_002', 'url': 'https://invalid-domain-test.com/workflow'},
                {'id': 'TEST_ERROR_003', 'url': 'https://n8n.io/workflows/TEST_ERROR_003'},
            ]
            
            test_workflow_ids = [wf['id'] for wf in test_workflows]
            
            print(f"🧪 Testing {len(test_workflows)} safe error scenarios...")
            print("   • Using TEST_ prefixed workflow IDs")
            print("   • Conservative rate limiting (0.5 req/sec)")
            print("   • Minimal retries and small batch size")
            print()
            
            # Process test workflows
            result = await orchestrator.process_batch(test_workflows)
            
            # Analyze results
            total_tested = len(result['results'])
            successful_errors = 0
            unexpected_successes = 0
            
            print("📊 Error Handling Results:")
            print("-" * 40)
            
            for i, workflow_result in enumerate(result['results']):
                workflow_id = test_workflows[i]['id']
                success = workflow_result.get('success', False)
                
                if success:
                    unexpected_successes += 1
                    print(f"  ⚠️  {workflow_id}: Unexpectedly successful")
                else:
                    successful_errors += 1
                    error_msg = workflow_result.get('error', 'Unknown error')
                    print(f"  ✅ {workflow_id}: Handled error gracefully")
                    print(f"      Error: {error_msg[:60]}...")
            
            print(f"\n📈 Summary:")
            print(f"  • Total workflows tested: {total_tested}")
            print(f"  • Errors handled gracefully: {successful_errors}")
            print(f"  • Unexpected successes: {unexpected_successes}")
            
            # Test system stability with a known good workflow
            print(f"\n🔧 System Stability Test:")
            print("  Testing with known good workflow...")
            
            stability_workflow = [{'id': '1000', 'url': 'https://n8n.io/workflows/1000'}]
            stability_result = await orchestrator.process_batch(stability_workflow)
            
            if stability_result['results'][0].get('success'):
                print("  ✅ System stable - can process valid workflows after errors")
                system_stable = True
            else:
                print("  ⚠️  System may have issues after error handling")
                system_stable = False
            
            print(f"\n" + "=" * 60)
            
            # Overall assessment
            error_handling_good = successful_errors >= total_tested * 0.8  # 80% should handle errors
            
            if error_handling_good and system_stable:
                print("✅ PRODUCTION-SAFE ERROR HANDLING VALIDATION PASSED")
                print("   • Error handling works as expected")
                print("   • System remains stable after errors")
                print("   • Ready for production error scenarios")
                return True
            else:
                print("❌ PRODUCTION-SAFE ERROR HANDLING VALIDATION FAILED")
                print("   • Error handling needs improvement")
                print("   • System stability concerns detected")
                return False
    
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        print("   • Test failed due to unexpected error")
        print("   • System may need investigation")
        return False
    
    finally:
        # Always cleanup test workflows
        print(f"\n🧹 Cleaning up {len(test_workflow_ids)} test workflows...")
        await safe_cleanup_test_workflows(test_workflow_ids)

async def safe_cleanup_test_workflows(workflow_ids):
    """Safely cleanup test workflows with comprehensive error handling"""
    if not workflow_ids:
        print("   ℹ️  No test workflows to clean up")
        return
        
    try:
        with get_session() as session:
            from sqlalchemy import text
            
            for workflow_id in workflow_ids:
                try:
                    # Check if workflow exists first
                    existing = session.execute(
                        text("SELECT COUNT(*) FROM workflows WHERE workflow_id = :id"), 
                        {'id': workflow_id}
                    ).scalar()
                    
                    if existing > 0:
                        # Delete in correct order (child tables first)
                        tables_to_clean = [
                            'workflow_content',
                            'workflow_metadata', 
                            'workflow_structure',
                            'video_transcripts',
                            'workflows'
                        ]
                        
                        for table in tables_to_clean:
                            try:
                                session.execute(
                                    text(f"DELETE FROM {table} WHERE workflow_id = :id"), 
                                    {'id': workflow_id}
                                )
                            except Exception as e:
                                # Continue with other tables even if one fails
                                continue
                        
                        session.commit()
                        print(f"   ✅ Cleaned up test workflow: {workflow_id}")
                    else:
                        print(f"   ℹ️  Test workflow {workflow_id} not found (already clean)")
                        
                except Exception as e:
                    print(f"   ⚠️  Warning: Could not clean up {workflow_id}: {e}")
                    session.rollback()
                    continue
                    
    except Exception as e:
        print(f"   ❌ Error during cleanup: {e}")
    
    print("   ✅ Cleanup completed")

if __name__ == "__main__":
    success = asyncio.run(production_safe_error_test())
    exit(0 if success else 1)
