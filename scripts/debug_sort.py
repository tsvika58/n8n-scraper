#!/usr/bin/env python3
"""
Debug the sorting issue
"""

import psycopg2
from psycopg2.extras import RealDictCursor

def get_db_connection():
    return psycopg2.connect(
        host='n8n-scraper-database',
        port=5432,
        database='n8n_scraper',
        user='scraper_user',
        password='scraper_pass'
    )

# Test the exact query the database viewer should be using
conn = get_db_connection()
cursor = conn.cursor(cursor_factory=RealDictCursor)

# Test string sort (what we're seeing)
print("=== STRING SORT (what we're seeing) ===")
cursor.execute("SELECT workflow_id FROM workflows ORDER BY workflow_id ASC LIMIT 10")
workflows = cursor.fetchall()
for w in workflows:
    print(f"  {w['workflow_id']}")

print("\n=== NUMERICAL SORT (what we want) ===")
cursor.execute("SELECT workflow_id FROM workflows ORDER BY CAST(workflow_id AS INTEGER) ASC LIMIT 10")
workflows = cursor.fetchall()
for w in workflows:
    print(f"  {w['workflow_id']}")

cursor.close()
conn.close()



