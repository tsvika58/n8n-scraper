# 🎯 N8N Workflow Dataset Scraper - Project Brief

**Version:** 1.0  
**Date:** January 17, 2025  
**Project Code:** n8n-scraper-v1  
**Team:** R&D + 1 Developer  
**Timeline:** 2 weeks (Sprint-based)

---

## 📋 EXECUTIVE SUMMARY

### Project Goal
Build a production-grade web scraper to extract comprehensive workflow data from n8n.io, creating a rich dataset for training an AI model that converts natural language descriptions into n8n workflows.

### Business Value
- **Primary:** Enable AI-powered workflow generation from natural language
- **Secondary:** Build reusable scraping infrastructure for similar automation platforms
- **Impact:** Foundation for the n8n-claude-engine NLP model

### Success Criteria
✅ Extract 2,100+ complete workflows with 95%+ data completeness  
✅ Capture workflow JSON, node configurations, and contextual explanations  
✅ Extract multimodal content (text, images, videos, transcripts)  
✅ Production-ready, maintainable, and well-documented codebase  
✅ Dataset ready for AI model training

---

## 🎯 COMPLETE DATA EXTRACTION SPECIFICATION

### What Data Will Be Available

**YES - Complete Parameter Coverage:**

#### 1. Node Configurations (100% Coverage)
```json
{
  "node_id": "unique-node-123",
  "node_name": "Send Telegram Message",
  "node_type": "n8n-nodes-base.telegram",
  "type_version": 1.1,
  "position": [400, 300],
  
  "parameters": {
    "operation": "sendMessage",
    "chatId": "={{ $json.userId }}",
    "text": "Hello {{ $json.name }}! Your order #{{ $json.orderId }} is confirmed.",
    "additionalFields": {
      "parse_mode": "HTML",
      "disable_notification": false,
      "reply_markup": {
        "inline_keyboard": [
          [{"text": "Track Order", "url": "https://example.com/track"}]
        ]
      }
    }
  },
  
  "credentials": {
    "telegramApi": {
      "id": "1",
      "name": "Telegram Bot Token"
    }
  },
  
  "notes": "Sends confirmation message to customer via Telegram",
  "disabled": false,
  "continue_on_fail": false,
  "retry_on_fail": true,
  "max_tries": 3,
  "wait_between_tries": 1000
}
```

**Every parameter will include:**
- Parameter name (e.g., `chatId`)
- Parameter value (e.g., `"={{ $json.userId }}"`)
- Parameter type (`string`, `number`, `boolean`, `expression`, `json`)
- Is expression: `true/false`
- Default values
- Conditional parameters (shown only when certain conditions met)
- Nested parameters (like `additionalFields`)

#### 2. Connections (Complete Mapping)
```json
{
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
    },
    "Process Message": {
      "main": [
        [
          {
            "node": "Send to OpenAI",
            "type": "main",
            "index": 0
          }
        ]
      ],
      "error": [
        [
          {
            "node": "Error Handler",
            "type": "main",
            "index": 0
          }
        ]
      ]
    }
  }
}
```

**Connection details include:**
- Source node name
- Target node name
- Connection type (`main`, `error`, `conditional`)
- Output index (for multi-output nodes)
- Input index (for multi-input nodes)
- Data flow description

#### 3. Context for Each Node
```json
{
  "node_context": {
    "node_id": "telegram-trigger-1",
    "purpose": "Listens for incoming messages from Telegram bot",
    "trigger_type": "webhook",
    "trigger_description": "Fires when user sends message to bot",
    
    "input_data": {
      "description": "Receives webhook payload from Telegram",
      "example": {
        "message": {
          "text": "Hello bot",
          "from": {"id": 12345, "username": "john_doe"}
        }
      }
    },
    
    "output_data": {
      "description": "Outputs parsed message data",
      "example": {
        "message": "Hello bot",
        "userId": 12345,
        "username": "john_doe",
        "chatId": 67890
      }
    },
    
    "expressions_used": [
      "={{ $json.message.text }}",
      "={{ $json.message.from.id }}"
    ],
    
    "common_patterns": [
      "Used as workflow trigger",
      "Often connected to message processing",
      "Typically followed by conditional logic"
    ],
    
    "configuration_tips": [
      "Set up bot token from @BotFather first",
      "Enable webhook in Telegram Bot settings",
      "Use ngrok for local testing"
    ]
  }
}
```

