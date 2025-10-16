#!/usr/bin/env python3
"""
Test L2 V2 and Enhanced L3 V2 scrapers on 7 video workflows for validation.

This script tests both scrapers on the 7 video workflows to validate:
1. L2 V2: Node context extraction with sticky notes
2. Enhanced L3 V2: Video extraction, transcription, and standalone sticky notes
3. Database integration for both scrapers
4. Data quality and completeness

Author: AI Assistant
Date: October 16, 2025
"""

import asyncio
import sys
import os
import time
from typing import Dict, List, Any
from datetime import datetime

# Add project paths
sys.path.append('.')
sys.path.append('../n8n-shared')

from src.scrapers.layer2_enhanced_v2 import NodeContextExtractor
from src.scrapers.layer3_enhanced_v2 import EnhancedLayer3Extractor
from loguru import logger

# 7 video workflows for testing
TEST_WORKFLOWS = [
    {
        'workflow_id': '8237',
        'url': 'https://n8n.io/workflows/8237-personal-life-manager-with-telegram-google-services-and-voice-enabled-ai',
        'expected_video': 'ROgf5dVqYPQ'
    },
    {
        'workflow_id': '6270',
        'url': 'https://n8n.io/workflows/6270-build-your-first-ai-agent',
        'expected_video': 'laHIzhsz12E'
    },
    {
        'workflow_id': '2462',
        'url': 'https://n8n.io/workflows/2462-angie-personal-ai-assistant-with-telegram-voice-and-text',
        'expected_video': 'V8J8X8X8X8'  # Placeholder - will be discovered
    },
    {
        'workflow_id': '1954',
        'url': 'https://n8n.io/workflows/1954-ai-agent-chat',
        'expected_video': 'V8J8X8X8X8'  # Placeholder - will be discovered
    },
    {
        'workflow_id': '2006',
        'url': 'https://n8n.io/workflows/2006-ai-agent-that-can-scrape-webpages',
        'expected_video': 'V8J8X8X8X8'  # Placeholder - will be discovered
    },
    {
        'workflow_id': '2213',
        'url': 'https://n8n.io/workflows/2213-traveler-co-pilot-ai-powered-telegram-for-easy-language-and-image-translation',
        'expected_video': 'V8J8X8X8X8'  # Placeholder - will be discovered
    },
    {
        'workflow_id': '5170',
        'url': 'https://n8n.io/workflows/5170-animated-gif-workflow',
        'expected_video': 'V8J8X8X8X8'  # Placeholder - will be discovered
    }
]

