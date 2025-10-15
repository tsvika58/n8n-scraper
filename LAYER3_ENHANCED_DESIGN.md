# Enhanced Layer 3: 100% Multimedia & Content Discovery

## 🎯 **Design Philosophy**

**Hybrid Approach:** Playwright visual discovery + comprehensive content extraction
- **Phase 1:** Playwright discovers what's there (videos, text boxes, interactive elements)
- **Phase 2:** Deep extraction of all discovered content
- **Phase 3:** Fallback scanning to catch anything missed

**Goal:** 100% multimedia and content discovery, zero reliance on assumptions

---

## 🔍 **Enhanced Layer 3 Architecture**

### **Phase 1: Visual Discovery with Playwright**

```python
async def _visual_content_discovery(self, page: Page) -> Dict[str, List]:
    """Use Playwright to visually discover all content types"""
    
    discovery = {
        'videos': [],
        'text_boxes': [],
        'interactive_elements': [],
        'images': [],
        'code_blocks': [],
        'tutorial_sections': [],
        'iframe_sources': []
    }
    
    # 1. Discover ALL iframes and their sources
    iframes = await page.query_selector_all('iframe')
    for iframe in iframes:
        src = await iframe.get_attribute('src')
        title = await iframe.get_attribute('title')
        discovery['iframe_sources'].append({
            'src': src,
            'title': title,
            'iframe_element': iframe
        })
    
    # 2. Navigate into each iframe and discover content
    for iframe_info in discovery['iframe_sources']:
        iframe = iframe_info['iframe_element']
        try:
            frame = await iframe.content_frame()
            if frame:
                # Discover videos in iframe
                videos = await self._discover_videos_in_frame(frame)
                discovery['videos'].extend(videos)
                
                # Discover text content areas
                text_areas = await self._discover_text_areas_in_frame(frame)
                discovery['text_boxes'].extend(text_areas)
                
                # Discover interactive elements
                interactive = await self._discover_interactive_elements(frame)
                discovery['interactive_elements'].extend(interactive)
                
                # Discover images
                images = await self._discover_images_in_frame(frame)
                discovery['images'].extend(images)
                
        except Exception as e:
            logger.warning(f"Could not access iframe: {e}")
    
    # 3. Discover content on main page
    main_page_content = await self._discover_main_page_content(page)
    discovery.update(main_page_content)
    
    return discovery

async def _discover_videos_in_frame(self, frame) -> List[Dict]:
    """Discover ALL video-related elements in iframe"""
    videos = []
    
    # 1. Direct video elements
    video_elements = await frame.query_selector_all('video')
    for video in video_elements:
        videos.append({
            'type': 'video_element',
            'src': await video.get_attribute('src'),
            'poster': await video.get_attribute('poster'),
            'element': video
        })
    
    # 2. YouTube/video links
    video_links = await frame.query_selector_all('a[href*="youtube"], a[href*="youtu.be"], a[href*="vimeo"]')
    for link in video_links:
        href = await link.get_attribute('href')
        videos.append({
            'type': 'video_link',
            'url': href,
            'element': link
        })
    
    # 3. Embedded video players
    embeds = await frame.query_selector_all('embed[src*="video"], object[data*="video"]')
    for embed in embeds:
        videos.append({
            'type': 'video_embed',
            'src': await embed.get_attribute('src') or await embed.get_attribute('data'),
            'element': embed
        })
    
    # 4. Video thumbnails with play buttons
    video_thumbs = await frame.query_selector_all('img[alt*="video"], img[src*="video"], [class*="video"], [id*="video"]')
    for thumb in video_thumbs:
        videos.append({
            'type': 'video_thumbnail',
            'src': await thumb.get_attribute('src'),
            'alt': await thumb.get_attribute('alt'),
            'element': thumb
        })
    
    # 5. Elements with video-related classes/IDs
    video_elements_by_class = await frame.query_selector_all('[class*="player"], [class*="tutorial"], [id*="player"]')
    for elem in video_elements_by_class:
        videos.append({
            'type': 'video_container',
            'class': await elem.get_attribute('class'),
            'id': await elem.get_attribute('id'),
            'element': elem
        })
    
    return videos

async def _discover_text_areas_in_frame(self, frame) -> List[Dict]:
    """Discover ALL text content areas in iframe"""
    text_areas = []
    
    # 1. Explicit text content elements
    text_elements = await frame.query_selector_all('p, div, span, h1, h2, h3, h4, h5, h6, li, td, th')
    for elem in text_elements:
        text = await elem.inner_text()
        if text and len(text.strip()) > 10:  # Meaningful text
            text_areas.append({
                'type': 'text_content',
                'tag': await elem.evaluate('el => el.tagName'),
                'text': text,
                'element': elem
            })
    
    # 2. Tutorial/explainer specific elements
    tutorial_elements = await frame.query_selector_all('[class*="tutorial"], [class*="explainer"], [class*="guide"], [class*="step"]')
    for elem in tutorial_elements:
        text = await elem.inner_text()
        if text:
            text_areas.append({
                'type': 'tutorial_content',
                'class': await elem.get_attribute('class'),
                'text': text,
                'element': elem
            })
    
    # 3. Instructions and descriptions
    instruction_elements = await frame.query_selector_all('[class*="instruction"], [class*="description"], [class*="setup"]')
    for elem in instruction_elements:
        text = await elem.inner_text()
        if text:
            text_areas.append({
                'type': 'instruction_content',
                'class': await elem.get_attribute('class'),
                'text': text,
                'element': elem
            })
    
    return text_areas
```

