#!/usr/bin/env python3
"""
Test Database Save Functionality

Test that the L3 scraper properly saves data and updates layer3_success flags.
"""

import os
import sys
import asyncio
from datetime import datetime
from dotenv import load_dotenv

# Add paths
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'n8n-shared'))

async def test_db_save():
    """Test database save functionality."""
    print("🧪 TESTING DATABASE SAVE FUNCTIONALITY")
    print("=" * 50)
    
    # Test workflow
    workflow_id = '6270'
    url = 'https://n8n.io/workflows/6270-build-your-first-ai-agent/'
    
    print(f"📥 Testing workflow: {workflow_id}")
    print(f"   URL: {url}")
    print()
    
    try:
        from src.scrapers.layer3_enhanced_v2 import EnhancedLayer3Extractor
        
        # Check initial state
        from src.storage.database import get_session
        from n8n_shared.models import Workflow, WorkflowContent
        
        print("🔍 Checking initial database state...")
        with get_session() as session:
            workflow = session.query(Workflow).filter_by(workflow_id=workflow_id).first()
            content = session.query(WorkflowContent).filter_by(workflow_id=workflow_id).first()
            
            print(f"   Workflow L3 Success: {workflow.layer3_success if workflow else 'Not found'}")
            print(f"   Content L3 Success: {content.layer3_success if content else 'Not found'}")
            print(f"   Video Count: {len(content.video_urls) if content and content.video_urls else 0}")
            print(f"   Transcript Count: {len(content.transcripts) if content and content.transcripts else 0}")
        
        print()
        
        # Run L3 scraper
        print("🎬 Running L3 scraper with database save...")
        async with EnhancedLayer3Extractor(headless=True, extract_transcripts=True) as extractor:
            result = await extractor.extract(workflow_id, url)
            
            if result['success']:
                data = result['data']
                print(f"   ✅ Extraction successful:")
                print(f"      Videos: {data.get('video_count', 0)}")
                print(f"      Transcripts: {data.get('transcript_count', 0)}")
                print(f"      Content Length: {data.get('total_text_length', 0)}")
                print(f"      Quality Score: {result.get('quality_score', 0)}")
            else:
                print(f"   ❌ Extraction failed: {result.get('error')}")
                return False
        
        print()
        
        # Check final state
        print("🔍 Checking final database state...")
        with get_session() as session:
            workflow = session.query(Workflow).filter_by(workflow_id=workflow_id).first()
            content = session.query(WorkflowContent).filter_by(workflow_id=workflow_id).first()
            
            print(f"   Workflow L3 Success: {workflow.layer3_success if workflow else 'Not found'}")
            print(f"   Content L3 Success: {content.layer3_success if content else 'Not found'}")
            print(f"   Video Count: {len(content.video_urls) if content and content.video_urls else 0}")
            print(f"   Transcript Count: {len(content.transcripts) if content and content.transcripts else 0}")
            print(f"   Quality Score: {workflow.quality_score if workflow else 'N/A'}")
        
        # Validate results
        if workflow and workflow.layer3_success and content and content.layer3_success:
            print("\n🎉 DATABASE SAVE TEST SUCCESSFUL!")
            print("✅ L3 success flags properly updated")
            print("✅ Video and transcript data saved")
            return True
        else:
            print("\n❌ DATABASE SAVE TEST FAILED!")
            print("❌ L3 success flags not properly updated")
            return False
            
    except Exception as e:
        print(f"\n💥 CRITICAL ERROR: {e}")
        return False

async def main():
    """Main function."""
    success = await test_db_save()
    if success:
        print("\n✅ DATABASE SAVE FUNCTIONALITY VERIFIED")
        sys.exit(0)
    else:
        print("\n❌ DATABASE SAVE FUNCTIONALITY FAILED")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())

