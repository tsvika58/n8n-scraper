"""
Layer 6: Technical Details Extraction
Extracts technical specifications, API information, security requirements, and performance metrics.

This layer focuses on understanding the technical implementation details,
API endpoints, security considerations, performance characteristics,
and technical complexity of each workflow.

Author: RND Team - Comprehensive Scraping Expansion
Date: October 12, 2025
"""

import asyncio
import re
import json
from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass
from datetime import datetime

from loguru import logger

from src.scrapers.base import BaseExtractor


@dataclass
class TechnicalDetailsData:
    """Technical details data structure."""
    
    # API Information
    api_endpoints: Optional[List[Dict[str, Any]]] = None
    api_authentication_types: Optional[List[str]] = None
    api_rate_limits: Optional[Dict[str, Any]] = None
    
    # Security & Credentials
    credential_requirements: Optional[List[str]] = None
    credential_types: Optional[List[str]] = None
    security_requirements: Optional[List[str]] = None
    
    # Performance Metrics
    performance_metrics: Optional[Dict[str, Any]] = None
    execution_time: Optional[float] = None
    memory_usage: Optional[float] = None
    cpu_usage: Optional[float] = None
    
    # Error Handling
    error_handling_patterns: Optional[List[str]] = None
    retry_mechanisms: Optional[List[str]] = None
    fallback_strategies: Optional[List[str]] = None
    
    # Data Processing
    data_validation_rules: Optional[List[str]] = None
    data_transformation_rules: Optional[List[str]] = None
    
    # Workflow Structure
    workflow_triggers: Optional[List[str]] = None
    workflow_conditions: Optional[List[str]] = None
    workflow_actions: Optional[List[str]] = None
    workflow_branches: Optional[List[str]] = None
    workflow_loops: Optional[List[str]] = None
    workflow_parallelism: Optional[List[str]] = None
    
    # Workflow Management
    workflow_error_handling: Optional[List[str]] = None
    workflow_logging: Optional[List[str]] = None
    workflow_monitoring: Optional[List[str]] = None
    workflow_backup_strategies: Optional[List[str]] = None
    workflow_recovery_strategies: Optional[List[str]] = None
    workflow_scaling_strategies: Optional[List[str]] = None
    workflow_optimization_strategies: Optional[List[str]] = None
    
    # Development & Deployment
    workflow_testing_strategies: Optional[List[str]] = None
    workflow_deployment_strategies: Optional[List[str]] = None
    workflow_maintenance_strategies: Optional[List[str]] = None
    workflow_support_strategies: Optional[List[str]] = None
    
    # Documentation & Examples
    workflow_documentation_level: Optional[str] = None
    workflow_tutorial_level: Optional[str] = None
    workflow_example_count: int = 0
    workflow_template_count: int = 0
    
    # Capability Levels
    workflow_customization_level: Optional[str] = None
    workflow_configuration_level: Optional[str] = None
    workflow_integration_level: Optional[str] = None
    workflow_extension_level: Optional[str] = None
    workflow_automation_level: Optional[str] = None
    workflow_intelligence_level: Optional[str] = None


