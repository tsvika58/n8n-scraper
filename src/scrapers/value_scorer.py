"""
Smart Value Scoring System for N8N Workflow Prioritization

This module implements the intelligent value scoring algorithm that ranks workflows
0-100 based on engagement, complexity, quality, recency, and business value.
"""

from datetime import datetime, timezone
from typing import Dict, Any, Optional
import math


class WorkflowValueScorer:
    """
    Intelligent workflow value scoring system.
    
    Scores workflows 0-100 based on:
    - Engagement (30%): Views, upvotes, shares
    - Complexity (20%): Node count (sweet spot: 5-15 nodes)
    - Quality (25%): Documentation completeness, structure
    - Recency (15%): Newer workflows preferred
    - Business Value (10%): Category relevance, use case clarity
    """
    
    def __init__(self):
        self.weights = {
            'engagement': 0.30,    # 30%
            'complexity': 0.20,    # 20%
            'quality': 0.25,       # 25%
            'recency': 0.15,       # 15%
            'business_value': 0.10 # 10%
        }
        
        # Business value categories (higher value = more important)
        self.business_categories = {
            'sales': 100,
            'marketing': 95,
            'crm': 90,
            'automation': 85,
            'data': 80,
            'integration': 75,
            'notification': 70,
            'productivity': 65,
            'social': 60,
            'other': 50
        }
    
    def calculate_score(self, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate comprehensive value score for a workflow.
        
        Args:
            workflow_data: Dictionary containing workflow metadata and metrics
            
        Returns:
            Dictionary with individual scores and total value score
        """
        try:
            # Extract metrics
            engagement_score = self._calculate_engagement_score(workflow_data)
            complexity_score = self._calculate_complexity_score(workflow_data)
            quality_score = self._calculate_quality_score(workflow_data)
            recency_score = self._calculate_recency_score(workflow_data)
            business_value_score = self._calculate_business_value_score(workflow_data)
            
            # Calculate weighted total
            total_score = (
                engagement_score * self.weights['engagement'] +
                complexity_score * self.weights['complexity'] +
                quality_score * self.weights['quality'] +
                recency_score * self.weights['recency'] +
                business_value_score * self.weights['business_value']
            )
            
            return {
                'total_score': round(total_score, 2),
                'engagement_score': round(engagement_score, 2),
                'complexity_score': round(complexity_score, 2),
                'quality_score': round(quality_score, 2),
                'recency_score': round(recency_score, 2),
                'business_value_score': round(business_value_score, 2),
                'weights': self.weights,
                'calculated_at': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            print(f"Error calculating value score: {e}")
            return {
                'total_score': 0.0,
                'engagement_score': 0.0,
                'complexity_score': 0.0,
                'quality_score': 0.0,
                'recency_score': 0.0,
                'business_value_score': 0.0,
                'error': str(e),
                'calculated_at': datetime.now(timezone.utc).isoformat()
            }
    
    def _calculate_engagement_score(self, data: Dict[str, Any]) -> float:
        """Calculate engagement score (0-100) based on views, shares, upvotes."""
        try:
            views = data.get('views', 0) or 0
            shares = data.get('shares', 0) or 0
            upvotes = data.get('upvotes', 0) or 0
            
            # Normalize views (log scale, max at 10,000 views = 100 points)
            views_score = min(100, (math.log10(views + 1) / math.log10(10001)) * 100)
            
            # Shares are worth 5x views
            shares_score = min(100, shares * 5)
            
            # Upvotes are worth 10x views
            upvotes_score = min(100, upvotes * 10)
            
            # Weighted combination
            engagement = (views_score * 0.6 + shares_score * 0.2 + upvotes_score * 0.2)
            return min(100, engagement)
            
        except Exception:
            return 0.0
    
    def _calculate_complexity_score(self, data: Dict[str, Any]) -> float:
        """Calculate complexity score (0-100) - sweet spot at 5-15 nodes."""
        try:
            node_count = data.get('node_count', 0) or 0
            
            # Sweet spot is 5-15 nodes (100 points)
            # Too simple (<5) or too complex (>20) gets lower scores
            if node_count == 0:
                return 0.0
            elif 5 <= node_count <= 15:
                return 100.0
            elif node_count < 5:
                # Linear increase from 0-5
                return (node_count / 5) * 80
            else:
                # Exponential decay for >15 nodes
                excess = node_count - 15
                penalty = min(90, excess * 5)
                return max(10, 100 - penalty)
                
        except Exception:
            return 0.0
    
    def _calculate_quality_score(self, data: Dict[str, Any]) -> float:
        """Calculate quality score (0-100) based on documentation and structure."""
        try:
            score = 0.0
            
            # Title quality (20 points)
            title = data.get('title', '')
            if title and len(title) > 10:
                score += 20
            
            # Description quality (30 points)
            description = data.get('description', '')
            if description:
                desc_length = len(description)
                if desc_length > 100:
                    score += 30
                elif desc_length > 50:
                    score += 20
                elif desc_length > 20:
                    score += 10
            
            # Use case clarity (25 points)
            use_case = data.get('use_case', '')
            if use_case and len(use_case) > 20:
                score += 25
            elif use_case:
                score += 10
            
            # Author information (15 points)
            author = data.get('author_name', '')
            if author:
                score += 15
            
            # Categories/tags (10 points)
            categories = data.get('categories', [])
            if categories and len(categories) > 0:
                score += 10
            
            return min(100, score)
            
        except Exception:
            return 0.0
    
    def _calculate_recency_score(self, data: Dict[str, Any]) -> float:
        """Calculate recency score (0-100) - newer workflows preferred."""
        try:
            created_at = data.get('workflow_created_at')
            if not created_at:
                return 50.0  # Default middle score if no date
            
            # Parse date
            if isinstance(created_at, str):
                created_date = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            else:
                created_date = created_at
            
            # Calculate days since creation
            now = datetime.now(timezone.utc)
            days_old = (now - created_date).days
            
            # Score based on age (newer = higher score)
            if days_old <= 30:      # Last month
                return 100.0
            elif days_old <= 90:    # Last 3 months
                return 85.0
            elif days_old <= 180:   # Last 6 months
                return 70.0
            elif days_old <= 365:   # Last year
                return 50.0
            elif days_old <= 730:   # Last 2 years
                return 30.0
            else:                   # Older than 2 years
                return 10.0
                
        except Exception:
            return 50.0  # Default middle score on error
    
    def _calculate_business_value_score(self, data: Dict[str, Any]) -> float:
        """Calculate business value score (0-100) based on category relevance."""
        try:
            categories = data.get('categories', [])
            if not categories:
                return 50.0  # Default middle score
            
            # Get the primary category
            primary_category = categories[0].lower() if isinstance(categories, list) else str(categories).lower()
            
            # Check for business value keywords
            business_keywords = [
                'sales', 'marketing', 'crm', 'automation', 'data', 'integration',
                'notification', 'productivity', 'social', 'ecommerce', 'analytics'
            ]
            
            max_score = 50.0  # Default
            for keyword in business_keywords:
                if keyword in primary_category:
                    max_score = self.business_categories.get(keyword, 75)
                    break
            
            return max_score
            
        except Exception:
            return 50.0  # Default middle score on error
    
    def rank_workflows(self, workflows: list) -> list:
        """
        Rank a list of workflows by their value scores.
        
        Args:
            workflows: List of workflow dictionaries with metadata
            
        Returns:
            List of workflows sorted by value score (highest first)
        """
        try:
            # Calculate scores for all workflows
            scored_workflows = []
            for workflow in workflows:
                score_data = self.calculate_score(workflow)
                workflow['value_score'] = score_data
                scored_workflows.append(workflow)
            
            # Sort by total score (highest first)
            scored_workflows.sort(key=lambda x: x['value_score']['total_score'], reverse=True)
            
            return scored_workflows
            
        except Exception as e:
            print(f"Error ranking workflows: {e}")
            return workflows  # Return original list on error
    
    def get_top_workflows(self, workflows: list, top_n: int = 100) -> list:
        """
        Get top N highest-value workflows.
        
        Args:
            workflows: List of workflow dictionaries
            top_n: Number of top workflows to return
            
        Returns:
            List of top N workflows by value score
        """
        ranked_workflows = self.rank_workflows(workflows)
        return ranked_workflows[:top_n]



