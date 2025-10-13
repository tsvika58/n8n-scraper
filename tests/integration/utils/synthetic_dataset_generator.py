"""
Synthetic Dataset Generator for SCRAPE-010 Integration Testing.

Generates realistic extraction results representing 500 workflows
for fast, reliable integration testing without actual scraping.

Author: Dev1
Task: SCRAPE-010
Date: October 11, 2025
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict
import random


class SyntheticDatasetGenerator:
    """Generate realistic synthetic workflow extraction results."""
    
    # Realistic workflow titles and descriptions
    WORKFLOW_TEMPLATES = [
        {
            'title': 'Send Slack notifications from Google Sheets updates',
            'description': 'Automate Slack notifications whenever Google Sheets data changes',
            'use_case': 'Team Communication',
            'categories': ['Communication', 'Productivity'],
            'tags': ['slack', 'google-sheets', 'automation'],
            'node_types': ['googleSheets', 'slack', 'webhook', 'set'],
            'node_count_range': (5, 12)
        },
        {
            'title': 'CRM to Email Marketing Sync',
            'description': 'Sync contacts from CRM to email marketing platform',
            'use_case': 'Marketing Automation',
            'categories': ['Marketing', 'Sales'],
            'tags': ['crm', 'email', 'mailchimp', 'automation'],
            'node_types': ['httpRequest', 'set', 'if', 'function'],
            'node_count_range': (8, 15)
        },
        {
            'title': 'GitHub Issue to Project Management',
            'description': 'Create project tasks from GitHub issues automatically',
            'use_case': 'Project Management',
            'categories': ['Development', 'Productivity'],
            'tags': ['github', 'project-management', 'automation'],
            'node_types': ['github', 'httpRequest', 'set'],
            'node_count_range': (6, 10)
        },
        {
            'title': 'AI-Powered Customer Support',
            'description': 'Automate customer support with AI responses',
            'use_case': 'Customer Support',
            'categories': ['AI', 'Customer Service'],
            'tags': ['ai', 'openai', 'support', 'automation'],
            'node_types': ['openAI', 'httpRequest', 'if', 'set'],
            'node_count_range': (10, 20)
        },
        {
            'title': 'Data Pipeline ETL',
            'description': 'Extract, transform, and load data between systems',
            'use_case': 'Data Engineering',
            'categories': ['Data', 'Development'],
            'tags': ['etl', 'data', 'transformation'],
            'node_types': ['httpRequest', 'function', 'set', 'postgres'],
            'node_count_range': (12, 25)
        }
    ]
    
    AUTHORS = [
        {'name': 'John Smith', 'url': 'https://n8n.io/creators/john-smith'},
        {'name': 'Sarah Chen', 'url': 'https://n8n.io/creators/sarah-chen'},
        {'name': 'Mike Johnson', 'url': 'https://n8n.io/creators/mike-johnson'},
        {'name': 'Emily Davis', 'url': 'https://n8n.io/creators/emily-davis'},
        {'name': 'Alex Martinez', 'url': 'https://n8n.io/creators/alex-martinez'}
    ]
    
    def __init__(self):
        self.dataset = []
        random.seed(42)  # Reproducible results
    
    def generate_workflow_extraction_result(
        self,
        workflow_id: str,
        template: Dict,
        layer1_success: bool = True,
        layer2_success: bool = True,
        layer3_success: bool = True
    ) -> Dict:
        """Generate a complete E2E extraction result for a workflow."""
        
        # Random variations
        node_count = random.randint(*template['node_count_range'])
        connection_count = node_count - 1 if node_count > 0 else 0
        views = random.randint(100, 10000)
        shares = random.randint(10, 500)
        processing_time = random.uniform(15.0, 45.0)
        
        # Quality score based on layer success
        quality_score = 0
        if layer1_success:
            quality_score += 30
        if layer2_success:
            quality_score += 40
        if layer3_success:
            quality_score += 30
        
        # Add randomness
        quality_score += random.uniform(-5, 5)
        quality_score = max(0, min(100, quality_score))
        
        # Create extraction result
        result = {
            'workflow_id': workflow_id,
            'url': f'https://n8n.io/workflows/{workflow_id}',
            'processing_time': processing_time,
            'quality_score': quality_score,
            'extracted_at': datetime.utcnow().isoformat(),
            'layers': {}
        }
        
        # Layer 1: Metadata
        if layer1_success:
            result['layers']['layer1'] = {
                'success': True,
                'title': template['title'],
                'description': template['description'],
                'use_case': template['use_case'],
                'author': random.choice(self.AUTHORS),
                'categories': template['categories'],
                'tags': template['tags'],
                'views': views,
                'shares': shares,
                'created_at': (datetime.utcnow() - timedelta(days=random.randint(30, 365))).isoformat(),
                'updated_at': (datetime.utcnow() - timedelta(days=random.randint(1, 30))).isoformat(),
                'extraction_time': random.uniform(2.0, 5.0)
            }
        else:
            result['layers']['layer1'] = {
                'success': False,
                'error': 'Failed to extract metadata',
                'extraction_time': random.uniform(1.0, 3.0)
            }
        
        # Layer 2: Workflow JSON
        if layer2_success:
            result['layers']['layer2'] = {
                'success': True,
                'node_count': node_count,
                'connection_count': connection_count,
                'node_types': template['node_types'],
                'extraction_type': 'full',
                'fallback_used': False,
                'data': {
                    'nodes': [
                        {
                            'id': f'node-{i}',
                            'type': template['node_types'][i % len(template['node_types'])],
                            'name': f'Node {i}',
                            'parameters': {}
                        }
                        for i in range(node_count)
                    ],
                    'connections': {}
                },
                'extraction_time': random.uniform(5.0, 15.0)
            }
        else:
            # Simulate Layer 2 failure (common - 60% success rate)
            result['layers']['layer2'] = {
                'success': False,
                'node_count': 0,
                'connection_count': 0,
                'node_types': [],
                'extraction_type': 'failed',
                'fallback_used': False,
                'error': 'Workflow JSON not accessible',
                'extraction_time': random.uniform(3.0, 8.0)
            }
        
        # Layer 3: Explainer Content
        if layer3_success:
            explainer_text = f"""
            {template['title']}
            
            {template['description']}
            
            ## Overview
            This workflow demonstrates {template['use_case'].lower()}.
            
            ## Setup Instructions
            1. Connect your accounts
            2. Configure the workflow
            3. Test the automation
            
            ## How to Use
            The workflow will automatically process items when triggered.
            """
            
            result['layers']['layer3'] = {
                'success': True,
                'explainer_text': explainer_text.strip(),
                'explainer_html': f'<div><h1>{template["title"]}</h1><p>{template["description"]}</p></div>',
                'setup_instructions': 'Connect accounts and configure settings',
                'use_instructions': 'Workflow runs automatically on trigger',
                'has_videos': random.random() < 0.3,  # 30% have videos
                'videos': self._generate_videos(workflow_id) if random.random() < 0.3 else [],
                'has_iframes': True,
                'iframe_count': 1,
                'extraction_time': random.uniform(3.0, 10.0)
            }
        else:
            result['layers']['layer3'] = {
                'success': False,
                'error': 'Explainer content not available',
                'extraction_time': random.uniform(2.0, 5.0)
            }
        
        return result
    
    def _generate_videos(self, workflow_id: str) -> List[Dict]:
        """Generate synthetic video data."""
        video_count = random.randint(1, 3)
        videos = []
        
        for i in range(video_count):
            video = {
                'url': f'https://youtube.com/watch?v=video_{workflow_id}_{i}',
                'video_id': f'video_{workflow_id}_{i}',
                'platform': 'youtube',
                'transcript': {
                    'text': f'This is a tutorial for workflow {workflow_id}. ' * 20,
                    'duration': random.randint(180, 600),
                    'language': 'en'
                }
            }
            videos.append(video)
        
        return videos
    
    def generate_dataset(self, total: int = 500) -> List[Dict]:
        """
        Generate complete synthetic dataset.
        
        Dataset composition:
        - 300 "good" workflows (all layers succeed, 80%+ quality)
        - 150 "challenging" workflows (Layer 2 fails, 50-70% quality)
        - 50 "edge case" workflows (various edge conditions)
        """
        print(f"🔧 Generating {total} synthetic workflow extraction results...")
        
        # Good workflows (60%)
        good_count = int(total * 0.6)
        print(f"  Generating {good_count} good workflows...")
        for i in range(good_count):
            template = random.choice(self.WORKFLOW_TEMPLATES)
            workflow_id = f'GOOD-{i:04d}'
            result = self.generate_workflow_extraction_result(
                workflow_id, template,
                layer1_success=True,
                layer2_success=True,
                layer3_success=True
            )
            self.dataset.append(result)
        
        # Challenging workflows (30% - Layer 2 issues)
        challenging_count = int(total * 0.3)
        print(f"  Generating {challenging_count} challenging workflows...")
        for i in range(challenging_count):
            template = random.choice(self.WORKFLOW_TEMPLATES)
            workflow_id = f'CHAL-{i:04d}'
            result = self.generate_workflow_extraction_result(
                workflow_id, template,
                layer1_success=True,
                layer2_success=False,  # Layer 2 fails
                layer3_success=True
            )
            self.dataset.append(result)
        
        # Edge case workflows (10%)
        edge_count = total - good_count - challenging_count
        print(f"  Generating {edge_count} edge case workflows...")
        for i in range(edge_count):
            template = random.choice(self.WORKFLOW_TEMPLATES)
            workflow_id = f'EDGE-{i:04d}'
            
            # Random edge conditions
            layer1 = random.random() < 0.9  # 90% success
            layer2 = random.random() < 0.4  # 40% success (challenging)
            layer3 = random.random() < 0.8  # 80% success
            
            result = self.generate_workflow_extraction_result(
                workflow_id, template,
                layer1_success=layer1,
                layer2_success=layer2,
                layer3_success=layer3
            )
            self.dataset.append(result)
        
        print(f"✅ Generated {len(self.dataset)} synthetic extraction results")
        print(f"   - Good: {good_count}")
        print(f"   - Challenging: {challenging_count}")
        print(f"   - Edge cases: {edge_count}")
        
        # Shuffle for realistic distribution
        random.shuffle(self.dataset)
        
        return self.dataset
    
    def save_dataset(self, output_path: str = None):
        """Save dataset to JSON file."""
        if output_path is None:
            output_path = Path(__file__).parent.parent.parent / "data" / "scrape_010_synthetic_dataset.json"
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(self.dataset, f, indent=2)
        
        print(f"✅ Dataset saved to: {output_path}")
        print(f"   Total size: {len(json.dumps(self.dataset)) / 1024:.1f} KB")
        
        return output_path
    
    def get_statistics(self) -> Dict:
        """Get dataset statistics."""
        if not self.dataset:
            return {}
        
        layer1_success = sum(1 for w in self.dataset if w['layers']['layer1']['success'])
        layer2_success = sum(1 for w in self.dataset if w['layers']['layer2']['success'])
        layer3_success = sum(1 for w in self.dataset if w['layers']['layer3']['success'])
        
        avg_quality = sum(w['quality_score'] for w in self.dataset) / len(self.dataset)
        avg_processing_time = sum(w['processing_time'] for w in self.dataset) / len(self.dataset)
        
        return {
            'total_workflows': len(self.dataset),
            'layer1_success_rate': layer1_success / len(self.dataset) * 100,
            'layer2_success_rate': layer2_success / len(self.dataset) * 100,
            'layer3_success_rate': layer3_success / len(self.dataset) * 100,
            'avg_quality_score': avg_quality,
            'avg_processing_time': avg_processing_time
        }


if __name__ == "__main__":
    # Generate 500 workflow dataset
    generator = SyntheticDatasetGenerator()
    dataset = generator.generate_dataset(500)
    output_path = generator.save_dataset()
    
    # Print statistics
    stats = generator.get_statistics()
    print("\n" + "="*60)
    print("📊 DATASET STATISTICS")
    print("="*60)
    print(f"Total Workflows: {stats['total_workflows']}")
    print(f"Layer 1 Success Rate: {stats['layer1_success_rate']:.1f}%")
    print(f"Layer 2 Success Rate: {stats['layer2_success_rate']:.1f}%")
    print(f"Layer 3 Success Rate: {stats['layer3_success_rate']:.1f}%")
    print(f"Avg Quality Score: {stats['avg_quality_score']:.2f}")
    print(f"Avg Processing Time: {stats['avg_processing_time']:.2f}s")
    print("="*60)
    print(f"\n✅ Dataset ready for SCRAPE-010 integration testing!")
    print(f"   Location: {output_path}")





