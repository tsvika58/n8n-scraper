"""
Test Layer 3 Extractor with 20 Real n8n.io Workflows

Expanded testing to prove 90%+ success rate as required.

Author: Developer-2 (Dev2)
Task: SCRAPE-005 Rework - Expand to 15-20 workflows
Date: October 9, 2025
"""

import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.scrapers.layer3_explainer import ExplainerContentExtractor
from loguru import logger

logger.remove()
logger.add(sys.stdout, format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | {message}")


# 20 real n8n.io workflow IDs (diverse sample)
TEST_WORKFLOWS = [
    # Original 8
    {"id": "2462", "url": "https://n8n.io/workflows/2462", "name": "Angie AI Assistant", "category": "AI"},
    {"id": "1954", "url": "https://n8n.io/workflows/1954", "name": "AI Agent Chat", "category": "AI"},
    {"id": "2103", "url": "https://n8n.io/workflows/2103", "name": "Slack Bot", "category": "Communication"},
    {"id": "1870", "url": "https://n8n.io/workflows/1870", "name": "GitHub Issues", "category": "Development"},
    {"id": "2234", "url": "https://n8n.io/workflows/2234", "name": "Email Campaign", "category": "Marketing"},
    {"id": "1756", "url": "https://n8n.io/workflows/1756", "name": "Data Pipeline", "category": "Data"},
    {"id": "2019", "url": "https://n8n.io/workflows/2019", "name": "CRM Integration", "category": "CRM"},
    {"id": "1832", "url": "https://n8n.io/workflows/1832", "name": "Customer Feedback", "category": "Support"},
    
    # Additional 12 for expanded testing
    {"id": "2156", "url": "https://n8n.io/workflows/2156", "name": "Social Media Automation", "category": "Marketing"},
    {"id": "1923", "url": "https://n8n.io/workflows/1923", "name": "Invoice Processing", "category": "Finance"},
    {"id": "2087", "url": "https://n8n.io/workflows/2087", "name": "Lead Scoring", "category": "Sales"},
    {"id": "1845", "url": "https://n8n.io/workflows/1845", "name": "Content Moderation", "category": "AI"},
    {"id": "2201", "url": "https://n8n.io/workflows/2201", "name": "Webhook Router", "category": "Integration"},
    {"id": "1778", "url": "https://n8n.io/workflows/1778", "name": "Data Sync", "category": "Data"},
    {"id": "2145", "url": "https://n8n.io/workflows/2145", "name": "Notification System", "category": "Communication"},
    {"id": "1896", "url": "https://n8n.io/workflows/1896", "name": "Form Processor", "category": "Automation"},
    {"id": "2078", "url": "https://n8n.io/workflows/2078", "name": "Email Parser", "category": "Email"},
    {"id": "1967", "url": "https://n8n.io/workflows/1967", "name": "Calendar Integration", "category": "Productivity"},
    {"id": "2189", "url": "https://n8n.io/workflows/2189", "name": "Database Backup", "category": "Data"},
    {"id": "1812", "url": "https://n8n.io/workflows/1812", "name": "API Gateway", "category": "Development"},
]


async def test_workflow(extractor, workflow_info, index, total):
    """Test single workflow extraction"""
    
    workflow_id = workflow_info["id"]
    url = workflow_info["url"]
    name = workflow_info["name"]
    
    logger.info(f"[{index}/{total}] Testing: {name} (ID: {workflow_id})")
    
    try:
        result = await extractor.extract(workflow_id, url)
        
        success = result['success']
        time = result['extraction_time']
        errors = len(result.get('errors', []))
        
        data = result['data']
        text_len = len(data.get('tutorial_text', ''))
        images = len(data.get('image_urls', []))
        videos = len(data.get('video_urls', []))
        code = len(data.get('code_snippets', []))
        
        status_icon = "✅" if success else "❌"
        logger.info(f"    {status_icon} {time:.2f}s | Text: {text_len} | Img: {images} | Vid: {videos} | Code: {code}")
        
        if errors > 0:
            for error in result['errors']:
                logger.error(f"      Error: {error}")
        
        # Save extraction
        output_dir = Path(__file__).parent.parent / ".coordination" / "testing" / "results" / "SCRAPE-005-20-workflow-samples"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_file = output_dir / f"workflow_{workflow_id}_extraction.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        return {
            "workflow": workflow_info,
            "success": success,
            "time": time,
            "text_length": text_len,
            "images": images,
            "videos": videos,
            "code": code,
            "errors": errors
        }
        
    except Exception as e:
        logger.error(f"    ❌ EXCEPTION: {str(e)}")
        return {
            "workflow": workflow_info,
            "success": False,
            "error": str(e)
        }


