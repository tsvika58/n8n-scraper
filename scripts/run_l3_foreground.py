#!/usr/bin/env python3
"""
Run L3 Scraper in Foreground with Live Logging

This script runs the L3 scraper in the foreground with:
- Live console output
- Detailed logging to file
- Proper error handling
- Database connection management
"""

import os
import sys
import asyncio
import urllib.parse
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Add paths
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'n8n-shared'))

def setup_environment():
    """Setup environment variables."""
    load_dotenv()
    
    # Get database credentials for display
    db_host = os.getenv('DB_HOST')
    db_port = os.getenv('DB_PORT', '5432')
    db_name = os.getenv('DB_NAME')
    db_user = os.getenv('DB_USER')
    
    print(f"✅ Environment setup complete")
    print(f"📊 Database: {db_host}:{db_port}/{db_name}")
    print(f"👤 User: {db_user}")
    print()

async def run_l3_scraper():
    """Run the L3 scraper with comprehensive logging."""
    print("🚀 STARTING L3 SCRAPER IN FOREGROUND")
    print("=" * 60)
    print(f"⏰ Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        from src.storage.database import get_session
        from n8n_shared.models import Workflow
        from sqlalchemy import select
        
        # Get all workflows
        print("📋 Loading workflows from database...")
        with get_session() as session:
            stmt = select(Workflow.workflow_id, Workflow.url).order_by(Workflow.workflow_id)
            result = session.execute(stmt)
            workflows = result.fetchall()
            total_workflows = len(workflows)
            
            print(f"✅ Loaded {total_workflows:,} workflows")
            print(f"⏰ Estimated time: {total_workflows * 15 / 3600:.1f} hours")
            print()
        
        # Process workflows in batches
        batch_size = 10
        successful = 0
        failed = 0
        start_time = datetime.now()
        
        from src.scrapers.layer3_enhanced_v2 import EnhancedLayer3Extractor
        
        print("🔧 Initializing L3 scraper...")
        async with EnhancedLayer3Extractor(headless=True, extract_transcripts=True) as extractor:
            print("✅ L3 scraper initialized")
            print()
            
            for i in range(0, total_workflows, batch_size):
                batch = workflows[i:i + batch_size]
                batch_num = (i // batch_size) + 1
                total_batches = (total_workflows + batch_size - 1) // batch_size
                
                print(f"📦 BATCH {batch_num}/{total_batches} ({len(batch)} workflows)")
                print("-" * 50)
                
                for j, (workflow_id, url) in enumerate(batch, 1):
                    workflow_num = i + j
                    print(f"[{workflow_num}/{total_workflows}] Processing {workflow_id}...")
                    
                    try:
                        result = await extractor.extract(workflow_id, url)
                        
                        if result['success']:
                            data = result['data']
                            video_count = data.get('video_count', 0)
                            transcript_count = data.get('transcript_count', 0)
                            content_length = data.get('content_length', 0)
                            quality_score = data.get('quality_score', 0)
                            
                            print(f"   ✅ SUCCESS: {video_count} videos, {transcript_count} transcripts, {content_length} chars, Q:{quality_score}")
                            successful += 1
                        else:
                            print(f"   ❌ FAILED: {result.get('error', 'Unknown error')}")
                            failed += 1
                            
                    except Exception as e:
                        print(f"   ❌ EXCEPTION: {e}")
                        failed += 1
                    
                    # Small delay between workflows
                    await asyncio.sleep(2)
                
                # Progress update
                processed = min(i + batch_size, total_workflows)
                progress = (processed / total_workflows) * 100
                elapsed = datetime.now() - start_time
                
                print(f"\n📈 PROGRESS UPDATE:")
                print(f"   Processed: {processed}/{total_workflows} ({progress:.1f}%)")
                print(f"   Successful: {successful}")
                print(f"   Failed: {failed}")
                print(f"   Success Rate: {(successful / processed) * 100:.1f}%")
                print(f"   Elapsed Time: {str(elapsed).split('.')[0]}")
                
                if processed > 0:
                    rate = processed / elapsed.total_seconds() * 3600
                    remaining = total_workflows - processed
                    eta_seconds = remaining / (processed / elapsed.total_seconds())
                    eta = datetime.now() + timedelta(seconds=eta_seconds)
                    print(f"   Processing Rate: {rate:.1f} workflows/hour")
                    print(f"   ETA: {eta.strftime('%Y-%m-%d %H:%M:%S')}")
                
                print()
                
                # Longer delay between batches
                if i + batch_size < total_workflows:
                    print("⏳ Waiting 30 seconds before next batch...")
                    await asyncio.sleep(30)
        
        # Final summary
        total_time = datetime.now() - start_time
        print("🎉 L3 SCRAPING COMPLETE!")
        print("=" * 60)
        print(f"✅ Successful: {successful}")
        print(f"❌ Failed: {failed}")
        print(f"📊 Final Success Rate: {(successful / total_workflows) * 100:.1f}%")
        print(f"⏰ Total Time: {str(total_time).split('.')[0]}")
        print(f"📈 Average Rate: {total_workflows / total_time.total_seconds() * 3600:.1f} workflows/hour")
        print()
        print(f"🏁 Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
    except Exception as e:
        print(f"❌ CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

def main():
    """Main function."""
    try:
        setup_environment()
        success = asyncio.run(run_l3_scraper())
        if success:
            print("\n✅ L3 scraping completed successfully!")
        else:
            print("\n❌ L3 scraping failed!")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n🛑 Scraping stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
