"""
Quality Scoring System - SCRAPE-004
Calculates overall quality scores for workflows based on all validation layers
"""

from typing import Dict, Optional, List
import logging

logger = logging.getLogger(__name__)


class QualityScorer:
    """Calculates quality scores for workflows based on validation results."""
    
    # Weight distribution for scoring algorithm (7 layers + consistency)
    WEIGHTS = {
        'layer1': 0.15,  # Metadata: 15%
        'layer2': 0.25,  # JSON Structure: 25%
        'layer3': 0.25,  # Content Quality: 25%
        'layer4': 0.10,  # Business Intelligence: 10%
        'layer5': 0.05,  # Community Data: 5%
        'layer6': 0.05,  # Technical Details: 5%
        'layer7': 0.05,  # Performance Analytics: 5%
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
                       layer3_result: Optional[Dict] = None,
                       layer4_result: Optional[Dict] = None,
                       layer5_result: Optional[Dict] = None,
                       layer6_result: Optional[Dict] = None,
                       layer7_result: Optional[Dict] = None) -> Dict:
        """
        Calculate overall quality score from validation results.
        
        Args:
            layer1_result: Layer 1 validation result with 'score' and 'issues'
            layer2_result: Layer 2 validation result with 'score' and 'issues'
            layer3_result: Layer 3 validation result with 'score' and 'issues'
            layer4_result: Layer 4 validation result with 'score' and 'issues'
            layer5_result: Layer 5 validation result with 'score' and 'issues'
            layer6_result: Layer 6 validation result with 'score' and 'issues'
            layer7_result: Layer 7 validation result with 'score' and 'issues'
            
        Returns:
            dict with:
                - overall_score: float (0-100)
                - classification: str
                - layer1_score: float or None
                - layer2_score: float or None
                - layer3_score: float or None
                - layer4_score: float or None
                - layer5_score: float or None
                - layer6_score: float or None
                - layer7_score: float or None
                - consistency_score: float
                - total_issues: int
        """
        # Get individual scores (default to 0 if not provided)
        layer1_score = layer1_result.get('score', 0) if layer1_result else 0
        layer2_score = layer2_result.get('score', 0) if layer2_result else 0
        layer3_score = layer3_result.get('score', 0) if layer3_result else 0
        layer4_score = layer4_result.get('score', 0) if layer4_result else 0
        layer5_score = layer5_result.get('score', 0) if layer5_result else 0
        layer6_score = layer6_result.get('score', 0) if layer6_result else 0
        layer7_score = layer7_result.get('score', 0) if layer7_result else 0
        
        # Calculate consistency score
        consistency_score = self._calculate_consistency(
            layer1_result, layer2_result, layer3_result, layer4_result,
            layer5_result, layer6_result, layer7_result
        )
        
        # Calculate weighted overall score
        overall_score = (
            layer1_score * self.WEIGHTS['layer1'] +
            layer2_score * self.WEIGHTS['layer2'] +
            layer3_score * self.WEIGHTS['layer3'] +
            layer4_score * self.WEIGHTS['layer4'] +
            layer5_score * self.WEIGHTS['layer5'] +
            layer6_score * self.WEIGHTS['layer6'] +
            layer7_score * self.WEIGHTS['layer7'] +
            consistency_score * self.WEIGHTS['consistency']
        )
        
        # Classify quality
        classification = self._classify_quality(overall_score)
        
        # Count total issues
        total_issues = 0
        for layer_result in [layer1_result, layer2_result, layer3_result, layer4_result, 
                             layer5_result, layer6_result, layer7_result]:
            if layer_result:
                total_issues += len(layer_result.get('issues', []))
        
        return {
            'overall_score': round(overall_score, 1),
            'classification': classification,
            'layer1_score': round(layer1_score, 1) if layer1_score > 0 else None,
            'layer2_score': round(layer2_score, 1) if layer2_score > 0 else None,
            'layer3_score': round(layer3_score, 1) if layer3_score > 0 else None,
            'layer4_score': round(layer4_score, 1) if layer4_score > 0 else None,
            'layer5_score': round(layer5_score, 1) if layer5_score > 0 else None,
            'layer6_score': round(layer6_score, 1) if layer6_score > 0 else None,
            'layer7_score': round(layer7_score, 1) if layer7_score > 0 else None,
            'consistency_score': round(consistency_score, 1),
            'total_issues': total_issues
        }
    
    def _calculate_consistency(self, layer1_result: Optional[Dict],
                               layer2_result: Optional[Dict],
                               layer3_result: Optional[Dict],
                               layer4_result: Optional[Dict] = None,
                               layer5_result: Optional[Dict] = None,
                               layer6_result: Optional[Dict] = None,
                               layer7_result: Optional[Dict] = None) -> float:
        """
        Calculate cross-layer consistency score.
        
        Args:
            layer1-7_result: Validation results for all layers
            
        Returns:
            float: Consistency score (0-100)
        """
        # Check which layers have data
        layers_with_data = sum([
            1 for result in [layer1_result, layer2_result, layer3_result, 
                           layer4_result, layer5_result, layer6_result, layer7_result]
            if result is not None and result.get('score', 0) > 0
        ])
        
        # Score based on data completeness across all 7 layers
        if layers_with_data >= 6:
            return 100.0  # 6-7 layers present - excellent consistency
        elif layers_with_data >= 4:
            return 80.0   # 4-5 layers present - good consistency
        elif layers_with_data >= 3:
            return 60.0   # 3 layers present - fair consistency
        elif layers_with_data >= 2:
            return 40.0   # 2 layers present - poor consistency
        elif layers_with_data == 1:
            return 20.0   # 1 layer present - very poor consistency
        else:
            return 0.0    # No layers present - no consistency
    
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

