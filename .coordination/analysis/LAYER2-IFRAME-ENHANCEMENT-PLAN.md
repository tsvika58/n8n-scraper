# 🚀 LAYER 2 IFRAME ENHANCEMENT PLAN

**Date:** October 13, 2025  
**Objective:** Add iframe parsing to Layer 2 for complete workflow data extraction  
**Priority:** HIGH (User confirmed iframe contains critical data)

---

## 📊 WHAT WE FOUND IN THE IFRAME

### **Confirmed Data Sources:**

1. **✅ Workflow Node Names** (14 nodes found)
   - "When chat message received"
   - "Simple Memory"
   - "OpenAI Chat Model"
   - "SerpAPI"
   - "AI Agent"

2. **✅ Node Technical Data** (via data attributes)
   ```html
   data-node-name="When chat message received"
   data-node-type="@n8n/n8n-nodes-langchain.chatTrigger"
   data-id="ef4c6982-f746-4d48-944b-449f8bdbb69f"
   data-test-id="canvas-node"
   ```

3. **✅ Node Connections** (via data attributes)
   ```html
   data-handleid="outputs/main/0"
   data-connection-type="main"
   data-index="0"
   ```

4. **✅ Visual Layout** (via CSS classes and positioning)
   - Node positions (X/Y coordinates)
   - Canvas zoom/pan state
   - Node rendering type

5. **✅ Node Icons** (2 images found)
   - OpenAI icon: `/icons/@n8n/n8n-nodes-langchain/dist/nodes/llms/LMChatOpenAi/openAiLight.svg`
   - SerpAPI icon: `/icons/@n8n/n8n-nodes-langchain/dist/nodes/tools/ToolSerpApi/serpApi.svg`

6. **✅ Explanatory Text** (2 substantial text blocks)
   - "I can answer most questions about building workflows in n8n..."
   - "For specific tasks, you'll see the Ask Assistant button in the UI..."

7. **✅ Input Fields** (1 text input)
   - Placeholder: "Enter your response..."

---

## 🎯 ENHANCEMENT STRATEGY

### **PHASE 1: Basic Iframe Parsing** (2-3 hours)

**Goal:** Extract node names, types, and IDs from iframe

**Implementation:**
```python
class EnhancedLayer2Extractor(WorkflowJSONExtractor):
    """Enhanced Layer 2 with iframe parsing."""
    
    async def extract_with_iframe(self, workflow_id: str, workflow_url: str):
        """Extract from both API and iframe."""
        
        # 1. Get API data (existing functionality)
        api_data = await self.extract(workflow_id)
        
        # 2. Get iframe data (new functionality)
        iframe_data = await self._extract_from_iframe(workflow_url)
        
        # 3. Merge data
        merged_data = self._merge_api_and_iframe(api_data, iframe_data)
        
        return merged_data
    
    async def _extract_from_iframe(self, workflow_url: str):
        """Extract data from iframe."""
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            try:
                # Navigate to workflow page
                await page.goto(workflow_url, wait_until='networkidle')
                await asyncio.sleep(3)  # Wait for iframe to load
                
                # Find workflow iframe
                frames = page.frames
                workflow_frame = None
                for frame in frames:
                    if 'n8n-preview' in frame.url or 'demo' in frame.url:
                        workflow_frame = frame
                        break
                
                if not workflow_frame:
                    return {'success': False, 'error': 'Iframe not found'}
                
                # Extract node data
                nodes = await workflow_frame.locator('[data-node-name]').all()
                
                node_data = []
                for node in nodes:
                    node_info = {
                        'name': await node.get_attribute('data-node-name'),
                        'type': await node.get_attribute('data-node-type'),
                        'id': await node.get_attribute('data-id'),
                        'test_id': await node.get_attribute('data-test-id')
                    }
                    node_data.append(node_info)
                
                # Extract text content
                text_content = await workflow_frame.evaluate('() => document.body.innerText')
                
                # Extract images/icons
                images = await workflow_frame.locator('img').all()
                image_data = []
                for img in images:
                    image_data.append({
                        'src': await img.get_attribute('src'),
                        'alt': await img.get_attribute('alt')
                    })
                
                return {
                    'success': True,
                    'nodes': node_data,
                    'text_content': text_content,
                    'images': image_data,
                    'node_count': len(node_data)
                }
                
            finally:
                await browser.close()
```

**Data Captured:**
- ✅ Node names
- ✅ Node types
- ✅ Node IDs
- ✅ Text content
- ✅ Node icons

**Value:** HIGH - Provides node metadata and explanatory text
**Effort:** 2-3 hours

---

### **PHASE 2: Visual Layout Extraction** (2-3 hours)

**Goal:** Extract node positions and canvas state

