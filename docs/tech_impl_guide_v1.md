# Technical Implementation Guide v1.0.0
**Document Version:** 1.0.0  
**Date:** January 17, 2025  
**Project:** n8n-scraper-v1  
**Author:** Technical Architect  
**Status:** Ready for Development

---

## 📋 VERSION CONTROL

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0.0 | 2025-01-17 | Initial release | Tech Architect |

---

## 🎯 DOCUMENT PURPOSE

This document provides complete technical implementation details for developers building the n8n workflow scraper. It includes:
- Detailed code architecture
- Implementation patterns
- Code examples for each component
- Error handling strategies
- Testing approaches
- Performance optimization

---

## 🏗️ SYSTEM ARCHITECTURE

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     CLI LAYER                                │
│  Entry Point: src/cli.py                                    │
│  Framework: Click                                            │
│  Responsibility: User interface, command routing             │
└──────────────────┬──────────────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────────────┐
│                  ORCHESTRATOR LAYER                          │
│  Main: src/orchestrator/scraper.py                          │
│  Components:                                                 │
│    - WorkflowScraperOrchestrator (main controller)          │
│    - WorkQueue (manages scraping queue)                     │
│    - RetryManager (handles failures)                        │
│    - RateLimiter (prevents overload)                        │
│  Responsibility: Coordinate extraction pipeline             │
└──────────────────┬──────────────────────────────────────────┘
                   │
       ┌───────────┼───────────┐
       │           │           │
┌──────▼─────┐ ┌──▼─────┐ ┌──▼─────────┐
│  Phase 1   │ │Phase 2 │ │  Phase 3   │
│  Extractor │ │Extractor│ │ Extractor  │
└────────────┘ └─────────┘ └────────────┘
       │           │           │
       └───────────┼───────────┘
                   │
┌──────────────────▼──────────────────────────────────────────┐
│                  PROCESSOR LAYER                             │
│  Components:                                                 │
│    - ImageProcessor (download + OCR)                        │
│    - VideoProcessor (transcript extraction)                 │
│    - TextAggregator (combine all text)                      │
│  Responsibility: Process extracted data                     │
└──────────────────┬──────────────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────────────┐
│                  VALIDATION LAYER                            │
│  Components:                                                 │
│    - WorkflowValidator (validate JSON structure)            │
│    - DataValidator (check completeness)                     │
│  Responsibility: Ensure data quality                        │
└──────────────────┬──────────────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────────────┐
│                  STORAGE LAYER                               │
│  Components:                                                 │
│    - JSONExporter                                            │
│    - JSONLExporter (ML training format)                     │
│    - CSVExporter (metadata)                                 │
│    - SQLiteExporter (queryable DB)                          │
│  Responsibility: Persist data in multiple formats           │
└─────────────────────────────────────────────────────────────┘
```

---

## 📦 CORE COMPONENTS

### 1. CLI Interface (src/cli.py)

```python
"""
CLI Interface for n8n Workflow Scraper
Version: 1.0.0
"""

import click
from typing import Optional
from pathlib import Path
import structlog

from .orchestrator.scraper import WorkflowScraperOrchestrator
from .config import Config
from .utils.logger import setup_logging

logger = structlog.get_logger()

@click.group()
@click.version_option(version='1.0.0')
@click.option('--config', type=click.Path(exists=True), 
              help='Path to config file')
@click.option('--verbose', is_flag=True, help='Enable verbose logging')
@click.pass_context
def cli(ctx: click.Context, config: Optional[str], verbose: bool):
    """n8n Workflow Scraper - Extract comprehensive workflow data"""
    
    # Setup logging
    log_level = 'DEBUG' if verbose else 'INFO'
    setup_logging(level=log_level)
    
    # Load configuration
    config_obj = Config.from_file(config) if config else Config.from_defaults()
    ctx.obj = {
        'config': config_obj,
        'orchestrator': WorkflowScraperOrchestrator(config_obj)
    }
    
    logger.info("n8n scraper initialized", version="1.0.0")


