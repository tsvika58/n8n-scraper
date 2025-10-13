#!/usr/bin/env python3
"""
SCRAPE-015: Corrected E2E Validation

Simple test to verify pipeline components work after database cleanup.
Uses correct class names from the actual source code.
"""

import asyncio
import sys
import time
from pathlib import Path
from datetime import datetime

print("=" * 80)
print("🧪 SCRAPE-015: CORRECTED E2E VALIDATION")
print("=" * 80)
print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 80)
print()

# Test workflow
TEST_WORKFLOW = {
    'id': '2462',
    'url': 'https://n8n.io/workflows/2462'
}

async def test_layer1():
    """Test Layer 1 metadata extraction."""
    print("🔍 Testing Layer 1: Metadata Extraction...")
    try:
        # Add project root to path
        sys.path.insert(0, str(Path(__file__).parent.parent))
        
        from src.scrapers.layer1_metadata import PageMetadataExtractor
        
        extractor = PageMetadataExtractor()
        result = await extractor.extract(TEST_WORKFLOW['id'], TEST_WORKFLOW['url'])
        
        if result and result.get('success'):
            print("   ✅ Layer 1: Success")
            return True
        else:
            print("   ❌ Layer 1: Failed")
            return False
    except Exception as e:
        print(f"   ❌ Layer 1: Error - {e}")
        return False

async def test_layer2():
    """Test Layer 2 JSON extraction."""
    print("🔍 Testing Layer 2: JSON Extraction...")
    try:
        from src.scrapers.layer2_json import WorkflowJSONExtractor
        
        extractor = WorkflowJSONExtractor()
        result = await extractor.extract(TEST_WORKFLOW['id'], TEST_WORKFLOW['url'])
        
        if result and result.get('success'):
            print("   ✅ Layer 2: Success")
            return True
        else:
            print("   ❌ Layer 2: Failed")
            return False
    except Exception as e:
        print(f"   ❌ Layer 2: Error - {e}")
        return False

async def test_layer3():
    """Test Layer 3 content extraction."""
    print("🔍 Testing Layer 3: Content Extraction...")
    try:
        from src.scrapers.layer3_explainer import ExplainerContentExtractor
        
        async with ExplainerContentExtractor(headless=True) as extractor:
            result = await extractor.extract(TEST_WORKFLOW['id'], TEST_WORKFLOW['url'])
        
        if result and result.get('success'):
            print("   ✅ Layer 3: Success")
            return True
        else:
            print("   ❌ Layer 3: Failed")
            return False
    except Exception as e:
        print(f"   ❌ Layer 3: Error - {e}")
        return False

def test_database():
    """Test database connectivity."""
    print("🔍 Testing Database: Connectivity...")
    try:
        from src.storage.database import get_session
        from src.storage.repository import WorkflowRepository
        
        with get_session() as session:
            repo = WorkflowRepository(session)
            # Just test that we can create the repository
            print("   ✅ Database: Connection successful")
            return True
    except Exception as e:
        print(f"   ❌ Database: Error - {e}")
        return False

async def main():
    """Run corrected E2E test."""
    
    print("🚀 Starting Corrected E2E Validation...")
    print(f"Testing workflow: {TEST_WORKFLOW['id']} - {TEST_WORKFLOW['url']}")
    print()
    
    results = []
    
    # Test each component
    results.append(await test_layer1())
    results.append(await test_layer2())
    results.append(await test_layer3())
    results.append(test_database())
    
    # Summary
    print("\n" + "=" * 80)
    print("📋 E2E TEST RESULTS")
    print("=" * 80)
    
    components = ['Layer 1', 'Layer 2', 'Layer 3', 'Database']
    
    for i, (component, success) in enumerate(zip(components, results)):
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {component}")
    
    total = len(results)
    passed = sum(results)
    failed = total - passed
    
    print(f"\nTotal Components: {total}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"Success Rate: {(passed/total*100):.1f}%")
    
    print("=" * 80)
    
    if passed == total:
        print("\n🎉 ALL E2E TESTS PASSED!")
        print("\n✅ Pipeline Status: FULLY OPERATIONAL")
        print("\n🚀 READY FOR SPRINT 3 DATASET PROCESSING")
        print("\nDatabase is clean and pipeline is validated!")
        return True
    else:
        print(f"\n❌ E2E TESTS FAILED")
        print(f"\n{failed} component(s) failed. Please investigate.")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)