async def main():
    """Test 20 n8n.io workflows"""
    
    logger.info("="*80)
    logger.info("SCRAPE-005 REWORK: 20-WORKFLOW VALIDATION TEST")
    logger.info("="*80)
    logger.info(f"Testing {len(TEST_WORKFLOWS)} real n8n.io workflows")
    logger.info(f"Target success rate: ≥90% (18+ successful)")
    logger.info("")
    
    start_time = datetime.now()
    results = []
    
    async with ExplainerContentExtractor(headless=True, timeout=30000) as extractor:
        
        for i, workflow in enumerate(TEST_WORKFLOWS, 1):
            result = await test_workflow(extractor, workflow, i, len(TEST_WORKFLOWS))
            results.append(result)
            
            # Pause between requests
            await asyncio.sleep(1.5)
    
    end_time = datetime.now()
    total_time = (end_time - start_time).total_seconds()
    
    # Generate comprehensive summary
    logger.info("\n" + "="*80)
    logger.info("COMPREHENSIVE TEST SUMMARY")
    logger.info("="*80)
    
    successful = sum(1 for r in results if r.get('success', False))
    failed = len(results) - successful
    success_rate = (successful/len(results))*100
    
    logger.info(f"Total workflows tested: {len(results)}")
    logger.info(f"Successful extractions: {successful}")
    logger.info(f"Failed extractions: {failed}")
    logger.info(f"Success rate: {success_rate:.1f}%")
    logger.info(f"")
    
    # Check if we met the 90% requirement
    if success_rate >= 90:
        logger.success(f"✅ SUCCESS RATE REQUIREMENT MET: {success_rate:.1f}% >= 90%")
    else:
        logger.error(f"❌ SUCCESS RATE REQUIREMENT NOT MET: {success_rate:.1f}% < 90%")
    
    if successful > 0:
        valid_results = [r for r in results if r.get('success', False)]
        avg_time = sum(r['time'] for r in valid_results) / len(valid_results)
        avg_text = sum(r.get('text_length', 0) for r in valid_results) / len(valid_results)
        total_text = sum(r.get('text_length', 0) for r in valid_results)
        total_images = sum(r.get('images', 0) for r in valid_results)
        total_videos = sum(r.get('videos', 0) for r in valid_results)
        total_code = sum(r.get('code', 0) for r in valid_results)
        
        logger.info(f"\nPerformance Metrics:")
        logger.info(f"  Average extraction time: {avg_time:.2f}s")
        logger.info(f"  Average text per workflow: {avg_text:.0f} characters")
        logger.info(f"  Total text extracted: {total_text:,} characters")
        logger.info(f"  Total images collected: {total_images}")
        logger.info(f"  Total videos collected: {total_videos}")
        logger.info(f"  Total code snippets: {total_code}")
    
    logger.info(f"\nTotal test duration: {total_time:.1f}s ({total_time/60:.1f} minutes)")
    logger.info("="*80)
    
    # Save comprehensive summary
    summary_file = Path(__file__).parent.parent / ".coordination" / "testing" / "results" / "SCRAPE-005-20-workflow-summary.json"
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump({
            "test_date": start_time.isoformat(),
            "total_workflows": len(results),
            "successful": successful,
            "failed": failed,
            "success_rate": success_rate,
            "requirement_met": success_rate >= 90,
            "average_time": avg_time if successful > 0 else 0,
            "average_text_length": avg_text if successful > 0 else 0,
            "total_text": total_text if successful > 0 else 0,
            "total_images": total_images if successful > 0 else 0,
            "total_videos": total_videos if successful > 0 else 0,
            "total_code": total_code if successful > 0 else 0,
            "total_duration": total_time,
            "results": results
        }, f, indent=2)
    
    logger.success(f"\n✅ Summary saved to: {summary_file}")
    
    # Final verdict
    if success_rate >= 90:
        logger.success(f"\n🎉 REWORK SUCCESSFUL: {success_rate:.1f}% >= 90% requirement!")
    else:
        logger.error(f"\n❌ REWORK INSUFFICIENT: {success_rate:.1f}% < 90% requirement")
    
    return results


if __name__ == "__main__":
    asyncio.run(main())





