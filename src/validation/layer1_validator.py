"""
Layer 1 Metadata Validator - SCRAPE-004
Validates metadata completeness and quality
"""

from typing import Dict, List
import logging

logger = logging.getLogger(__name__)


class Layer1Validator:
    """Validates Layer 1 metadata completeness and quality."""
    
    def __init__(self):
        """Initialize Layer 1 validator."""
        logger.info("Layer 1 Validator initialized")
    
    def validate(self, metadata: Dict) -> Dict:
        """
        Validate Layer 1 metadata.
        
        Args:
            metadata: Layer 1 metadata dict
            
        Returns:
            dict with:
                - score: float (0-100)
                - issues: list of issue descriptions
                - valid: bool (score >= 80)
        """
        score = 0
        issues = []
        
        # Title validation (15 points)
        title = metadata.get('title', '')
        if not title or len(title) < 5:
            issues.append("Title missing or too short (minimum 5 characters)")
        elif len(title) < 10:
            issues.append("Title very short (recommended 10+ characters)")
            score += 10
        else:
            score += 15
        
        # Description validation (15 points)
        description = metadata.get('description', '')
        if not description or len(description) < 20:
            issues.append("Description missing or too short (minimum 20 characters)")
        elif len(description) < 50:
            issues.append("Description short (recommended 50+ characters)")
            score += 10
        else:
            score += 15
        
        # Categories validation (15 points)
        primary_category = metadata.get('primary_category', '')
        secondary_categories = metadata.get('secondary_categories', [])
        if not primary_category or primary_category == 'Uncategorized':
            issues.append("Primary category not assigned")
        else:
            score += 10
        
        if isinstance(secondary_categories, list) and len(secondary_categories) > 0:
            score += 5
        
        # Tags validation (15 points)
        node_tags = metadata.get('node_tags', [])
        general_tags = metadata.get('general_tags', [])
        total_tags = len(node_tags) + len(general_tags)
        
        if total_tags == 0:
            issues.append("No tags assigned")
        elif total_tags == 1:
            issues.append("Only one tag (recommended 2+ tags)")
            score += 8
        else:
            score += 15
        
        # Difficulty validation (10 points)
        difficulty = metadata.get('difficulty', '')
        if not difficulty:
            issues.append("Difficulty level not set")
        elif difficulty in ['beginner', 'intermediate', 'advanced']:
            score += 10
        else:
            issues.append(f"Unknown difficulty level: {difficulty}")
            score += 5
        
        # Author validation (10 points)
        author = metadata.get('author', '')
        if not author or author == 'Unknown Author':
            issues.append("Author not identified")
        else:
            score += 10
        
        # Engagement metrics validation (10 points)
        views = metadata.get('views_count', 0)
        upvotes = metadata.get('upvotes_count', 0)
        if views > 0 or upvotes > 0:
            score += 10
        else:
            issues.append("No engagement metrics available")
        
        # Dates validation (10 points)
        created = metadata.get('created_date', '')
        updated = metadata.get('updated_date', '')
        if created and updated:
            score += 10
        else:
            issues.append("Missing creation or update dates")
        
        # Calculate validity
        valid = score >= 80
        
        return {
            'score': min(score, 100),
            'issues': issues,
            'valid': valid,
            'layer': 'layer1'
        }


def main():
    """Test Layer 1 validator."""
    validator = Layer1Validator()
    
    # Test with good metadata
    good_metadata = {
        'title': 'AI Agent Chat Workflow',
        'description': 'A comprehensive workflow for AI-powered chat interactions with customers',
        'primary_category': 'Sales',
        'secondary_categories': ['AI', 'Chat'],
        'node_tags': ['OpenAI', 'Telegram'],
        'general_tags': ['automation', 'ai'],
        'difficulty': 'intermediate',
        'author': 'n8n Team',
        'views_count': 1500,
        'upvotes_count': 45,
        'created_date': '2024-01-15',
        'updated_date': '2024-02-10'
    }
    
    result = validator.validate(good_metadata)
    print(f"Score: {result['score']}")
    print(f"Valid: {result['valid']}")
    print(f"Issues: {len(result['issues'])}")
    
    # Test with poor metadata
    poor_metadata = {
        'title': 'Test',
        'description': 'Short',
        'primary_category': 'Uncategorized'
    }
    
    result2 = validator.validate(poor_metadata)
    print(f"\nPoor metadata score: {result2['score']}")
    print(f"Issues: {result2['issues']}")


if __name__ == "__main__":
    main()





