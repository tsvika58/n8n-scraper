# 🧪 **SCRAPE-010: IMPLEMENTATION GUIDE**

**From:** RND Manager  
**To:** Dev1  
**Date:** October 11, 2025, 2:10 PM  
**Subject:** Detailed Implementation Guide for Integration Testing  
**Task:** SCRAPE-010 - Integration Testing Suite

---

## 🔧 **PHASE 1: TEST INFRASTRUCTURE & DATASET (2 HOURS)**

### **Step 1: Configure Integration Test Framework (30 minutes)**

Create `tests/integration/conftest.py`:

```python
"""
Shared pytest fixtures for integration testing.

Provides database connections, E2E pipeline, and test data.
"""

import pytest
import json
import asyncio
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.storage.database import Base, get_engine, get_session
from src.storage.repository import WorkflowRepository
from src.orchestrator.e2e_pipeline import E2EPipeline
from src.validators.quality import QualityValidator

# ============================================================================
# DATABASE FIXTURES
# ============================================================================

@pytest.fixture(scope="session")
def test_database_url():
    """Test database connection string."""
    return "postgresql://scraper_user:scraper_password@localhost:5432/n8n_scraper"

@pytest.fixture(scope="session")
def test_engine(test_database_url):
    """SQLAlchemy engine for testing."""
    engine = create_engine(
        test_database_url,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True
    )
    yield engine
    engine.dispose()

@pytest.fixture(scope="session")
def test_session_factory(test_engine):
    """Session factory for tests."""
    return sessionmaker(bind=test_engine)

@pytest.fixture
def test_session(test_session_factory):
    """Database session for each test."""
    session = test_session_factory()
    try:
        yield session
    finally:
        session.rollback()
        session.close()

@pytest.fixture
def repository(test_session):
    """WorkflowRepository instance for testing."""
    return WorkflowRepository(session=test_session)

# ============================================================================
# E2E PIPELINE FIXTURES
# ============================================================================

@pytest.fixture
def e2e_pipeline():
    """E2E Pipeline instance for testing."""
    return E2EPipeline()

@pytest.fixture
def quality_validator():
    """Quality Validator instance for testing."""
    return QualityValidator()

# ============================================================================
# TEST DATASET FIXTURES
# ============================================================================

@pytest.fixture(scope="session")
def workflow_test_dataset():
    """Load 500 workflow test dataset."""
    dataset_path = Path(__file__).parent.parent / "data" / "integration_test_workflows.json"
    with open(dataset_path) as f:
        workflows = json.load(f)
    return workflows

@pytest.fixture
def good_workflows(workflow_test_dataset):
    """300 workflows expected to succeed (80%+ quality)."""
    return [w for w in workflow_test_dataset if w['category'] == 'good']

@pytest.fixture
def challenging_workflows(workflow_test_dataset):
    """150 workflows with expected Layer 2 issues."""
    return [w for w in workflow_test_dataset if w['category'] == 'challenging']

@pytest.fixture
def edge_case_workflows(workflow_test_dataset):
    """50 edge case workflows."""
    return [w for w in workflow_test_dataset if w['category'] == 'edge_case']

# ============================================================================
# PERFORMANCE MONITORING FIXTURES
# ============================================================================

@pytest.fixture
def performance_monitor():
    """Performance monitoring utility."""
    from tests.integration.utils.performance_monitor import PerformanceMonitor
    return PerformanceMonitor()

# ============================================================================
# CLEANUP FIXTURES
# ============================================================================

@pytest.fixture(autouse=True)
def cleanup_test_data(test_session):
    """Clean up test data after each test."""
    yield
    # Cleanup happens after test completes
    try:
        test_session.execute("DELETE FROM video_transcripts WHERE workflow_id LIKE 'TEST-%'")
        test_session.execute("DELETE FROM workflow_content WHERE workflow_id LIKE 'TEST-%'")
        test_session.execute("DELETE FROM workflow_structure WHERE workflow_id LIKE 'TEST-%'")
        test_session.execute("DELETE FROM workflow_metadata WHERE workflow_id LIKE 'TEST-%'")
        test_session.execute("DELETE FROM workflows WHERE workflow_id LIKE 'TEST-%'")
        test_session.commit()
    except Exception as e:
        test_session.rollback()
        print(f"Cleanup warning: {e}")
```

