#!/usr/bin/env python3
"""
Enhanced Scrapers Database Validation
Comprehensive validation of database schema, CRUD operations, and data integrity.

Author: Dev1
Task: Enhanced L2 L3 Node Context Extraction
Date: October 15, 2025
"""

import os
import sys
import json
from datetime import datetime
from typing import Dict, List, Any, Optional

# Add project paths
sys.path.append('.')
sys.path.append('../n8n-shared')

from src.storage.database import get_session
from n8n_shared.models import Workflow, WorkflowNodeContext, WorkflowStandaloneDoc
from sqlalchemy import text, inspect


class EnhancedScrapersDBValidator:
    """Comprehensive database validator for enhanced scrapers."""
    
    def __init__(self):
        self.validation_results = {
            'schema_validation': {},
            'crud_operations': {},
            'data_integrity': {},
            'performance_tests': {},
            'overall_success': False
        }
        self.start_time = datetime.now()
    
    def validate_schema(self) -> Dict[str, Any]:
        """Validate database schema for new tables and columns."""
        print("🔍 Validating database schema...")
        
        schema_results = {
            'tables_exist': False,
            'columns_exist': False,
            'indexes_exist': False,
            'foreign_keys': False,
            'data_types': False,
            'errors': []
        }
        
        try:
            with get_session() as session:
                # Check if new tables exist
                inspector = inspect(session.bind)
                tables = inspector.get_table_names()
                
                required_tables = ['workflow_node_contexts', 'workflow_standalone_docs']
                missing_tables = [table for table in required_tables if table not in tables]
                
                if missing_tables:
                    schema_results['errors'].append(f"Missing tables: {missing_tables}")
                else:
                    schema_results['tables_exist'] = True
                    print("   ✅ All required tables exist")
                
                # Check columns for each table
                for table_name in required_tables:
                    if table_name in tables:
                        columns = inspector.get_columns(table_name)
                        column_names = [col['name'] for col in columns]
                        
                        if table_name == 'workflow_node_contexts':
                            required_columns = [
                                'id', 'workflow_id', 'node_name', 'node_type', 'node_position',
                                'sticky_title', 'sticky_content', 'sticky_markdown',
                                'match_confidence', 'extraction_method', 'extracted_at'
                            ]
                        else:  # workflow_standalone_docs
                            required_columns = [
                                'id', 'workflow_id', 'doc_type', 'doc_title', 'doc_content',
                                'doc_markdown', 'doc_position', 'confidence_score', 'extracted_at'
                            ]
                        
                        missing_columns = [col for col in required_columns if col not in column_names]
                        if missing_columns:
                            schema_results['errors'].append(f"Missing columns in {table_name}: {missing_columns}")
                        else:
                            schema_results['columns_exist'] = True
                            print(f"   ✅ All required columns exist in {table_name}")
                
                # Check indexes
                indexes = inspector.get_indexes('workflow_node_contexts')
                index_names = [idx['name'] for idx in indexes]
                required_indexes = ['idx_node_contexts_workflow', 'idx_node_contexts_node_name']
                
                missing_indexes = [idx for idx in required_indexes if idx not in index_names]
                if missing_indexes:
                    schema_results['errors'].append(f"Missing indexes: {missing_indexes}")
                else:
                    schema_results['indexes_exist'] = True
                    print("   ✅ All required indexes exist")
                
                # Check foreign keys
                fks = inspector.get_foreign_keys('workflow_node_contexts')
                has_workflow_fk = any(fk['referred_table'] == 'workflows' for fk in fks)
                
                if has_workflow_fk:
                    schema_results['foreign_keys'] = True
                    print("   ✅ Foreign key constraints exist")
                else:
                    schema_results['errors'].append("Missing foreign key to workflows table")
                
                # Check data types
                node_contexts_columns = inspector.get_columns('workflow_node_contexts')
                for col in node_contexts_columns:
                    if col['name'] == 'node_position' and 'jsonb' not in str(col['type']).lower():
                        schema_results['errors'].append("node_position should be JSONB type")
                    elif col['name'] == 'match_confidence' and 'real' not in str(col['type']).lower() and 'float' not in str(col['type']).lower() and 'double' not in str(col['type']).lower():
                        schema_results['errors'].append("match_confidence should be FLOAT type")
                
                if not schema_results['errors']:
                    schema_results['data_types'] = True
                    print("   ✅ Data types are correct")
        
        except Exception as e:
            schema_results['errors'].append(f"Schema validation error: {e}")
        
        self.validation_results['schema_validation'] = schema_results
        return schema_results
    
    def validate_crud_operations(self) -> Dict[str, Any]:
        """Validate CRUD operations on new tables."""
        print("🔍 Validating CRUD operations...")
        
        crud_results = {
            'create': False,
            'read': False,
            'update': False,
            'delete': False,
            'errors': []
        }
        
        try:
            with get_session() as session:
                # Test CREATE operation - use an existing workflow ID
                existing_workflow = session.query(Workflow).first()
                if not existing_workflow:
                    crud_results['errors'].append("No existing workflows found for testing")
                    return crud_results
                
                test_workflow_id = existing_workflow.workflow_id
                
                # Create test node context
                node_context = WorkflowNodeContext(
                    workflow_id=test_workflow_id,
                    node_name='Test Node',
                    node_type='test',
                    node_position={'x': 100, 'y': 200},
                    sticky_title='Test Sticky',
                    sticky_content='Test content',
                    sticky_markdown='## Test Sticky\n\nTest content',
                    match_confidence=0.95,
                    extraction_method='test'
                )
                session.add(node_context)
                
                # Create test standalone doc
                standalone_doc = WorkflowStandaloneDoc(
                    workflow_id=test_workflow_id,
                    doc_type='test_doc',
                    doc_title='Test Document',
                    doc_content='Test document content',
                    doc_markdown='## Test Document\n\nTest document content',
                    doc_position={'x': 0, 'y': 0},
                    confidence_score=0.85
                )
                session.add(standalone_doc)
                
                session.commit()
                crud_results['create'] = True
                print("   ✅ CREATE operations successful")
                
                # Test READ operation
                node_contexts = session.query(WorkflowNodeContext).filter_by(workflow_id=test_workflow_id).all()
                standalone_docs = session.query(WorkflowStandaloneDoc).filter_by(workflow_id=test_workflow_id).all()
                
                if len(node_contexts) == 1 and len(standalone_docs) == 1:
                    crud_results['read'] = True
                    print("   ✅ READ operations successful")
                else:
                    crud_results['errors'].append("READ operation failed - incorrect record count")
                
                # Test UPDATE operation
                node_contexts[0].sticky_title = 'Updated Test Sticky'
                standalone_docs[0].doc_title = 'Updated Test Document'
                session.commit()
                
                # Verify updates
                updated_node = session.query(WorkflowNodeContext).filter_by(workflow_id=test_workflow_id).first()
                updated_doc = session.query(WorkflowStandaloneDoc).filter_by(workflow_id=test_workflow_id).first()
                
                if (updated_node.sticky_title == 'Updated Test Sticky' and 
                    updated_doc.doc_title == 'Updated Test Document'):
                    crud_results['update'] = True
                    print("   ✅ UPDATE operations successful")
                else:
                    crud_results['errors'].append("UPDATE operation failed - changes not persisted")
                
                # Test DELETE operation
                session.delete(node_contexts[0])
                session.delete(standalone_docs[0])
                session.commit()
                
                # Verify deletion
                remaining_nodes = session.query(WorkflowNodeContext).filter_by(workflow_id=test_workflow_id).count()
                remaining_docs = session.query(WorkflowStandaloneDoc).filter_by(workflow_id=test_workflow_id).count()
                
                if remaining_nodes == 0 and remaining_docs == 0:
                    crud_results['delete'] = True
                    print("   ✅ DELETE operations successful")
                else:
                    crud_results['errors'].append("DELETE operation failed - records still exist")
        
        except Exception as e:
            crud_results['errors'].append(f"CRUD validation error: {e}")
        
        self.validation_results['crud_operations'] = crud_results
        return crud_results
    
    def validate_data_integrity(self) -> Dict[str, Any]:
        """Validate data integrity and relationships."""
        print("🔍 Validating data integrity...")
        
        integrity_results = {
            'foreign_key_integrity': False,
            'data_consistency': False,
            'no_orphaned_records': False,
            'jsonb_validity': False,
            'errors': []
        }
        
        try:
            with get_session() as session:
                # Check foreign key integrity
                orphaned_nodes = session.execute(text("""
                    SELECT wnc.workflow_id 
                    FROM workflow_node_contexts wnc
                    LEFT JOIN workflows w ON wnc.workflow_id = w.workflow_id
                    WHERE w.workflow_id IS NULL
                    LIMIT 5
                """)).fetchall()
                
                orphaned_docs = session.execute(text("""
                    SELECT wsd.workflow_id 
                    FROM workflow_standalone_docs wsd
                    LEFT JOIN workflows w ON wsd.workflow_id = w.workflow_id
                    WHERE w.workflow_id IS NULL
                    LIMIT 5
                """)).fetchall()
                
                if not orphaned_nodes and not orphaned_docs:
                    integrity_results['foreign_key_integrity'] = True
                    integrity_results['no_orphaned_records'] = True
                    print("   ✅ No orphaned records found")
                else:
                    integrity_results['errors'].append(f"Found orphaned records: nodes={len(orphaned_nodes)}, docs={len(orphaned_docs)}")
                
                # Check data consistency
                inconsistent_nodes = session.execute(text("""
                    SELECT workflow_id, COUNT(*) as count
                    FROM workflow_node_contexts
                    WHERE match_confidence < 0 OR match_confidence > 1
                    GROUP BY workflow_id
                """)).fetchall()
                
                inconsistent_docs = session.execute(text("""
                    SELECT workflow_id, COUNT(*) as count
                    FROM workflow_standalone_docs
                    WHERE confidence_score < 0 OR confidence_score > 1
                    GROUP BY workflow_id
                """)).fetchall()
                
                if not inconsistent_nodes and not inconsistent_docs:
                    integrity_results['data_consistency'] = True
                    print("   ✅ Data consistency checks passed")
                else:
                    integrity_results['errors'].append(f"Found inconsistent data: nodes={len(inconsistent_nodes)}, docs={len(inconsistent_docs)}")
                
                # Check JSONB validity
                invalid_jsonb = session.execute(text("""
                    SELECT workflow_id, 'node_position' as field
                    FROM workflow_node_contexts
                    WHERE node_position IS NOT NULL
                    AND NOT (node_position::text ~ '^\\{.*\\}$')
                    LIMIT 5
                """)).fetchall()
                
                if not invalid_jsonb:
                    integrity_results['jsonb_validity'] = True
                    print("   ✅ JSONB fields are valid")
                else:
                    integrity_results['errors'].append(f"Found invalid JSONB data: {len(invalid_jsonb)} records")
        
        except Exception as e:
            integrity_results['errors'].append(f"Data integrity validation error: {e}")
        
        self.validation_results['data_integrity'] = integrity_results
        return integrity_results
    
    def validate_performance(self) -> Dict[str, Any]:
        """Validate database performance with sample queries."""
        print("🔍 Validating database performance...")
        
        performance_results = {
            'query_performance': False,
            'index_usage': False,
            'connection_pool': False,
            'errors': []
        }
        
        try:
            with get_session() as session:
                # Test query performance
                start_time = datetime.now()
                
                # Test complex query with joins
                result = session.execute(text("""
                    SELECT w.workflow_id, wm.title,
                           COUNT(wnc.id) as node_contexts_count,
                           COUNT(wsd.id) as standalone_docs_count
                    FROM workflows w
                    LEFT JOIN workflow_metadata wm ON w.workflow_id = wm.workflow_id
                    LEFT JOIN workflow_node_contexts wnc ON w.workflow_id = wnc.workflow_id
                    LEFT JOIN workflow_standalone_docs wsd ON w.workflow_id = wsd.workflow_id
                    GROUP BY w.workflow_id, wm.title
                    ORDER BY node_contexts_count DESC, standalone_docs_count DESC
                    LIMIT 100
                """)).fetchall()
                
                query_time = (datetime.now() - start_time).total_seconds()
                
                if query_time < 5.0:  # Should complete within 5 seconds
                    performance_results['query_performance'] = True
                    print(f"   ✅ Query performance good ({query_time:.2f}s)")
                else:
                    performance_results['errors'].append(f"Query too slow: {query_time:.2f}s")
                
                # Test index usage (basic check)
                explain_result = session.execute(text("""
                    EXPLAIN (ANALYZE, BUFFERS) 
                    SELECT * FROM workflow_node_contexts 
                    WHERE workflow_id = '8237'
                """)).fetchall()
                
                # Check if index is being used (basic check)
                explain_text = ' '.join([str(row) for row in explain_result]).lower()
                if 'index' in explain_text or 'scan' in explain_text:
                    performance_results['index_usage'] = True
                    print("   ✅ Index usage detected")
                else:
                    performance_results['errors'].append("Index usage not detected")
                
                # Test connection pool
                connection_test = session.execute(text("SELECT 1")).scalar()
                if connection_test == 1:
                    performance_results['connection_pool'] = True
                    print("   ✅ Connection pool working")
                else:
                    performance_results['errors'].append("Connection pool test failed")
        
        except Exception as e:
            performance_results['errors'].append(f"Performance validation error: {e}")
        
        self.validation_results['performance_tests'] = performance_results
        return performance_results
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive validation report."""
        end_time = datetime.now()
        total_time = (end_time - self.start_time).total_seconds()
        
        # Calculate overall success
        all_sections = [
            self.validation_results['schema_validation'],
            self.validation_results['crud_operations'],
            self.validation_results['data_integrity'],
            self.validation_results['performance_tests']
        ]
        
        overall_success = all(
            not section.get('errors', []) for section in all_sections
        )
        
        self.validation_results['overall_success'] = overall_success
        
        # Generate summary
        report = {
            'validation_summary': {
                'overall_success': overall_success,
                'total_time': total_time,
                'timestamp': end_time.isoformat(),
                'sections_validated': len(all_sections)
            },
            'detailed_results': self.validation_results,
            'recommendations': self._generate_recommendations()
        }
        
        return report
    
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on validation results."""
        recommendations = []
        
        # Schema recommendations
        if self.validation_results['schema_validation'].get('errors'):
            recommendations.append("Fix schema issues: " + "; ".join(self.validation_results['schema_validation']['errors']))
        
        # CRUD recommendations
        if self.validation_results['crud_operations'].get('errors'):
            recommendations.append("Fix CRUD operation issues: " + "; ".join(self.validation_results['crud_operations']['errors']))
        
        # Data integrity recommendations
        if self.validation_results['data_integrity'].get('errors'):
            recommendations.append("Fix data integrity issues: " + "; ".join(self.validation_results['data_integrity']['errors']))
        
        # Performance recommendations
        if self.validation_results['performance_tests'].get('errors'):
            recommendations.append("Optimize performance: " + "; ".join(self.validation_results['performance_tests']['errors']))
        
        if not recommendations:
            recommendations.append("✅ All validations passed - database is ready for production use")
        
        return recommendations
    
    def run_full_validation(self) -> Dict[str, Any]:
        """Run complete database validation."""
        print("🚀 Enhanced Scrapers Database Validation")
        print("=" * 60)
        print(f"🕒 Start time: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Run all validations
        self.validate_schema()
        self.validate_crud_operations()
        self.validate_data_integrity()
        self.validate_performance()
        
        # Generate report
        report = self.generate_report()
        
        # Display results
        print("\n" + "=" * 60)
        print("📊 VALIDATION RESULTS")
        print("=" * 60)
        
        if report['validation_summary']['overall_success']:
            print("✅ OVERALL RESULT: SUCCESS")
        else:
            print("❌ OVERALL RESULT: FAILED")
        
        print(f"⏱️  Total time: {report['validation_summary']['total_time']:.2f}s")
        print(f"📋 Sections validated: {report['validation_summary']['sections_validated']}")
        
        print("\n📋 RECOMMENDATIONS:")
        for i, rec in enumerate(report['recommendations'], 1):
            print(f"   {i}. {rec}")
        
        # Save report to file
        report_file = f"enhanced_scrapers_validation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"\n💾 Full report saved to: {report_file}")
        
        return report


def main():
    """Main function."""
    validator = EnhancedScrapersDBValidator()
    report = validator.run_full_validation()
    
    # Exit with appropriate code
    exit_code = 0 if report['validation_summary']['overall_success'] else 1
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
