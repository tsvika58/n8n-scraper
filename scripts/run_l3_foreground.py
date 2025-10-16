#!/usr/bin/env python3
"""
Run L3 Scraper in Foreground with Live Progress Monitoring

This script runs the L3 scraper in the foreground with:
- Live console output with progress dashboard
- Real-time progress tracking
- Detailed logging to file
- Proper error handling
- Database connection management
- Live statistics and ETA
"""

import os
import sys
import asyncio
import urllib.parse
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Add paths
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'n8n-shared'))

class ProgressMonitor:
    """Real-time progress monitoring for L3 scraping."""
    
    def __init__(self, total_workflows: int):
        self.total_workflows = total_workflows
        self.processed = 0
        self.successful = 0
        self.failed = 0
        self.start_time = datetime.now()
        self.last_update = time.time()
        self.videos_found = 0
        self.transcripts_extracted = 0
        self.total_content_length = 0
        
    def update(self, workflow_id: str, success: bool, data: dict = None):
        """Update progress with workflow result."""
        self.processed += 1
        
        if success:
            self.successful += 1
            if data:
                self.videos_found += data.get('video_count', 0)
                self.transcripts_extracted += data.get('transcript_count', 0)
                self.total_content_length += data.get('content_length', 0)
        else:
            self.failed += 1
            
        # Update display every 5 seconds or every 10 workflows
        current_time = time.time()
        if current_time - self.last_update >= 5 or self.processed % 10 == 0:
            self.display_progress(workflow_id)
            self.last_update = current_time
    
    def display_progress(self, current_workflow: str = ""):
        """Display live progress dashboard."""
        # Clear screen and move cursor to top
        print("\033[2J\033[H", end="")
        
        # Calculate metrics
        progress_pct = (self.processed / self.total_workflows) * 100
        elapsed = datetime.now() - self.start_time
        
        # Progress bar
        bar_length = 50
        filled_length = int(bar_length * progress_pct / 100)
        bar = '█' * filled_length + '░' * (bar_length - filled_length)
        
        # ETA calculation
        if self.processed > 0:
            rate = self.processed / elapsed.total_seconds() * 3600
            remaining = self.total_workflows - self.processed
            eta_seconds = remaining / (self.processed / elapsed.total_seconds()) if self.processed > 0 else 0
            eta = datetime.now() + timedelta(seconds=eta_seconds)
        else:
            rate = 0
            eta = "Unknown"
        
        # Success rate
        success_rate = (self.successful / self.processed * 100) if self.processed > 0 else 0
        
        # Display dashboard
        print("🚀 L3 SCRAPER - LIVE PROGRESS MONITOR")
        print("=" * 80)
        print(f"⏰ Started: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')} | Current: {datetime.now().strftime('%H:%M:%S')}")
        print()
        
        print(f"📊 PROGRESS: {self.processed:,}/{self.total_workflows:,} ({progress_pct:.1f}%)")
        print(f"Progress: [{bar}] {progress_pct:.1f}%")
        print()
        
        print(f"✅ Successful: {self.successful:,} | ❌ Failed: {self.failed:,} | 📈 Success Rate: {success_rate:.1f}%")
        print(f"🎥 Videos Found: {self.videos_found:,} | 📝 Transcripts: {self.transcripts_extracted:,} | 📄 Content: {self.total_content_length:,} chars")
        print()
        
        print(f"⚡ Rate: {rate:.1f} workflows/hour | ⏱️ Elapsed: {str(elapsed).split('.')[0]}")
        if isinstance(eta, datetime):
            print(f"🎯 ETA: {eta.strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            print(f"🎯 ETA: {eta}")
        print()
        
        if current_workflow:
            print(f"🔄 Currently Processing: {current_workflow}")
        print()
        print("Press Ctrl+C to stop gracefully...")
        print("=" * 80)
    
    def final_summary(self):
        """Display final summary."""
        total_time = datetime.now() - self.start_time
        final_rate = self.total_workflows / total_time.total_seconds() * 3600 if total_time.total_seconds() > 0 else 0
        
        print("\n🎉 L3 SCRAPING COMPLETE!")
        print("=" * 80)
        print(f"✅ Successful: {self.successful:,}")
        print(f"❌ Failed: {self.failed:,}")
        print(f"📊 Final Success Rate: {(self.successful / self.total_workflows) * 100:.1f}%")
        print(f"🎥 Total Videos Found: {self.videos_found:,}")
        print(f"📝 Total Transcripts: {self.transcripts_extracted:,}")
        print(f"📄 Total Content: {self.total_content_length:,} characters")
        print(f"⏰ Total Time: {str(total_time).split('.')[0]}")
        print(f"📈 Average Rate: {final_rate:.1f} workflows/hour")
        print(f"🏁 Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)

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
    """Run the L3 scraper with live progress monitoring."""
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
        
        # Initialize progress monitor
        monitor = ProgressMonitor(total_workflows)
        monitor.display_progress("Initializing...")
        
        from src.scrapers.layer3_enhanced_v2 import EnhancedLayer3Extractor
        
        print("🔧 Initializing L3 scraper...")
        async with EnhancedLayer3Extractor(headless=True, extract_transcripts=True) as extractor:
            print("✅ L3 scraper initialized")
            print()
            
            # Process workflows one by one with live monitoring
            for i, (workflow_id, url) in enumerate(workflows, 1):
                try:
                    # Update monitor with current workflow
                    monitor.display_progress(f"{workflow_id} ({i}/{total_workflows})")
                    
                    result = await extractor.extract(workflow_id, url)
                    
                    if result['success']:
                        data = result['data']
                        monitor.update(workflow_id, True, data)
                    else:
                        monitor.update(workflow_id, False)
                        
                except Exception as e:
                    print(f"❌ EXCEPTION for {workflow_id}: {e}")
                    monitor.update(workflow_id, False)
                
                # Small delay between workflows
                await asyncio.sleep(2)
        
        # Final summary
        monitor.final_summary()
        
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
        print("🚀 STARTING L3 SCRAPER WITH LIVE PROGRESS MONITORING")
        print("=" * 80)
        print(f"⏰ Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        success = asyncio.run(run_l3_scraper())
        if success:
            print("\n✅ L3 scraping completed successfully!")
        else:
            print("\n❌ L3 scraping failed!")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n🛑 Scraping stopped by user")
        print("📊 Progress saved - you can resume later")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
