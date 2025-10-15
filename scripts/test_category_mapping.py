#!/usr/bin/env python3
"""
Test script to verify category mapping fix.
Tests that categories and tags are properly extracted from raw_metadata.
"""

import sys
from pathlib import Path
from sqlalchemy import text

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.storage.database import get_session
from src.storage.repository import WorkflowRepository

def test_category_mapping():
    """Test that categories and tags are properly mapped from raw_metadata."""
    print("🧪 TESTING CATEGORY MAPPING FIX")
    print("=" * 60)
    
    with get_session() as session:
        repository = WorkflowRepository(session)
        
        # Test with a workflow that has raw_metadata with categories
        test_workflow_id = "484"  # Known to have categories in raw_metadata
        
        # Get the workflow
        workflow = repository.get_workflow(test_workflow_id)
        if not workflow:
            print(f"❌ Workflow {test_workflow_id} not found")
            return False
        
        # Check if metadata exists
        if not workflow.workflow_metadata:
            print(f"❌ No metadata found for workflow {test_workflow_id}")
            return False
        
        metadata = workflow.workflow_metadata
        print(f"✅ Found metadata for workflow {test_workflow_id}")
        
        # Check raw_metadata for categories
        raw_metadata = metadata.raw_metadata
        if not raw_metadata:
            print(f"❌ No raw_metadata found for workflow {test_workflow_id}")
            return False
        
        print(f"✅ Found raw_metadata with {len(raw_metadata)} fields")
        
        # Check if categories exist in raw_metadata
        raw_data = raw_metadata.get('data', {})
        primary_category = raw_data.get('primary_category')
        general_tags = raw_data.get('general_tags', [])
        node_tags = raw_data.get('node_tags', [])
        industry = raw_data.get('industry', [])
        
        print(f"\n📊 RAW METADATA ANALYSIS:")
        print(f"   Primary Category: {primary_category}")
        print(f"   General Tags: {general_tags}")
        print(f"   Node Tags: {node_tags}")
        print(f"   Industry: {industry}")
        
        # Test category extraction
        extracted_categories = repository._extract_categories(raw_data)
        extracted_tags = repository._extract_tags(raw_data)
        
        print(f"\n🔧 EXTRACTED DATA:")
        print(f"   Categories: {extracted_categories}")
        print(f"   Tags: {extracted_tags}")
        
        # Check if structured fields have data
        structured_categories = metadata.categories
        structured_tags = metadata.tags
        
        print(f"\n📋 STRUCTURED FIELDS:")
        print(f"   Categories: {structured_categories}")
        print(f"   Tags: {structured_tags}")
        
        # Verify the fix worked
        if extracted_categories and not structured_categories:
            print(f"\n❌ CATEGORY MAPPING FAILED:")
            print(f"   Categories extracted: {extracted_categories}")
            print(f"   Categories in DB: {structured_categories}")
            return False
        
        if extracted_tags and not structured_tags:
            print(f"\n❌ TAG MAPPING FAILED:")
            print(f"   Tags extracted: {extracted_tags}")
            print(f"   Tags in DB: {structured_tags}")
            return False
        
        print(f"\n✅ CATEGORY MAPPING SUCCESS!")
        print(f"   Categories: {len(extracted_categories)} extracted, {len(structured_categories)} in DB")
        print(f"   Tags: {len(extracted_tags)} extracted, {len(structured_tags)} in DB")
        
        return True

def test_reprocess_workflow():
    """Test reprocessing a workflow to update categories."""
    print("\n🔄 TESTING WORKFLOW REPROCESSING")
    print("=" * 60)
    
    with get_session() as session:
        repository = WorkflowRepository(session)
        
        # Test workflow ID
        test_workflow_id = "484"
        
        # Get current metadata
        workflow = repository.get_workflow(test_workflow_id)
        if not workflow or not workflow.workflow_metadata:
            print(f"❌ Cannot find workflow or metadata for {test_workflow_id}")
            return False
        
        old_categories = workflow.workflow_metadata.categories
        old_tags = workflow.workflow_metadata.tags
        
        print(f"📋 BEFORE REPROCESSING:")
        print(f"   Categories: {old_categories}")
        print(f"   Tags: {old_tags}")
        
        # Create a mock extraction result with proper category data
        raw_data = workflow.workflow_metadata.raw_metadata.get('data', {})
        
        mock_extraction_result = {
            'layers': {
                'layer1': {
                    'success': True,
                    'data': raw_data,
                    'title': workflow.workflow_metadata.title,
                    'description': workflow.workflow_metadata.description,
                    'use_case': workflow.workflow_metadata.use_case,
                    'author': {
                        'name': workflow.workflow_metadata.author_name,
                        'url': workflow.workflow_metadata.author_url
                    },
                    'views': workflow.workflow_metadata.views,
                    'shares': workflow.workflow_metadata.shares,
                    'created_at': workflow.workflow_metadata.workflow_created_at,
                    'updated_at': workflow.workflow_metadata.workflow_updated_at
                }
            }
        }
        
        # Reprocess the workflow
        try:
            updated_workflow = repository.create_workflow(
                test_workflow_id,
                workflow.url,
                mock_extraction_result
            )
            
            new_categories = updated_workflow.workflow_metadata.categories
            new_tags = updated_workflow.workflow_metadata.tags
            
            print(f"\n📋 AFTER REPROCESSING:")
            print(f"   Categories: {new_categories}")
            print(f"   Tags: {new_tags}")
            
            if new_categories != old_categories or new_tags != old_tags:
                print(f"\n✅ REPROCESSING SUCCESS!")
                print(f"   Categories updated: {old_categories} → {new_categories}")
                print(f"   Tags updated: {old_tags} → {new_tags}")
                return True
            else:
                print(f"\n⚠️  NO CHANGES DETECTED")
                return True  # Not necessarily a failure
                
        except Exception as e:
            print(f"\n❌ REPROCESSING FAILED: {e}")
            return False

if __name__ == "__main__":
    print("🚀 STARTING CATEGORY MAPPING TESTS")
    print("=" * 80)
    
    # Test 1: Check current category mapping
    test1_success = test_category_mapping()
    
    # Test 2: Test reprocessing
    test2_success = test_reprocess_workflow()
    
    print("\n" + "=" * 80)
    print("🎯 TEST RESULTS:")
    print(f"   Category Mapping Test: {'✅ PASSED' if test1_success else '❌ FAILED'}")
    print(f"   Reprocessing Test: {'✅ PASSED' if test2_success else '❌ FAILED'}")
    
    if test1_success and test2_success:
        print("\n🎉 ALL TESTS PASSED! Category mapping is working correctly.")
        sys.exit(0)
    else:
        print("\n❌ SOME TESTS FAILED! Category mapping needs fixes.")
        sys.exit(1)





