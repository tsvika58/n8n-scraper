# API Documentation v1.0.0
**Document Version:** 1.0.0  
**Date:** January 17, 2025  
**Project:** n8n-scraper-v1  
**Author:** Technical Documentation Team  
**Status:** Reference Documentation

---

## 📋 VERSION CONTROL

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0.0 | 2025-01-17 | Initial API documentation | Tech Docs Team |

---

## 🎯 DOCUMENT PURPOSE

Complete API reference for all classes, methods, and utilities in the n8n workflow scraper. This document serves as the authoritative reference for developers working with the codebase.

---

## 📦 CORE CLASSES

### WorkflowScraperOrchestrator

**Location:** `src/orchestrator/scraper.py`

Main orchestrator class that coordinates the three-phase extraction process.

```python
class WorkflowScraperOrchestrator:
    """
    Main orchestrator for workflow scraping.
    
    Attributes:
        config (Config): Configuration object
        phase1_extractor (PageContentExtractor): Phase 1 extractor
        phase2_extractor (WorkflowIframeExtractor): Phase 2 extractor
        phase3_extractor (ExplainerIframeExtractor): Phase 3 extractor
        VERSION (str): Scraper version
    """
```

#### Methods

##### `__init__(config: Config)`

Initialize the orchestrator with configuration.

**Parameters:**
- `config` (Config): Configuration object

**Example:**
```python
from src.config import Config
from src.orchestrator.scraper import WorkflowScraperOrchestrator

config = Config.from_defaults()
orchestrator = WorkflowScraperOrchestrator(config)
```

##### `async scrape_workflow(url: str, progress_callback: Optional[Callable] = None) -> Dict`

Scrape a single workflow through all three phases.

**Parameters:**
- `url` (str): Full workflow URL (e.g., "https://n8n.io/workflows/2462-...")
- `progress_callback` (Optional[Callable]): Callback function called after each phase

**Returns:**
- `Dict`: Complete workflow data with all three layers

**Raises:**
- `ExtractionError`: If extraction fails
- `NetworkError`: If network request fails
- `ValidationError`: If validation fails

**Example:**
```python
url = "https://n8n.io/workflows/2462-angie-personal-ai-assistant/"

def on_progress(phase):
    print(f"Completed {phase}")

result = await orchestrator.scrape_workflow(url, progress_callback=on_progress)

print(f"Extracted {len(result['workflow']['workflow_json']['nodes'])} nodes")
```

##### `scrape_batch(urls: List[str], concurrency: int = 2, progress: bool = True) -> List[Dict]`

Scrape multiple workflows with controlled concurrency.

**Parameters:**
- `urls` (List[str]): List of workflow URLs
- `concurrency` (int): Number of parallel scrapers (default: 2)
- `progress` (bool): Show progress bar (default: True)

**Returns:**
- `List[Dict]`: List of scraped workflow data

**Example:**
```python
urls = [
    "https://n8n.io/workflows/2462-angie...",
    "https://n8n.io/workflows/8237-personal-life-manager...",
]

results = orchestrator.scrape_batch(urls, concurrency=2)

successful = sum(1 for r in results if r.get('success'))
print(f"Successfully scraped {successful}/{len(urls)} workflows")
```

##### `fetch_sitemap_urls() -> List[str]`

Fetch all workflow URLs from n8n.io sitemap.

**Returns:**
- `List[str]`: List of workflow URLs from sitemap

**Example:**
```python
urls = orchestrator.fetch_sitemap_urls()
print(f"Found {len(urls)} workflows in sitemap")
```

##### `test_connection() -> bool`

Test connection to n8n.io.

**Returns:**
- `bool`: True if connection successful, False otherwise

**Example:**
```python
if orchestrator.test_connection():
    print("Connection OK")
else:
    print("Connection failed")
```

##### `extract_workflow_id(url: str) -> str`

Extract workflow ID from URL.

