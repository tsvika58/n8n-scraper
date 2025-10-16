#!/usr/bin/env python3
"""
Apply Schema Fixes
Applies the missing fields migration to the database.

Author: Dev1
Task: Apply Schema Fixes
Date: October 16, 2025
"""

import sys
sys.path.append('.')

from src.storage.database import get_session
from sqlalchemy import text


def apply_schema_fixes():
    """Apply the missing fields migration."""
    print("🔧 Applying Schema Fixes...")
    
    with get_session() as session:
        try:
            # Add missing extraction timestamp fields
            session.execute(text("""
                ALTER TABLE workflows ADD COLUMN IF NOT EXISTS layer2_extracted_at TIMESTAMP;
            """))
            session.execute(text("""
                ALTER TABLE workflows ADD COLUMN IF NOT EXISTS layer3_extracted_at TIMESTAMP;
            """))
            
            # Add unified extraction fields for new approach
            session.execute(text("""
                ALTER TABLE workflows ADD COLUMN IF NOT EXISTS unified_extraction_success BOOLEAN DEFAULT FALSE;
            """))
            session.execute(text("""
                ALTER TABLE workflows ADD COLUMN IF NOT EXISTS unified_extraction_at TIMESTAMP;
            """))
            
            # Add indexes for performance
            session.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_workflows_layer2_extracted ON workflows(layer2_extracted_at);
            """))
            session.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_workflows_layer3_extracted ON workflows(layer3_extracted_at);
            """))
            session.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_workflows_unified_extraction ON workflows(unified_extraction_success);
            """))
            
            session.commit()
            print("   ✅ Schema fixes applied successfully")
            
            # Verify the changes
            result = session.execute(text("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'workflows' 
                AND column_name IN ('layer2_extracted_at', 'layer3_extracted_at', 'unified_extraction_success', 'unified_extraction_at')
                ORDER BY column_name;
            """)).fetchall()
            
            print("   📋 Added columns:")
            for row in result:
                print(f"      - {row[0]}: {row[1]}")
            
            return True
            
        except Exception as e:
            print(f"   ❌ Error applying schema fixes: {e}")
            session.rollback()
            return False


if __name__ == "__main__":
    success = apply_schema_fixes()
    if success:
        print("🏆 Schema fixes applied successfully!")
    else:
        print("❌ Failed to apply schema fixes")
        sys.exit(1)