#### 4. Complete Workflow Structure
```json
{
  "workflow": {
    "id": "2462",
    "name": "Angie - Personal AI Assistant",
    "description": "Voice and text AI assistant via Telegram",
    
    "nodes": [
      {
        "id": "node-1",
        "name": "Telegram Trigger",
        "type": "n8n-nodes-base.telegramTrigger",
        "parameters": {...},
        "credentials": {...},
        "position": [100, 200],
        "notes": "Entry point for user messages"
      },
      // ... all nodes with complete configs
    ],
    
    "connections": {
      // Complete connection mapping
    },
    
    "settings": {
      "executionOrder": "v1",
      "saveDataErrorExecution": "all",
      "saveDataSuccessExecution": "all",
      "saveManualExecutions": true,
      "timezone": "America/New_York",
      "errorWorkflow": null
    },
    
    "staticData": {
      "conversationHistory": [],
      "userPreferences": {}
    },
    
    "tags": ["ai", "telegram", "assistant", "voice"],
    "active": true,
    "versionId": "1.0"
  }
}
```

#### 5. Contextual Information
```json
{
  "context": {
    "use_case": {
      "problem": "Users need a personal AI assistant accessible via Telegram",
      "solution": "Voice and text interaction with AI via Telegram bot",
      "benefits": [
        "Natural language interaction",
        "Voice message support",
        "Context-aware responses",
        "Multi-service integration"
      ]
    },
    
    "setup_requirements": {
      "credentials_needed": [
        {
          "service": "Telegram",
          "type": "telegramApi",
          "used_in_nodes": ["Telegram Trigger", "Send Message", "Get Voice File"],
          "setup_guide": "Create bot via @BotFather, get token"
        },
        {
          "service": "OpenAI",
          "type": "openAiApi",
          "used_in_nodes": ["OpenAI Chat", "Whisper Transcription"],
          "setup_guide": "Get API key from platform.openai.com"
        }
      ],
      
      "estimated_setup_time": "15 minutes",
      "difficulty": "intermediate"
    },
    
    "workflow_pattern": {
      "pattern_type": "conversational_ai",
      "entry_point": "webhook_trigger",
      "main_flow": [
        "Receive message",
        "Process/transcribe if voice",
        "Send to AI model",
        "Format response",
        "Send back to user"
      ],
      "error_handling": "Sends error message to user",
      "common_variations": [
        "Add context from database",
        "Include web search",
        "Save conversation history"
      ]
    },
    
    "natural_language_queries": [
      "How do I create a Telegram AI assistant?",
      "Build a voice-enabled chatbot with OpenAI",
      "Create an AI assistant that responds to Telegram messages",
      "Set up a conversational AI with voice support",
      "Make a Telegram bot that uses ChatGPT"
    ]
  }
}
```

#### 6. Multi-Modal Content
```json
{
  "media_content": {
    "images": [
      {
        "image_id": "workflow_diagram_1",
        "local_path": "./data/images/2462_workflow.png",
        "context_type": "workflow_diagram",
        "contains_nodes": ["Telegram Trigger", "OpenAI", "Send Message"],
        "ocr_text": {
          "extracted_text": "1. User sends message\n2. Process with AI\n3. Send response",
          "confidence": 0.95
        }
      }
    ],
    
    "videos": [
      {
        "platform": "youtube",
        "video_id": "xyz123",
        "title": "Setting up Telegram AI Assistant",
        "transcript": {
          "full_text": "In this tutorial, we'll create a Telegram bot...",
          "segments": [
            {
              "start_time": 0,
              "end_time": 15,
              "text": "First, open Telegram and search for BotFather"
            }
          ]
        },
        "topics_covered": ["bot creation", "API setup", "testing"],
        "nodes_demonstrated": ["Telegram Trigger", "OpenAI Chat"]
      }
    ],
    
    "explainer_sections": [
      {
        "section_type": "overview",
        "heading": "What This Workflow Does",
        "content": "This workflow creates a personal AI assistant...",
        "code_snippets": [],
        "tips": [
          "Test with simple messages first",
          "Monitor API usage to avoid costs"
        ]
      }
    ]
  }
}
```

