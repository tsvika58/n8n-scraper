#!/usr/bin/env python3
"""
Comprehensive Preparation & Validation Script

This script validates the system is ready for production scraping with
the expanded comprehensive scraping capabilities (7 layers, 200+ fields).

Performs the same level of validation as the original pre-scraping checklist.

Author: RND Team - Comprehensive Scraping Expansion
Date: October 12, 2025
"""

import sys
import asyncio
from pathlib import Path
from datetime import datetime
import time

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.orchestrator.e2e_pipeline import E2EPipeline
from src.storage.database import get_session
from src.storage.repository import WorkflowRepository


async def test_comprehensive_workflows():
    """Test 20 diverse workflows to validate the comprehensive pipeline."""
    print("=" * 80)
    print("🧪 PHASE 1: COMPREHENSIVE WORKFLOW TESTING")
    print("=" * 80)
    print()
    
    # Test 20 diverse workflows (mix of simple, medium, complex)
    test_workflows = [
        # Simple workflows (5-15 nodes)
        {'id': '2462', 'url': 'https://n8n.io/workflows/2462', 'complexity': 'simple'},
        {'id': '2463', 'url': 'https://n8n.io/workflows/2463', 'complexity': 'simple'},
        {'id': '2464', 'url': 'https://n8n.io/workflows/2464', 'complexity': 'simple'},
        {'id': '2465', 'url': 'https://n8n.io/workflows/2465', 'complexity': 'simple'},
        {'id': '2466', 'url': 'https://n8n.io/workflows/2466', 'complexity': 'simple'},
        
        # Medium workflows (15-30 nodes)
        {'id': '2467', 'url': 'https://n8n.io/workflows/2467', 'complexity': 'medium'},
        {'id': '2468', 'url': 'https://n8n.io/workflows/2468', 'complexity': 'medium'},
        {'id': '2469', 'url': 'https://n8n.io/workflows/2469', 'complexity': 'medium'},
        {'id': '2470', 'url': 'https://n8n.io/workflows/2470', 'complexity': 'medium'},
        {'id': '2471', 'url': 'https://n8n.io/workflows/2471', 'complexity': 'medium'},
        
        # Complex workflows (30+ nodes)
        {'id': '2472', 'url': 'https://n8n.io/workflows/2472', 'complexity': 'complex'},
        {'id': '2473', 'url': 'https://n8n.io/workflows/2473', 'complexity': 'complex'},
        {'id': '2474', 'url': 'https://n8n.io/workflows/2474', 'complexity': 'complex'},
        {'id': '2475', 'url': 'https://n8n.io/workflows/2475', 'complexity': 'complex'},
        {'id': '2476', 'url': 'https://n8n.io/workflows/2476', 'complexity': 'complex'},
        
        # Edge cases
        {'id': '2477', 'url': 'https://n8n.io/workflows/2477', 'complexity': 'edge'},
        {'id': '2478', 'url': 'https://n8n.io/workflows/2478', 'complexity': 'edge'},
        {'id': '2479', 'url': 'https://n8n.io/workflows/2479', 'complexity': 'edge'},
        {'id': '2480', 'url': 'https://n8n.io/workflows/2480', 'complexity': 'edge'},
        {'id': '2481', 'url': 'https://n8n.io/workflows/2481', 'complexity': 'edge'},
    ]
    
    print(f"📋 Testing {len(test_workflows)} diverse workflows:")
    print()
    
    # Initialize pipeline
    print("🔧 Initializing E2E Pipeline...")
    pipeline = E2EPipeline()
    print("✅ Pipeline initialized")
    print()
    
    # Track results
    results = []
    layer_stats = {f'layer{i}': {'success': 0, 'failed': 0} for i in range(1, 8)}
    
    with get_session() as session:
        repository = WorkflowRepository(session)
        
        for i, workflow in enumerate(test_workflows, 1):
            workflow_id = workflow['id']
            url = workflow['url']
            complexity = workflow['complexity']
            
            print(f"🔄 [{i}/{len(test_workflows)}] Testing {workflow_id} ({complexity})...")
            
            try:
                start_time = time.time()
                result = await pipeline.process_workflow(workflow_id, url)
                end_time = time.time()
                processing_time = end_time - start_time
                
                # Track layer success
                layers = result.get('layers', {})
                for layer_name, layer_data in layers.items():
                    if layer_data and layer_data.get('success'):
                        layer_stats[layer_name]['success'] += 1
                    else:
                        layer_stats[layer_name]['failed'] += 1
                
                # Save to database
                workflow_obj = repository.create_workflow(workflow_id, url, result)
                
                results.append({
                    'workflow_id': workflow_id,
                    'complexity': complexity,
                    'success': result.get('success', False),
                    'processing_time': processing_time,
                    'layers': {k: (v.get('success') if v else False) for k, v in layers.items()}
                })
                
                print(f"   ✅ Completed in {processing_time:.2f}s")
                
            except Exception as e:
                print(f"   ❌ Error: {e}")
                results.append({
                    'workflow_id': workflow_id,
                    'complexity': complexity,
                    'success': False,
                    'error': str(e)
                })
            
            print()
    
    # Generate report
    print("=" * 80)
    print("📊 VALIDATION REPORT")
    print("=" * 80)
    print()
    
    successful = sum(1 for r in results if r.get('success'))
    total = len(results)
    
    print(f"📈 Overall Success Rate: {successful}/{total} ({successful/total*100:.1f}%)")
    print()
    
    print("🎯 Layer Performance:")
    for layer_name, stats in layer_stats.items():
        total_attempts = stats['success'] + stats['failed']
        success_rate = (stats['success'] / total_attempts * 100) if total_attempts > 0 else 0
        print(f"   {layer_name}: {stats['success']}/{total_attempts} ({success_rate:.1f}%)")
    print()
    
    # Performance by complexity
    complexity_stats = {}
    for r in results:
        if r.get('success'):
            comp = r['complexity']
            if comp not in complexity_stats:
                complexity_stats[comp] = []
            complexity_stats[comp].append(r['processing_time'])
    
    print("⏱️  Performance by Complexity:")
    for comp, times in complexity_stats.items():
        avg_time = sum(times) / len(times)
        print(f"   {comp}: {avg_time:.2f}s average ({len(times)} workflows)")
    print()
    
    # Readiness assessment
    print("🚦 READINESS ASSESSMENT:")
    print()
    
    checks = []
    checks.append(("20+ workflows tested", total >= 20, "CRITICAL"))
    checks.append(("Success rate > 80%", successful/total > 0.8, "CRITICAL"))
    checks.append(("Layer 1 > 90%", layer_stats['layer1']['success']/total > 0.9, "CRITICAL"))
    checks.append(("Layer 2 > 80%", layer_stats['layer2']['success']/total > 0.8, "CRITICAL"))
    checks.append(("Layer 3 > 80%", layer_stats['layer3']['success']/total > 0.8, "CRITICAL"))
    checks.append(("Layer 4 > 50%", layer_stats['layer4']['success']/total > 0.5, "HIGH"))
    checks.append(("Avg time < 20s", sum(complexity_stats.get('simple', [0])) / max(len(complexity_stats.get('simple', [1])), 1) < 20, "HIGH"))
    
    all_critical_passed = all(passed for _, passed, priority in checks if priority == "CRITICAL")
    all_high_passed = all(passed for _, passed, priority in checks if priority == "HIGH")
    
    for check, passed, priority in checks:
        status = "✅" if passed else "❌"
        print(f"   {status} [{priority}] {check}")
    
    print()
    
    if all_critical_passed and all_high_passed:
        print("🎉 PHASE 1 VALIDATION: ✅ PASSED")
        print("   System ready for Phase 2 (Infrastructure)")
        return True
    elif all_critical_passed:
        print("⚠️  PHASE 1 VALIDATION: 🟡 PARTIAL PASS")
        print("   Critical checks passed, but some high-priority checks failed")
        print("   Consider improvements before production")
        return True
    else:
        print("❌ PHASE 1 VALIDATION: ❌ FAILED")
        print("   Critical checks failed - NOT ready for production")
        return False