**Implementation:**
```python
async def _extract_visual_layout(self, workflow_frame):
    """Extract visual layout data from iframe."""
    
    # Get node positions
    nodes = await workflow_frame.locator('[data-node-name]').all()
    
    positions = []
    for node in nodes:
        # Get bounding box (position and size)
        box = await node.bounding_box()
        
        # Get CSS transform (for exact positioning)
        transform = await node.evaluate('''
            el => {
                const style = window.getComputedStyle(el);
                return {
                    transform: style.transform,
                    left: style.left,
                    top: style.top
                };
            }
        ''')
        
        positions.append({
            'node_name': await node.get_attribute('data-node-name'),
            'x': box['x'] if box else None,
            'y': box['y'] if box else None,
            'width': box['width'] if box else None,
            'height': box['height'] if box else None,
            'transform': transform
        })
    
    # Get canvas state
    canvas_state = await workflow_frame.evaluate('''
        () => {
            // Try to find canvas/viewport element
            const viewport = document.querySelector('.vue-flow__viewport, [class*="viewport"]');
            if (viewport) {
                const style = window.getComputedStyle(viewport);
                return {
                    transform: style.transform,
                    zoom: style.zoom || '1',
                    width: viewport.clientWidth,
                    height: viewport.clientHeight
                };
            }
            return null;
        }
    ''')
    
    return {
        'node_positions': positions,
        'canvas_state': canvas_state
    }
```

**Data Captured:**
- ✅ Node X/Y positions
- ✅ Node width/height
- ✅ Canvas zoom level
- ✅ Canvas pan offset

**Value:** MEDIUM - Enables exact visual recreation
**Effort:** 2-3 hours

---

### **PHASE 3: Explanatory Content Extraction** (1-2 hours)

**Goal:** Extract all explanatory text, descriptions, and help content

**Implementation:**
```python
async def _extract_explanatory_content(self, workflow_frame):
    """Extract explanatory content from iframe."""
    
    # Get all substantial text blocks
    text_elements = await workflow_frame.locator('p, span, div[class*="description"], div[class*="text"], div[class*="help"]').all()
    
    explanatory_texts = []
    for el in text_elements:
        text = await el.text_content()
        if text and len(text.strip()) > 30:  # Substantial text only
            explanatory_texts.append({
                'text': text.strip(),
                'length': len(text),
                'classes': await el.get_attribute('class')
            })
    
    # Get input field placeholders (often contain instructions)
    inputs = await workflow_frame.locator('input, textarea').all()
    input_hints = []
    for inp in inputs:
        placeholder = await inp.get_attribute('placeholder')
        if placeholder:
            input_hints.append(placeholder)
    
    return {
        'explanatory_texts': explanatory_texts,
        'input_hints': input_hints,
        'total_text_blocks': len(explanatory_texts)
    }
```

**Data Captured:**
- ✅ Explanatory text blocks
- ✅ Help text
- ✅ Input placeholders
- ✅ Instructions

**Value:** HIGH - Provides context and usage instructions
**Effort:** 1-2 hours

---

### **PHASE 4: Video/Media Extraction** (1 hour)

**Goal:** Extract video URLs and media content

**Implementation:**
```python
async def _extract_media_content(self, workflow_frame):
    """Extract videos and media from iframe."""
    
    # Find videos
    videos = await workflow_frame.locator('video, iframe[src*="youtube"], iframe[src*="vimeo"]').all()
    
    video_data = []
    for video in videos:
        tag = await video.evaluate('el => el.tagName')
        src = await video.get_attribute('src')
        
        video_data.append({
            'type': tag,
            'source': src,
            'platform': 'youtube' if 'youtube' in src else 'vimeo' if 'vimeo' in src else 'direct'
        })
    
    # Find images (screenshots, diagrams, etc.)
    images = await workflow_frame.locator('img').all()
    
    image_data = []
    for img in images:
        src = await img.get_attribute('src')
        alt = await img.get_attribute('alt')
        
        # Skip node icons, get only content images
        if src and not src.startswith('/icons/'):
            image_data.append({
                'source': src,
                'alt_text': alt,
                'type': 'screenshot' if 'screenshot' in src.lower() else 'diagram' if 'diagram' in src.lower() else 'image'
            })
    
    return {
        'videos': video_data,
        'images': image_data,
        'video_count': len(video_data),
        'image_count': len(image_data)
    }
```

**Data Captured:**
- ✅ Video URLs (YouTube, Vimeo, direct)
- ✅ Screenshots
- ✅ Diagrams
- ✅ Explanatory images

**Value:** MEDIUM - Provides visual documentation
**Effort:** 1 hour

---

## 📊 COMPLETE IMPLEMENTATION

### **Full Enhanced Layer 2 Extractor:**

