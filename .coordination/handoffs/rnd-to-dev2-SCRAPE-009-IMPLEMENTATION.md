# 🧪 **SCRAPE-009: IMPLEMENTATION GUIDE**

**From:** RND Manager  
**To:** Dev2  
**Date:** October 11, 2025, 12:40 PM  
**Subject:** Detailed Implementation Guide for Unit Testing Suite  
**Task:** SCRAPE-009 - Unit Testing Suite

---

## 🔧 **PHASE 1: TEST INFRASTRUCTURE (2 HOURS)**

### **Step 1: Install Dependencies (15 minutes)**

```bash
# Install testing dependencies
pip install pytest pytest-cov pytest-asyncio pytest-mock pytest-html

# Verify installation
pytest --version
```

### **Step 2: Configure pytest.ini (15 minutes)**

Create `pytest.ini` in project root:

```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    --cov=src
    --cov-report=html
    --cov-report=term
    --cov-fail-under=90
    --cov-branch
    --strict-markers
    --strict-config
    --verbose
    --tb=short
asyncio_mode = auto
markers =
    unit: Unit tests
    integration: Integration tests
    slow: Slow tests
    external: Tests requiring external services
filterwarnings =
    ignore::DeprecationWarning
    ignore::PendingDeprecationWarning
```

### **Step 3: Create Test Structure (15 minutes)**

```bash
# Create test directories
mkdir -p tests/unit
mkdir -p tests/integration

# Create __init__.py files
touch tests/__init__.py
touch tests/unit/__init__.py
touch tests/integration/__init__.py
```

### **Step 4: Create Shared Fixtures (45 minutes)**

Create `tests/conftest.py`:

```python
"""
Shared pytest fixtures for unit testing.

Provides common mocks and test data for all test files.
"""

import pytest
import json
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime

# ============================================================================
# MOCK RESPONSE DATA
# ============================================================================

@pytest.fixture
def mock_layer1_metadata():
    """Mock Layer 1 metadata response."""
    return {
        'title': 'Test Workflow',
        'description': 'This is a test workflow for automation',
        'author': {
            'name': 'Test Author',
            'url': 'https://n8n.io/user/test-author'
        },
        'categories': ['Sales', 'Marketing'],
        'tags': ['email', 'automation'],
        'views': 1000,
        'shares': 50,
        'created_at': '2024-01-01T00:00:00Z',
        'updated_at': '2024-01-15T12:00:00Z',
        'use_case': 'Email automation for sales team'
    }

@pytest.fixture
def mock_layer2_workflow_json():
    """Mock Layer 2 workflow JSON response."""
    return {
        'id': '2462',
        'name': 'Test Workflow',
        'workflow': {
            'nodes': [
                {
                    'id': 'node1',
                    'name': 'Start',
                    'type': 'n8n-nodes-base.start',
                    'position': [100, 200],
                    'parameters': {}
                },
                {
                    'id': 'node2',
                    'name': 'HTTP Request',
                    'type': 'n8n-nodes-base.httpRequest',
                    'position': [300, 200],
                    'parameters': {
                        'url': 'https://api.example.com',
                        'method': 'GET'
                    }
                }
            ],
            'connections': {
                'Start': {
                    'main': [
                        [
                            {
                                'node': 'HTTP Request',
                                'type': 'main',
                                'index': 0
                            }
                        ]
                    ]
                }
            }
        }
    }

@pytest.fixture
def mock_layer3_content():
    """Mock Layer 3 content response."""
    return {
        'explainer_text': 'This workflow automates email sending',
        'explainer_html': '<p>This workflow automates email sending</p>',
        'setup_instructions': '1. Configure API credentials\n2. Set up email template',
        'use_instructions': '1. Run the workflow\n2. Check results',
        'has_videos': True,
        'videos': [
            {
                'url': 'https://youtube.com/watch?v=test123',
                'video_id': 'test123',
                'platform': 'youtube',
                'transcript': {
                    'text': 'Welcome to this workflow tutorial',
                    'duration': 300,
                    'language': 'en'
                }
            }
        ],
        'has_iframes': True,
        'iframe_count': 2
    }

# ============================================================================
# MOCK EXTERNAL DEPENDENCIES
# ============================================================================

@pytest.fixture
def mock_aiohttp_response():
    """Mock aiohttp response object."""
    response = AsyncMock()
    response.status = 200
    response.json = AsyncMock(return_value={'success': True})
    response.text = AsyncMock(return_value='<html>Success</html>')
    response.headers = {'content-type': 'application/json'}
    return response

@pytest.fixture
def mock_aiohttp_session():
    """Mock aiohttp ClientSession."""
    session = AsyncMock()
    session.get = AsyncMock()
    session.post = AsyncMock()
    session.close = AsyncMock()
    return session

@pytest.fixture
def mock_playwright_page():
    """Mock Playwright page object."""
    page = Mock()
    page.goto = AsyncMock()
    page.content = AsyncMock(return_value='<html>Test content</html>')
    page.query_selector = AsyncMock()
    page.query_selector_all = AsyncMock(return_value=[])
    page.wait_for_selector = AsyncMock()
    page.evaluate = AsyncMock()
    page.close = AsyncMock()
    return page

@pytest.fixture
def mock_playwright_browser():
    """Mock Playwright browser object."""
    browser = Mock()
    browser.new_page = AsyncMock()
    browser.close = AsyncMock()
    return browser

# ============================================================================
# TEST DATA UTILITIES
# ============================================================================

@pytest.fixture
def sample_workflow_id():
    """Sample workflow ID for testing."""
    return '2462'

@pytest.fixture
def sample_workflow_url():
    """Sample workflow URL for testing."""
    return 'https://n8n.io/workflows/2462'

@pytest.fixture
def mock_extraction_result(mock_layer1_metadata, mock_layer2_workflow_json, mock_layer3_content):
    """Complete mock extraction result."""
    return {
        'workflow_id': '2462',
        'url': 'https://n8n.io/workflows/2462',
        'processing_time': 14.5,
        'quality_score': 85.3,
        'layers': {
            'layer1': {
                'success': True,
                'data': mock_layer1_metadata
            },
            'layer2': {
                'success': True,
                'node_count': 2,
                'connection_count': 1,
                'node_types': ['start', 'httpRequest'],
                'extraction_type': 'full',
                'fallback_used': False,
                'data': mock_layer2_workflow_json
            },
            'layer3': {
                'success': True,
                'data': mock_layer3_content
            }
        }
    }

# ============================================================================
# ASYNC TEST HELPERS
# ============================================================================

@pytest.fixture
def event_loop():
    """Create an instance of the default event loop for the test session."""
    import asyncio
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

# ============================================================================
# PATCH DECORATORS
# ============================================================================

@pytest.fixture
def mock_aiohttp():
    """Patch aiohttp for all tests."""
    with patch('aiohttp.ClientSession') as mock:
        yield mock

@pytest.fixture
def mock_playwright():
    """Patch playwright for all tests."""
    with patch('playwright.async_api.async_playwright') as mock:
        mock_instance = AsyncMock()
        mock.return_value.__aenter__.return_value = mock_instance
        yield mock_instance

@pytest.fixture
def mock_youtube_api():
    """Patch YouTube API for transcript tests."""
    with patch('youtube_transcript_api.YouTubeTranscriptApi') as mock:
        mock.get_transcript.return_value = [
            {'text': 'Welcome to this tutorial', 'start': 0.0, 'duration': 5.0}
        ]
        yield mock
```

