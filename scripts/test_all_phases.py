#!/usr/bin/env python3
"""
Test complete Layer 2 Enhanced extractor (all phases) on diverse workflows.
"""

import asyncio
import sys
import json
sys.path.insert(0, '/Users/tsvikavagman/Desktop/Code Projects/shared-tools/n8n-scraper')
from src.scrapers.layer2_enhanced import EnhancedLayer2Extractor
from datetime import datetime


# Diverse test workflows
TEST_WORKFLOWS = [
    {
        'id': '2462',
        'url': 'https://n8n.io/workflows/2462',
        'name': 'Angie AI Assistant (Telegram + Voice)',
        'complexity': 'High',
        'expected_nodes': '10+',
        'features': ['AI', 'Voice', 'Telegram', 'Multimodal']
    },
    {
        'id': '9343',
        'url': 'https://n8n.io/workflows/9343',
        'name': 'iOS App Store Monitor',
        'complexity': 'Medium',
        'expected_nodes': '8+',
        'features': ['Scheduled', 'API', 'Email', 'Monitoring']
    },
    {
        'id': '1954',
        'url': 'https://n8n.io/workflows/1954',
        'name': 'AI Agent Chat',
        'complexity': 'Medium',
        'expected_nodes': '5',
        'features': ['LangChain', 'AI', 'Chat', 'Memory']
    }
]


async def test_workflow(extractor, workflow):
    """Test extraction on a single workflow."""
    
    print(f"\n{'='*80}")
    print(f"🧪 TESTING: {workflow['name']}")
    print(f"   ID: {workflow['id']}")
    print(f"   Complexity: {workflow['complexity']}")
    print(f"   Expected Nodes: {workflow['expected_nodes']}")
    print(f"   Features: {', '.join(workflow['features'])}")
    print(f"{'='*80}\n")
    
    try:
        result = await extractor.extract_complete(workflow['id'], workflow['url'])
        
        # Extract key metrics
        api_data = result['sources']['api']
        iframe_data = result['sources']['iframe']
        
        print(f"✅ EXTRACTION SUCCESSFUL")
        print(f"   Time: {result['extraction_time']:.2f}s")
        print(f"   Completeness: {result['completeness']['merged']:.1f}%")
        
        print(f"\n📊 API DATA:")
        print(f"   Nodes: {api_data.get('node_count', 0)}")
        print(f"   Connections: {api_data.get('connection_count', 0)}")
        print(f"   Success: {api_data.get('success', False)}")
        
        print(f"\n📊 IFRAME DATA:")
        print(f"   Nodes: {iframe_data.get('node_count', 0)}")
        print(f"   Text blocks (basic): {len(iframe_data.get('text_content', {}).get('text_blocks', []))}")
        print(f"   Images (basic): {len(iframe_data.get('images', []))}")
        
        # PHASE 2: Visual Layout
        if 'visual_layout' in iframe_data:
            layout = iframe_data['visual_layout']
            print(f"\n📊 PHASE 2: Visual Layout")
            print(f"   Node positions: {len(layout.get('node_positions', []))}")
            print(f"   Canvas zoom: {layout.get('canvas_state', {}).get('zoom', 'N/A')}")
            print(f"   Canvas size: {layout.get('canvas_state', {}).get('width', 0):.0f} x {layout.get('canvas_state', {}).get('height', 0):.0f}")
            
            if layout.get('spatial_metrics'):
                metrics = layout['spatial_metrics']
                print(f"   Bounding box: {metrics.get('bounding_box', {}).get('width', 0):.0f} x {metrics.get('bounding_box', {}).get('height', 0):.0f}")
                print(f"   Density: {metrics.get('density', 0):.6f}")
        
        # PHASE 3: Enhanced Content
        if 'enhanced_content' in iframe_data:
            content = iframe_data['enhanced_content']
            print(f"\n📊 PHASE 3: Enhanced Content")
            print(f"   All text blocks: {len(content.get('all_text_blocks', []))}")
            print(f"   Total text length: {content.get('total_text_length', 0):,} chars")
            print(f"   Help texts: {len(content.get('help_texts', []))}")
            print(f"   Error messages: {len(content.get('error_messages', []))}")
            
            # Show text categories
            if content.get('all_text_blocks'):
                categories = {}
                for block in content['all_text_blocks']:
                    cat = block.get('category', 'unknown')
                    categories[cat] = categories.get(cat, 0) + 1
                print(f"   Text categories: {dict(sorted(categories.items(), key=lambda x: x[1], reverse=True))}")
        
        # PHASE 4: Media Content
        if 'media_content' in iframe_data:
            media = iframe_data['media_content']
            print(f"\n📊 PHASE 4: Media Content")
            print(f"   Videos: {media.get('video_count', 0)}")
            print(f"   Images: {media.get('image_count', 0)}")
            print(f"   SVGs: {media.get('svg_count', 0)}")
            
            # Show image types
            if media.get('images'):
                img_types = {}
                for img in media['images']:
                    img_type = img.get('type', 'unknown')
                    img_types[img_type] = img_types.get(img_type, 0) + 1
                print(f"   Image types: {img_types}")
        
        # Save result
        filename = f"complete_test_{workflow['id']}.json"
        with open(filename, 'w') as f:
            json.dump(result, f, indent=2, default=str)
        print(f"\n💾 Saved to: {filename}")
        
        return {
            'workflow_id': workflow['id'],
            'success': True,
            'extraction_time': result['extraction_time'],
            'completeness': result['completeness']['merged']
        }
        
    except Exception as e:
        print(f"\n❌ EXTRACTION FAILED: {e}")
        import traceback
        traceback.print_exc()
        return {
            'workflow_id': workflow['id'],
            'success': False,
            'error': str(e)
        }


async def main():
    """Test all workflows."""
    
    print("\n" + "="*80)
    print("🔬 TESTING COMPLETE LAYER 2 ENHANCED EXTRACTOR")
    print("   All Phases: 1 (Node Metadata) + 2 (Visual Layout) + 3 (Enhanced Text) + 4 (Media)")
    print("="*80)
    print(f"\nTesting {len(TEST_WORKFLOWS)} diverse workflows...")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    results = []
    
    async with EnhancedLayer2Extractor() as extractor:
        for i, workflow in enumerate(TEST_WORKFLOWS, 1):
            print(f"\n[{i}/{len(TEST_WORKFLOWS)}] ", end='')
            result = await test_workflow(extractor, workflow)
            results.append(result)
            
            # Rate limiting
            if i < len(TEST_WORKFLOWS):
                print(f"\n⏸️  Waiting 3 seconds before next workflow...")
                await asyncio.sleep(3)
    
    # Summary
    print(f"\n\n{'='*80}")
    print("📊 TEST SUMMARY")
    print(f"{'='*80}\n")
    
    successful = sum(1 for r in results if r['success'])
    failed = len(results) - successful
    
    print(f"Total Workflows: {len(results)}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    print(f"Success Rate: {successful/len(results)*100:.1f}%")
    
    if successful > 0:
        avg_time = sum(r.get('extraction_time', 0) for r in results if r['success']) / successful
        print(f"Average Extraction Time: {avg_time:.2f}s")
    
    print(f"\n✅ All test results saved to:")
    for workflow in TEST_WORKFLOWS:
        print(f"   • complete_test_{workflow['id']}.json")
    
    print(f"\nCompleted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n")


if __name__ == "__main__":
    asyncio.run(main())