async def main():
    """Main validation workflow."""
    print("=" * 80)
    print("🚀 COMPREHENSIVE PREPARATION & VALIDATION")
    print("=" * 80)
    print()
    print("This script will validate the system is ready for production")
    print("scraping with the expanded comprehensive scraping capabilities.")
    print()
    print("=" * 80)
    print()
    
    # Phase 1: Test workflows
    phase1_passed = await test_comprehensive_workflows()
    
    if not phase1_passed:
        print()
        print("🔴 VALIDATION FAILED")
        print("=" * 80)
        print("System is NOT ready for production scraping.")
        print("Review the validation report and address failures.")
        print("=" * 80)
        return False
    
    print()
    print("✅ PHASE 1 COMPLETE")
    print("=" * 80)
    print()
    print("📋 NEXT STEPS:")
    print("   1. ✅ Phase 1 (Testing) - COMPLETE")
    print("   2. ⏳ Phase 2 (Infrastructure) - Update monitoring, backup DB, rebuild Docker")
    print("   3. ⏳ Phase 3 (Quality) - Validate data extraction accuracy")
    print("   4. ⏳ Phase 4 (Production Prep) - Document procedures, set up alerts")
    print()
    print("Continue with Phase 2 preparation:")
    print("   ./scripts/infrastructure_prep.sh")
    print()
    
    return True


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)





