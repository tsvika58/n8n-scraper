"""
Layer 7: Performance Analytics Extraction
Extracts performance metrics, execution analytics, optimization opportunities, and monitoring requirements.

This layer focuses on understanding the performance characteristics,
execution patterns, optimization potential, and monitoring needs
of each workflow for production deployment and scaling.

Author: RND Team - Comprehensive Scraping Expansion
Date: October 12, 2025
"""

import asyncio
import re
import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime

from loguru import logger

from src.scrapers.base import BaseExtractor


@dataclass
class PerformanceAnalyticsData:
    """Performance analytics data structure."""
    
    # Execution Metrics
    execution_success_rate: Optional[float] = None
    execution_failure_rate: Optional[float] = None
    execution_error_rate: Optional[float] = None
    
    # Performance Data
    performance_benchmarks: Optional[Dict[str, Any]] = None
    performance_metrics: Optional[Dict[str, Any]] = None
    performance_trends: Optional[Dict[str, Any]] = None
    
    # Usage Analytics
    usage_statistics: Optional[Dict[str, Any]] = None
    usage_patterns: Optional[Dict[str, Any]] = None
    usage_analytics: Optional[Dict[str, Any]] = None
    
    # Error Analytics
    error_analytics: Optional[Dict[str, Any]] = None
    error_patterns: Optional[List[str]] = None
    error_trends: Optional[Dict[str, Any]] = None
    
    # Optimization
    optimization_opportunities: Optional[List[str]] = None
    optimization_recommendations: Optional[List[str]] = None
    
    # Scaling
    scaling_requirements: Optional[Dict[str, Any]] = None
    scaling_limitations: Optional[List[str]] = None
    scaling_recommendations: Optional[List[str]] = None
    
    # Monitoring
    monitoring_requirements: Optional[Dict[str, Any]] = None
    monitoring_metrics: Optional[List[str]] = None
    monitoring_alerts: Optional[List[str]] = None
    
    # Cost Analysis
    maintenance_cost: Optional[float] = None
    support_cost: Optional[float] = None
    training_cost: Optional[float] = None
    documentation_cost: Optional[float] = None
    testing_cost: Optional[float] = None
    deployment_cost: Optional[float] = None
    integration_cost: Optional[float] = None
    customization_cost: Optional[float] = None
    security_cost: Optional[float] = None
    compliance_cost: Optional[float] = None
    governance_cost: Optional[float] = None
    audit_cost: Optional[float] = None
    backup_cost: Optional[float] = None
    
    # Requirements
    maintenance_requirements: Optional[List[str]] = None
    support_requirements: Optional[List[str]] = None
    training_requirements: Optional[List[str]] = None
    documentation_requirements: Optional[List[str]] = None
    testing_requirements: Optional[List[str]] = None
    deployment_requirements: Optional[List[str]] = None
    integration_requirements: Optional[List[str]] = None
    customization_requirements: Optional[List[str]] = None
    security_requirements: Optional[List[str]] = None
    compliance_requirements: Optional[List[str]] = None
    governance_requirements: Optional[List[str]] = None
    audit_requirements: Optional[List[str]] = None
    backup_requirements: Optional[List[str]] = None
    
    # Levels
    support_level: Optional[str] = None
    training_level: Optional[str] = None
    documentation_level: Optional[str] = None
    testing_level: Optional[str] = None
    deployment_level: Optional[str] = None
    integration_level: Optional[str] = None
    customization_level: Optional[str] = None
    security_level: Optional[str] = None
    compliance_level: Optional[str] = None
    governance_level: Optional[str] = None
    audit_level: Optional[str] = None
    backup_level: Optional[str] = None
    
    # Schedules
    maintenance_schedule: Optional[Dict[str, Any]] = None