@cli.command()
@click.pass_context
def test_connection(ctx: click.Context):
    """Test connection to n8n.io"""
    
    orchestrator = ctx.obj['orchestrator']
    
    try:
        success = orchestrator.test_connection()
        if success:
            click.echo(click.style('✓ Connection successful!', fg='green'))
        else:
            click.echo(click.style('✗ Connection failed', fg='red'))
            raise click.Abort()
    except Exception as e:
        logger.error("Connection test failed", error=str(e))
        click.echo(click.style(f'✗ Error: {e}', fg='red'))
        raise click.Abort()


@cli.command()
@click.argument('url')
@click.option('--output', type=click.Path(), help='Output file path')
@click.pass_context
def scrape_workflow(ctx: click.Context, url: str, output: Optional[str]):
    """Scrape a single workflow (all three phases)"""
    
    orchestrator = ctx.obj['orchestrator']
    
    click.echo(f'Scraping workflow: {url}')
    
    with click.progressbar(length=3, label='Extracting') as bar:
        result = orchestrator.scrape_workflow(
            url, 
            progress_callback=lambda phase: bar.update(1)
        )
    
    if output:
        output_path = Path(output)
    else:
        workflow_id = orchestrator.extract_workflow_id(url)
        output_path = Path(f'./data/workflows/{workflow_id}.json')
    
    # Save result
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        import json
        json.dump(result, f, indent=2)
    
    click.echo(click.style(f'✓ Saved to {output_path}', fg='green'))
    
    # Show summary
    click.echo('\nSummary:')
    click.echo(f'  Nodes: {len(result["workflow"]["workflow_json"]["nodes"])}')
    click.echo(f'  Images: {len(result["explainer_content"]["images"])}')
    click.echo(f'  Videos: {len(result["explainer_content"]["videos"])}')


@cli.command()
@click.option('--urls-file', type=click.Path(exists=True), required=True,
              help='File containing URLs (one per line)')
@click.option('--concurrency', type=int, default=2, 
              help='Number of parallel scrapers')
@click.option('--limit', type=int, help='Limit number of workflows')
@click.pass_context
def scrape_batch(ctx: click.Context, urls_file: str, 
                 concurrency: int, limit: Optional[int]):
    """Scrape multiple workflows from a file"""
    
    orchestrator = ctx.obj['orchestrator']
    
    # Read URLs
    with open(urls_file) as f:
        urls = [line.strip() for line in f if line.strip()]
    
    if limit:
        urls = urls[:limit]
    
    click.echo(f'Scraping {len(urls)} workflows with concurrency={concurrency}')
    
    # Run batch scraping
    results = orchestrator.scrape_batch(
        urls, 
        concurrency=concurrency,
        progress=True
    )
    
    # Show results
    successful = sum(1 for r in results if r.get('success'))
    click.echo(click.style(
        f'\n✓ Completed: {successful}/{len(urls)} successful', 
        fg='green'
    ))


@cli.command()
@click.option('--limit', type=int, help='Limit workflows to scrape')
@click.option('--offset', type=int, default=0, help='Start offset')
@click.pass_context
def scrape_sitemap(ctx: click.Context, limit: Optional[int], offset: int):
    """Scrape workflows from n8n.io sitemap"""
    
    orchestrator = ctx.obj['orchestrator']
    
    click.echo('Fetching sitemap...')
    urls = orchestrator.fetch_sitemap_urls()
    
    click.echo(f'Found {len(urls)} workflows in sitemap')
    
    # Apply offset and limit
    urls = urls[offset:]
    if limit:
        urls = urls[:limit]
    
    click.echo(f'Scraping {len(urls)} workflows (offset={offset})')
    
    # Run scraping
    results = orchestrator.scrape_batch(urls, progress=True)
    
    click.echo(click.style(f'\n✓ Scraping complete', fg='green'))


@cli.command()
@click.argument('url')
@click.pass_context
def extract_page(ctx: click.Context, url: str):
    """Extract only page content (Phase 1)"""
    
    orchestrator = ctx.obj['orchestrator']
    result = orchestrator.extract_phase1(url)
    
    click.echo(json.dumps(result, indent=2))


