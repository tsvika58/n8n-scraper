"""
Layer 3 Content Quality Validator - SCRAPE-004
Validates content quality and completeness
"""

from typing import Dict, List
import logging

logger = logging.getLogger(__name__)


class Layer3Validator:
    """Validates Layer 3 content quality and completeness."""
    
    def __init__(self):
        """Initialize Layer 3 validator."""
        logger.info("Layer 3 Validator initialized")
    
    def validate(self, content_data: Dict) -> Dict:
        """
        Validate Layer 3 content quality.
        
        Args:
            content_data: Layer 3 content dict
            
        Returns:
            dict with:
                - score: float (0-100)
                - issues: list of issue descriptions
                - valid: bool (score >= 70)
        """
        score = 0
        issues = []
        
        # Tutorial text validation (30 points)
        tutorial_text = content_data.get('tutorial_text', '')
        if not tutorial_text:
            issues.append("Tutorial text missing")
        elif len(tutorial_text) < 100:
            issues.append("Tutorial text too short (minimum 100 characters)")
            score += 10
        elif len(tutorial_text) < 200:
            issues.append("Tutorial text short (recommended 200+ characters)")
            score += 20
        else:
            score += 30
        
        # Tutorial sections validation (25 points)
        sections = content_data.get('tutorial_sections', [])
        if not isinstance(sections, list) or len(sections) == 0:
            issues.append("No tutorial sections extracted")
        elif len(sections) < 2:
            issues.append("Only one tutorial section (recommended 3+)")
            score += 10
        elif len(sections) < 3:
            issues.append("Limited tutorial sections (recommended 3+)")
            score += 15
        else:
            score += 25
        
        # Image URLs validation (20 points)
        images = content_data.get('images', [])
        if not isinstance(images, list) or len(images) == 0:
            issues.append("No images extracted")
        else:
            valid_images = 0
            for img in images:
                if isinstance(img, dict) and img.get('url', '').startswith('http'):
                    valid_images += 1
            
            if valid_images == 0:
                issues.append("No valid image URLs found")
            elif valid_images < len(images):
                issues.append(f"Some invalid image URLs ({valid_images}/{len(images)} valid)")
                score += 10
            else:
                score += 20
        
        # Structure completeness validation (15 points)
        required_fields = ['title', 'description', 'steps']
        missing_fields = [field for field in required_fields if not content_data.get(field)]
        
        if not missing_fields:
            score += 15
        elif len(missing_fields) == 1:
            issues.append(f"Missing field: {missing_fields[0]}")
            score += 10
        else:
            issues.append(f"Missing required fields: {', '.join(missing_fields)}")
            score += 5
        
        # Step-by-step content validation (10 points)
        steps = content_data.get('steps', [])
        if isinstance(steps, list) and len(steps) >= 3:
            score += 10
        elif isinstance(steps, list) and len(steps) > 0:
            issues.append(f"Limited step-by-step content ({len(steps)} steps, recommended 3+)")
            score += 5
        else:
            issues.append("No step-by-step content extracted")
        
        # Calculate validity
        valid = score >= 70
        
        return {
            'score': min(score, 100),
            'issues': issues,
            'valid': valid,
            'layer': 'layer3'
        }


def main():
    """Test Layer 3 validator."""
    validator = Layer3Validator()
    
    # Test with good content
    good_content = {
        'title': 'AI Agent Chat',
        'description': 'Complete tutorial for building AI chat agents',
        'tutorial_text': 'This comprehensive tutorial will guide you through building a sophisticated AI-powered chat agent using n8n workflows. You will learn how to integrate OpenAI, handle conversations, and deploy production-ready chat solutions.',
        'tutorial_sections': [
            'Introduction',
            'Setup Requirements',
            'Building the Workflow',
            'Testing and Deployment'
        ],
        'images': [
            {'url': 'https://n8n.io/images/workflow1.png', 'alt': 'Workflow'},
            {'url': 'https://n8n.io/images/workflow2.png', 'alt': 'Nodes'}
        ],
        'steps': [
            'Set up OpenAI credentials',
            'Create chat trigger node',
            'Configure AI agent',
            'Test workflow',
            'Deploy to production'
        ]
    }
    
    result = validator.validate(good_content)
    print(f"Good Content Score: {result['score']}")
    print(f"Valid: {result['valid']}")
    print(f"Issues: {len(result['issues'])}")


if __name__ == "__main__":
    main()





