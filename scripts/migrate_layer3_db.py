"""
Migrate Layer 3 Database Schema

Author: Developer-2 (Dev2)
Date: October 14, 2025
"""

import sys
from pathlib import Path

sys.path.append('/app')

from src.storage.database import get_session
from sqlalchemy import text

def migrate():
    """Execute migration"""
    
    print('🔄 LAYER 3 COMPREHENSIVE SCHEMA MIGRATION')
    print('=' * 80)
    print()
    
    # Create table
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS workflow_content (
        id SERIAL PRIMARY KEY,
        workflow_id VARCHAR(50) UNIQUE NOT NULL,
        
        video_urls TEXT[] DEFAULT '{}',
        video_metadata JSONB DEFAULT '[]',
        video_count INTEGER DEFAULT 0,
        has_videos BOOLEAN DEFAULT FALSE,
        
        transcripts JSONB DEFAULT '{}',
        transcript_count INTEGER DEFAULT 0,
        has_transcripts BOOLEAN DEFAULT FALSE,
        
        content_text TEXT,
        content_html TEXT,
        content_markdown TEXT,
        total_text_length INTEGER DEFAULT 0,
        
        image_urls TEXT[] DEFAULT '{}',
        image_count INTEGER DEFAULT 0,
        link_urls TEXT[] DEFAULT '{}',
        link_count INTEGER DEFAULT 0,
        
        iframe_sources TEXT[] DEFAULT '{}',
        iframe_count INTEGER DEFAULT 0,
        has_iframes BOOLEAN DEFAULT FALSE,
        iframe_content JSONB DEFAULT '[]',
        
        meta_tags JSONB DEFAULT '{}',
        data_attributes JSONB DEFAULT '[]',
        
        extraction_passes JSONB DEFAULT '{}',
        deduplication_stats JSONB DEFAULT '{}',
        quality_score INTEGER DEFAULT 0,
        
        content_hash VARCHAR(64),
        screenshot_path TEXT,
        validation_data JSONB DEFAULT '{}',
        
        layer3_success BOOLEAN DEFAULT FALSE,
        layer3_extracted_at TIMESTAMP,
        layer3_version VARCHAR(20) DEFAULT '3.0.0-comprehensive'
    )
    """
    
    gin_indexes = [
        "CREATE INDEX IF NOT EXISTS idx_video_metadata_gin ON workflow_content USING gin(video_metadata)",
        "CREATE INDEX IF NOT EXISTS idx_transcripts_gin ON workflow_content USING gin(transcripts)",
        "CREATE INDEX IF NOT EXISTS idx_iframe_content_gin ON workflow_content USING gin(iframe_content)",
        "CREATE INDEX IF NOT EXISTS idx_meta_tags_gin ON workflow_content USING gin(meta_tags)",
        "CREATE INDEX IF NOT EXISTS idx_extraction_passes_gin ON workflow_content USING gin(extraction_passes)",
        "CREATE INDEX IF NOT EXISTS idx_video_urls_gin ON workflow_content USING gin(video_urls)",
    ]
    
    btree_indexes = [
        "CREATE INDEX IF NOT EXISTS idx_has_videos ON workflow_content(has_videos)",
        "CREATE INDEX IF NOT EXISTS idx_has_transcripts ON workflow_content(has_transcripts)",
        "CREATE INDEX IF NOT EXISTS idx_layer3_success ON workflow_content(layer3_success)",
        "CREATE INDEX IF NOT EXISTS idx_quality_score ON workflow_content(quality_score)",
    ]
    
    try:
        with get_session() as session:
            print('⚙️  Creating table...')
            session.execute(text(create_table_sql))
            session.commit()
            print('✅ Table created!')
            print()
            
            print('⚙️  Creating GIN indexes...')
            for idx_sql in gin_indexes:
                session.execute(text(idx_sql))
            session.commit()
            print(f'✅ Created {len(gin_indexes)} GIN indexes!')
            print()
            
            print('⚙️  Creating B-tree indexes...')
            for idx_sql in btree_indexes:
                session.execute(text(idx_sql))
            session.commit()
            print(f'✅ Created {len(btree_indexes)} B-tree indexes!')
            print()
            
            print('=' * 80)
            print('🎉 MIGRATION COMPLETE!')
            print('=' * 80)
            return True
            
    except Exception as e:
        print(f'❌ Error: {e}')
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = migrate()
    sys.exit(0 if success else 1)