@cli.command()
@click.argument('url')
@click.pass_context
def extract_workflow(ctx: click.Context, url: str):
    """Extract only workflow iframe (Phase 2)"""
    
    orchestrator = ctx.obj['orchestrator']
    result = orchestrator.extract_phase2(url)
    
    click.echo(json.dumps(result, indent=2))


@cli.command()
@click.argument('url')
@click.pass_context
def extract_explainer(ctx: click.Context, url: str):
    """Extract only explainer content (Phase 3)"""
    
    orchestrator = ctx.obj['orchestrator']
    result = orchestrator.extract_phase3(url)
    
    click.echo(json.dumps(result, indent=2))


@cli.command()
@click.option('--workflow-id', help='Process specific workflow')
@click.pass_context
def process_media(ctx: click.Context, workflow_id: Optional[str]):
    """Process media content (images, videos)"""
    
    orchestrator = ctx.obj['orchestrator']
    
    if workflow_id:
        result = orchestrator.process_workflow_media(workflow_id)
        click.echo(f'Processed media for workflow {workflow_id}')
    else:
        results = orchestrator.process_all_media()
        click.echo(f'Processed media for {len(results)} workflows')


@cli.command()
@click.option('--workflow-id', help='Validate specific workflow')
@click.pass_context
def validate(ctx: click.Context, workflow_id: Optional[str]):
    """Validate scraped data quality"""
    
    orchestrator = ctx.obj['orchestrator']
    
    if workflow_id:
        result = orchestrator.validate_workflow(workflow_id)
        click.echo(json.dumps(result, indent=2))
    else:
        results = orchestrator.validate_all()
        
        total = len(results)
        valid = sum(1 for r in results if r['valid'])
        
        click.echo(f'\nValidation Results:')
        click.echo(f'  Total: {total}')
        click.echo(f'  Valid: {valid} ({valid/total*100:.1f}%)')
        click.echo(f'  Invalid: {total-valid}')


@cli.command()
@click.option('--format', type=click.Choice(['json', 'jsonl', 'csv', 'sqlite']),
              required=True, help='Export format')
@click.option('--output', type=click.Path(), required=True,
              help='Output file path')
@click.pass_context
def export(ctx: click.Context, format: str, output: str):
    """Export dataset in various formats"""
    
    orchestrator = ctx.obj['orchestrator']
    
    click.echo(f'Exporting dataset as {format}...')
    
    orchestrator.export_dataset(format=format, output_path=output)
    
    click.echo(click.style(f'✓ Exported to {output}', fg='green'))


@cli.command()
@click.option('--verbose', is_flag=True, help='Show detailed stats')
@click.pass_context
def stats(ctx: click.Context, verbose: bool):
    """Show dataset statistics"""
    
    orchestrator = ctx.obj['orchestrator']
    stats = orchestrator.get_statistics()
    
    click.echo('\n📊 Dataset Statistics\n')
    click.echo(f'Total Workflows: {stats["total_workflows"]}')
    click.echo(f'Complete: {stats["complete_workflows"]}')
    click.echo(f'Incomplete: {stats["incomplete_workflows"]}')
    click.echo(f'\nTotal Nodes: {stats["total_nodes"]}')
    click.echo(f'Unique Node Types: {stats["unique_node_types"]}')
    click.echo(f'\nImages: {stats["total_images"]}')
    click.echo(f'Videos: {stats["total_videos"]}')
    
    if verbose:
        click.echo('\n--- Detailed Breakdown ---')
        for category, count in stats['categories'].items():
            click.echo(f'{category}: {count}')


@cli.command()
@click.option('--from-checkpoint', type=click.Path(exists=True),
              help='Resume from checkpoint file')
@click.pass_context
def resume(ctx: click.Context, from_checkpoint: Optional[str]):
    """Resume interrupted scraping session"""
    
    orchestrator = ctx.obj['orchestrator']
    
    if from_checkpoint:
        checkpoint_path = from_checkpoint
    else:
        checkpoint_path = './data/.checkpoint'
    
    click.echo(f'Resuming from {checkpoint_path}...')
    
    result = orchestrator.resume_from_checkpoint(checkpoint_path)
    
    click.echo(click.style('✓ Resume complete', fg='green'))


