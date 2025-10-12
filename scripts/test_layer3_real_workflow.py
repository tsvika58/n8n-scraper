"""
Test Script: Layer 3 Extraction with Real n8n.io Workflow

This script tests the Layer 3 extractor with a real n8n.io workflow
to provide concrete evidence of extraction capabilities.

Author: Developer-2 (Dev2)
Task: SCRAPE-005 Validation
Date: October 9, 2025
"""

import asyncio
import json
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.scrapers.layer3_explainer import ExplainerContentExtractor
from loguru import logger

# Configure logger for this test
logger.remove()
logger.add(sys.stdout, format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | {message}")
logger.add(
    "logs/layer3_real_workflow_test.log",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}",
    rotation="10 MB"
)


async def test_single_workflow(workflow_id: str, url: str):
    """Test extraction on a single real workflow"""
    
    logger.info(f"Starting test extraction for workflow {workflow_id}")
    logger.info(f"URL: {url}")
    
    try:
        async with ExplainerContentExtractor(headless=True) as extractor:
            result = await extractor.extract(workflow_id, url)
            
            # Log results
            logger.info(f"Extraction completed in {result['extraction_time']:.2f}s")
            logger.info(f"Success: {result['success']}")
            logger.info(f"Errors: {len(result.get('errors', []))}")
            
            if result['errors']:
                for error in result['errors']:
                    logger.error(f"  - {error}")
            
            # Log data quality
            data = result['data']
            logger.info("\n" + "="*60)
            logger.info("EXTRACTION RESULTS:")
            logger.info("="*60)
            logger.info(f"Introduction length: {len(data.get('introduction', ''))} chars")
            logger.info(f"Overview length: {len(data.get('overview', ''))} chars")
            logger.info(f"Tutorial text length: {len(data.get('tutorial_text', ''))} chars")
            logger.info(f"Tutorial sections: {len(data.get('tutorial_sections', []))}")
            logger.info(f"Step-by-step items: {len(data.get('step_by_step', []))}")
            logger.info(f"Best practices: {len(data.get('best_practices', []))}")
            logger.info(f"Common pitfalls: {len(data.get('common_pitfalls', []))}")
            logger.info(f"Image URLs: {len(data.get('image_urls', []))}")
            logger.info(f"Video URLs: {len(data.get('video_urls', []))}")
            logger.info(f"Code snippets: {len(data.get('code_snippets', []))}")
            logger.info("="*60)
            
            # Show sample content
            if data.get('introduction'):
                logger.info(f"\nIntroduction (first 200 chars):\n{data['introduction'][:200]}...")
            
            if data.get('tutorial_text'):
                logger.info(f"\nTutorial text (first 300 chars):\n{data['tutorial_text'][:300]}...")
            
            if data.get('image_urls'):
                logger.info(f"\nFirst 3 image URLs:")
                for url in data['image_urls'][:3]:
                    logger.info(f"  - {url}")
            
            if data.get('video_urls'):
                logger.info(f"\nVideo URLs:")
                for url in data['video_urls']:
                    logger.info(f"  - {url}")
            
            # Save complete result to file
            output_dir = Path(__file__).parent.parent / ".coordination" / "testing" / "results" / "SCRAPE-005-explainer-samples"
            output_dir.mkdir(parents=True, exist_ok=True)
            
            output_file = output_dir / f"workflow_{workflow_id}_extraction.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            logger.success(f"Full extraction saved to: {output_file}")
            
            return result
            
    except Exception as e:
        logger.error(f"Test failed with exception: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return None


async def main():
    """Run test with real n8n.io workflows"""
    
    logger.info("="*60)
    logger.info("LAYER 3 EXPLAINER - REAL WORKFLOW TEST")
    logger.info("="*60)
    
    # Test workflows - using publicly available n8n.io workflow IDs
    test_workflows = [
        {
            "id": "2462",
            "url": "https://n8n.io/workflows/2462",
            "name": "Angie, Personal AI Assistant"
        },
    ]
    
    results = []
    for workflow in test_workflows:
        logger.info(f"\n{'='*60}")
        logger.info(f"Testing: {workflow['name']} (ID: {workflow['id']})")
        logger.info(f"{'='*60}\n")
        
        result = await test_single_workflow(workflow['id'], workflow['url'])
        results.append({
            "workflow": workflow,
            "result": result
        })
        
        # Brief pause between requests
        await asyncio.sleep(2)
    
    # Summary
    logger.info("\n" + "="*60)
    logger.info("TEST SUMMARY")
    logger.info("="*60)
    
    successful = sum(1 for r in results if r['result'] and r['result']['success'])
    total = len(results)
    
    logger.info(f"Total workflows tested: {total}")
    logger.info(f"Successful extractions: {successful}")
    logger.info(f"Success rate: {(successful/total)*100:.1f}%")
    
    if successful > 0:
        avg_time = sum(r['result']['extraction_time'] for r in results if r['result'] and r['result']['success']) / successful
        logger.info(f"Average extraction time: {avg_time:.2f}s")
    
    logger.info("="*60)
    logger.success("Real workflow testing complete!")
    
    return results


if __name__ == "__main__":
    asyncio.run(main())









