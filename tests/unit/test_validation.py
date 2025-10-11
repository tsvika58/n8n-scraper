"""
Unit tests for Validation & Quality Scoring System - SCRAPE-004
"""

import pytest
from src.validation.layer1_validator import Layer1Validator
from src.validation.layer2_validator import Layer2Validator
from src.validation.layer3_validator import Layer3Validator
from src.validation.quality_scorer import QualityScorer
from src.database.validation_schema import ValidationDatabase, QualityScore, ValidationIssue


class TestLayer1Validator:
    """Tests for Layer 1 metadata validator."""
    
    @pytest.fixture
    def validator(self):
        return Layer1Validator()
    
    def test_validator_initialization(self, validator):
        """Test validator initializes correctly."""
        assert validator is not None
    
    def test_validate_perfect_metadata(self, validator):
        """Test validation with perfect metadata."""
        metadata = {
            'title': 'Comprehensive AI Agent Workflow',
            'description': 'A detailed workflow for AI-powered customer service automation with multiple integrations',
            'primary_category': 'Sales',
            'secondary_categories': ['AI', 'Automation'],
            'node_tags': ['OpenAI', 'Telegram', 'Gmail'],
            'general_tags': ['automation', 'ai', 'chat'],
            'difficulty': 'intermediate',
            'author': 'n8n Team',
            'views_count': 1500,
            'upvotes_count': 45,
            'created_date': '2024-01-15',
            'updated_date': '2024-02-10'
        }
        
        result = validator.validate(metadata)
        
        assert result['score'] == 100
        assert result['valid'] is True
        assert len(result['issues']) == 0
    
    def test_validate_poor_metadata(self, validator):
        """Test validation with poor metadata."""
        metadata = {
            'title': 'Test',
            'description': 'Short'
        }
        
        result = validator.validate(metadata)
        
        assert result['score'] < 50
        assert result['valid'] is False
        assert len(result['issues']) > 5
    
    def test_validate_missing_title(self, validator):
        """Test validation flags missing title."""
        metadata = {'description': 'Good description here with enough length'}
        
        result = validator.validate(metadata)
        
        assert 'Title' in str(result['issues'])
        assert result['score'] < 100
    
    def test_validate_short_description(self, validator):
        """Test validation flags short description."""
        metadata = {
            'title': 'Good Title Here',
            'description': 'Too short'
        }
        
        result = validator.validate(metadata)
        
        assert any('Description' in issue for issue in result['issues'])
    
    def test_validate_no_tags(self, validator):
        """Test validation flags missing tags."""
        metadata = {
            'title': 'Good Title',
            'description': 'Good description with sufficient length',
            'node_tags': [],
            'general_tags': []
        }
        
        result = validator.validate(metadata)
        
        assert any('tags' in issue.lower() for issue in result['issues'])


class TestLayer2Validator:
    """Tests for Layer 2 JSON structure validator."""
    
    @pytest.fixture
    def validator(self):
        return Layer2Validator()
    
    def test_validator_initialization(self, validator):
        """Test validator initializes correctly."""
        assert validator is not None
    
    def test_validate_perfect_json(self, validator):
        """Test validation with perfect workflow JSON."""
        workflow_json = {
            'workflow': {
                'nodes': [
                    {'id': '1', 'name': 'Start', 'type': 'n8n-nodes-base.start', 'position': [0, 0]},
                    {'id': '2', 'name': 'HTTP', 'type': 'n8n-nodes-base.httpRequest', 'position': [200, 0]},
                    {'id': '3', 'name': 'Set', 'type': 'n8n-nodes-base.set', 'position': [400, 0]}
                ],
                'connections': {
                    'Start': {'main': [[{'node': 'HTTP', 'type': 'main', 'index': 0}]]},
                    'HTTP': {'main': [[{'node': 'Set', 'type': 'main', 'index': 0}]]}
                },
                'meta': {'instanceId': 'test123'}
            }
        }
        
        result = validator.validate(workflow_json)
        
        assert result['score'] == 100
        assert result['valid'] is True
        assert len(result['issues']) == 0
    
    def test_validate_empty_json(self, validator):
        """Test validation with empty/invalid JSON."""
        result = validator.validate({})
        
        assert result['score'] < 50
        assert result['valid'] is False
        assert len(result['issues']) > 0
    
    def test_validate_missing_nodes(self, validator):
        """Test validation flags missing nodes."""
        workflow_json = {
            'workflow': {
                'nodes': [],
                'connections': {}
            }
        }
        
        result = validator.validate(workflow_json)
        
        assert any('nodes' in issue.lower() for issue in result['issues'])
    
    def test_validate_invalid_node_structure(self, validator):
        """Test validation flags invalid node structure."""
        workflow_json = {
            'workflow': {
                'nodes': [
                    {'name': 'Missing ID'}  # Missing required 'id' and 'type'
                ],
                'connections': {}
            }
        }
        
        result = validator.validate(workflow_json)
        
        assert any('node' in issue.lower() for issue in result['issues'])


