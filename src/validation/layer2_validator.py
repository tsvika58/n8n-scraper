"""
Layer 2 JSON Structure Validator - SCRAPE-004
Validates workflow JSON structure integrity
"""

from typing import Dict, List
import logging

logger = logging.getLogger(__name__)


class Layer2Validator:
    """Validates Layer 2 JSON structure and integrity."""
    
    def __init__(self):
        """Initialize Layer 2 validator."""
        logger.info("Layer 2 Validator initialized")
    
    def validate(self, workflow_json: Dict) -> Dict:
        """
        Validate Layer 2 workflow JSON structure.
        
        Args:
            workflow_json: Complete workflow JSON
            
        Returns:
            dict with:
                - score: float (0-100)
                - issues: list of issue descriptions
                - valid: bool (score >= 75)
        """
        score = 0
        issues = []
        
        # Check if workflow_json exists and is dict (10 points)
        if not workflow_json or not isinstance(workflow_json, dict):
            issues.append("Invalid or missing JSON structure")
            return {'score': 0, 'issues': issues, 'valid': False, 'layer': 'layer2'}
        else:
            score += 10
        
        # Check for 'workflow' key (10 points)
        workflow = workflow_json.get('workflow', {})
        if not workflow:
            issues.append("Missing 'workflow' key in JSON")
            return {'score': score, 'issues': issues, 'valid': False, 'layer': 'layer2'}
        else:
            score += 10
        
        # Validate nodes array (30 points)
        nodes = workflow.get('nodes', [])
        if not isinstance(nodes, list):
            issues.append("Nodes is not an array")
        elif len(nodes) == 0:
            issues.append("Workflow has no nodes")
        else:
            score += 20
            
            # Check nodes have required structure
            valid_nodes = 0
            for node in nodes:
                if isinstance(node, dict) and all(k in node for k in ['id', 'name', 'type']):
                    valid_nodes += 1
            
            if valid_nodes == len(nodes):
                score += 10
            elif valid_nodes > 0:
                issues.append(f"Some nodes missing required fields ({valid_nodes}/{len(nodes)} valid)")
                score += 5
            else:
                issues.append("All nodes missing required fields (id, name, type)")
        
        # Validate connections (25 points)
        connections = workflow.get('connections', {})
        if not isinstance(connections, dict):
            issues.append("Connections is not a dict")
        elif len(connections) == 0:
            issues.append("Workflow has no connections")
        else:
            score += 20
            
            # Check connections structure
            valid_connections = True
            for node_name, conn_data in connections.items():
                if not isinstance(conn_data, dict):
                    valid_connections = False
                    break
            
            if valid_connections:
                score += 5
            else:
                issues.append("Invalid connection structure")
        
        # Validate metadata (10 points)
        meta = workflow.get('meta', {})
        if isinstance(meta, dict) and meta:
            score += 10
        else:
            issues.append("Missing or invalid workflow metadata")
        
        # Check for node type diversity (15 points)
        if nodes:
            node_types = set(node.get('type', '') for node in nodes if isinstance(node, dict))
            if len(node_types) >= 3:
                score += 15
            elif len(node_types) >= 2:
                score += 10
                issues.append("Limited node type diversity (only 2 types)")
            else:
                score += 5
                issues.append("Very limited node type diversity (1 type)")
        
        # Calculate validity
        valid = score >= 75
        
        return {
            'score': min(score, 100),
            'issues': issues,
            'valid': valid,
            'layer': 'layer2'
        }


def main():
    """Test Layer 2 validator."""
    validator = Layer2Validator()
    
    # Test with good JSON
    good_json = {
        'workflow': {
            'nodes': [
                {'id': '1', 'name': 'Start', 'type': 'n8n-nodes-base.start'},
                {'id': '2', 'name': 'HTTP', 'type': 'n8n-nodes-base.httpRequest'},
                {'id': '3', 'name': 'Set', 'type': 'n8n-nodes-base.set'}
            ],
            'connections': {
                'Start': {'main': [[{'node': 'HTTP', 'type': 'main', 'index': 0}]]},
                'HTTP': {'main': [[{'node': 'Set', 'type': 'main', 'index': 0}]]}
            },
            'meta': {'instanceId': 'test123'}
        }
    }
    
    result = validator.validate(good_json)
    print(f"Good JSON Score: {result['score']}")
    print(f"Valid: {result['valid']}")
    print(f"Issues: {len(result['issues'])}")
    
    # Test with poor JSON
    poor_json = {
        'workflow': {
            'nodes': [],
            'connections': {}
        }
    }
    
    result2 = validator.validate(poor_json)
    print(f"\nPoor JSON Score: {result2['score']}")
    print(f"Issues: {result2['issues']}")


if __name__ == "__main__":
    main()





