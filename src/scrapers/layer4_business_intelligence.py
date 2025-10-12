"""
Layer 4: Business Intelligence Extraction
Extracts business value, ROI, cost analysis, and strategic information from workflows.

This layer focuses on understanding the business impact and value proposition
of each workflow, including revenue impact, cost savings, efficiency gains,
and strategic business context.

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
class BusinessIntelligenceData:
    """Business intelligence data structure."""
    
    # Revenue & Cost Metrics
    revenue_impact: Optional[float] = None
    cost_savings: Optional[float] = None
    efficiency_gains: Optional[float] = None
    time_savings: Optional[int] = None
    resource_savings: Optional[float] = None
    error_reduction: Optional[float] = None
    productivity_gains: Optional[float] = None
    quality_improvements: Optional[float] = None
    customer_satisfaction: Optional[float] = None
    
    # Business Value Metrics
    business_value_score: Optional[float] = None
    roi_estimate: Optional[float] = None
    payback_period: Optional[int] = None
    
    # Cost Breakdown
    implementation_cost: Optional[float] = None
    maintenance_cost: Optional[float] = None
    support_cost: Optional[float] = None
    training_cost: Optional[float] = None
    customization_cost: Optional[float] = None
    integration_cost: Optional[float] = None
    
    # Business Context
    business_function: Optional[str] = None
    business_process: Optional[str] = None
    business_outcome: Optional[str] = None
    business_metric: Optional[str] = None
    business_kpi: Optional[str] = None
    business_goal: Optional[str] = None
    
    # Business Details
    business_requirement: Optional[str] = None
    business_constraint: Optional[str] = None
    business_risk: Optional[str] = None
    business_opportunity: Optional[str] = None
    business_challenge: Optional[str] = None
    business_solution: Optional[str] = None
    business_benefit: Optional[str] = None
    business_advantage: Optional[str] = None
    business_competitive_advantage: Optional[str] = None
    
    # Business Transformation
    business_innovation: Optional[str] = None
    business_transformation: Optional[str] = None
    business_digitalization: Optional[str] = None
    business_automation: Optional[str] = None
    business_optimization: Optional[str] = None
    business_standardization: Optional[str] = None
    
    # Compliance & Governance
    business_compliance: Optional[str] = None
    business_governance: Optional[str] = None
    business_audit: Optional[str] = None
    business_security: Optional[str] = None
    business_privacy: Optional[str] = None
    business_ethics: Optional[str] = None


class BusinessIntelligenceExtractor(BaseExtractor):
    """
    Extracts business intelligence data from workflow pages.
    
    This extractor analyzes workflow descriptions, use cases, and content
    to extract business value, ROI estimates, cost analysis, and strategic
    business context information.
    """
    
    def __init__(self):
        super().__init__("Layer 4 - Business Intelligence")
        
        # Business function keywords
        self.business_functions = {
            'sales': ['sales', 'selling', 'revenue', 'lead', 'customer acquisition', 'conversion'],
            'marketing': ['marketing', 'campaign', 'promotion', 'brand', 'advertising', 'social media'],
            'customer_service': ['support', 'service', 'help', 'ticket', 'response', 'satisfaction'],
            'operations': ['operations', 'process', 'workflow', 'automation', 'efficiency', 'productivity'],
            'finance': ['finance', 'accounting', 'billing', 'payment', 'invoice', 'budget', 'cost'],
            'hr': ['hr', 'human resources', 'employee', 'hiring', 'recruitment', 'payroll', 'benefits'],
            'it': ['it', 'technology', 'system', 'integration', 'api', 'data', 'security'],
            'analytics': ['analytics', 'reporting', 'dashboard', 'metrics', 'kpi', 'insights', 'data'],
            'compliance': ['compliance', 'regulation', 'audit', 'governance', 'policy', 'security']
        }
        
        # Business value indicators
        self.value_indicators = {
            'revenue': ['revenue', 'income', 'profit', 'sales', 'earnings', 'monetize'],
            'cost_savings': ['save', 'savings', 'reduce cost', 'cut cost', 'budget', 'efficient'],
            'time_savings': ['time', 'faster', 'quicker', 'speed', 'reduce time', 'hours'],
            'efficiency': ['efficiency', 'productivity', 'automate', 'streamline', 'optimize'],
            'quality': ['quality', 'accuracy', 'error', 'mistake', 'improve', 'better'],
            'customer': ['customer', 'client', 'satisfaction', 'experience', 'service']
        }
        
        # ROI and cost patterns
        self.roi_patterns = [
            r'roi[:\s]*(\d+(?:\.\d+)?%)?',
            r'return on investment[:\s]*(\d+(?:\.\d+)?%)?',
            r'payback[:\s]*(\d+)\s*(?:months?|years?|days?)',
            r'savings[:\s]*\$?(\d+(?:,\d{3})*(?:\.\d{2})?)(?:\s*(?:per|/)\s*(?:month|year|day|hour))?',
            r'cost[:\s]*\$?(\d+(?:,\d{3})*(?:\.\d{2})?)(?:\s*(?:per|/)\s*(?:month|year|day|hour))?'
        ]
    
    async def extract(self, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract business intelligence data from workflow.
        
        Args:
            workflow_data: Combined data from previous layers
            
        Returns:
            Dictionary with business intelligence data
        """
        workflow_id = workflow_data.get('workflow_id', 'unknown')
        logger.info(f"Starting {self.layer_name} extraction for workflow {workflow_id}")
        
        try:
            # Initialize business intelligence data
            bi_data = BusinessIntelligenceData()
            
            # Extract from workflow metadata
            await self._extract_from_metadata(workflow_data, bi_data)
            
            # Extract from content
            await self._extract_from_content(workflow_data, bi_data)
            
            # Extract from use case
            await self._extract_from_use_case(workflow_data, bi_data)
            
            # Analyze business context
            await self._analyze_business_context(workflow_data, bi_data)
            
            # Calculate business value score
            await self._calculate_business_value_score(bi_data)
            
            # Convert to dictionary
            result = {
                'success': True,
                'data': bi_data.__dict__,
                'extraction_time': 0.01,  # Placeholder - will be measured by E2E pipeline
                'layer': self.layer_name
            }
            
            logger.info(f"Successfully extracted business intelligence data: {len(result['data'])} fields")
            return result
            
        except Exception as e:
            logger.error(f"Error in {self.layer_name} extraction: {e}")
            return {
                'success': False,
                'error': str(e),
                'extraction_time': 0.0,
                'layer': self.layer_name
            }
    
    async def _extract_from_metadata(self, workflow_data: Dict[str, Any], bi_data: BusinessIntelligenceData):
        """Extract business intelligence from workflow metadata."""
        
        # Get metadata from layer 1
        layer1_data = workflow_data.get('layers', {}).get('layer1', {}).get('data', {})
        
        # Extract business function from title/description
        title = layer1_data.get('title', '').lower()
        description = layer1_data.get('description', '').lower()
        use_case = layer1_data.get('use_case', '').lower()
        
        # Determine business function
        for func, keywords in self.business_functions.items():
            for keyword in keywords:
                if keyword in title or keyword in description or keyword in use_case:
                    bi_data.business_function = func.title()
                    break
            if bi_data.business_function:
                break
        
        # Extract business process
        bi_data.business_process = self._extract_business_process(title, description, use_case)
        
        # Extract business outcome
        bi_data.business_outcome = self._extract_business_outcome(description, use_case)
        
        # Extract business goal
        bi_data.business_goal = self._extract_business_goal(description, use_case)
    
    async def _extract_from_content(self, workflow_data: Dict[str, Any], bi_data: BusinessIntelligenceData):
        """Extract business intelligence from workflow content."""
        
        # Get content from layer 3
        layer3_data = workflow_data.get('layers', {}).get('layer3', {}).get('data', {})
        
        explainer_text = layer3_data.get('explainer_text', '')
        setup_instructions = layer3_data.get('setup_instructions', '')
        use_instructions = layer3_data.get('use_instructions', '')
        
        # Combine all text for analysis
        full_text = f"{explainer_text} {setup_instructions} {use_instructions}".lower()
        
        # Extract ROI and cost information
        await self._extract_roi_and_costs(full_text, bi_data)
        
        # Extract business benefits
        await self._extract_business_benefits(full_text, bi_data)
        
        # Extract business challenges and solutions
        await self._extract_challenges_and_solutions(full_text, bi_data)
    
    async def _extract_from_use_case(self, workflow_data: Dict[str, Any], bi_data: BusinessIntelligenceData):
        """Extract business intelligence from use case information."""
        
        layer1_data = workflow_data.get('layers', {}).get('layer1', {}).get('data', {})
        use_case = layer1_data.get('use_case', '')
        
        if not use_case:
            return
        
        # Extract business requirements
        bi_data.business_requirement = self._extract_business_requirements(use_case)
        
        # Extract business constraints
        bi_data.business_constraint = self._extract_business_constraints(use_case)
        
        # Extract business risks
        bi_data.business_risk = self._extract_business_risks(use_case)
    
    async def _analyze_business_context(self, workflow_data: Dict[str, Any], bi_data: BusinessIntelligenceData):
        """Analyze overall business context and transformation potential."""
        
        # Get all text content
        layer1_data = workflow_data.get('layers', {}).get('layer1', {}).get('data', {})
        layer3_data = workflow_data.get('layers', {}).get('layer3', {}).get('data', {})
        
        title = layer1_data.get('title', '')
        description = layer1_data.get('description', '')
        use_case = layer1_data.get('use_case', '')
        explainer_text = layer3_data.get('explainer_text', '')
        
        full_text = f"{title} {description} {use_case} {explainer_text}".lower()
        
        # Analyze transformation potential
        bi_data.business_automation = self._analyze_automation_potential(full_text)
        bi_data.business_optimization = self._analyze_optimization_potential(full_text)
        bi_data.business_innovation = self._analyze_innovation_potential(full_text)
        
        # Analyze compliance and governance
        bi_data.business_compliance = self._analyze_compliance_requirements(full_text)
        bi_data.business_security = self._analyze_security_requirements(full_text)
    
    async def _extract_roi_and_costs(self, text: str, bi_data: BusinessIntelligenceData):
        """Extract ROI and cost information from text."""
        
        # Look for ROI patterns
        for pattern in self.roi_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                # Extract numeric values
                for match in matches:
                    if match:
                        try:
                            # Clean and convert to float
                            value = float(match.replace('%', '').replace(',', ''))
                            if 'roi' in pattern.lower() or 'return' in pattern.lower():
                                bi_data.roi_estimate = value
                            elif 'payback' in pattern.lower():
                                bi_data.payback_period = int(value)
                            elif 'savings' in pattern.lower():
                                bi_data.cost_savings = value
                            elif 'cost' in pattern.lower():
                                bi_data.implementation_cost = value
                        except ValueError:
                            continue
        
        # Look for time savings
        time_patterns = [
            r'save[s]?\s+(\d+)\s+(?:hours?|hrs?)',
            r'reduce[s]?\s+(\d+)\s+(?:hours?|hrs?)',
            r'(\d+)\s+(?:hours?|hrs?)\s+(?:per|/)\s+(?:day|week|month|year)'
        ]
        
        for pattern in time_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                try:
                    bi_data.time_savings = int(matches[0])
                except ValueError:
                    continue
    
    async def _extract_business_benefits(self, text: str, bi_data: BusinessIntelligenceData):
        """Extract business benefits from text."""
        
        # Look for benefit indicators
        benefit_patterns = {
            'efficiency': ['efficiency', 'productivity', 'streamline', 'optimize'],
            'quality': ['quality', 'accuracy', 'reduce error', 'improve'],
            'customer': ['customer satisfaction', 'user experience', 'service quality'],
            'cost': ['cost effective', 'reduce cost', 'save money', 'budget'],
            'time': ['faster', 'quicker', 'reduce time', 'speed up']
        }
        
        for benefit_type, keywords in benefit_patterns.items():
            for keyword in keywords:
                if keyword in text:
                    if benefit_type == 'efficiency':
                        bi_data.efficiency_gains = 0.25  # Default 25% improvement
                    elif benefit_type == 'quality':
                        bi_data.quality_improvements = 0.20  # Default 20% improvement
                    elif benefit_type == 'customer':
                        bi_data.customer_satisfaction = 0.15  # Default 15% improvement
                    elif benefit_type == 'cost':
                        bi_data.cost_savings = bi_data.cost_savings or 1000  # Default $1000 savings
                    elif benefit_type == 'time':
                        bi_data.time_savings = bi_data.time_savings or 5  # Default 5 hours saved
                    break
    
    async def _extract_challenges_and_solutions(self, text: str, bi_data: BusinessIntelligenceData):
        """Extract business challenges and solutions from text."""
        
        # Look for challenge indicators
        challenge_keywords = ['challenge', 'problem', 'issue', 'difficulty', 'struggle', 'pain point']
        solution_keywords = ['solution', 'solve', 'resolve', 'fix', 'address', 'overcome']
        
        for keyword in challenge_keywords:
            if keyword in text:
                bi_data.business_challenge = f"Addresses {keyword} in workflow automation"
                break
        
        for keyword in solution_keywords:
            if keyword in text:
                bi_data.business_solution = f"Provides {keyword} through automated workflow"
                break
        
        # Extract business advantage
        advantage_keywords = ['advantage', 'benefit', 'competitive', 'edge', 'superior']
        for keyword in advantage_keywords:
            if keyword in text:
                bi_data.business_advantage = f"Provides {keyword} through workflow automation"
                break
    
    async def _calculate_business_value_score(self, bi_data: BusinessIntelligenceData):
        """Calculate overall business value score."""
        
        score = 0.0
        factors = 0
        
        # Revenue impact
        if bi_data.revenue_impact:
            score += min(bi_data.revenue_impact / 10000, 1.0) * 0.3
            factors += 1
        
        # Cost savings
        if bi_data.cost_savings:
            score += min(bi_data.cost_savings / 5000, 1.0) * 0.25
            factors += 1
        
        # Time savings
        if bi_data.time_savings:
            score += min(bi_data.time_savings / 20, 1.0) * 0.2
            factors += 1
        
        # Efficiency gains
        if bi_data.efficiency_gains:
            score += bi_data.efficiency_gains * 0.15
            factors += 1
        
        # Quality improvements
        if bi_data.quality_improvements:
            score += bi_data.quality_improvements * 0.1
            factors += 1
        
        # Normalize score
        if factors > 0:
            bi_data.business_value_score = round(score / factors * 100, 2)
        else:
            bi_data.business_value_score = 50.0  # Default neutral score
    
    def _extract_business_process(self, title: str, description: str, use_case: str) -> Optional[str]:
        """Extract business process from text."""
        
        process_keywords = ['process', 'workflow', 'procedure', 'operation', 'task']
        
        for keyword in process_keywords:
            if keyword in title or keyword in description or keyword in use_case:
                return f"Automated {keyword} management"
        
        return None
    
    def _extract_business_outcome(self, description: str, use_case: str) -> Optional[str]:
        """Extract business outcome from text."""
        
        outcome_keywords = ['outcome', 'result', 'goal', 'objective', 'target', 'achievement']
        
        for keyword in outcome_keywords:
            if keyword in description or keyword in use_case:
                return f"Improved {keyword} through automation"
        
        return None
    
    def _extract_business_goal(self, description: str, use_case: str) -> Optional[str]:
        """Extract business goal from text."""
        
        goal_keywords = ['goal', 'objective', 'target', 'aim', 'purpose', 'mission']
        
        for keyword in goal_keywords:
            if keyword in description or keyword in use_case:
                return f"Achieve {keyword} through workflow automation"
        
        return None
    
    def _extract_business_requirements(self, use_case: str) -> Optional[str]:
        """Extract business requirements from use case."""
        
        requirement_keywords = ['require', 'need', 'must', 'should', 'necessary']
        
        for keyword in requirement_keywords:
            if keyword in use_case:
                return f"Workflow addresses {keyword} in business operations"
        
        return None
    
    def _extract_business_constraints(self, use_case: str) -> Optional[str]:
        """Extract business constraints from use case."""
        
        constraint_keywords = ['constraint', 'limit', 'restriction', 'boundary', 'barrier']
        
        for keyword in constraint_keywords:
            if keyword in use_case:
                return f"Workflow works within {keyword} limitations"
        
        return None
    
    def _extract_business_risks(self, use_case: str) -> Optional[str]:
        """Extract business risks from use case."""
        
        risk_keywords = ['risk', 'threat', 'danger', 'vulnerability', 'exposure']
        
        for keyword in risk_keywords:
            if keyword in use_case:
                return f"Workflow mitigates {keyword} in business operations"
        
        return None
    
    def _analyze_automation_potential(self, text: str) -> Optional[str]:
        """Analyze automation potential from text."""
        
        automation_keywords = ['automate', 'automatic', 'manual', 'hand', 'process']
        
        automation_count = sum(1 for keyword in automation_keywords if keyword in text)
        
        if automation_count >= 2:
            return "High automation potential - reduces manual processes"
        elif automation_count >= 1:
            return "Medium automation potential - some manual processes"
        else:
            return "Low automation potential - limited automation focus"
    
    def _analyze_optimization_potential(self, text: str) -> Optional[str]:
        """Analyze optimization potential from text."""
        
        optimization_keywords = ['optimize', 'improve', 'enhance', 'better', 'efficient']
        
        optimization_count = sum(1 for keyword in optimization_keywords if keyword in text)
        
        if optimization_count >= 2:
            return "High optimization potential - focuses on improvement"
        elif optimization_count >= 1:
            return "Medium optimization potential - some improvement focus"
        else:
            return "Low optimization potential - limited improvement focus"
    
    def _analyze_innovation_potential(self, text: str) -> Optional[str]:
        """Analyze innovation potential from text."""
        
        innovation_keywords = ['innovative', 'new', 'cutting-edge', 'advanced', 'modern']
        
        innovation_count = sum(1 for keyword in innovation_keywords if keyword in text)
        
        if innovation_count >= 2:
            return "High innovation potential - uses advanced techniques"
        elif innovation_count >= 1:
            return "Medium innovation potential - some advanced features"
        else:
            return "Low innovation potential - standard approaches"
    
    def _analyze_compliance_requirements(self, text: str) -> Optional[str]:
        """Analyze compliance requirements from text."""
        
        compliance_keywords = ['compliance', 'regulation', 'policy', 'standard', 'audit']
        
        compliance_count = sum(1 for keyword in compliance_keywords if keyword in text)
        
        if compliance_count >= 2:
            return "High compliance requirements - multiple regulatory considerations"
        elif compliance_count >= 1:
            return "Medium compliance requirements - some regulatory considerations"
        else:
            return "Low compliance requirements - minimal regulatory focus"
    
    def _analyze_security_requirements(self, text: str) -> Optional[str]:
        """Analyze security requirements from text."""
        
        security_keywords = ['security', 'secure', 'privacy', 'protection', 'encryption']
        
        security_count = sum(1 for keyword in security_keywords if keyword in text)
        
        if security_count >= 2:
            return "High security requirements - multiple security considerations"
        elif security_count >= 1:
            return "Medium security requirements - some security considerations"
        else:
            return "Low security requirements - minimal security focus"
