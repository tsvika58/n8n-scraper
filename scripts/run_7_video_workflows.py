#!/usr/bin/env python3
"""
Run L3 Scraper on 7 Video Workflows with Resume Capability

This script runs the L3 scraper on the 7 specific workflows that are known to have videos,
with resume capability and live monitoring at the bottom.
"""

import os
import sys
import asyncio
import urllib.parse
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Add paths
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'n8n-shared'))

# The 7 test workflows with videos
TEST_WORKFLOWS = [
    ('6270', 'https://n8n.io/workflows/6270-build-your-first-ai-agent/'),
    ('8642', 'https://n8n.io/workflows/8642-generate-ai-viral-videos-with-veo-3-and-upload-to-tiktok/'),
    ('8527', 'https://n8n.io/workflows/8527-learn-n8n-basics-in-3-easy-steps/'),
    ('8237', 'https://n8n.io/workflows/8237-personal-life-manager-with-telegram-google-services-and-voice-enabled-ai/'),
    ('7639', 'https://n8n.io/workflows/7639-talk-to-your-google-sheets-using-chatgpt-5/'),
    ('5170', 'https://n8n.io/workflows/5170-learn-json-basics-with-an-interactive-step-by-step-tutorial-for-beginners/'),
    ('2462', 'https://n8n.io/workflows/2462-angie-personal-ai-assistant-with-telegram-voice-and-text/')
]

# Resume state file
RESUME_STATE_FILE = 'video_workflows_progress.json'

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

def load_resume_state():
    """Load resume state from file."""
    if os.path.exists(RESUME_STATE_FILE):
        try:
            with open(RESUME_STATE_FILE, 'r') as f:
                state = json.load(f)
                print(f"📂 Loaded resume state: {state['completed']}/{len(TEST_WORKFLOWS)} completed")
                return state
        except Exception as e:
            print(f"⚠️  Could not load resume state: {e}")
    
    return {
        'completed': [],
        'failed': [],
        'start_time': datetime.now().isoformat(),
        'last_workflow': None
    }

def save_resume_state(state):
    """Save resume state to file."""
    try:
        with open(RESUME_STATE_FILE, 'w') as f:
            json.dump(state, f, indent=2)
    except Exception as e:
        print(f"⚠️  Could not save resume state: {e}")

def get_remaining_workflows(state):
    """Get workflows that haven't been completed yet."""
    completed_ids = set(state['completed'])
    remaining = []
    
    for workflow_id, url in TEST_WORKFLOWS:
        if workflow_id not in completed_ids:
            remaining.append((workflow_id, url))
    
    return remaining

def display_progress(state, current_workflow=None):
    """Display current progress."""
    total = len(TEST_WORKFLOWS)
    completed = len(state['completed'])
    failed = len(state['failed'])
    remaining = total - completed - failed
    
    # Progress bar
    bar_length = 30
    filled_length = int(bar_length * completed / total)
    bar = '█' * filled_length + '░' * (bar_length - filled_length)
    
    print(f"\n🎥 VIDEO WORKFLOWS PROGRESS")
    print("=" * 50)
    print(f"Progress: [{bar}] {completed}/{total} ({completed/total*100:.1f}%)")
    print(f"✅ Completed: {completed}")
    print(f"❌ Failed: {failed}")
    print(f"⏳ Remaining: {remaining}")
    
    if current_workflow:
        print(f"🔄 Current: {current_workflow}")
    
    if state['completed']:
        print(f"✅ Completed: {', '.join(state['completed'])}")
    if state['failed']:
        print(f"❌ Failed: {', '.join(state['failed'])}")
    
    print("=" * 50)

async def run_video_workflows():
    """Run L3 scraper on the 7 video workflows with resume capability."""
    print("🎥 STARTING L3 SCRAPER ON 7 VIDEO WORKFLOWS")
    print("=" * 60)
    print(f"⏰ Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Load resume state
    state = load_resume_state()
    remaining_workflows = get_remaining_workflows(state)
    
    if not remaining_workflows:
        print("🎉 All workflows already completed!")
        return True
    
    print(f"📋 Processing {len(remaining_workflows)} remaining workflows")
    print(f"🔄 Resume from: {state.get('last_workflow', 'beginning')}")
    print()
    
    try:
        from src.storage.database import get_session
        from src.scrapers.layer3_enhanced_v2 import EnhancedLayer3Extractor
        
        successful = 0
        failed = 0
        start_time = datetime.now()
        
        print("🔧 Initializing L3 scraper...")
        async with EnhancedLayer3Extractor(headless=True, extract_transcripts=True) as extractor:
            print("✅ L3 scraper initialized")
            print()
            
            for i, (workflow_id, url) in enumerate(remaining_workflows, 1):
                print(f"🎬 [{i}/{len(remaining_workflows)}] Processing {workflow_id}...")
                print(f"   URL: {url}")
                
                try:
                    result = await extractor.extract(workflow_id, url)
                    
                    if result['success']:
                        data = result['data']
                        video_count = data.get('video_count', 0)
                        transcript_count = data.get('transcript_count', 0)
                        content_length = data.get('content_length', 0)
                        quality_score = data.get('quality_score', 0)
                        
                        print(f"   ✅ SUCCESS: {video_count} videos, {transcript_count} transcripts, {content_length} chars, Q:{quality_score}")
                        
                        # Update state
                        state['completed'].append(workflow_id)
                        state['last_workflow'] = workflow_id
                        save_resume_state(state)
                        successful += 1
                        
                    else:
                        print(f"   ❌ FAILED: {result.get('error', 'Unknown error')}")
                        state['failed'].append(workflow_id)
                        state['last_workflow'] = workflow_id
                        save_resume_state(state)
                        failed += 1
                        
                except Exception as e:
                    print(f"   ❌ EXCEPTION: {e}")
                    state['failed'].append(workflow_id)
                    state['last_workflow'] = workflow_id
                    save_resume_state(state)
                    failed += 1
                
                # Display progress
                display_progress(state, workflow_id)
                
                # Small delay between workflows
                await asyncio.sleep(3)
        
        # Final summary
        total_time = datetime.now() - start_time
        print("\n🎉 VIDEO WORKFLOWS SCRAPING COMPLETE!")
        print("=" * 60)
        print(f"✅ Successful: {successful}")
        print(f"❌ Failed: {failed}")
        print(f"📊 Final Success Rate: {(successful / len(remaining_workflows)) * 100:.1f}%")
        print(f"⏰ Total Time: {str(total_time).split('.')[0]}")
        print()
        
        # Clean up resume state file
        if os.path.exists(RESUME_STATE_FILE):
            os.remove(RESUME_STATE_FILE)
            print("🧹 Cleaned up resume state file")
        
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
        success = asyncio.run(run_video_workflows())
        if success:
            print("\n✅ Video workflows scraping completed successfully!")
        else:
            print("\n❌ Video workflows scraping failed!")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n🛑 Scraping stopped by user")
        print("💾 Progress saved - run again to resume")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
