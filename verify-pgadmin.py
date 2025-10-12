#!/usr/bin/env python3
"""
Verify pgAdmin connection settings
"""

import psycopg2
from psycopg2.extras import RealDictCursor

def verify_connection():
    """Verify the exact connection that pgAdmin should use"""
    
    print("🔍 VERIFYING PGADMIN CONNECTION SETTINGS")
    print("=" * 60)
    
    # This is the EXACT connection pgAdmin should use
    config = {
        'host': 'localhost',
        'port': 5432,
        'database': 'n8n_scraper',
        'user': 'scraper_user',
        'password': 'scraper_pass'
    }
    
    print("📋 PGADMIN CONNECTION SETTINGS:")
    print(f"   Host: {config['host']}")
    print(f"   Port: {config['port']}")
    print(f"   Database: {config['database']}")
    print(f"   Username: {config['user']}")
    print(f"   Password: {config['password']}")
    print()
    
    try:
        print("🔌 Testing connection...")
        conn = psycopg2.connect(**config)
        
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Get basic stats
        cursor.execute("""
            SELECT 
                COUNT(*) as total_workflows,
                COUNT(*) FILTER (WHERE layer1_success AND layer2_success AND layer3_success) as fully_successful,
                ROUND(AVG(quality_score)::numeric, 2) as avg_quality_score,
                MIN(extracted_at) as first_workflow,
                MAX(extracted_at) as latest_workflow
            FROM workflows;
        """)
        
        stats = cursor.fetchone()
        
        print("✅ CONNECTION SUCCESSFUL!")
        print()
        print("📊 DATABASE STATISTICS:")
        print(f"   Total Workflows: {stats['total_workflows']:,}")
        print(f"   Fully Successful: {stats['fully_successful']:,}")
        print(f"   Average Quality: {stats['avg_quality_score']}%")
        print(f"   First Workflow: {stats['first_workflow']}")
        print(f"   Latest Workflow: {stats['latest_workflow']}")
        print()
        
        # Show table structure
        cursor.execute("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns 
            WHERE table_name = 'workflows'
            ORDER BY ordinal_position;
        """)
        
        columns = cursor.fetchall()
        
        print("🗂️  WORKFLOWS TABLE STRUCTURE:")
        for col in columns:
            nullable = "NULL" if col['is_nullable'] == 'YES' else "NOT NULL"
            print(f"   {col['column_name']:<20} {col['data_type']:<20} {nullable}")
        
        cursor.close()
        conn.close()
        
        print()
        print("🎯 PGADMIN SETUP INSTRUCTIONS:")
        print("=" * 60)
        print("1. In pgAdmin, right-click 'Servers' → 'Register' → 'Server...'")
        print("2. General Tab:")
        print("   - Name: N8N Scraper Database")
        print("3. Connection Tab:")
        print(f"   - Host name/address: {config['host']}")
        print(f"   - Port: {config['port']}")
        print(f"   - Maintenance database: {config['database']}")
        print(f"   - Username: {config['user']}")
        print(f"   - Password: {config['password']}")
        print("   - ✅ CHECK 'Save password'")
        print("4. Click 'Save'")
        print()
        print("🔍 TO VIEW YOUR DATA:")
        print("1. Expand: Servers → N8N Scraper Database → Databases → n8n_scraper → Schemas → public → Tables")
        print("2. Right-click 'workflows' → 'View/Edit Data' → 'All Rows'")
        print()
        print("💡 QUICK SQL QUERIES TO TRY:")
        print("   SELECT COUNT(*) FROM workflows;")
        print("   SELECT * FROM workflows ORDER BY quality_score DESC LIMIT 10;")
        print("   SELECT workflow_id, quality_score FROM workflows WHERE layer1_success = true LIMIT 20;")
        
    except Exception as e:
        print(f"❌ CONNECTION FAILED: {str(e)}")
        print()
        print("🔧 TROUBLESHOOTING:")
        print("1. Make sure Docker containers are running:")
        print("   docker-compose ps")
        print("2. Check database logs:")
        print("   docker-compose logs n8n-scraper-database")
        print("3. Verify port 5432 is accessible:")
        print("   telnet localhost 5432")

if __name__ == '__main__':
    verify_connection()
