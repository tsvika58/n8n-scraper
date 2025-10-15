#!/usr/bin/env python3
"""Show all fields from a complete workflow to demonstrate the 324 fields."""

import sys
import json
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.storage.database import get_session
from sqlalchemy import text

workflow_id = "2137"

print("="*100)
print(f"🔍 COMPLETE WORKFLOW DATA: {workflow_id}")
print("="*100)
print()

field_count = 0

with get_session() as session:
    # Get all tables
    tables = [
        ('workflows', 'Core Tracking'),
        ('workflow_metadata', 'Layer 1 - Metadata'),
        ('workflow_structure', 'Layer 2 - Structure'),
        ('workflow_content', 'Layer 3 - Content'),
        ('workflow_business_intelligence', 'Layer 4 - Business Intelligence'),
        ('workflow_community_data', 'Layer 5 - Community'),
        ('workflow_technical_details', 'Layer 6 - Technical'),
        ('workflow_performance_analytics', 'Layer 7 - Performance'),
    ]
    
    for table_name, layer_name in tables:
        print(f"\n{'='*100}")
        print(f"📋 {table_name.upper()}")
        print(f"   {layer_name}")
        print(f"{'='*100}\n")
        
        # Get column names
        col_query = text(f"""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = '{table_name}' 
            ORDER BY ordinal_position
        """)
        columns_result = session.execute(col_query)
        columns = [(row[0], row[1]) for row in columns_result]
        
        # Get data
        data_query = text(f"SELECT * FROM {table_name} WHERE workflow_id = :wf_id")
        data_result = session.execute(data_query, {'wf_id': workflow_id})
        data = data_result.fetchone()
        
        if data:
            table_fields = 0
            for i, (col_name, col_type) in enumerate(columns):
                value = data[i]
                
                if value is not None and value != '':
                    # Handle different data types
                    if col_type == 'jsonb':
                        try:
                            json_data = json.loads(value) if isinstance(value, str) else value
                            if isinstance(json_data, list):
                                print(f"  {field_count+1:3d}. {col_name:35s} = [{len(json_data)} items]")
                                # Show first few items
                                for j, item in enumerate(json_data[:3]):
                                    print(f"       {' ':35s}   [{j}] {str(item)[:60]}")
                            elif isinstance(json_data, dict):
                                print(f"  {field_count+1:3d}. {col_name:35s} = {{{len(json_data)} keys}}")
                                # Show first few keys
                                for j, (key, val) in enumerate(list(json_data.items())[:3]):
                                    print(f"       {' ':35s}   {key}: {str(val)[:50]}")
                            else:
                                print(f"  {field_count+1:3d}. {col_name:35s} = {str(json_data)[:60]}")
                        except:
                            print(f"  {field_count+1:3d}. {col_name:35s} = {str(value)[:60]}")
                    elif col_type == 'text' and len(str(value)) > 100:
                        print(f"  {field_count+1:3d}. {col_name:35s} = {len(str(value))} characters")
                    else:
                        print(f"  {field_count+1:3d}. {col_name:35s} = {str(value)[:70]}")
                    
                    field_count += 1
                    table_fields += 1
            
            print(f"\n   ✅ {table_fields} fields with data in this table")
        else:
            print(f"   ⚠️  No data found in this table for workflow {workflow_id}")

print("\n" + "="*100)
print(f"📊 TOTAL NON-NULL FIELDS: {field_count}")
print("="*100)
print()
print(f"💡 This workflow has {field_count} fields populated across all tables.")
print(f"   The database schema supports 324 total fields.")
print()






