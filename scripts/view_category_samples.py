#!/usr/bin/env python3
"""
View Category Mapping Samples

Shows sample workflows with their discovered categories.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.storage.database import get_session
from src.storage.models import Workflow, WorkflowMetadata
from sqlalchemy import text

print("=" * 80)
print("📂 CATEGORY MAPPING SAMPLES")
print("=" * 80)
print()

try:
    with get_session() as session:
        # Get category statistics
        print("📊 Category Statistics:")
        print()
        
        result = session.execute(text("""
            SELECT 
                jsonb_array_elements_text(categories) as category,
                COUNT(*) as workflow_count
            FROM workflow_metadata
            WHERE categories IS NOT NULL AND categories != 'null'::jsonb
            GROUP BY category
            ORDER BY workflow_count DESC
            LIMIT 30
        """))
        
        for i, row in enumerate(result, 1):
            print(f"   {i:2d}. {row[1]:4d} workflows - {row[0]}")
        
        print()
        print("=" * 80)
        print("📋 SAMPLE WORKFLOWS WITH CATEGORIES")
        print("=" * 80)
        print()
        
        # Get sample workflows with categories
        workflows = session.query(Workflow, WorkflowMetadata).join(
            WorkflowMetadata,
            Workflow.workflow_id == WorkflowMetadata.workflow_id
        ).filter(
            WorkflowMetadata.categories.isnot(None)
        ).limit(20).all()
        
        for workflow, metadata in workflows:
            categories_str = ', '.join(metadata.categories) if metadata.categories else 'None'
            print(f"Workflow {workflow.workflow_id}:")
            print(f"  URL: {workflow.url}")
            print(f"  Categories: {categories_str}")
            print()
        
        print("=" * 80)
        print("📈 COVERAGE ANALYSIS")
        print("=" * 80)
        print()
        
        # Count workflows with/without categories
        total = session.query(Workflow).count()
        with_categories = session.query(WorkflowMetadata).filter(
            WorkflowMetadata.categories.isnot(None),
            WorkflowMetadata.categories != 'null'
        ).count()
        
        coverage_pct = (with_categories / total * 100) if total > 0 else 0
        
        print(f"Total workflows:        {total}")
        print(f"With categories:        {with_categories}")
        print(f"Without categories:     {total - with_categories}")
        print(f"Coverage:               {coverage_pct:.1f}%")
        print()
        
        # Multi-category analysis
        result = session.execute(text("""
            SELECT 
                jsonb_array_length(categories) as category_count,
                COUNT(*) as workflow_count
            FROM workflow_metadata
            WHERE categories IS NOT NULL AND categories != 'null'::jsonb
            GROUP BY jsonb_array_length(categories)
            ORDER BY category_count
        """))
        
        print("📊 Multi-Category Distribution:")
        print()
        for row in result:
            cat_count = row[0]
            wf_count = row[1]
            print(f"   {cat_count} {'category ' if cat_count == 1 else 'categories'}: {wf_count:4d} workflows")
        
        print()
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)