---

### **Step 2: Create 500 Workflow Test Dataset (45 minutes)**

Create `tests/integration/utils/dataset_generator.py`:

```python
"""
Generate 500 workflow test dataset for integration testing.

Dataset composition:
- 300 "good" workflows (expected 80%+ quality)
- 150 "challenging" workflows (Layer 2 issues expected)
- 50 "edge case" workflows (various edge conditions)
"""

import json
import random
from pathlib import Path
from typing import List, Dict

class DatasetGenerator:
    """Generate integration test dataset."""
    
    def __init__(self):
        self.dataset = []
    
    def generate_dataset(self, total: int = 500) -> List[Dict]:
        """Generate complete test dataset."""
        print(f"Generating {total} workflow test dataset...")
        
        # Good workflows (60%)
        good_count = int(total * 0.6)
        self.dataset.extend(self._generate_good_workflows(good_count))
        
        # Challenging workflows (30%)
        challenging_count = int(total * 0.3)
        self.dataset.extend(self._generate_challenging_workflows(challenging_count))
        
        # Edge case workflows (10%)
        edge_count = total - good_count - challenging_count
        self.dataset.extend(self._generate_edge_case_workflows(edge_count))
        
        # Shuffle for realistic distribution
        random.shuffle(self.dataset)
        
        print(f"✅ Generated {len(self.dataset)} workflows")
        print(f"   - Good: {good_count}")
        print(f"   - Challenging: {challenging_count}")
        print(f"   - Edge cases: {edge_count}")
        
        return self.dataset
    
    def _generate_good_workflows(self, count: int) -> List[Dict]:
        """Generate workflows expected to succeed."""
        # Use known good workflow IDs from SCRAPE-007 results
        known_good_ids = [
            '2462', '2091', '1925', '2203', '1865', '1948',
            '1983', '2008', '2050', '2100', '2150', '2200',
            # ... add more from SCRAPE-007 successful workflows
        ]
        
        workflows = []
        for i in range(count):
            if i < len(known_good_ids):
                wf_id = known_good_ids[i]
            else:
                # Generate synthetic IDs for testing
                wf_id = f"TEST-GOOD-{i:04d}"
            
            workflows.append({
                'id': wf_id,
                'url': f'https://n8n.io/workflows/{wf_id}',
                'category': 'good',
                'expected_layer1': 'success',
                'expected_layer2': 'success',
                'expected_layer3': 'success',
                'expected_quality': 85,
                'description': f'Good workflow {wf_id} with complete data'
            })
        
        return workflows
    
    def _generate_challenging_workflows(self, count: int) -> List[Dict]:
        """Generate workflows with expected Layer 2 issues."""
        # Use known Layer 2 failures from SCRAPE-007
        known_layer2_failures = [
            '2021', '1847', '1912', '2134', '2076',
            # ... add from SCRAPE-007 Layer 2 failures
        ]
        
        workflows = []
        for i in range(count):
            if i < len(known_layer2_failures):
                wf_id = known_layer2_failures[i]
            else:
                wf_id = f"TEST-CHAL-{i:04d}"
            
            workflows.append({
                'id': wf_id,
                'url': f'https://n8n.io/workflows/{wf_id}',
                'category': 'challenging',
                'expected_layer1': 'success',
                'expected_layer2': 'failure',  # Expected to fail
                'expected_layer3': 'success',
                'expected_quality': 50,
                'description': f'Challenging workflow {wf_id} with Layer 2 issues'
            })
        
        return workflows
    
    def _generate_edge_case_workflows(self, count: int) -> List[Dict]:
        """Generate edge case workflows."""
        edge_cases = []
        
        for i in range(count):
            edge_type = i % 5  # 5 types of edge cases
            
            if edge_type == 0:
                # Minimal data
                edge_cases.append({
                    'id': f"TEST-EDGE-MIN-{i:04d}",
                    'url': f'https://n8n.io/workflows/TEST-EDGE-MIN-{i:04d}',
                    'category': 'edge_case',
                    'edge_type': 'minimal_data',
                    'expected_quality': 30,
                    'description': 'Workflow with minimal valid data'
                })
            elif edge_type == 1:
                # Special characters
                edge_cases.append({
                    'id': f"TEST-EDGE-CHAR-{i:04d}",
                    'url': f'https://n8n.io/workflows/TEST-EDGE-CHAR-{i:04d}',
                    'category': 'edge_case',
                    'edge_type': 'special_chars',
                    'expected_quality': 60,
                    'description': 'Workflow with unicode and special characters'
                })
            elif edge_type == 2:
                # Large payload
                edge_cases.append({
                    'id': f"TEST-EDGE-LARGE-{i:04d}",
                    'url': f'https://n8n.io/workflows/TEST-EDGE-LARGE-{i:04d}',
                    'category': 'edge_case',
                    'edge_type': 'large_payload',
                    'expected_quality': 75,
                    'description': 'Workflow with very large JSON payload'
                })
            elif edge_type == 3:
                # Missing metadata
                edge_cases.append({
                    'id': f"TEST-EDGE-NOMETA-{i:04d}",
                    'url': f'https://n8n.io/workflows/TEST-EDGE-NOMETA-{i:04d}',
                    'category': 'edge_case',
                    'edge_type': 'missing_metadata',
                    'expected_quality': 40,
                    'description': 'Workflow without metadata'
                })
            else:
                # Duplicate
                edge_cases.append({
                    'id': '2462',  # Duplicate ID
                    'url': 'https://n8n.io/workflows/2462',
                    'category': 'edge_case',
                    'edge_type': 'duplicate',
                    'expected_quality': 85,
                    'description': 'Duplicate workflow ID for conflict testing'
                })
        
        return edge_cases
    
    def save_dataset(self, output_path: str = None):
        """Save dataset to JSON file."""
        if output_path is None:
            output_path = Path(__file__).parent.parent.parent / "data" / "integration_test_workflows.json"
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(self.dataset, f, indent=2)
        
        print(f"✅ Dataset saved to: {output_path}")
        print(f"   Total workflows: {len(self.dataset)}")


if __name__ == "__main__":
    generator = DatasetGenerator()
    dataset = generator.generate_dataset(500)
    generator.save_dataset()
```