---

## 📊 COMPLETE DATA MODEL

### Full Dataset Structure

```typescript
interface CompleteWorkflowDataset {
  // Metadata
  workflow_id: string;
  url: string;
  scraped_at: string;
  scrape_version: string;
  
  // Layer 1: Page Content
  page_content: {
    title: string;
    description: string;
    categories: CategoryTag[];
    node_tags: NodeTag[];
    tags: string[];
    author: string;
    created_at: string;
    updated_at: string;
    views: number;
    likes: number;
    setup_instructions: SetupInstructions;
    related_workflows: string[];
    prerequisites: string[];
  };
  
  // Layer 2: Complete Workflow (MOST IMPORTANT)
  workflow: {
    iframe_url: string;
    
    // Complete n8n workflow JSON
    workflow_json: {
      id: string;
      name: string;
      nodes: Node[];           // Every node with ALL parameters
      connections: Connections; // Complete connection mapping
      settings: WorkflowSettings;
      staticData: any;
      tags: string[];
      active: boolean;
    };
    
    // Detailed node configurations
    node_configurations: NodeConfiguration[];
    
    // Visual layout
    canvas_layout: {
      node_positions: NodePosition[];
      connections: ConnectionVisualization[];
      canvas_bounds: BoundingBox;
      flow_direction: string;
    };
    
    // Screenshot
    screenshot_path: string;
  };
  
  // Layer 3: Explainer Content
  explainer_content: {
    sections: ExplainerSection[];
    images: ImageAsset[];
    videos: VideoAsset[];
    extracted_text: AggregatedText;
  };
  
  // Derived Context
  context: {
    use_case: UseCaseContext;
    workflow_pattern: WorkflowPattern;
    natural_language_queries: string[];
    parameter_examples: ParameterExample[];
    expression_examples: ExpressionExample[];
  };
  
  // Quality Metrics
  quality: {
    completeness_score: number;  // 0-1
    has_workflow_json: boolean;
    has_all_parameters: boolean;
    has_connections: boolean;
    has_context: boolean;
    has_media: boolean;
    extraction_warnings: string[];
  };
}

interface Node {
  id: string;
  name: string;
  type: string;                    // e.g., "n8n-nodes-base.telegram"
  typeVersion: number;
  position: [number, number];
  
  // COMPLETE parameters object
  parameters: Record<string, any>; // Every config value
  
  // Credentials used
  credentials?: Record<string, CredentialReference>;
  
  // Additional config
  notes?: string;
  disabled?: boolean;
  continueOnFail?: boolean;
  retryOnFail?: boolean;
  maxTries?: number;
  waitBetweenTries?: number;
  alwaysOutputData?: boolean;
  executeOnce?: boolean;
  onError?: string;
}

interface NodeConfiguration {
  node_id: string;
  node_name: string;
  node_type: string;
  
  // Operation being performed
  operation: string;
  
  // ALL parameters with metadata
  parameters: ConfiguredParameter[];
  
  // Context
  purpose: string;
  input_example: any;
  output_example: any;
  
  // Expressions used
  expressions: string[];
  
  // Configuration tips
  common_mistakes: string[];
  best_practices: string[];
}

interface ConfiguredParameter {
  name: string;              // Parameter name
  display_name: string;      // Human-readable name
  value: any;                // Actual configured value
  value_type: string;        // "fixed" | "expression" | "credential"
  is_expression: boolean;
  expression_code?: string;  // If expression
  default_value: any;
  required: boolean;
  description: string;
  
  // For learning
  example_values: any[];
  common_patterns: string[];
}

interface Connections {
  [sourceNodeName: string]: {
    [outputType: string]: Array<Array<{
      node: string;          // Target node name
      type: string;          // Connection type
      index: number;         // Output/input index
    }>>;
  };
}
```