### **Step 5: Set Up CI/CD (30 minutes)**

Create `.github/workflows/tests.yml`:

```yaml
name: Unit Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.9, 3.10, 3.11]

    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Cache pip dependencies
      uses: actions/cache@v3
      with:
        path: ~/.cache/pip
        key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}
        restore-keys: |
          ${{ runner.os }}-pip-
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest pytest-cov pytest-asyncio pytest-mock
    
    - name: Run tests
      run: |
        pytest --cov=src --cov-report=xml --cov-report=html --junitxml=test-results.xml
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        flags: unittests
        name: codecov-umbrella
        fail_ci_if_error: false
    
    - name: Upload test results
      uses: actions/upload-artifact@v3
      if: always()
      with:
        name: test-results-${{ matrix.python-version }}
        path: |
          test-results.xml
          htmlcov/
    
    - name: Fail if coverage < 90%
      run: |
        pytest --cov=src --cov-fail-under=90 --cov-report=term
```

---

## 🧪 **PHASE 2: EXTRACTOR TESTS (4 HOURS)**

### **Layer 1 Metadata Extractor Tests (1 hour)**

Create `tests/unit/test_layer1_metadata.py`:

```python
"""
Unit tests for Layer 1 Metadata Extractor.

Tests PageMetadataExtractor with mocked HTTP responses.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from src.extractors.layer1_metadata import PageMetadataExtractor


class TestPageMetadataExtractor:
    """Tests for PageMetadataExtractor."""
    
    @pytest.fixture
    def extractor(self):
        """Create extractor instance."""
        return PageMetadataExtractor()
    
    # ========================================================================
    # SUCCESS CASES (8 tests)
    # ========================================================================
    
    @patch('aiohttp.ClientSession.get')
    async def test_extract_basic_metadata(
        self, 
        mock_get, 
        extractor, 
        mock_aiohttp_response,
        mock_layer1_metadata
    ):
        """Test successful metadata extraction."""
        # Mock response
        mock_response = mock_aiohttp_response
        mock_response.text = AsyncMock(return_value=self._create_mock_html(mock_layer1_metadata))
        mock_get.return_value.__aenter__.return_value = mock_response
        
        # Test extraction
        result = await extractor.extract('2462', 'https://n8n.io/workflows/2462')
        
        # Assertions
        assert result['success'] == True
        assert result['title'] == 'Test Workflow'
        assert result['author']['name'] == 'Test Author'
        assert result['categories'] == ['Sales', 'Marketing']
        assert result['views'] == 1000
    
    @patch('aiohttp.ClientSession.get')
    async def test_extract_author_info(self, mock_get, extractor, mock_aiohttp_response):
        """Test author information extraction."""
        metadata = {
            'title': 'Test',
            'author': {'name': 'John Doe', 'url': 'https://example.com/john'},
            'categories': [],
            'views': 100
        }
        
        mock_response = mock_aiohttp_response
        mock_response.text = AsyncMock(return_value=self._create_mock_html(metadata))
        mock_get.return_value.__aenter__.return_value = mock_response
        
        result = await extractor.extract('2462', 'https://n8n.io/workflows/2462')
        
        assert result['success'] == True
        assert result['author']['name'] == 'John Doe'
        assert result['author']['url'] == 'https://example.com/john'
    
    @patch('aiohttp.ClientSession.get')
    async def test_extract_categories(self, mock_get, extractor, mock_aiohttp_response):
        """Test categories extraction."""
        metadata = {
            'title': 'Test',
            'author': {'name': 'Test'},
            'categories': ['Sales', 'Marketing', 'Automation'],
            'views': 100
        }
        
        mock_response = mock_aiohttp_response
        mock_response.text = AsyncMock(return_value=self._create_mock_html(metadata))
        mock_get.return_value.__aenter__.return_value = mock_response
        
        result = await extractor.extract('2462', 'https://n8n.io/workflows/2462')
        
        assert result['success'] == True
        assert len(result['categories']) == 3
        assert 'Sales' in result['categories']
        assert 'Marketing' in result['categories']
        assert 'Automation' in result['categories']
    
    @patch('aiohttp.ClientSession.get')
    async def test_extract_view_counts(self, mock_get, extractor, mock_aiohttp_response):
        """Test view and share count extraction."""
        metadata = {
            'title': 'Test',
            'author': {'name': 'Test'},
            'categories': [],
            'views': 5000,
            'shares': 250
        }
        
        mock_response = mock_aiohttp_response
        mock_response.text = AsyncMock(return_value=self._create_mock_html(metadata))
        mock_get.return_value.__aenter__.return_value = mock_response
        
        result = await extractor.extract('2462', 'https://n8n.io/workflows/2462')
        
        assert result['success'] == True
        assert result['views'] == 5000
        assert result['shares'] == 250
    
    # ========================================================================
    # ERROR CASES (8 tests)
    # ========================================================================
    
    @patch('aiohttp.ClientSession.get')
    async def test_extract_with_404(self, mock_get, extractor):
        """Test handling of 404 errors."""
        mock_response = AsyncMock()
        mock_response.status = 404
        mock_response.text = AsyncMock(return_value='Not Found')
        mock_get.return_value.__aenter__.return_value = mock_response
        
        result = await extractor.extract('9999', 'https://n8n.io/workflows/9999')
        
        assert result['success'] == False
        assert '404' in result['error']
    
    @patch('aiohttp.ClientSession.get')
    async def test_extract_with_timeout(self, mock_get, extractor):
        """Test handling of timeout errors."""
        mock_get.side_effect = asyncio.TimeoutError("Request timeout")
        
        result = await extractor.extract('2462', 'https://n8n.io/workflows/2462')
        
        assert result['success'] == False
        assert 'timeout' in result['error'].lower()
    
    @patch('aiohttp.ClientSession.get')
    async def test_extract_with_invalid_html(self, mock_get, extractor, mock_aiohttp_response):
        """Test handling of invalid HTML."""
        mock_response = mock_aiohttp_response
        mock_response.text = AsyncMock(return_value='<html><body>Invalid content</body></html>')
        mock_get.return_value.__aenter__.return_value = mock_response
        
        result = await extractor.extract('2462', 'https://n8n.io/workflows/2462')
        
        # Should still succeed but with minimal data
        assert result['success'] == True
        assert result['title'] is None or result['title'] == ''
    
    @patch('aiohttp.ClientSession.get')
    async def test_extract_with_network_error(self, mock_get, extractor):
        """Test handling of network errors."""
        mock_get.side_effect = Exception("Network error")
        
        result = await extractor.extract('2462', 'https://n8n.io/workflows/2462')
        
        assert result['success'] == False
        assert 'network' in result['error'].lower() or 'error' in result['error'].lower()
    
    # ========================================================================
    # EDGE CASES (4 tests)
    # ========================================================================
    
    @patch('aiohttp.ClientSession.get')
    async def test_extract_minimal_workflow(self, mock_get, extractor, mock_aiohttp_response):
        """Test extraction of minimal workflow data."""
        minimal_metadata = {
            'title': 'Minimal',
            'author': {'name': 'User'},
            'categories': [],
            'views': 1
        }
        
        mock_response = mock_aiohttp_response
        mock_response.text = AsyncMock(return_value=self._create_mock_html(minimal_metadata))
        mock_get.return_value.__aenter__.return_value = mock_response
        
        result = await extractor.extract('2462', 'https://n8n.io/workflows/2462')
        
        assert result['success'] == True
        assert result['title'] == 'Minimal'
        assert result['categories'] == []
        assert result['views'] == 1
    
    @patch('aiohttp.ClientSession.get')
    async def test_extract_workflow_without_author(self, mock_get, extractor, mock_aiohttp_response):
        """Test extraction when author info is missing."""
        metadata = {
            'title': 'Test',
            'author': None,
            'categories': ['Sales'],
            'views': 100
        }
        
        mock_response = mock_aiohttp_response
        mock_response.text = AsyncMock(return_value=self._create_mock_html(metadata))
        mock_get.return_value.__aenter__.return_value = mock_response
        
        result = await extractor.extract('2462', 'https://n8n.io/workflows/2462')
        
        assert result['success'] == True
        assert result['author'] is None or result['author'] == {}
    
    def _create_mock_html(self, metadata):
        """Create mock HTML with metadata."""
        return f"""
        <html>
        <head>
            <title>{metadata.get('title', '')}</title>
            <meta name="description" content="{metadata.get('description', '')}">
        </head>
        <body>
            <div class="workflow-meta">
                <h1>{metadata.get('title', '')}</h1>
                <div class="author">{metadata.get('author', {}).get('name', '')}</div>
                <div class="categories">{','.join(metadata.get('categories', []))}</div>
                <div class="views">{metadata.get('views', 0)}</div>
                <div class="shares">{metadata.get('shares', 0)}</div>
            </div>
        </body>
        </html>
        """
```