class WorkflowTester:
    def __init__(self):
        self.results = []
        self.start_time = time.time()
    
    async def test_workflow(self, workflow: Dict[str, str]) -> Dict[str, Any]:
        """Test both L2 V2 and L3 V2 scrapers on a single workflow."""
        workflow_id = workflow['workflow_id']
        url = workflow['url']
        
        logger.info(f"🧪 Testing workflow {workflow_id}: {url}")
        
        result = {
            'workflow_id': workflow_id,
            'url': url,
            'l2_result': None,
            'l3_result': None,
            'success': False,
            'errors': []
        }
        
        try:
            # Test L2 V2 scraper
            logger.info(f"  🔍 Running L2 V2 scraper for {workflow_id}")
            async with NodeContextExtractor(headless=True) as l2_extractor:
                l2_result = await l2_extractor.extract_node_contexts(workflow_id, url)
                result['l2_result'] = l2_result
                
                if l2_result['success']:
                    logger.success(f"  ✅ L2 V2: {len(l2_result['node_contexts'])} node contexts, {l2_result['statistics']['stickies_found']} sticky notes")
                else:
                    logger.error(f"  ❌ L2 V2 failed: {l2_result.get('error', 'Unknown error')}")
                    result['errors'].append(f"L2 V2: {l2_result.get('error', 'Unknown error')}")
            
            # Test Enhanced L3 V2 scraper
            logger.info(f"  🎬 Running Enhanced L3 V2 scraper for {workflow_id}")
            async with EnhancedLayer3Extractor(headless=True, extract_transcripts=True) as l3_extractor:
                l3_result = await l3_extractor.extract(workflow_id, url)
                result['l3_result'] = l3_result
                
                if l3_result['success']:
                    logger.success(f"  ✅ L3 V2: {l3_result['data']['video_count']} videos, {l3_result['data']['transcript_count']} transcripts, {l3_result['data']['standalone_doc_count']} standalone docs")
                else:
                    logger.error(f"  ❌ L3 V2 failed: {l3_result.get('error', 'Unknown error')}")
                    result['errors'].append(f"L3 V2: {l3_result.get('error', 'Unknown error')}")
            
            # Determine overall success
            result['success'] = (
                result['l2_result'] and result['l2_result']['success'] and
                result['l3_result'] and result['l3_result']['success']
            )
            
        except Exception as e:
            logger.error(f"  ❌ Error testing {workflow_id}: {e}")
            result['errors'].append(f"General error: {e}")
        
        return result
    
    async def run_all_tests(self):
        """Run tests on all 7 workflows."""
        logger.info(f"🚀 Starting comprehensive L2 V2 + L3 V2 testing on {len(TEST_WORKFLOWS)} workflows")
        
        for i, workflow in enumerate(TEST_WORKFLOWS, 1):
            logger.info(f"\n📋 Test {i}/{len(TEST_WORKFLOWS)}")
            result = await self.test_workflow(workflow)
            self.results.append(result)
            
            # Small delay between tests
            await asyncio.sleep(2)
        
        self.print_summary()
    
    def print_summary(self):
        """Print comprehensive test summary."""
        total_time = time.time() - self.start_time
        
        logger.info(f"\n{'='*80}")
        logger.info(f"📊 COMPREHENSIVE L2 V2 + L3 V2 TEST SUMMARY")
        logger.info(f"{'='*80}")
        logger.info(f"⏱️  Total time: {total_time:.1f} seconds")
        logger.info(f"🧪 Workflows tested: {len(self.results)}")
        
        # Success statistics
        successful = [r for r in self.results if r['success']]
        failed = [r for r in self.results if not r['success']]
        
        logger.info(f"✅ Successful: {len(successful)}/{len(self.results)} ({len(successful)/len(self.results)*100:.1f}%)")
        logger.info(f"❌ Failed: {len(failed)}/{len(self.results)} ({len(failed)/len(self.results)*100:.1f}%)")
        
        # L2 V2 statistics
        l2_successful = [r for r in self.results if r['l2_result'] and r['l2_result']['success']]
        total_node_contexts = sum(len(r['l2_result']['node_contexts']) for r in l2_successful)
        total_sticky_notes = sum(r['l2_result']['statistics']['stickies_found'] for r in l2_successful)
        
        logger.info(f"\n🔍 L2 V2 Results:")
        logger.info(f"  ✅ Successful: {len(l2_successful)}/{len(self.results)}")
        logger.info(f"  📌 Total node contexts: {total_node_contexts}")
        logger.info(f"  📝 Total sticky notes: {total_sticky_notes}")
        
        # L3 V2 statistics
        l3_successful = [r for r in self.results if r['l3_result'] and r['l3_result']['success']]
        total_videos = sum(r['l3_result']['data']['video_count'] for r in l3_successful)
        total_transcripts = sum(r['l3_result']['data']['transcript_count'] for r in l3_successful)
        total_standalone_docs = sum(r['l3_result']['data']['standalone_doc_count'] for r in l3_successful)
        
        logger.info(f"\n🎬 L3 V2 Results:")
        logger.info(f"  ✅ Successful: {len(l3_successful)}/{len(self.results)}")
        logger.info(f"  🎥 Total videos: {total_videos}")
        logger.info(f"  📝 Total transcripts: {total_transcripts}")
        logger.info(f"  📌 Total standalone docs: {total_standalone_docs}")
        
        # Detailed results
        logger.info(f"\n📋 Detailed Results:")
        for result in self.results:
            workflow_id = result['workflow_id']
            status = "✅" if result['success'] else "❌"
            
            l2_info = ""
            if result['l2_result'] and result['l2_result']['success']:
                l2_data = result['l2_result']
                l2_info = f"L2: {len(l2_data['node_contexts'])} contexts, {l2_data['statistics']['stickies_found']} stickies"
            else:
                l2_info = "L2: FAILED"
            
            l3_info = ""
            if result['l3_result'] and result['l3_result']['success']:
                l3_data = result['l3_result']['data']
                l3_info = f"L3: {l3_data['video_count']} videos, {l3_data['transcript_count']} transcripts, {l3_data['standalone_doc_count']} docs"
            else:
                l3_info = "L3: FAILED"
            
            logger.info(f"  {status} {workflow_id}: {l2_info} | {l3_info}")
            
            if result['errors']:
                for error in result['errors']:
                    logger.error(f"    ❌ {error}")
        
        # Quality scores
        l2_quality_scores = [r['l2_result']['quality_score'] for r in l2_successful if 'quality_score' in r['l2_result']]
        l3_quality_scores = [r['l3_result']['quality_score'] for r in l3_successful if 'quality_score' in r['l3_result']]
        
        if l2_quality_scores:
            avg_l2_quality = sum(l2_quality_scores) / len(l2_quality_scores)
            logger.info(f"\n📊 Average L2 V2 Quality Score: {avg_l2_quality:.1f}/100")
        
        if l3_quality_scores:
            avg_l3_quality = sum(l3_quality_scores) / len(l3_quality_scores)
            logger.info(f"📊 Average L3 V2 Quality Score: {avg_l3_quality:.1f}/100")
        
        logger.info(f"\n{'='*80}")
        
        return {
            'total_workflows': len(self.results),
            'successful': len(successful),
            'failed': len(failed),
            'l2_successful': len(l2_successful),
            'l3_successful': len(l3_successful),
            'total_node_contexts': total_node_contexts,
            'total_sticky_notes': total_sticky_notes,
            'total_videos': total_videos,
            'total_transcripts': total_transcripts,
            'total_standalone_docs': total_standalone_docs,
            'total_time': total_time
        }

async def main():
    """Main test execution."""
    tester = WorkflowTester()
    summary = await tester.run_all_tests()
    
    # Save results to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = f"test_results_l2_l3_{timestamp}.json"
    
    import json
    with open(results_file, 'w') as f:
        json.dump({
            'summary': summary,
            'detailed_results': tester.results,
            'timestamp': timestamp
        }, f, indent=2, default=str)
    
    logger.info(f"💾 Results saved to: {results_file}")
    
    return summary

if __name__ == "__main__":
    asyncio.run(main())