```python
class EnhancedLayer2Extractor(WorkflowJSONExtractor):
    """Enhanced Layer 2 with API + Iframe extraction."""
    
    def __init__(self):
        super().__init__()
        self.browser = None
        self.context = None
    
    async def __aenter__(self):
        """Initialize browser for iframe extraction."""
        from playwright.async_api import async_playwright
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=True)
        self.context = await self.browser.new_context()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Cleanup browser."""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
    
    async def extract_complete(self, workflow_id: str, workflow_url: str):
        """Extract complete workflow data from API + Iframe."""
        
        start_time = datetime.now()
        
        # 1. Extract from API (existing functionality)
        api_data = await self.extract(workflow_id)
        
        # 2. Extract from iframe (new functionality)
        iframe_data = await self._extract_from_iframe(workflow_url)
        
        # 3. Merge data
        merged_data = {
            'workflow_id': workflow_id,
            'url': workflow_url,
            'extraction_time': (datetime.now() - start_time).total_seconds(),
            'sources': {
                'api': api_data,
                'iframe': iframe_data
            },
            'merged': self._merge_sources(api_data, iframe_data),
            'completeness': {
                'api_only': self._calculate_completeness(api_data),
                'with_iframe': self._calculate_completeness(iframe_data)
            }
        }
        
        return merged_data
    
    async def _extract_from_iframe(self, workflow_url: str):
        """Extract all data from iframe."""
        
        page = await self.context.new_page()
        
        try:
            # Navigate
            await page.goto(workflow_url, wait_until='networkidle', timeout=30000)
            await asyncio.sleep(3)
            
            # Find iframe
            frames = page.frames
            workflow_frame = None
            for frame in frames:
                if 'n8n-preview' in frame.url or 'demo' in frame.url:
                    workflow_frame = frame
                    break
            
            if not workflow_frame:
                return {'success': False, 'error': 'Iframe not found'}
            
            # Extract all data
            node_data = await self._extract_node_data(workflow_frame)
            visual_layout = await self._extract_visual_layout(workflow_frame)
            explanatory_content = await self._extract_explanatory_content(workflow_frame)
            media_content = await self._extract_media_content(workflow_frame)
            
            return {
                'success': True,
                'source': 'iframe',
                'nodes': node_data,
                'visual_layout': visual_layout,
                'explanatory_content': explanatory_content,
                'media_content': media_content,
                'completeness': 100
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
        
        finally:
            await page.close()
    
    def _merge_sources(self, api_data, iframe_data):
        """Merge API and iframe data."""
        
        if not api_data['success'] or not iframe_data['success']:
            # Return whichever succeeded
            return api_data if api_data['success'] else iframe_data
        
        # Merge node data
        api_nodes = api_data['data']['workflow']['nodes']
        iframe_nodes = iframe_data['nodes']
        
        # Enrich API nodes with iframe data
        for api_node in api_nodes:
            # Find matching iframe node
            iframe_node = next((n for n in iframe_nodes if n['name'] == api_node['name']), None)
            if iframe_node:
                api_node['iframe_data'] = iframe_node
        
        # Create merged structure
        merged = {
            'workflow_id': api_data['workflow_id'],
            'workflow': api_data['data']['workflow'],
            'metadata': api_data['data'],
            'visual_layout': iframe_data.get('visual_layout', {}),
            'explanatory_content': iframe_data.get('explanatory_content', {}),
            'media_content': iframe_data.get('media_content', {}),
            'sources_used': ['api', 'iframe'],
            'completeness': 100
        }
        
        return merged
```

---

## 🎯 IMPLEMENTATION TIMELINE

### **Total Effort: 6-9 hours**

**Phase 1 (Basic Iframe Parsing):** 2-3 hours
  - Extract node names, types, IDs
  - Extract text content
  - Extract node icons

**Phase 2 (Visual Layout):** 2-3 hours
  - Extract node positions
  - Extract canvas state
  - Calculate layout metrics

**Phase 3 (Explanatory Content):** 1-2 hours
  - Extract text blocks
  - Extract help content
  - Extract input hints

**Phase 4 (Media Content):** 1 hour
  - Extract videos
  - Extract images
  - Categorize media types

---

## 📋 TESTING STRATEGY

### **Test on 5 Diverse Workflows:**

1. **Workflow 1954** (AI Agent Chat) - Complex LangChain workflow
2. **Workflow 2462** (Telegram AI Assistant) - Voice + Text
3. **Workflow 2134** (Email Scraper) - Simple utility workflow
4. **Workflow 9343** (App Store Monitor) - Scheduled workflow
5. **Workflow 3456** (Discord Chatbot) - Integration workflow

### **Validation Criteria:**

- ✅ All nodes extracted from iframe
- ✅ Node names match API data
- ✅ Visual positions captured
- ✅ Explanatory text extracted
- ✅ Media content identified
- ✅ 100% completeness achieved

---

## 🚀 RECOMMENDATION

**Proceed with Full Implementation (All 4 Phases)**

**Rationale:**
1. ✅ User confirmed iframe contains critical data
2. ✅ Inspection shows rich content (nodes, text, media)
3. ✅ 6-9 hours is reasonable for 100% completeness
4. ✅ Enables complete workflow recreation
5. ✅ Provides explanatory content for documentation

**Next Steps:**
1. Implement Phase 1 (Basic Iframe Parsing) - 2-3 hours
2. Test on sample workflows
3. Implement Phase 2 (Visual Layout) - 2-3 hours
4. Implement Phase 3 (Explanatory Content) - 1-2 hours
5. Implement Phase 4 (Media Content) - 1 hour
6. Validate on 5 diverse workflows
7. Deploy in parallel with Layer 1

---

**Ready to start implementation?**