Run the generator:

```bash
python tests/integration/utils/dataset_generator.py
```

---

### **Step 3: Create Performance Monitor (30 minutes)**

Create `tests/integration/utils/performance_monitor.py`:

```python
"""
Performance monitoring utility for integration tests.

Tracks:
- Execution time per workflow
- Database query performance
- Memory usage
- Success rates
- Error rates
"""

import time
import psutil
from typing import Dict, List
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class PerformanceMetrics:
    """Performance metrics container."""
    workflow_id: str
    start_time: float
    end_time: float = 0.0
    duration: float = 0.0
    success: bool = False
    layer1_time: float = 0.0
    layer2_time: float = 0.0
    layer3_time: float = 0.0
    storage_time: float = 0.0
    memory_mb: float = 0.0
    error: str = None

class PerformanceMonitor:
    """Monitor performance during integration tests."""
    
    def __init__(self):
        self.metrics: List[PerformanceMetrics] = []
        self.start_time = time.time()
    
    def start_workflow(self, workflow_id: str) -> PerformanceMetrics:
        """Start monitoring a workflow."""
        metric = PerformanceMetrics(
            workflow_id=workflow_id,
            start_time=time.time()
        )
        return metric
    
    def end_workflow(self, metric: PerformanceMetrics, success: bool, error: str = None):
        """End monitoring a workflow."""
        metric.end_time = time.time()
        metric.duration = metric.end_time - metric.start_time
        metric.success = success
        metric.error = error
        metric.memory_mb = psutil.Process().memory_info().rss / 1024 / 1024
        self.metrics.append(metric)
    
    def get_statistics(self) -> Dict:
        """Get performance statistics."""
        if not self.metrics:
            return {}
        
        total_time = time.time() - self.start_time
        successful = [m for m in self.metrics if m.success]
        failed = [m for m in self.metrics if not m.success]
        
        durations = [m.duration for m in self.metrics if m.duration > 0]
        
        return {
            'total_workflows': len(self.metrics),
            'successful': len(successful),
            'failed': len(failed),
            'success_rate': len(successful) / len(self.metrics) * 100 if self.metrics else 0,
            'total_time': total_time,
            'avg_time_per_workflow': sum(durations) / len(durations) if durations else 0,
            'min_time': min(durations) if durations else 0,
            'max_time': max(durations) if durations else 0,
            'throughput': len(self.metrics) / total_time * 60 if total_time > 0 else 0,  # workflows/minute
            'avg_memory_mb': sum(m.memory_mb for m in self.metrics) / len(self.metrics) if self.metrics else 0,
            'errors': [{'workflow_id': m.workflow_id, 'error': m.error} for m in failed]
        }
    
    def print_report(self):
        """Print performance report."""
        stats = self.get_statistics()
        
        print("\n" + "="*60)
        print("📊 PERFORMANCE REPORT")
        print("="*60)
        print(f"Total Workflows: {stats['total_workflows']}")
        print(f"Successful: {stats['successful']} ({stats['success_rate']:.1f}%)")
        print(f"Failed: {stats['failed']}")
        print(f"\nTiming:")
        print(f"  Total Time: {stats['total_time']:.2f}s")
        print(f"  Average per Workflow: {stats['avg_time_per_workflow']:.2f}s")
        print(f"  Min: {stats['min_time']:.2f}s")
        print(f"  Max: {stats['max_time']:.2f}s")
        print(f"  Throughput: {stats['throughput']:.1f} workflows/minute")
        print(f"\nMemory:")
        print(f"  Average: {stats['avg_memory_mb']:.1f} MB")
        
        if stats['errors']:
            print(f"\nErrors ({len(stats['errors'])}):")
            for error in stats['errors'][:10]:  # Show first 10
                print(f"  - {error['workflow_id']}: {error['error']}")
        
        print("="*60 + "\n")
    
    def save_report(self, output_path: str):
        """Save performance report to file."""
        import json
        stats = self.get_statistics()
        
        with open(output_path, 'w') as f:
            json.dump(stats, f, indent=2)
        
        print(f"✅ Performance report saved to: {output_path}")
```

