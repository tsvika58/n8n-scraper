#!/usr/bin/env python3
"""
Test script to verify database viewer functionality
"""

import sys
import os

# Add the scripts directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scripts'))

try:
    # Try to import the database viewer
    import importlib.util
    spec = importlib.util.spec_from_file_location("view_database", "/app/scripts/view-database.py")
    view_database = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(view_database)
    
    get_db_connection = view_database.get_db_connection
    get_statistics = view_database.get_statistics
    get_workflows = view_database.get_workflows
    
    print("✅ Database viewer imports successfully")
    
    # Test database connection
    try:
        conn = get_db_connection()
        print("✅ Database connection successful")
        conn.close()
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
    
    # Test statistics
    try:
        stats = get_statistics()
        print(f"✅ Statistics retrieved: {stats}")
    except Exception as e:
        print(f"❌ Statistics failed: {e}")
    
    # Test workflows
    try:
        workflows, total = get_workflows(limit=5)
        print(f"✅ Workflows retrieved: {len(workflows)} of {total}")
    except Exception as e:
        print(f"❌ Workflows failed: {e}")
        
except Exception as e:
    print(f"❌ Import failed: {e}")
    import traceback
    traceback.print_exc()