**Parameters:**
- `url` (str): Workflow URL

**Returns:**
- `str`: Workflow ID (e.g., "2462")

**Example:**
```python
url = "https://n8n.io/workflows/2462-angie-personal-ai-assistant/"
workflow_id = orchestrator.extract_workflow_id(url)
# Returns: "2462"
```

---

### PageContentExtractor

**Location:** `src/extractors/phase1_page.py`

Extracts content from the main workflow page (Layer 1).

```python
class PageContentExtractor:
    """
    Phase 1: Extract page-level content.
    
    Extracts metadata, categories, tags, and setup instructions
    from the main workflow page.
    """
```

#### Methods

##### `async extract(page: Page) -> Dict`

Extract all page content.

**Parameters:**
- `page` (playwright.Page): Playwright page object

**Returns:**
- `Dict`: Page content including:
  - `title` (str): Workflow title
  - `description` (str): Workflow description
  - `categories` (List[Dict]): Category tags
  - `node_tags` (List[Dict]): Node/integration tags
  - `setup_instructions` (Dict): Setup requirements
  - `author` (str): Author name
  - `created_at` (str): Creation date
  - `metadata` (Dict): Additional metadata

**Example:**
```python
from playwright.async_api import async_playwright

async with async_playwright() as p:
    browser = await p.chromium.launch()
    page = await browser.new_page()
    await page.goto(url)
    
    extractor = PageContentExtractor(config)
    page_content = await extractor.extract(page)
    
    print(f"Title: {page_content['title']}")
    print(f"Categories: {page_content['categories']}")
```

##### `async extract_categories(page: Page) -> List[Dict]`

Extract category badges.

**Parameters:**
- `page` (playwright.Page): Playwright page object

**Returns:**
- `List[Dict]`: List of categories with structure:
```python
{
    "id": "personal-productivity",
    "name": "Personal Productivity",
    "type": "primary"  # or "secondary"
}
```

##### `async extract_node_tags(page: Page) -> List[Dict]`

Extract node/integration tags.

**Parameters:**
- `page` (playwright.Page): Playwright page object

**Returns:**
- `List[Dict]`: List of node tags with structure:
```python
{
    "id": "openai",
    "display_name": "OpenAI",
    "node_type": "n8n-nodes-base.openai",
    "icon_url": "https://...",
    "is_trigger": False
}
```

##### `async extract_setup_modal(page: Page) -> Optional[Dict]`

Extract setup instructions from modal.

**Parameters:**
- `page` (playwright.Page): Playwright page object

**Returns:**
- `Optional[Dict]`: Setup instructions or None if modal not present

**Structure:**
```python
{
    "requirements_text": "You need 1x Telegram, 1x OpenAI...",
    "services_needed": [
        {"service": "Telegram", "count": 1},
        {"service": "OpenAI", "count": 1}
    ],
    "setup_steps": [
        {
            "step_number": 1,
            "service": "Telegram",
            "instructions": "The credential you select...",
            "nodes_affected": ["Telegram Trigger", "Send Message"],
            "button_text": "Create new Telegram credential"
        }
    ]
}
```

---

### WorkflowIframeExtractor

**Location:** `src/extractors/phase2_workflow.py`

Extracts workflow data from the interactive n8n iframe (Layer 2).

```python
class WorkflowIframeExtractor:
    """
    Phase 2: Extract workflow from iframe.
    
    Extracts complete workflow JSON including all nodes,
    connections, and parameter configurations.
    """
```

#### Methods

##### `async extract(page: Page) -> Dict`

Extract complete workflow data from iframe.

**Parameters:**
- `page` (playwright.Page): Playwright page object

**Returns:**
- `Dict`: Workflow data including:
  - `iframe_url` (str): URL of the iframe
  - `workflow_json` (Dict): Complete n8n workflow JSON
  - `node_configurations` (List[Dict]): Detailed node configs
  - `canvas_layout` (Dict): Visual layout information
  - `screenshot_path` (str): Path to workflow screenshot

