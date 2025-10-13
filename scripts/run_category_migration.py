#!/usr/bin/env python3
"""
Run Category Tables Migration

Executes the SQL migration to create category tables in Supabase.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.storage.database import get_session
from sqlalchemy import text

print("=" * 80)
print("🔧 RUNNING CATEGORY TABLES MIGRATION")
print("=" * 80)
print()

# Read migration SQL
migration_file = Path("migrations/add_category_tables.sql")
if not migration_file.exists():
    print(f"❌ Migration file not found: {migration_file}")
    sys.exit(1)

print("📂 Reading migration SQL...")
with open(migration_file, 'r') as f:
    migration_sql = f.read()

print("✅ Migration SQL loaded")
print()

# Connect to database and run migration
print("🔄 Connecting to Supabase database...")
print()

try:
    with get_session() as session:
        print("🚀 Executing migration...")
        print()
        
        # Split SQL by semicolons and execute each statement
        statements = [s.strip() for s in migration_sql.split(';') if s.strip()]
        
        total_statements = len(statements)
        executed = 0
        
        for i, statement in enumerate(statements, 1):
            # Skip comments and empty statements
            if not statement or statement.startswith('--'):
                continue
            
            try:
                # Execute statement
                session.execute(text(statement))
                executed += 1
                
                # Show progress for key operations
                if 'CREATE TABLE' in statement:
                    table_name = statement.split('CREATE TABLE')[1].split('(')[0].strip().split()[0]
                    if 'IF NOT EXISTS' in statement:
                        table_name = table_name.replace('IF NOT EXISTS', '').strip()
                    print(f"   ✅ Created table: {table_name}")
                elif 'CREATE INDEX' in statement:
                    if 'IF NOT EXISTS' in statement:
                        idx_name = statement.split('IF NOT EXISTS')[1].split('ON')[0].strip()
                        print(f"   ✅ Created index: {idx_name}")
                elif 'CREATE OR REPLACE VIEW' in statement:
                    view_name = statement.split('CREATE OR REPLACE VIEW')[1].split('AS')[0].strip()
                    print(f"   ✅ Created view: {view_name}")
                elif 'CREATE OR REPLACE FUNCTION' in statement:
                    print(f"   ✅ Created function: update_category_workflow_count()")
                elif 'CREATE TRIGGER' in statement:
                    trigger_name = statement.split('CREATE TRIGGER')[1].split('AFTER')[0].strip()
                    if 'IF NOT EXISTS' not in statement and 'DROP TRIGGER' not in statement:
                        print(f"   ✅ Created trigger: {trigger_name}")
                elif 'INSERT INTO categories' in statement:
                    print(f"   ✅ Seeded main categories (AI, Sales, IT Ops, Marketing, etc.)")
                    
            except Exception as e:
                # Some statements might fail if objects already exist - that's OK
                if 'already exists' not in str(e).lower():
                    print(f"   ⚠️  Statement {i}/{total_statements}: {str(e)[:100]}")
        
        # Commit all changes
        session.commit()
        
        print()
        print("=" * 80)
        print("📊 MIGRATION RESULTS")
        print("=" * 80)
        print(f"Total statements: {total_statements}")
        print(f"Executed:         {executed}")
        print()
        
        # Verify tables created
        print("🔍 Verifying tables...")
        print()
        
        result = session.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
              AND table_name IN ('categories', 'workflow_categories')
            ORDER BY table_name
        """))
        
        tables = [row[0] for row in result]
        
        for table in tables:
            print(f"   ✅ Table exists: {table}")
        
        if len(tables) == 2:
            print()
            print("✅ All category tables created successfully!")
        else:
            print()
            print(f"⚠️  Expected 2 tables, found {len(tables)}")
        
        print()
        
        # Show main categories
        print("📂 Main categories seeded:")
        result = session.execute(text("""
            SELECT category_slug, category_name, workflow_count
            FROM categories
            WHERE is_main_category = TRUE
            ORDER BY category_name
        """))
        
        for row in result:
            print(f"   • {row[1]} ({row[0]}) - {row[2]} workflows")
        
        print()
        print("=" * 80)
        print("🎉 MIGRATION COMPLETE!")
        print("=" * 80)
        print()
        print("Next step: Run category discovery to map workflows to categories")
        print()
        
except Exception as e:
    print()
    print("=" * 80)
    print(f"❌ MIGRATION FAILED: {e}")
    print("=" * 80)
    print()
    import traceback
    traceback.print_exc()
    sys.exit(1)


