#!/usr/bin/env python3
"""
Simple test script for a single workflow to debug issues.

Tests just one workflow to isolate the problems.

Author: RND Team - Comprehensive Scraping Expansion
Date: October 12, 2025
"""

import sys
import asyncio
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.orchestrator.e2e_pipeline import E2EPipeline
from src.storage.database import get_session
from src.storage.repository import WorkflowRepository


async def test_single_workflow():
    """Test a single workflow to debug issues."""
    print("=" * 80)
    print("🧪 TESTING SINGLE WORKFLOW")
    print("=" * 80)
    print()
    
    # Test workflow
    workflow_id = '2462'
    url = 'https://n8n.io/workflows/2462'
    
    print(f"📋 Testing workflow: {workflow_id}")
    print(f"   URL: {url}")
    print()
    
    # Initialize pipeline
    print("🔧 Initializing E2E Pipeline...")
    pipeline = E2EPipeline()
    print("✅ Pipeline initialized")
    print()
    
    try:
        # Process workflow through complete pipeline
        print("🔄 Processing through all 7 layers...")
        start_time = datetime.now()
        
        result = await pipeline.process_workflow(workflow_id, url)
        
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        
        print(f"⏱️  Processing time: {processing_time:.2f}s")
        print(f"✅ Pipeline processing completed")
        
        # Debug: Print result structure
        print(f"\n🔍 Result structure:")
        print(f"   Keys: {list(result.keys())}")
        print(f"   Success: {result.get('success')}")
        print(f"   Quality: {result.get('quality')}")
        print(f"   Layers: {list(result.get('layers', {}).keys())}")
        
        # Check layer success rates
        layers = result.get('layers', {})
        successful_layers = sum(1 for layer in layers.values() if layer and layer.get('success', False))
        total_layers = len(layers)
        
        print(f"📈 Layer success: {successful_layers}/{total_layers} layers")
        
        # Try to save to database
        print("\n💾 Attempting to save to database...")
        try:
            with get_session() as session:
                repository = WorkflowRepository(session)
                workflow_obj = repository.create_workflow(workflow_id, url, result)
                print(f"✅ Successfully saved workflow {workflow_id} to database")
                
                # Verify database storage
                print("🔍 Verifying database storage...")
                stored_workflow = repository.get_workflow(workflow_id, include_relationships=True)
                
                if stored_workflow:
                    print(f"✅ Workflow retrieved from database")
                    print(f"📊 Quality score: {stored_workflow.quality_score}")
                    print(f"🎯 Layer success flags:")
                    print(f"      Layer 1: {stored_workflow.layer1_success}")
                    print(f"      Layer 2: {stored_workflow.layer2_success}")
                    print(f"      Layer 3: {stored_workflow.layer3_success}")
                    print(f"      Layer 4: {stored_workflow.layer4_success}")
                    print(f"      Layer 5: {stored_workflow.layer5_success}")
                    print(f"      Layer 6: {stored_workflow.layer6_success}")
                    print(f"      Layer 7: {stored_workflow.layer7_success}")
                else:
                    print(f"❌ Failed to retrieve workflow from database")
                    
        except Exception as e:
            print(f"❌ Database error: {e}")
            import traceback
            traceback.print_exc()
        
        print(f"\n✅ Single workflow test completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error processing workflow {workflow_id}: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_single_workflow())
    sys.exit(0 if success else 1)