### **Phase 2: Comprehensive Content Extraction**

```python
async def _extract_discovered_content(self, discovery: Dict, page: Page) -> Dict[str, Any]:
    """Extract all discovered content comprehensively"""
    
    extraction_result = {
        'videos': [],
        'tutorial_text': '',
        'instructions': [],
        'code_snippets': [],
        'images': [],
        'interactive_content': [],
        'metadata': {}
    }
    
    # 1. Extract all discovered videos
    for video_info in discovery['videos']:
        video_data = await self._extract_video_content(video_info, page)
        extraction_result['videos'].append(video_data)
    
    # 2. Extract all text content
    all_text = []
    for text_area in discovery['text_boxes']:
        text_content = await self._extract_text_content(text_area)
        all_text.append(text_content)
    
    extraction_result['tutorial_text'] = '\n\n'.join(all_text)
    
    # 3. Extract code snippets
    for interactive in discovery['interactive_elements']:
        if await self._is_code_element(interactive):
            code = await self._extract_code_content(interactive)
            extraction_result['code_snippets'].append(code)
    
    # 4. Extract images
    for image_info in discovery['images']:
        image_data = await self._extract_image_content(image_info)
        extraction_result['images'].append(image_data)
    
    return extraction_result

async def _extract_video_content(self, video_info: Dict, page: Page) -> Dict:
    """Extract comprehensive video content"""
    video_data = {
        'type': video_info['type'],
        'url': None,
        'title': None,
        'description': None,
        'thumbnail': None,
        'transcript_available': False,
        'metadata': {}
    }
    
    element = video_info['element']
    
    if video_info['type'] == 'video_link':
        # Extract from video link
        video_data['url'] = video_info['url']
        video_data['title'] = await element.get_attribute('title')
        video_data['description'] = await element.inner_text()
        
        # Try to find associated thumbnail
        img = await element.query_selector('img')
        if img:
            video_data['thumbnail'] = await img.get_attribute('src')
    
    elif video_info['type'] == 'video_element':
        # Extract from video element
        video_data['url'] = video_info['src']
        video_data['poster'] = video_info['poster']
        
        # Get video metadata
        video_data['duration'] = await element.evaluate('el => el.duration')
        video_data['metadata'] = {
            'width': await element.get_attribute('width'),
            'height': await element.get_attribute('height'),
            'controls': await element.get_attribute('controls')
        }
    
    # Check if transcript is available (for YouTube videos)
    if 'youtube' in str(video_data['url']):
        video_data['transcript_available'] = await self._check_transcript_availability(video_data['url'])
    
    return video_data
```

### **Phase 3: Fallback Comprehensive Scanning**