**Example:**
```python
extractor = WorkflowIframeExtractor(config)
workflow_data = await extractor.extract(page)

# Access workflow JSON
workflow_json = workflow_data['workflow_json']
nodes = workflow_json['nodes']

print(f"Workflow has {len(nodes)} nodes")

# Access specific node parameters
for node in nodes:
    print(f"Node: {node['name']}")
    print(f"  Type: {node['type']}")
    print(f"  Parameters: {node['parameters']}")
```

##### `async extract_workflow_json(iframe: Frame) -> Dict`

Extract the n8n workflow JSON from iframe.

**Parameters:**
- `iframe` (playwright.Frame): Iframe frame object

**Returns:**
- `Dict`: Complete n8n workflow JSON with structure:
```python
{
    "name": "Workflow Name",
    "nodes": [
        {
            "id": "node-123",
            "name": "Telegram Trigger",
            "type": "n8n-nodes-base.telegramTrigger",
            "typeVersion": 1,
            "position": [100, 200],
            "parameters": {
                "updates": ["message"],
                "additionalFields": {}
            },
            "credentials": {
                "telegramApi": {"id": "1", "name": "Telegram Bot"}
            },
            "notes": "Triggers when message received"
        }
    ],
    "connections": {
        "Telegram Trigger": {
            "main": [
                [
                    {
                        "node": "Process Message",
                        "type": "main",
                        "index": 0
                    }
                ]
            ]
        }
    },
    "settings": {
        "executionOrder": "v1"
    }
}
```

##### `async extract_node_configurations(iframe: Frame, workflow_json: Dict) -> List[Dict]`

Extract detailed node configurations with parameter metadata.

**Parameters:**
- `iframe` (playwright.Frame): Iframe frame object
- `workflow_json` (Dict): Base workflow JSON

**Returns:**
- `List[Dict]`: List of detailed node configurations:
```python
{
    "node_id": "node-123",
    "node_name": "Send Message",
    "node_type": "n8n-nodes-base.telegram",
    "operation": "sendMessage",
    "parameters": [
        {
            "name": "chatId",
            "display_name": "Chat ID",
            "value": "={{ $json.userId }}",
            "value_type": "expression",
            "is_expression": True,
            "expression_code": "={{ $json.userId }}",
            "description": "Telegram chat ID",
            "required": True,
            "example_values": ["123456", "={{ $json.id }}"]
        }
    ],
    "credentials_used": ["telegramApi"],
    "purpose": "Sends message to Telegram user",
    "input_example": {"userId": 12345, "message": "Hello"},
    "output_example": {"message_id": 789, "success": True}
}
```

##### `async take_workflow_screenshot(iframe: Frame) -> Optional[str]`

Take screenshot of workflow canvas.

**Parameters:**
- `iframe` (playwright.Frame): Iframe frame object

**Returns:**
- `Optional[str]`: Path to saved screenshot or None

---

### ExplainerIframeExtractor

**Location:** `src/extractors/phase3_explainer.py`

Extracts tutorial content, images, and videos (Layer 3).

```python
class ExplainerIframeExtractor:
    """
    Phase 3: Extract explainer content.
    
    Extracts tutorial text, images, videos, and transcripts
    from the explainer section/iframe.
    """
```

#### Methods

##### `async extract(page: Page) -> Dict`

Extract all explainer content.

**Parameters:**
- `page` (playwright.Page): Playwright page object

**Returns:**
- `Dict`: Explainer content including:
  - `sections` (List[Dict]): Text sections
  - `images` (List[Dict]): Images with OCR text
  - `videos` (List[Dict]): Videos with transcripts
  - `extracted_text` (Dict): Aggregated text from all sources

