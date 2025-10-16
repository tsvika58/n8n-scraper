#!/usr/bin/env python3
"""
Production Readiness Test - FIXED
Focused test of production infrastructure components with correct field names.

Author: Dev1
Task: Test Production Readiness - Fixed
Date: October 16, 2025
"""

import asyncio
import sys
import time
from datetime import datetime
sys.path.append('.')

from src.scrapers.unified_workflow_extractor import UnifiedWorkflowExtractor
from src.storage.database import get_session
import sys
sys.path.append('../n8n-shared')
from n8n_shared.models import Workflow, WorkflowNodeContext, WorkflowStandaloneDoc, WorkflowExtractionSnapshot


class ProductionReadinessTesterFixed:
    """Focused test of production readiness components with correct field names."""
    
    def __init__(self):
        self.test_workflow_id = 'TEST_PROD_FIXED_001'
        self.test_workflows = [
            {'id': '7639', 'url': 'https://n8n.io/workflows/7639-talk-to-your-google-sheets-using-chatgpt-5'},
            {'id': '8237', 'url': 'https://n8n.io/workflows/8237-personal-life-manager-with-telegram-google-services-and-voice-enabled-ai'},
            {'id': '6270', 'url': 'https://n8n.io/workflows/6270-automate-customer-support-with-ai-and-telegram'}
        ]
        self.test_results = {
            'database_crud': {'success': 0, 'total': 0, 'errors': []},
            'unified_scraper_integration': {'success': 0, 'total': 0, 'errors': []},
            'resume_capabilities': {'success': 0, 'total': 0, 'errors': []},
            'error_handling': {'success': 0, 'total': 0, 'errors': []},
            'performance_under_load': {'success': 0, 'total': 0, 'errors': []}
        }
    
    async def test_database_crud_operations(self):
        """Test comprehensive database CRUD operations with correct field names."""
        print("🗄️  Testing Database CRUD Operations")
        print("=" * 50)
        
        try:
            # Test 1: Create workflow
            print("   📝 Test 1: Create Workflow")
            self.test_results['database_crud']['total'] += 1
            
            try:
                with get_session() as session:
                    # Create test workflow with correct fields
                    test_workflow = Workflow(
                        workflow_id=self.test_workflow_id,
                        url='https://n8n.io/workflows/test-prod-fixed-001',
                        extracted_at=datetime.utcnow(),
                        updated_at=datetime.utcnow(),
                        layer1_success=True,
                        layer2_success=False,
                        layer3_success=False,
                        unified_extraction_success=False
                    )
                    
                    session.add(test_workflow)
                    session.commit()
                    print("      ✅ CREATE: Success")
                    
                    # Verify creation
                    retrieved = session.query(Workflow).filter_by(workflow_id=self.test_workflow_id).first()
                    if retrieved and retrieved.url == 'https://n8n.io/workflows/test-prod-fixed-001':
                        print("      ✅ CREATE VERIFICATION: Success")
                    else:
                        raise Exception("Create verification failed")
                
                self.test_results['database_crud']['success'] += 1
                
            except Exception as e:
                print(f"      ❌ Create Workflow Failed: {e}")
                self.test_results['database_crud']['errors'].append(f"Create: {e}")
            
            # Test 2: Update workflow
            print("   📝 Test 2: Update Workflow")
            self.test_results['database_crud']['total'] += 1
            
            try:
                with get_session() as session:
                    # Update workflow
                    workflow = session.query(Workflow).filter_by(workflow_id=self.test_workflow_id).first()
                    if workflow:
                        workflow.layer2_success = True
                        workflow.updated_at = datetime.utcnow()
                        session.commit()
                        print("      ✅ UPDATE: Success")
                        
                        # Verify update
                        updated = session.query(Workflow).filter_by(workflow_id=self.test_workflow_id).first()
                        if updated and updated.layer2_success:
                            print("      ✅ UPDATE VERIFICATION: Success")
                        else:
                            raise Exception("Update verification failed")
                    else:
                        raise Exception("Workflow not found for update")
                
                self.test_results['database_crud']['success'] += 1
                
            except Exception as e:
                print(f"      ❌ Update Workflow Failed: {e}")
                self.test_results['database_crud']['errors'].append(f"Update: {e}")
            
            # Test 3: Complex data operations
            print("   📝 Test 3: Complex Data Operations")
            self.test_results['database_crud']['total'] += 1
            
            try:
                with get_session() as session:
                    # Add a node context
                    node_context = WorkflowNodeContext(
                        workflow_id=self.test_workflow_id,
                        node_name="Test Node",
                        node_type="n8n-nodes-base.testNode",
                        sticky_title="Test Sticky",
                        sticky_content="This is a test sticky note content.",
                        sticky_markdown="This is a **test** sticky note content.",
                        match_confidence=0.9,
                        extraction_method="test_method"
                    )
                    session.add(node_context)
                    
                    # Add a standalone doc
                    standalone_doc = WorkflowStandaloneDoc(
                        workflow_id=self.test_workflow_id,
                        doc_type="text",
                        doc_title="Standalone Doc",
                        doc_content="This is a standalone document.",
                        doc_markdown="This is a **standalone** document.",
                        confidence_score=0.8
                    )
                    session.add(standalone_doc)
                    
                    # Add an extraction snapshot
                    snapshot = WorkflowExtractionSnapshot(
                        workflow_id=self.test_workflow_id,
                        layer="UNIFIED_TEST",
                        payload={"test_key": "test_value"}
                    )
                    session.add(snapshot)
                    
                    session.commit()
                    print("      ✅ COMPLEX DATA SAVE: Success")
                
                self.test_results['database_crud']['success'] += 1
                
            except Exception as e:
                print(f"      ❌ Complex Data Operations Failed: {e}")
                self.test_results['database_crud']['errors'].append(f"Complex Data: {e}")
            
            # Test 4: Delete workflow (cleanup)
            print("   📝 Test 4: Delete Workflow (Cleanup)")
            self.test_results['database_crud']['total'] += 1
            
            try:
                with get_session() as session:
                    # Delete related data first (manual cascade)
                    session.query(WorkflowNodeContext).filter_by(workflow_id=self.test_workflow_id).delete()
                    session.query(WorkflowStandaloneDoc).filter_by(workflow_id=self.test_workflow_id).delete()
                    session.query(WorkflowExtractionSnapshot).filter_by(workflow_id=self.test_workflow_id).delete()
                    
                    # Delete workflow
                    session.query(Workflow).filter_by(workflow_id=self.test_workflow_id).delete()
                    session.commit()
                    print("      ✅ DELETE: Success")
                    
                    # Verify deletion
                    deleted = session.query(Workflow).filter_by(workflow_id=self.test_workflow_id).first()
                    if not deleted:
                        print("      ✅ DELETE VERIFICATION: Success")
                    else:
                        raise Exception("Delete verification failed")
                
                self.test_results['database_crud']['success'] += 1
                
            except Exception as e:
                print(f"      ❌ Delete Workflow Failed: {e}")
                self.test_results['database_crud']['errors'].append(f"Delete: {e}")
            
        except Exception as e:
            print(f"❌ Database CRUD test failed: {e}")
    
    async def test_unified_scraper_integration(self):
        """Test unified scraper integration with database."""
        print("\n🔗 Testing Unified Scraper Integration")
        print("=" * 50)
        
        try:
            # Test 1: Database save verification for existing workflow
            print("   📝 Test 1: Database Save Verification")
            self.test_results['unified_scraper_integration']['total'] += 1
            
            try:
                # Use a workflow that was already extracted (from previous tests)
                test_workflow_id = '8237'
                
                # Verify that existing workflow has proper database save
                with get_session() as session:
                    workflow = session.query(Workflow).filter_by(workflow_id=test_workflow_id).first()
                    
                    if workflow:
                        print(f"      ✅ WORKFLOW FOUND: {test_workflow_id}")
                        print(f"      📊 EXTRACTION STATUS: unified_extraction_success={workflow.unified_extraction_success}")
                        
                        # Check related data
                        contexts = session.query(WorkflowNodeContext).filter_by(workflow_id=test_workflow_id).count()
                        docs = session.query(WorkflowStandaloneDoc).filter_by(workflow_id=test_workflow_id).count()
                        snapshots = session.query(WorkflowExtractionSnapshot).filter_by(workflow_id=test_workflow_id).count()
                        
                        print(f"      📊 RELATED DATA: {contexts} contexts, {docs} docs, {snapshots} snapshots")
                        
                        # Verify data integrity
                        if workflow.unified_extraction_success and contexts > 0 and snapshots > 0:
                            print("      ✅ DATABASE SAVE: Success")
                            print("      ✅ EXTRACTION FLAGS: Success")
                            print("      ✅ RELATED DATA SAVE: Success")
                            self.test_results['unified_scraper_integration']['success'] += 1
                        else:
                            raise Exception(f"Incomplete data: unified_success={workflow.unified_extraction_success}, contexts={contexts}, snapshots={snapshots}")
                    else:
                        raise Exception(f"Workflow {test_workflow_id} not found in database")
                    
            except Exception as e:
                print(f"      ❌ Database Save Verification Failed: {e}")
                self.test_results['unified_scraper_integration']['errors'].append(f"Database Save: {e}")
            
            # Test 2: Multiple workflow processing
            print("   📝 Test 2: Multiple Workflow Processing")
            self.test_results['unified_scraper_integration']['total'] += 1
            
            try:
                extractor = UnifiedWorkflowExtractor()
                results = []
                
                for workflow in self.test_workflows[1:3]:  # Test 2 workflows
                    start_time = time.time()
                    result = await extractor.extract(workflow['id'], workflow['url'])
                    end_time = time.time()
                    
                    if result and result.get('success'):
                        results.append({
                            'id': workflow['id'],
                            'success': True,
                            'time': end_time - start_time
                        })
                        print(f"      ✅ {workflow['id']}: Success in {end_time - start_time:.2f}s")
                    else:
                        results.append({
                            'id': workflow['id'],
                            'success': False,
                            'time': end_time - start_time
                        })
                        print(f"      ❌ {workflow['id']}: Failed")
                
                success_count = sum(1 for r in results if r['success'])
                avg_time = sum(r['time'] for r in results) / len(results)
                
                print(f"      📊 MULTIPLE WORKFLOW RESULTS: {success_count}/{len(results)} ({success_count/len(results)*100:.1f}%) in {avg_time:.2f}s avg")
                
                if success_count == len(results):
                    print("      ✅ MULTIPLE WORKFLOW PROCESSING: Success")
                    self.test_results['unified_scraper_integration']['success'] += 1
                else:
                    raise Exception(f"Only {success_count}/{len(results)} workflows processed successfully")
                    
            except Exception as e:
                print(f"      ❌ Multiple Workflow Processing Failed: {e}")
                self.test_results['unified_scraper_integration']['errors'].append(f"Multiple Workflows: {e}")
            
        except Exception as e:
            print(f"❌ Unified scraper integration test failed: {e}")
    
    async def test_resume_capabilities(self):
        """Test resume capabilities - simplified to test database upsert functionality."""
        print("\n🔄 Testing Resume Capabilities")
        print("=" * 50)
        
        try:
            # Test 1: Database upsert (update or insert) functionality
            print("   📝 Test 1: Database Upsert (Resume Simulation)")
            self.test_results['resume_capabilities']['total'] += 1
            
            try:
                test_workflow_id = 'TEST_RESUME_UPSERT_001'
                
                # Step 1: Create initial workflow
                with get_session() as session:
                    initial_workflow = Workflow(
                        workflow_id=test_workflow_id,
                        url='https://n8n.io/workflows/test-resume-upsert-001',
                        extracted_at=datetime.utcnow(),
                        updated_at=datetime.utcnow(),
                        unified_extraction_success=False
                    )
                    session.add(initial_workflow)
                    session.commit()
                    print("      📝 Created initial workflow record")
                
                # Step 2: Upsert (update) the workflow
                with get_session() as session:
                    existing = session.query(Workflow).filter_by(workflow_id=test_workflow_id).first()
                    if existing:
                        # Simulate resume completion
                        existing.unified_extraction_success = True
                        existing.unified_extraction_at = datetime.utcnow()
                        existing.layer2_extracted_at = datetime.utcnow()
                        existing.layer3_extracted_at = datetime.utcnow()
                        existing.updated_at = datetime.utcnow()
                        session.commit()
                        print("      ✅ UPSERT (UPDATE): Success")
                    else:
                        raise Exception("Workflow not found for upsert")
                
                # Step 3: Verify upsert
                with get_session() as session:
                    updated = session.query(Workflow).filter_by(workflow_id=test_workflow_id).first()
                    if updated and updated.unified_extraction_success and updated.unified_extraction_at:
                        print("      ✅ UPSERT VERIFICATION: Success")
                        print(f"      📊 UPSERT STATUS: unified_extraction_success={updated.unified_extraction_success}")
                        self.test_results['resume_capabilities']['success'] += 1
                    else:
                        raise Exception("Upsert verification failed")
                
                # Cleanup
                with get_session() as session:
                    session.query(Workflow).filter_by(workflow_id=test_workflow_id).delete()
                    session.commit()
                    print("      🧹 Cleanup: Success")
                    
            except Exception as e:
                print(f"      ❌ Database Upsert Failed: {e}")
                self.test_results['resume_capabilities']['errors'].append(f"Upsert: {e}")
            
        except Exception as e:
            print(f"❌ Resume capabilities test failed: {e}")
    
    async def test_error_handling(self):
        """Test error handling and recovery."""
        print("\n🛡️  Testing Error Handling")
        print("=" * 50)
        
        try:
            # Test 1: Invalid workflow handling
            print("   📝 Test 1: Invalid Workflow Handling")
            self.test_results['error_handling']['total'] += 1
            
            try:
                extractor = UnifiedWorkflowExtractor()
                result = await extractor.extract('INVALID_ID', 'https://n8n.io/workflows/invalid-id')
                
                if not result or not result.get('success'):
                    print("      ✅ INVALID WORKFLOW HANDLING: Success (expected failure)")
                    self.test_results['error_handling']['success'] += 1
                else:
                    raise Exception("Should have failed for invalid workflow")
                    
            except Exception as e:
                print(f"      ❌ Invalid Workflow Handling Failed: {e}")
                self.test_results['error_handling']['errors'].append(f"Invalid Workflow: {e}")
            
            # Test 2: Database error handling
            print("   📝 Test 2: Database Error Handling")
            self.test_results['error_handling']['total'] += 1
            
            try:
                with get_session() as session:
                    # Try to query non-existent workflow
                    workflow = session.query(Workflow).filter_by(workflow_id='NON_EXISTENT_001').first()
                    if not workflow:
                        print("      ✅ INVALID WORKFLOW QUERY: Success (not found as expected)")
                        self.test_results['error_handling']['success'] += 1
                    else:
                        raise Exception("Should not have found non-existent workflow")
                        
            except Exception as e:
                print(f"      ❌ Database Error Handling Failed: {e}")
                self.test_results['error_handling']['errors'].append(f"Database Error: {e}")
            
        except Exception as e:
            print(f"❌ Error handling test failed: {e}")
    
    async def test_performance_under_load(self):
        """Test performance under load."""
        print("\n⚡ Testing Performance Under Load")
        print("=" * 50)
        
        try:
            # Test 1: Concurrent extractions
            print("   📝 Test 1: Concurrent Extractions")
            self.test_results['performance_under_load']['total'] += 1
            
            try:
                extractor = UnifiedWorkflowExtractor()
                
                # Run concurrent extractions
                tasks = []
                for workflow in self.test_workflows[:2]:  # Test 2 workflows concurrently
                    task = extractor.extract(workflow['id'], workflow['url'])
                    tasks.append(task)
                
                start_time = time.time()
                results = await asyncio.gather(*tasks, return_exceptions=True)
                end_time = time.time()
                
                success_count = sum(1 for r in results if isinstance(r, dict) and r.get('success'))
                total_time = end_time - start_time
                
                print(f"      📊 CONCURRENT RESULTS: {success_count}/{len(results)} ({success_count/len(results)*100:.1f}%) in {total_time:.2f}s")
                
                if success_count == len(results):
                    print("      ✅ CONCURRENT EXTRACTIONS: Success")
                    self.test_results['performance_under_load']['success'] += 1
                else:
                    raise Exception(f"Only {success_count}/{len(results)} concurrent extractions succeeded")
                    
            except Exception as e:
                print(f"      ❌ Concurrent Extractions Failed: {e}")
                self.test_results['performance_under_load']['errors'].append(f"Concurrent: {e}")
            
        except Exception as e:
            print(f"❌ Performance under load test failed: {e}")
    
    def calculate_production_readiness(self):
        """Calculate overall production readiness score."""
        print("\n📊 PRODUCTION READINESS CALCULATION")
        print("=" * 60)
        
        total_tests = 0
        total_success = 0
        total_errors = 0
        
        for component, results in self.test_results.items():
            success_rate = (results['success'] / results['total'] * 100) if results['total'] > 0 else 0
            total_tests += results['total']
            total_success += results['success']
            total_errors += len(results['errors'])
            
            print(f"📋 {component.replace('_', ' ').title()}:")
            print(f"   Tests: {results['success']}/{results['total']} ({success_rate:.1f}%)")
            if results['errors']:
                print(f"   Errors: {len(results['errors'])}")
                for error in results['errors'][:3]:  # Show first 3 errors
                    print(f"      - {error}")
                if len(results['errors']) > 3:
                    print(f"      - ... and {len(results['errors']) - 3} more")
        
        overall_success_rate = (total_success / total_tests * 100) if total_tests > 0 else 0
        
        print(f"\n🎯 Overall Production Readiness:")
        print(f"   Total Tests: {total_tests}")
        print(f"   Successful: {total_success}")
        print(f"   Failed: {total_tests - total_success}")
        print(f"   Success Rate: {overall_success_rate:.1f}%")
        print(f"   Total Errors: {total_errors}")
        
        return overall_success_rate
    
    def generate_report(self, success_rate):
        """Generate production readiness report."""
        print(f"\n📋 PRODUCTION READINESS REPORT")
        print("=" * 60)
        
        if success_rate >= 90:
            status = "🟢 EXCELLENT"
            recommendation = "✅ System is production-ready\n   ✅ Deploy with confidence\n   ✅ Monitor performance in production"
        elif success_rate >= 80:
            status = "🟡 GOOD"
            recommendation = "✅ System is mostly production-ready\n   ⚠️  Address minor issues before deployment\n   ✅ Monitor closely in production"
        elif success_rate >= 70:
            status = "🟠 FAIR"
            recommendation = "⚠️  System needs improvements before production\n   🔧 Fix critical issues\n   🧪 Run additional tests"
        else:
            status = "🔴 POOR"
            recommendation = "❌ System is not production-ready\n   🔧 Fix critical issues\n   🧪 Extensive testing required"
        
        print(f"🎯 PRODUCTION READINESS ASSESSMENT:")
        print(f"   {status} ({success_rate:.1f}%)")
        
        if success_rate < 80:
            print("   ❌ Multiple critical failures")
            print("   ❌ Not ready for production")
        else:
            print("   ✅ System is production-ready")
            print("   ✅ Deploy with confidence")
        
        print(f"\n📊 DETAILED BREAKDOWN:")
        print(f"   Overall Success Rate: {success_rate:.1f}%")
        print(f"   Total Tests: {sum(r['total'] for r in self.test_results.values())}")
        print(f"   Successful Tests: {sum(r['success'] for r in self.test_results.values())}")
        print(f"   Total Errors: {sum(len(r['errors']) for r in self.test_results.values())}")
        
        print(f"\n🔧 COMPONENT STATUS:")
        for component, results in self.test_results.items():
            success_rate = (results['success'] / results['total'] * 100) if results['total'] > 0 else 0
            status_icon = "🟢" if success_rate >= 80 else "🟡" if success_rate >= 60 else "🔴"
            print(f"   {status_icon} {component.replace('_', ' ').title()}: {success_rate:.1f}% success")
        
        print(f"\n💡 RECOMMENDATIONS:")
        print(f"   {recommendation}")
    
    async def run_production_readiness_test(self):
        """Run complete production readiness test."""
        print("🚀 Starting Production Readiness Test")
        print(f"⏰ Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Run all tests
        await self.test_database_crud_operations()
        await self.test_unified_scraper_integration()
        await self.test_resume_capabilities()
        await self.test_error_handling()
        await self.test_performance_under_load()
        
        # Calculate and report results
        success_rate = self.calculate_production_readiness()
        self.generate_report(success_rate)
        
        print(f"\n⏰ Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return success_rate


async def main():
    """Main function to run production readiness test."""
    tester = ProductionReadinessTesterFixed()
    success_rate = await tester.run_production_readiness_test()
    return success_rate


if __name__ == "__main__":
    asyncio.run(main())
