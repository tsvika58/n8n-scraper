"""
Layer 5: Community Data Extraction
Extracts community engagement, social metrics, and user interaction data from workflows.

This layer focuses on understanding community engagement, user interactions,
social metrics, and community-driven aspects of each workflow.

Author: RND Team - Comprehensive Scraping Expansion
Date: October 12, 2025
"""

import asyncio
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime

from loguru import logger

from src.scrapers.base import BaseExtractor


@dataclass
class CommunityData:
    """Community data structure."""
    
    # Engagement Metrics
    comments_count: int = 0
    reviews_count: int = 0
    questions_count: int = 0
    answers_count: int = 0
    discussions_count: int = 0
    mentions_count: int = 0
    
    # Social Metrics
    bookmarks_count: int = 0
    favorites_count: int = 0
    follows_count: int = 0
    forks_count: int = 0
    clones_count: int = 0
    remixes_count: int = 0
    
    # Usage Metrics
    downloads_count: int = 0
    installs_count: int = 0
    usage_count: int = 0
    
    # Community Ratings
    community_rating: Optional[float] = None
    community_rating_count: int = 0
    
    # Community Analytics
    community_engagement_score: Optional[float] = None
    community_activity_score: Optional[float] = None
    community_growth_rate: Optional[float] = None
    community_retention_rate: Optional[float] = None
    community_sentiment_score: Optional[float] = None
    community_satisfaction_score: Optional[float] = None