---

## 📊 **PHASE 3: COVERAGE & CI (2 HOURS)**

### **Coverage Analysis Commands:**

```bash
# Run tests with coverage
pytest --cov=src --cov-report=html --cov-report=term

# View coverage report
open htmlcov/index.html

# Check specific module coverage
pytest --cov=src.extractors --cov-report=term-missing

# Generate coverage badge
coverage-badge -o coverage.svg
```

### **Coverage Targets by Module:**

- `src/extractors/layer1_metadata.py`: 95%+
- `src/extractors/layer2_json.py`: 95%+
- `src/extractors/layer3_content.py`: 95%+
- `src/extractors/multimodal.py`: 90%+
- `src/extractors/transcripts.py`: 90%+
- `src/validators/quality.py`: 90%+

### **Documentation Template:**

Create `docs/testing.md`:

```markdown
# Testing Guide

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/unit/test_layer2_json.py -v

# Run tests matching pattern
pytest -k "test_extract_success" -v
```

## Test Structure

- `tests/unit/` - Unit tests (100+ tests)
- `tests/integration/` - Integration tests
- `tests/conftest.py` - Shared fixtures

## Coverage

- Target: 90%+ overall coverage
- Individual modules: 90-95% coverage
- View report: `htmlcov/index.html`

## CI/CD

Tests run automatically on:
- Push to main/develop
- Pull requests
- Multiple Python versions (3.9, 3.10, 3.11)
```

---

## ✅ **SUCCESS VALIDATION**

### **Final Checklist:**

- [ ] 100+ tests implemented across 6 files
- [ ] All tests passing (100% pass rate)
- [ ] 90%+ code coverage achieved
- [ ] Test execution <2 minutes
- [ ] Mock-based testing (no real API calls)
- [ ] CI/CD integration working
- [ ] Documentation complete
- [ ] Performance targets met

### **Validation Commands:**

```bash
# Run full test suite
pytest --cov=src --cov-report=html --cov-report=term

# Check coverage threshold
pytest --cov=src --cov-fail-under=90

# Performance test
time pytest --cov=src --cov-report=term

# Verify no external calls
grep -r "n8n.io" tests/ || echo "No external calls found"
```

---

**🎯 Ready to implement comprehensive unit testing suite!**

---

*Implementation Guide v1.0*  
*Created: October 11, 2025, 12:40 PM*  
*Author: RND Manager*  
*For: Dev2*






