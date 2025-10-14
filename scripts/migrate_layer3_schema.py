"""
Migrate Layer 3 Schema to Comprehensive Version

Safely migrates workflow_content table to support:
- Video URLs array
- Video metadata JSONB
- Transcripts JSONB
- Complete DOM content
- Multi-pass extraction metadata
- GIN indexes for fast queries

Author: Developer-2 (Dev2)
Task: SCRAPE-010
Date: October 14, 2025
"""

import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / 'src'))

from storage.database import get_session
from sqlalchemy import text
from loguru import logger


def migrate_schema():
    """Execute schema migration"""
    
    print('🔄 LAYER 3 COMPREHENSIVE SCHEMA MIGRATION')
    print('=' * 80)
    print()
    
    migration_file = Path(__file__).parent.parent / 'migrations' / 'layer3_comprehensive_schema.sql'
    
    if not migration_file.exists():
        print(f'❌ Migration file not found: {migration_file}')
        return False
    
    print(f'📄 Loading migration from: {migration_file}')
    migration_sql = migration_file.read_text()
    
    print('🔍 Migration will create/update:')
    print('   - workflow_content table with comprehensive schema')
    print('   - Video URLs array (TEXT[])')
    print('   - Video metadata (JSONB with GIN index)')
    print('   - Transcripts (JSONB with GIN index)')
    print('   - Complete DOM content (TEXT)')
    print('   - Multi-pass extraction metadata (JSONB)')
    print('   - Deduplication stats (JSONB)')
    print('   - 12 GIN indexes for fast JSONB queries')
    print('   - 6 B-tree indexes for common queries')
    print('   - Full-text search index for content')
    print()
    
    try:
        with get_session() as session:
            print('⚙️  Executing migration...')
            
            # Execute migration
            session.execute(text(migration_sql))
            session.commit()
            
            print('✅ Migration executed successfully!')
            print()
            
            # Verify schema
            print('🔍 Verifying schema...')
            
            # Check columns
            result = session.execute(text("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_name = 'workflow_content'
                ORDER BY ordinal_position
            """))
            
            columns = result.fetchall()
            print(f'✅ Table has {len(columns)} columns:')
            for col in columns[:10]:  # Show first 10
                print(f'   - {col[0]}: {col[1]}')
            if len(columns) > 10:
                print(f'   ... and {len(columns) - 10} more')
            print()
            
            # Check indexes
            result = session.execute(text("""
                SELECT indexname, indexdef
                FROM pg_indexes
                WHERE tablename = 'workflow_content'
                ORDER BY indexname
            """))
            
            indexes = result.fetchall()
            print(f'✅ Table has {len(indexes)} indexes:')
            for idx in indexes[:10]:  # Show first 10
                print(f'   - {idx[0]}')
            if len(indexes) > 10:
                print(f'   ... and {len(indexes) - 10} more')
            print()
            
            # Check GIN indexes specifically
            result = session.execute(text("""
                SELECT indexname
                FROM pg_indexes
                WHERE tablename = 'workflow_content'
                  AND indexdef LIKE '%gin%'
            """))
            
            gin_indexes = result.fetchall()
            print(f'✅ GIN indexes: {len(gin_indexes)}')
            for idx in gin_indexes:
                print(f'   - {idx[0]}')
            print()
            
            print('=' * 80)
            print('🎉 SCHEMA MIGRATION COMPLETE!')
            print('=' * 80)
            print()
            print('✅ Database is ready for comprehensive Layer 3 extraction!')
            print()
            
            return True
            
    except Exception as e:
        print(f'❌ Migration failed: {str(e)}')
        logger.error(f"Schema migration error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = migrate_schema()
    sys.exit(0 if success else 1)
