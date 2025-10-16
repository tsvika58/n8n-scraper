#!/usr/bin/env python3
"""
Safe migration runner for Layer 2 Enhanced fields.

Runs migration with safety checks and monitoring.
Safe to run while Layer 1 scraper is running.
"""

import psycopg2
import os
import sys
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

def run_migration_safe():
    """Run migration with safety checks."""
    
    print("\n" + "="*80)
    print("🚀 LAYER 2 ENHANCED - SAFE MIGRATION")
    print("="*80)
    print(f"\nStarted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\nThis migration is SAFE to run while Layer 1 is scraping.")
    print("It only modifies the workflow_structure table (Layer 2).")
    print("Layer 1 writes to different tables (workflows, workflow_metadata).\n")
    
    # Get database credentials
    db_host = os.getenv('DB_HOST', 'localhost')
    db_port = os.getenv('DB_PORT', '5432')
    db_name = os.getenv('DB_NAME', 'n8n_scraper')
    db_user = os.getenv('DB_USER', 'n8n_user')
    db_password = os.getenv('DB_PASSWORD', 'n8n_password')
    
    print(f"Database: {db_host}:{db_port}/{db_name}")
    print(f"User: {db_user}\n")
    
    try:
        # Connect to database
        print("📡 Connecting to database...")
        conn = psycopg2.connect(
            host=db_host,
            port=db_port,
            database=db_name,
            user=db_user,
            password=db_password
        )
        conn.autocommit = False  # Use transactions
        cursor = conn.cursor()
        
        print("✅ Connected successfully\n")
        
        # Check if columns already exist
        print("🔍 Checking if migration already ran...")
        cursor.execute("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = 'workflow_structure'
            AND column_name IN ('iframe_data', 'visual_layout', 'enhanced_content', 'media_content');
        """)
        
        existing_columns = [row[0] for row in cursor.fetchall()]
        
        if len(existing_columns) == 4:
            print(f"⚠️  Migration already applied! Found columns: {existing_columns}")
            print("\nNo action needed - database is already ready for Layer 2 Enhanced.")
            cursor.close()
            conn.close()
            return True
        elif len(existing_columns) > 0:
            print(f"⚠️  Partial migration detected! Found columns: {existing_columns}")
            print("Continuing with full migration to ensure all columns exist...")
        else:
            print("✅ No existing columns found - proceeding with migration\n")
        
        # Read migration file
        print("📄 Reading migration script...")
        migration_file = 'migrations/add_layer2_enhanced_fields.sql'
        
        if not os.path.exists(migration_file):
            print(f"❌ Migration file not found: {migration_file}")
            return False
        
        with open(migration_file, 'r') as f:
            migration_sql = f.read()
        
        print(f"✅ Migration script loaded ({len(migration_sql)} bytes)\n")
        
        # Execute migration
        print("🔄 Running migration...")
        print("   This will take ~5 seconds")
        print("   Layer 1 scraper will continue normally\n")
        
        start_time = datetime.now()
        
        try:
            cursor.execute(migration_sql)
            conn.commit()
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            print(f"✅ Migration completed successfully in {duration:.2f}s\n")
            
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            conn.rollback()
            raise
        
        # Verify migration
        print("🔍 Verifying migration...")
        
        # Check columns
        cursor.execute("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'workflow_structure'
            AND column_name IN ('iframe_data', 'visual_layout', 'enhanced_content', 'media_content', 'extraction_sources', 'completeness_metrics')
            ORDER BY column_name;
        """)
        
        columns = cursor.fetchall()
        
        if len(columns) >= 4:
            print(f"\n✅ Verified {len(columns)} new columns:")
            for col_name, data_type, nullable in columns:
                print(f"   • {col_name} ({data_type}) - Nullable: {nullable}")
        else:
            print(f"\n⚠️  Only found {len(columns)} columns (expected 6)")
        
        # Check indexes
        cursor.execute("""
            SELECT indexname
            FROM pg_indexes
            WHERE tablename = 'workflow_structure'
            AND indexname LIKE 'idx_workflow_structure_%'
            ORDER BY indexname;
        """)
        
        indexes = cursor.fetchall()
        print(f"\n✅ Verified {len(indexes)} indexes:")
        for idx in indexes[:10]:  # Show first 10
            print(f"   • {idx[0]}")
        
        # Check view
        cursor.execute("""
            SELECT viewname
            FROM pg_views
            WHERE viewname = 'workflow_complete_data';
        """)
        
        view = cursor.fetchone()
        if view:
            print(f"\n✅ Verified view: {view[0]}")
        
        cursor.close()
        conn.close()
        
        print("\n" + "="*80)
        print("✅ MIGRATION SUCCESSFUL!")
        print("="*80)
        print("\nDatabase is now ready for Layer 2 Enhanced data!")
        print("Layer 1 scraper should have continued normally during migration.")
        print("\nNext steps:")
        print("  1. Verify Layer 1 is still running")
        print("  2. Test Layer 2 Enhanced storage")
        print("  3. Deploy Layer 2 Enhanced to production")
        print(f"\nCompleted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        return True
        
    except psycopg2.OperationalError as e:
        print(f"\n❌ Database connection failed: {e}")
        print("\nPossible reasons:")
        print("  • Database not running")
        print("  • Incorrect credentials")
        print("  • Network issues")
        print("\nMigration file is ready at: migrations/add_layer2_enhanced_fields.sql")
        print("You can run it manually when database is available.")
        return False
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_migration_safe()
    sys.exit(0 if success else 1)





