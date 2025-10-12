#!/usr/bin/env python3
"""
Test database connection from outside Docker
"""

import psycopg2
from psycopg2.extras import RealDictCursor

def test_connection():
    """Test connection with different host configurations"""
    
    configs = [
        {
            'name': 'localhost',
            'host': 'localhost',
            'port': 5432,
            'database': 'n8n_scraper',
            'user': 'scraper_user',
            'password': 'scraper_pass'
        },
        {
            'name': 'container name',
            'host': 'n8n-scraper-database',
            'port': 5432,
            'database': 'n8n_scraper',
            'user': 'scraper_user',
            'password': 'scraper_pass'
        },
        {
            'name': '127.0.0.1',
            'host': '127.0.0.1',
            'port': 5432,
            'database': 'n8n_scraper',
            'user': 'scraper_user',
            'password': 'scraper_pass'
        }
    ]
    
    print("🔍 Testing Database Connections...")
    print("=" * 50)
    
    for config in configs:
        print(f"\n📡 Testing: {config['name']} ({config['host']}:{config['port']})")
        try:
            conn = psycopg2.connect(
                host=config['host'],
                port=config['port'],
                database=config['database'],
                user=config['user'],
                password=config['password']
            )
            
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute("SELECT COUNT(*) as count FROM workflows;")
            result = cursor.fetchone()
            
            print(f"✅ SUCCESS! Connected and found {result['count']} workflows")
            
            cursor.close()
            conn.close()
            
        except Exception as e:
            print(f"❌ FAILED: {str(e)}")
    
    print("\n" + "=" * 50)
    print("🎯 RECOMMENDATION FOR PGADMIN:")
    print("Use 'localhost' as the host name in pgAdmin")
    print("Port: 5432")
    print("Database: n8n_scraper")
    print("Username: scraper_user")
    print("Password: scraper_pass")

if __name__ == '__main__':
    test_connection()
