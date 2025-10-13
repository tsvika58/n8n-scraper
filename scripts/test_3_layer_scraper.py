#!/usr/bin/env python3
"""
Test 3-Layer Scraper System
Validates all capabilities:
1. Layer 1: Workflow page data (title, author, description, etc.)
2. Layer 2: Workflow structure via iframe (nodes, connections, configurations)
3. Layer 3: Multimedia extraction (videos + transcripts, images + OCR)
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.storage.database import get_session
from src.storage.models import Workflow
from src.scrapers.layer1_metadata import PageMetadataExtractor
from src.scrapers.layer2_json import WorkflowJSONExtractor
from src.scrapers.multimodal_processor import MultimodalProcessor
from loguru import logger


async def test_3_layer_scraping(workflow_id: str, url: str):
    """
    Test complete 3-layer scraping on a single workflow.
    """
    print("=" * 80)
    print("🧪 TESTING 3-LAYER SCRAPER")
    print("=" * 80)
    print(f"Workflow ID: {workflow_id}")
    print(f"URL: {url}")
    print("=" * 80)
    print()
    
    results = {
        'layer1': {'success': False, 'data': None},
        'layer2': {'success': False, 'data': None},
        'layer3': {'success': False, 'data': None}
    }
    
    # ========================================================================
    # LAYER 1: Page Metadata Extraction
    # ========================================================================
    print("🔄 LAYER 1: Extracting Page Metadata...")
    print("-" * 80)
    
    try:
        layer1_extractor = PageMetadataExtractor()
        # PageMetadataExtractor initializes in __init__, no need for separate initialize()
        
        layer1_result = await layer1_extractor.extract(workflow_id, url)
        
        if layer1_result and layer1_result.get('success'):
            layer1_data = layer1_result.get('data', {})
            results['layer1']['success'] = True
            results['layer1']['data'] = layer1_data
            
            print("✅ LAYER 1 SUCCESS")
            print(f"   Title: {layer1_data.get('title', 'N/A')}")
            print(f"   Author: {layer1_data.get('author', 'N/A')}")
            print(f"   Views: {layer1_data.get('views', 0)}")
            print(f"   Categories: {layer1_data.get('primary_category', 'N/A')} + {len(layer1_data.get('secondary_categories', []))} secondary")
            print(f"   Description Length: {len(layer1_data.get('description', ''))} chars")
        else:
            print("❌ LAYER 1 FAILED: No data returned")
        
        # Layer1 cleanup happens automatically
        
    except Exception as e:
        print(f"❌ LAYER 1 ERROR: {e}")
        logger.error(f"Layer 1 failed: {e}")
    
    print()
    
    # ========================================================================
    # LAYER 2: Workflow JSON/Structure Extraction (via iframe)
    # ========================================================================
    print("🔄 LAYER 2: Extracting Workflow Structure (iframe)...")
    print("-" * 80)
    
    try:
        layer2_extractor = WorkflowJSONExtractor()
        # Layer2 extract() only takes workflow_id
        layer2_data = await layer2_extractor.extract(workflow_id)
        
        if layer2_data:
            results['layer2']['success'] = True
            results['layer2']['data'] = layer2_data
            
            nodes = layer2_data.get('nodes', [])
            connections = layer2_data.get('connections', [])
            
            print("✅ LAYER 2 SUCCESS")
            print(f"   Nodes: {len(nodes)}")
            print(f"   Connections: {len(connections)}")
            
            if nodes:
                print(f"   Node Types:")
                node_types = {}
                for node in nodes:
                    node_type = node.get('type', 'unknown')
                    node_types[node_type] = node_types.get(node_type, 0) + 1
                
                for node_type, count in sorted(node_types.items()):
                    print(f"      - {node_type}: {count}")
        else:
            print("❌ LAYER 2 FAILED: No workflow JSON found")
    
    except Exception as e:
        print(f"❌ LAYER 2 ERROR: {e}")
        logger.error(f"Layer 2 failed: {e}")
    
    print()
    
    # ========================================================================
    # LAYER 3: Multimedia Extraction (Videos + Transcripts, Images + OCR)
    # ========================================================================
    print("🔄 LAYER 3: Extracting Multimedia (Videos + Transcripts, Images + OCR)...")
    print("-" * 80)
    
    try:
        layer3_processor = MultimodalProcessor()
        await layer3_processor.initialize()
        
        layer3_data = await layer3_processor.process_workflow(workflow_id, url)
        
        if layer3_data and layer3_data.get('success'):
            results['layer3']['success'] = True
            results['layer3']['data'] = layer3_data
            
            print("✅ LAYER 3 SUCCESS")
            print(f"   Images Found: {layer3_data.get('images_found', 0)}")
            print(f"   Images with OCR Success: {layer3_data.get('images_success', 0)}")
            print(f"   Videos Found: {layer3_data.get('videos_found', 0)}")
            print(f"   Videos with Transcript Success: {layer3_data.get('videos_success', 0)}")
            
            video_urls = layer3_data.get('video_urls', [])
            if video_urls:
                print(f"   Video URLs:")
                for i, video_url in enumerate(video_urls, 1):
                    print(f"      {i}. {video_url[:60]}...")
        else:
            print("⚠️  LAYER 3 PARTIAL: Some multimedia might be missing")
        
        await layer3_processor.cleanup()
    
    except Exception as e:
        print(f"❌ LAYER 3 ERROR: {e}")
        logger.error(f"Layer 3 failed: {e}")
    
    print()
    
    # ========================================================================
    # SUMMARY
    # ========================================================================
    print("=" * 80)
    print("📊 SCRAPING SUMMARY")
    print("=" * 80)
    
    success_count = sum(1 for r in results.values() if r['success'])
    
    print(f"Layer 1 (Page Metadata): {'✅ PASS' if results['layer1']['success'] else '❌ FAIL'}")
    print(f"Layer 2 (Workflow Structure): {'✅ PASS' if results['layer2']['success'] else '❌ FAIL'}")
    print(f"Layer 3 (Multimedia): {'✅ PASS' if results['layer3']['success'] else '❌ FAIL'}")
    print()
    print(f"Overall: {success_count}/3 layers successful")
    print("=" * 80)
    
    return results


async def main():
    """Main test function."""
    
    # Test on workflow 7423 (has YouTube video and rich content)
    workflow_id = "7423"
    url = "https://n8n.io/workflows/7423-lead-generation-agent/"
    
    print()
    print("🚀 STARTING 3-LAYER SCRAPER TEST")
    print()
    
    results = await test_3_layer_scraping(workflow_id, url)
    
    print()
    
    # Show detailed results
    if results['layer1']['success']:
        data = results['layer1']['data']
        print("📄 LAYER 1 DETAILS:")
        print(f"   Title: {data.get('title')}")
        print(f"   URL: {data.get('url')}")
        print(f"   Author: {data.get('author', {}).get('name')}")
        print()
    
    if results['layer2']['success']:
        data = results['layer2']['data']
        print("🔧 LAYER 2 DETAILS:")
        print(f"   Total Nodes: {len(data.get('nodes', []))}")
        print(f"   Total Connections: {len(data.get('connections', []))}")
        print()
    
    if results['layer3']['success']:
        data = results['layer3']['data']
        print("🎬 LAYER 3 DETAILS:")
        print(f"   Images: {data.get('images_found', 0)} found, {data.get('images_success', 0)} with OCR")
        print(f"   Videos: {data.get('videos_found', 0)} found, {data.get('videos_success', 0)} with transcripts")
        print()


if __name__ == '__main__':
    asyncio.run(main())

