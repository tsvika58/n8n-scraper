#!/usr/bin/env python3
"""
Scrape a single workflow and show all extracted data across all layers.

Usage:
    python scripts/scrape_single_workflow.py <workflow_id>
"""

import asyncio
import sys
import json
from pathlib import Path
from datetime import datetime

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.orchestrator.e2e_pipeline import E2EPipeline
from src.storage.database import get_session
from src.storage.repository import WorkflowRepository
from loguru import logger

async def scrape_workflow(workflow_id: str):
    """Scrape a single workflow through the complete E2E pipeline."""
    
    url = f"https://n8n.io/workflows/{workflow_id}"
    
    print("="*100)
    print(f"🚀 SCRAPING WORKFLOW: {workflow_id}")
    print("="*100)
    print(f"URL: {url}")
    print()
    print("📊 Extracting all 7 layers + multimodal data...")
    print()
    
    # Initialize E2E pipeline
    pipeline = E2EPipeline()
    
    # Process the workflow
    result = await pipeline.process_workflow(workflow_id, url)
    
    print()
    print("="*100)
    print("✅ EXTRACTION COMPLETE")
    print("="*100)
    print()
    
    if result['success']:
        print(f"✅ Status: SUCCESS")
        print(f"⏱️  Processing Time: {result['extraction_time']:.2f} seconds")
        print(f"⭐ Quality Score: {result.get('quality', {}).get('score', 0):.1f}/100")
        print()
        
        print("📊 Layers Extracted:")
        for i in range(1, 8):
            layer_key = f'layer{i}_success'
            status = "✅" if result.get('layers', {}).get(f'layer{i}', {}).get('success', False) else "❌"
            layer_time = result.get('layers', {}).get(f'layer{i}', {}).get('extraction_time', 0)
            print(f"   {status} Layer {i}: {layer_time:.2f}s")
        
        print()
        print("💾 Storing in database...")
        
        # Store in database
        with get_session() as session:
            repo = WorkflowRepository(session)
            stored = repo.create_workflow(result)
            
            if stored:
                print("✅ Successfully stored in database!")
                print()
                print(f"🌐 View in Database Viewer: http://localhost:5004/workflow/{workflow_id}")
                print()
                
                # Show summary of extracted data
                print("="*100)
                print("📋 EXTRACTED DATA SUMMARY")
                print("="*100)
                print()
                
                # Layer 1: Metadata
                if 'layer1_data' in result:
                    data = result['layer1_data']
                    print("📌 Layer 1 - Metadata:")
                    print(f"   Title: {data.get('title', 'N/A')}")
                    print(f"   Author: {data.get('author', 'N/A')}")
                    print(f"   Description: {data.get('description', 'N/A')[:100]}...")
                    print(f"   Categories: {data.get('primary_category', 'N/A')}")
                    print(f"   Tags: {len(data.get('node_tags', []))} node tags, {len(data.get('general_tags', []))} general tags")
                    print()
                
                # Layer 2: Structure
                if 'layer2_data' in result:
                    data = result['layer2_data']
                    print("🏗️  Layer 2 - Structure:")
                    print(f"   Nodes: {data.get('node_count', 0)}")
                    print(f"   Connections: {data.get('connection_count', 0)}")
                    print(f"   Node Types: {len(data.get('node_types', []))}")
                    print()
                
                # Layer 3: Content
                if 'layer3_data' in result:
                    data = result['layer3_data']
                    print("📝 Layer 3 - Content:")
                    text_len = len(data.get('explainer_text', ''))
                    html_len = len(data.get('explainer_html', ''))
                    print(f"   Explainer Text: {text_len} characters")
                    print(f"   Explainer HTML: {html_len} characters")
                    print(f"   Videos: {data.get('video_count', 0)}")
                    print(f"   iFrames: {data.get('iframe_count', 0)}")
                    print()
                
                # Layer 4: Business Intelligence
                if 'layer4_data' in result:
                    data = result['layer4_data']
                    print("💼 Layer 4 - Business Intelligence:")
                    print(f"   Business Value Score: {data.get('business_value_score', 0)}/100")
                    print(f"   Function: {data.get('business_function', 'N/A')}")
                    print(f"   Process: {data.get('business_process', 'N/A')}")
                    print(f"   Automation Level: {data.get('business_automation', 'N/A')}")
                    print()
                
                # Layer 5: Community
                if 'layer5_data' in result:
                    data = result['layer5_data']
                    print("👥 Layer 5 - Community Data:")
                    print(f"   Engagement Score: {data.get('community_engagement_score', 0)}")
                    print(f"   Activity Score: {data.get('community_activity_score', 0)}")
                    print(f"   Sentiment Score: {data.get('community_sentiment_score', 0)}")
                    print()
                
                # Layer 6: Technical
                if 'layer6_data' in result:
                    data = result['layer6_data']
                    print("🔧 Layer 6 - Technical Details:")
                    print(f"   Documentation Level: {data.get('workflow_documentation_level', 'N/A')}")
                    print(f"   Customization Level: {data.get('workflow_customization_level', 'N/A')}")
                    print(f"   Automation Level: {data.get('workflow_automation_level', 'N/A')}")
                    print()
                
                # Layer 7: Performance
                if 'layer7_data' in result:
                    data = result['layer7_data']
                    print("📈 Layer 7 - Performance Analytics:")
                    print(f"   Performance Benchmarks: {len(data.get('performance_benchmarks', {}))} metrics")
                    print(f"   Usage Statistics: {len(data.get('usage_statistics', {}))} stats")
                    print(f"   Error Analytics: {len(data.get('error_analytics', {}))} metrics")
                    print()
                
                return True
            else:
                print("❌ Failed to store in database")
                return False
    else:
        print(f"❌ Status: FAILED")
        print(f"Error: {result.get('error_message', 'Unknown error')}")
        return False

async def main():
    if len(sys.argv) > 1:
        workflow_id = sys.argv[1]
    else:
        workflow_id = "6270"  # Default to the AI Agent workflow
    
    success = await scrape_workflow(workflow_id)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    asyncio.run(main())

