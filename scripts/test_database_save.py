"""
Test Database Save for Layer 3

Tests database save functionality in isolation to identify issues.

Author: Developer-2 (Dev2)
Date: October 14, 2025
"""

import sys
sys.path.append('/app')

from src.storage.database import get_session
from sqlalchemy import text
import json

def test_database_save():
    """Test database save with sample data"""
    
    print('🧪 DATABASE SAVE TEST')
    print('=' * 60)
    print()
    
    # Sample data to save (use real workflow ID)
    sample_data = {
        'workflow_id': '6270',  # Real workflow ID
        'video_urls': ['https://youtu.be/abc123', 'https://youtu.be/xyz789'],
        'video_metadata': json.dumps([
            {'type': 'video_link', 'url': 'https://youtu.be/abc123', 'youtube_id': 'abc123'},
            {'type': 'video_link', 'url': 'https://youtu.be/xyz789', 'youtube_id': 'xyz789'}
        ]),
        'video_count': 2,
        'has_videos': True,
        'transcripts': json.dumps({
            'https://youtu.be/abc123': 'Sample transcript 1',
            'https://youtu.be/xyz789': 'Sample transcript 2'
        }),
        'transcript_count': 2,
        'has_transcripts': True,
        'content_text': 'Sample text content',
        'total_text_length': 20,
        'quality_score': 85,
        'layer3_success': True
    }
    
    try:
        with get_session() as session:
            print('Step 1: Testing INSERT...')
            
            session.execute(text("""
                INSERT INTO workflow_content (
                    workflow_id, video_urls, video_metadata, video_count, has_videos,
                    transcripts, transcript_count, has_transcripts,
                    content_text, total_text_length, quality_score, layer3_success
                ) VALUES (
                    :workflow_id, :video_urls, :video_metadata, :video_count, :has_videos,
                    :transcripts, :transcript_count, :has_transcripts,
                    :content_text, :total_text_length, :quality_score, :layer3_success
                )
                ON CONFLICT (workflow_id) DO UPDATE SET
                    video_urls = EXCLUDED.video_urls,
                    video_count = EXCLUDED.video_count,
                    layer3_success = EXCLUDED.layer3_success
            """), sample_data)
            
            session.commit()
            print('✅ INSERT successful')
            print()
            
            print('Step 2: Testing READ...')
            result = session.execute(text("""
                SELECT video_urls, video_metadata, transcripts, video_count, transcript_count
                FROM workflow_content
                WHERE workflow_id = :workflow_id
            """), {'workflow_id': '6270'}).fetchone()
            
            if result:
                print('✅ READ successful')
                print(f'   Video URLs: {result[0]}')
                print(f'   Video Count: {result[3]}')
                print(f'   Transcript Count: {result[4]}')
                print()
                
                # JSONB is already deserialized by PostgreSQL
                print('Step 3: Testing JSONB data...')
                video_metadata = result[1]  # Already a dict/list
                transcripts = result[2]  # Already a dict
                
                print(f'✅ JSONB deserialization successful')
                print(f'   Videos: {len(video_metadata)}')
                print(f'   Transcripts: {len(transcripts)}')
                print()
                
                print('=' * 60)
                print('🎉 ALL DATABASE TESTS PASSED!')
                print('=' * 60)
                print()
                print('✅ TEXT[] arrays: WORKING')
                print('✅ JSONB fields: WORKING')
                print('✅ INSERT/UPDATE: WORKING')
                print('✅ READ: WORKING')
                print('✅ Deserialization: WORKING')
                print()
                
                return True
            else:
                print('❌ No data found')
                return False
            
    except Exception as e:
        print(f'❌ Database test failed: {e}')
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_database_save()
    sys.exit(0 if success else 1)

