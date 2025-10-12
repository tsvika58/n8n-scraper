#!/usr/bin/env python3
"""
Smart Filtering Phase 1: Metadata Scanner

This script implements Phase 1 of the smart filtering strategy:
- Scans all 6,022 workflows for metadata only (Layers 1-2)
- Calculates value scores for each workflow
- Identifies top 100 high-value candidates for Phase 2 deep scraping
- Estimated time: 1 hour (vs 19.5 hours for blind scraping)

Usage:
    python scripts/smart_filtering_phase1.py
"""

import asyncio
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any
import logging

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.storage.database import get_session
from src.storage.repository import WorkflowRepository
from src.scrapers.metadata_extractor import MetadataExtractor
from src.storage.models import Workflow


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('smart_filtering_phase1.log')
    ]
)
logger = logging.getLogger(__name__)


class SmartFilteringPhase1:
    """
    Phase 1 Smart Filtering: Metadata Scanner
    
    Processes all workflows in the database to extract metadata and
    calculate value scores for intelligent prioritization.
    """
    
    def __init__(self):
        self.metadata_extractor = MetadataExtractor()
        self.batch_size = 3  # Concurrent workflows per batch (reduced for stability)
        self.max_workflows = None  # Set to limit for testing
        
    async def run_phase1(self) -> Dict[str, Any]:
        """
        Execute Phase 1 smart filtering.
        
        Returns:
            Dictionary with results and top 100 workflows
        """
        logger.info("🚀 STARTING SMART FILTERING PHASE 1")
        logger.info("=" * 60)
        
        start_time = datetime.now()
        
        try:
            # Step 1: Get all workflows from database
            workflows = await self._get_workflows_to_process()
            logger.info(f"📊 Found {len(workflows)} workflows to process")
            
            if not workflows:
                logger.error("❌ No workflows found in database")
                return {'error': 'No workflows found'}
            
            # Step 2: Process workflows in batches
            results = await self._process_workflows(workflows)
            
            # Step 3: Rank and identify top 100
            top_workflows = self._identify_top_workflows(results)
            
            # Step 4: Generate reports
            report = self._generate_report(results, top_workflows, start_time)
            
            # Step 5: Save results
            await self._save_results(results, top_workflows, report)
            
            logger.info("✅ PHASE 1 COMPLETE!")
            logger.info(f"📊 Processed: {len(results)} workflows")
            logger.info(f"🎯 Top 100 identified: {len(top_workflows)} workflows")
            
            return report
            
        except Exception as e:
            logger.error(f"❌ Phase 1 failed: {e}")
            return {'error': str(e)}
    
    async def _get_workflows_to_process(self) -> List[Dict[str, Any]]:
        """Get workflows that need metadata extraction."""
        try:
            with get_session() as session:
                repository = WorkflowRepository(session)
                
                # Get workflows that haven't been processed or need re-scoring
                workflows = session.query(Workflow).filter(
                    Workflow.url.isnot(None),
                    Workflow.url != ''
                ).all()
                
                # Convert to list of dictionaries
                workflow_list = []
                for workflow in workflows:
                    workflow_list.append({
                        'workflow_id': workflow.workflow_id,
                        'url': workflow.url,
                        'existing_quality_score': workflow.quality_score
                    })
                
                # Limit for testing if specified
                if self.max_workflows:
                    workflow_list = workflow_list[:self.max_workflows]
                
                return workflow_list
                
        except Exception as e:
            logger.error(f"Error getting workflows: {e}")
            return []
    
    async def _process_workflows(self, workflows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process workflows in batches for metadata extraction."""
        logger.info(f"🔄 Processing {len(workflows)} workflows in batches of {self.batch_size}")
        
        results = []
        total_batches = (len(workflows) + self.batch_size - 1) // self.batch_size
        
        for batch_num in range(total_batches):
            start_idx = batch_num * self.batch_size
            end_idx = min(start_idx + self.batch_size, len(workflows))
            batch = workflows[start_idx:end_idx]
            
            logger.info(f"📦 Batch {batch_num + 1}/{total_batches}: Processing workflows {start_idx + 1}-{end_idx}")
            
            # Extract metadata for batch
            batch_results = await self.metadata_extractor.batch_extract_metadata(batch, self.batch_size)
            results.extend(batch_results)
            
            # Progress update
            processed = len(results)
            successful = sum(1 for r in results if r.get('success'))
            logger.info(f"📊 Progress: {processed}/{len(workflows)} processed, {successful} successful")
            
            # Small delay between batches
            await asyncio.sleep(0.2)
        
        return results
    
    def _identify_top_workflows(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify top 100 highest-value workflows."""
        logger.info("🎯 Identifying top 100 highest-value workflows")
        
        # Filter successful extractions with value scores
        successful_results = [
            r for r in results 
            if r.get('success') and r.get('value_score') and r['value_score'].get('total_score', 0) > 0
        ]
        
        # Sort by value score (highest first)
        ranked_results = sorted(
            successful_results,
            key=lambda x: x['value_score']['total_score'],
            reverse=True
        )
        
        # Get top 100
        top_100 = ranked_results[:100]
        
        logger.info(f"📊 Top 100 workflows identified:")
        logger.info(f"   • Score range: {top_100[-1]['value_score']['total_score']:.1f} - {top_100[0]['value_score']['total_score']:.1f}")
        logger.info(f"   • Average score: {sum(w['value_score']['total_score'] for w in top_100) / len(top_100):.1f}")
        
        return top_100
    
    def _generate_report(self, results: List[Dict[str, Any]], top_workflows: List[Dict[str, Any]], start_time: datetime) -> Dict[str, Any]:
        """Generate comprehensive report of Phase 1 results."""
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        successful = [r for r in results if r.get('success')]
        failed = [r for r in results if not r.get('success')]
        
        # Calculate statistics
        if successful:
            avg_score = sum(r['value_score']['total_score'] for r in successful if r.get('value_score')) / len(successful)
            avg_extraction_time = sum(r.get('extraction_time', 0) for r in successful) / len(successful)
        else:
            avg_score = 0
            avg_extraction_time = 0
        
        report = {
            'phase': 'Phase 1: Metadata Scanner',
            'timestamp': end_time.isoformat(),
            'duration_seconds': duration,
            'duration_formatted': f"{duration//3600:.0f}h {(duration%3600)//60:.0f}m {duration%60:.0f}s",
            
            'processing_stats': {
                'total_workflows': len(results),
                'successful': len(successful),
                'failed': len(failed),
                'success_rate': len(successful) / len(results) * 100 if results else 0,
                'avg_extraction_time': avg_extraction_time
            },
            
            'value_scoring': {
                'avg_value_score': avg_score,
                'top_score': max((r['value_score']['total_score'] for r in successful if r.get('value_score')), default=0),
                'min_score': min((r['value_score']['total_score'] for r in successful if r.get('value_score')), default=0)
            },
            
            'top_100_candidates': {
                'count': len(top_workflows),
                'score_range': {
                    'highest': top_workflows[0]['value_score']['total_score'] if top_workflows else 0,
                    'lowest': top_workflows[-1]['value_score']['total_score'] if top_workflows else 0
                },
                'avg_score': sum(w['value_score']['total_score'] for w in top_workflows) / len(top_workflows) if top_workflows else 0
            },
            
            'recommendations': {
                'phase2_ready': len(top_workflows) >= 100,
                'estimated_phase2_time': f"{len(top_workflows) * 14 / 3600:.1f} hours",
                'total_time_savings': f"{(19.5 * 3600 - duration) / 3600:.1f} hours saved"
            }
        }
        
        return report
    
    async def _save_results(self, results: List[Dict[str, Any]], top_workflows: List[Dict[str, Any]], report: Dict[str, Any]):
        """Save results to files."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save full results
        results_file = f"smart_filtering_phase1_results_{timestamp}.json"
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        logger.info(f"💾 Full results saved to: {results_file}")
        
        # Save top 100 workflows
        top100_file = f"smart_filtering_top100_{timestamp}.json"
        with open(top100_file, 'w') as f:
            json.dump(top_workflows, f, indent=2, default=str)
        logger.info(f"💾 Top 100 workflows saved to: {top100_file}")
        
        # Save report
        report_file = f"smart_filtering_phase1_report_{timestamp}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        logger.info(f"💾 Report saved to: {report_file}")
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 PHASE 1 SUMMARY")
        print("=" * 60)
        print(f"⏱️  Duration: {report['duration_formatted']}")
        print(f"📈 Processed: {report['processing_stats']['total_workflows']} workflows")
        print(f"✅ Success Rate: {report['processing_stats']['success_rate']:.1f}%")
        print(f"🎯 Avg Value Score: {report['value_scoring']['avg_value_score']:.1f}")
        print(f"🏆 Top 100 Ready: {report['top_100_candidates']['count']} workflows")
        print(f"⏭️  Phase 2 Est: {report['recommendations']['estimated_phase2_time']} hours")
        print(f"💾 Files saved: {results_file}, {top100_file}, {report_file}")
        print("=" * 60)


async def main():
    """Main entry point for Phase 1 smart filtering."""
    try:
        # Initialize Phase 1 scanner
        phase1 = SmartFilteringPhase1()
        
        # For testing, limit to first 50 workflows
        phase1.max_workflows = 50
        logger.info("🧪 TESTING MODE: Limited to 50 workflows")
        
        # Run Phase 1
        report = await phase1.run_phase1()
        
        if 'error' in report:
            logger.error(f"❌ Phase 1 failed: {report['error']}")
            sys.exit(1)
        else:
            logger.info("🎉 Phase 1 completed successfully!")
            
    except KeyboardInterrupt:
        logger.info("⏹️  Phase 1 interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