if __name__ == '__main__':
    cli()
```

---

### 2. Configuration Management (src/config.py)

```python
"""
Configuration Management
Version: 1.0.0
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
import yaml


@dataclass
class ScraperConfig:
    """Scraper-specific configuration"""
    rate_limit: float = 2.0  # requests per second
    timeout: int = 30  # seconds
    retries: int = 3
    concurrency: int = 2
    user_agent: str = 'n8n-scraper/1.0.0'


@dataclass
class StorageConfig:
    """Storage configuration"""
    base_dir: Path = Path('./data')
    workflows_dir: Path = Path('./data/workflows')
    images_dir: Path = Path('./data/images')
    transcripts_dir: Path = Path('./data/transcripts')
    checkpoints_dir: Path = Path('./data/checkpoints')
    
    def __post_init__(self):
        # Ensure all directories exist
        for dir_path in [
            self.base_dir, 
            self.workflows_dir,
            self.images_dir, 
            self.transcripts_dir,
            self.checkpoints_dir
        ]:
            dir_path.mkdir(parents=True, exist_ok=True)


@dataclass
class BrowserConfig:
    """Browser automation configuration"""
    headless: bool = True
    browser_type: str = 'chromium'  # chromium, firefox, webkit
    viewport_width: int = 1920
    viewport_height: int = 1080
    slow_mo: int = 0  # milliseconds to slow down operations


@dataclass
class OCRConfig:
    """OCR configuration"""
    enabled: bool = True
    language: str = 'eng'
    dpi: int = 300
    tesseract_cmd: Optional[str] = None  # Path to tesseract executable


@dataclass
class VideoConfig:
    """Video processing configuration"""
    download_transcripts: bool = True
    fallback_to_autogenerated: bool = True
    max_duration: Optional[int] = None  # seconds


@dataclass
class Config:
    """Main configuration object"""
    scraper: ScraperConfig = field(default_factory=ScraperConfig)
    storage: StorageConfig = field(default_factory=StorageConfig)
    browser: BrowserConfig = field(default_factory=BrowserConfig)
    ocr: OCRConfig = field(default_factory=OCRConfig)
    video: VideoConfig = field(default_factory=VideoConfig)
    
    @classmethod
    def from_file(cls, path: str) -> 'Config':
        """Load configuration from YAML file"""
        with open(path) as f:
            data = yaml.safe_load(f)
        
        return cls(
            scraper=ScraperConfig(**data.get('scraper', {})),
            storage=StorageConfig(**data.get('storage', {})),
            browser=BrowserConfig(**data.get('browser', {})),
            ocr=OCRConfig(**data.get('ocr', {})),
            video=VideoConfig(**data.get('video', {}))
        )
    
    @classmethod
    def from_defaults(cls) -> 'Config':
        """Create configuration with default values"""
        return cls()
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'scraper': self.scraper.__dict__,
            'storage': {k: str(v) for k, v in self.storage.__dict__.items()},
            'browser': self.browser.__dict__,
            'ocr': self.ocr.__dict__,
            'video': self.video.__dict__
        }
```

---

### 3. Main Orchestrator (src/orchestrator/scraper.py)

```python
"""
Main Workflow Scraper Orchestrator
Version: 1.0.0

