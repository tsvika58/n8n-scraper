#!/usr/bin/env python3
"""
Smart Filtering CLI

Command-line interface for the smart filtering system.
Provides easy access to Phase 1 metadata scanning and Phase 2 deep scraping.

Usage:
    python scripts/smart_filtering_cli.py phase1 [--limit N] [--test]
    python scripts/smart_filtering_cli.py phase2 [--workflows-file FILE]
    python scripts/smart_filtering_cli.py status
    python scripts/smart_filtering_cli.py test-value-scoring
"""

import asyncio
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.scrapers.value_scorer import WorkflowValueScorer
from src.scrapers.metadata_extractor import MetadataExtractor
from scripts.smart_filtering_phase1 import SmartFilteringPhase1


class SmartFilteringCLI:
    """Command-line interface for smart filtering operations."""
    
    def __init__(self):
        self.value_scorer = WorkflowValueScorer()
        self.metadata_extractor = MetadataExtractor()
        self.phase1_scanner = SmartFilteringPhase1()
    
    async def run_phase1(self, limit: int = None, test_mode: bool = False):
        """Run Phase 1: Metadata scanning and value scoring."""
        print("🚀 SMART FILTERING PHASE 1")
        print("=" * 50)
        
        if test_mode:
            self.phase1_scanner.max_workflows = 10
            print("🧪 TEST MODE: Limited to 10 workflows")
        elif limit:
            self.phase1_scanner.max_workflows = limit
            print(f"📊 LIMITED MODE: Processing {limit} workflows")
        else:
            print("📊 FULL MODE: Processing all workflows")
        
        # Run Phase 1
        report = await self.phase1_scanner.run_phase1()
        
        if 'error' in report:
            print(f"❌ Phase 1 failed: {report['error']}")
            return False
        else:
            print("✅ Phase 1 completed successfully!")
            return True
    
    async def run_phase2(self, workflows_file: str):
        """Run Phase 2: Deep scraping of top workflows."""
        print("🚀 SMART FILTERING PHASE 2")
        print("=" * 50)
        
        try:
            # Load top workflows
            with open(workflows_file, 'r') as f:
                top_workflows = json.load(f)
            
            print(f"📊 Loading {len(top_workflows)} top workflows from {workflows_file}")
            
            # TODO: Implement Phase 2 deep scraping
            print("⚠️  Phase 2 deep scraping not yet implemented")
            print("   This would use the full 7-layer extraction pipeline")
            print("   on the top 100 highest-value workflows")
            
            return True
            
        except FileNotFoundError:
            print(f"❌ Workflows file not found: {workflows_file}")
            return False
        except Exception as e:
            print(f"❌ Phase 2 failed: {e}")
            return False
    
    def show_status(self):
        """Show current system status."""
        print("📊 SMART FILTERING SYSTEM STATUS")
        print("=" * 50)
        
        # Check for existing result files
        result_files = list(Path('.').glob('smart_filtering_*.json'))
        
        if result_files:
            print(f"📁 Found {len(result_files)} result files:")
            for file in sorted(result_files):
                size = file.stat().st_size / 1024  # KB
                mtime = datetime.fromtimestamp(file.stat().st_mtime)
                print(f"   • {file.name} ({size:.1f} KB, {mtime.strftime('%Y-%m-%d %H:%M')})")
        else:
            print("📁 No result files found")
        
        print("\n🔧 Available commands:")
        print("   • python scripts/smart_filtering_cli.py phase1 --test")
        print("   • python scripts/smart_filtering_cli.py phase1 --limit 100")
        print("   • python scripts/smart_filtering_cli.py phase1")
        print("   • python scripts/smart_filtering_cli.py test-value-scoring")
    
    def test_value_scoring(self):
        """Test the value scoring algorithm with sample data."""
        print("🧪 TESTING VALUE SCORING ALGORITHM")
        print("=" * 50)
        
        # Sample workflows with different characteristics
        sample_workflows = [
            {
                'workflow_id': 'high_value',
                'title': 'Advanced CRM Lead Scoring Automation',
                'description': 'Comprehensive workflow that automatically scores leads based on multiple criteria including engagement, demographics, and behavior patterns.',
                'use_case': 'Sales automation for high-value lead prioritization',
                'views': 1500,
                'shares': 45,
                'upvotes': 120,
                'node_count': 12,
                'categories': ['sales', 'automation'],
                'author_name': 'John Doe',
                'workflow_created_at': '2024-01-15T10:30:00Z'
            },
            {
                'workflow_id': 'medium_value',
                'title': 'Simple Email Notification',
                'description': 'Basic workflow for sending email notifications.',
                'use_case': 'Notification system',
                'views': 200,
                'shares': 5,
                'upvotes': 15,
                'node_count': 3,
                'categories': ['notification'],
                'author_name': 'Jane Smith',
                'workflow_created_at': '2024-06-01T14:20:00Z'
            },
            {
                'workflow_id': 'low_value',
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
                'workflow_id': 'complex_workflow',
                'title': 'Enterprise Data Pipeline with 50+ Steps',
                'description': 'Complex enterprise workflow with extensive data processing steps.',
                'use_case': 'Enterprise data processing',
                'views': 800,
                'shares': 20,
                'upvotes': 30,
                'node_count': 45,
                'categories': ['data', 'enterprise'],
                'author_name': 'Data Team',
                'workflow_created_at': '2024-03-10T16:45:00Z'
            }
        ]
        
        # Score each workflow
        print("📊 Scoring sample workflows:")
        print()
        
        for workflow in sample_workflows:
            score_data = self.value_scorer.calculate_score(workflow)
            total_score = score_data['total_score']
            
            print(f"🔍 {workflow['workflow_id']}: {total_score:.1f}/100")
            print(f"   Title: {workflow['title']}")
            print(f"   Engagement: {score_data['engagement_score']:.1f}")
            print(f"   Complexity: {score_data['complexity_score']:.1f}")
            print(f"   Quality: {score_data['quality_score']:.1f}")
            print(f"   Recency: {score_data['recency_score']:.1f}")
            print(f"   Business Value: {score_data['business_value_score']:.1f}")
            print()
        
        # Rank workflows
        ranked = self.value_scorer.rank_workflows(sample_workflows)
        
        print("🏆 RANKED WORKFLOWS (highest to lowest):")
        for i, workflow in enumerate(ranked, 1):
            score = workflow['value_score']['total_score']
            print(f"   {i}. {workflow['workflow_id']}: {score:.1f}/100")
        
        print("\n✅ Value scoring test completed!")
    
    async def run(self, args):
        """Run the CLI with parsed arguments."""
        if args.command == 'phase1':
            return await self.run_phase1(limit=args.limit, test_mode=args.test)
        elif args.command == 'phase2':
            return await self.run_phase2(args.workflows_file)
        elif args.command == 'status':
            self.show_status()
            return True
        elif args.command == 'test-value-scoring':
            self.test_value_scoring()
            return True
        else:
            print(f"❌ Unknown command: {args.command}")
            return False


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Smart Filtering CLI for N8N Workflow Prioritization",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Test Phase 1 with 10 workflows
  python scripts/smart_filtering_cli.py phase1 --test
  
  # Run Phase 1 with limited workflows
  python scripts/smart_filtering_cli.py phase1 --limit 100
  
  # Run Phase 1 on all workflows
  python scripts/smart_filtering_cli.py phase1
  
  # Check system status
  python scripts/smart_filtering_cli.py status
  
  # Test value scoring algorithm
  python scripts/smart_filtering_cli.py test-value-scoring
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Phase 1 command
    phase1_parser = subparsers.add_parser('phase1', help='Run Phase 1: Metadata scanning')
    phase1_parser.add_argument('--limit', type=int, help='Limit number of workflows to process')
    phase1_parser.add_argument('--test', action='store_true', help='Test mode (limit to 10 workflows)')
    
    # Phase 2 command
    phase2_parser = subparsers.add_parser('phase2', help='Run Phase 2: Deep scraping')
    phase2_parser.add_argument('--workflows-file', required=True, help='JSON file with top workflows')
    
    # Status command
    subparsers.add_parser('status', help='Show system status')
    
    # Test command
    subparsers.add_parser('test-value-scoring', help='Test value scoring algorithm')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Run CLI
    cli = SmartFilteringCLI()
    try:
        success = asyncio.run(cli.run(args))
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⏹️  Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()






