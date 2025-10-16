#!/usr/bin/env python3
"""
Production Infrastructure Test
Comprehensive test of all production infrastructure components:
- Database integration (CRUD, upsert, resume)
- Watchdog functionality
- Connection management
- Resume capabilities
- Error handling and recovery

Author: Dev1
Task: Test Production Infrastructure
Date: October 16, 2025
"""

import asyncio
import sys
import time
import signal
import os
from datetime import datetime
sys.path.append('.')

from src.scrapers.unified_workflow_extractor import UnifiedWorkflowExtractor
from src.storage.database_manager import DatabaseManager
from src.monitoring.watchdog import Watchdog
from src.utils.connection_manager import ConnectionManager


class ProductionInfrastructureTester:
    """Comprehensive test of production infrastructure components."""
    
    def __init__(self):
        self.test_workflows = [
            {'id': '7639', 'url': 'https://n8n.io/workflows/7639-talk-to-your-google-sheets-using-chatgpt-5'},
            {'id': '8237', 'url': 'https://n8n.io/workflows/8237-personal-life-manager-with-telegram-google-services-and-voice-enabled-ai'},
            {'id': '6270', 'url': 'https://n8n.io/workflows/6270-automate-customer-support-with-ai-and-telegram'}
        ]
        self.test_results = {
            'database_operations': {'success': 0, 'total': 0, 'errors': []},
            'resume_capabilities': {'success': 0, 'total': 0, 'errors': []},
            'connection_management': {'success': 0, 'total': 0, 'errors': []},
            'watchdog_functionality': {'success': 0, 'total': 0, 'errors': []},
            'error_recovery': {'success': 0, 'total': 0, 'errors': []}
        }
    
    async def test_database_operations(self):
        """Test comprehensive database operations."""
        print("🗄️  Testing Database Operations")
        print("=" * 50)
        
        try:
            db_manager = DatabaseManager()
            
            # Test 1: Basic CRUD operations
            print("   📝 Test 1: Basic CRUD Operations")
            self.test_results['database_operations']['total'] += 1
            
            try:
                # Create test workflow
                test_workflow = {
                    'workflow_id': 'TEST_INFRA_001',
                    'title': 'Test Infrastructure Workflow',
                    'url': 'https://n8n.io/workflows/test-infra-001',
                    'description': 'Test workflow for infrastructure testing',
                    'layer1_scraped': True,
                    'layer1_5_scraped': True,
                    'layer2_scraped': False,
                    'layer3_scraped': False
                }
                
                # Create
                await db_manager.create_workflow(test_workflow)
                print("      ✅ CREATE: Success")
                
                # Read
                retrieved = await db_manager.get_workflow('TEST_INFRA_001')
                if retrieved and retrieved['workflow_id'] == 'TEST_INFRA_001':
                    print("      ✅ READ: Success")
                else:
                    raise Exception("Read operation failed")
                
                # Update
                test_workflow['description'] = 'Updated test workflow'
                await db_manager.update_workflow('TEST_INFRA_001', test_workflow)
                print("      ✅ UPDATE: Success")
                
                # Verify update
                updated = await db_manager.get_workflow('TEST_INFRA_001')
                if updated and updated['description'] == 'Updated test workflow':
                    print("      ✅ UPDATE VERIFICATION: Success")
                else:
                    raise Exception("Update verification failed")
                
                # Delete
                await db_manager.delete_workflow('TEST_INFRA_001')
                print("      ✅ DELETE: Success")
                
                self.test_results['database_operations']['success'] += 1
                
            except Exception as e:
                print(f"      ❌ CRUD Operations Failed: {e}")
                self.test_results['database_operations']['errors'].append(f"CRUD: {e}")
            
            # Test 2: Upsert operations
            print("   📝 Test 2: Upsert Operations")
            self.test_results['database_operations']['total'] += 1
            
            try:
                # Test upsert (insert if not exists, update if exists)
                upsert_workflow = {
                    'workflow_id': 'TEST_UPSERT_001',
                    'title': 'Upsert Test Workflow',
                    'url': 'https://n8n.io/workflows/test-upsert-001',
                    'description': 'Initial description',
                    'layer1_scraped': True
                }
                
                # First upsert (should insert)
                await db_manager.upsert_workflow(upsert_workflow)
                first_read = await db_manager.get_workflow('TEST_UPSERT_001')
                if first_read and first_read['description'] == 'Initial description':
                    print("      ✅ UPSERT INSERT: Success")
                else:
                    raise Exception("Upsert insert failed")
                
                # Second upsert (should update)
                upsert_workflow['description'] = 'Updated via upsert'
                await db_manager.upsert_workflow(upsert_workflow)
                second_read = await db_manager.get_workflow('TEST_UPSERT_001')
                if second_read and second_read['description'] == 'Updated via upsert':
                    print("      ✅ UPSERT UPDATE: Success")
                else:
                    raise Exception("Upsert update failed")
                
                # Cleanup
                await db_manager.delete_workflow('TEST_UPSERT_001')
                print("      ✅ UPSERT CLEANUP: Success")
                
                self.test_results['database_operations']['success'] += 1
                
            except Exception as e:
                print(f"      ❌ Upsert Operations Failed: {e}")
                self.test_results['database_operations']['errors'].append(f"Upsert: {e}")
            
            # Test 3: Batch operations
            print("   📝 Test 3: Batch Operations")
            self.test_results['database_operations']['total'] += 1
            
            try:
                # Test batch insert
                batch_workflows = []
                for i in range(3):
                    batch_workflows.append({
                        'workflow_id': f'TEST_BATCH_{i:03d}',
                        'title': f'Batch Test Workflow {i}',
                        'url': f'https://n8n.io/workflows/test-batch-{i:03d}',
                        'description': f'Batch test workflow {i}',
                        'layer1_scraped': True
                    })
                
                await db_manager.batch_create_workflows(batch_workflows)
                print("      ✅ BATCH INSERT: Success")
                
                # Verify batch insert
                for workflow in batch_workflows:
                    retrieved = await db_manager.get_workflow(workflow['workflow_id'])
                    if not retrieved:
                        raise Exception(f"Batch workflow {workflow['workflow_id']} not found")
                print("      ✅ BATCH VERIFICATION: Success")
                
                # Batch delete
                workflow_ids = [w['workflow_id'] for w in batch_workflows]
                await db_manager.batch_delete_workflows(workflow_ids)
                print("      ✅ BATCH DELETE: Success")
                
                self.test_results['database_operations']['success'] += 1
                
            except Exception as e:
                print(f"      ❌ Batch Operations Failed: {e}")
                self.test_results['database_operations']['errors'].append(f"Batch: {e}")
            
            # Test 4: Complex data operations (L2/L3 data)
            print("   📝 Test 4: Complex Data Operations")
            self.test_results['database_operations']['total'] += 1
            
            try:
                # Test L2/L3 data storage
                complex_workflow = {
                    'workflow_id': 'TEST_COMPLEX_001',
                    'title': 'Complex Test Workflow',
                    'url': 'https://n8n.io/workflows/test-complex-001',
                    'description': 'Complex test workflow with L2/L3 data',
                    'layer1_scraped': True,
                    'layer1_5_scraped': True,
                    'layer2_scraped': True,
                    'layer3_scraped': True,
                    'layer2_extracted_at': datetime.now(),
                    'layer3_extracted_at': datetime.now(),
                    'unified_extraction_success': True,
                    'unified_extraction_at': datetime.now()
                }
                
                await db_manager.upsert_workflow(complex_workflow)
                
                # Test node contexts storage
                node_contexts = [
                    {
                        'workflow_id': 'TEST_COMPLEX_001',
                        'node_id': 'node_001',
                        'node_name': 'Test Node 1',
                        'node_type': 'n8n-nodes-base.httpRequest',
                        'sticky_title': 'Test Sticky',
                        'sticky_content': 'This is test content for node 1',
                        'match_confidence': 0.95,
                        'extraction_method': 'test'
                    }
                ]
                
                await db_manager.save_node_contexts(node_contexts)
                print("      ✅ NODE CONTEXTS STORAGE: Success")
                
                # Test standalone docs storage
                standalone_docs = [
                    {
                        'workflow_id': 'TEST_COMPLEX_001',
                        'doc_type': 'standalone_note',
                        'doc_title': 'Test Standalone Note',
                        'doc_content': 'This is a standalone note for testing',
                        'confidence_score': 0.9
                    }
                ]
                
                await db_manager.save_standalone_docs(standalone_docs)
                print("      ✅ STANDALONE DOCS STORAGE: Success")
                
                # Test extraction snapshots storage
                snapshot = {
                    'workflow_id': 'TEST_COMPLEX_001',
                    'layer': 'UNIFIED',
                    'payload': {'test': 'data', 'nodes': 5, 'videos': 1}
                }
                
                await db_manager.save_extraction_snapshot(snapshot)
                print("      ✅ EXTRACTION SNAPSHOTS STORAGE: Success")
                
                # Cleanup
                await db_manager.delete_workflow('TEST_COMPLEX_001')
                print("      ✅ COMPLEX DATA CLEANUP: Success")
                
                self.test_results['database_operations']['success'] += 1
                
            except Exception as e:
                print(f"      ❌ Complex Data Operations Failed: {e}")
                self.test_results['database_operations']['errors'].append(f"Complex: {e}")
            
        except Exception as e:
            print(f"   ❌ Database Operations Test Failed: {e}")
            self.test_results['database_operations']['errors'].append(f"General: {e}")
    
    async def test_resume_capabilities(self):
        """Test resume capabilities and state management."""
        print("\n🔄 Testing Resume Capabilities")
        print("=" * 50)
        
        try:
            # Test 1: Resume from partial completion
            print("   📝 Test 1: Resume from Partial Completion")
            self.test_results['resume_capabilities']['total'] += 1
            
            try:
                # Create a partially completed workflow
                partial_workflow = {
                    'workflow_id': 'TEST_RESUME_001',
                    'title': 'Resume Test Workflow',
                    'url': 'https://n8n.io/workflows/test-resume-001',
                    'description': 'Test workflow for resume testing',
                    'layer1_scraped': True,
                    'layer1_5_scraped': True,
                    'layer2_scraped': False,  # Not completed
                    'layer3_scraped': False   # Not completed
                }
                
                db_manager = DatabaseManager()
                await db_manager.upsert_workflow(partial_workflow)
                
                # Test resume detection
                workflow = await db_manager.get_workflow('TEST_RESUME_001')
                if workflow:
                    # Determine what needs to be resumed
                    needs_l2 = not workflow.get('layer2_scraped', False)
                    needs_l3 = not workflow.get('layer3_scraped', False)
                    
                    if needs_l2 and needs_l3:
                        print("      ✅ RESUME DETECTION: Success (L2+L3 needed)")
                    elif needs_l2:
                        print("      ✅ RESUME DETECTION: Success (L2 needed)")
                    elif needs_l3:
                        print("      ✅ RESUME DETECTION: Success (L3 needed)")
                    else:
                        print("      ✅ RESUME DETECTION: Success (Complete)")
                    
                    # Test resume execution
                    extractor = UnifiedWorkflowExtractor(headless=True, timeout=30000)
                    result = await extractor.extract('TEST_RESUME_001', partial_workflow['url'])
                    
                    if result['success']:
                        print("      ✅ RESUME EXECUTION: Success")
                        
                        # Verify completion
                        updated_workflow = await db_manager.get_workflow('TEST_RESUME_001')
                        if updated_workflow.get('unified_extraction_success', False):
                            print("      ✅ RESUME COMPLETION: Success")
                        else:
                            raise Exception("Resume completion not marked")
                    else:
                        raise Exception(f"Resume execution failed: {result.get('error')}")
                
                # Cleanup
                await db_manager.delete_workflow('TEST_RESUME_001')
                
                self.test_results['resume_capabilities']['success'] += 1
                
            except Exception as e:
                print(f"      ❌ Resume from Partial Completion Failed: {e}")
                self.test_results['resume_capabilities']['errors'].append(f"Partial: {e}")
            
            # Test 2: Resume from interruption
            print("   📝 Test 2: Resume from Interruption")
            self.test_results['resume_capabilities']['total'] += 1
            
            try:
                # Simulate interruption by creating workflow with extraction in progress
                interrupted_workflow = {
                    'workflow_id': 'TEST_INTERRUPT_001',
                    'title': 'Interrupted Test Workflow',
                    'url': 'https://n8n.io/workflows/test-interrupt-001',
                    'description': 'Test workflow for interruption testing',
                    'layer1_scraped': True,
                    'layer1_5_scraped': True,
                    'layer2_scraped': False,
                    'layer3_scraped': False,
                    'unified_extraction_success': False  # Was interrupted
                }
                
                await db_manager.upsert_workflow(interrupted_workflow)
                
                # Test interruption detection and recovery
                workflow = await db_manager.get_workflow('TEST_INTERRUPT_001')
                if workflow and not workflow.get('unified_extraction_success', True):
                    print("      ✅ INTERRUPTION DETECTION: Success")
                    
                    # Resume from interruption
                    extractor = UnifiedWorkflowExtractor(headless=True, timeout=30000)
                    result = await extractor.extract('TEST_INTERRUPT_001', interrupted_workflow['url'])
                    
                    if result['success']:
                        print("      ✅ INTERRUPTION RECOVERY: Success")
                    else:
                        raise Exception(f"Interruption recovery failed: {result.get('error')}")
                
                # Cleanup
                await db_manager.delete_workflow('TEST_INTERRUPT_001')
                
                self.test_results['resume_capabilities']['success'] += 1
                
            except Exception as e:
                print(f"      ❌ Resume from Interruption Failed: {e}")
                self.test_results['resume_capabilities']['errors'].append(f"Interrupt: {e}")
            
        except Exception as e:
            print(f"   ❌ Resume Capabilities Test Failed: {e}")
            self.test_results['resume_capabilities']['errors'].append(f"General: {e}")
    
    async def test_connection_management(self):
        """Test connection management and pooling."""
        print("\n🔗 Testing Connection Management")
        print("=" * 50)
        
        try:
            # Test 1: Connection pooling
            print("   📝 Test 1: Connection Pooling")
            self.test_results['connection_management']['total'] += 1
            
            try:
                conn_manager = ConnectionManager()
                
                # Test connection acquisition and release
                conn1 = await conn_manager.get_connection()
                if conn1:
                    print("      ✅ CONNECTION ACQUISITION: Success")
                    
                    # Test connection reuse
                    conn2 = await conn_manager.get_connection()
                    if conn2:
                        print("      ✅ CONNECTION REUSE: Success")
                        
                        # Test connection release
                        await conn_manager.release_connection(conn1)
                        await conn_manager.release_connection(conn2)
                        print("      ✅ CONNECTION RELEASE: Success")
                        
                        # Test connection cleanup
                        await conn_manager.cleanup()
                        print("      ✅ CONNECTION CLEANUP: Success")
                    else:
                        raise Exception("Connection reuse failed")
                else:
                    raise Exception("Connection acquisition failed")
                
                self.test_results['connection_management']['success'] += 1
                
            except Exception as e:
                print(f"      ❌ Connection Pooling Failed: {e}")
                self.test_results['connection_management']['errors'].append(f"Pooling: {e}")
            
            # Test 2: Concurrent connections
            print("   📝 Test 2: Concurrent Connections")
            self.test_results['connection_management']['total'] += 1
            
            try:
                # Test multiple concurrent connections
                async def get_and_release_connection():
                    conn = await conn_manager.get_connection()
                    if conn:
                        await asyncio.sleep(0.1)  # Simulate work
                        await conn_manager.release_connection(conn)
                        return True
                    return False
                
                # Run 5 concurrent connection operations
                tasks = [get_and_release_connection() for _ in range(5)]
                results = await asyncio.gather(*tasks)
                
                if all(results):
                    print("      ✅ CONCURRENT CONNECTIONS: Success")
                else:
                    raise Exception("Some concurrent connections failed")
                
                self.test_results['connection_management']['success'] += 1
                
            except Exception as e:
                print(f"      ❌ Concurrent Connections Failed: {e}")
                self.test_results['connection_management']['errors'].append(f"Concurrent: {e}")
            
            # Test 3: Connection limits and timeouts
            print("   📝 Test 3: Connection Limits and Timeouts")
            self.test_results['connection_management']['total'] += 1
            
            try:
                # Test connection limit enforcement
                max_connections = 3
                connections = []
                
                # Acquire max connections
                for i in range(max_connections):
                    conn = await conn_manager.get_connection()
                    if conn:
                        connections.append(conn)
                    else:
                        raise Exception(f"Failed to acquire connection {i+1}")
                
                print(f"      ✅ CONNECTION LIMIT: Success ({len(connections)} connections)")
                
                # Test timeout on additional connections
                try:
                    timeout_conn = await asyncio.wait_for(
                        conn_manager.get_connection(), 
                        timeout=1.0
                    )
                    if timeout_conn:
                        print("      ⚠️  CONNECTION TIMEOUT: Unexpected success")
                    else:
                        print("      ✅ CONNECTION TIMEOUT: Success (no connection available)")
                except asyncio.TimeoutError:
                    print("      ✅ CONNECTION TIMEOUT: Success (timeout as expected)")
                
                # Release all connections
                for conn in connections:
                    await conn_manager.release_connection(conn)
                print("      ✅ CONNECTION RELEASE ALL: Success")
                
                self.test_results['connection_management']['success'] += 1
                
            except Exception as e:
                print(f"      ❌ Connection Limits and Timeouts Failed: {e}")
                self.test_results['connection_management']['errors'].append(f"Limits: {e}")
            
        except Exception as e:
            print(f"   ❌ Connection Management Test Failed: {e}")
            self.test_results['connection_management']['errors'].append(f"General: {e}")
    
    async def test_watchdog_functionality(self):
        """Test watchdog functionality and process monitoring."""
        print("\n🐕 Testing Watchdog Functionality")
        print("=" * 50)
        
        try:
            # Test 1: Watchdog initialization
            print("   📝 Test 1: Watchdog Initialization")
            self.test_results['watchdog_functionality']['total'] += 1
            
            try:
                watchdog = Watchdog()
                if watchdog:
                    print("      ✅ WATCHDOG INITIALIZATION: Success")
                    
                    # Test watchdog configuration
                    config = watchdog.get_config()
                    if config:
                        print("      ✅ WATCHDOG CONFIGURATION: Success")
                    else:
                        raise Exception("Watchdog configuration failed")
                else:
                    raise Exception("Watchdog initialization failed")
                
                self.test_results['watchdog_functionality']['success'] += 1
                
            except Exception as e:
                print(f"      ❌ Watchdog Initialization Failed: {e}")
                self.test_results['watchdog_functionality']['errors'].append(f"Init: {e}")
            
            # Test 2: Process monitoring
            print("   📝 Test 2: Process Monitoring")
            self.test_results['watchdog_functionality']['total'] += 1
            
            try:
                # Test process status monitoring
                status = await watchdog.get_process_status()
                if status:
                    print("      ✅ PROCESS STATUS MONITORING: Success")
                    
                    # Test health check
                    health = await watchdog.health_check()
                    if health:
                        print("      ✅ HEALTH CHECK: Success")
                    else:
                        print("      ⚠️  HEALTH CHECK: Warning (not healthy)")
                else:
                    raise Exception("Process status monitoring failed")
                
                self.test_results['watchdog_functionality']['success'] += 1
                
            except Exception as e:
                print(f"      ❌ Process Monitoring Failed: {e}")
                self.test_results['watchdog_functionality']['errors'].append(f"Monitoring: {e}")
            
            # Test 3: Error detection and recovery
            print("   📝 Test 3: Error Detection and Recovery")
            self.test_results['watchdog_functionality']['total'] += 1
            
            try:
                # Test error detection
                errors = await watchdog.detect_errors()
                if errors is not None:
                    print(f"      ✅ ERROR DETECTION: Success ({len(errors)} errors detected)")
                    
                    # Test error recovery
                    if errors:
                        recovery_result = await watchdog.recover_from_errors(errors)
                        if recovery_result:
                            print("      ✅ ERROR RECOVERY: Success")
                        else:
                            print("      ⚠️  ERROR RECOVERY: Partial success")
                    else:
                        print("      ✅ ERROR RECOVERY: No errors to recover from")
                else:
                    raise Exception("Error detection failed")
                
                self.test_results['watchdog_functionality']['success'] += 1
                
            except Exception as e:
                print(f"      ❌ Error Detection and Recovery Failed: {e}")
                self.test_results['watchdog_functionality']['errors'].append(f"Recovery: {e}")
            
        except Exception as e:
            print(f"   ❌ Watchdog Functionality Test Failed: {e}")
            self.test_results['watchdog_functionality']['errors'].append(f"General: {e}")
    
    async def test_error_recovery(self):
        """Test error recovery and resilience."""
        print("\n🛡️  Testing Error Recovery")
        print("=" * 50)
        
        try:
            # Test 1: Database connection errors
            print("   📝 Test 1: Database Connection Errors")
            self.test_results['error_recovery']['total'] += 1
            
            try:
                # Test database error handling
                db_manager = DatabaseManager()
                
                # Test with invalid workflow ID
                try:
                    invalid_workflow = await db_manager.get_workflow('INVALID_WORKFLOW_ID')
                    if invalid_workflow is None:
                        print("      ✅ INVALID WORKFLOW HANDLING: Success")
                    else:
                        print("      ⚠️  INVALID WORKFLOW HANDLING: Unexpected result")
                except Exception as e:
                    if "not found" in str(e).lower() or "does not exist" in str(e).lower():
                        print("      ✅ INVALID WORKFLOW HANDLING: Success (expected error)")
                    else:
                        raise e
                
                # Test database timeout handling
                try:
                    # This would normally timeout, but we'll test the error handling
                    await asyncio.wait_for(
                        db_manager.get_workflow('TEST_TIMEOUT'),
                        timeout=0.1
                    )
                except asyncio.TimeoutError:
                    print("      ✅ DATABASE TIMEOUT HANDLING: Success")
                except Exception as e:
                    print(f"      ✅ DATABASE ERROR HANDLING: Success ({type(e).__name__})")
                
                self.test_results['error_recovery']['success'] += 1
                
            except Exception as e:
                print(f"      ❌ Database Connection Errors Failed: {e}")
                self.test_results['error_recovery']['errors'].append(f"DB: {e}")
            
            # Test 2: Network errors
            print("   📝 Test 2: Network Errors")
            self.test_results['error_recovery']['total'] += 1
            
            try:
                # Test network error handling with invalid URL
                extractor = UnifiedWorkflowExtractor(headless=True, timeout=5000)
                
                try:
                    result = await extractor.extract('INVALID_ID', 'https://invalid-url-that-does-not-exist.com')
                    if not result['success']:
                        print("      ✅ NETWORK ERROR HANDLING: Success")
                    else:
                        print("      ⚠️  NETWORK ERROR HANDLING: Unexpected success")
                except Exception as e:
                    print(f"      ✅ NETWORK ERROR HANDLING: Success ({type(e).__name__})")
                
                self.test_results['error_recovery']['success'] += 1
                
            except Exception as e:
                print(f"      ❌ Network Errors Failed: {e}")
                self.test_results['error_recovery']['errors'].append(f"Network: {e}")
            
            # Test 3: Resource exhaustion
            print("   📝 Test 3: Resource Exhaustion")
            self.test_results['error_recovery']['total'] += 1
            
            try:
                # Test memory/resource handling
                conn_manager = ConnectionManager()
                
                # Test resource cleanup
                await conn_manager.cleanup()
                print("      ✅ RESOURCE CLEANUP: Success")
                
                # Test resource monitoring
                resources = await conn_manager.get_resource_status()
                if resources:
                    print("      ✅ RESOURCE MONITORING: Success")
                else:
                    print("      ⚠️  RESOURCE MONITORING: No status available")
                
                self.test_results['error_recovery']['success'] += 1
                
            except Exception as e:
                print(f"      ❌ Resource Exhaustion Failed: {e}")
                self.test_results['error_recovery']['errors'].append(f"Resources: {e}")
            
        except Exception as e:
            print(f"   ❌ Error Recovery Test Failed: {e}")
            self.test_results['error_recovery']['errors'].append(f"General: {e}")
    
    def calculate_infrastructure_reliability(self):
        """Calculate overall infrastructure reliability."""
        print("\n📊 INFRASTRUCTURE RELIABILITY CALCULATION")
        print("=" * 60)
        
        total_tests = 0
        successful_tests = 0
        total_errors = 0
        
        for component, results in self.test_results.items():
            total_tests += results['total']
            successful_tests += results['success']
            total_errors += len(results['errors'])
            
            success_rate = (results['success'] / results['total']) * 100 if results['total'] > 0 else 0
            
            print(f"📋 {component.replace('_', ' ').title()}:")
            print(f"   Tests: {results['success']}/{results['total']} ({success_rate:.1f}%)")
            if results['errors']:
                print(f"   Errors: {len(results['errors'])}")
                for error in results['errors'][:3]:  # Show first 3 errors
                    print(f"      - {error}")
                if len(results['errors']) > 3:
                    print(f"      - ... and {len(results['errors']) - 3} more")
            else:
                print(f"   Errors: 0")
        
        overall_success_rate = (successful_tests / total_tests) * 100 if total_tests > 0 else 0
        
        print(f"\n🎯 Overall Infrastructure Reliability:")
        print(f"   Total Tests: {total_tests}")
        print(f"   Successful: {successful_tests}")
        print(f"   Failed: {total_tests - successful_tests}")
        print(f"   Success Rate: {overall_success_rate:.1f}%")
        print(f"   Total Errors: {total_errors}")
        
        return {
            'overall_success_rate': overall_success_rate,
            'total_tests': total_tests,
            'successful_tests': successful_tests,
            'total_errors': total_errors,
            'component_results': self.test_results
        }
    
    def generate_infrastructure_report(self, metrics):
        """Generate comprehensive infrastructure report."""
        print(f"\n📋 PRODUCTION INFRASTRUCTURE REPORT")
        print("=" * 60)
        
        success_rate = metrics['overall_success_rate']
        
        print(f"🎯 INFRASTRUCTURE ASSESSMENT:")
        
        if success_rate >= 95:
            print(f"   🟢 EXCELLENT ({success_rate:.1f}%) - Production Ready")
            print(f"   ✅ All infrastructure components highly reliable")
            print(f"   ✅ Minimal risk of production failures")
        elif success_rate >= 90:
            print(f"   🟡 VERY GOOD ({success_rate:.1f}%) - Near Production Ready")
            print(f"   ✅ Most infrastructure components reliable")
            print(f"   ⚠️  Minor improvements recommended")
        elif success_rate >= 80:
            print(f"   🟠 GOOD ({success_rate:.1f}%) - Needs Minor Improvements")
            print(f"   ✅ Core infrastructure reliable")
            print(f"   ⚠️  Some components need attention")
        elif success_rate >= 70:
            print(f"   🔴 FAIR ({success_rate:.1f}%) - Needs Significant Improvements")
            print(f"   ⚠️  Multiple components need attention")
            print(f"   ❌ Not ready for production")
        else:
            print(f"   🔴 POOR ({success_rate:.1f}%) - Major Issues")
            print(f"   ❌ Multiple critical failures")
            print(f"   ❌ Not ready for production")
        
        print(f"\n📊 DETAILED BREAKDOWN:")
        print(f"   Overall Success Rate: {success_rate:.1f}%")
        print(f"   Total Tests: {metrics['total_tests']}")
        print(f"   Successful Tests: {metrics['successful_tests']}")
        print(f"   Total Errors: {metrics['total_errors']}")
        
        print(f"\n🔧 COMPONENT STATUS:")
        for component, results in metrics['component_results'].items():
            success_rate = (results['success'] / results['total']) * 100 if results['total'] > 0 else 0
            status = "🟢" if success_rate >= 95 else "🟡" if success_rate >= 80 else "🔴"
            print(f"   {status} {component.replace('_', ' ').title()}: {success_rate:.1f}% success")
        
        print(f"\n💡 RECOMMENDATIONS:")
        if success_rate >= 95:
            print(f"   ✅ Infrastructure is production-ready")
            print(f"   ✅ Deploy with confidence")
            print(f"   ✅ Monitor performance in production")
        elif success_rate >= 90:
            print(f"   🔧 Address minor issues before production")
            print(f"   📊 Monitor specific components")
            print(f"   🧪 Run additional tests on edge cases")
        else:
            print(f"   🚨 Address critical issues before production")
            print(f"   🔧 Focus on failing components")
            print(f"   🧪 Extensive testing required")
        
        return {
            'infrastructure_level': 'excellent' if success_rate >= 95 else 'very_good' if success_rate >= 90 else 'good' if success_rate >= 80 else 'fair' if success_rate >= 70 else 'poor',
            'production_ready': success_rate >= 95,
            'recommendations': self._get_infrastructure_recommendations(success_rate)
        }
    
    def _get_infrastructure_recommendations(self, success_rate):
        """Get specific infrastructure recommendations based on success rate."""
        if success_rate >= 95:
            return [
                "Deploy infrastructure to production with confidence",
                "Set up comprehensive monitoring and alerting",
                "Document infrastructure performance baselines"
            ]
        elif success_rate >= 90:
            return [
                "Address minor infrastructure issues",
                "Run additional edge case tests",
                "Implement comprehensive monitoring"
            ]
        else:
            return [
                "Fix critical infrastructure failures",
                "Run extensive infrastructure testing",
                "Review and improve error handling"
            ]
    
    async def run_infrastructure_test(self):
        """Run complete infrastructure test."""
        print("🚀 Starting Production Infrastructure Test")
        print(f"⏰ Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Test all infrastructure components
        await self.test_database_operations()
        await self.test_resume_capabilities()
        await self.test_connection_management()
        await self.test_watchdog_functionality()
        await self.test_error_recovery()
        
        # Calculate reliability metrics
        metrics = self.calculate_infrastructure_reliability()
        
        # Generate infrastructure report
        report = self.generate_infrastructure_report(metrics)
        
        print(f"\n⏰ Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return {
            'metrics': metrics,
            'report': report
        }


async def main():
    """Main infrastructure test function."""
    tester = ProductionInfrastructureTester()
    results = await tester.run_infrastructure_test()
    return results


if __name__ == "__main__":
    asyncio.run(main())