---

### **Step 4: Verify Docker Database (15 minutes)**

```bash
# Ensure Docker database is running
./scripts/start.sh

# Verify connection
docker exec n8n-scraper-database psql -U scraper_user -d n8n_scraper -c "SELECT version();"

# Check tables
docker exec n8n-scraper-database psql -U scraper_user -d n8n_scraper -c "\dt"

# Verify your storage layer works
docker exec n8n-scraper-app python -c "
from src.storage.repository import WorkflowRepository
from src.storage.database import get_session

session = get_session()
repo = WorkflowRepository(session)
stats = repo.get_statistics()
print(f'✅ Repository working! {stats}')
"
```

---

## 🧪 **PHASE 2: INTEGRATION TEST DEVELOPMENT (4 HOURS)**

### **Test File 1: E2E Storage Integration (15 tests, 1 hour)**

Create `tests/integration/test_e2e_storage.py`:

```python
"""
E2E Pipeline → Storage Integration Tests.

Tests the complete flow: Layer 1 → Layer 2 → Layer 3 → Database Storage
"""

import pytest
import asyncio
from tests.integration.utils.performance_monitor import PerformanceMonitor

# ============================================================================
# SUCCESS PATH TESTS (5 tests)
# ============================================================================

@pytest.mark.asyncio
async def test_complete_workflow_e2e_success(
    good_workflows, 
    e2e_pipeline, 
    repository,
    performance_monitor
):
    """Test complete E2E pipeline with storage for successful workflows."""
    success_count = 0
    test_workflows = good_workflows[:10]  # Test first 10
    
    for workflow in test_workflows:
        metric = performance_monitor.start_workflow(workflow['id'])
        
        try:
            # Extract via E2E pipeline
            result = await e2e_pipeline.process_workflow(
                workflow['id'], 
                workflow['url']
            )
            
            # Verify extraction
            assert result['layers']['layer1']['success'] == True, "Layer 1 failed"
            
            # Store in database
            stored = repository.create_workflow(
                workflow_id=workflow['id'],
                url=workflow['url'],
                extraction_result=result
            )
            
            # Verify storage
            assert stored is not None, "Storage failed"
            assert stored.workflow_id == workflow['id']
            
            # Verify retrieval
            retrieved = repository.get_workflow(workflow['id'])
            assert retrieved is not None, "Retrieval failed"
            assert retrieved.workflow_id == workflow['id']
            
            performance_monitor.end_workflow(metric, True)
            success_count += 1
            
        except Exception as e:
            performance_monitor.end_workflow(metric, False, str(e))
            pytest.fail(f"Workflow {workflow['id']} failed: {e}")
    
    # Verify success rate
    assert success_count == len(test_workflows), f"Expected {len(test_workflows)}, got {success_count}"
    
    # Print performance
    performance_monitor.print_report()


@pytest.mark.asyncio
async def test_layer1_extraction_and_storage(
    good_workflows,
    e2e_pipeline,
    repository
):
    """Test Layer 1 (metadata) extraction and storage."""
    workflow = good_workflows[0]
    
    # Extract
    result = await e2e_pipeline.process_workflow(workflow['id'], workflow['url'])
    
    # Verify Layer 1 data
    assert result['layers']['layer1']['success'] == True
    layer1_data = result['layers']['layer1']['data']
    assert 'title' in layer1_data
    assert 'description' in layer1_data
    
    # Store
    stored = repository.create_workflow(
        workflow_id=workflow['id'],
        url=workflow['url'],
        extraction_result=result
    )
    
    # Verify metadata stored
    assert stored.metadata is not None
    assert stored.metadata.title == layer1_data['title']
    assert stored.metadata.description == layer1_data['description']


@pytest.mark.asyncio
async def test_layer2_extraction_and_storage(
    good_workflows,
    e2e_pipeline,
    repository
):
    """Test Layer 2 (JSON/nodes) extraction and storage."""
    workflow = good_workflows[0]
    
    # Extract
    result = await e2e_pipeline.process_workflow(workflow['id'], workflow['url'])
    
    # Verify Layer 2 data
    layer2_data = result['layers']['layer2']
    if layer2_data['success']:
        assert layer2_data['node_count'] > 0, "No nodes found"
        
        # Store
        stored = repository.create_workflow(
            workflow_id=workflow['id'],
            url=workflow['url'],
            extraction_result=result
        )
        
        # Verify structure stored
        assert stored.structure is not None
        assert stored.structure.node_count == layer2_data['node_count']
        assert stored.structure.nodes is not None


@pytest.mark.asyncio
async def test_layer3_extraction_and_storage(
    good_workflows,
    e2e_pipeline,
    repository
):
    """Test Layer 3 (content) extraction and storage."""
    workflow = good_workflows[0]
    
    # Extract
    result = await e2e_pipeline.process_workflow(workflow['id'], workflow['url'])
    
    # Verify Layer 3 data
    layer3_data = result['layers']['layer3']
    assert layer3_data['success'] == True
    
    # Store
    stored = repository.create_workflow(
        workflow_id=workflow['id'],
        url=workflow['url'],
        extraction_result=result
    )
    
    # Verify content stored
    assert stored.content is not None
    assert stored.content.explainer_text is not None


@pytest.mark.asyncio
async def test_all_layers_complete_workflow(
    good_workflows,
    e2e_pipeline,
    repository
):
    """Test complete workflow with all 3 layers stored."""
    workflow = good_workflows[0]
    
    # Extract
    result = await e2e_pipeline.process_workflow(workflow['id'], workflow['url'])
    
    # Store
    stored = repository.create_workflow(
        workflow_id=workflow['id'],
        url=workflow['url'],
        extraction_result=result
    )
    
    # Verify all relationships
    assert stored.metadata is not None, "Metadata missing"
    assert stored.structure is not None, "Structure missing"
    assert stored.content is not None, "Content missing"
    
    # Verify workflow record
    assert stored.processing_status == 'complete'
    assert stored.quality_score > 0


# ============================================================================
# PARTIAL SUCCESS TESTS (5 tests)
# ============================================================================

@pytest.mark.asyncio
async def test_layer2_fails_but_others_succeed(
    challenging_workflows,
    e2e_pipeline,
    repository
):
    """Test handling when Layer 2 fails but others succeed."""
    workflow = challenging_workflows[0]
    
    # Extract
    result = await e2e_pipeline.process_workflow(workflow['id'], workflow['url'])
    
    # Verify Layer 1 and 3 succeed
    assert result['layers']['layer1']['success'] == True
    assert result['layers']['layer3']['success'] == True
    
    # Layer 2 may fail (expected for challenging workflows)
    layer2_success = result['layers']['layer2']['success']
    
    # Store anyway (graceful degradation)
    stored = repository.create_workflow(
        workflow_id=workflow['id'],
        url=workflow['url'],
        extraction_result=result
    )
    
    # Verify partial storage
    assert stored.metadata is not None, "Metadata should be stored"
    assert stored.content is not None, "Content should be stored"
    
    if not layer2_success:
        # Structure may be None or have minimal data
        assert stored.processing_status in ['partial', 'complete']


@pytest.mark.asyncio
async def test_fallback_extraction_works(
    challenging_workflows,
    e2e_pipeline,
    repository
):
    """Test fallback API extraction and storage."""
    workflow = challenging_workflows[0]
    
    # Extract (may use fallback)
    result = await e2e_pipeline.process_workflow(workflow['id'], workflow['url'])
    
    layer2_data = result['layers']['layer2']
    
    if layer2_data.get('fallback_used'):
        # Verify fallback worked
        assert layer2_data['extraction_type'] == 'partial'
        
        # Store fallback data
        stored = repository.create_workflow(
            workflow_id=workflow['id'],
            url=workflow['url'],
            extraction_result=result
        )
        
        # Verify partial storage
        assert stored is not None
        assert stored.structure.extraction_type == 'partial'


# ============================================================================
# ERROR HANDLING TESTS (5 tests)
# ============================================================================

@pytest.mark.asyncio
async def test_invalid_workflow_id(
    e2e_pipeline,
    repository
):
    """Test handling of invalid workflow ID."""
    invalid_id = "INVALID-9999"
    invalid_url = f"https://n8n.io/workflows/{invalid_id}"
    
    # Should handle gracefully
    result = await e2e_pipeline.process_workflow(invalid_id, invalid_url)
    
    # Expect failures
    assert result['layers']['layer1']['success'] == False or \
           result['layers']['layer2']['success'] == False
    
    # Should NOT crash when storing
    try:
        stored = repository.create_workflow(
            workflow_id=invalid_id,
            url=invalid_url,
            extraction_result=result
        )
        # If stored, should have error status
        assert stored.processing_status in ['failed', 'error']
    except Exception as e:
        # Or gracefully reject
        assert '404' in str(e) or 'not found' in str(e).lower()


# Additional tests would follow similar patterns...
```

---

## 📊 **PHASE 3: EXECUTION & VALIDATION (2 HOURS)**

### **Run Complete Test Suite:**

```bash
# Run all integration tests with coverage
pytest tests/integration/ -v --cov=src --cov-report=html --cov-report=term

# Run with performance monitoring
pytest tests/integration/ -v -s  # -s shows print output

# Run specific test file
pytest tests/integration/test_e2e_storage.py -v

# Run 500 workflow test
pytest tests/integration/test_bulk_500_workflows.py -v --timeout=7200
```

### **Generate Performance Report:**

```python
# Create final performance report
python tests/integration/utils/generate_report.py
```

---

**🎯 Complete implementation guide ready for Dev1!**

---

*Implementation Guide v1.0*  
*Created: October 11, 2025, 2:10 PM*  
*Author: RND Manager*  
*For: Dev1*