class PerformanceAnalyticsExtractor(BaseExtractor):
    """
    Extracts performance analytics from workflow pages.
    
    This extractor analyzes workflow structure, content, and metadata
    to extract performance characteristics, execution patterns,
    optimization opportunities, and monitoring requirements.
    """
    
    def __init__(self):
        super().__init__("Layer 7 - Performance Analytics")
        
        # Performance patterns
        self.performance_patterns = {
            'success_rate': [
                r'success[^\s]*rate[:\s]*(\d+(?:\.\d+)?)%?',
                r'(\d+(?:\.\d+)?)%?\s*success',
                r'reliability[:\s]*(\d+(?:\.\d+)?)%?'
            ],
            'failure_rate': [
                r'failure[^\s]*rate[:\s]*(\d+(?:\.\d+)?)%?',
                r'(\d+(?:\.\d+)?)%?\s*failure',
                r'error[^\s]*rate[:\s]*(\d+(?:\.\d+)?)%?'
            ],
            'execution_time': [
                r'execution[^\s]*time[:\s]*(\d+(?:\.\d+)?)\s*(?:seconds?|minutes?|hours?)',
                r'runtime[:\s]*(\d+(?:\.\d+)?)\s*(?:seconds?|minutes?|hours?)',
                r'(\d+(?:\.\d+)?)\s*seconds?[^\s]*execution'
            ],
            'throughput': [
                r'throughput[:\s]*(\d+(?:\.\d+)?)\s*(?:per|/)\s*(?:second|minute|hour)',
                r'(\d+(?:\.\d+)?)\s*request[s]?\s*(?:per|/)\s*(?:second|minute|hour)',
                r'(\d+(?:\.\d+)?)\s*operation[s]?\s*(?:per|/)\s*(?:second|minute|hour)'
            ]
        }
        
        # Optimization patterns
        self.optimization_patterns = [
            r'optimize[^\s]*',
            r'improve[^\s]*',
            r'enhance[^\s]*',
            r'speed[^\s]*up',
            r'faster[^\s]*',
            r'efficient[^\s]*',
            r'reduce[^\s]*time',
            r'minimize[^\s]*',
            r'maximize[^\s]*'
        ]
        
        # Scaling patterns
        self.scaling_patterns = [
            r'scale[^\s]*',
            r'expand[^\s]*',
            r'grow[^\s]*',
            r'handle[^\s]*volume',
            r'capacity[^\s]*',
            r'load[^\s]*balanc',
            r'horizontal[^\s]*',
            r'vertical[^\s]*'
        ]
        
        # Monitoring patterns
        self.monitoring_patterns = [
            r'monitor[^\s]*',
            r'track[^\s]*',
            r'log[^\s]*',
            r'alert[^\s]*',
            r'metric[^\s]*',
            r'dashboard[^\s]*',
            r'analytics[^\s]*',
            r'report[^\s]*'
        ]
        
        # Cost patterns
        self.cost_patterns = {
            'maintenance': [r'maintenance[^\s]*cost[:\s]*\$?(\d+(?:,\d{3})*(?:\.\d{2})?)', r'upkeep[^\s]*cost[:\s]*\$?(\d+(?:,\d{3})*(?:\.\d{2})?)'],
            'support': [r'support[^\s]*cost[:\s]*\$?(\d+(?:,\d{3})*(?:\.\d{2})?)', r'help[^\s]*cost[:\s]*\$?(\d+(?:,\d{3})*(?:\.\d{2})?)'],
            'training': [r'training[^\s]*cost[:\s]*\$?(\d+(?:,\d{3})*(?:\.\d{2})?)', r'education[^\s]*cost[:\s]*\$?(\d+(?:,\d{3})*(?:\.\d{2})?)'],
            'documentation': [r'documentation[^\s]*cost[:\s]*\$?(\d+(?:,\d{3})*(?:\.\d{2})?)', r'manual[^\s]*cost[:\s]*\$?(\d+(?:,\d{3})*(?:\.\d{2})?)'],
            'testing': [r'testing[^\s]*cost[:\s]*\$?(\d+(?:,\d{3})*(?:\.\d{2})?)', r'qa[^\s]*cost[:\s]*\$?(\d+(?:,\d{3})*(?:\.\d{2})?)'],
            'deployment': [r'deployment[^\s]*cost[:\s]*\$?(\d+(?:,\d{3})*(?:\.\d{2})?)', r'install[^\s]*cost[:\s]*\$?(\d+(?:,\d{3})*(?:\.\d{2})?)'],
            'integration': [r'integration[^\s]*cost[:\s]*\$?(\d+(?:,\d{3})*(?:\.\d{2})?)', r'connect[^\s]*cost[:\s]*\$?(\d+(?:,\d{3})*(?:\.\d{2})?)'],
            'customization': [r'customization[^\s]*cost[:\s]*\$?(\d+(?:,\d{3})*(?:\.\d{2})?)', r'custom[^\s]*cost[:\s]*\$?(\d+(?:,\d{3})*(?:\.\d{2})?)'],
            'security': [r'security[^\s]*cost[:\s]*\$?(\d+(?:,\d{3})*(?:\.\d{2})?)', r'protect[^\s]*cost[:\s]*\$?(\d+(?:,\d{3})*(?:\.\d{2})?)'],
            'compliance': [r'compliance[^\s]*cost[:\s]*\$?(\d+(?:,\d{3})*(?:\.\d{2})?)', r'regulat[^\s]*cost[:\s]*\$?(\d+(?:,\d{3})*(?:\.\d{2})?)'],
            'governance': [r'governance[^\s]*cost[:\s]*\$?(\d+(?:,\d{3})*(?:\.\d{2})?)', r'control[^\s]*cost[:\s]*\$?(\d+(?:,\d{3})*(?:\.\d{2})?)'],
            'audit': [r'audit[^\s]*cost[:\s]*\$?(\d+(?:,\d{3})*(?:\.\d{2})?)', r'review[^\s]*cost[:\s]*\$?(\d+(?:,\d{3})*(?:\.\d{2})?)'],
            'backup': [r'backup[^\s]*cost[:\s]*\$?(\d+(?:,\d{3})*(?:\.\d{2})?)', r'recovery[^\s]*cost[:\s]*\$?(\d+(?:,\d{3})*(?:\.\d{2})?)']
        }
        
        # Requirement patterns
        self.requirement_patterns = {
            'maintenance': [r'maintenance[^\s]*requir', r'upkeep[^\s]*requir', r'support[^\s]*requir'],
            'support': [r'support[^\s]*requir', r'help[^\s]*requir', r'assistance[^\s]*requir'],
            'training': [r'training[^\s]*requir', r'education[^\s]*requir', r'learning[^\s]*requir'],
            'documentation': [r'documentation[^\s]*requir', r'manual[^\s]*requir', r'guide[^\s]*requir'],
            'testing': [r'testing[^\s]*requir', r'qa[^\s]*requir', r'validation[^\s]*requir'],
            'deployment': [r'deployment[^\s]*requir', r'install[^\s]*requir', r'setup[^\s]*requir'],
            'integration': [r'integration[^\s]*requir', r'connect[^\s]*requir', r'link[^\s]*requir'],
            'customization': [r'customization[^\s]*requir', r'custom[^\s]*requir', r'modify[^\s]*requir'],
            'security': [r'security[^\s]*requir', r'protect[^\s]*requir', r'secure[^\s]*requir'],
            'compliance': [r'compliance[^\s]*requir', r'regulat[^\s]*requir', r'policy[^\s]*requir'],
            'governance': [r'governance[^\s]*requir', r'control[^\s]*requir', r'manage[^\s]*requir'],
            'audit': [r'audit[^\s]*requir', r'review[^\s]*requir', r'check[^\s]*requir'],
            'backup': [r'backup[^\s]*requir', r'recovery[^\s]*requir', r'restore[^\s]*requir']
        }
        
        # Level patterns
        self.level_patterns = {
            'high': ['high', 'advanced', 'complex', 'sophisticated', 'enterprise', 'critical'],
            'medium': ['medium', 'intermediate', 'moderate', 'standard', 'normal', 'typical'],
            'low': ['low', 'basic', 'simple', 'minimal', 'easy', 'beginner']
        }
    
    async def extract(self, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract performance analytics from workflow.
        
        Args:
            workflow_data: Combined data from previous layers
            
        Returns:
            Dictionary with performance analytics data
        """
        logger.info(f"Starting {self.layer_name} extraction for workflow {workflow_data.get('workflow_id')}")
        
        try:
            # Initialize performance analytics data
            perf_data = PerformanceAnalyticsData()
            
            # Extract from workflow structure
            await self._extract_from_structure(workflow_data, perf_data)
            
            # Extract from content
            await self._extract_from_content(workflow_data, perf_data)
            
            # Extract from metadata
            await self._extract_from_metadata(workflow_data, perf_data)
            
            # Calculate performance metrics
            await self._calculate_performance_metrics(workflow_data, perf_data)
            
            # Analyze optimization opportunities
            await self._analyze_optimization_opportunities(workflow_data, perf_data)
            
            # Analyze scaling requirements
            await self._analyze_scaling_requirements(workflow_data, perf_data)
            
            # Analyze monitoring requirements
            await self._analyze_monitoring_requirements(workflow_data, perf_data)
            
            # Calculate cost estimates
            await self._calculate_cost_estimates(workflow_data, perf_data)
            
            # Analyze requirements
            await self._analyze_requirements(workflow_data, perf_data)
            
            # Convert to dictionary
            result = {
                'success': True,
                'data': perf_data.__dict__,
                'extraction_time': 0.0,
                'layer': self.layer_name
            }
            
            logger.info(f"Successfully extracted performance analytics: {len(result['data'])} fields")
            return result
            
        except Exception as e:
            logger.error(f"Error in {self.layer_name} extraction: {e}")
            return {
                'success': False,
                'error': str(e),
                'extraction_time': 0.0,
                'layer': self.layer_name
            }
    
    async def _extract_from_structure(self, workflow_data: Dict[str, Any], perf_data: PerformanceAnalyticsData):
        """Extract performance analytics from workflow structure."""
        
        # Get structure from layer 2
        layer2_data = workflow_data.get('layers', {}).get('layer2', {}).get('data', {})
        
        node_count = layer2_data.get('node_count', 0)
        connection_count = layer2_data.get('connection_count', 0)
        
        # Calculate complexity-based performance estimates
        if node_count > 0:
            # Estimate execution time based on node count
            estimated_time = node_count * 0.5  # 0.5 seconds per node
            perf_data.performance_metrics = {
                'estimated_execution_time': estimated_time,
                'node_count': node_count,
                'connection_count': connection_count,
                'complexity_score': node_count + connection_count
            }
            
            # Estimate success rate based on complexity
            if node_count <= 5:
                perf_data.execution_success_rate = 95.0
            elif node_count <= 15:
                perf_data.execution_success_rate = 90.0
            else:
                perf_data.execution_success_rate = 85.0
            
            # Calculate failure and error rates
            perf_data.execution_failure_rate = 100.0 - (perf_data.execution_success_rate or 0)
            perf_data.execution_error_rate = perf_data.execution_failure_rate * 0.7  # 70% of failures are errors
    
    async def _extract_from_content(self, workflow_data: Dict[str, Any], perf_data: PerformanceAnalyticsData):
        """Extract performance analytics from workflow content."""
        
        # Get content from layer 3
        layer3_data = workflow_data.get('layers', {}).get('layer3', {}).get('data', {})
        
        explainer_text = layer3_data.get('explainer_text', '')
        setup_instructions = layer3_data.get('setup_instructions', '')
        use_instructions = layer3_data.get('use_instructions', '')
        
        # Combine all text for analysis
        full_text = f"{explainer_text} {setup_instructions} {use_instructions}".lower()
        
        # Extract performance metrics from text
        await self._extract_performance_from_text(full_text, perf_data)
        
        # Extract optimization opportunities from text
        await self._extract_optimization_from_text(full_text, perf_data)
        
        # Extract scaling requirements from text
        await self._extract_scaling_from_text(full_text, perf_data)
        
        # Extract monitoring requirements from text
        await self._extract_monitoring_from_text(full_text, perf_data)
        
        # Extract cost information from text
        await self._extract_costs_from_text(full_text, perf_data)
    
    async def _extract_from_metadata(self, workflow_data: Dict[str, Any], perf_data: PerformanceAnalyticsData):
        """Extract performance analytics from workflow metadata."""
        
        # Get metadata from layer 1
        layer1_data = workflow_data.get('layers', {}).get('layer1', {}).get('data', {})
        
        # Extract views and engagement for usage analytics
        views = layer1_data.get('views', 0) or 0
        upvotes = layer1_data.get('upvotes', 0) or 0
        shares = layer1_data.get('shares', 0) or 0
        
        # Calculate usage statistics
        perf_data.usage_statistics = {
            'total_views': views,
            'total_upvotes': upvotes,
            'total_shares': shares,
            'engagement_rate': (upvotes + shares) / max(views, 1) * 100 if views > 0 else 0
        }
        
        # Calculate usage patterns
        if views > 1000:
            perf_data.usage_patterns = {'usage_level': 'high', 'popularity': 'very_popular'}
        elif views > 500:
            perf_data.usage_patterns = {'usage_level': 'medium', 'popularity': 'popular'}
        elif views > 100:
            perf_data.usage_patterns = {'usage_level': 'low', 'popularity': 'moderate'}
        else:
            perf_data.usage_patterns = {'usage_level': 'minimal', 'popularity': 'low'}
        
        # Calculate usage analytics
        perf_data.usage_analytics = {
            'adoption_score': min(views / 100, 100),  # Normalize to 100
            'community_score': min((upvotes + shares) / 10, 100),  # Normalize to 100
            'growth_potential': 'high' if views > 500 else 'medium' if views > 100 else 'low'
        }
    
    async def _calculate_performance_metrics(self, workflow_data: Dict[str, Any], perf_data: PerformanceAnalyticsData):
        """Calculate comprehensive performance metrics."""
        
        # Get structure data
        layer2_data = workflow_data.get('layers', {}).get('layer2', {}).get('data', {})
        node_count = layer2_data.get('node_count', 0)
        connection_count = layer2_data.get('connection_count', 0)
        
        # Calculate performance benchmarks
        perf_data.performance_benchmarks = {
            'node_processing_time': 0.5,  # seconds per node
            'connection_overhead': 0.1,   # seconds per connection
            'estimated_total_time': (node_count * 0.5) + (connection_count * 0.1),
            'complexity_factor': node_count + connection_count,
            'efficiency_rating': 'high' if node_count <= 10 else 'medium' if node_count <= 20 else 'low'
        }
        
        # Calculate performance trends
        perf_data.performance_trends = {
            'scalability_trend': 'positive' if node_count <= 15 else 'neutral' if node_count <= 25 else 'negative',
            'complexity_trend': 'increasing' if connection_count > node_count else 'stable',
            'optimization_potential': 'high' if node_count > 20 else 'medium' if node_count > 10 else 'low'
        }
        
        # Calculate error analytics
        perf_data.error_analytics = {
            'error_prone_nodes': max(0, node_count // 5),  # Estimate 20% of nodes are error-prone
            'connection_risks': max(0, connection_count // 10),  # Estimate 10% of connections are risky
            'overall_risk_score': min((node_count + connection_count) / 10, 100)
        }
        
        # Calculate error patterns
        error_patterns = []
        if node_count > 20:
            error_patterns.append('high_complexity_errors')
        if connection_count > 30:
            error_patterns.append('connection_timeout_errors')
        if node_count > 15:
            error_patterns.append('resource_exhaustion_errors')
        
        perf_data.error_patterns = error_patterns if error_patterns else None
        
        # Calculate error trends
        perf_data.error_trends = {
            'error_frequency': 'high' if node_count > 20 else 'medium' if node_count > 10 else 'low',
            'error_severity': 'high' if connection_count > 30 else 'medium' if connection_count > 15 else 'low',
            'error_recovery_time': 'long' if node_count > 25 else 'medium' if node_count > 15 else 'short'
        }
    
    async def _analyze_optimization_opportunities(self, workflow_data: Dict[str, Any], perf_data: PerformanceAnalyticsData):
        """Analyze optimization opportunities."""
        
        # Get structure data
        layer2_data = workflow_data.get('layers', {}).get('layer2', {}).get('data', {})
        node_count = layer2_data.get('node_count', 0)
        connection_count = layer2_data.get('connection_count', 0)
        
        optimization_opportunities = []
        optimization_recommendations = []
        
        # Analyze based on structure
        if node_count > 20:
            optimization_opportunities.append('reduce_node_count')
            optimization_recommendations.append('Consider consolidating similar nodes to reduce complexity')
        
        if connection_count > 30:
            optimization_opportunities.append('optimize_connections')
            optimization_recommendations.append('Review connection patterns for potential optimization')
        
        if node_count > 15:
            optimization_opportunities.append('parallel_processing')
            optimization_recommendations.append('Implement parallel processing for independent operations')
        
        if connection_count > 20:
            optimization_opportunities.append('connection_optimization')
            optimization_recommendations.append('Optimize connection patterns for better performance')
        
        # Add general optimization opportunities
        optimization_opportunities.extend([
            'caching_implementation',
            'error_handling_improvement',
            'resource_optimization'
        ])
        
        optimization_recommendations.extend([
            'Implement caching for frequently accessed data',
            'Improve error handling and recovery mechanisms',
            'Optimize resource usage and allocation'
        ])
        
        perf_data.optimization_opportunities = optimization_opportunities
        perf_data.optimization_recommendations = optimization_recommendations
    
    async def _analyze_scaling_requirements(self, workflow_data: Dict[str, Any], perf_data: PerformanceAnalyticsData):
        """Analyze scaling requirements."""
        
        # Get structure data
        layer2_data = workflow_data.get('layers', {}).get('layer2', {}).get('data', {})
        node_count = layer2_data.get('node_count', 0)
        connection_count = layer2_data.get('connection_count', 0)
        
        # Calculate scaling requirements
        scaling_requirements = {}
        scaling_limitations = []
        scaling_recommendations = []
        
        # Analyze horizontal scaling
        if node_count > 15:
            scaling_requirements['horizontal_scaling'] = 'required'
            scaling_recommendations.append('Implement horizontal scaling for high node count')
        else:
            scaling_requirements['horizontal_scaling'] = 'optional'
        
        # Analyze vertical scaling
        if connection_count > 25:
            scaling_requirements['vertical_scaling'] = 'required'
            scaling_recommendations.append('Implement vertical scaling for high connection count')
        else:
            scaling_requirements['vertical_scaling'] = 'optional'
        
        # Analyze load balancing
        if node_count > 10:
            scaling_requirements['load_balancing'] = 'recommended'
            scaling_recommendations.append('Implement load balancing for distributed processing')
        
        # Analyze resource requirements
        scaling_requirements['resource_requirements'] = {
            'cpu': 'high' if node_count > 20 else 'medium' if node_count > 10 else 'low',
            'memory': 'high' if connection_count > 30 else 'medium' if connection_count > 15 else 'low',
            'storage': 'medium' if node_count > 15 else 'low'
        }
        
        # Identify scaling limitations
        if node_count > 30:
            scaling_limitations.append('High node count may limit scaling efficiency')
        if connection_count > 50:
            scaling_limitations.append('High connection count may create bottlenecks')
        
        perf_data.scaling_requirements = scaling_requirements
        perf_data.scaling_limitations = scaling_limitations if scaling_limitations else None
        perf_data.scaling_recommendations = scaling_recommendations
    
    async def _analyze_monitoring_requirements(self, workflow_data: Dict[str, Any], perf_data: PerformanceAnalyticsData):
        """Analyze monitoring requirements."""
        
        # Get structure data
        layer2_data = workflow_data.get('layers', {}).get('layer2', {}).get('data', {})
        node_count = layer2_data.get('node_count', 0)
        connection_count = layer2_data.get('connection_count', 0)
        
        # Calculate monitoring requirements
        monitoring_requirements = {}
        monitoring_metrics = []
        monitoring_alerts = []
        
        # Basic monitoring requirements
        monitoring_requirements['performance_monitoring'] = 'required'
        monitoring_requirements['error_monitoring'] = 'required'
        monitoring_requirements['resource_monitoring'] = 'required'
        
        # Advanced monitoring for complex workflows
        if node_count > 15:
            monitoring_requirements['node_monitoring'] = 'required'
            monitoring_metrics.append('node_execution_time')
            monitoring_metrics.append('node_success_rate')
            monitoring_alerts.append('node_failure_alert')
        
        if connection_count > 20:
            monitoring_requirements['connection_monitoring'] = 'required'
            monitoring_metrics.append('connection_latency')
            monitoring_metrics.append('connection_success_rate')
            monitoring_alerts.append('connection_timeout_alert')
        
        # Standard monitoring metrics
        monitoring_metrics.extend([
            'execution_time',
            'success_rate',
            'error_rate',
            'resource_usage',
            'throughput'
        ])
        
        # Standard monitoring alerts
        monitoring_alerts.extend([
            'execution_failure_alert',
            'performance_degradation_alert',
            'resource_exhaustion_alert',
            'error_rate_threshold_alert'
        ])
        
        perf_data.monitoring_requirements = monitoring_requirements
        perf_data.monitoring_metrics = monitoring_metrics
        perf_data.monitoring_alerts = monitoring_alerts
    
    async def _calculate_cost_estimates(self, workflow_data: Dict[str, Any], perf_data: PerformanceAnalyticsData):
        """Calculate cost estimates based on workflow complexity."""
        
        # Get structure data
        layer2_data = workflow_data.get('layers', {}).get('layer2', {}).get('data', {})
        node_count = layer2_data.get('node_count', 0)
        connection_count = layer2_data.get('connection_count', 0)
        
        # Calculate complexity factor
        complexity_factor = node_count + connection_count
        
        # Base costs (monthly estimates in USD)
        base_costs = {
            'maintenance': 100,
            'support': 150,
            'training': 200,
            'documentation': 50,
            'testing': 75,
            'deployment': 100,
            'integration': 125,
            'customization': 175,
            'security': 100,
            'compliance': 150,
            'governance': 125,
            'audit': 100,
            'backup': 75
        }
        
        # Apply complexity multipliers
        if complexity_factor > 30:
            multiplier = 2.0  # High complexity
        elif complexity_factor > 15:
            multiplier = 1.5  # Medium complexity
        else:
            multiplier = 1.0  # Low complexity
        
        # Calculate final costs
        perf_data.maintenance_cost = base_costs['maintenance'] * multiplier
        perf_data.support_cost = base_costs['support'] * multiplier
        perf_data.training_cost = base_costs['training'] * multiplier
        perf_data.documentation_cost = base_costs['documentation'] * multiplier
        perf_data.testing_cost = base_costs['testing'] * multiplier
        perf_data.deployment_cost = base_costs['deployment'] * multiplier
        perf_data.integration_cost = base_costs['integration'] * multiplier
        perf_data.customization_cost = base_costs['customization'] * multiplier
        perf_data.security_cost = base_costs['security'] * multiplier
        perf_data.compliance_cost = base_costs['compliance'] * multiplier
        perf_data.governance_cost = base_costs['governance'] * multiplier
        perf_data.audit_cost = base_costs['audit'] * multiplier
        perf_data.backup_cost = base_costs['backup'] * multiplier
    
    async def _analyze_requirements(self, workflow_data: Dict[str, Any], perf_data: PerformanceAnalyticsData):
        """Analyze various requirements based on workflow complexity."""
        
        # Get structure data
        layer2_data = workflow_data.get('layers', {}).get('layer2', {}).get('data', {})
        node_count = layer2_data.get('node_count', 0)
        connection_count = layer2_data.get('connection_count', 0)
        
        # Calculate complexity factor
        complexity_factor = node_count + connection_count
        
        # Determine levels based on complexity
        if complexity_factor > 30:
            level = 'high'
        elif complexity_factor > 15:
            level = 'medium'
        else:
            level = 'low'
        
        # Set all levels
        perf_data.support_level = level
        perf_data.training_level = level
        perf_data.documentation_level = level
        perf_data.testing_level = level
        perf_data.deployment_level = level
        perf_data.integration_level = level
        perf_data.customization_level = level
        perf_data.security_level = level
        perf_data.compliance_level = level
        perf_data.governance_level = level
        perf_data.audit_level = level
        perf_data.backup_level = level
        
        # Generate requirements based on complexity
        requirements = {
            'maintenance': ['regular_updates', 'performance_monitoring', 'error_tracking'],
            'support': ['user_support', 'technical_support', 'troubleshooting'],
            'training': ['user_training', 'admin_training', 'documentation_review'],
            'documentation': ['user_manual', 'technical_docs', 'api_documentation'],
            'testing': ['unit_testing', 'integration_testing', 'performance_testing'],
            'deployment': ['staging_deployment', 'production_deployment', 'rollback_plan'],
            'integration': ['api_integration', 'data_integration', 'system_integration'],
            'customization': ['configuration', 'custom_logic', 'branding'],
            'security': ['access_control', 'data_encryption', 'security_audit'],
            'compliance': ['regulatory_compliance', 'data_privacy', 'audit_trail'],
            'governance': ['access_governance', 'data_governance', 'process_governance'],
            'audit': ['security_audit', 'compliance_audit', 'performance_audit'],
            'backup': ['data_backup', 'system_backup', 'recovery_testing']
        }
        
        # Add complexity-specific requirements
        if complexity_factor > 30:
            for req_type, req_list in requirements.items():
                req_list.extend([f'advanced_{req_type}', f'enterprise_{req_type}'])
        
        # Set requirements
        for req_type, req_list in requirements.items():
            attr_name = f"{req_type}_requirements"
            setattr(perf_data, attr_name, req_list)
        
        # Set maintenance schedule
        perf_data.maintenance_schedule = {
            'daily': ['monitoring', 'error_checking'],
            'weekly': ['performance_review', 'backup_verification'],
            'monthly': ['security_audit', 'performance_optimization'],
            'quarterly': ['compliance_review', 'system_updates']
        }
    
    async def _extract_performance_from_text(self, text: str, perf_data: PerformanceAnalyticsData):
        """Extract performance metrics from text."""
        
        # Extract success rate
        for pattern in self.performance_patterns['success_rate']:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                try:
                    success_rate = float(matches[0])
                    if success_rate <= 1:  # Convert decimal to percentage
                        success_rate *= 100
                    perf_data.execution_success_rate = success_rate
                    perf_data.execution_failure_rate = 100 - success_rate
                    perf_data.execution_error_rate = (100 - success_rate) * 0.7
                    break
                except ValueError:
                    continue
        
        # Extract execution time
        for pattern in self.performance_patterns['execution_time']:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                try:
                    time_value = float(matches[0])
                    # Convert to seconds
                    if 'minute' in text.lower():
                        time_value *= 60
                    elif 'hour' in text.lower():
                        time_value *= 3600
                    if not perf_data.performance_metrics:
                        perf_data.performance_metrics = {}
                    perf_data.performance_metrics['extracted_execution_time'] = time_value
                    break
                except ValueError:
                    continue
        
        # Extract throughput
        for pattern in self.performance_patterns['throughput']:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                try:
                    throughput = float(matches[0])
                    if not perf_data.performance_metrics:
                        perf_data.performance_metrics = {}
                    perf_data.performance_metrics['throughput'] = throughput
                    break
                except ValueError:
                    continue
    
    async def _extract_optimization_from_text(self, text: str, perf_data: PerformanceAnalyticsData):
        """Extract optimization opportunities from text."""
        
        optimization_opportunities = []
        
        for pattern in self.optimization_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                optimization_opportunities.append(pattern.replace('[^\s]*', '').strip())
        
        if optimization_opportunities and not perf_data.optimization_opportunities:
            perf_data.optimization_opportunities = optimization_opportunities
    
    async def _extract_scaling_from_text(self, text: str, perf_data: PerformanceAnalyticsData):
        """Extract scaling requirements from text."""
        
        scaling_requirements = {}
        
        for pattern in self.scaling_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                scaling_requirements['scaling_mentioned'] = True
                break
        
        if scaling_requirements and not perf_data.scaling_requirements:
            perf_data.scaling_requirements = scaling_requirements
    
    async def _extract_monitoring_from_text(self, text: str, perf_data: PerformanceAnalyticsData):
        """Extract monitoring requirements from text."""
        
        monitoring_requirements = {}
        
        for pattern in self.monitoring_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                monitoring_requirements['monitoring_mentioned'] = True
                break
        
        if monitoring_requirements and not perf_data.monitoring_requirements:
            perf_data.monitoring_requirements = monitoring_requirements
    
    async def _extract_costs_from_text(self, text: str, perf_data: PerformanceAnalyticsData):
        """Extract cost information from text."""
        
        for cost_type, patterns in self.cost_patterns.items():
            for pattern in patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                if matches:
                    try:
                        cost_value = float(matches[0].replace(',', ''))
                        attr_name = f"{cost_type}_cost"
                        setattr(perf_data, attr_name, cost_value)
                        break
                    except ValueError:
                        continue
