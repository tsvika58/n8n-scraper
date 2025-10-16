#!/usr/bin/env python3
"""
Analyze Video Detection Issues in Workflow 7639
Analyzes why the video detection algorithm missed the video in workflow 7639.

Author: Dev1
Task: Fix Video Detection Edge Cases
Date: October 16, 2025
"""

import asyncio
import sys
import json
import re
from datetime import datetime
sys.path.append('.')

from src.scrapers.unified_workflow_extractor import UnifiedWorkflowExtractor
from src.scrapers.layer2_json import WorkflowJSONExtractor


class VideoDetectionAnalyzer:
    """Analyzes video detection issues in workflow 7639."""
    
    def __init__(self):
        self.workflow_id = "7639"
        self.workflow_url = "https://n8n.io/workflows/7639-talk-to-your-google-sheets-using-chatgpt-5"
        self.expected_video_id = "qsrVPdo6svc"
        self.expected_video_url = "https://youtu.be/qsrVPdo6svc"
    
    async def analyze_video_detection(self):
        """Analyze why video detection failed in workflow 7639."""
        print("🔍 Analyzing Video Detection Issues in Workflow 7639")
        print("=" * 60)
        
        print(f"📹 Expected Video Information:")
        print(f"   Video ID: {self.expected_video_id}")
        print(f"   Video URL: {self.expected_video_url}")
        print(f"   Workflow: {self.workflow_id}")
        
        # Step 1: Extract JSON data
        print(f"\n📊 Step 1: Extracting JSON Data...")
        json_extractor = WorkflowJSONExtractor()
        
        try:
            json_result = await json_extractor.extract(self.workflow_id)
            if json_result['success']:
                json_data = json_result['data']
            else:
                raise Exception(f"JSON extraction failed: {json_result.get('error', 'Unknown error')}")
            print(f"   ✅ JSON extracted successfully")
            print(f"   📄 JSON contains {len(json_data.get('nodes', []))} nodes")
            
            # Save JSON for analysis
            with open(f'workflow_{self.workflow_id}_json.json', 'w') as f:
                json.dump(json_data, f, indent=2)
            print(f"   💾 JSON saved to workflow_{self.workflow_id}_json.json")
            
        except Exception as e:
            print(f"   ❌ JSON extraction failed: {e}")
            return None
        
        # Step 2: Analyze sticky notes for video content
        print(f"\n📝 Step 2: Analyzing Sticky Notes for Video Content...")
        sticky_notes = []
        for node in json_data.get('nodes', []):
            if node.get('type') == 'n8n-nodes-base.stickyNote':
                sticky_notes.append(node)
        
        print(f"   📌 Found {len(sticky_notes)} sticky notes")
        
        video_found_in_stickies = False
        for i, sticky in enumerate(sticky_notes):
            content = sticky.get('parameters', {}).get('content', '')
            print(f"\n   📝 Sticky Note {i+1}:")
            print(f"      Content: {content[:100]}...")
            
            # Check for video URLs
            video_urls = self._extract_youtube_links_from_text(content)
            if video_urls:
                print(f"      🎬 Found video URLs: {video_urls}")
                if self.expected_video_url in video_urls:
                    video_found_in_stickies = True
                    print(f"      ✅ Expected video found in this sticky note!")
            else:
                print(f"      ❌ No video URLs found")
        
        if not video_found_in_stickies:
            print(f"\n   🚨 ISSUE IDENTIFIED: Expected video not found in sticky notes!")
            print(f"   🔍 This explains why the algorithm missed it")
        
        # Step 3: Check for video in other locations
        print(f"\n🔍 Step 3: Checking for Video in Other Locations...")
        
        # Check all text content in the JSON
        all_text_content = self._extract_all_text_content(json_data)
        print(f"   📄 Extracted {len(all_text_content)} text fields from JSON")
        
        video_found_in_other_content = False
        for field_name, content in all_text_content.items():
            if content and isinstance(content, str):
                video_urls = self._extract_youtube_links_from_text(content)
                if video_urls and self.expected_video_url in video_urls:
                    print(f"   ✅ Found video in {field_name}: {content[:100]}...")
                    video_found_in_other_content = True
        
        if not video_found_in_other_content:
            print(f"   🚨 Video not found in any other JSON content")
        
        # Step 4: Analyze the current detection algorithm
        print(f"\n🔧 Step 4: Analyzing Current Detection Algorithm...")
        
        # Simulate the current algorithm
        current_algorithm_results = self._simulate_current_algorithm(json_data)
        print(f"   📊 Current algorithm results:")
        print(f"      Videos found: {len(current_algorithm_results)}")
        for video in current_algorithm_results:
            print(f"      - {video}")
        
        # Step 5: Identify the edge case
        print(f"\n🎯 Step 5: Identifying the Edge Case...")
        
        if not video_found_in_stickies and not video_found_in_other_content:
            print(f"   🚨 EDGE CASE IDENTIFIED:")
            print(f"      The video URL is not present in the JSON data at all!")
            print(f"      This means the video is embedded in the iframe but not in the JSON")
            print(f"      The current algorithm only looks at JSON content")
            print(f"      We need to add iframe content extraction to the algorithm")
        
        return {
            'json_data': json_data,
            'sticky_notes': sticky_notes,
            'video_found_in_stickies': video_found_in_stickies,
            'video_found_in_other_content': video_found_in_other_content,
            'current_algorithm_results': current_algorithm_results,
            'edge_case_identified': not video_found_in_stickies and not video_found_in_other_content
        }
    
    def _extract_youtube_links_from_text(self, text: str) -> list:
        """Extract YouTube links from text."""
        if not text:
            return []
        
        # YouTube URL patterns
        patterns = [
            r'https?://(?:www\.)?youtube\.com/watch\?v=([a-zA-Z0-9_-]{11})',
            r'https?://(?:www\.)?youtu\.be/([a-zA-Z0-9_-]{11})',
            r'https?://(?:www\.)?youtube\.com/embed/([a-zA-Z0-9_-]{11})',
            r'youtube\.com/watch\?v=([a-zA-Z0-9_-]{11})',
            r'youtu\.be/([a-zA-Z0-9_-]{11})',
            r'youtube\.com/embed/([a-zA-Z0-9_-]{11})'
        ]
        
        video_urls = []
        for pattern in patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                if 'youtu.be' in pattern:
                    video_urls.append(f'https://youtu.be/{match}')
                elif 'embed' in pattern:
                    video_urls.append(f'https://youtu.be/{match}')
                else:
                    video_urls.append(f'https://youtu.be/{match}')
        
        return list(set(video_urls))  # Remove duplicates
    
    def _extract_all_text_content(self, json_data: dict) -> dict:
        """Extract all text content from JSON data."""
        text_content = {}
        
        def extract_text_recursive(obj, path=""):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    current_path = f"{path}.{key}" if path else key
                    if isinstance(value, str) and len(value) > 10:
                        text_content[current_path] = value
                    else:
                        extract_text_recursive(value, current_path)
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    current_path = f"{path}[{i}]" if path else f"[{i}]"
                    extract_text_recursive(item, current_path)
            elif isinstance(obj, str) and len(obj) > 10:
                text_content[path] = obj
        
        extract_text_recursive(json_data)
        return text_content
    
    def _simulate_current_algorithm(self, json_data: dict) -> list:
        """Simulate the current video detection algorithm."""
        videos = []
        
        # Current algorithm only looks at sticky notes
        for node in json_data.get('nodes', []):
            if node.get('type') == 'n8n-nodes-base.stickyNote':
                content = node.get('parameters', {}).get('content', '')
                if content:
                    video_urls = self._extract_youtube_links_from_text(content)
                    for url in video_urls:
                        video_id = self._extract_youtube_id(url)
                        if video_id:
                            videos.append({
                                'url': url,
                                'youtube_id': video_id,
                                'source': 'sticky_note',
                                'content_preview': content[:100]
                            })
        
        return videos
    
    def _extract_youtube_id(self, url: str) -> str:
        """Extract YouTube video ID from URL."""
        patterns = [
            r'youtu\.be/([a-zA-Z0-9_-]{11})',
            r'youtube\.com/watch\?v=([a-zA-Z0-9_-]{11})',
            r'youtube\.com/embed/([a-zA-Z0-9_-]{11})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return ""
    
    def propose_algorithm_improvements(self, analysis_results):
        """Propose improvements to the video detection algorithm."""
        print(f"\n🚀 Step 6: Proposing Algorithm Improvements...")
        
        if analysis_results['edge_case_identified']:
            print(f"   🎯 EDGE CASE SOLUTION:")
            print(f"      The video is embedded in the iframe but not in the JSON")
            print(f"      We need to add iframe content extraction to the algorithm")
            
            print(f"\n   💡 PROPOSED IMPROVEMENTS:")
            print(f"      1. Add iframe content extraction using Playwright")
            print(f"      2. Look for video elements in the iframe DOM")
            print(f"      3. Extract video URLs from iframe content")
            print(f"      4. Combine JSON-based detection with iframe-based detection")
            
            print(f"\n   🔧 IMPLEMENTATION PLAN:")
            print(f"      - Add iframe navigation to the unified extractor")
            print(f"      - Use Playwright to find video elements in iframe")
            print(f"      - Extract video URLs from iframe DOM")
            print(f"      - Merge iframe results with JSON results")
            print(f"      - Deduplicate videos found in both sources")
        
        return {
            'needs_iframe_extraction': analysis_results['edge_case_identified'],
            'improvements': [
                'Add iframe content extraction using Playwright',
                'Look for video elements in the iframe DOM',
                'Extract video URLs from iframe content',
                'Combine JSON-based detection with iframe-based detection'
            ]
        }
    
    async def run_analysis(self):
        """Run complete video detection analysis."""
        print("🚀 Starting Video Detection Analysis for Workflow 7639")
        print(f"⏰ Analysis started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Analyze video detection
        analysis_results = await self.analyze_video_detection()
        
        if analysis_results is None:
            print("❌ Analysis failed - cannot proceed with improvements")
            return None
        
        # Propose improvements
        improvements = self.propose_algorithm_improvements(analysis_results)
        
        print(f"\n⏰ Analysis completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return {
            'analysis_results': analysis_results,
            'improvements': improvements
        }


async def main():
    """Main analysis function."""
    analyzer = VideoDetectionAnalyzer()
    results = await analyzer.run_analysis()
    return results


if __name__ == "__main__":
    asyncio.run(main())
