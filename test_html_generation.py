#!/usr/bin/env python3
"""
Test HTML generation to find the formatting error
"""

import importlib.util
import sys

# Import the database viewer
spec = importlib.util.spec_from_file_location("view_database", "/app/scripts/view-database.py")
view_database = importlib.util.module_from_spec(spec)
spec.loader.exec_module(view_database)

try:
    # Get statistics and workflows
    stats = view_database.get_statistics()
    workflows, total = view_database.get_workflows(limit=5)
    
    print("✅ Data retrieved successfully")
    print(f"Stats: {stats}")
    print(f"Workflows: {len(workflows)}")
    
    # Test HTML generation
    html = view_database.generate_html(workflows, stats, total, page=1, limit=5, search=None, sort_by='extracted_at', sort_order='desc')
    print("✅ HTML generated successfully")
    print("HTML length:", len(html))
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
