# Layer 3 Enhancement Plan - CRITICAL GAPS IDENTIFIED

## 🚨 **User Feedback: Critical Gaps**

The user identified 4 critical missing features:

1. ❌ **Video Deduplication**: Are videos different or versions of the same?
2. ❌ **Transcript Extraction**: Have we extracted transcripts from videos?
3. ❌ **Complete Iframe Crawling**: Are we getting ALL content or just visual discovery?
4. ❌ **Systematic Processes**: Do we have methods and processes for comprehensive extraction?

---

## 📊 **Current State Assessment**

### ✅ What We HAVE
- Video URL extraction (basic)
- Visual discovery with Playwright
- Text content extraction from visible elements
- Fallback regex scanning

### ❌ What We're MISSING
1. **Video Deduplication**
   - Not checking if videos are duplicates
   - Not comparing video IDs
   - Not detecting different versions of same video

2. **Transcript Extraction**
   - `TranscriptExtractor` exists but NOT integrated
   - No transcript extraction in Layer 3
   - Missing critical video content

3. **Complete Iframe Content**
   - Only extracting VISIBLE content
   - Missing hidden/lazy-loaded content
   - Not scrolling through iframes
   - Not triggering dynamic content loading

4. **Systematic Processes**
   - Ad-hoc discovery methods
   - No comprehensive crawling strategy
   - Missing iframe DOM traversal
   - No screenshot comparison for validation

---

## 🎯 **Required Enhancements**

### **Enhancement 1: Video Deduplication**

**Goal**: Ensure we only keep unique videos

**Implementation**:
```python
def _deduplicate_videos(self, videos: List[Dict]) -> List[Dict]:
    """
    Deduplicate videos by:
    1. YouTube video ID
    2. URL normalization
    3. Title similarity
    """
    seen_ids = set()
    unique_videos = []
    
    for video in videos:
        # Extract video ID from URL
        video_id = self._extract_video_id(video.get('url', ''))
        
        if video_id and video_id not in seen_ids:
            seen_ids.add(video_id)
            unique_videos.append(video)
    
    return unique_videos

def _extract_video_id(self, url: str) -> Optional[str]:
    """Extract YouTube video ID from URL"""
    patterns = [
        r'youtube\.com/watch\?v=([^&]+)',
        r'youtu\.be/([^?]+)',
        r'youtube\.com/embed/([^?]+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    return None
```

### **Enhancement 2: Transcript Extraction**

**Goal**: Extract ALL video transcripts

**Implementation**:
```python
async def _extract_video_transcripts(self, videos: List[Dict]) -> Dict[str, str]:
    """
    Extract transcripts for all YouTube videos.
    
    Uses TranscriptExtractor to get video transcripts.
    """
    from src.scrapers.transcript_extractor import TranscriptExtractor
    
    transcripts = {}
    
    async with TranscriptExtractor(headless=True) as extractor:
        for video in videos:
            video_url = video.get('url')
            if video_url and 'youtube' in video_url:
                try:
                    success, transcript, error = await extractor.extract_transcript(
                        video_url,
                        video.get('id', '')
                    )
                    
                    if success and transcript:
                        transcripts[video_url] = transcript
                        video['transcript'] = transcript
                        video['has_transcript'] = True
                    else:
                        video['has_transcript'] = False
                        video['transcript_error'] = error
                        
                except Exception as e:
                    logger.warning(f"Error extracting transcript for {video_url}: {e}")
                    video['has_transcript'] = False
    
    return transcripts
```

### **Enhancement 3: Complete Iframe Crawling**

**Goal**: Extract ALL content from iframe, not just visible

**Implementation**:
```python
async def _comprehensive_iframe_crawl(self, frame) -> Dict:
    """
    Comprehensive iframe crawling:
    1. Scroll through entire iframe
    2. Trigger lazy loading
    3. Extract ALL DOM content
    4. Get hidden/dynamic content
    """
    content = {
        'all_text': '',
        'all_html': '',
        'all_links': [],
        'all_media': [],
        'dynamic_content': []
    }
    
    # 1. Scroll through iframe to trigger lazy loading
    await self._scroll_through_frame(frame)
    
    # 2. Extract complete DOM content
    all_html = await frame.content()
    content['all_html'] = all_html
    
    # 3. Parse with BeautifulSoup for comprehensive extraction
    soup = BeautifulSoup(all_html, 'html.parser')
    
    # Extract ALL text (including hidden)
    content['all_text'] = soup.get_text(separator='\n', strip=True)
    
    # Extract ALL links
    for link in soup.find_all('a', href=True):
        content['all_links'].append(link['href'])
    
    # Extract ALL media (images, videos, audio)
    for media in soup.find_all(['img', 'video', 'audio', 'source']):
        content['all_media'].append({
            'tag': media.name,
            'src': media.get('src', ''),
            'alt': media.get('alt', ''),
            'data_src': media.get('data-src', '')
        })
    
    # 4. Extract dynamic/lazy-loaded content
    dynamic = await frame.evaluate('''
        () => {
            const content = [];
            
            // Get all data attributes that might contain content
            document.querySelectorAll('[data-src], [data-content], [data-text]').forEach(el => {
                content.push({
                    tag: el.tagName,
                    data_src: el.dataset.src || '',
                    data_content: el.dataset.content || '',
                    data_text: el.dataset.text || ''
                });
            });
            
            return content;
        }
    ''')
    content['dynamic_content'] = dynamic
    
    return content

async def _scroll_through_frame(self, frame):
    """Scroll through frame to trigger lazy loading"""
    try:
        # Get frame height
        height = await frame.evaluate('() => document.body.scrollHeight')
        
        # Scroll down in steps
        scroll_step = 500
        current_position = 0
        
        while current_position < height:
            await frame.evaluate(f'() => window.scrollTo(0, {current_position})')
            await frame.wait_for_timeout(500)  # Wait for content to load
            current_position += scroll_step
        
        # Scroll back to top
        await frame.evaluate('() => window.scrollTo(0, 0)')
        
    except Exception as e:
        logger.warning(f"Error scrolling through frame: {e}")
```

