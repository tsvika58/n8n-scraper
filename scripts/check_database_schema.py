#!/usr/bin/env python3
"""
Check Database Schema
Check what columns actually exist in the database tables.

Author: Dev1
Task: Check Database Schema
Date: October 16, 2025
"""

import sys
import os
sys.path.append('.')

from src.storage.database import get_session
from sqlalchemy import text


def check_schema():
    """Check the actual database schema."""
    print("🔍 Checking Database Schema")
    print("=" * 50)
    
    try:
        with get_session() as session:
            # Check workflows table
            print("📋 Workflows Table:")
            workflows_query = """
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'workflows' 
            AND table_schema = 'public'
            ORDER BY ordinal_position;
            """
            
            result = session.execute(text(workflows_query))
            workflows_columns = result.fetchall()
            
            for col in workflows_columns:
                print(f"   - {col[0]}: {col[1]} {'NULL' if col[2] == 'YES' else 'NOT NULL'}")
            
            print(f"\n   Total columns: {len(workflows_columns)}")
            
            # Check workflow_node_contexts table
            print("\n📋 Workflow Node Contexts Table:")
            node_contexts_query = """
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'workflow_node_contexts' 
            AND table_schema = 'public'
            ORDER BY ordinal_position;
            """
            
            result = session.execute(text(node_contexts_query))
            node_contexts_columns = result.fetchall()
            
            for col in node_contexts_columns:
                print(f"   - {col[0]}: {col[1]} {'NULL' if col[2] == 'YES' else 'NOT NULL'}")
            
            print(f"\n   Total columns: {len(node_contexts_columns)}")
            
            # Check workflow_standalone_docs table
            print("\n📋 Workflow Standalone Docs Table:")
            standalone_docs_query = """
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'workflow_standalone_docs' 
            AND table_schema = 'public'
            ORDER BY ordinal_position;
            """
            
            result = session.execute(text(standalone_docs_query))
            standalone_docs_columns = result.fetchall()
            
            for col in standalone_docs_columns:
                print(f"   - {col[0]}: {col[1]} {'NULL' if col[2] == 'YES' else 'NOT NULL'}")
            
            print(f"\n   Total columns: {len(standalone_docs_columns)}")
            
            # Check workflow_extraction_snapshots table
            print("\n📋 Workflow Extraction Snapshots Table:")
            snapshots_query = """
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'workflow_extraction_snapshots' 
            AND table_schema = 'public'
            ORDER BY ordinal_position;
            """
            
            result = session.execute(text(snapshots_query))
            snapshots_columns = result.fetchall()
            
            for col in snapshots_columns:
                print(f"   - {col[0]}: {col[1]} {'NULL' if col[2] == 'YES' else 'NOT NULL'}")
            
            print(f"\n   Total columns: {len(snapshots_columns)}")
            
            # Check existing indexes
            print("\n📋 Existing Indexes:")
            indexes_query = """
            SELECT indexname, tablename, indexdef
            FROM pg_indexes 
            WHERE schemaname = 'public' 
            AND tablename IN ('workflows', 'workflow_node_contexts', 'workflow_standalone_docs', 'workflow_extraction_snapshots')
            ORDER BY tablename, indexname;
            """
            
            result = session.execute(text(indexes_query))
            indexes = result.fetchall()
            
            for idx in indexes:
                print(f"   - {idx[0]} on {idx[1]}")
            
            print(f"\n   Total indexes: {len(indexes)}")
            
            # Check existing constraints
            print("\n📋 Existing Constraints:")
            constraints_query = """
            SELECT conname, contype, conrelid::regclass as table_name
            FROM pg_constraint 
            WHERE conrelid IN (
                SELECT oid FROM pg_class 
                WHERE relname IN ('workflows', 'workflow_node_contexts', 'workflow_standalone_docs', 'workflow_extraction_snapshots')
                AND relkind = 'r'
            )
            ORDER BY conrelid::regclass, conname;
            """
            
            result = session.execute(text(constraints_query))
            constraints = result.fetchall()
            
            for con in constraints:
                constraint_type = {
                    'p': 'PRIMARY KEY',
                    'f': 'FOREIGN KEY',
                    'c': 'CHECK',
                    'u': 'UNIQUE'
                }.get(con[1], con[1])
                print(f"   - {con[0]} ({constraint_type}) on {con[2]}")
            
            print(f"\n   Total constraints: {len(constraints)}")
            
            return True
            
    except Exception as e:
        print(f"❌ Schema check failed: {e}")
        return False


if __name__ == "__main__":
    check_schema()

