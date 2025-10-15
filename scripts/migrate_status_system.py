#!/usr/bin/env python3
"""
Status System Migration Script
Adds new status tracking columns to workflows table.
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import create_engine, text
from dotenv import load_dotenv

def main():
    """Run the status system migration."""
    
    # Load environment variables
    load_dotenv()
    
    # Get database URL from individual variables
    db_host = os.getenv('DB_HOST')
    db_port = os.getenv('DB_PORT', '5432')
    db_name = os.getenv('DB_NAME')
    db_user = os.getenv('DB_USER')
    db_password = os.getenv('DB_PASSWORD')
    
    if not all([db_host, db_name, db_user, db_password]):
        print("❌ Database configuration not found in environment variables")
        return False
    
    # URL encode password to handle special characters
    import urllib.parse
    encoded_password = urllib.parse.quote_plus(db_password)
    database_url = f"postgresql://{db_user}:{encoded_password}@{db_host}:{db_port}/{db_name}"
    
    print("🔧 Running Status System Migration...")
    print(f"📊 Database: {database_url.split('@')[1] if '@' in database_url else 'local'}")
    
    try:
        # Connect to database
        engine = create_engine(database_url)
        
        # Read migration SQL
        migration_file = project_root / 'migrations' / 'status_system_schema.sql'
        with open(migration_file, 'r') as f:
            migration_sql = f.read()
        
        # Execute migration
        with engine.connect() as conn:
            # Split SQL into individual statements
            statements = [stmt.strip() for stmt in migration_sql.split(';') if stmt.strip()]
            
            for i, statement in enumerate(statements, 1):
                if statement:
                    print(f"   {i}. Executing: {statement[:50]}...")
                    conn.execute(text(statement))
            
            conn.commit()
        
        print("✅ Status system migration completed successfully!")
        
        # Verify the changes
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT 
                    COUNT(*) as total_workflows,
                    COUNT(CASE WHEN scraping_status = 'scraping_complete' THEN 1 END) as scraping_complete,
                    COUNT(CASE WHEN scraping_status = 'scraping_in_progress' THEN 1 END) as scraping_in_progress,
                    COUNT(CASE WHEN scraping_status = 'not_started' THEN 1 END) as not_started
                FROM workflows
            """))
            
            stats = result.fetchone()
            print(f"\n📊 Migration Results:")
            print(f"   Total workflows: {stats[0]}")
            print(f"   Scraping complete: {stats[1]}")
            print(f"   Scraping in progress: {stats[2]}")
            print(f"   Not started: {stats[3]}")
        
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