---

## 🎯 DATA COMPLETENESS GUARANTEE

### What You WILL Get (Guaranteed)

✅ **Complete Node Parameters**
- Every parameter configured in the workflow
- Parameter names and values
- Expression code if used
- Default values and options
- Parameter descriptions

✅ **Complete Connections**
- All node-to-node connections
- Connection types (main, error, conditional)
- Multi-output handling
- Error flow routing

✅ **Complete Context**
- What each node does
- Why it's configured that way
- Common patterns and use cases
- Setup instructions
- Natural language descriptions

✅ **Complete Examples**
- Real-world parameter values
- Expression examples
- Input/output data examples
- Configuration variations

### Example: Complete Node Extraction

```json
{
  "node_name": "OpenAI Chat Model",
  "node_type": "@n8n/n8n-nodes-langchain.lmChatOpenAi",
  "operation": "chat",
  
  "parameters": {
    "model": "gpt-4-turbo-preview",
    "options": {
      "temperature": 0.7,
      "maxTokens": 2000,
      "topP": 1,
      "frequencyPenalty": 0,
      "presencePenalty": 0,
      "timeout": 60000
    },
    "systemMessage": "You are Angie, a helpful personal assistant. Be concise and friendly.",
    "messages": [
      {
        "role": "user",
        "content": "={{ $json.userMessage }}"
      }
    ]
  },
  
  "credentials": {
    "openAiApi": {
      "id": "5",
      "name": "OpenAI Account"
    }
  },
  
  "parameter_context": {
    "model": {
      "value": "gpt-4-turbo-preview",
      "why": "Chosen for better reasoning and longer context window",
      "alternatives": ["gpt-3.5-turbo", "gpt-4"],
      "cost_consideration": "More expensive but better quality"
    },
    "temperature": {
      "value": 0.7,
      "why": "Balanced between creativity and consistency",
      "range": "0.0 (deterministic) to 2.0 (very creative)",
      "typical_values": {
        "factual_qa": 0.3,
        "creative_writing": 1.2,
        "chat": 0.7
      }
    },
    "systemMessage": {
      "value": "You are Angie...",
      "why": "Sets the AI's personality and behavior",
      "tips": [
        "Be specific about tone and style",
        "Include relevant context",
        "Set clear boundaries"
      ]
    }
  },
  
  "expressions_explained": {
    "{{ $json.userMessage }}": {
      "description": "Gets the message text from previous node",
      "data_path": "$json.userMessage",
      "alternative_paths": [
        "{{ $json.text }}",
        "{{ $json.message.text }}"
      ]
    }
  }
}
```

---

## 🏗️ TECHNICAL ARCHITECTURE

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                    CLI INTERFACE                             │
│                  (User Commands)                             │
└──────────────────┬──────────────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────────────┐
│              ORCHESTRATOR                                    │
│  - Workflow queue management                                │
│  - Progress tracking                                        │
│  - Error handling & retry                                   │
│  - Rate limiting                                            │
└──────────────────┬──────────────────────────────────────────┘
                   │
       ┌───────────┼───────────┐
       │           │           │
┌──────▼─────┐ ┌──▼─────┐ ┌──▼─────────┐
│  Phase 1   │ │Phase 2 │ │  Phase 3   │
│   Page     │ │Workflow│ │ Explainer  │
│  Extractor │ │ Iframe │ │   Iframe   │
└──────┬─────┘ └──┬─────┘ └──┬─────────┘
       │          │           │
       └──────────┼───────────┘
                  │
