#!/usr/bin/env python3
"""
Test fallback API on CORRECT list of failed workflows.
This tests the actual 20 workflows that failed in SCRAPE-007 test.
"""

import asyncio
import sys
import os

# Add project root to path
sys.path.append('.')

from src.scrapers.layer2_json import WorkflowJSONExtractor

async def test_correct_failed_list():
    """Test fallback API on the CORRECT list of failed workflows."""
    
    print('🔍 TESTING CORRECT 20 FAILED WORKFLOWS WITH FALLBACK API')
    print('=' * 60)
    
    extractor = WorkflowJSONExtractor()
    
    # CORRECT list of actually failed workflows from SCRAPE-007 test
    failed_workflows = [
        '2021', '1847', '2091', '1925', '1876', '1912', '2203', '1865', 
        '2268', '1893', '1935', '1854', '1982', '2296', '1904', '1843', 
        '1965', '1887', '1812', '2229'
    ]
    
    print(f'📊 Testing {len(failed_workflows)} CORRECT failed workflows...')
    print(f'   (These are the workflows that actually failed in SCRAPE-007 test)')
    print()
    
    fallback_success = 0
    fallback_failed = 0
    fallback_errors = []
    
    # Test first 10 workflows (representative sample)
    test_count = 10
    for i, wf_id in enumerate(failed_workflows[:test_count]):
        print(f'[{i+1}/{test_count}] Testing workflow {wf_id}...')
        try:
            result = await extractor.extract(wf_id)
            if result['success']:
                fallback_success += 1
                node_count = len(result.get('data', {}).get('workflow', {}).get('nodes', []))
                print(f'   ✅ SUCCESS: {node_count} nodes extracted')
            else:
                fallback_failed += 1
                error = result.get('error', 'Unknown error')
                print(f'   ❌ FAILED: {error}')
                fallback_errors.append(f'{wf_id}: {error}')
        except Exception as e:
            fallback_failed += 1
            print(f'   ❌ EXCEPTION: {e}')
            fallback_errors.append(f'{wf_id}: Exception - {e}')
        print()
    
    print('=' * 60)
    print('📊 FALLBACK API RESULTS:')
    print(f'   ✅ Success: {fallback_success}/{test_count} workflows')
    print(f'   ❌ Failed: {fallback_failed}/{test_count} workflows')
    print(f'   📈 Success Rate: {fallback_success/test_count*100:.1f}%')
    print()
    
    if fallback_errors:
        print('❌ Error Details:')
        for error in fallback_errors:
            print(f'   - {error}')
        print()
    
    # Project to full 20 workflows
    projected_success = fallback_success * 2
    projected_rate = fallback_success / test_count * 100
    
    print('📊 PROJECTION TO FULL 20 WORKFLOWS:')
    print(f'   Expected Success: {projected_success}/20 workflows')
    print(f'   Expected Rate: {projected_rate:.1f}%')
    print()
    
    # Decision recommendation
    print('🎯 RECOMMENDATION:')
    if projected_rate == 0:
        print('   CANCEL SCRAPE-006C - 0% fallback value')
        print('   Rationale: No workflows recovered by fallback API')
    elif projected_rate < 20:
        print('   CANCEL SCRAPE-006C - Marginal value (<20%)')
        print('   Rationale: Very few workflows recovered, not worth 3 hours')
    elif projected_rate < 30:
        print('   MAYBE CONTINUE - Moderate value (20-30%)')
        print('   Rationale: Some value, but marginal ROI')
    else:
        print('   CONTINUE SCRAPE-006C - Good value (>30%)')
        print('   Rationale: Significant improvement, worth the time')
    
    print()
    print('✅ Test complete!')
    
    return {
        'tested': test_count,
        'success': fallback_success,
        'failed': fallback_failed,
        'rate': projected_rate,
        'recommendation': 'cancel' if projected_rate < 20 else 'continue'
    }

if __name__ == "__main__":
    result = asyncio.run(test_correct_failed_list())