class TestLayer3Validator:
    """Tests for Layer 3 content quality validator."""
    
    @pytest.fixture
    def validator(self):
        return Layer3Validator()
    
    def test_validator_initialization(self, validator):
        """Test validator initializes correctly."""
        assert validator is not None
    
    def test_validate_perfect_content(self, validator):
        """Test validation with perfect content."""
        content = {
            'title': 'Complete Workflow Tutorial',
            'description': 'Comprehensive guide to building advanced workflows',
            'tutorial_text': 'This extensive tutorial provides step-by-step instructions for building sophisticated n8n workflows. You will learn best practices, common patterns, and advanced techniques that will make you proficient in workflow automation.',
            'tutorial_sections': ['Introduction', 'Prerequisites', 'Setup', 'Implementation', 'Testing'],
            'images': [
                {'url': 'https://n8n.io/img1.png', 'alt': 'Workflow'},
                {'url': 'https://n8n.io/img2.png', 'alt': 'Nodes'}
            ],
            'steps': ['Step 1', 'Step 2', 'Step 3', 'Step 4']
        }
        
        result = validator.validate(content)
        
        assert result['score'] == 100
        assert result['valid'] is True
        assert len(result['issues']) == 0
    
    def test_validate_missing_content(self, validator):
        """Test validation with missing content."""
        content = {}
        
        result = validator.validate(content)
        
        assert result['score'] < 40
        assert result['valid'] is False
        assert len(result['issues']) > 3
    
    def test_validate_short_tutorial_text(self, validator):
        """Test validation flags short tutorial text."""
        content = {
            'tutorial_text': 'Too short',
            'title': 'Test',
            'description': 'Test desc'
        }
        
        result = validator.validate(content)
        
        assert any('tutorial text' in issue.lower() for issue in result['issues'])


class TestQualityScorer:
    """Tests for quality scoring system."""
    
    @pytest.fixture
    def scorer(self):
        return QualityScorer()
    
    def test_scorer_initialization(self, scorer):
        """Test scorer initializes correctly."""
        assert scorer is not None
        assert scorer.WEIGHTS['layer1'] == 0.20
        assert scorer.WEIGHTS['layer2'] == 0.30
        assert scorer.WEIGHTS['layer3'] == 0.40
        assert scorer.WEIGHTS['consistency'] == 0.10
    
    def test_calculate_perfect_score(self, scorer):
        """Test score calculation with perfect results."""
        layer1 = {'score': 100, 'issues': []}
        layer2 = {'score': 100, 'issues': []}
        layer3 = {'score': 100, 'issues': []}
        
        result = scorer.calculate_score(layer1, layer2, layer3)
        
        assert result['overall_score'] == 100.0
        assert result['classification'] == 'Excellent'
        assert result['consistency_score'] == 100.0
    
    def test_calculate_good_score(self, scorer):
        """Test score calculation for 'Good' classification."""
        layer1 = {'score': 85, 'issues': []}
        layer2 = {'score': 80, 'issues': []}
        layer3 = {'score': 75, 'issues': []}
        
        result = scorer.calculate_score(layer1, layer2, layer3)
        
        assert 75 <= result['overall_score'] < 90
        assert result['classification'] == 'Good'
    
    def test_calculate_fair_score(self, scorer):
        """Test score calculation for 'Fair' classification."""
        layer1 = {'score': 70, 'issues': ['minor issue']}
        layer2 = {'score': 65, 'issues': ['minor issue']}
        layer3 = {'score': 60, 'issues': ['minor issue']}
        
        result = scorer.calculate_score(layer1, layer2, layer3)
        
        assert 60 <= result['overall_score'] < 75
        assert result['classification'] == 'Fair'
    
    def test_calculate_poor_score(self, scorer):
        """Test score calculation for 'Poor' classification."""
        layer1 = {'score': 40, 'issues': ['issue1', 'issue2']}
        layer2 = {'score': 30, 'issues': ['issue3']}
        layer3 = {'score': 20, 'issues': ['issue4', 'issue5']}
        
        result = scorer.calculate_score(layer1, layer2, layer3)
        
        assert result['overall_score'] < 60
        assert result['classification'] == 'Poor'
        assert result['total_issues'] == 5
    
    def test_calculate_with_missing_layers(self, scorer):
        """Test scoring with some layers missing."""
        layer1 = {'score': 90, 'issues': []}
        # layer2 and layer3 missing
        
        result = scorer.calculate_score(layer1, None, None)
        
        assert result['overall_score'] < 100
        assert result['layer1_score'] == 90.0
        assert result['layer2_score'] is None
        assert result['layer3_score'] is None
        assert result['consistency_score'] < 100  # Not all layers present
    
    def test_classify_excellent(self, scorer):
        """Test Excellent classification."""
        assert scorer._classify_quality(95) == 'Excellent'
        assert scorer._classify_quality(90) == 'Excellent'
    
    def test_classify_good(self, scorer):
        """Test Good classification."""
        assert scorer._classify_quality(85) == 'Good'
        assert scorer._classify_quality(75) == 'Good'
    
    def test_classify_fair(self, scorer):
        """Test Fair classification."""
        assert scorer._classify_quality(70) == 'Fair'
        assert scorer._classify_quality(60) == 'Fair'
    
    def test_classify_poor(self, scorer):
        """Test Poor classification."""
        assert scorer._classify_quality(50) == 'Poor'
        assert scorer._classify_quality(0) == 'Poor'
    
    def test_consistency_all_layers(self, scorer):
        """Test consistency score with all layers present."""
        layer1 = {'score': 80, 'issues': []}
        layer2 = {'score': 85, 'issues': []}
        layer3 = {'score': 90, 'issues': []}
        
        consistency = scorer._calculate_consistency(layer1, layer2, layer3)
        
        assert consistency == 100.0
    
    def test_consistency_two_layers(self, scorer):
        """Test consistency score with two layers present."""
        layer1 = {'score': 80, 'issues': []}
        layer2 = {'score': 85, 'issues': []}
        
        consistency = scorer._calculate_consistency(layer1, layer2, None)
        
        assert consistency == 70.0
    
    def test_consistency_one_layer(self, scorer):
        """Test consistency score with one layer present."""
        layer1 = {'score': 80, 'issues': []}
        
        consistency = scorer._calculate_consistency(layer1, None, None)
        
        assert consistency == 40.0
    
    def test_consistency_no_layers(self, scorer):
        """Test consistency score with no layers present."""
        consistency = scorer._calculate_consistency(None, None, None)
        
        assert consistency == 0.0