┌─────────────────▼──────────────────────────────────────────┐
│              DATA PIPELINE                                  │
│  - Image downloader & OCR                                  │
│  - Video transcript fetcher                                │
│  - Data validator                                          │
│  - Format converters (JSON/JSONL/CSV)                      │
└──────────────────┬─────────────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────────────┐
│              STORAGE LAYER                                   │
│  - ./data/workflows/     (JSON files)                       │
│  - ./data/images/        (Downloaded images)                │
│  - ./data/transcripts/   (Video transcripts)                │
│  - ./data/database.db    (SQLite for queries)               │
└─────────────────────────────────────────────────────────────┘
```

### Technology Stack

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| **Browser Automation** | Playwright (Python) | Modern, reliable, handles JS-heavy sites |
| **HTTP Client** | aiohttp | Async downloads for images/videos |
| **OCR** | Tesseract (pytesseract) | Open-source, accurate, widely supported |
| **Video Transcripts** | youtube-transcript-api | Direct YouTube API access |
| **Data Storage** | JSON + SQLite | Flexible (JSON) + queryable (SQLite) |
| **CLI Framework** | Click | Industry standard, clean syntax |
| **Logging** | structlog | Structured logging for debugging |
| **Testing** | pytest + pytest-asyncio | Async-aware testing framework |

---

## 📁 PROJECT STRUCTURE

```
n8n-scraper/
├── README.md                      # Project documentation
├── pyproject.toml                 # Dependencies & config
├── .env.example                   # Environment variables template
├── .gitignore
│
├── src/
│   ├── __init__.py
│   ├── cli.py                     # Main CLI entry point
│   ├── config.py                  # Configuration management
│   │
│   ├── orchestrator/
│   │   ├── __init__.py
│   │   ├── scraper.py            # Main orchestrator
│   │   ├── queue.py              # Work queue management
│   │   ├── retry.py              # Retry logic
│   │   └── rate_limiter.py       # Rate limiting
│   │
│   ├── extractors/
│   │   ├── __init__.py
│   │   ├── base.py               # Base extractor class
│   │   ├── phase1_page.py        # Page content extractor
│   │   ├── phase2_workflow.py    # Workflow iframe extractor
│   │   └── phase3_explainer.py   # Explainer iframe extractor
│   │
│   ├── processors/
│   │   ├── __init__.py
│   │   ├── image_processor.py    # Download + OCR
│   │   ├── video_processor.py    # Transcript extraction
│   │   └── text_aggregator.py    # Text aggregation
│   │
│   ├── validators/
│   │   ├── __init__.py
│   │   ├── workflow_validator.py # Validate workflow JSON
│   │   └── data_validator.py     # Validate completeness
│   │
│   ├── exporters/
│   │   ├── __init__.py
│   │   ├── json_exporter.py      # JSON export
│   │   ├── jsonl_exporter.py     # JSONL for training
│   │   ├── csv_exporter.py       # CSV metadata
│   │   └── sqlite_exporter.py    # SQLite database
│   │
│   └── utils/
│       ├── __init__.py
│       ├── logger.py             # Structured logging
│       ├── progress.py           # Progress tracking
│       └── helpers.py            # Common utilities
│
├── tests/
│   ├── __init__.py
│   ├── test_extractors.py
│   ├── test_processors.py
│   ├── test_validators.py
│   └── fixtures/                 # Test data
│       ├── sample_page.html
│       └── sample_workflow.json
│
├── data/                         # Output directory (gitignored)
│   ├── workflows/
│   ├── images/
│   ├── transcripts/
│   └── database.db
│
├── docs/
│   ├── ARCHITECTURE.md           # Technical architecture
│   ├── API.md                    # API documentation
│   └── DATASET_SCHEMA.md         # Dataset structure
│
└── scripts/
    ├── setup.sh                  # Environment setup
    ├── run_sample.sh             # Test on sample URLs
    └── run_full.sh               # Full scrape execution
```

---

## 🚀 DEVELOPMENT ROADMAP

### Sprint 1: Foundation (Days 1-7)

#### Day 1-2: Project Setup & Infrastructure
**Developer Tasks:**
- [ ] Initialize Python project with Poetry
- [ ] Set up project structure
- [ ] Configure Playwright (install browsers)
- [ ] Set up logging infrastructure
- [ ] Create base configuration system
- [ ] Write initial CLI skeleton

**Deliverable:** Basic project scaffold with working CLI

**Acceptance Criteria:**
```bash
$ n8n-scraper --help
# Shows help menu

