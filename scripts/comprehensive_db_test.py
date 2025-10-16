#!/usr/bin/env python3
"""
Comprehensive Database Operations Test
Tests all database operations: save, read, update, upsert, resume, schema validation.

Author: Dev1
Task: Comprehensive Database Testing
Date: October 16, 2025
"""

import asyncio
import sys
import json
import time
from datetime import datetime
sys.path.append('.')

from src.storage.database import get_session
from src.scrapers.unified_workflow_extractor import extract_workflow_unified
import sys
sys.path.append('../n8n-shared')
from n8n_shared.models import (
    Workflow, WorkflowMetadata, WorkflowStructure, WorkflowContent,
    WorkflowNodeContext, WorkflowStandaloneDoc, WorkflowExtractionSnapshot,
    VideoTranscript
)
from sqlalchemy import text, inspect
from sqlalchemy.exc import IntegrityError


class DatabaseTester:
    """Comprehensive database operations tester."""
    
    def __init__(self):
        self.test_workflow_id = "TEST_UNIFIED_001"
        self.test_url = "https://n8n.io/workflows/test-unified-workflow"
        self.results = {}
    
    def test_schema_validation(self):
        """Test database schema completeness and consistency."""
        print("🔍 Testing Database Schema...")
        
        with get_session() as session:
            inspector = inspect(session.bind)
            
            # Check all required tables exist
            required_tables = [
                'workflows', 'workflow_metadata', 'workflow_structure', 
                'workflow_content', 'workflow_node_contexts', 
                'workflow_standalone_docs', 'workflow_extraction_snapshots',
                'video_transcripts'
            ]
            
            existing_tables = inspector.get_table_names()
            missing_tables = [t for t in required_tables if t not in existing_tables]
            
            if missing_tables:
                print(f"   ❌ Missing tables: {missing_tables}")
                return False
            else:
                print(f"   ✅ All required tables exist")
            
            # Check table structures
            for table_name in required_tables:
                columns = inspector.get_columns(table_name)
                print(f"   📋 {table_name}: {len(columns)} columns")
                
                # Check for critical columns
                column_names = [col['name'] for col in columns]
                if table_name == 'workflows':
                    critical_cols = ['workflow_id', 'url', 'quality_score', 'layer2_success', 'layer3_success']
                elif table_name == 'workflow_node_contexts':
                    critical_cols = ['workflow_id', 'node_name', 'node_type', 'sticky_content']
                elif table_name == 'workflow_standalone_docs':
                    critical_cols = ['workflow_id', 'doc_type', 'doc_content']
                else:
                    critical_cols = ['workflow_id']
                
                missing_cols = [col for col in critical_cols if col not in column_names]
                if missing_cols:
                    print(f"      ❌ Missing columns: {missing_cols}")
                else:
                    print(f"      ✅ Critical columns present")
            
            return True
    
    def test_basic_crud_operations(self):
        """Test basic CRUD operations."""
        print("\n🔧 Testing Basic CRUD Operations...")
        
        with get_session() as session:
            try:
                # CREATE - Insert test workflow
                test_workflow = Workflow(
                    workflow_id=self.test_workflow_id,
                    url=self.test_url,
                    quality_score=0.95,
                    layer2_success=True,
                    layer3_success=True,
                    layer2_extracted_at=datetime.utcnow(),
                    layer3_extracted_at=datetime.utcnow()
                )
                session.add(test_workflow)
                session.commit()
                print("   ✅ CREATE: Workflow inserted successfully")
                
                # READ - Query workflow
                workflow = session.query(Workflow).filter_by(workflow_id=self.test_workflow_id).first()
                if workflow:
                    print(f"   ✅ READ: Workflow found - Quality: {workflow.quality_score}")
                else:
                    print("   ❌ READ: Workflow not found")
                    return False
                
                # UPDATE - Update workflow
                workflow.quality_score = 0.98
                workflow.updated_at = datetime.utcnow()
                session.commit()
                print("   ✅ UPDATE: Workflow updated successfully")
                
                # Verify update
                updated_workflow = session.query(Workflow).filter_by(workflow_id=self.test_workflow_id).first()
                if updated_workflow.quality_score == 0.98:
                    print("   ✅ UPDATE VERIFICATION: Quality score updated correctly")
                else:
                    print("   ❌ UPDATE VERIFICATION: Quality score not updated")
                    return False
                
                return True
                
            except Exception as e:
                print(f"   ❌ CRUD Error: {e}")
                session.rollback()
                return False
    
    def test_enhanced_tables_operations(self):
        """Test operations on enhanced tables."""
        print("\n🔧 Testing Enhanced Tables Operations...")
        
        with get_session() as session:
            try:
                # Test WorkflowNodeContext
                node_context = WorkflowNodeContext(
                    workflow_id=self.test_workflow_id,
                    node_name="Test Node",
                    node_type="n8n-nodes-base.set",
                    node_position={"x": 100, "y": 200},
                    sticky_title="Test Sticky",
                    sticky_content="This is a test sticky note content",
                    sticky_markdown="## Test Sticky\n\nThis is a test sticky note content",
                    match_confidence=0.95,
                    extraction_method="proximity"
                )
                session.add(node_context)
                
                # Test WorkflowStandaloneDoc
                standalone_doc = WorkflowStandaloneDoc(
                    workflow_id=self.test_workflow_id,
                    doc_type="setup_instructions",
                    doc_title="Test Setup Instructions",
                    doc_content="These are test setup instructions",
                    doc_markdown="## Test Setup Instructions\n\nThese are test setup instructions",
                    doc_position={"x": 50, "y": 150},
                    confidence_score=0.90
                )
                session.add(standalone_doc)
                
                # Test WorkflowExtractionSnapshot
                snapshot = WorkflowExtractionSnapshot(
                    workflow_id=self.test_workflow_id,
                    layer="UNIFIED",
                    payload={"test": "data", "nodes": 5, "videos": 1}
                )
                session.add(snapshot)
                
                session.commit()
                print("   ✅ Enhanced tables: All records inserted successfully")
                
                # Verify reads
                node_contexts = session.query(WorkflowNodeContext).filter_by(workflow_id=self.test_workflow_id).all()
                standalone_docs = session.query(WorkflowStandaloneDoc).filter_by(workflow_id=self.test_workflow_id).all()
                snapshots = session.query(WorkflowExtractionSnapshot).filter_by(workflow_id=self.test_workflow_id).all()
                
                print(f"   ✅ READ VERIFICATION: {len(node_contexts)} node contexts, {len(standalone_docs)} standalone docs, {len(snapshots)} snapshots")
                
                return True
                
            except Exception as e:
                print(f"   ❌ Enhanced Tables Error: {e}")
                session.rollback()
                return False
    
    def test_upsert_operations(self):
        """Test upsert operations."""
        print("\n🔧 Testing Upsert Operations...")
        
        with get_session() as session:
            try:
                # Test workflow upsert
                upsert_sql = text("""
                    INSERT INTO workflows (workflow_id, url, quality_score, layer2_success, layer3_success, extracted_at, updated_at)
                    VALUES (:workflow_id, :url, :quality_score, :layer2_success, :layer3_success, :extracted_at, :updated_at)
                    ON CONFLICT (workflow_id) 
                    DO UPDATE SET 
                        quality_score = EXCLUDED.quality_score,
                        layer2_success = EXCLUDED.layer2_success,
                        layer3_success = EXCLUDED.layer3_success,
                        updated_at = EXCLUDED.updated_at
                """)
                
                session.execute(upsert_sql, {
                    'workflow_id': self.test_workflow_id,
                    'url': self.test_url,
                    'quality_score': 0.99,
                    'layer2_success': True,
                    'layer3_success': True,
                    'extracted_at': datetime.utcnow(),
                    'updated_at': datetime.utcnow()
                })
                session.commit()
                print("   ✅ UPSERT: Workflow upserted successfully")
                
                # Verify upsert
                workflow = session.query(Workflow).filter_by(workflow_id=self.test_workflow_id).first()
                if workflow.quality_score == 0.99:
                    print("   ✅ UPSERT VERIFICATION: Quality score updated via upsert")
                else:
                    print("   ❌ UPSERT VERIFICATION: Quality score not updated")
                    return False
                
                return True
                
            except Exception as e:
                print(f"   ❌ Upsert Error: {e}")
                session.rollback()
                return False
    
    def test_resume_operations(self):
        """Test resume operations (checking existing data)."""
        print("\n🔧 Testing Resume Operations...")
        
        with get_session() as session:
            try:
                # Check if workflow exists
                existing_workflow = session.query(Workflow).filter_by(workflow_id=self.test_workflow_id).first()
                if existing_workflow:
                    print(f"   ✅ RESUME: Workflow exists - Quality: {existing_workflow.quality_score}")
                    
                    # Check layer completion status
                    layer2_complete = existing_workflow.layer2_success
                    layer3_complete = existing_workflow.layer3_success
                    print(f"   📊 Layer Status - L2: {layer2_complete}, L3: {layer3_complete}")
                    
                    # Check related data
                    node_contexts = session.query(WorkflowNodeContext).filter_by(workflow_id=self.test_workflow_id).count()
                    standalone_docs = session.query(WorkflowStandaloneDoc).filter_by(workflow_id=self.test_workflow_id).count()
                    snapshots = session.query(WorkflowExtractionSnapshot).filter_by(workflow_id=self.test_workflow_id).count()
                    
                    print(f"   📊 Related Data - Node Contexts: {node_contexts}, Standalone Docs: {standalone_docs}, Snapshots: {snapshots}")
                    
                    return True
                else:
                    print("   ❌ RESUME: Workflow not found")
                    return False
                    
            except Exception as e:
                print(f"   ❌ Resume Error: {e}")
                return False
    
    def test_unified_scraper_integration(self):
        """Test unified scraper integration with database."""
        print("\n🔧 Testing Unified Scraper Integration...")
        
        try:
            # Test with a real workflow (8237)
            result = asyncio.run(extract_workflow_unified(
                workflow_id="8237",
                workflow_url="https://n8n.io/workflows/8237-personal-life-manager-with-telegram-google-services-and-voice-enabled-ai",
                headless=True,
                save_to_db=True
            ))
            
            if result['success']:
                print("   ✅ UNIFIED SCRAPER: Extraction successful")
                
                # Verify data was saved
                with get_session() as session:
                    workflow = session.query(Workflow).filter_by(workflow_id="8237").first()
                    if workflow and workflow.layer2_success and workflow.layer3_success:
                        print("   ✅ DATABASE INTEGRATION: Workflow marked as L2+L3 complete")
                        
                        # Check node contexts
                        node_contexts = session.query(WorkflowNodeContext).filter_by(workflow_id="8237").count()
                        standalone_docs = session.query(WorkflowStandaloneDoc).filter_by(workflow_id="8237").count()
                        snapshots = session.query(WorkflowExtractionSnapshot).filter_by(workflow_id="8237").count()
                        
                        print(f"   📊 SAVED DATA - Node Contexts: {node_contexts}, Standalone Docs: {standalone_docs}, Snapshots: {snapshots}")
                        
                        return True
                    else:
                        print("   ❌ DATABASE INTEGRATION: Workflow not properly marked as complete")
                        return False
            else:
                print(f"   ❌ UNIFIED SCRAPER: Extraction failed - {result.get('error', 'Unknown error')}")
                return False
                
        except Exception as e:
            print(f"   ❌ Integration Error: {e}")
            return False
    
    def cleanup_test_data(self):
        """Clean up test data."""
        print("\n🧹 Cleaning up test data...")
        
        with get_session() as session:
            try:
                # Delete test workflow and all related data (manual cascade)
                session.execute(text("DELETE FROM workflow_node_contexts WHERE workflow_id = :workflow_id"), 
                              {'workflow_id': self.test_workflow_id})
                session.execute(text("DELETE FROM workflow_standalone_docs WHERE workflow_id = :workflow_id"), 
                              {'workflow_id': self.test_workflow_id})
                session.execute(text("DELETE FROM workflow_extraction_snapshots WHERE workflow_id = :workflow_id"), 
                              {'workflow_id': self.test_workflow_id})
                session.execute(text("DELETE FROM workflows WHERE workflow_id = :workflow_id"), 
                              {'workflow_id': self.test_workflow_id})
                session.commit()
                print("   ✅ Cleanup: Test data removed")
                return True
            except Exception as e:
                print(f"   ❌ Cleanup Error: {e}")
                session.rollback()
                return False
    
    def run_comprehensive_test(self):
        """Run all database tests."""
        print("🚀 Starting Comprehensive Database Test")
        print("=" * 60)
        
        tests = [
            ("Schema Validation", self.test_schema_validation),
            ("Basic CRUD Operations", self.test_basic_crud_operations),
            ("Enhanced Tables Operations", self.test_enhanced_tables_operations),
            ("Upsert Operations", self.test_upsert_operations),
            ("Resume Operations", self.test_resume_operations),
            ("Unified Scraper Integration", self.test_unified_scraper_integration),
            ("Cleanup", self.cleanup_test_data)
        ]
        
        results = {}
        for test_name, test_func in tests:
            try:
                result = test_func()
                results[test_name] = result
                status = "✅ PASS" if result else "❌ FAIL"
                print(f"\n{status}: {test_name}")
            except Exception as e:
                results[test_name] = False
                print(f"\n❌ FAIL: {test_name} - Exception: {e}")
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 COMPREHENSIVE TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for result in results.values() if result)
        total = len(results)
        
        for test_name, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status}: {test_name}")
        
        print(f"\n🎯 Overall Result: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
        
        if passed == total:
            print("🏆 ALL TESTS PASSED - Database is production ready!")
        else:
            print("⚠️  Some tests failed - Review issues before production")
        
        return results


if __name__ == "__main__":
    tester = DatabaseTester()
    results = tester.run_comprehensive_test()