class TestValidationDatabase:
    """Tests for validation database operations."""
    
    @pytest.fixture
    def db(self, tmp_path):
        """Create temporary test database."""
        db_file = tmp_path / "test_validation.db"
        database = ValidationDatabase(str(db_file))
        database.create_tables()
        return database
    
    def test_database_initialization(self, db):
        """Test database initializes correctly."""
        assert db is not None
        assert db.Session is not None
    
    def test_create_tables(self, db):
        """Test tables are created."""
        stats = db.get_stats()
        assert stats['total_workflows'] == 0
    
    def test_store_quality_score(self, db):
        """Test storing quality score."""
        success = db.store_quality_score(
            workflow_id="1954",
            overall_score=85.5,
            classification="Good",
            layer1_score=90.0,
            layer2_score=85.0,
            layer3_score=80.0,
            consistency_score=100.0
        )
        
        assert success is True
        
        # Verify stored
        scores = db.get_quality_scores()
        assert len(scores) == 1
        assert scores[0]['overall_score'] == 85.5
    
    def test_store_validation_issue(self, db):
        """Test storing validation issue."""
        success = db.store_validation_issue(
            workflow_id="1954",
            layer="layer1",
            issue_type="missing_data",
            issue_description="Title too short",
            severity="warning"
        )
        
        assert success is True
        
        # Verify stored
        issues = db.get_validation_issues()
        assert len(issues) == 1
        assert issues[0]['workflow_id'] == "1954"
    
    def test_get_quality_scores_filtered(self, db):
        """Test getting quality scores filtered by classification."""
        # Store multiple scores
        db.store_quality_score("1", 95.0, "Excellent", 90.0, 95.0, 98.0, 100.0)
        db.store_quality_score("2", 80.0, "Good", 85.0, 80.0, 75.0, 100.0)
        db.store_quality_score("3", 65.0, "Fair", 70.0, 65.0, 60.0, 70.0)
        
        # Get all excellent
        excellent = db.get_quality_scores(classification="Excellent")
        assert len(excellent) == 1
        
        # Get all good
        good = db.get_quality_scores(classification="Good")
        assert len(good) == 1
    
    def test_get_stats(self, db):
        """Test getting validation statistics."""
        # Store scores
        db.store_quality_score("1", 95.0, "Excellent")
        db.store_quality_score("2", 80.0, "Good")
        db.store_quality_score("3", 65.0, "Fair")
        
        # Store issues
        db.store_validation_issue("1", "layer1", "minor", "Minor issue", "warning")
        db.store_validation_issue("2", "layer2", "major", "Major issue", "critical")
        
        stats = db.get_stats()
        
        assert stats['total_workflows'] == 3
        assert stats['excellent_count'] == 1
        assert stats['good_count'] == 1
        assert stats['fair_count'] == 1
        assert stats['total_issues'] == 2
        assert stats['critical_issues'] == 1
    
    def test_update_existing_score(self, db):
        """Test updating existing quality score."""
        # Store initial
        db.store_quality_score("1954", 80.0, "Good")
        
        # Update
        db.store_quality_score("1954", 90.0, "Excellent")
        
        # Should still be 1 record
        scores = db.get_quality_scores()
        assert len(scores) == 1
        assert scores[0]['overall_score'] == 90.0