$ n8n-scraper test-connection
# Tests connection to n8n.io
```

#### Day 3-4: Phase 1 - Page Content Extractor
**Developer Tasks:**
- [ ] Implement PageContentExtractor class
- [ ] Extract title, description, metadata
- [ ] Extract categories and node tags
- [ ] Extract setup modal content
- [ ] Write unit tests
- [ ] Test on 5 sample workflows

**Deliverable:** Working Phase 1 extractor

#### Day 5-6: Phase 2 - Workflow Iframe Extractor
**Developer Tasks:**
- [ ] Implement WorkflowIframeExtractor class
- [ ] Extract workflow JSON from iframe
- [ ] Extract ALL node configurations with ALL parameters
- [ ] Extract complete connection mapping
- [ ] Extract canvas layout
- [ ] Take workflow screenshots
- [ ] Write unit tests

**Deliverable:** Working Phase 2 extractor with COMPLETE parameter extraction

#### Day 7: Phase 3 - Explainer Iframe Extractor
**Developer Tasks:**
- [ ] Implement ExplainerIframeExtractor class
- [ ] Extract text sections
- [ ] Extract and download images
- [ ] Extract video embeds
- [ ] Write unit tests

**Deliverable:** Working Phase 3 extractor

---

### Sprint 2: Integration & Optimization (Days 8-14)

#### Day 8-9: Orchestrator & Full Pipeline
**Developer Tasks:**
- [ ] Implement main ScraperOrchestrator class
- [ ] Integrate all three extractors
- [ ] Add retry logic with exponential backoff
- [ ] Implement rate limiting (2 requests/second)
- [ ] Add progress tracking
- [ ] Add resume capability

**Deliverable:** Complete end-to-end scraper

#### Day 10: Multimodal Processing
**Developer Tasks:**
- [ ] Implement image downloader
- [ ] Integrate Tesseract OCR
- [ ] Implement YouTube transcript fetcher
- [ ] Create text aggregator
- [ ] Write unit tests

**Deliverable:** Multimodal content processor

#### Day 11: Data Validation & Quality
**Developer Tasks:**
- [ ] Implement workflow JSON validator
- [ ] Implement data completeness validator
- [ ] Create quality metrics calculator
- [ ] Generate validation reports
- [ ] Write unit tests

**Deliverable:** Data validation system

#### Day 12: Export Formats
**Developer Tasks:**
- [ ] Implement JSON exporter (complete dataset)
- [ ] Implement JSONL exporter (training format)
- [ ] Implement CSV exporter (metadata only)
- [ ] Implement SQLite exporter (queryable)
- [ ] Write unit tests

**Deliverable:** Multiple export formats

#### Day 13: Full Scrape Test Run
**Developer Tasks:**
- [ ] Prepare sitemap URLs (2,100 workflows)
- [ ] Run scraper on 50-100 workflows
- [ ] Monitor for errors and edge cases
- [ ] Fix bugs discovered
- [ ] Optimize performance
- [ ] Document manual interventions

**Deliverable:** Tested scraper on real data

#### Day 14: Documentation & Handoff
**Developer Tasks:**
- [ ] Write comprehensive README
- [ ] Document CLI commands
- [ ] Create dataset schema documentation
- [ ] Write troubleshooting guide
- [ ] Create usage examples
- [ ] Prepare handoff presentation

**Deliverable:** Production-ready project

---

## 🎯 CLI INTERFACE DESIGN

### Main Commands

```bash
# Test connection
n8n-scraper test-connection

# Scrape single workflow (all phases)
n8n-scraper scrape-workflow <URL> [--output <path>]

# Scrape multiple workflows
n8n-scraper scrape-batch --urls-file <file> [--concurrency <n>]

# Scrape from sitemap
n8n-scraper scrape-sitemap [--limit <n>] [--offset <n>]

# Extract specific phase
n8n-scraper extract-page <URL>
n8n-scraper extract-workflow <URL>
n8n-scraper extract-explainer <URL>

# Process media
n8n-scraper process-media --workflow-id <id>

# Validate data
n8n-scraper validate [--workflow-id <id>]

