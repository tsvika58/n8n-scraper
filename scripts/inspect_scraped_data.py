#!/usr/bin/env python3
"""
Inspect actual scraped data to show all ~200 fields being extracted.

This script queries the database and displays all fields from 5 successful workflows
across all tables to verify comprehensive data extraction.
"""

import sys
import json
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.storage.database import get_session
from sqlalchemy import text

print("="*100)
print("🔍 INSPECTING SCRAPED DATA - SHOWING ALL ~200 FIELDS")
print("="*100)
print()

# Get 5 successful workflows
with get_session() as session:
    # Query for successful workflows
    query = text("""
        SELECT workflow_id, quality_score, processing_time,
               layer1_success, layer2_success, layer3_success,
               layer4_success, layer5_success, layer6_success, layer7_success
        FROM workflows
        WHERE layer1_success = true 
          AND layer2_success = true
          AND layer3_success = true
        ORDER BY extracted_at DESC
        LIMIT 5
    """)
    
    result = session.execute(query)
    workflows = result.fetchall()
    
    if not workflows:
        print("❌ No successful workflows found in database")
        sys.exit(1)
    
    print(f"✅ Found {len(workflows)} successful workflows")
    print()
    
    for idx, wf in enumerate(workflows, 1):
        workflow_id = wf[0]
        quality_score = wf[1]
        processing_time = wf[2]
        
        print("="*100)
        print(f"📊 WORKFLOW #{idx}: {workflow_id}")
        print("="*100)
        print(f"Quality Score: {quality_score:.1f}/100")
        print(f"Processing Time: {processing_time:.1f}s")
        print(f"Layers: L1={wf[3]} L2={wf[4]} L3={wf[5]} L4={wf[6]} L5={wf[7]} L6={wf[8]} L7={wf[9]}")
        print()
        
        field_count = 0
        
        # ================================================================
        # TABLE 1: workflows (core tracking)
        # ================================================================
        print("📋 TABLE 1: workflows (Core Tracking)")
        print("-"*100)
        
        query = text("""
            SELECT workflow_id, url, extracted_at, updated_at, processing_time, quality_score,
                   layer1_success, layer2_success, layer3_success, layer4_success, 
                   layer5_success, layer6_success, layer7_success,
                   error_message, retry_count, last_scraped_at, created_at
            FROM workflows WHERE workflow_id = :wf_id
        """)
        result = session.execute(query, {'wf_id': workflow_id})
        wf_data = result.fetchone()
        
        if wf_data:
            fields = ['workflow_id', 'url', 'extracted_at', 'updated_at', 'processing_time', 'quality_score',
                     'layer1_success', 'layer2_success', 'layer3_success', 'layer4_success',
                     'layer5_success', 'layer6_success', 'layer7_success',
                     'error_message', 'retry_count', 'last_scraped_at', 'created_at']
            for i, field in enumerate(fields):
                value = wf_data[i]
                if value is not None and value != '':
                    print(f"  {field_count+1:3d}. {field:30s} = {str(value)[:60]}")
                    field_count += 1
        
        print()
        
        # ================================================================
        # TABLE 2: workflow_metadata (Layer 1 - Page Metadata)
        # ================================================================
        print("📋 TABLE 2: workflow_metadata (Layer 1 - Page Metadata)")
        print("-"*100)
        
        query = text("""
            SELECT title, description, use_case, author_name, author_url,
                   views, shares, categories, tags, 
                   workflow_created_at, workflow_updated_at, extracted_at,
                   raw_metadata
            FROM workflow_metadata WHERE workflow_id = :wf_id
        """)
        result = session.execute(query, {'wf_id': workflow_id})
        meta_data = result.fetchone()
        
        if meta_data:
            # Basic fields
            basic_fields = {
                'title': meta_data[0],
                'description': meta_data[1],
                'use_case': meta_data[2],
                'author_name': meta_data[3],
                'author_url': meta_data[4],
                'views': meta_data[5],
                'shares': meta_data[6],
                'workflow_created_at': meta_data[9],
                'workflow_updated_at': meta_data[10],
                'extracted_at': meta_data[11],
            }
            
            for field, value in basic_fields.items():
                if value is not None and value != '':
                    print(f"  {field_count+1:3d}. {field:30s} = {str(value)[:60]}")
                    field_count += 1
            
            # Categories (array)
            if meta_data[7]:
                try:
                    categories = json.loads(meta_data[7])
                    for i, cat in enumerate(categories):
                        print(f"  {field_count+1:3d}. category_{i+1:02d}{' ':20s} = {cat}")
                        field_count += 1
                except:
                    pass
            
            # Tags (array)
            if meta_data[8]:
                try:
                    tags = json.loads(meta_data[8])
                    for i, tag in enumerate(tags[:10]):  # Show first 10 tags
                        print(f"  {field_count+1:3d}. tag_{i+1:02d}{' ':25s} = {tag}")
                        field_count += 1
                except:
                    pass
            
            # Raw metadata (JSON with all Layer 1 fields)
            if meta_data[12]:
                try:
                    raw_meta = json.loads(meta_data[12])
                    for key, value in raw_meta.items():
                        if key not in ['title', 'description', 'author', 'views', 'upvotes']:
                            if isinstance(value, (str, int, float, bool)):
                                print(f"  {field_count+1:3d}. meta_{key:24s} = {str(value)[:60]}")
                                field_count += 1
                            elif isinstance(value, list) and len(value) > 0:
                                print(f"  {field_count+1:3d}. meta_{key:24s} = {len(value)} items")
                                field_count += 1
                except:
                    pass
        
        print()
        
        # ================================================================
        # TABLE 3: workflow_structure (Layer 2 - JSON Structure)
        # ================================================================
        print("📋 TABLE 3: workflow_structure (Layer 2 - JSON Structure)")
        print("-"*100)
        
        query = text("""
            SELECT node_count, connection_count, node_types, 
                   extraction_type, fallback_used, workflow_json, extracted_at
            FROM workflow_structure WHERE workflow_id = :wf_id
        """)
        result = session.execute(query, {'wf_id': workflow_id})
        struct_data = result.fetchone()
        
        if struct_data:
            print(f"  {field_count+1:3d}. node_count{' ':21s} = {struct_data[0]}")
            field_count += 1
            print(f"  {field_count+1:3d}. connection_count{' ':16s} = {struct_data[1]}")
            field_count += 1
            print(f"  {field_count+1:3d}. extraction_type{' ':17s} = {struct_data[3]}")
            field_count += 1
            print(f"  {field_count+1:3d}. fallback_used{' ':18s} = {struct_data[4]}")
            field_count += 1
            
            # Node types
            if struct_data[2]:
                try:
                    node_types = json.loads(struct_data[2])
                    print(f"  {field_count+1:3d}. node_types_count{' ':16s} = {len(node_types)} unique types")
                    field_count += 1
                    for i, ntype in enumerate(node_types[:10]):  # Show first 10
                        print(f"  {field_count+1:3d}. node_type_{i+1:02d}{' ':19s} = {ntype}")
                        field_count += 1
                except:
                    pass
            
            # Workflow JSON (extract key fields)
            if struct_data[5]:
                try:
                    wf_json = json.loads(struct_data[5])
                    if 'nodes' in wf_json:
                        nodes = wf_json['nodes']
                        print(f"  {field_count+1:3d}. workflow_nodes_count{' ':10s} = {len(nodes)}")
                        field_count += 1
                        
                        # Extract node details
                        for i, node in enumerate(nodes[:5]):  # Show first 5 nodes
                            if 'type' in node:
                                print(f"  {field_count+1:3d}. node_{i+1:02d}_type{' ':18s} = {node['type']}")
                                field_count += 1
                            if 'name' in node:
                                print(f"  {field_count+1:3d}. node_{i+1:02d}_name{' ':18s} = {node['name']}")
                                field_count += 1
                    
                    if 'connections' in wf_json:
                        print(f"  {field_count+1:3d}. workflow_connections{' ':11s} = {len(wf_json['connections'])} connections")
                        field_count += 1
                except:
                    pass
        
        print()
        
        # ================================================================
        # TABLE 4: workflow_content (Layer 3 - Content)
        # ================================================================
        print("📋 TABLE 4: workflow_content (Layer 3 - Content)")
        print("-"*100)
        
        query = text("""
            SELECT explainer_text, explainer_html, setup_instructions, use_instructions,
                   has_videos, video_count, has_iframes, iframe_count,
                   raw_content, extracted_at
            FROM workflow_content WHERE workflow_id = :wf_id
        """)
        result = session.execute(query, {'wf_id': workflow_id})
        content_data = result.fetchone()
        
        if content_data:
            if content_data[0]:
                print(f"  {field_count+1:3d}. explainer_text_length{' ':10s} = {len(content_data[0])} chars")
                field_count += 1
            if content_data[1]:
                print(f"  {field_count+1:3d}. explainer_html_length{' ':10s} = {len(content_data[1])} chars")
                field_count += 1
            if content_data[2]:
                print(f"  {field_count+1:3d}. setup_instructions{' ':13s} = {len(content_data[2])} chars")
                field_count += 1
            if content_data[3]:
                print(f"  {field_count+1:3d}. use_instructions{' ':15s} = {len(content_data[3])} chars")
                field_count += 1
            
            print(f"  {field_count+1:3d}. has_videos{' ':21s} = {content_data[4]}")
            field_count += 1
            print(f"  {field_count+1:3d}. video_count{' ':20s} = {content_data[5]}")
            field_count += 1
            print(f"  {field_count+1:3d}. has_iframes{' ':20s} = {content_data[6]}")
            field_count += 1
            print(f"  {field_count+1:3d}. iframe_count{' ':19s} = {content_data[7]}")
            field_count += 1
            
            # Raw content (JSON with all Layer 3 fields)
            if content_data[8]:
                try:
                    raw_content = json.loads(content_data[8])
                    for key, value in raw_content.items():
                        if key not in ['explainer_text', 'explainer_html']:
                            if isinstance(value, (str, int, float, bool)):
                                print(f"  {field_count+1:3d}. content_{key:22s} = {str(value)[:60]}")
                                field_count += 1
                            elif isinstance(value, list):
                                print(f"  {field_count+1:3d}. content_{key:22s} = {len(value)} items")
                                field_count += 1
                except:
                    pass
        
        print()
        
        # ================================================================
        # TABLE 5: workflow_business_intelligence (Layer 4)
        # ================================================================
        print("📋 TABLE 5: workflow_business_intelligence (Layer 4 - Business Intelligence)")
        print("-"*100)
        
        query = text("""
            SELECT * FROM workflow_business_intelligence WHERE workflow_id = :wf_id
        """)
        result = session.execute(query, {'wf_id': workflow_id})
        bi_data = result.fetchone()
        
        if bi_data:
            # Get column names
            columns = result.keys()
            for i, (col, val) in enumerate(zip(columns, bi_data)):
                if col not in ['id', 'workflow_id'] and val is not None:
                    print(f"  {field_count+1:3d}. bi_{col:26s} = {str(val)[:60]}")
                    field_count += 1
        else:
            print("  ⚠️  No Layer 4 data found (may not be implemented yet)")
        
        print()
        
        # ================================================================
        # SUMMARY
        # ================================================================
        print("="*100)
        print(f"📊 TOTAL FIELDS EXTRACTED FOR WORKFLOW {workflow_id}: {field_count}")
        print("="*100)
        print()
        print()

print("="*100)
print("✅ INSPECTION COMPLETE")
print("="*100)
print()
print("💡 Note: The system extracts ~200+ fields across 7 layers.")
print("   Some layers (4-7) may still be in development or have sparse data.")
print()