Coordinates the three-phase extraction process.
"""

import asyncio
from typing import Optional, List, Dict, Callable
from pathlib import Path
import structlog
from playwright.async_api import async_playwright, Page

from ..config import Config
from ..extractors.phase1_page import PageContentExtractor
from ..extractors.phase2_workflow import WorkflowIframeExtractor
from ..extractors.phase3_explainer import ExplainerIframeExtractor
from ..processors.image_processor import ImageProcessor
from ..processors.video_processor import VideoProcessor
from ..validators.workflow_validator import WorkflowValidator
from .queue import WorkQueue
from .retry import RetryManager
from .rate_limiter import RateLimiter

logger = structlog.get_logger()


class WorkflowScraperOrchestrator:
    """
    Main orchestrator for workflow scraping.
    
    Responsibilities:
    - Coordinate three-phase extraction
    - Manage browser lifecycle
    - Handle errors and retries
    - Rate limiting
    - Progress tracking
    """
    
    VERSION = "1.0.0"
    
    def __init__(self, config: Config):
        self.config = config
        
        # Initialize extractors
        self.phase1_extractor = PageContentExtractor(config)
        self.phase2_extractor = WorkflowIframeExtractor(config)
        self.phase3_extractor = ExplainerIframeExtractor(config)
        
        # Initialize processors
        self.image_processor = ImageProcessor(config)
        self.video_processor = VideoProcessor(config)
        
        # Initialize validators
        self.workflow_validator = WorkflowValidator(config)
        
        # Initialize utilities
        self.work_queue = WorkQueue()
        self.retry_manager = RetryManager(max_retries=config.scraper.retries)
        self.rate_limiter = RateLimiter(
            requests_per_second=config.scraper.rate_limit
        )
        
        logger.info("Orchestrator initialized", version=self.VERSION)
    
    def test_connection(self) -> bool:
        """Test connection to n8n.io"""
        try:
            import requests
            response = requests.get('https://n8n.io', timeout=10)
            return response.status_code == 200
        except Exception as e:
            logger.error("Connection test failed", error=str(e))
            return False
    
    async def scrape_workflow(
        self, 
        url: str, 
        progress_callback: Optional[Callable] = None
    ) -> Dict:
        """
        Scrape a single workflow (all three phases).
        
        Args:
            url: Workflow URL
            progress_callback: Optional callback for progress updates
        
        Returns:
            Complete workflow data
        """
        
        workflow_id = self.extract_workflow_id(url)
        logger.info("Starting workflow scrape", workflow_id=workflow_id, url=url)
        
        # Rate limiting
        await self.rate_limiter.acquire()
        
        workflow_data = {
            'url': url,
            'id': workflow_id,
            'scrape_timestamp': self._get_timestamp(),
            'scrape_version': self.VERSION
        }
        
        async with async_playwright() as p:
            browser = await p[self.config.browser.browser_type].launch(
                headless=self.config.browser.headless,
                slow_mo=self.config.browser.slow_mo
            )
            
            page = await browser.new_page(
                viewport={
                    'width': self.config.browser.viewport_width,
                    'height': self.config.browser.viewport_height
                }
            )
            
            try:
                # Navigate to page
                await page.goto(url, wait_until='networkidle', timeout=30000)
                
                # Phase 1: Extract page content
                logger.info("Phase 1: Extracting page content", workflow_id=workflow_id)
                page_content = await self.phase1_extractor.extract(page)
                workflow_data['page_content'] = page_content
                
                if progress_callback:
                    progress_callback('phase1')
                
                # Phase 2: Extract workflow iframe
                logger.info("Phase 2: Extracting workflow", workflow_id=workflow_id)
                workflow = await self.phase2_extractor.extract(page)
                workflow_data['workflow'] = workflow
                
                if progress_callback:
                    progress_callback('phase2')
                
                # Phase 3: Extract explainer content
                logger.info("Phase 3: Extracting explainer", workflow_id=workflow_id)
                explainer = await self.phase3_extractor.extract(page)
                workflow_data['explainer_content'] = explainer
                
                if progress_callback:
                    progress_callback('phase3')
                
                # Validate
                validation = self.workflow_validator.validate(workflow_data)
                workflow_data['validation'] = validation
                
                # Save to file
                self._save_workflow(workflow_data)
                
                logger.info(
                    "Workflow scrape complete", 
                    workflow_id=workflow_id,
                    nodes=len(workflow.get('workflow_json', {}).get('nodes', [])),
                    valid=validation['valid']
                )
                
                return workflow_data
                
            except Exception as e:
                logger.error(
                    "Workflow scrape failed", 
                    workflow_id=workflow_id,
                    error=str(e)
                )
                raise
                
            finally:
                await browser.close()
    
    def scrape_batch(
        self, 
        urls: List[str], 
        concurrency: int = 2,
        progress: bool = True
    ) -> List[Dict]:
        """
        Scrape multiple workflows with controlled concurrency.
        
        Args:
            urls: List of workflow URLs
            concurrency: Number of parallel scrapers
            progress: Show progress bar
        
        Returns:
            List of scraped workflow data
        """
        
        return asyncio.run(
            self._scrape_batch_async(urls, concurrency, progress)
        )
    
    async def _scrape_batch_async(
        self, 
        urls: List[str],
        concurrency: int,
        progress: bool
    ) -> List[Dict]:
        """Async implementation of batch scraping"""
        
        from tqdm import tqdm
        
        results = []
        semaphore = asyncio.Semaphore(concurrency)
        
        async def scrape_with_semaphore(url: str):
            async with semaphore:
                try:
                    result = await self.scrape_workflow(url)
                    result['success'] = True
                    return result
                except Exception as e:
                    logger.error("Batch scrape error", url=url, error=str(e))
                    return {
                        'url': url,
                        'success': False,
                        'error': str(e)
                    }
        
        if progress:
            tasks = [scrape_with_semaphore(url) for url in urls]
            
            for coro in tqdm(
                asyncio.as_completed(tasks), 
                total=len(urls),
                desc="Scraping workflows"
            ):
                result = await coro
                results.append(result)
        else:
            results = await asyncio.gather(
                *[scrape_with_semaphore(url) for url in urls]
            )
        
        return results
    
    def fetch_sitemap_urls(self) -> List[str]:
        """Fetch workflow URLs from n8n.io sitemap"""
        
        import requests
        from bs4 import BeautifulSoup
        
        sitemap_url = 'https://n8n.io/sitemap-workflows.xml'
        
        logger.info("Fetching sitemap", url=sitemap_url)
        
        response = requests.get(sitemap_url)
        soup = BeautifulSoup(response.content, 'xml')
        
        urls = [loc.text for loc in soup.find_all('loc')]
        
        logger.info("Sitemap fetched", count=len(urls))
        
        return urls
    
    def extract_workflow_id(self, url: str) -> str:
        """Extract workflow ID from URL"""
        import re
        match = re.search(r'/workflows/(\d+)-', url)
        return match.group(1) if match else 'unknown'
    
    def _save_workflow(self, workflow_data: Dict):
        """Save workflow data to file"""
        
        import json
        
        workflow_id = workflow_data['id']
        output_path = self.config.storage.workflows_dir / f'{workflow_id}.json'
        
        with open(output_path, 'w') as f:
            json.dump(workflow_data, f, indent=2)
        
        logger.debug("Workflow saved", workflow_id=workflow_id, path=str(output_path))
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()
```

---

## 🔄 EXTRACTION PIPELINE

### Phase 1 Extractor Implementation

See separate artifact for complete implementation...

---

## 🧪 TESTING STRATEGY

### Unit Test Example

```python
"""
Unit tests for Phase 1 Extractor
Version: 1.0.0
"""

import pytest
from pathlib import Path
from bs4 import BeautifulSoup

from src.extractors.phase1_page import PageContentExtractor
from src.config import Config


@pytest.fixture
def config():
    """Test configuration"""
    return Config.from_defaults()


@pytest.fixture
def extractor(config):
    """Phase 1 extractor instance"""
    return PageContentExtractor(config)


@pytest.fixture
def sample_html():
    """Load sample HTML"""
    html_path = Path(__file__).parent / 'fixtures' / 'sample_page.html'
    with open(html_path) as f:
        return f.read()


@pytest.mark.asyncio
async def test_extract_title(extractor, sample_html):
    """Test title extraction"""
    
    # Mock page object
    from unittest.mock import AsyncMock, MagicMock
    
    page = MagicMock()
    page.locator = MagicMock()
    
    title_locator = MagicMock()
    title_locator.first.inner_text = AsyncMock(
        return_value="Angie, Personal AI Assistant"
    )
    
    page.locator.return_value = title_locator
    
    # Extract
    result = await extractor.extract(page)
    
    # Verify
    assert result['title'] == "Angie, Personal AI Assistant"


@pytest.mark.asyncio
async def test_extract_categories(extractor):
    """Test category extraction"""
    # Implementation...
    pass


@pytest.mark.integration
@pytest.mark.asyncio
async def test_full_extraction():
    """Integration test: full page extraction"""
    # Implementation...
    pass
```

---

## 🎯 ERROR HANDLING PATTERNS

```python
"""
Error Handling Patterns
Version: 1.0.0
"""

class ScraperError(Exception):
    """Base exception for scraper errors"""
    pass


class ExtractionError(ScraperError):
    """Error during data extraction"""
    pass


class ValidationError(ScraperError):
    """Error during validation"""
    pass


class NetworkError(ScraperError):
    """Network-related error"""
    pass


# Usage in extractors

async def extract_with_error_handling(self, page):
    """Example extraction with proper error handling"""
    
    try:
        # Attempt extraction
        title = await page.locator('h1').first.inner_text()
        
    except PlaywrightTimeoutError:
        logger.warning("Timeout extracting title, using default")
        title = "Unknown"
        
    except Exception as e:
        logger.error("Unexpected error extracting title", error=str(e))
        raise ExtractionError(f"Failed to extract title: {e}")
    
    return title
```

---

## 📊 PERFORMANCE OPTIMIZATION

### Async Operations

```python
"""
Performance optimization patterns
Version: 1.0.0
"""

import asyncio
from typing import List

async def parallel_image_download(urls: List[str]) -> List[Path]:
    """Download multiple images in parallel"""
    
    async def download_one(url: str) -> Path:
        # Download logic
        pass
    
    # Execute in parallel with limit
    semaphore = asyncio.Semaphore(5)  # Max 5 concurrent downloads
    
    async def download_with_limit(url: str):
        async with semaphore:
            return await download_one(url)
    
    results = await asyncio.gather(
        *[download_with_limit(url) for url in urls],
        return_exceptions=True
    )
    
    return [r for r in results if isinstance(r, Path)]
```

---

## 📝 LOGGING STANDARDS

```python
"""
Logging standards
Version: 1.0.0
"""

import structlog

# Configure structured logging
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.add_log_level,
        structlog.processors.JSONRenderer()
    ]
)

logger = structlog.get_logger()

# Usage examples

# Info level
logger.info(
    "Workflow scraped successfully",
    workflow_id="2462",
    nodes_count=15,
    duration_ms=3450
)

# Warning level
logger.warning(
    "Missing optional field",
    workflow_id="2462",
    field="author"
)

# Error level
logger.error(
    "Extraction failed",
    workflow_id="2462",
    phase="phase2",
    error=str(e),
    exc_info=True
)
```

---

## 🔐 SECURITY CONSIDERATIONS

1. **No Credential Storage**
   - Never store credentials in code
   - Use environment variables
   - Implement secure credential management

2. **Rate Limiting**
   - Respect robots.txt
   - Implement exponential backoff
   - Monitor for 429 responses

3. **Data Sanitization**
   - Validate all URLs before requesting
   - Sanitize file names
   - Validate JSON structure

---

## 📋 DEVELOPER CHECKLIST

### Before Starting Development
- [ ] Review project brief
- [ ] Understand three-layer architecture
- [ ] Set up development environment
- [ ] Install dependencies
- [ ] Configure IDE

### During Development
- [ ] Write unit tests for each component
- [ ] Use type hints (mypy)
- [ ] Follow PEP 8 style guide
- [ ] Add docstrings to all functions
- [ ] Use structured logging
- [ ] Handle errors appropriately

### Before Committing
- [ ] Run all tests (`pytest`)
- [ ] Check type coverage (`mypy`)
- [ ] Run linter (`pylint`)
- [ ] Format code (`black`)
- [ ] Update documentation
- [ ] Review changes

---

## 🎓 NEXT STEPS

1. Review this implementation guide
2. Review API documentation (separate artifact)
3. Review dataset schema (separate artifact)
4. Set up development environment
5. Start with Day 1-2 tasks (project setup)

---

**Document Version:** 1.0.0  
**Last Updated:** January 17, 2025  
**Next Review:** After Sprint 1 completion