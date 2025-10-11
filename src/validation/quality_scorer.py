"""
Quality Scoring System - SCRAPE-004
Calculates overall quality scores for workflows based on all validation layers
"""

from typing import Dict, Optional, List
import logging

logger = logging.getLogger(__name__)


class QualityScorer:
    """Calculates quality scores for workflows based on validation results."""
    
    # Weight distribution for scoring algorithm
    WEIGHTS = {
        'layer1': 0.20,  # Metadata: 20%
        'layer2': 0.30,  # JSON Structure: 30%
        'layer3': 0.40,  # Content Quality: 40%
        'consistency': 0.10  # Cross-layer Consistency: 10%
    }
    
    # Classification thresholds
    CLASSIFICATIONS = {
        'Excellent': 90,
        'Good': 75,
        'Fair': 60,
        'Poor': 0
    }
    
    def __init__(self):
        """Initialize quality scorer."""
        logger.info("Quality Scorer initialized")
    
    def calculate_score(self, layer1_result: Optional[Dict] = None,
                       layer2_result: Optional[Dict] = None,
                       layer3_result: Optional[Dict] = None) -> Dict:
        """
        Calculate overall quality score from validation results.
        
        Args:
            layer1_result: Layer 1 validation result with 'score' and 'issues'
            layer2_result: Layer 2 validation result with 'score' and 'issues'
            layer3_result: Layer 3 validation result with 'score' and 'issues'
            
        Returns:
            dict with:
                - overall_score: float (0-100)
                - classification: str
                - layer1_score: float or None
                - layer2_score: float or None
                - layer3_score: float or None
                - consistency_score: float
                - total_issues: int
        """
        # Get individual scores (default to 0 if not provided)
        layer1_score = layer1_result.get('score', 0) if layer1_result else 0
        layer2_score = layer2_result.get('score', 0) if layer2_result else 0
        layer3_score = layer3_result.get('score', 0) if layer3_result else 0
        
        # Calculate consistency score
        consistency_score = self._calculate_consistency(
            layer1_result, layer2_result, layer3_result
        )
        
        # Calculate weighted overall score
        overall_score = (
            layer1_score * self.WEIGHTS['layer1'] +
            layer2_score * self.WEIGHTS['layer2'] +
            layer3_score * self.WEIGHTS['layer3'] +
            consistency_score * self.WEIGHTS['consistency']
        )
        
        # Classify quality
        classification = self._classify_quality(overall_score)
        
        # Count total issues
        total_issues = 0
        if layer1_result:
            total_issues += len(layer1_result.get('issues', []))
        if layer2_result:
            total_issues += len(layer2_result.get('issues', []))
        if layer3_result:
            total_issues += len(layer3_result.get('issues', []))
        
        return {
            'overall_score': round(overall_score, 1),
            'classification': classification,
            'layer1_score': round(layer1_score, 1) if layer1_score > 0 else None,
            'layer2_score': round(layer2_score, 1) if layer2_score > 0 else None,
            'layer3_score': round(layer3_score, 1) if layer3_score > 0 else None,
            'consistency_score': round(consistency_score, 1),
            'total_issues': total_issues
        }
    
    def _calculate_consistency(self, layer1_result: Optional[Dict],
                               layer2_result: Optional[Dict],
                               layer3_result: Optional[Dict]) -> float:
        """
        Calculate cross-layer consistency score.
        
        Args:
            layer1_result, layer2_result, layer3_result: Validation results
            
        Returns:
            float: Consistency score (0-100)
        """
        # Check which layers have data
        has_layer1 = layer1_result is not None and layer1_result.get('score', 0) > 0
        has_layer2 = layer2_result is not None and layer2_result.get('score', 0) > 0
        has_layer3 = layer3_result is not None and layer3_result.get('score', 0) > 0
        
        layers_present = sum([has_layer1, has_layer2, has_layer3])
        
        # Score based on data completeness across layers
        if layers_present == 3:
            return 100.0  # All three layers present - excellent consistency
        elif layers_present == 2:
            return 70.0   # Two layers present - good consistency
        elif layers_present == 1:
            return 40.0   # One layer present - fair consistency
        else:
            return 0.0    # No layers present - poor consistency
    
    def _classify_quality(self, score: float) -> str:
        """
        Classify quality based on score.
        
        Args:
            score: Overall quality score (0-100)
            
        Returns:
            str: Classification (Excellent/Good/Fair/Poor)
        """
        if score >= self.CLASSIFICATIONS['Excellent']:
            return 'Excellent'
        elif score >= self.CLASSIFICATIONS['Good']:
            return 'Good'
        elif score >= self.CLASSIFICATIONS['Fair']:
            return 'Fair'
        else:
            return 'Poor'
    
    def get_classification_summary(self, scores: List[Dict]) -> Dict:
        """
        Get summary statistics for a list of quality scores.
        
        Args:
            scores: List of quality score dicts
            
        Returns:
            dict with distribution and statistics
        """
        if not scores:
            return {
                'total': 0,
                'avg_score': 0.0,
                'excellent': 0,
                'good': 0,
                'fair': 0,
                'poor': 0
            }
        
        # Calculate distribution
        excellent = sum(1 for s in scores if s['classification'] == 'Excellent')
        good = sum(1 for s in scores if s['classification'] == 'Good')
        fair = sum(1 for s in scores if s['classification'] == 'Fair')
        poor = sum(1 for s in scores if s['classification'] == 'Poor')
        
        # Calculate average
        avg_score = sum(s['overall_score'] for s in scores) / len(scores)
        
        return {
            'total': len(scores),
            'avg_score': round(avg_score, 1),
            'excellent': excellent,
            'good': good,
            'fair': fair,
            'poor': poor,
            'excellent_pct': round(excellent / len(scores) * 100, 1),
            'good_pct': round(good / len(scores) * 100, 1),
            'fair_pct': round(fair / len(scores) * 100, 1),
            'poor_pct': round(poor / len(scores) * 100, 1)
        }


def main():
    """Test quality scorer."""
    scorer = QualityScorer()
    
    # Test with sample results
    layer1 = {'score': 85, 'issues': []}
    layer2 = {'score': 90, 'issues': []}
    layer3 = {'score': 75, 'issues': ['minor issue']}
    
    result = scorer.calculate_score(layer1, layer2, layer3)
    
    print(f"Overall Score: {result['overall_score']}")
    print(f"Classification: {result['classification']}")
    print(f"Consistency: {result['consistency_score']}")


if __name__ == "__main__":
    main()