class TechnicalDetailsExtractor(BaseExtractor):
    """
    Extracts technical details from workflow pages.
    
    This extractor analyzes workflow structure, content, and metadata
    to extract technical specifications, API information, security requirements,
    and performance characteristics.
    """
    
    def __init__(self):
        super().__init__("Layer 6 - Technical Details")
        
        # API patterns
        self.api_patterns = {
            'endpoints': [
                r'https?://[^\s<>"\']+',
                r'api/[^\s<>"\']+',
                r'endpoint[s]?[:\s]*([^\s\n]+)',
                r'url[s]?[:\s]*([^\s\n]+)'
            ],
            'authentication': [
                r'auth[^\s]*[:\s]*([^\s\n]+)',
                r'bearer[^\s]*',
                r'api[^\s]*key[^\s]*',
                r'oauth[^\s]*',
                r'token[^\s]*'
            ],
            'rate_limits': [
                r'rate[^\s]*limit[^\s]*[:\s]*(\d+)',
                r'(\d+)\s*request[s]?\s*per\s*(?:hour|minute|second)',
                r'throttle[^\s]*[:\s]*(\d+)'
            ]
        }
        
        # Security patterns
        self.security_patterns = {
            'credentials': [
                r'credential[s]?[^\s]*',
                r'password[s]?[^\s]*',
                r'secret[s]?[^\s]*',
                r'key[s]?[^\s]*',
                r'token[s]?[^\s]*'
            ],
            'security': [
                r'security[^\s]*',
                r'encrypt[^\s]*',
                r'secure[^\s]*',
                r'protect[^\s]*',
                r'privacy[^\s]*'
            ]
        }
        
        # Performance patterns
        self.performance_patterns = {
            'execution_time': [
                r'execution[^\s]*time[:\s]*(\d+(?:\.\d+)?)\s*(?:seconds?|minutes?|hours?)',
                r'runtime[:\s]*(\d+(?:\.\d+)?)\s*(?:seconds?|minutes?|hours?)',
                r'(\d+(?:\.\d+)?)\s*seconds?[^\s]*execution'
            ],
            'memory': [
                r'memory[^\s]*[:\s]*(\d+(?:\.\d+)?)\s*(?:mb|gb|kb)',
                r'ram[^\s]*[:\s]*(\d+(?:\.\d+)?)\s*(?:mb|gb|kb)'
            ],
            'cpu': [
                r'cpu[^\s]*[:\s]*(\d+(?:\.\d+)?)\s*%',
                r'processor[^\s]*[:\s]*(\d+(?:\.\d+)?)\s*%'
            ]
        }
        
        # Error handling patterns
        self.error_patterns = [
            r'error[^\s]*handling',
            r'retry[^\s]*mechanism',
            r'fallback[^\s]*strateg',
            r'catch[^\s]*error',
            r'handle[^\s]*exception'
        ]
        
        # Workflow structure patterns
        self.structure_patterns = {
            'triggers': [r'trigger[s]?[^\s]*', r'start[s]?[^\s]*', r'initiate[s]?[^\s]*'],
            'conditions': [r'condition[s]?[^\s]*', r'if[^\s]*', r'when[^\s]*'],
            'actions': [r'action[s]?[^\s]*', r'do[^\s]*', r'execute[s]?[^\s]*'],
            'branches': [r'branch[s]?[^\s]*', r'split[s]?[^\s]*', r'fork[s]?[^\s]*'],
            'loops': [r'loop[s]?[^\s]*', r'repeat[s]?[^\s]*', r'iterate[s]?[^\s]*'],
            'parallelism': [r'parallel[^\s]*', r'concurrent[^\s]*', r'simultaneous[^\s]*']
        }
        
        # Documentation levels
        self.documentation_levels = {
            'high': ['tutorial', 'guide', 'documentation', 'example', 'demo'],
            'medium': ['instruction', 'setup', 'config', 'help'],
            'low': ['basic', 'simple', 'quick']
        }
        
        # Capability levels
        self.capability_levels = {
            'high': ['advanced', 'complex', 'sophisticated', 'enterprise'],
            'medium': ['intermediate', 'moderate', 'standard'],
            'low': ['basic', 'simple', 'beginner', 'easy']
        }
    
    async def extract(self, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract technical details from workflow.
        
        Args:
            workflow_data: Combined data from previous layers
            
        Returns:
            Dictionary with technical details data
        """
        logger.info(f"Starting {self.layer_name} extraction for workflow {workflow_data.get('workflow_id')}")
        
        try:
            # Initialize technical details data
            tech_data = TechnicalDetailsData()
            
            # Extract from workflow structure
            await self._extract_from_structure(workflow_data, tech_data)
            
            # Extract from content
            await self._extract_from_content(workflow_data, tech_data)
            
            # Extract from metadata
            await self._extract_from_metadata(workflow_data, tech_data)
            
            # Analyze technical complexity
            await self._analyze_technical_complexity(workflow_data, tech_data)
            
            # Convert to dictionary
            result = {
                'success': True,
                'data': tech_data.__dict__,
                'extraction_time': 0.0,
                'layer': self.layer_name
            }
            
            logger.info(f"Successfully extracted technical details: {len(result['data'])} fields")
            return result
            
        except Exception as e:
            logger.error(f"Error in {self.layer_name} extraction: {e}")
            return {
                'success': False,
                'error': str(e),
                'extraction_time': 0.0,
                'layer': self.layer_name
            }
    
    async def _extract_from_structure(self, workflow_data: Dict[str, Any], tech_data: TechnicalDetailsData):
        """Extract technical details from workflow structure."""
        
        # Get structure from layer 2
        layer2_data = workflow_data.get('layers', {}).get('layer2', {}).get('data', {})
        
        # Extract node types and workflow JSON
        node_types = layer2_data.get('node_types', [])
        workflow_json = layer2_data.get('data')
        
        if workflow_json:
            # Analyze workflow JSON for technical details
            await self._analyze_workflow_json(workflow_json, tech_data)
        
        # Extract workflow structure patterns
        await self._extract_workflow_structure(node_types, tech_data)
        
        # Extract API information from node types
        await self._extract_api_info(node_types, tech_data)
        
        # Extract security requirements from node types
        await self._extract_security_requirements(node_types, tech_data)
    
    async def _extract_from_content(self, workflow_data: Dict[str, Any], tech_data: TechnicalDetailsData):
        """Extract technical details from workflow content."""
        
        # Get content from layer 3
        layer3_data = workflow_data.get('layers', {}).get('layer3', {}).get('data', {})
        
        explainer_text = layer3_data.get('explainer_text', '')
        setup_instructions = layer3_data.get('setup_instructions', '')
        use_instructions = layer3_data.get('use_instructions', '')
        
        # Combine all text for analysis
        full_text = f"{explainer_text} {setup_instructions} {use_instructions}".lower()
        
        # Extract API information from text
        await self._extract_api_from_text(full_text, tech_data)
        
        # Extract performance metrics from text
        await self._extract_performance_from_text(full_text, tech_data)
        
        # Extract error handling patterns from text
        await self._extract_error_handling_from_text(full_text, tech_data)
        
        # Extract workflow structure from text
        await self._extract_structure_from_text(full_text, tech_data)
        
        # Analyze documentation level
        await self._analyze_documentation_level(full_text, tech_data)
        
        # Count examples and templates
        await self._count_examples_and_templates(full_text, tech_data)
    
    async def _extract_from_metadata(self, workflow_data: Dict[str, Any], tech_data: TechnicalDetailsData):
        """Extract technical details from workflow metadata."""
        
        # Get metadata from layer 1
        layer1_data = workflow_data.get('layers', {}).get('layer1', {}).get('data', {})
        
        # Extract technical complexity indicators
        title = layer1_data.get('title', '').lower()
        description = layer1_data.get('description', '').lower()
        use_case = layer1_data.get('use_case', '').lower()
        
        full_text = f"{title} {description} {use_case}"
        
        # Analyze capability levels
        await self._analyze_capability_levels(full_text, tech_data)
    
    async def _analyze_technical_complexity(self, workflow_data: Dict[str, Any], tech_data: TechnicalDetailsData):
        """Analyze overall technical complexity."""
        
        # Get structure data
        layer2_data = workflow_data.get('layers', {}).get('layer2', {}).get('data', {})
        node_count = layer2_data.get('node_count', 0)
        connection_count = layer2_data.get('connection_count', 0)
        
        # Calculate complexity based on structure
        complexity_score = 0
        
        # Node count complexity
        if node_count > 20:
            complexity_score += 3
        elif node_count > 10:
            complexity_score += 2
        elif node_count > 5:
            complexity_score += 1
        
        # Connection complexity
        if connection_count > 30:
            complexity_score += 3
        elif connection_count > 15:
            complexity_score += 2
        elif connection_count > 5:
            complexity_score += 1
        
        # API complexity
        if tech_data.api_endpoints and len(tech_data.api_endpoints) > 5:
            complexity_score += 2
        elif tech_data.api_endpoints and len(tech_data.api_endpoints) > 2:
            complexity_score += 1
        
        # Security complexity
        if tech_data.security_requirements and len(tech_data.security_requirements) > 3:
            complexity_score += 2
        elif tech_data.security_requirements and len(tech_data.security_requirements) > 1:
            complexity_score += 1
        
        # Set automation level based on complexity
        if complexity_score >= 8:
            tech_data.workflow_automation_level = "high"
        elif complexity_score >= 4:
            tech_data.workflow_automation_level = "medium"
        else:
            tech_data.workflow_automation_level = "low"
        
        # Set intelligence level based on structure
        if node_count > 15 and connection_count > 20:
            tech_data.workflow_intelligence_level = "high"
        elif node_count > 8 and connection_count > 10:
            tech_data.workflow_intelligence_level = "medium"
        else:
            tech_data.workflow_intelligence_level = "low"
    
    async def _analyze_workflow_json(self, workflow_json: Any, tech_data: TechnicalDetailsData):
        """Analyze workflow JSON for technical details."""
        
        try:
            if isinstance(workflow_json, str):
                workflow_data = json.loads(workflow_json)
            else:
                workflow_data = workflow_json
            
            # Extract nodes
            nodes = workflow_data.get('nodes', [])
            
            # Analyze each node for technical details
            api_endpoints = []
            credential_types = set()
            security_requirements = set()
            
            for node in nodes:
                node_type = node.get('type', '')
                node_data = node.get('parameters', {})
                
                # Extract API endpoints
                if 'url' in node_data:
                    api_endpoints.append({
                        'url': node_data['url'],
                        'method': node_data.get('method', 'GET'),
                        'node_type': node_type
                    })
                
                # Extract credential types
                if 'authentication' in node_data:
                    credential_types.add(node_data['authentication'])
                
                # Extract security requirements
                if 'security' in node_data or 'ssl' in node_data:
                    security_requirements.add('ssl_required')
                
                if 'oauth' in str(node_data).lower():
                    security_requirements.add('oauth_required')
                
                if 'api_key' in str(node_data).lower():
                    security_requirements.add('api_key_required')
            
            tech_data.api_endpoints = api_endpoints if api_endpoints else None
            tech_data.credential_types = list(credential_types) if credential_types else None
            tech_data.security_requirements = list(security_requirements) if security_requirements else None
            
        except Exception as e:
            logger.warning(f"Error analyzing workflow JSON: {e}")
    
    async def _extract_workflow_structure(self, node_types: List[str], tech_data: TechnicalDetailsData):
        """Extract workflow structure from node types."""
        
        # Categorize nodes by function
        triggers = []
        conditions = []
        actions = []
        branches = []
        loops = []
        
        for node_type in node_types:
            node_lower = node_type.lower()
            
            if any(keyword in node_lower for keyword in ['trigger', 'webhook', 'schedule', 'start']):
                triggers.append(node_type)
            elif any(keyword in node_lower for keyword in ['condition', 'if', 'switch', 'filter']):
                conditions.append(node_type)
            elif any(keyword in node_lower for keyword in ['action', 'http', 'email', 'slack']):
                actions.append(node_type)
            elif any(keyword in node_lower for keyword in ['split', 'merge', 'branch']):
                branches.append(node_type)
            elif any(keyword in node_lower for keyword in ['loop', 'repeat', 'iterate']):
                loops.append(node_type)
        
        tech_data.workflow_triggers = triggers if triggers else None
        tech_data.workflow_conditions = conditions if conditions else None
        tech_data.workflow_actions = actions if actions else None
        tech_data.workflow_branches = branches if branches else None
        tech_data.workflow_loops = loops if loops else None
    
    async def _extract_api_info(self, node_types: List[str], tech_data: TechnicalDetailsData):
        """Extract API information from node types."""
        
        api_authentication_types = set()
        
        for node_type in node_types:
            node_lower = node_type.lower()
            
            if 'http' in node_lower or 'api' in node_lower:
                if 'oauth' in node_lower:
                    api_authentication_types.add('oauth')
                elif 'bearer' in node_lower:
                    api_authentication_types.add('bearer_token')
                elif 'basic' in node_lower:
                    api_authentication_types.add('basic_auth')
                elif 'api_key' in node_lower:
                    api_authentication_types.add('api_key')
                else:
                    api_authentication_types.add('http')
        
        tech_data.api_authentication_types = list(api_authentication_types) if api_authentication_types else None
    
    async def _extract_security_requirements(self, node_types: List[str], tech_data: TechnicalDetailsData):
        """Extract security requirements from node types."""
        
        security_requirements = set()
        credential_requirements = set()
        
        for node_type in node_types:
            node_lower = node_type.lower()
            
            if 'oauth' in node_lower:
                security_requirements.add('oauth_authentication')
                credential_requirements.add('oauth_credentials')
            elif 'api_key' in node_lower:
                security_requirements.add('api_key_authentication')
                credential_requirements.add('api_key')
            elif 'password' in node_lower:
                security_requirements.add('password_authentication')
                credential_requirements.add('username_password')
            elif 'ssl' in node_lower or 'https' in node_lower:
                security_requirements.add('ssl_encryption')
            elif 'encrypt' in node_lower:
                security_requirements.add('data_encryption')
        
        tech_data.security_requirements = list(security_requirements) if security_requirements else None
        tech_data.credential_requirements = list(credential_requirements) if credential_requirements else None
    
    async def _extract_api_from_text(self, text: str, tech_data: TechnicalDetailsData):
        """Extract API information from text."""
        
        # Extract API endpoints
        for pattern in self.api_patterns['endpoints']:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                if not tech_data.api_endpoints:
                    tech_data.api_endpoints = []
                for match in matches:
                    tech_data.api_endpoints.append({
                        'url': match,
                        'method': 'GET',
                        'source': 'text_extraction'
                    })
        
        # Extract authentication types
        auth_types = set()
        for pattern in self.api_patterns['authentication']:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                auth_types.add(match.lower())
        
        if auth_types:
            tech_data.api_authentication_types = list(auth_types)
        
        # Extract rate limits
        rate_limits = {}
        for pattern in self.api_patterns['rate_limits']:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                rate_limits['requests_per_minute'] = int(matches[0])
                break
        
        if rate_limits:
            tech_data.api_rate_limits = rate_limits
    
    async def _extract_performance_from_text(self, text: str, tech_data: TechnicalDetailsData):
        """Extract performance metrics from text."""
        
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
                    tech_data.execution_time = time_value
                    break
                except ValueError:
                    continue
        
        # Extract memory usage
        for pattern in self.performance_patterns['memory']:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                try:
                    memory_value = float(matches[0])
                    # Convert to MB
                    if 'gb' in text.lower():
                        memory_value *= 1024
                    elif 'kb' in text.lower():
                        memory_value /= 1024
                    tech_data.memory_usage = memory_value
                    break
                except ValueError:
                    continue
        
        # Extract CPU usage
        for pattern in self.performance_patterns['cpu']:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                try:
                    tech_data.cpu_usage = float(matches[0])
                    break
                except ValueError:
                    continue
    
    async def _extract_error_handling_from_text(self, text: str, tech_data: TechnicalDetailsData):
        """Extract error handling patterns from text."""
        
        error_patterns = []
        retry_mechanisms = []
        fallback_strategies = []
        
        for pattern in self.error_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                error_patterns.append(pattern)
        
        # Look for retry mechanisms
        if 'retry' in text.lower():
            retry_mechanisms.append('automatic_retry')
        if 'fallback' in text.lower():
            fallback_strategies.append('fallback_strategy')
        if 'catch' in text.lower() or 'handle' in text.lower():
            error_patterns.append('error_handling')
        
        tech_data.error_handling_patterns = error_patterns if error_patterns else None
        tech_data.retry_mechanisms = retry_mechanisms if retry_mechanisms else None
        tech_data.fallback_strategies = fallback_strategies if fallback_strategies else None
    
    async def _extract_structure_from_text(self, text: str, tech_data: TechnicalDetailsData):
        """Extract workflow structure from text."""
        
        for structure_type, patterns in self.structure_patterns.items():
            found_patterns = []
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    found_patterns.append(pattern)
            
            if found_patterns:
                attr_name = f"workflow_{structure_type}"
                setattr(tech_data, attr_name, found_patterns)
    
    async def _analyze_documentation_level(self, text: str, tech_data: TechnicalDetailsData):
        """Analyze documentation level from text."""
        
        doc_score = 0
        
        for level, keywords in self.documentation_levels.items():
            for keyword in keywords:
                if keyword in text:
                    if level == 'high':
                        doc_score += 3
                    elif level == 'medium':
                        doc_score += 2
                    else:
                        doc_score += 1
        
        if doc_score >= 6:
            tech_data.workflow_documentation_level = "high"
        elif doc_score >= 3:
            tech_data.workflow_documentation_level = "medium"
        else:
            tech_data.workflow_documentation_level = "low"
    
    async def _count_examples_and_templates(self, text: str, tech_data: TechnicalDetailsData):
        """Count examples and templates in text."""
        
        # Count examples
        example_patterns = [
            r'example[s]?[^\s]*',
            r'demo[s]?[^\s]*',
            r'sample[s]?[^\s]*',
            r'test[s]?[^\s]*'
        ]
        
        example_count = 0
        for pattern in example_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            example_count += len(matches)
        
        tech_data.workflow_example_count = example_count
        
        # Count templates
        template_patterns = [
            r'template[s]?[^\s]*',
            r'boilerplate[^\s]*',
            r'starter[^\s]*'
        ]
        
        template_count = 0
        for pattern in template_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            template_count += len(matches)
        
        tech_data.workflow_template_count = template_count
    
    async def _analyze_capability_levels(self, text: str, tech_data: TechnicalDetailsData):
        """Analyze capability levels from text."""
        
        # Analyze customization level
        customization_score = 0
        for level, keywords in self.capability_levels.items():
            for keyword in keywords:
                if keyword in text:
                    if level == 'high':
                        customization_score += 3
                    elif level == 'medium':
                        customization_score += 2
                    else:
                        customization_score += 1
        
        if customization_score >= 6:
            tech_data.workflow_customization_level = "high"
        elif customization_score >= 3:
            tech_data.workflow_customization_level = "medium"
        else:
            tech_data.workflow_customization_level = "low"
        
        # Analyze configuration level
        if 'config' in text or 'setting' in text or 'parameter' in text:
            tech_data.workflow_configuration_level = "high"
        elif 'setup' in text or 'install' in text:
            tech_data.workflow_configuration_level = "medium"
        else:
            tech_data.workflow_configuration_level = "low"
        
        # Analyze integration level
        if 'integration' in text or 'api' in text or 'webhook' in text:
            tech_data.workflow_integration_level = "high"
        elif 'connect' in text or 'link' in text:
            tech_data.workflow_integration_level = "medium"
        else:
            tech_data.workflow_integration_level = "low"
        
        # Analyze extension level
        if 'extend' in text or 'plugin' in text or 'addon' in text:
            tech_data.workflow_extension_level = "high"
        elif 'customize' in text or 'modify' in text:
            tech_data.workflow_extension_level = "medium"
        else:
            tech_data.workflow_extension_level = "low"
