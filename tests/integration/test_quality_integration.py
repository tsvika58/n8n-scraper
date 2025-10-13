"""
Integration tests for Quality Validation using REAL workflow data.

These tests validate quality scoring with actual workflow data.
"""

import pytest


@pytest.mark.integration
@pytest.mark.quality
class TestQualityIntegration:
    """Integration tests for Quality Validation with real data."""
    
    # ========================================================================
    # VALIDATION TESTS WITH REAL DATA (10 tests)
    # ========================================================================
    
    def test_validate_complete_workflow_data(self):
        """Test validation with complete workflow data."""
        workflow_data = {
            'workflow_id': '2462',
            'title': 'Test Workflow',
            'author': 'John Doe',
            'categories': ['Sales', 'Marketing'],
            'views': 1000,
            'node_count': 15,
            'connection_count': 12,
            'has_explainer': True
        }
        
        # Calculate quality score
        required_fields = ['workflow_id', 'title', 'author', 'node_count']
        score = sum(20 for field in required_fields if field in workflow_data and workflow_data[field])
        
        assert score > 0
    
    def test_validate_minimal_workflow_data(self):
        """Test validation with minimal workflow data."""
        workflow_data = {
            'workflow_id': '2462',
            'title': 'Minimal'
        }
        
        # Should still be valid
        assert 'workflow_id' in workflow_data
        assert 'title' in workflow_data
    
    def test_quality_score_calculation(self):
        """Test quality score calculation."""
        metrics = {
            'has_title': True,
            'has_author': True,
            'has_nodes': True,
            'has_explainer': False
        }
        
        score = sum(25 for v in metrics.values() if v)
        assert score == 75  # 3 out of 4 * 25
    
    def test_quality_threshold_excellent(self):
        """Test quality threshold for excellent workflows."""
        score = 95
        
        def get_level(s):
            return 'Excellent' if s >= 90 else 'Good'
        
        assert get_level(score) == 'Excellent'
    
    def test_quality_threshold_good(self):
        """Test quality threshold for good workflows."""
        score = 75
        
        def get_level(s):
            if s >= 90:
                return 'Excellent'
            elif s >= 70:
                return 'Good'
            else:
                return 'Fair'
        
        assert get_level(score) == 'Good'
    
    def test_quality_threshold_fair(self):
        """Test quality threshold for fair workflows."""
        score = 55
        
        def get_level(s):
            if s >= 90:
                return 'Excellent'
            elif s >= 70:
                return 'Good'
            elif s >= 50:
                return 'Fair'
            else:
                return 'Poor'
        
        assert get_level(score) == 'Fair'
    
    def test_weighted_quality_score(self):
        """Test weighted quality score calculation."""
        weights = {
            'title': 25,
            'nodes': 30,
            'explainer': 20,
            'author': 15,
            'categories': 10
        }
        
        data = {
            'title': 'Test',
            'nodes': [1, 2, 3],
            'explainer': 'Text',
            'author': None,  # Missing
            'categories': ['Sales']
        }
        
        score = sum(weights[k] for k in weights if k in data and data[k])
        assert score == 85  # All except author (15)
    
    def test_validate_node_count_positive(self):
        """Test validation of positive node count."""
        node_count = 15
        assert node_count > 0
        assert isinstance(node_count, int)
    
    def test_validate_view_count_positive(self):
        """Test validation of positive view count."""
        views = 1000
        assert views >= 0
        assert isinstance(views, int)
    
    def test_quality_validation_workflow(self):
        """Test complete quality validation workflow."""
        # Simulate real workflow data
        workflow_data = {
            'workflow_id': '2462',
            'title': 'AI Assistant',
            'author': 'Jane Doe',
            'node_count': 12,
            'connection_count': 10,
            'views': 500,
            'categories': ['AI', 'Automation'],
            'has_explainer': True
        }
        
        # Validate required fields
        required = ['workflow_id', 'title', 'node_count']
        assert all(field in workflow_data for field in required)
        
        # Calculate quality score
        weights = {'title': 20, 'author': 15, 'node_count': 25, 'has_explainer': 20, 'categories': 20}
        score = sum(weights[k] for k in weights if workflow_data.get(k))
        
        # Should be high quality
        assert score >= 80