### **Enhancement 4: Systematic Process Framework**

**Goal**: Create systematic, repeatable process

**Implementation**:
```python
class ComprehensiveIframeExtractor:
    """
    Systematic iframe extraction with multiple passes:
    
    Pass 1: Visual Discovery (current implementation)
    Pass 2: DOM Traversal (comprehensive HTML parsing)
    Pass 3: Dynamic Content Triggering (scrolling, clicking, lazy loading)
    Pass 4: Validation (screenshot comparison, content verification)
    """
    
    async def extract_comprehensive(self, page: Page, workflow_id: str) -> Dict:
        """
        Multi-pass comprehensive extraction.
        """
        result = {
            'pass1_visual': {},
            'pass2_dom': {},
            'pass3_dynamic': {},
            'pass4_validation': {},
            'merged': {}
        }
        
        # Pass 1: Visual Discovery
        result['pass1_visual'] = await self._pass1_visual_discovery(page)
        
        # Pass 2: DOM Traversal
        result['pass2_dom'] = await self._pass2_dom_traversal(page)
        
        # Pass 3: Dynamic Content
        result['pass3_dynamic'] = await self._pass3_dynamic_content(page)
        
        # Pass 4: Validation
        result['pass4_validation'] = await self._pass4_validation(page, workflow_id)
        
        # Merge all results
        result['merged'] = self._merge_all_passes(result)
        
        return result
    
    async def _pass2_dom_traversal(self, page: Page) -> Dict:
        """
        Pass 2: Comprehensive DOM traversal.
        
        Extracts ALL content from DOM, not just visible.
        """
        dom_content = {
            'all_iframes': [],
            'all_text_nodes': [],
            'all_scripts': [],
            'all_styles': [],
            'all_meta': [],
            'all_data_attributes': []
        }
        
        # Get ALL iframes
        iframes = await page.query_selector_all('iframe')
        for iframe in iframes:
            try:
                src = await iframe.get_attribute('src')
                frame = await iframe.content_frame()
                
                if frame:
                    # Get complete iframe HTML
                    iframe_html = await frame.content()
                    
                    dom_content['all_iframes'].append({
                        'src': src,
                        'html': iframe_html,
                        'comprehensive_content': await self._comprehensive_iframe_crawl(frame)
                    })
            except Exception as e:
                logger.warning(f"Error in DOM traversal for iframe: {e}")
        
        return dom_content
    
    async def _pass3_dynamic_content(self, page: Page) -> Dict:
        """
        Pass 3: Trigger and extract dynamic content.
        
        Scrolls, clicks, waits for lazy loading.
        """
        dynamic = {
            'lazy_loaded_images': [],
            'lazy_loaded_videos': [],
            'ajax_content': [],
            'intersection_observer_content': []
        }
        
        # Scroll through page to trigger lazy loading
        await self._scroll_through_frame(page)
        
        # Wait for network idle (AJAX/fetch requests)
        await page.wait_for_load_state('networkidle')
        
        # Re-scan for new content
        new_content = await page.content()
        
        dynamic['ajax_content'] = new_content
        
        return dynamic
    
    async def _pass4_validation(self, page: Page, workflow_id: str) -> Dict:
        """
        Pass 4: Validation and quality checks.
        
        Takes screenshots, compares content, validates completeness.
        """
        validation = {
            'screenshot_path': '',
            'content_hash': '',
            'completeness_score': 0
        }
        
        # Take screenshot for validation
        screenshot_path = f'/tmp/layer3_validation_{workflow_id}.png'
        await page.screenshot(path=screenshot_path, full_page=True)
        validation['screenshot_path'] = screenshot_path
        
        # Calculate content hash for comparison
        content = await page.content()
        import hashlib
        validation['content_hash'] = hashlib.sha256(content.encode()).hexdigest()
        
        return validation
```

---

## 🚀 **Implementation Priority**

1. **IMMEDIATE**: Transcript Extraction (use existing TranscriptExtractor)
2. **HIGH**: Video Deduplication (prevent duplicates)
3. **HIGH**: Complete Iframe Crawling (get ALL content)
4. **MEDIUM**: Systematic Process Framework (ensure repeatability)

---

## 📋 **Next Steps**

1. ✅ Create this enhancement plan
2. ⏳ Implement video deduplication
3. ⏳ Integrate TranscriptExtractor
4. ⏳ Add comprehensive iframe crawling
5. ⏳ Create systematic process framework
6. ⏳ Test on video workflows
7. ⏳ Validate completeness

**Do you want me to proceed with implementing these enhancements?**


