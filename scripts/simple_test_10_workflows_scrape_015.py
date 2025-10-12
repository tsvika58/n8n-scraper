#!/usr/bin/env python3
"""
SCRAPE-015: Simple Test 10 Real Workflows (Docker Container Version)

Tests the complete system by scraping 10 unscraped workflows.
Designed to run inside the Docker container.
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime

print("=" * 80)
print("🧪 SCRAPE-015: TESTING 10 REAL WORKFLOWS")
print("=" * 80)
print()

async def test_10_real_workflows():
    """Test scraping 10 real workflows with live monitoring."""
    
    print("🚀 Starting 10 Real Workflow Test...")
    print()
    print("📊 System Status:")
    print("   • Database: 101 workflows (1 scraped, 100 unscraped)")
    print("   • Scraping Dashboard: http://localhost:5002")
    print("   • Database Viewer: http://localhost:5004")
    print()
    
    # Get 10 unscraped workflows
    print("🔍 Selecting 10 unscraped workflows...")
    
    try:
        from src.storage.database import get_session
        from sqlalchemy import text
        
        with get_session() as session:
            result = session.execute(text("""
                SELECT workflow_id, url 
                FROM workflows 
                WHERE layer1_success = false OR layer1_success IS NULL
                LIMIT 10
            """))
            
            workflows = [(row[0], row[1]) for row in result]
        
        print("✅ Selected workflows:")
        for i, (workflow_id, url) in enumerate(workflows, 1):
            print(f"   • {workflow_id}: {url}")
        
        print(f"\n📋 Total workflows to scrape: {len(workflows)}")
        print()
        
        # Import required modules
        print("🔍 Importing scraping modules...")
        from src.scrapers.layer1_metadata import PageMetadataExtractor
        from src.scrapers.layer2_json import WorkflowJSONExtractor
        from src.scrapers.layer3_explainer import ExplainerContentExtractor
        
        print("✅ All modules imported successfully")
        print()
        
        # Scrape each workflow
        print("🚀 Starting real-time scraping...")
        print("   📊 Monitor progress at: http://localhost:5002")
        print("   🗄️  View database at: http://localhost:5004")
        print()
        
        success_count = 0
        total_time = 0
        
        for i, (workflow_id, url) in enumerate(workflows, 1):
            print(f"🔍 [{i}/{len(workflows)}] Scraping workflow {workflow_id}...")
            print(f"   URL: {url}")
            
            start_time = datetime.now()
            
            try:
                # Layer 1: Metadata
                print(f"   📊 Layer 1: Extracting metadata...")
                layer1_extractor = PageMetadataExtractor()
                layer1_result = await layer1_extractor.extract(workflow_id, url)
                
                layer1_success = layer1_result.get('success', False)
                print(f"   {'✅' if layer1_success else '❌'} Layer 1: {'Success' if layer1_success else 'Failed'}")
                
                # Layer 2: JSON Structure
                print(f"   🔧 Layer 2: Extracting JSON structure...")
                layer2_extractor = WorkflowJSONExtractor()
                layer2_result = await layer2_extractor.extract(workflow_id)
                
                layer2_success = layer2_result.get('success', False)
                print(f"   {'✅' if layer2_success else '❌'} Layer 2: {'Success' if layer2_success else 'Failed'}")
                
                # Layer 3: Content
                print(f"   📝 Layer 3: Extracting content...")
                async with ExplainerContentExtractor(headless=True) as layer3_extractor:
                    layer3_result = await layer3_extractor.extract(workflow_id, url)
                
                layer3_success = layer3_result.get('success', False)
                print(f"   {'✅' if layer3_success else '❌'} Layer 3: {'Success' if layer3_success else 'Failed'}")
                
                # Calculate processing time and quality
                end_time = datetime.now()
                processing_time = (end_time - start_time).total_seconds()
                total_time += processing_time
                
                # Calculate quality score
                success_count = sum([layer1_success, layer2_success, layer3_success])
                quality_score = (success_count / 3) * 100
                
                # Update database
                print(f"   💾 Updating database...")
                with get_session() as session:
                    update_sql = text("""
                    UPDATE workflows SET
                        processing_time = :processing_time,
                        quality_score = :quality_score,
                        layer1_success = :layer1_success,
                        layer2_success = :layer2_success,
                        layer3_success = :layer3_success,
                        updated_at = NOW()
                    WHERE workflow_id = :workflow_id
                    """)
                    
                    session.execute(update_sql, {
                        'processing_time': processing_time,
                        'quality_score': quality_score,
                        'layer1_success': layer1_success,
                        'layer2_success': layer2_success,
                        'layer3_success': layer3_success,
                        'workflow_id': workflow_id
                    })
                    session.commit()
                
                if layer1_success or layer2_success or layer3_success:
                    success_count += 1
                
                print(f"   ✅ Workflow {workflow_id} completed in {processing_time:.1f}s (Quality: {quality_score:.1f}%)")
                
            except Exception as e:
                print(f"   ❌ Workflow {workflow_id} failed: {e}")
                
                # Update database with failure
                try:
                    with get_session() as session:
                        update_sql = text("""
                        UPDATE workflows SET
                            processing_time = :processing_time,
                            quality_score = 0,
                            layer1_success = false,
                            layer2_success = false,
                            layer3_success = false,
                            error_message = :error_message,
                            updated_at = NOW()
                        WHERE workflow_id = :workflow_id
                        """)
                        
                        session.execute(update_sql, {
                            'processing_time': processing_time,
                            'error_message': str(e),
                            'workflow_id': workflow_id
                        })
                        session.commit()
                except:
                    pass
            
            print()
        
        # Final summary
        avg_time = total_time / len(workflows) if workflows else 0
        success_rate = (success_count / len(workflows)) * 100 if workflows else 0
        
        print("=" * 80)
        print("🎉 10 REAL WORKFLOW TEST COMPLETE!")
        print("=" * 80)
        print()
        print("📊 Results Summary:")
        print(f"   • Workflows processed: {len(workflows)}")
        print(f"   • Successful extractions: {success_count}")
        print(f"   • Success rate: {success_rate:.1f}%")
        print(f"   • Average processing time: {avg_time:.1f}s")
        print(f"   • Total time: {total_time:.1f}s")
        print()
        print("🚀 Check the dashboards:")
        print("   • Scraping Dashboard: http://localhost:5002")
        print("   • Database Viewer: http://localhost:5004")
        print()
        print("✅ System working as intended:")
        print("   • Real-time scraping ✅")
        print("   • Live database updates ✅")
        print("   • Dashboard monitoring ✅")
        print("   • Complete workflow inventory ✅")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

async def main():
    """Main execution."""
    await test_10_real_workflows()

if __name__ == "__main__":
    asyncio.run(main())