**Example:**
```python
extractor = ExplainerIframeExtractor(config)
explainer_data = await extractor.extract(page)

# Access sections
for section in explainer_data['sections']:
    print(f"Section: {section['heading']}")
    print(f"Content: {section['content'][:100]}...")

# Access images
for image in explainer_data['images']:
    print(f"Image: {image['local_path']}")
    if image.get('ocr_text'):
        print(f"  OCR: {image['ocr_text']['full_text'][:50]}...")

# Access videos
for video in explainer_data['videos']:
    print(f"Video: {video['title']}")
    if video.get('transcript'):
        print(f"  Transcript: {video['transcript']['full_text'][:50]}...")
```

##### `async extract_text_sections(frame: Union[Page, Frame]) -> List[Dict]`

Extract organized text sections.

**Returns:**
- `List[Dict]`: Text sections with structure:
```python
{
    "section_type": "overview",  # or "how_it_works", "setup", etc.
    "heading": "What This Workflow Does",
    "content": "Full text content...",
    "subsections": [],
    "lists": [["Item 1", "Item 2"]],
    "code_snippets": [
        {
            "code": "const x = 1;",
            "language": "javascript"
        }
    ]
}
```

##### `async extract_images(frame: Union[Page, Frame]) -> List[Dict]`

Extract and download all images.

**Returns:**
- `List[Dict]`: Images with structure:
```python
{
    "image_id": "explainer_0",
    "source_url": "https://...",
    "local_path": "./data/images/2462_0.png",
    "alt_text": "Workflow diagram",
    "context_type": "workflow_diagram",
    "ocr_text": {
        "full_text": "Extracted text...",
        "confidence_score": 0.95,
        "detected_elements": [...]
    }
}
```

##### `async extract_videos(frame: Union[Page, Frame]) -> List[Dict]`

Extract video metadata and transcripts.

**Returns:**
- `List[Dict]`: Videos with structure:
```python
{
    "video_id": "2462_video_0",
    "platform": "youtube",
    "platform_video_id": "xyz123",
    "embed_url": "https://youtube.com/embed/xyz123",
    "watch_url": "https://youtube.com/watch?v=xyz123",
    "title": "Setting up Telegram Bot",
    "description": "Tutorial video...",
    "duration": 600,
    "transcript": {
        "full_text": "Complete transcript...",
        "segments": [
            {
                "start_time": 0,
                "end_time": 15,
                "text": "First, open Telegram..."
            }
        ],
        "source": "youtube_api"
    },
    "topics_covered": ["bot creation", "API setup"],
    "nodes_demonstrated": ["Telegram Trigger", "OpenAI"]
}
```

---

## 🔧 UTILITY CLASSES

### ImageProcessor

**Location:** `src/processors/image_processor.py`

Handles image downloading and OCR processing.

```python
class ImageProcessor:
    """Process images: download and OCR"""
```

#### Methods

##### `async download_image(url: str, output_path: Path) -> bool`

Download image from URL.

**Parameters:**
- `url` (str): Image URL
- `output_path` (Path): Where to save image

**Returns:**
- `bool`: True if successful

##### `perform_ocr(image_path: Path) -> Dict`

Perform OCR on image using Tesseract.

**Parameters:**
- `image_path` (Path): Path to image file

**Returns:**
- `Dict`: OCR results:
```python
{
    "full_text": "Extracted text...",
    "detected_elements": [
        {
            "element_type": "paragraph",
            "text": "Line of text",
            "confidence": 0.95,
            "bounding_box": {"x": 10, "y": 20, "width": 100, "height": 30}
        }
    ],
    "confidence_score": 0.92,
    "language": "eng",
    "ocr_engine": "tesseract"
}
```

---

### VideoProcessor

**Location:** `src/processors/video_processor.py`

Handles video transcript extraction.

```python
class VideoProcessor:
    """Process videos: extract transcripts"""
```

#### Methods

##### `async get_youtube_transcript(video_id: str) -> Optional[Dict]`

Get transcript from YouTube video.

