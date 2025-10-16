#!/usr/bin/env python3
"""
Test script for the progress monitor
"""

import time
from datetime import datetime, timedelta

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
            
        # Update display every 2 seconds or every 5 workflows
        current_time = time.time()
        if current_time - self.last_update >= 2 or self.processed % 5 == 0:
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
        print("🚀 L3 SCRAPER - LIVE PROGRESS MONITOR (TEST)")
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

def test_progress_monitor():
    """Test the progress monitor with simulated data."""
    print("🧪 Testing Progress Monitor...")
    time.sleep(2)
    
    # Simulate 50 workflows
    monitor = ProgressMonitor(50)
    
    for i in range(50):
        workflow_id = f"workflow_{i+1}"
        
        # Simulate some success/failure
        success = i % 10 != 0  # 90% success rate
        
        if success:
            # Simulate some data
            data = {
                'video_count': 1 if i % 5 == 0 else 0,
                'transcript_count': 1 if i % 3 == 0 else 0,
                'content_length': 15000 + (i * 100)
            }
            monitor.update(workflow_id, True, data)
        else:
            monitor.update(workflow_id, False)
        
        # Simulate processing time
        time.sleep(0.5)
    
    print("\n✅ Test completed!")

if __name__ == "__main__":
    try:
        test_progress_monitor()
    except KeyboardInterrupt:
        print("\n🛑 Test stopped by user")