```python
async def _fallback_comprehensive_scan(self, page: Page) -> Dict[str, Any]:
    """Fallback scan to catch anything missed by visual discovery"""
    
    fallback_result = {
        'additional_videos': [],
        'additional_text': [],
        'additional_images': [],
        'hidden_content': []
    }
    
    # 1. Scan ALL page content for video URLs (regex patterns)
    page_content = await page.content()
    video_patterns = [
        r'https?://(?:www\.)?youtube\.com/watch\?v=([\w-]+)',
        r'https?://(?:www\.)?youtube\.com/embed/([\w-]+)',
        r'https?://youtu\.be/([\w-]+)',
        r'https?://vimeo\.com/(\d+)',
        r'https?://player\.vimeo\.com/video/(\d+)'
    ]
    
    for pattern in video_patterns:
        matches = re.findall(pattern, page_content)
        for match in matches:
            fallback_result['additional_videos'].append({
                'type': 'regex_discovered',
                'pattern': pattern,
                'url': match,
                'source': 'page_content_scan'
            })
    
    # 2. Scan for hidden/dynamic content
    try:
        # Look for content loaded via JavaScript
        dynamic_content = await page.evaluate('''
            () => {
                const videos = [];
                const text = [];
                
                // Find all elements that might contain videos
                document.querySelectorAll('*').forEach(el => {
                    if (el.innerHTML.includes('youtube') || el.innerHTML.includes('youtu.be')) {
                        videos.push(el.outerHTML);
                    }
                    
                    if (el.className && (el.className.includes('tutorial') || el.className.includes('guide'))) {
                        text.push(el.innerText);
                    }
                });
                
                return { videos, text };
            }
        ''')
        
        fallback_result['hidden_content'] = dynamic_content
        
    except Exception as e:
        logger.warning(f"Could not scan dynamic content: {e}")
    
    return fallback_result
```

---

## 🚀 **Enhanced Layer 3 Implementation**

### **Main Extraction Method**

```python
async def extract_enhanced(self, workflow_id: str, url: str) -> Dict[str, Any]:
    """Enhanced Layer 3 extraction with 100% content discovery"""
    
    start_time = time.time()
    
    try:
        page = await self.browser.new_page()
        await page.goto(url, timeout=self.timeout)
        await page.wait_for_load_state('networkidle', timeout=self.timeout)
        await page.wait_for_timeout(3000)  # Wait for dynamic content
        
        # Phase 1: Visual discovery
        logger.info(f"Phase 1: Visual content discovery for {workflow_id}")
        discovery = await self._visual_content_discovery(page)
        
        # Phase 2: Comprehensive extraction
        logger.info(f"Phase 2: Comprehensive content extraction for {workflow_id}")
        extraction = await self._extract_discovered_content(discovery, page)
        
        # Phase 3: Fallback scanning
        logger.info(f"Phase 3: Fallback comprehensive scan for {workflow_id}")
        fallback = await self._fallback_comprehensive_scan(page)
        
        # Combine all results
        result = {
            'success': True,
            'workflow_id': workflow_id,
            'extraction_time': time.time() - start_time,
            'data': {
                # Videos (all sources)
                'videos': extraction['videos'] + fallback['additional_videos'],
                'video_count': len(extraction['videos']) + len(fallback['additional_videos']),
                
                # Text content (all sources)
                'tutorial_text': extraction['tutorial_text'],
                'additional_text': fallback['additional_text'],
                'total_text_length': len(extraction['tutorial_text']),
                
                # Other content
                'code_snippets': extraction['code_snippets'],
                'images': extraction['images'] + fallback['additional_images'],
                'instructions': extraction['instructions'],
                
                # Metadata
                'discovery_metadata': {
                    'iframes_found': len(discovery['iframe_sources']),
                    'videos_discovered': len(discovery['videos']),
                    'text_areas_found': len(discovery['text_boxes']),
                    'fallback_videos': len(fallback['additional_videos'])
                }
            },
            'metadata': {
                'extractor_version': '3.0.0-enhanced',
                'extraction_method': 'visual_discovery + comprehensive_extraction + fallback_scan',
                'content_sources': ['main_page', 'iframes', 'dynamic_content', 'regex_scan']
            }
        }
        
        # Validate extraction quality
        quality_score = self._calculate_extraction_quality(result)
        result['quality_score'] = quality_score
        
        logger.success(f"Enhanced Layer 3 extraction completed for {workflow_id}: "
                      f"{result['data']['video_count']} videos, "
                      f"{result['data']['total_text_length']} chars, "
                      f"Quality: {quality_score}/100")
        
        return result
        
    except Exception as e:
        logger.error(f"Enhanced Layer 3 extraction failed for {workflow_id}: {str(e)}")
        return {
            'success': False,
            'workflow_id': workflow_id,
            'extraction_time': time.time() - start_time,
            'error': str(e)
        }
    finally:
        await page.close()

def _calculate_extraction_quality(self, result: Dict) -> int:
    """Calculate extraction quality score (0-100)"""
    score = 0
    
    # Video discovery quality (40 points)
    video_count = result['data']['video_count']
    if video_count > 0:
        score += 40  # Found videos
    if video_count > 1:
        score += 10  # Found multiple videos
    
    # Text content quality (30 points)
    text_length = result['data']['total_text_length']
    if text_length > 1000:
        score += 30
    elif text_length > 500:
        score += 20
    elif text_length > 100:
        score += 10
    
    # Content diversity (20 points)
    if result['data']['code_snippets']:
        score += 10
    if result['data']['images']:
        score += 10
    
    # Discovery completeness (10 points)
    metadata = result['data']['discovery_metadata']
    if metadata['iframes_found'] > 0:
        score += 5
    if metadata['fallback_videos'] > 0:
        score += 5
    
    return min(score, 100)
```

