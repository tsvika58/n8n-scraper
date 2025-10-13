#!/usr/bin/env python3
"""
Batch Size Optimization Test
Tests different batch sizes to find optimal performance
"""
import asyncio
import time
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.storage.database import get_session
from src.storage.repository import WorkflowRepository
from src.orchestrator.workflow_orchestrator import WorkflowOrchestrator

async def test_batch_size(batch_size, test_workflows):
    """Test a specific batch size"""
    print(f"\n🧪 Testing batch size: {batch_size}")
    print("-" * 40)
    
    with get_session() as session:
        repository = WorkflowRepository(session)
        
        # Create orchestrator with specific batch size
        orchestrator = WorkflowOrchestrator(
            repository=repository,
            rate_limit=2.0,
            max_retries=2,
            batch_size=batch_size
        )
        
        start_time = time.time()
        
        try:
            # Process test workflows
            results = await orchestrator.process_batch(test_workflows[:batch_size])
            
            end_time = time.time()
            duration = end_time - start_time
            
            # Calculate metrics
            total_workflows = len(results['results'])
            successful = sum(1 for r in results['results'] if r.get('success'))
            failed = total_workflows - successful
            success_rate = (successful / total_workflows * 100) if total_workflows > 0 else 0
            throughput = total_workflows / (duration / 60)  # workflows per minute
            
            print(f"  ✅ Completed: {total_workflows} workflows")
            print(f"  ✅ Success: {successful} ({success_rate:.1f}%)")
            print(f"  ❌ Failed: {failed}")
            print(f"  ⏱️  Duration: {duration:.1f}s")
            print(f"  📈 Throughput: {throughput:.1f} workflows/min")
            
            return {
                'batch_size': batch_size,
                'total_workflows': total_workflows,
                'successful': successful,
                'failed': failed,
                'success_rate': success_rate,
                'duration': duration,
                'throughput': throughput
            }
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
            return {
                'batch_size': batch_size,
                'error': str(e),
                'duration': time.time() - start_time
            }

async def main():
    """Run batch optimization tests"""
    print("🚀 Batch Size Optimization Test")
    print("=" * 50)
    
    # Test workflows (using higher IDs to avoid conflicts)
    test_workflows = [
        {'id': f'400{i}', 'url': f'https://n8n.io/workflows/400{i}'} 
        for i in range(1, 21)  # 20 test workflows
    ]
    
    # Test different batch sizes
    batch_sizes = [1, 3, 5, 10, 15]
    results = []
    
    for batch_size in batch_sizes:
        result = await test_batch_size(batch_size, test_workflows)
        results.append(result)
        
        # Small delay between tests
        await asyncio.sleep(2)
    
    # Summary
    print("\n📊 OPTIMIZATION SUMMARY")
    print("=" * 50)
    print(f"{'Batch Size':<12} {'Success Rate':<12} {'Throughput':<15} {'Duration':<10}")
    print("-" * 50)
    
    for result in results:
        if 'error' not in result:
            print(f"{result['batch_size']:<12} "
                  f"{result['success_rate']:<11.1f}% "
                  f"{result['throughput']:<14.1f} "
                  f"{result['duration']:<9.1f}s")
        else:
            print(f"{result['batch_size']:<12} ERROR")
    
    # Find optimal batch size
    valid_results = [r for r in results if 'error' not in r]
    if valid_results:
        # Optimize for throughput while maintaining good success rate
        best_result = max(valid_results, key=lambda x: x['throughput'] if x['success_rate'] > 80 else 0)
        
        print(f"\n🎯 RECOMMENDED BATCH SIZE: {best_result['batch_size']}")
        print(f"   • Throughput: {best_result['throughput']:.1f} workflows/min")
        print(f"   • Success rate: {best_result['success_rate']:.1f}%")
        print(f"   • Duration: {best_result['duration']:.1f}s")
        
        if best_result['batch_size'] != 5:
            print(f"\n💡 Consider updating default batch size from 5 to {best_result['batch_size']}")
    else:
        print("\n❌ No valid results to recommend optimal batch size")

if __name__ == "__main__":
    asyncio.run(main())



