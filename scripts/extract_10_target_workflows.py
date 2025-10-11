"""
Extract 10 Target Sales/Lead Generation Workflows for SCRAPE-002 v2.1

This script extracts metadata from 10 pre-selected sales/lead generation workflows
for task SCRAPE-002 v2.1 validation.

Author: Developer-1 (Dev1)
Date: October 10, 2025
"""

import asyncio
import json
import time
import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.scrapers.layer1_metadata import PageMetadataExtractor
from loguru import logger

# The 10 target sales/lead generation workflows (validated by Dev2 in SCRAPE-005)
TARGET_WORKFLOWS = [
    ("2462", "https://n8n.io/workflows/2462"),
    ("1954", "https://n8n.io/workflows/1954"),
    ("2103", "https://n8n.io/workflows/2103"),
    ("2234", "https://n8n.io/workflows/2234"),
    ("1756", "https://n8n.io/workflows/1756"),
    ("1832", "https://n8n.io/workflows/1832"),
    ("2156", "https://n8n.io/workflows/2156"),
    ("1923", "https://n8n.io/workflows/1923"),
    ("2087", "https://n8n.io/workflows/2087"),
    ("2145", "https://n8n.io/workflows/2145"),
]


async def main():
    """Extract all 10 target workflows."""
    logger.info("🚀 Starting extraction of 10 target sales/lead gen workflows")
    logger.info(f"Target workflows: {[wf[0] for wf in TARGET_WORKFLOWS]}")
    
    extractor = PageMetadataExtractor()
    results = []
    extraction_times = []
    
    start_total = time.time()
    
    for idx, (workflow_id, url) in enumerate(TARGET_WORKFLOWS, 1):
        logger.info(f"📊 [{idx}/10] Extracting workflow {workflow_id}...")
        
        try:
            # Extract workflow
            result = await extractor.extract(workflow_id, url)
            
            if result['success']:
                logger.success(f"✅ [{idx}/10] Successfully extracted workflow {workflow_id} in {result['extraction_time']:.2f}s")
                extraction_times.append(result['extraction_time'])
            else:
                logger.error(f"❌ [{idx}/10] Failed to extract workflow {workflow_id}: {result.get('error', 'Unknown error')}")
            
            results.append({
                'workflow_id': workflow_id,
                'url': url,
                'result': result
            })
            
            # Rate limiting: 2 seconds between requests (except after last one)
            if idx < len(TARGET_WORKFLOWS):
                logger.info("⏱️  Waiting 2 seconds (rate limiting)...")
                await asyncio.sleep(2)
                
        except Exception as e:
            logger.error(f"❌ [{idx}/10] Exception extracting workflow {workflow_id}: {e}")
            results.append({
                'workflow_id': workflow_id,
                'url': url,
                'result': {
                    'success': False,
                    'workflow_id': workflow_id,
                    'data': {},
                    'extraction_time': 0,
                    'error': str(e)
                }
            })
    
    total_time = time.time() - start_total
    
    # Calculate metrics
    successful = sum(1 for r in results if r['result']['success'])
    failed = len(results) - successful
    success_rate = (successful / len(results)) * 100
    
    avg_time = sum(extraction_times) / len(extraction_times) if extraction_times else 0
    min_time = min(extraction_times) if extraction_times else 0
    max_time = max(extraction_times) if extraction_times else 0
    
    # Summary
    logger.info("\n" + "="*60)
    logger.info("📊 EXTRACTION SUMMARY")
    logger.info("="*60)
    logger.info(f"Total workflows attempted: {len(results)}")
    logger.info(f"✅ Successful extractions: {successful}")
    logger.info(f"❌ Failed extractions: {failed}")
    logger.info(f"📈 Success rate: {success_rate:.1f}%")
    logger.info(f"⏱️  Average extraction time: {avg_time:.2f}s")
    logger.info(f"⏱️  Min extraction time: {min_time:.2f}s")
    logger.info(f"⏱️  Max extraction time: {max_time:.2f}s")
    logger.info(f"⏱️  Total time: {total_time:.2f}s")
    logger.info("="*60 + "\n")
    
    # Save all extractions to individual JSON files
    sample_dir = project_root / ".coordination" / "testing" / "results" / "SCRAPE-002-sample-extractions"
    sample_dir.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"💾 Saving {len(results)} workflow extractions to {sample_dir}")
    
    for result_data in results:
        workflow_id = result_data['workflow_id']
        result = result_data['result']
        
        # Create individual workflow JSON
        workflow_file = sample_dir / f"workflow_{workflow_id}.json"
        
        # Prepare JSON data (extract data dict + metadata)
        json_data = {
            'workflow_id': workflow_id,
            'url': result_data['url'],
            'extraction_status': 'complete' if result['success'] else 'failed',
            'extraction_time': f"{result['extraction_time']:.2f}s",
            'error': result.get('error'),
            **result['data']  # Spread all data fields
        }
        
        with open(workflow_file, 'w') as f:
            json.dump(json_data, f, indent=2, default=str)
        
        logger.info(f"  📄 Saved: workflow_{workflow_id}.json")
    
    # Create summary JSON
    summary_file = project_root / ".coordination" / "testing" / "results" / "SCRAPE-002-10-workflow-summary.json"
    summary_data = {
        "task_id": "SCRAPE-002",
        "total_workflows_attempted": len(results),
        "successful_extractions": successful,
        "failed_extractions": failed,
        "partial_extractions": 0,
        "success_rate": round(success_rate, 1),
        "average_extraction_time": f"{avg_time:.2f}s",
        "min_time": f"{min_time:.2f}s",
        "max_time": f"{max_time:.2f}s",
        "total_time": f"{total_time:.2f}s",
        "extraction_date": time.strftime("%Y-%m-%d"),
        "workflow_focus": "sales_lead_generation",
        "target_workflows": [wf[0] for wf in TARGET_WORKFLOWS]
    }
    
    with open(summary_file, 'w') as f:
        json.dump(summary_data, f, indent=2)
    
    logger.success(f"✅ Summary saved to: {summary_file}")
    
    logger.info("\n🎉 Extraction complete!")
    logger.info(f"📁 All files saved to: {sample_dir.parent}")
    
    return results


if __name__ == "__main__":
    asyncio.run(main())





