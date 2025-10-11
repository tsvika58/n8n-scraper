"""
Integration tests for Validation System - SCRAPE-004
Tests with real data from database
"""

import pytest
from src.validation.layer1_validator import Layer1Validator
from src.validation.layer2_validator import Layer2Validator
from src.validation.layer3_validator import Layer3Validator
from src.validation.quality_scorer import QualityScorer
from src.database.validation_schema import ValidationDatabase


class TestValidationIntegration:
    """Integration tests for validation system."""
    
    def test_end_to_end_validation_pipeline(self, tmp_path):
        """Test complete validation pipeline."""
        # Initialize all components
        layer1_val = Layer1Validator()
        layer2_val = Layer2Validator()
        layer3_val = Layer3Validator()
        scorer = QualityScorer()
        
        db_file = tmp_path / "test_integration.db"
        db = ValidationDatabase(str(db_file))
        db.create_tables()
        
        # Sample workflow data
        metadata = {
            'title': 'Sales Automation Workflow',
            'description': 'Automated sales workflow with CRM integration and email notifications',
            'primary_category': 'Sales',
            'node_tags': ['Salesforce', 'Gmail'],
            'difficulty': 'intermediate',
            'author': 'Community'
        }
        
        workflow_json = {
            'workflow': {
                'nodes': [
                    {'id': '1', 'name': 'Trigger', 'type': 'webhook'},
                    {'id': '2', 'name': 'CRM', 'type': 'salesforce'}
                ],
                'connections': {'Trigger': {'main': [[{'node': 'CRM'}]]}},
                'meta': {}
            }
        }
        
        # Run validation
        l1_result = layer1_val.validate(metadata)
        l2_result = layer2_val.validate(workflow_json)
        
        # Calculate quality
        quality = scorer.calculate_score(l1_result, l2_result, None)
        
        # Store in database
        success = db.store_quality_score(
            workflow_id="test_wf",
            overall_score=quality['overall_score'],
            classification=quality['classification'],
            layer1_score=quality['layer1_score'],
            layer2_score=quality['layer2_score']
        )
        
        assert success is True
        
        # Verify retrieval
        scores = db.get_quality_scores()
        assert len(scores) == 1
        assert scores[0]['workflow_id'] == "test_wf"
    
    def test_multi_workflow_validation(self, tmp_path):
        """Test validation of multiple workflows."""
        layer1_val = Layer1Validator()
        scorer = QualityScorer()
        
        # Multiple workflows
        workflows = [
            {'title': f'Workflow {i}', 'description': f'Description for workflow {i}' * 5}
            for i in range(5)
        ]
        
        scores = []
        for wf in workflows:
            result = layer1_val.validate(wf)
            quality = scorer.calculate_score(result, None, None)
            scores.append(quality)
        
        assert len(scores) == 5
        assert all(s['overall_score'] > 0 for s in scores)
    
    def test_quality_classification_distribution(self):
        """Test that quality classifications distribute correctly."""
        scorer = QualityScorer()
        
        # Create workflows with different quality levels
        excellent_data = {'score': 95, 'issues': []}
        good_data = {'score': 80, 'issues': []}
        fair_data = {'score': 65, 'issues': []}
        poor_data = {'score': 40, 'issues': []}
        
        scores = []
        for data in [excellent_data, good_data, fair_data, poor_data]:
            result = scorer.calculate_score(data, data, data)
            scores.append(result)
        
        # Verify classifications
        assert scores[0]['classification'] == 'Excellent'
        assert scores[1]['classification'] == 'Good'
        assert scores[2]['classification'] == 'Fair'
        assert scores[3]['classification'] == 'Poor'
    
    def test_issue_tracking_across_layers(self, tmp_path):
        """Test issue tracking across all validation layers."""
        db_file = tmp_path / "test_issues.db"
        db = ValidationDatabase(str(db_file))
        db.create_tables()
        
        # Store issues from different layers
        db.store_validation_issue("wf1", "layer1", "missing_data", "Title missing", "warning")
        db.store_validation_issue("wf1", "layer2", "invalid_format", "Invalid JSON", "critical")
        db.store_validation_issue("wf1", "layer3", "incomplete_content", "No images", "info")
        
        # Get all issues for workflow
        issues = db.get_validation_issues(workflow_id="wf1")
        
        assert len(issues) == 3
        assert any(i['layer'] == 'layer1' for i in issues)
        assert any(i['layer'] == 'layer2' for i in issues)
        assert any(i['layer'] == 'layer3' for i in issues)
    
    def test_validation_statistics(self, tmp_path):
        """Test validation statistics calculation."""
        db_file = tmp_path / "test_stats.db"
        db = ValidationDatabase(str(db_file))
        db.create_tables()
        
        # Store multiple scores
        db.store_quality_score("1", 95.0, "Excellent")
        db.store_quality_score("2", 92.0, "Excellent")
        db.store_quality_score("3", 82.0, "Good")
        db.store_quality_score("4", 68.0, "Fair")
        db.store_quality_score("5", 45.0, "Poor")
        
        stats = db.get_stats()
        
        assert stats['total_workflows'] == 5
        assert stats['excellent_count'] == 2
        assert stats['good_count'] == 1
        assert stats['fair_count'] == 1
        assert stats['poor_count'] == 1
        assert stats['avg_quality_score'] > 0





