# Dataset Schema Documentation v1.0.0

**Version:** 1.0.0  
**Date:** October 9, 2025  
**Project:** n8n Workflow Dataset Scraper  
**Purpose:** Complete data structure specification for training dataset

---

## 📋 TABLE OF CONTENTS

1. [Schema Overview](#schema-overview)
2. [Core Interfaces](#core-interfaces)
3. [Metadata Structures](#metadata-structures)
4. [Workflow Content](#workflow-content)
5. [Node Configuration](#node-configuration)
6. [Explainer Content](#explainer-content)
7. [Multimodal Content](#multimodal-content)
8. [Validation Rules](#validation-rules)
9. [Quality Metrics](#quality-metrics)
10. [Export Formats](#export-formats)
11. [Complete Examples](#complete-examples)

---

## 🎯 SCHEMA OVERVIEW

### Purpose
This schema defines the complete structure of scraped n8n workflow data, ensuring:
- **Completeness:** Every parameter, connection, and context captured
- **Consistency:** Uniform structure across all workflows
- **Trainability:** Optimized for AI model training
- **Queryability:** Structured for database storage and analysis

### Design Principles
1. **Flat where possible, nested where necessary**
2. **Every field has explicit type and constraints**
3. **Optional fields marked clearly**
4. **Examples provided for every structure**
5. **Validation rules embedded**

---

## 🔧 CORE INTERFACES

### WorkflowData

The root interface representing a complete scraped workflow.

```typescript
interface WorkflowData {
  // Identification
  id: string;                           // Workflow ID from URL
  url: string;                          // Full workflow URL
  scraped_at: string;                   // ISO 8601 timestamp
  scraper_version: string;              // Version of scraper used
  
  // Core Data Layers
  basic_metadata: BasicMetadata;        // Layer 1: Page data
  workflow_content: WorkflowContent;    // Layer 2: Workflow JSON
  explainer_content: ExplainerContent;  // Layer 3: Tutorials
  
  // Quality Metrics
  extraction_quality: {
    completeness_score: number;         // 0-100%
    missing_fields: string[];           // List of missing data
    has_errors: boolean;                // Extraction errors occurred
    error_messages?: string[];          // Error details if any
  };
  
  // Processing Status
  processing_status: {
    page_extracted: boolean;
    workflow_extracted: boolean;
    explainer_extracted: boolean;
    media_downloaded: boolean;
    validation_passed: boolean;
  };
}
```

**Constraints:**
- `id`: Required, must match URL pattern
- `url`: Required, valid n8n.io URL
- `scraped_at`: Required, ISO 8601 format
- `completeness_score`: 0-100, target ≥95

---

## 📊 METADATA STRUCTURES

### BasicMetadata

```typescript
interface BasicMetadata {
  title: string;                        // Workflow title
  author?: string;                      // Creator name if available
  created_date?: string;                // ISO 8601 date
  last_updated?: string;                // ISO 8601 date
  description?: string;                 // Short description
  
  // Categorization
  categories: Category[];               // Primary & secondary categories
  node_tags: NodeTag[];                 // Node/integration badges
  tags: string[];                       // General keywords
  
  // Taxonomy
  taxonomy: {
    domain?: string;                    // e.g., "Personal", "Business"
    function?: string;                  // e.g., "Automation", "Integration"
    target_user?: string[];             // e.g., ["Developer", "Business User"]
    difficulty?: "beginner" | "intermediate" | "advanced";
    technical_level?: "no-code" | "low-code" | "pro-code";
    uses_ai?: boolean;
    uses_voice?: boolean;
    uses_webhooks?: boolean;
    integration_categories?: string[];  // e.g., ["AI & ML", "Communication"]
  };
  
  // Engagement Metrics
  metrics?: {
    views?: number;
    upvotes?: number;
    downvotes?: number;
    comments?: number;
    forks?: number;
  };
  
  // Setup Requirements
  setup_instructions?: SetupInstructions;
}
```

### Category

```typescript
interface Category {
  id: string;                           // e.g., "personal-productivity"
  name: string;                         // Display name
  type: "primary" | "secondary";        // Visual hierarchy
  slug?: string;                        // URL-friendly version
}
```

**Example:**
```json
{
  "id": "personal-productivity",
  "name": "Personal Productivity",
  "type": "primary",
  "slug": "personal-productivity"
}
```

### NodeTag

```typescript
interface NodeTag {
  id: string;                           // Node identifier
  display_name: string;                 // Human-readable name
  node_type?: string;                   // n8n node type (e.g., "n8n-nodes-base.telegram")
  icon_url?: string;                    // Node icon URL
  color?: string;                       // Badge color
  is_trigger: boolean;                  // Whether this is a trigger node
  node_url?: string;                    // Link to node documentation
}
```

**Example:**
```json
{
  "id": "telegram-trigger",
  "display_name": "Telegram Trigger",
  "node_type": "n8n-nodes-base.telegramTrigger",
  "icon_url": "https://n8n.io/icons/telegram.svg",
  "color": "#0088cc",
  "is_trigger": true,
  "node_url": "https://n8n.io/integrations/telegram-trigger/"
}
```

### SetupInstructions

```typescript
interface SetupInstructions {
  requirements_text: string;            // Full requirements text
  services_needed: ServiceRequirement[]; // Parsed services
  setup_steps: SetupStep[];             // Step-by-step instructions
}

interface ServiceRequirement {
  service: string;                      // Service name (e.g., "Telegram")
  count: number;                        // How many credentials needed
  credential_type?: string;             // Type of credential required
}

interface SetupStep {
  step_number: number;                  // Sequential step number
  service: string;                      // Which service
  instructions: string;                 // Step instructions
  nodes_affected?: string[];            // Which nodes use this credential
  button_text?: string;                 // UI button text
  is_optional?: boolean;                // Whether step is optional
}
```

**Example:**
```json
{
  "requirements_text": "You need 1x Telegram, 1x OpenAI, 1x Gmail Tool",
  "services_needed": [
    {"service": "Telegram", "count": 1, "credential_type": "telegram_api"},
    {"service": "OpenAI", "count": 1, "credential_type": "openai_api"},
    {"service": "Gmail Tool", "count": 1, "credential_type": "google_oauth2"}
  ],
  "setup_steps": [
    {
      "step_number": 1,
      "service": "Telegram",
      "instructions": "The credential you select will be used in the Telegram Trigger and Send Message nodes.",
      "nodes_affected": ["Telegram Trigger", "Send Message to Telegram"],
      "button_text": "Select Telegram credential",
      "is_optional": false
    },
    {
      "step_number": 2,
      "service": "OpenAI",
      "instructions": "Select your OpenAI API key for AI-powered responses.",
      "nodes_affected": ["OpenAI Chat Model"],
      "button_text": "Select OpenAI credential",
      "is_optional": false
    }
  ]
}
```

---

## 🔄 WORKFLOW CONTENT

### WorkflowContent

```typescript
interface WorkflowContent {
  // Raw n8n Workflow JSON
  workflow_json: N8nWorkflowJSON;       // Complete workflow structure
  
  // Parsed Components
  nodes: NodeConfiguration[];           // All nodes with configs
  connections: ConnectionMap;           // Node connection graph
  
  // Visual Layout
  layout: {
    canvas_width?: number;
    canvas_height?: number;
    zoom_level?: number;
  };
  
  // Workflow Metadata
  workflow_metadata: {
    node_count: number;
    connection_count: number;
    trigger_count: number;
    has_error_handling: boolean;
    has_conditional_logic: boolean;
    has_loops: boolean;
    complexity_score?: number;          // Calculated complexity
  };
  
  // Extracted Patterns
  patterns: {
    node_sequence: string[];            // Ordered node types
    common_patterns?: string[];         // Identified patterns
    data_transformations?: string[];    // Data manipulation steps
  };
}
```

### N8nWorkflowJSON

```typescript
interface N8nWorkflowJSON {
  name: string;                         // Workflow name
  nodes: N8nNode[];                     // Array of nodes
  connections: N8nConnections;          // Connection map
  active?: boolean;                     // Whether workflow is active
  settings?: {
    executionOrder?: "v0" | "v1";
    saveDataErrorExecution?: "all" | "none";
    saveDataSuccessExecution?: "all" | "none";
    saveManualExecutions?: boolean;
    callerPolicy?: string;
    errorWorkflow?: string;
  };
  staticData?: Record<string, any>;    // Workflow static data
  tags?: string[];                      // Workflow tags
  pinData?: Record<string, any>;        // Pinned test data
  versionId?: string;                   // Workflow version
}
```

### ConnectionMap

```typescript
interface ConnectionMap {
  [sourceNodeName: string]: {
    [outputType: string]: Array<Array<Connection>>;
  };
}

interface Connection {
  node: string;                         // Target node name
  type: string;                         // Connection type (main/error)
  index: number;                        // Input index on target
}
```

**Example:**
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
            "node": "OpenAI Chat",
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

---

## ⚙️ NODE CONFIGURATION

### NodeConfiguration

```typescript
interface NodeConfiguration {
  // Identity
  id: string;                           // Unique node ID
  name: string;                         // Node name in workflow
  type: string;                         // n8n node type
  typeVersion: number;                  // Node type version
  
  // Position
  position: [number, number];           // [x, y] coordinates
  
  // Configuration
  parameters: Record<string, any>;      // All node parameters
  credentials?: Record<string, CredentialReference>;
  
  // Behavior
  disabled?: boolean;                   // Whether node is disabled
  notes?: string;                       // Node documentation
  notesInFlow?: boolean;                // Show notes in canvas
  
  // Error Handling
  continueOnFail?: boolean;             // Continue on error
  retryOnFail?: boolean;                // Retry on failure
  maxTries?: number;                    // Max retry attempts
  waitBetween?: number;                 // Wait between retries (ms)
  
  // Execution
  alwaysOutputData?: boolean;           // Always output data
  executeOnce?: boolean;                // Execute only once
  
  // Metadata
  node_metadata: {
    is_trigger: boolean;
    is_credential_required: boolean;
    operation?: string;                 // Selected operation
    resource?: string;                  // Selected resource
    has_expressions: boolean;           // Uses expressions
    expression_count?: number;          // Number of expressions
  };
}
```

### CredentialReference

```typescript
interface CredentialReference {
  id: string;                           // Credential ID
  name: string;                         // Credential name
}
```

### Complete Node Example

```json
{
  "id": "a1b2c3d4-e5f6-7890",
  "name": "Send Telegram Message",
  "type": "n8n-nodes-base.telegram",
  "typeVersion": 1.1,
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
          [
            {
              "text": "Track Order",
              "url": "https://example.com/track/{{ $json.orderId }}"
            }
          ]
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
  
  "notes": "Sends order confirmation to customer via Telegram with tracking link",
  "notesInFlow": true,
  "continueOnFail": false,
  "retryOnFail": true,
  "maxTries": 3,
  "waitBetween": 1000,
  
  "node_metadata": {
    "is_trigger": false,
    "is_credential_required": true,
    "operation": "sendMessage",
    "resource": "message",
    "has_expressions": true,
    "expression_count": 3
  }
}
```

---

## 📚 EXPLAINER CONTENT

### ExplainerContent

```typescript
interface ExplainerContent {
  // Text Content
  introduction?: string;                // Workflow introduction
  sections: ExplainerSection[];         // Tutorial sections
  full_text: string;                    // Complete aggregated text
  
  // Multimodal Content
  images: ImageContent[];               // All images
  videos: VideoContent[];               // All videos
  code_snippets: CodeSnippet[];         // Code examples
  
  // Metadata
  content_metadata: {
    total_sections: number;
    total_images: number;
    total_videos: number;
    total_code_snippets: number;
    has_setup_guide: boolean;
    has_troubleshooting: boolean;
    estimated_read_time_minutes?: number;
  };
}
```

### ExplainerSection

```typescript
interface ExplainerSection {
  section_number: number;               // Sequential section number
  heading: string;                      // Section title
  content: string;                      // Section text content
  subsections?: ExplainerSection[];     // Nested subsections
  images?: string[];                    // Image IDs in this section
  videos?: string[];                    // Video IDs in this section
  code_snippets?: string[];             // Code snippet IDs
}
```

**Example:**
```json
{
  "section_number": 1,
  "heading": "Setting Up Your Telegram Bot",
  "content": "To use this workflow, you'll need to create a Telegram bot using BotFather...",
  "subsections": [
    {
      "section_number": 1.1,
      "heading": "Creating the Bot",
      "content": "Open Telegram and search for @BotFather...",
      "images": ["img_001"]
    }
  ]
}
```

---

## 🎨 MULTIMODAL CONTENT

### ImageContent

```typescript
interface ImageContent {
  id: string;                           // Unique image ID
  original_url: string;                 // Source URL
  local_path: string;                   // Downloaded file path
  alt_text?: string;                    // Alt text if available
  caption?: string;                     // Image caption
  
  // OCR Results
  ocr_text?: string;                    // Extracted text from image
  ocr_confidence?: number;              // OCR confidence score
  
  // Image Metadata
  metadata: {
    width?: number;
    height?: number;
    format?: string;                    // e.g., "png", "jpg"
    file_size?: number;                 // Bytes
  };
  
  // Context
  context: {
    section_id?: string;                // Which section contains this
    purpose?: string;                   // e.g., "screenshot", "diagram", "icon"
  };
}
```

**Example:**
```json
{
  "id": "img_001",
  "original_url": "https://n8n.io/images/workflows/2462/setup.png",
  "local_path": "./media/images/2462_setup.png",
  "alt_text": "Telegram bot setup screen",
  "caption": "BotFather conversation showing bot creation",
  
  "ocr_text": "BotFather: Alright, a new bot. How are we going to call it? Please choose a name for your bot.\nYou: MyAssistantBot",
  "ocr_confidence": 0.94,
  
  "metadata": {
    "width": 1200,
    "height": 800,
    "format": "png",
    "file_size": 245678
  },
  
  "context": {
    "section_id": "1.1",
    "purpose": "screenshot"
  }
}
```

### VideoContent

```typescript
interface VideoContent {
  id: string;                           // Unique video ID
  platform: "youtube" | "vimeo" | "other";
  video_id: string;                     // Platform video ID
  url: string;                          // Full video URL
  embed_url?: string;                   // Embed URL
  
  // Video Metadata
  title?: string;
  duration_seconds?: number;
  thumbnail_url?: string;
  
  // Transcript
  transcript?: VideoTranscript;
  
  // Context
  context: {
    section_id?: string;
    purpose?: string;                   // e.g., "tutorial", "demo"
  };
}

interface VideoTranscript {
  full_text: string;                    // Complete transcript
  segments?: TranscriptSegment[];       // Timestamped segments
  language?: string;
  auto_generated: boolean;
}

interface TranscriptSegment {
  start_time: number;                   // Seconds
  end_time: number;                     // Seconds
  text: string;                         // Segment text
}
```

**Example:**
```json
{
  "id": "vid_001",
  "platform": "youtube",
  "video_id": "dQw4w9WgXcQ",
  "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
  "embed_url": "https://www.youtube.com/embed/dQw4w9WgXcQ",
  
  "title": "How to Set Up Telegram Bot for n8n",
  "duration_seconds": 180,
  "thumbnail_url": "https://img.youtube.com/vi/dQw4w9WgXcQ/maxresdefault.jpg",
  
  "transcript": {
    "full_text": "In this video, I'll show you how to create a Telegram bot...",
    "segments": [
      {
        "start_time": 0,
        "end_time": 5,
        "text": "In this video, I'll show you how to create a Telegram bot"
      },
      {
        "start_time": 5,
        "end_time": 12,
        "text": "First, open Telegram and search for BotFather"
      }
    ],
    "language": "en",
    "auto_generated": false
  },
  
  "context": {
    "section_id": "1",
    "purpose": "tutorial"
  }
}
```

### CodeSnippet

```typescript
interface CodeSnippet {
  id: string;                           // Unique snippet ID
  language?: string;                    // Programming language
  code: string;                         // Code content
  description?: string;                 // What the code does
  
  // Context
  context: {
    section_id?: string;
    node_name?: string;                 // Related node if applicable
    purpose?: string;                   // e.g., "expression", "function", "example"
  };
}
```

**Example:**
```json
{
  "id": "code_001",
  "language": "javascript",
  "code": "return items.map(item => ({\n  json: {\n    userId: item.json.from.id,\n    message: item.json.text\n  }\n}));",
  "description": "Transform Telegram message data for processing",
  
  "context": {
    "section_id": "2.3",
    "node_name": "Process Message",
    "purpose": "expression"
  }
}
```

---

## ✅ VALIDATION RULES

### Field Validation

```typescript
interface ValidationRules {
  // Required Fields
  required: {
    id: "must be non-empty string",
    url: "must be valid n8n.io URL",
    scraped_at: "must be ISO 8601 timestamp",
    basic_metadata: {
      title: "must be non-empty string",
      categories: "must have at least 1 category"
    },
    workflow_content: {
      workflow_json: "must be valid n8n JSON",
      nodes: "must have at least 1 node"
    }
  };
  
  // Optional But Recommended
  recommended: {
    basic_metadata: {
      description: "workflow description",
      tags: "at least 3 tags",
      setup_instructions: "if credentials required"
    },
    explainer_content: {
      introduction: "workflow overview",
      sections: "at least 1 tutorial section"
    }
  };
  
  // Format Validation
  formats: {
    url: "^https://n8n\\.io/workflows/[0-9]+",
    iso_timestamp: "^\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}",
    email: "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$"
  };
  
  // Range Validation
  ranges: {
    completeness_score: "0-100",
    upvotes: "≥0",
    downvotes: "≥0",
    node_count: "≥1"
  };
}
```

### Quality Checks

```typescript
interface QualityChecks {
  // Completeness Checks
  has_workflow_json: boolean;           // Core workflow data present
  has_all_nodes: boolean;               // All nodes extracted
  has_connections: boolean;             // Connection data present
  has_parameters: boolean;              // Node parameters captured
  has_explainer: boolean;               // Tutorial content present
  has_media: boolean;                   // Images/videos downloaded
  
  // Data Quality Checks
  nodes_match_json: boolean;            // Parsed nodes match JSON
  connections_valid: boolean;           // All connections reference valid nodes
  parameters_complete: boolean;         // No missing parameter values
  credentials_identified: boolean;      // Credential requirements found
  
  // Content Quality Checks
  text_length_adequate: boolean;        // Enough text content (>100 chars)
  images_downloaded: boolean;           // All images successfully saved
  videos_processed: boolean;            // Video transcripts extracted
  ocr_completed: boolean;               // OCR performed on images
}
```

---

## 📊 QUALITY METRICS

### CompletenessScore Calculation

```typescript
function calculateCompletenessScore(workflow: WorkflowData): number {
  const weights = {
    has_workflow_json: 30,              // Critical
    has_all_parameters: 20,             // Critical
    has_connections: 15,                // Important
    has_explainer_text: 10,             // Important
    has_setup_instructions: 10,         // Important
    has_images: 5,                      // Nice to have
    has_videos: 5,                      // Nice to have
    has_ocr_text: 5                     // Nice to have
  };
  
  let score = 0;
  
  // Calculate based on presence
  if (workflow.workflow_content.workflow_json) score += weights.has_workflow_json;
  if (allParametersCaptured(workflow)) score += weights.has_all_parameters;
  if (workflow.workflow_content.connections) score += weights.has_connections;
  if (workflow.explainer_content.full_text.length > 100) score += weights.has_explainer_text;
  if (workflow.basic_metadata.setup_instructions) score += weights.has_setup_instructions;
  if (workflow.explainer_content.images.length > 0) score += weights.has_images;
  if (workflow.explainer_content.videos.length > 0) score += weights.has_videos;
  if (hasOcrText(workflow)) score += weights.has_ocr_text;
  
  return score; // 0-100
}
```

### Dataset Quality Metrics

```typescript
interface DatasetMetrics {
  // Extraction Success
  total_workflows: number;
  successful_extractions: number;
  failed_extractions: number;
  success_rate: number;                 // Percentage
  
  // Completeness Distribution
  completeness_distribution: {
    "90-100%": number;                  // Target: >95%
    "80-89%": number;
    "70-79%": number;
    "below-70%": number;
  };
  
  // Content Statistics
  avg_nodes_per_workflow: number;
  avg_parameters_per_node: number;
  avg_text_length: number;
  avg_images_per_workflow: number;
  avg_videos_per_workflow: number;
  
  // Quality Indicators
  workflows_with_setup: number;
  workflows_with_explainer: number;
  workflows_with_media: number;
  workflows_with_ocr: number;
  
  // Category Distribution
  category_breakdown: Record<string, number>;
  node_type_frequency: Record<string, number>;
}
```

---

## 📤 EXPORT FORMATS

### JSON Format (Complete)

```json
{
  "dataset_metadata": {
    "version": "1.0.0",
    "created_at": "2025-01-20T10:00:00Z",
    "total_workflows": 2100,
    "scraper_version": "1.0.0"
  },
  "workflows": [
    {
      "id": "2462",
      "url": "https://n8n.io/workflows/2462",
      "basic_metadata": { /* ... */ },
      "workflow_content": { /* ... */ },
      "explainer_content": { /* ... */ },
      "extraction_quality": { /* ... */ }
    }
  ]
}
```

### JSONL Format (Training-Optimized)

Each line is a complete workflow (newline-delimited):

```jsonl
{"id":"2462","title":"Telegram AI Assistant","workflow_json":{...},"explainer_text":"..."}
{"id":"8237","title":"Slack Automation","workflow_json":{...},"explainer_text":"..."}
```

### CSV Format (Metadata Summary)

```csv
id,title,url,category,node_count,has_explainer,completeness_score,scraped_at
2462,"Telegram AI Assistant",https://n8n.io/workflows/2462,"Personal Productivity",8,true,98,2025-01-20T10:00:00Z
8237,"Slack Automation",https://n8n.io/workflows/8237,"Communication",5,true,95,2025-01-20T10:05:00Z
```

### SQLite Schema

```sql
-- Workflows Table
CREATE TABLE workflows (
  id TEXT PRIMARY KEY,
  url TEXT UNIQUE NOT NULL,
  title TEXT NOT NULL,
  description TEXT,
  scraped_at TIMESTAMP NOT NULL,
  completeness_score INTEGER,
  workflow_json TEXT,  -- JSON as text
  full_text TEXT
);

-- Nodes Table
CREATE TABLE nodes (
  id TEXT PRIMARY KEY,
  workflow_id TEXT,
  name TEXT,
  type TEXT,
  parameters TEXT,  -- JSON as text
  FOREIGN KEY (workflow_id) REFERENCES workflows(id)
);

-- Categories Table
CREATE TABLE workflow_categories (
  workflow_id TEXT,
  category_id TEXT,
  category_name TEXT,
  category_type TEXT,
  PRIMARY KEY (workflow_id, category_id),
  FOREIGN KEY (workflow_id) REFERENCES workflows(id)
);

-- Media Table
CREATE TABLE media (
  id TEXT PRIMARY KEY,
  workflow_id TEXT,
  type TEXT,  -- 'image' or 'video'
  url TEXT,
  local_path TEXT,
  ocr_text TEXT,
  FOREIGN KEY (workflow_id) REFERENCES workflows(id)
);
```

---

## 📋 COMPLETE EXAMPLES

### Minimal Valid Workflow

```json
{
  "id": "123",
  "url": "https://n8n.io/workflows/123",
  "scraped_at": "2025-01-20T10:00:00Z",
  "scraper_version": "1.0.0",
  
  "basic_metadata": {
    "title": "Simple HTTP Request",
    "categories": [
      {"id": "automation", "name": "Automation", "type": "primary"}
    ],
    "node_tags": [],
    "tags": ["http", "api"],
    "taxonomy": {}
  },
  
  "workflow_content": {
    "workflow_json": {
      "name": "Simple HTTP Request",
      "nodes": [
        {
          "id": "node1",
          "name": "HTTP Request",
          "type": "n8n-nodes-base.httpRequest",
          "typeVersion": 1,
          "position": [250, 300],
          "parameters": {
            "url": "https://api.example.com/data",
            "method": "GET"
          }
        }
      ],
      "connections": {}
    },
    "nodes": [
      {
        "id": "node1",
        "name": "HTTP Request",
        "type": "n8n-nodes-base.httpRequest",
        "typeVersion": 1,
        "position": [250, 300],
        "parameters": {
          "url": "https://api.example.com/data",
          "method": "GET"
        },
        "node_metadata": {
          "is_trigger": false,
          "is_credential_required": false,
          "has_expressions": false
        }
      }
    ],
    "connections": {},
    "layout": {},
    "workflow_metadata": {
      "node_count": 1,
      "connection_count": 0,
      "trigger_count": 0,
      "has_error_handling": false,
      "has_conditional_logic": false,
      "has_loops": false
    },
    "patterns": {
      "node_sequence": ["n8n-nodes-base.httpRequest"]
    }
  },
  
  "explainer_content": {
    "full_text": "A simple workflow that makes an HTTP request.",
    "sections": [],
    "images": [],
    "videos": [],
    "code_snippets": [],
    "content_metadata": {
      "total_sections": 0,
      "total_images": 0,
      "total_videos": 0,
      "total_code_snippets": 0,
      "has_setup_guide": false,
      "has_troubleshooting": false
    }
  },
  
  "extraction_quality": {
    "completeness_score": 75,
    "missing_fields": ["setup_instructions", "explainer_sections"],
    "has_errors": false
  },
  
  "processing_status": {
    "page_extracted": true,
    "workflow_extracted": true,
    "explainer_extracted": true,
    "media_downloaded": true,
    "validation_passed": true
  }
}
```

### Complete Rich Workflow (Excerpt)

```json
{
  "id": "2462",
  "url": "https://n8n.io/workflows/2462",
  "scraped_at": "2025-01-20T10:00:00Z",
  "scraper_version": "1.0.0",
  
  "basic_metadata": {
    "title": "Angie, Personal AI Assistant with Telegram Voice and Text",
    "author": "n8n Team",
    "created_date": "2024-06-15",
    "description": "A personal AI assistant that responds to Telegram messages using OpenAI",
    
    "categories": [
      {"id": "personal-productivity", "name": "Personal Productivity", "type": "primary"},
      {"id": "ai-chatbot", "name": "AI Chatbot", "type": "secondary"}
    ],
    
    "node_tags": [
      {
        "id": "telegram-trigger",
        "display_name": "Telegram Trigger",
        "node_type": "n8n-nodes-base.telegramTrigger",
        "is_trigger": true,
        "node_url": "https://n8n.io/integrations/telegram-trigger/"
      },
      {
        "id": "openai",
        "display_name": "OpenAI",
        "node_type": "n8n-nodes-base.openai",
        "is_trigger": false,
        "node_url": "https://n8n.io/integrations/openai/"
      }
    ],
    
    "tags": ["ai", "telegram", "assistant", "voice", "gpt"],
    
    "taxonomy": {
      "domain": "Personal",
      "function": "Automation",
      "target_user": ["Personal User", "Small Business"],
      "difficulty": "intermediate",
      "technical_level": "low-code",
      "uses_ai": true,
      "uses_voice": true,
      "uses_webhooks": true,
      "integration_categories": ["AI & ML", "Communication"]
    },
    
    "metrics": {
      "views": 15420,
      "upvotes": 287,
      "downvotes": 12,
      "comments": 43,
      "forks": 156
    },
    
    "setup_instructions": {
      "requirements_text": "You need 1x Telegram, 1x OpenAI, 1x Gmail Tool",
      "services_needed": [
        {"service": "Telegram", "count": 1, "credential_type": "telegram_api"},
        {"service": "OpenAI", "count": 1, "credential_type": "openai_api"}
      ],
      "setup_steps": [
        {
          "step_number": 1,
          "service": "Telegram",
          "instructions": "Create a bot using @BotFather and get your API token",
          "nodes_affected": ["Telegram Trigger", "Send Message"],
          "button_text": "Select Telegram credential"
        }
      ]
    }
  },
  
  "workflow_content": {
    "workflow_json": {
      "name": "Angie AI Assistant",
      "nodes": [
        /* Complete node array */
      ],
      "connections": {
        /* Connection map */
      }
    },
    "nodes": [
      /* Parsed nodes with full parameters */
    ],
    "connections": {
      /* Structured connection graph */
    },
    "workflow_metadata": {
      "node_count": 8,
      "connection_count": 7,
      "trigger_count": 1,
      "has_error_handling": true,
      "has_conditional_logic": true,
      "has_loops": false,
      "complexity_score": 42
    }
  },
  
  "explainer_content": {
    "introduction": "Build your own AI assistant that responds to Telegram messages...",
    "sections": [
      {
        "section_number": 1,
        "heading": "Setting Up Telegram Bot",
        "content": "First, you'll need to create a Telegram bot...",
        "images": ["img_001", "img_002"],
        "videos": ["vid_001"]
      }
    ],
    "full_text": "Build your own AI assistant...",
    "images": [
      {
        "id": "img_001",
        "original_url": "https://n8n.io/images/...",
        "local_path": "./media/images/2462_setup.png",
        "ocr_text": "BotFather conversation...",
        "ocr_confidence": 0.94
      }
    ],
    "videos": [
      {
        "id": "vid_001",
        "platform": "youtube",
        "video_id": "abc123",
        "transcript": {
          "full_text": "In this tutorial...",
          "segments": [/* Timestamped segments */]
        }
      }
    ],
    "content_metadata": {
      "total_sections": 5,
      "total_images": 8,
      "total_videos": 2,
      "total_code_snippets": 3,
      "has_setup_guide": true,
      "has_troubleshooting": true,
      "estimated_read_time_minutes": 12
    }
  },
  
  "extraction_quality": {
    "completeness_score": 98,
    "missing_fields": [],
    "has_errors": false
  },
  
  "processing_status": {
    "page_extracted": true,
    "workflow_extracted": true,
    "explainer_extracted": true,
    "media_downloaded": true,
    "validation_passed": true
  }
}
```

---

## 🎯 USAGE GUIDELINES

### For Developers

1. **Validation:** Always validate against schema before export
2. **Completeness:** Aim for 95%+ completeness score
3. **Media:** Download all media, don't just reference URLs
4. **OCR:** Run OCR on all images with text
5. **Transcripts:** Extract video transcripts when available

### For Data Scientists

1. **Quality Filter:** Use workflows with completeness_score ≥ 90
2. **Categorization:** Leverage taxonomy for dataset splits
3. **Patterns:** Use node_sequence for pattern analysis
4. **Multimodal:** Combine text, images, and video for richer training
5. **Normalization:** Standardize parameter names across versions

### For Product Teams

1. **Coverage:** Track category distribution for gaps
2. **Popularity:** Use metrics for prioritization
3. **Complexity:** Use complexity_score for difficulty assessment
4. **Setup:** Use setup_instructions for UX improvements
5. **Patterns:** Identify common workflows for templates

---

## ✅ VALIDATION CHECKLIST

Before considering a workflow "complete":

- [ ] Has valid workflow JSON
- [ ] All nodes extracted with parameters
- [ ] Connections mapped correctly
- [ ] At least 1 category assigned
- [ ] Title and description present
- [ ] Setup instructions if credentials required
- [ ] Explainer text >100 characters
- [ ] Images downloaded and OCR'd
- [ ] Videos have transcripts
- [ ] Completeness score ≥90%
- [ ] Validation passed without errors
- [ ] Quality checks all green

---

**This schema ensures complete, consistent, and high-quality data for training your n8n-claude-engine AI model.** 🎯

**Version:** 1.0.0  
**Status:** Complete and Ready for Implementation  
**Next Step:** Begin scraper development with RND team