class TestIntegratedValidation:
    """Tests for integrated validation workflow."""
    
    def test_complete_validation_flow(self):
        """Test complete validation flow with all validators."""
        # Initialize all validators
        layer1_val = Layer1Validator()
        layer2_val = Layer2Validator()
        layer3_val = Layer3Validator()
        scorer = QualityScorer()
        
        # Sample data
        metadata = {
            'title': 'AI Workflow',
            'description': 'Comprehensive AI automation workflow for customer service',
            'primary_category': 'Sales',
            'difficulty': 'intermediate',
            'author': 'n8n Team',
            'node_tags': ['AI', 'OpenAI'],
            'general_tags': ['automation']
        }
        
        workflow_json = {
            'workflow': {
                'nodes': [
                    {'id': '1', 'name': 'Start', 'type': 'start'},
                    {'id': '2', 'name': 'Process', 'type': 'function'}
                ],
                'connections': {'Start': {'main': [[{'node': 'Process'}]]}},
                'meta': {}
            }
        }
        
        content = {
            'title': 'Tutorial',
            'description': 'How to build this workflow',
            'tutorial_text': 'This tutorial shows you how to build an AI-powered workflow for customer service automation using n8n and OpenAI.',
            'tutorial_sections': ['Intro', 'Setup', 'Deploy'],
            'steps': ['Step 1', 'Step 2', 'Step 3']
        }
        
        # Run validations
        l1_result = layer1_val.validate(metadata)
        l2_result = layer2_val.validate(workflow_json)
        l3_result = layer3_val.validate(content)
        
        # Calculate quality score
        quality = scorer.calculate_score(l1_result, l2_result, l3_result)
        
        # Verify results
        assert l1_result['score'] > 0
        assert l2_result['score'] > 0
        assert l3_result['score'] > 0
        assert quality['overall_score'] > 0
        assert quality['classification'] in ['Excellent', 'Good', 'Fair', 'Poor']
    
    def test_layer1_medium_quality_metadata(self):
        """Test Layer 1 with medium quality metadata."""
        validator = Layer1Validator()
        
        metadata = {
            'title': 'Medium Workflow',
            'description': 'A medium length description that meets minimum requirements',
            'primary_category': 'Sales',
            'node_tags': ['Tag1'],
            'general_tags': [],
            'difficulty': 'beginner'
        }
        
        result = validator.validate(metadata)
        assert 30 < result['score'] < 80
    
    def test_layer2_with_one_node_type(self):
        """Test Layer 2 with limited node type diversity."""
        validator = Layer2Validator()
        
        workflow = {
            'workflow': {
                'nodes': [
                    {'id': '1', 'name': 'N1', 'type': 'same-type'},
                    {'id': '2', 'name': 'N2', 'type': 'same-type'}
                ],
                'connections': {},
                'meta': {}
            }
        }
        
        result = validator.validate(workflow)
        assert any('diversity' in issue.lower() for issue in result['issues'])
    
    def test_layer3_with_minimal_sections(self):
        """Test Layer 3 with minimal sections."""
        validator = Layer3Validator()
        
        content = {
            'title': 'Test',
            'description': 'Test desc',
            'tutorial_text': 'Short tutorial text that meets minimum length requirements for basic validation testing.',
            'tutorial_sections': ['Section 1'],
            'steps': ['Step 1']
        }
        
        result = validator.validate(content)
        assert result['score'] < 100
        assert any('section' in issue.lower() for issue in result['issues'])
    
    def test_scorer_get_classification_summary(self):
        """Test classification summary calculation."""
        scorer = QualityScorer()
        
        scores = [
            {'overall_score': 95, 'classification': 'Excellent'},
            {'overall_score': 92, 'classification': 'Excellent'},
            {'overall_score': 80, 'classification': 'Good'},
            {'overall_score': 65, 'classification': 'Fair'},
            {'overall_score': 45, 'classification': 'Poor'}
        ]
        
        summary = scorer.get_classification_summary(scores)
        
        assert summary['total'] == 5
        assert summary['excellent'] == 2
        assert summary['good'] == 1
        assert summary['fair'] == 1
        assert summary['poor'] == 1
        assert summary['avg_score'] > 0
    
    def test_scorer_empty_scores_list(self):
        """Test classification summary with empty list."""
        scorer = QualityScorer()
        
        summary = scorer.get_classification_summary([])
        
        assert summary['total'] == 0
        assert summary['avg_score'] == 0.0

