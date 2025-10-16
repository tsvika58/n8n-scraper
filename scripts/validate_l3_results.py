"""
Layer 3 Results Validation Script

Quick validation of L3 extraction results for the 7 test URLs.

Author: AI Assistant
Date: October 15, 2025
"""

import sys
sys.path.append('/app')

from src.storage.global_connection_coordinator import global_coordinator
from sqlalchemy import text
import json

def validate_l3_results():
    """Validate L3 extraction results"""
    
    test_workflows = ['6270', '8642', '8527', '8237', '7639', '5170', '2462']
    
    with global_coordinator.get_session() as session:
        print('🔍 LAYER 3 VALIDATION RESULTS')
        print('=' * 80)
        
        total_videos = 0
        total_transcripts = 0
        completed_workflows = 0
        
        for workflow_id in test_workflows:
            result = session.execute(text('''
                SELECT 
                    video_count, transcript_count, has_videos, has_transcripts,
                    layer3_success, layer3_extracted_at, quality_score,
                    video_urls, transcripts
                FROM workflow_content
                WHERE workflow_id = :workflow_id
            '''), {"workflow_id": workflow_id}).fetchone()
            
            if result:
                video_count, transcript_count, has_videos, has_transcripts, success, extracted_at, quality, video_urls, transcripts = result
                
                status = "✅" if success else "❌"
                print(f'{status} {workflow_id}: {video_count} videos, {transcript_count} transcripts, Q:{quality or 0}')
                
                if success:
                    completed_workflows += 1
                    total_videos += video_count or 0
                    total_transcripts += transcript_count or 0
                    
                    # Show video URLs if any
                    if video_urls:
                        print(f'   🎥 Videos: {", ".join(video_urls[:3])}{"..." if len(video_urls) > 3 else ""}')
                    
                    # Show transcript status
                    if transcripts:
                        try:
                            transcript_data = json.loads(transcripts) if isinstance(transcripts, str) else transcripts
                            if transcript_data:
                                print(f'   📝 Transcripts: {len(transcript_data)} available')
                        except:
                            pass
            else:
                print(f'❌ {workflow_id}: No L3 data found')
        
        print()
        print('📊 SUMMARY:')
        print(f'✅ Completed workflows: {completed_workflows}/{len(test_workflows)}')
        print(f'🎥 Total videos found: {total_videos}')
        print(f'📝 Total transcripts: {total_transcripts}')
        print(f'📈 Success rate: {(completed_workflows/len(test_workflows)*100):.1f}%')

if __name__ == "__main__":
    validate_l3_results()

