#!/usr/bin/env python3
"""
Enhance database schema for better status tracking
"""

import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime

def get_db_connection():
    """Get database connection"""
    return psycopg2.connect(
        host='n8n-scraper-database',
        port=5432,
        database='n8n_scraper',
        user='scraper_user',
        password='scraper_pass'
    )

def enhance_schema():
    """Add new columns for better tracking"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Add last_scraped_at column if it doesn't exist
        cursor.execute("""
            ALTER TABLE workflows 
            ADD COLUMN IF NOT EXISTS last_scraped_at TIMESTAMP DEFAULT NULL;
        """)
        
        # Add created_at column if it doesn't exist
        cursor.execute("""
            ALTER TABLE workflows 
            ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT NOW();
        """)
        
        # Update existing records to have created_at = extracted_at
        cursor.execute("""
            UPDATE workflows 
            SET created_at = extracted_at 
            WHERE created_at IS NULL AND extracted_at IS NOT NULL;
        """)
        
        # Update existing records to have last_scraped_at = extracted_at if they have any success
        cursor.execute("""
            UPDATE workflows 
            SET last_scraped_at = extracted_at 
            WHERE last_scraped_at IS NULL 
            AND (layer1_success = true OR layer2_success = true OR layer3_success = true);
        """)
        
        conn.commit()
        print("✅ Database schema enhanced successfully")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error enhancing schema: {e}")
    finally:
        cursor.close()
        conn.close()

def test_enhanced_schema():
    """Test the enhanced schema"""
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        # Get sample data to verify
        cursor.execute("""
            SELECT 
                workflow_id,
                url,
                created_at,
                extracted_at,
                last_scraped_at,
                layer1_success,
                layer2_success,
                layer3_success,
                CASE 
                    WHEN layer1_success AND layer2_success AND layer3_success THEN 'fully_scraped'
                    WHEN layer1_success OR layer2_success OR layer3_success THEN 'partially_scraped'
                    WHEN last_scraped_at IS NOT NULL THEN 'attempted'
                    ELSE 'not_scraped'
                END as status
            FROM workflows 
            ORDER BY workflow_id 
            LIMIT 10;
        """)
        
        workflows = cursor.fetchall()
        
        print("📊 Enhanced Schema Test Results:")
        print("=" * 80)
        for w in workflows:
            print(f"ID: {w['workflow_id']}")
            print(f"  Status: {w['status']}")
            print(f"  Created: {w['created_at']}")
            print(f"  Extracted: {w['extracted_at']}")
            print(f"  Last Scraped: {w['last_scraped_at']}")
            print(f"  Layers: L1={w['layer1_success']}, L2={w['layer2_success']}, L3={w['layer3_success']}")
            print()
            
    except Exception as e:
        print(f"❌ Error testing schema: {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    print("🔧 Enhancing Database Schema...")
    enhance_schema()
    print("\n🧪 Testing Enhanced Schema...")
    test_enhanced_schema()