# Export dataset
n8n-scraper export --format <json|jsonl|csv|sqlite> --output <path>

# Show statistics
n8n-scraper stats [--verbose]

# Resume interrupted scrape
n8n-scraper resume [--from-checkpoint <path>]
```

### Configuration File

```yaml
# config.yaml
scraper:
  rate_limit: 2  # requests per second
  timeout: 30    # seconds
  retries: 3
  concurrency: 2  # parallel browsers

storage:
  base_dir: ./data
  workflows_dir: ./data/workflows
  images_dir: ./data/images
  transcripts_dir: ./data/transcripts

browser:
  headless: true
  browser_type: chromium
  viewport_width: 1920
  viewport_height: 1080

ocr:
  enabled: true
  language: eng
  dpi: 300

videos:
  download_transcripts: true
  fallback_to_autogenerated: true
```

---

## 📦 DEPENDENCIES

```toml
# pyproject.toml
[tool.poetry.dependencies]
python = "^3.11"
playwright = "^1.40.0"
aiohttp = "^3.9.0"
click = "^8.1.0"
structlog = "^24.1.0"
pydantic = "^2.5.0"
pytesseract = "^0.3.10"
Pillow = "^10.0.0"
youtube-transcript-api = "^0.6.1"
yt-dlp = "^2023.11.16"
beautifulsoup4 = "^4.12.0"
lxml = "^5.0.0"
tqdm = "^4.66.0"
pyyaml = "^6.0"
sqlalchemy = "^2.0.0"

[tool.poetry.dev-dependencies]
pytest = "^7.4.0"
pytest-asyncio = "^0.21.0"
pytest-cov = "^4.1.0"
black = "^23.12.0"
mypy = "^1.7.0"
pylint = "^3.0.0"
```

---

## 📊 SUCCESS METRICS

### Development Metrics
- **Test Coverage:** >80%
- **Code Quality:** Pylint score >8.0
- **Type Coverage:** 100% (using mypy)
- **Documentation:** All public APIs documented

### Scraping Metrics
- **Success Rate:** >95% of workflows successfully scraped
- **Data Completeness:** >90% of required fields populated
- **Parameter Coverage:** 100% of configured parameters extracted
- **Connection Coverage:** 100% of node connections mapped
- **Performance:** <45 seconds per workflow (average)

### Dataset Quality
- **Total Workflows:** 2,000+ complete workflows
- **Complete Parameters:** Every node parameter with values
- **Complete Connections:** All node-to-node connections
- **Complete Context:** Natural language descriptions
- **Multimodal Content:** Images, videos, transcripts

---

## 🚨 RISK ASSESSMENT

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| **n8n.io changes HTML** | High | Medium | Flexible selectors, fallbacks |
| **Rate limiting** | High | Low | Exponential backoff, respect robots.txt |
| **JS rendering issues** | Medium | Medium | Playwright with wait strategies |
| **Incomplete parameters** | High | Low | Multiple extraction methods |
| **Storage constraints** | Medium | Low | ~50GB for full dataset |

---

## ✅ FINAL ACCEPTANCE CRITERIA

### Must Have
✅ Scraper extracts 2,000+ workflows  
✅ ALL node parameters captured (100% coverage)  
✅ ALL connections mapped completely  
✅ Context and explanations included  
✅ Multimodal content captured  
✅ Multiple export formats  
✅ 95%+ success rate  
✅ Complete documentation  

### Data Completeness Guarantee
✅ Every node has ALL configured parameters  
✅ Every parameter has value, type, and context  
✅ Every connection is mapped with type  
✅ Every expression is captured and explained  
✅ Every credential reference is documented  

---

## 🎓 DELIVERABLES

1. **Complete Scraper** - Production-ready code
2. **Dataset** - 2,000+ workflows with complete data
3. **Documentation** - README, API docs, examples
4. **Quality Report** - Metrics and validation results
5. **Training Data** - JSONL format ready for ML

---

**This project will provide COMPLETE workflow data including every parameter, connection, and contextual detail needed for training your NL → workflow AI model.** 🚀