---

## 🎯 **Key Enhancements**

### **1. Visual Discovery First**
- **Playwright discovers what's there** before extraction
- **No assumptions** - finds all content types visually
- **Comprehensive iframe navigation** - checks every iframe

### **2. Multi-Source Video Detection**
- Direct video elements (`<video>`)
- YouTube/video links (`<a href="...">`)
- Embedded players (`<embed>`, `<object>`)
- Video thumbnails with play buttons
- Elements with video-related classes/IDs
- Regex scanning of page content
- JavaScript-loaded dynamic content

### **3. Comprehensive Text Extraction**
- All text elements in iframes
- Tutorial/explainer specific elements
- Instruction and setup content
- Dynamic content loaded via JavaScript
- Fallback regex scanning

### **4. Quality Assurance**
- **Quality scoring** (0-100) based on content discovery
- **Multiple discovery methods** to ensure nothing is missed
- **Fallback scanning** for edge cases
- **Comprehensive metadata** tracking

### **5. Zero Reliance on Assumptions**
- **Visual discovery** finds what's actually there
- **Multiple extraction methods** for each content type
- **Fallback scanning** catches anything missed
- **Comprehensive logging** of discovery process

---

## 📊 **Expected Results**

### **Video Discovery**
- **Current Layer 3:** ~50% of videos found
- **Enhanced Layer 3:** ~95-100% of videos found
- **Multiple videos per workflow:** Properly detected
- **All video types:** YouTube, Vimeo, embedded, thumbnails

### **Content Extraction**
- **Tutorial text:** All text content from iframes
- **Instructions:** Step-by-step guides
- **Code snippets:** All code examples
- **Images:** All tutorial images
- **Metadata:** Comprehensive content metadata

### **Quality Metrics**
- **Success rate:** 95%+ (vs current 90%)
- **Content completeness:** 100% (vs current ~50%)
- **Video discovery rate:** 95%+ (vs current 50%)
- **Average quality score:** 85+ (vs current ~60)

---

## 🚀 **Implementation Plan**

### **Phase 1: Create Enhanced Layer 3 (2-3 hours)**
1. Implement visual discovery methods
2. Add comprehensive content extraction
3. Create fallback scanning
4. Add quality scoring

### **Phase 2: Test Enhanced Layer 3 (1 hour)**
1. Test on 10 video workflows
2. Compare with current Layer 3
3. Validate 100% content discovery
4. Measure performance

### **Phase 3: Production Deployment (1 hour)**
1. Create production scraper
2. Add resume capability
3. Integrate with existing pipeline
4. Start rollout

**Total:** ~4-5 hours for 100% multimedia discovery!

---

**What do you think of this approach? Should I proceed with implementing the enhanced Layer 3 with visual discovery + comprehensive extraction + fallback scanning?**


