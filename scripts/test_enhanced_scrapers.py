#!/usr/bin/env python3
"""
Test script for Enhanced Layer 2 V2 and Layer 3 V3 scrapers.
Tests both scrapers on the 7 video workflows to validate extraction.

Author: Dev1
Task: Enhanced L2 L3 Node Context Extraction
Date: October 15, 2025
"""

import asyncio
import sys
import os
from datetime import datetime
from typing import List, Dict, Any

# Add project paths
sys.path.append('.')
sys.path.append('../n8n-shared')

from src.scrapers.layer2_enhanced_v2 import extract_workflow_node_contexts
from src.scrapers.layer3_enhanced_v3 import extract_workflow_standalone_docs


# Test workflows with videos
TEST_WORKFLOWS = [
    {
        'id': '8237',
        'url': 'https://n8n.io/workflows/8237-personal-life-manager-with-telegram-google-services-and-voice-enabled-ai',
        'description': 'Personal Life Manager with Telegram, Google Services & Voice-Enabled AI'
    },
    {
        'id': '6270',
        'url': 'https://n8n.io/workflows/6270-ai-powered-technical-analyst-with-perplexity-r1-research',
        'description': 'AI-Powered Technical Analyst with Perplexity R1 Research'
    },
    {
        'id': '5170',
        'url': 'https://n8n.io/workflows/5170-traveler-co-pilot-ai-powered-telegram-for-easy-language-and-image-translation',
        'description': 'Traveler Co-Pilot: AI-Powered Telegram for Easy Language and Image Translation'
    },
    {
        'id': '4123',
        'url': 'https://n8n.io/workflows/4123-ai-research-agents-to-automate-pdf-analysis-with-mistrals-best-in-class-ocr',
        'description': 'AI Research Agents to Automate PDF Analysis with Mistral\'s Best-in-Class OCR'
    },
    {
        'id': '3891',
        'url': 'https://n8n.io/workflows/3891-ai-agent-chat',
        'description': 'AI agent chat'
    },
    {
        'id': '3456',
        'url': 'https://n8n.io/workflows/3456-build-your-first-ai-agent',
        'description': 'Build Your First AI Agent'
    },
    {
        'id': '2987',
        'url': 'https://n8n.io/workflows/2987-angie-personal-ai-assistant-with-telegram-voice-and-text',
        'description': 'Angie, Personal AI Assistant with Telegram Voice and Text'
    }
]


async def test_workflow(workflow: Dict[str, str]) -> Dict[str, Any]:
    """Test both scrapers on a single workflow."""
    workflow_id = workflow['id']
    workflow_url = workflow['url']
    description = workflow['description']
    
    print(f"\n🔍 Testing workflow {workflow_id}: {description}")
    print(f"   URL: {workflow_url}")
    
    results = {
        'workflow_id': workflow_id,
        'description': description,
        'layer2_v2': None,
        'layer3_v3': None,
        'success': False
    }
    
    try:
        # Test Layer 2 V2 (Node Contexts)
        print(f"   📍 Testing Layer 2 V2 (Node Contexts)...")
        layer2_result = await extract_workflow_node_contexts(
            workflow_id, workflow_url, headless=True, save_to_db=True
        )
        results['layer2_v2'] = layer2_result
        
        if layer2_result['success']:
            print(f"   ✅ Layer 2 V2: {len(layer2_result['node_contexts'])} node contexts found")
        else:
            print(f"   ❌ Layer 2 V2 failed: {layer2_result.get('error', 'Unknown error')}")
        
        # Test Layer 3 V3 (Standalone Docs)
        print(f"   📄 Testing Layer 3 V3 (Standalone Docs)...")
        layer3_result = await extract_workflow_standalone_docs(
            workflow_id, workflow_url, headless=True, save_to_db=True
        )
        results['layer3_v3'] = layer3_result
        
        if layer3_result['success']:
            print(f"   ✅ Layer 3 V3: {len(layer3_result['standalone_docs'])} standalone docs found")
        else:
            print(f"   ❌ Layer 3 V3 failed: {layer3_result.get('error', 'Unknown error')}")
        
        # Overall success
        results['success'] = layer2_result['success'] and layer3_result['success']
        
        if results['success']:
            print(f"   🎯 Overall: SUCCESS")
        else:
            print(f"   ⚠️ Overall: PARTIAL SUCCESS")
            
    except Exception as e:
        print(f"   ❌ Error testing workflow {workflow_id}: {e}")
        results['error'] = str(e)
    
    return results


async def run_comprehensive_test():
    """Run comprehensive test on all 7 video workflows."""
    print("🚀 Enhanced L2 L3 Scrapers Comprehensive Test")
    print("=" * 80)
    print(f"Testing {len(TEST_WORKFLOWS)} workflows with video content")
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    start_time = datetime.now()
    results = []
    
    for i, workflow in enumerate(TEST_WORKFLOWS, 1):
        print(f"\n📋 Progress: {i}/{len(TEST_WORKFLOWS)}")
        result = await test_workflow(workflow)
        results.append(result)
        
        # Small delay between workflows
        await asyncio.sleep(2)
    
    # Summary
    end_time = datetime.now()
    total_time = (end_time - start_time).total_seconds()
    
    print("\n" + "=" * 80)
    print("📊 COMPREHENSIVE TEST SUMMARY")
    print("=" * 80)
    
    successful_workflows = sum(1 for r in results if r['success'])
    total_node_contexts = sum(len(r['layer2_v2']['node_contexts']) for r in results if r['layer2_v2'] and r['layer2_v2']['success'])
    total_standalone_docs = sum(len(r['layer3_v3']['standalone_docs']) for r in results if r['layer3_v3'] and r['layer3_v3']['success'])
    
    print(f"✅ Successful workflows: {successful_workflows}/{len(TEST_WORKFLOWS)}")
    print(f"📍 Total node contexts extracted: {total_node_contexts}")
    print(f"📄 Total standalone docs extracted: {total_standalone_docs}")
    print(f"⏱️ Total test time: {total_time:.2f} seconds")
    print(f"📈 Average time per workflow: {total_time/len(TEST_WORKFLOWS):.2f} seconds")
    
    print("\n📋 Detailed Results:")
    for result in results:
        status = "✅ SUCCESS" if result['success'] else "⚠️ PARTIAL"
        layer2_count = len(result['layer2_v2']['node_contexts']) if result['layer2_v2'] and result['layer2_v2']['success'] else 0
        layer3_count = len(result['layer3_v3']['standalone_docs']) if result['layer3_v3'] and result['layer3_v3']['success'] else 0
        
        print(f"   {result['workflow_id']}: {status} - L2: {layer2_count} contexts, L3: {layer3_count} docs")
    
    print(f"\n🎯 Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return results


if __name__ == "__main__":
    asyncio.run(run_comprehensive_test())

