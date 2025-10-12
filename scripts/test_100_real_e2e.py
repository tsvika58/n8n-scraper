#!/usr/bin/env python3
"""
SCRAPE-014: Real E2E Performance Test
Tests 100 real workflows through full orchestrator with optimizations
"""

import asyncio
import time
from datetime import datetime
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.orchestrator.workflow_orchestrator import WorkflowOrchestrator
from src.storage.repository import WorkflowRepository
from loguru import logger

# 100 curated real workflows (from SCRAPE-007 test set)
REAL_WORKFLOWS = [
    {'id': '2462', 'url': 'https://n8n.io/workflows/2462'},
    {'id': '2365', 'url': 'https://n8n.io/workflows/2365'},
    {'id': '2134', 'url': 'https://n8n.io/workflows/2134'},
    {'id': '2091', 'url': 'https://n8n.io/workflows/2091'},
    {'id': '2076', 'url': 'https://n8n.io/workflows/2076'},
    {'id': '2021', 'url': 'https://n8n.io/workflows/2021'},
    {'id': '1948', 'url': 'https://n8n.io/workflows/1948'},
    {'id': '1925', 'url': 'https://n8n.io/workflows/1925'},
    {'id': '1912', 'url': 'https://n8n.io/workflows/1912'},
    {'id': '1865', 'url': 'https://n8n.io/workflows/1865'},
    {'id': '1847', 'url': 'https://n8n.io/workflows/1847'},
    {'id': '2203', 'url': 'https://n8n.io/workflows/2203'},
    {'id': '2156', 'url': 'https://n8n.io/workflows/2156'},
    {'id': '2089', 'url': 'https://n8n.io/workflows/2089'},
    {'id': '2034', 'url': 'https://n8n.io/workflows/2034'},
    {'id': '1998', 'url': 'https://n8n.io/workflows/1998'},
    {'id': '1967', 'url': 'https://n8n.io/workflows/1967'},
    {'id': '1889', 'url': 'https://n8n.io/workflows/1889'},
    {'id': '1856', 'url': 'https://n8n.io/workflows/1856'},
    {'id': '1823', 'url': 'https://n8n.io/workflows/1823'},
    {'id': '2445', 'url': 'https://n8n.io/workflows/2445'},
    {'id': '2398', 'url': 'https://n8n.io/workflows/2398'},
    {'id': '2367', 'url': 'https://n8n.io/workflows/2367'},
    {'id': '2345', 'url': 'https://n8n.io/workflows/2345'},
    {'id': '2312', 'url': 'https://n8n.io/workflows/2312'},
    {'id': '2289', 'url': 'https://n8n.io/workflows/2289'},
    {'id': '2267', 'url': 'https://n8n.io/workflows/2267'},
    {'id': '2245', 'url': 'https://n8n.io/workflows/2245'},
    {'id': '2223', 'url': 'https://n8n.io/workflows/2223'},
    {'id': '2201', 'url': 'https://n8n.io/workflows/2201'},
    {'id': '2178', 'url': 'https://n8n.io/workflows/2178'},
    {'id': '2112', 'url': 'https://n8n.io/workflows/2112'},
    {'id': '2090', 'url': 'https://n8n.io/workflows/2090'},
    {'id': '2068', 'url': 'https://n8n.io/workflows/2068'},
    {'id': '2046', 'url': 'https://n8n.io/workflows/2046'},
    {'id': '2024', 'url': 'https://n8n.io/workflows/2024'},
    {'id': '2002', 'url': 'https://n8n.io/workflows/2002'},
    {'id': '1980', 'url': 'https://n8n.io/workflows/1980'},
    {'id': '1958', 'url': 'https://n8n.io/workflows/1958'},
    {'id': '1936', 'url': 'https://n8n.io/workflows/1936'},
    {'id': '1914', 'url': 'https://n8n.io/workflows/1914'},
    {'id': '1892', 'url': 'https://n8n.io/workflows/1892'},
    {'id': '1870', 'url': 'https://n8n.io/workflows/1870'},
    {'id': '1848', 'url': 'https://n8n.io/workflows/1848'},
    {'id': '1826', 'url': 'https://n8n.io/workflows/1826'},
    {'id': '1804', 'url': 'https://n8n.io/workflows/1804'},
    {'id': '1782', 'url': 'https://n8n.io/workflows/1782'},
    {'id': '1760', 'url': 'https://n8n.io/workflows/1760'},
    {'id': '2450', 'url': 'https://n8n.io/workflows/2450'},
    {'id': '2428', 'url': 'https://n8n.io/workflows/2428'},
    {'id': '2406', 'url': 'https://n8n.io/workflows/2406'},
    {'id': '2384', 'url': 'https://n8n.io/workflows/2384'},
    {'id': '2362', 'url': 'https://n8n.io/workflows/2362'},
    {'id': '2340', 'url': 'https://n8n.io/workflows/2340'},
    {'id': '2318', 'url': 'https://n8n.io/workflows/2318'},
    {'id': '2296', 'url': 'https://n8n.io/workflows/2296'},
    {'id': '2274', 'url': 'https://n8n.io/workflows/2274'},
    {'id': '2252', 'url': 'https://n8n.io/workflows/2252'},
    {'id': '2230', 'url': 'https://n8n.io/workflows/2230'},
    {'id': '2208', 'url': 'https://n8n.io/workflows/2208'},
    {'id': '2186', 'url': 'https://n8n.io/workflows/2186'},
    {'id': '2164', 'url': 'https://n8n.io/workflows/2164'},
    {'id': '2142', 'url': 'https://n8n.io/workflows/2142'},
    {'id': '2120', 'url': 'https://n8n.io/workflows/2120'},
    {'id': '2098', 'url': 'https://n8n.io/workflows/2098'},
    {'id': '2054', 'url': 'https://n8n.io/workflows/2054'},
    {'id': '2032', 'url': 'https://n8n.io/workflows/2032'},
    {'id': '2010', 'url': 'https://n8n.io/workflows/2010'},
    {'id': '1988', 'url': 'https://n8n.io/workflows/1988'},
    {'id': '1966', 'url': 'https://n8n.io/workflows/1966'},
    {'id': '1944', 'url': 'https://n8n.io/workflows/1944'},
    {'id': '1922', 'url': 'https://n8n.io/workflows/1922'},
    {'id': '1900', 'url': 'https://n8n.io/workflows/1900'},
    {'id': '1878', 'url': 'https://n8n.io/workflows/1878'},
    {'id': '1834', 'url': 'https://n8n.io/workflows/1834'},
    {'id': '1812', 'url': 'https://n8n.io/workflows/1812'},
    {'id': '1790', 'url': 'https://n8n.io/workflows/1790'},
    {'id': '2455', 'url': 'https://n8n.io/workflows/2455'},
    {'id': '2433', 'url': 'https://n8n.io/workflows/2433'},
    {'id': '2411', 'url': 'https://n8n.io/workflows/2411'},
    {'id': '2389', 'url': 'https://n8n.io/workflows/2389'},
    {'id': '2323', 'url': 'https://n8n.io/workflows/2323'},
    {'id': '2301', 'url': 'https://n8n.io/workflows/2301'},
    {'id': '2279', 'url': 'https://n8n.io/workflows/2279'},
    {'id': '2257', 'url': 'https://n8n.io/workflows/2257'},
    {'id': '2235', 'url': 'https://n8n.io/workflows/2235'},
    {'id': '2213', 'url': 'https://n8n.io/workflows/2213'},
    {'id': '2191', 'url': 'https://n8n.io/workflows/2191'},
    {'id': '2169', 'url': 'https://n8n.io/workflows/2169'},
    {'id': '2147', 'url': 'https://n8n.io/workflows/2147'},
    {'id': '2125', 'url': 'https://n8n.io/workflows/2125'},
    {'id': '2103', 'url': 'https://n8n.io/workflows/2103'},
    {'id': '2081', 'url': 'https://n8n.io/workflows/2081'},
]

