#!/usr/bin/env python3
"""
Test numerical sorting in database viewer
"""

import importlib.util
import sys

# Import the database viewer
spec = importlib.util.spec_from_file_location("view_database", "/app/scripts/view-database.py")
view_database = importlib.util.module_from_spec(spec)
spec.loader.exec_module(view_database)

try:
    # Test the get_workflows function with workflow_id sort
    workflows, total = view_database.get_workflows(
        limit=10, 
        offset=0, 
        search=None, 
        sort_by='workflow_id', 
        sort_order='ASC'
    )
    
    print("✅ Database viewer numerical sort test:")
    print("Workflow IDs in order:")
    for w in workflows:
        print(f"  {w['workflow_id']}")
    
    # Test DESC sort too
    workflows_desc, total = view_database.get_workflows(
        limit=5, 
        offset=0, 
        search=None, 
        sort_by='workflow_id', 
        sort_order='DESC'
    )
    
    print("\n✅ DESC sort test:")
    for w in workflows_desc:
        print(f"  {w['workflow_id']}")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