**Parameters:**
- `video_id` (str): YouTube video ID

**Returns:**
- `Optional[Dict]`: Transcript data or None

---

### WorkflowValidator

**Location:** `src/validators/workflow_validator.py`

Validates scraped workflow data.

```python
class WorkflowValidator:
    """Validate workflow data completeness and quality"""
```

#### Methods

##### `validate(workflow_data: Dict) -> Dict`

Validate complete workflow data.

**Parameters:**
- `workflow_data` (Dict): Complete workflow data

**Returns:**
- `Dict`: Validation results:
```python
{
    "valid": True,
    "completeness_score": 0.95,
    "has_workflow_json": True,
    "has_all_parameters": True,
    "has_connections": True,
    "has_context": True,
    "missing_fields": [],
    "warnings": ["Minor issue..."],
    "errors": []
}
```

---

## 📊 DATA STRUCTURES

### Complete Workflow Data Structure

```python
{
    "url": "https://n8n.io/workflows/2462-...",
    "id": "2462",
    "scrape_timestamp": "2025-01-17T12:00:00",
    "scrape_version": "1.0.0",
    
    "page_content": {
        "title": str,
        "description": str,
        "categories": List[CategoryTag],
        "node_tags": List[NodeTag],
        "tags": List[str],
        "setup_instructions": Optional[SetupInstructions],
        "author": Optional[str],
        "created_at": Optional[str],
        "views": Optional[int],
        "likes": Optional[int]
    },
    
    "workflow": {
        "iframe_url": str,
        "workflow_json": WorkflowJSON,
        "node_configurations": List[NodeConfiguration],
        "canvas_layout": CanvasLayout,
        "screenshot_path": Optional[str]
    },
    
    "explainer_content": {
        "sections": List[ExplainerSection],
        "images": List[ImageAsset],
        "videos": List[VideoAsset],
        "extracted_text": AggregatedText
    },
    
    "validation": {
        "valid": bool,
        "completeness_score": float,
        "warnings": List[str],
        "errors": List[str]
    }
}
```

---

## 🚀 USAGE EXAMPLES

### Complete Workflow Scraping Example

```python
import asyncio
from src.config import Config
from src.orchestrator.scraper import WorkflowScraperOrchestrator

async def main():
    # Initialize
    config = Config.from_defaults()
    orchestrator = WorkflowScraperOrchestrator(config)
    
    # Test connection
    if not orchestrator.test_connection():
        print("Connection failed!")
        return
    
    # Scrape single workflow
    url = "https://n8n.io/workflows/2462-angie-personal-ai-assistant/"
    
    result = await orchestrator.scrape_workflow(url)
    
    # Access data
    print(f"Title: {result['page_content']['title']}")
    print(f"Nodes: {len(result['workflow']['workflow_json']['nodes'])}")
    print(f"Images: {len(result['explainer_content']['images'])}")
    print(f"Valid: {result['validation']['valid']}")

if __name__ == '__main__':
    asyncio.run(main())
```

### Batch Scraping Example

```python
# Scrape multiple workflows
urls = [
    "https://n8n.io/workflows/2462-angie...",
    "https://n8n.io/workflows/8237-personal-life-manager...",
    "https://n8n.io/workflows/8527-learn-n8n-basics...",
]

results = orchestrator.scrape_batch(urls, concurrency=2)

for result in results:
    if result.get('success'):
        print(f"✓ {result['id']}: {result['page_content']['title']}")
    else:
        print(f"✗ {result['url']}: {result['error']}")
```

### Export Example

```python
from src.exporters.jsonl_exporter import JSONLExporter

# Export to JSONL for training
exporter = JSONLExporter(config)
exporter.export('./data/workflows', './output/training_data.jsonl')

print("Training data exported!")
```

---

**Document Version:** 1.0.0  
**Last Updated:** January 17, 2025  
**Next Review:** After implementation completion