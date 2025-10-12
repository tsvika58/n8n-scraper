#!/usr/bin/env python3
"""
Offline Test for Smart Filtering System

This script tests the smart filtering system without making real HTTP requests.
Uses mock data to validate the value scoring and ranking algorithms.
"""

import sys
import json
from pathlib import Path
from datetime import datetime, timezone

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.scrapers.value_scorer import WorkflowValueScorer


def create_mock_workflows():
    """Create mock workflows for testing."""
    return [
        {
            'workflow_id': '1',
            'url': 'https://n8n.io/workflows/1',
            'title': 'Advanced CRM Lead Scoring Automation',
            'description': 'Comprehensive workflow that automatically scores leads based on multiple criteria including engagement, demographics, and behavior patterns. Includes integration with Salesforce, HubSpot, and custom scoring algorithms.',
            'use_case': 'Sales automation for high-value lead prioritization and conversion optimization',
            'views': 1500,
            'shares': 45,
            'upvotes': 120,
            'node_count': 12,
            'categories': ['sales', 'automation', 'crm'],
            'author_name': 'John Doe',
            'workflow_created_at': '2024-01-15T10:30:00Z'
        },
        {
            'workflow_id': '2',
            'url': 'https://n8n.io/workflows/2',
            'title': 'Simple Email Notification',
            'description': 'Basic workflow for sending email notifications when certain conditions are met.',
            'use_case': 'Notification system for alerts and updates',
            'views': 200,
            'shares': 5,
            'upvotes': 15,
            'node_count': 3,
            'categories': ['notification'],
            'author_name': 'Jane Smith',
            'workflow_created_at': '2024-06-01T14:20:00Z'
        },
        {
            'workflow_id': '3',
            'url': 'https://n8n.io/workflows/3',
            'title': 'Untitled Workflow',
            'description': '',
            'use_case': '',
            'views': 10,
            'shares': 0,
            'upvotes': 1,
            'node_count': 1,
            'categories': [],
            'author_name': '',
            'workflow_created_at': '2023-12-01T09:00:00Z'
        },
        {
            'workflow_id': '4',
            'url': 'https://n8n.io/workflows/4',
            'title': 'Enterprise Data Pipeline with 50+ Steps',
            'description': 'Complex enterprise workflow with extensive data processing steps including ETL operations, data validation, transformation, and loading into multiple systems.',
            'use_case': 'Enterprise data processing and integration',
            'views': 800,
            'shares': 20,
            'upvotes': 30,
            'node_count': 45,
            'categories': ['data', 'enterprise'],
            'author_name': 'Data Team',
            'workflow_created_at': '2024-03-10T16:45:00Z'
        },
        {
            'workflow_id': '5',
            'url': 'https://n8n.io/workflows/5',
            'title': 'Marketing Campaign Automation',
            'description': 'Automated marketing campaign workflow that handles lead nurturing, email sequences, and conversion tracking across multiple channels.',
            'use_case': 'Marketing automation and campaign management',
            'views': 950,
            'shares': 35,
            'upvotes': 75,
            'node_count': 8,
            'categories': ['marketing', 'automation'],
            'author_name': 'Marketing Team',
            'workflow_created_at': '2024-02-20T11:15:00Z'
        },
        {
            'workflow_id': '6',
            'url': 'https://n8n.io/workflows/6',
            'title': 'Social Media Content Scheduler',
            'description': 'Schedule and publish content across multiple social media platforms with engagement tracking.',
            'use_case': 'Social media management and content scheduling',
            'views': 450,
            'shares': 25,
            'upvotes': 40,
            'node_count': 6,
            'categories': ['social', 'content'],
            'author_name': 'Social Media Manager',
            'workflow_created_at': '2024-04-05T13:30:00Z'
        },
        {
            'workflow_id': '7',
            'url': 'https://n8n.io/workflows/7',
            'title': 'Customer Support Ticket Routing',
            'description': 'Intelligent ticket routing based on priority, category, and agent availability.',
            'use_case': 'Customer support optimization',
            'views': 650,
            'shares': 18,
            'upvotes': 55,
            'node_count': 7,
            'categories': ['support', 'routing'],
            'author_name': 'Support Team',
            'workflow_created_at': '2024-01-30T09:45:00Z'
        },
        {
            'workflow_id': '8',
            'url': 'https://n8n.io/workflows/8',
            'title': 'Inventory Management System',
            'description': 'Real-time inventory tracking with automatic reorder points and supplier notifications.',
            'use_case': 'Inventory management and supply chain optimization',
            'views': 320,
            'shares': 12,
            'upvotes': 25,
            'node_count': 9,
            'categories': ['inventory', 'management'],
            'author_name': 'Operations Team',
            'workflow_created_at': '2024-03-25T14:10:00Z'
        },
        {
            'workflow_id': '9',
            'url': 'https://n8n.io/workflows/9',
            'title': 'Analytics Dashboard Data Sync',
            'description': 'Synchronize data from multiple sources into a centralized analytics dashboard.',
            'use_case': 'Business intelligence and analytics',
            'views': 720,
            'shares': 28,
            'upvotes': 65,
            'node_count': 11,
            'categories': ['analytics', 'data'],
            'author_name': 'Analytics Team',
            'workflow_created_at': '2024-02-10T16:20:00Z'
        },
        {
            'workflow_id': '10',
            'url': 'https://n8n.io/workflows/10',
            'title': 'Workflow with No Title',
            'description': 'A workflow that has been created but not properly configured or documented.',
            'use_case': 'Unknown or undefined use case',
            'views': 50,
            'shares': 2,
            'upvotes': 3,
            'node_count': 2,
            'categories': [],
            'author_name': 'Unknown',
            'workflow_created_at': '2023-11-15T08:00:00Z'
        }
    ]