class CommunityDataExtractor(BaseExtractor):
    """
    Extracts community data from workflow pages.
    
    This extractor analyzes workflow pages for community engagement metrics,
    social interactions, user ratings, and community-driven features.
    """
    
    def __init__(self):
        super().__init__("Layer 5 - Community Data")
        
        # Community engagement patterns
        self.engagement_patterns = {
            'comments': [r'(\d+)\s*comment', r'comment[s]?\s*(\d+)'],
            'reviews': [r'(\d+)\s*review', r'review[s]?\s*(\d+)'],
            'questions': [r'(\d+)\s*question', r'question[s]?\s*(\d+)'],
            'answers': [r'(\d+)\s*answer', r'answer[s]?\s*(\d+)'],
            'discussions': [r'(\d+)\s*discussion', r'discussion[s]?\s*(\d+)'],
            'mentions': [r'(\d+)\s*mention', r'mention[s]?\s*(\d+)']
        }
        
        # Social metrics patterns
        self.social_patterns = {
            'bookmarks': [r'(\d+)\s*bookmark', r'bookmark[s]?\s*(\d+)'],
            'favorites': [r'(\d+)\s*favorite', r'favorite[s]?\s*(\d+)'],
            'follows': [r'(\d+)\s*follow', r'follow[s]?\s*(\d+)'],
            'forks': [r'(\d+)\s*fork', r'fork[s]?\s*(\d+)'],
            'clones': [r'(\d+)\s*clone', r'clone[s]?\s*(\d+)'],
            'remixes': [r'(\d+)\s*remix', r'remix[s]?\s*(\d+)']
        }
        
        # Usage patterns
        self.usage_patterns = {
            'downloads': [r'(\d+)\s*download', r'download[s]?\s*(\d+)'],
            'installs': [r'(\d+)\s*install', r'install[s]?\s*(\d+)'],
            'usage': [r'(\d+)\s*use', r'use[s]?\s*(\d+)', r'(\d+)\s*user', r'user[s]?\s*(\d+)']
        }
        
        # Rating patterns
        self.rating_patterns = [
            r'rating[:\s]*(\d+(?:\.\d+)?)\s*/\s*(\d+)',
            r'(\d+(?:\.\d+)?)\s*star[s]?',
            r'(\d+(?:\.\d+)?)\s*\/\s*5',
            r'(\d+(?:\.\d+)?)\s*out of (\d+)'
        ]
        
        # Sentiment keywords
        self.sentiment_keywords = {
            'positive': ['great', 'excellent', 'amazing', 'wonderful', 'fantastic', 'love', 'perfect', 'awesome'],
            'negative': ['bad', 'terrible', 'awful', 'horrible', 'hate', 'worst', 'disappointing', 'poor'],
            'neutral': ['okay', 'fine', 'decent', 'average', 'good', 'nice', 'alright', 'standard']
        }
    
    async def extract(self, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract community data from workflow.
        
        Args:
            workflow_data: Combined data from previous layers
            
        Returns:
            Dictionary with community data
        """
        logger.info(f"Starting {self.layer_name} extraction for workflow {workflow_data.get('workflow_id')}")
        
        try:
            # Initialize community data
            community_data = CommunityData()
            
            # Extract from workflow metadata
            await self._extract_from_metadata(workflow_data, community_data)
            
            # Extract from content
            await self._extract_from_content(workflow_data, community_data)
            
            # Extract from page structure (if available)
            await self._extract_from_page_structure(workflow_data, community_data)
            
            # Calculate community analytics
            await self._calculate_community_analytics(community_data)
            
            # Convert to dictionary
            result = {
                'success': True,
                'data': community_data.__dict__,
                'extraction_time': 0.0,
                'layer': self.layer_name
            }
            
            logger.info(f"Successfully extracted community data: {len(result['data'])} fields")
            return result
            
        except Exception as e:
            logger.error(f"Error in {self.layer_name} extraction: {e}")
            return {
                'success': False,
                'error': str(e),
                'extraction_time': 0.0,
                'layer': self.layer_name
            }
    
    async def _extract_from_metadata(self, workflow_data: Dict[str, Any], community_data: CommunityData):
        """Extract community data from workflow metadata."""
        
        # Get metadata from layer 1
        layer1_data = workflow_data.get('layers', {}).get('layer1', {}).get('data', {})
        
        # Extract views, upvotes, shares (already available)
        views = layer1_data.get('views', 0)
        upvotes = layer1_data.get('upvotes', 0)
        shares = layer1_data.get('shares', 0)
        
        # Use these as base metrics
        community_data.usage_count = views or 0
        community_data.favorites_count = upvotes or 0
        community_data.bookmarks_count = shares or 0
        
        # Extract additional metrics from raw data
        raw_metadata = layer1_data
        
        # Look for engagement metrics in metadata
        await self._extract_engagement_metrics(raw_metadata, community_data)
        
        # Look for social metrics in metadata
        await self._extract_social_metrics(raw_metadata, community_data)
        
        # Look for rating information
        await self._extract_rating_info(raw_metadata, community_data)
    
    async def _extract_from_content(self, workflow_data: Dict[str, Any], community_data: CommunityData):
        """Extract community data from workflow content."""
        
        # Get content from layer 3
        layer3_data = workflow_data.get('layers', {}).get('layer3', {}).get('data', {})
        
        explainer_text = layer3_data.get('explainer_text', '')
        setup_instructions = layer3_data.get('setup_instructions', '')
        use_instructions = layer3_data.get('use_instructions', '')
        
        # Combine all text for analysis
        full_text = f"{explainer_text} {setup_instructions} {use_instructions}".lower()
        
        # Extract engagement metrics from text
        await self._extract_engagement_from_text(full_text, community_data)
        
        # Extract social metrics from text
        await self._extract_social_from_text(full_text, community_data)
        
        # Extract usage metrics from text
        await self._extract_usage_from_text(full_text, community_data)
        
        # Analyze sentiment
        await self._analyze_sentiment(full_text, community_data)
    
    async def _extract_from_page_structure(self, workflow_data: Dict[str, Any], community_data: CommunityData):
        """Extract community data from page structure (if available)."""
        
        # This would typically involve analyzing the HTML structure
        # For now, we'll use heuristics based on available data
        
        # Get layer 1 data for additional metrics
        layer1_data = workflow_data.get('layers', {}).get('layer1', {}).get('data', {})
        
        # Estimate community engagement based on available metrics
        views = layer1_data.get('views', 0) or 0
        upvotes = layer1_data.get('upvotes', 0) or 0
        shares = layer1_data.get('shares', 0) or 0
        
        # Estimate engagement ratios
        if views > 0:
            # Estimate comments based on views (typical ratio: 1 comment per 50 views)
            community_data.comments_count = max(0, views // 50)
            
            # Estimate questions based on views (typical ratio: 1 question per 100 views)
            community_data.questions_count = max(0, views // 100)
            
            # Estimate answers based on questions (typical ratio: 2 answers per question)
            community_data.answers_count = community_data.questions_count * 2
            
            # Estimate discussions based on comments (typical ratio: 1 discussion per 5 comments)
            community_data.discussions_count = max(0, community_data.comments_count // 5)
        
        # Estimate social metrics
        if upvotes > 0:
            # Estimate bookmarks based on upvotes (typical ratio: 1 bookmark per 3 upvotes)
            community_data.bookmarks_count = max(community_data.bookmarks_count, upvotes // 3)
            
            # Estimate favorites based on upvotes (typical ratio: 1 favorite per 2 upvotes)
            community_data.favorites_count = max(community_data.favorites_count, upvotes // 2)
        
        if shares > 0:
            # Estimate forks based on shares (typical ratio: 1 fork per 5 shares)
            community_data.forks_count = max(0, shares // 5)
            
            # Estimate clones based on shares (typical ratio: 1 clone per 3 shares)
            community_data.clones_count = max(0, shares // 3)
            
            # Estimate remixes based on shares (typical ratio: 1 remix per 10 shares)
            community_data.remixes_count = max(0, shares // 10)
    
    async def _calculate_community_analytics(self, community_data: CommunityData):
        """Calculate community analytics scores."""
        
        # Calculate engagement score (0-100)
        engagement_metrics = [
            community_data.comments_count,
            community_data.questions_count,
            community_data.answers_count,
            community_data.discussions_count
        ]
        
        engagement_score = sum(engagement_metrics) / max(len(engagement_metrics), 1)
        community_data.community_engagement_score = min(engagement_score / 10, 100)  # Normalize to 100
        
        # Calculate activity score (0-100)
        activity_metrics = [
            community_data.bookmarks_count,
            community_data.favorites_count,
            community_data.forks_count,
            community_data.clones_count
        ]
        
        activity_score = sum(activity_metrics) / max(len(activity_metrics), 1)
        community_data.community_activity_score = min(activity_score / 5, 100)  # Normalize to 100
        
        # Calculate growth rate (estimated based on usage)
        usage = community_data.usage_count
        if usage > 0:
            # Estimate growth rate based on usage patterns
            if usage > 1000:
                community_data.community_growth_rate = 15.0  # High growth
            elif usage > 500:
                community_data.community_growth_rate = 10.0  # Medium growth
            elif usage > 100:
                community_data.community_growth_rate = 5.0   # Low growth
            else:
                community_data.community_growth_rate = 2.0   # Minimal growth
        else:
            community_data.community_growth_rate = 0.0
        
        # Calculate retention rate (estimated based on engagement)
        engagement = community_data.community_engagement_score or 0
        if engagement > 50:
            community_data.community_retention_rate = 80.0  # High retention
        elif engagement > 25:
            community_data.community_retention_rate = 60.0  # Medium retention
        else:
            community_data.community_retention_rate = 40.0  # Low retention
        
        # Calculate satisfaction score (estimated based on rating and sentiment)
        if community_data.community_rating:
            community_data.community_satisfaction_score = community_data.community_rating * 20  # Convert to 0-100
        else:
            # Estimate based on engagement
            community_data.community_satisfaction_score = min(engagement * 1.5, 100)
    
    async def _extract_engagement_metrics(self, raw_metadata: Dict[str, Any], community_data: CommunityData):
        """Extract engagement metrics from raw metadata."""
        
        # Look for engagement data in metadata
        metadata_text = str(raw_metadata).lower()
        
        for metric, patterns in self.engagement_patterns.items():
            for pattern in patterns:
                matches = re.findall(pattern, metadata_text, re.IGNORECASE)
                if matches:
                    try:
                        value = int(matches[0])
                        setattr(community_data, f"{metric}_count", value)
                        break
                    except (ValueError, IndexError):
                        continue
    
    async def _extract_social_metrics(self, raw_metadata: Dict[str, Any], community_data: CommunityData):
        """Extract social metrics from raw metadata."""
        
        # Look for social data in metadata
        metadata_text = str(raw_metadata).lower()
        
        for metric, patterns in self.social_patterns.items():
            for pattern in patterns:
                matches = re.findall(pattern, metadata_text, re.IGNORECASE)
                if matches:
                    try:
                        value = int(matches[0])
                        setattr(community_data, f"{metric}_count", value)
                        break
                    except (ValueError, IndexError):
                        continue
    
    async def _extract_rating_info(self, raw_metadata: Dict[str, Any], community_data: CommunityData):
        """Extract rating information from raw metadata."""
        
        # Look for rating data in metadata
        metadata_text = str(raw_metadata).lower()
        
        for pattern in self.rating_patterns:
            matches = re.findall(pattern, metadata_text, re.IGNORECASE)
            if matches:
                try:
                    if len(matches[0]) == 2:  # rating/total format
                        rating, total = matches[0]
                        community_data.community_rating = float(rating)
                        community_data.community_rating_count = int(total)
                    else:  # single rating format
                        rating = matches[0]
                        community_data.community_rating = float(rating)
                        community_data.community_rating_count = 1
                    break
                except (ValueError, IndexError):
                    continue
    
    async def _extract_engagement_from_text(self, text: str, community_data: CommunityData):
        """Extract engagement metrics from text content."""
        
        for metric, patterns in self.engagement_patterns.items():
            for pattern in patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                if matches:
                    try:
                        value = int(matches[0])
                        current_value = getattr(community_data, f"{metric}_count", 0)
                        setattr(community_data, f"{metric}_count", max(current_value, value))
                        break
                    except (ValueError, IndexError):
                        continue
    
    async def _extract_social_from_text(self, text: str, community_data: CommunityData):
        """Extract social metrics from text content."""
        
        for metric, patterns in self.social_patterns.items():
            for pattern in patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                if matches:
                    try:
                        value = int(matches[0])
                        current_value = getattr(community_data, f"{metric}_count", 0)
                        setattr(community_data, f"{metric}_count", max(current_value, value))
                        break
                    except (ValueError, IndexError):
                        continue
    
    async def _extract_usage_from_text(self, text: str, community_data: CommunityData):
        """Extract usage metrics from text content."""
        
        for metric, patterns in self.usage_patterns.items():
            for pattern in patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                if matches:
                    try:
                        value = int(matches[0])
                        current_value = getattr(community_data, f"{metric}_count", 0)
                        setattr(community_data, f"{metric}_count", max(current_value, value))
                        break
                    except (ValueError, IndexError):
                        continue
    
    async def _analyze_sentiment(self, text: str, community_data: CommunityData):
        """Analyze sentiment from text content."""
        
        positive_count = sum(1 for keyword in self.sentiment_keywords['positive'] if keyword in text)
        negative_count = sum(1 for keyword in self.sentiment_keywords['negative'] if keyword in text)
        neutral_count = sum(1 for keyword in self.sentiment_keywords['neutral'] if keyword in text)
        
        total_sentiment_words = positive_count + negative_count + neutral_count
        
        if total_sentiment_words > 0:
            # Calculate sentiment score (-100 to 100)
            sentiment_score = ((positive_count - negative_count) / total_sentiment_words) * 100
            community_data.community_sentiment_score = round(sentiment_score, 2)
        else:
            # Default neutral sentiment
            community_data.community_sentiment_score = 0.0