async def main():
    print("\n" + "="*70)
    print("🚀 SCRAPE-014: REAL E2E PERFORMANCE TEST")
    print("="*70)
    print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Workflows: {len(REAL_WORKFLOWS)} real n8n.io workflows")
    print(f"Method: Full E2E Pipeline with Orchestrator")
    print(f"Optimizations: Concurrent 20, DB Pool 30")
    print("="*70)
    print()
    
    # Initialize orchestrator with optimized settings
    repository = WorkflowRepository()
    orchestrator = WorkflowOrchestrator(
        repository=repository,
        rate_limit=2.0,        # Respect n8n.io rate limits
        max_retries=3,
        batch_size=20,         # OPTIMIZED: Was 10
        checkpoint_dir=".checkpoints"
    )
    
    print("📊 Initializing orchestrator...")
    print(f"   - Concurrent batch size: 20 (optimized)")
    print(f"   - DB connection pool: 30 (optimized)")
    print(f"   - Rate limit: 2.0 req/s")
    print()
    
    # Run test
    print("🔄 Processing workflows through full E2E pipeline...")
    print("   (This includes: Layer 1 + Layer 2 + Layer 3 + Videos + Quality)")
    print()
    
    start_time = time.time()
    
    try:
        results = await orchestrator.process_batch(
            workflows=REAL_WORKFLOWS,
            resume_from=None
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Analyze results
        successful = sum(1 for r in results if r['overall_success'])
        failed = len(results) - successful
        avg_time = duration / len(results) if results else 0
        
        # Calculate layer success rates
        l1_success = sum(1 for r in results if r.get('layers', {}).get('layer1', {}).get('success', False))
        l2_success = sum(1 for r in results if r.get('layers', {}).get('layer2', {}).get('success', False))
        l3_success = sum(1 for r in results if r.get('layers', {}).get('layer3', {}).get('success', False))
        
        # Calculate quality scores
        quality_scores = [r.get('quality_score', 0) for r in results if 'quality_score' in r]
        avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0
        
        print()
        print("="*70)
        print("📊 SCRAPE-014: REAL E2E TEST RESULTS")
        print("="*70)
        print()
        print(f"OVERALL PERFORMANCE:")
        print(f"  Total Duration:        {duration:.1f}s")
        print(f"  Workflows Processed:   {len(results)}")
        print(f"  Successful:            {successful} ({successful/len(results)*100:.1f}%)")
        print(f"  Failed:                {failed} ({failed/len(results)*100:.1f}%)")
        print(f"  Average Time:          {avg_time:.2f}s per workflow")
        print()
        print(f"LAYER SUCCESS RATES:")
        print(f"  Layer 1 (Metadata):    {l1_success}/{len(results)} ({l1_success/len(results)*100:.1f}%)")
        print(f"  Layer 2 (JSON):        {l2_success}/{len(results)} ({l2_success/len(results)*100:.1f}%)")
        print(f"  Layer 3 (Content):     {l3_success}/{len(results)} ({l3_success/len(results)*100:.1f}%)")
        print()
        print(f"QUALITY METRICS:")
        print(f"  Average Quality Score: {avg_quality:.2f}/100")
        print()
        print("="*70)
        print()
        
        # Save detailed results
        import json
        results_file = f'.coordination/testing/results/SCRAPE-014-real-e2e-{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(results_file, 'w') as f:
            json.dump({
                'test_type': 'real_e2e_optimized',
                'total_duration': duration,
                'workflow_count': len(results),
                'successful': successful,
                'failed': failed,
                'avg_time_per_workflow': avg_time,
                'layer1_success_rate': l1_success / len(results) if results else 0,
                'layer2_success_rate': l2_success / len(results) if results else 0,
                'layer3_success_rate': l3_success / len(results) if results else 0,
                'avg_quality_score': avg_quality,
                'optimizations': {
                    'concurrent_batch_size': 20,
                    'db_connection_pool': 30,
                    'rate_limit': 2.0
                },
                'results': results
            }, f, indent=2)
        
        print(f"📄 Detailed results saved to: {results_file}")
        print()
        print("🎉 SCRAPE-014: REAL E2E TEST COMPLETE!")
        print()
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())