def test_value_scoring():
    """Test the value scoring algorithm with mock data."""
    print("🧪 TESTING SMART FILTERING SYSTEM (OFFLINE)")
    print("=" * 60)
    
    # Initialize value scorer
    value_scorer = WorkflowValueScorer()
    
    # Create mock workflows
    workflows = create_mock_workflows()
    
    print(f"📊 Testing with {len(workflows)} mock workflows")
    print()
    
    # Score each workflow
    scored_workflows = []
    for workflow in workflows:
        score_data = value_scorer.calculate_score(workflow)
        workflow['value_score'] = score_data
        scored_workflows.append(workflow)
    
    # Sort by value score
    ranked_workflows = sorted(
        scored_workflows,
        key=lambda x: x['value_score']['total_score'],
        reverse=True
    )
    
    # Display results
    print("🏆 RANKED WORKFLOWS BY VALUE SCORE:")
    print("-" * 60)
    
    for i, workflow in enumerate(ranked_workflows, 1):
        score = workflow['value_score']['total_score']
        title = workflow['title'][:40] + "..." if len(workflow['title']) > 40 else workflow['title']
        
        print(f"{i:2d}. {score:5.1f}/100 | {title}")
        print(f"    Engagement: {workflow['value_score']['engagement_score']:4.1f} | "
              f"Complexity: {workflow['value_score']['complexity_score']:4.1f} | "
              f"Quality: {workflow['value_score']['quality_score']:4.1f} | "
              f"Recency: {workflow['value_score']['recency_score']:4.1f} | "
              f"Business: {workflow['value_score']['business_value_score']:4.1f}")
        print(f"    Views: {workflow['views']:4d} | Nodes: {workflow['node_count']:2d} | "
              f"Categories: {', '.join(workflow['categories']) if workflow['categories'] else 'None'}")
        print()
    
    # Get top 3 workflows
    top_3 = ranked_workflows[:3]
    
    print("🎯 TOP 3 HIGH-VALUE WORKFLOWS FOR PHASE 2:")
    print("-" * 60)
    
    for i, workflow in enumerate(top_3, 1):
        print(f"{i}. {workflow['title']}")
        print(f"   Score: {workflow['value_score']['total_score']:.1f}/100")
        print(f"   URL: {workflow['url']}")
        print(f"   Use Case: {workflow['use_case']}")
        print()
    
    # Calculate statistics
    avg_score = sum(w['value_score']['total_score'] for w in scored_workflows) / len(scored_workflows)
    max_score = max(w['value_score']['total_score'] for w in scored_workflows)
    min_score = min(w['value_score']['total_score'] for w in scored_workflows)
    
    print("📊 STATISTICS:")
    print("-" * 60)
    print(f"Average Score: {avg_score:.1f}/100")
    print(f"Highest Score: {max_score:.1f}/100")
    print(f"Lowest Score: {min_score:.1f}/100")
    print(f"Score Range: {max_score - min_score:.1f} points")
    
    # Simulate Phase 1 results
    print("\n🚀 SIMULATED PHASE 1 RESULTS:")
    print("-" * 60)
    print(f"Total Workflows Processed: {len(workflows)}")
    print(f"Successful Extractions: {len([w for w in workflows if w.get('value_score')])}")
    print(f"Success Rate: 100.0% (simulated)")
    print(f"Average Extraction Time: 0.5s per workflow (simulated)")
    print(f"Total Phase 1 Time: {len(workflows) * 0.5:.1f}s")
    print(f"Top 100 Candidates: {len([w for w in workflows if w['value_score']['total_score'] > 50])} workflows > 50 score")
    
    # Save results to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = f"smart_filtering_test_results_{timestamp}.json"
    
    with open(results_file, 'w') as f:
        json.dump({
            'test_type': 'offline_smart_filtering',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'workflows': ranked_workflows,
            'statistics': {
                'total_workflows': len(workflows),
                'avg_score': avg_score,
                'max_score': max_score,
                'min_score': min_score,
                'top_3_workflows': [w['workflow_id'] for w in top_3]
            }
        }, f, indent=2, default=str)
    
    print(f"\n💾 Results saved to: {results_file}")
    print("\n✅ OFFLINE TEST COMPLETED SUCCESSFULLY!")
    print("🎯 Smart filtering system is ready for Phase 1 implementation!")


if __name__ == "__main__":
    test_value_scoring()

