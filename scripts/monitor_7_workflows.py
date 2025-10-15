#!/usr/bin/env python3
"""
Monitor 7 Video Workflows Progress

Shows live progress of the 7 video workflows scraping with monitoring at the bottom.
"""

import os
import sys
import time
import json
from datetime import datetime
from dotenv import load_dotenv

# Add paths
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'n8n-shared'))

# The 7 test workflows
TEST_WORKFLOWS = [
    ('6270', 'https://n8n.io/workflows/6270-build-your-first-ai-agent/'),
    ('8642', 'https://n8n.io/workflows/8642-generate-ai-viral-videos-with-veo-3-and-upload-to-tiktok/'),
    ('8527', 'https://n8n.io/workflows/8527-learn-n8n-basics-in-3-easy-steps/'),
    ('8237', 'https://n8n.io/workflows/8237-personal-life-manager-with-telegram-google-services-and-voice-enabled-ai/'),
    ('7639', 'https://n8n.io/workflows/7639-talk-to-your-google-sheets-using-chatgpt-5/'),
    ('5170', 'https://n8n.io/workflows/5170-learn-json-basics-with-an-interactive-step-by-step-tutorial-for-beginners/'),
    ('2462', 'https://n8n.io/workflows/2462-angie-personal-ai-assistant-with-telegram-voice-and-text/')
]

RESUME_STATE_FILE = 'video_workflows_progress.json'

def clear_screen():
    """Clear the terminal screen."""
    os.system('clear' if os.name == 'posix' else 'cls')

def get_progress_data():
    """Get current progress from resume state and database."""
    try:
        # Load resume state
        if os.path.exists(RESUME_STATE_FILE):
            with open(RESUME_STATE_FILE, 'r') as f:
                state = json.load(f)
        else:
            state = {'completed': [], 'failed': [], 'start_time': None}
        
        # Get database stats
        from src.storage.database import get_session
        from n8n_shared.models import Workflow, WorkflowContent
        from sqlalchemy import select, func
        
        with get_session() as session:
            # Get L3 completion stats for our workflows
            workflow_ids = [w[0] for w in TEST_WORKFLOWS]
            
            # Count completed workflows
            completed_count = session.execute(
                select(func.count(Workflow.workflow_id))
                .where(Workflow.workflow_id.in_(workflow_ids))
                .where(Workflow.layer3_success == True)
            ).scalar()
            
            # Get content stats
            content_stats = session.execute(
                select(
                    func.count(WorkflowContent.workflow_id),
                    func.count(func.case((WorkflowContent.video_urls.isnot(None), 1))),
                    func.count(func.case((WorkflowContent.transcripts.isnot(None), 1))),
                    func.avg(func.length(WorkflowContent.explainer_text))
                )
                .where(WorkflowContent.workflow_id.in_(workflow_ids))
                .where(WorkflowContent.layer3_success == True)
            ).fetchone()
            
            # Get recent completions
            recent = session.execute(
                select(Workflow.workflow_id, Workflow.updated_at)
                .where(Workflow.workflow_id.in_(workflow_ids))
                .where(Workflow.layer3_success == True)
                .order_by(Workflow.updated_at.desc())
                .limit(3)
            ).fetchall()
            
            return {
                'total': len(TEST_WORKFLOWS),
                'completed': completed_count,
                'with_videos': content_stats[1] or 0,
                'with_transcripts': content_stats[2] or 0,
                'avg_content_length': content_stats[3] or 0,
                'recent': recent,
                'resume_state': state
            }
    except Exception as e:
        return {
            'total': len(TEST_WORKFLOWS),
            'completed': 0,
            'with_videos': 0,
            'with_transcripts': 0,
            'avg_content_length': 0,
            'recent': [],
            'resume_state': {'completed': [], 'failed': [], 'start_time': None}
        }

def display_status(data, update_count):
    """Display the current status with monitoring at the bottom."""
    current_time = datetime.now()
    
    # Calculate progress
    progress_pct = (data['completed'] / data['total']) * 100 if data['total'] > 0 else 0
    
    # Create progress bar
    bar_length = 40
    filled_length = int(bar_length * progress_pct / 100)
    bar = '█' * filled_length + '░' * (bar_length - filled_length)
    
    # Clear screen and show header
    clear_screen()
    print("🎥 7 VIDEO WORKFLOWS L3 SCRAPER MONITOR")
    print("=" * 60)
    print(f"⏰ {current_time.strftime('%Y-%m-%d %H:%M:%S')} | Update #{update_count}")
    print()
    
    # Main progress
    print(f"📊 PROGRESS: {progress_pct:.1f}%")
    print(f"[{bar}] {data['completed']}/{data['total']}")
    print()
    
    # Statistics
    print(f"📈 STATISTICS:")
    print(f"   Total Workflows: {data['total']}")
    print(f"   L3 Complete: {data['completed']}")
    print(f"   With Videos: {data['with_videos']}")
    print(f"   With Transcripts: {data['with_transcripts']}")
    if data['avg_content_length'] > 0:
        print(f"   Avg Content Length: {data['avg_content_length']:.0f} chars")
    print()
    
    # Resume state info
    resume_state = data['resume_state']
    if resume_state['completed']:
        print(f"✅ Resume - Completed: {', '.join(resume_state['completed'])}")
    if resume_state['failed']:
        print(f"❌ Resume - Failed: {', '.join(resume_state['failed'])}")
    print()
    
    # Recent completions
    print(f"🕒 RECENT COMPLETIONS:")
    for row in data['recent']:
        print(f"   {row[0]}: {row[1]}")
    print()
    
    # Workflow list with status
    print(f"📋 WORKFLOW STATUS:")
    for workflow_id, url in TEST_WORKFLOWS:
        status = "✅" if workflow_id in resume_state['completed'] else "❌" if workflow_id in resume_state['failed'] else "⏳"
        print(f"   {status} {workflow_id}: {url.split('/')[-2]}")
    print()
    
    # Monitoring section at bottom
    print("=" * 60)
    print("🔍 LIVE MONITORING (Updates every 3 seconds)")
    print("Press Ctrl+C to stop monitoring")
    print("=" * 60)

def main():
    """Main monitoring loop."""
    print("🎥 Starting 7 Video Workflows Monitor...")
    print("Updates every 3 seconds")
    print("Press Ctrl+C to stop")
    time.sleep(2)
    
    update_count = 0
    
    try:
        while True:
            update_count += 1
            
            try:
                data = get_progress_data()
                display_status(data, update_count)
            except Exception as e:
                print(f"❌ Error getting progress data: {e}")
                print("Retrying in 3 seconds...")
            
            time.sleep(3)
            
    except KeyboardInterrupt:
        print("\n\n🛑 Monitoring stopped by user")

if __name__ == "__main__":
    main()
