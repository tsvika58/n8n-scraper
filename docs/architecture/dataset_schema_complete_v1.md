# N8N Workflow Dataset - Complete Schema Documentation v1.0

**Version:** 1.0.0 - Complete  
**Date:** October 9, 2025  
**Purpose:** Comprehensive data structure specification for n8n workflow dataset  
**Status:** ✅ Production Ready

---

## 📋 **TABLE OF CONTENTS**

1. [Root Interface: WorkflowData](#root-interface)
2. [Layer 1: Basic Metadata](#layer-1-metadata)
3. [Layer 2: Workflow Content](#layer-2-workflow)
4. [Layer 3: Explainer Content](#layer-3-explainer)
5. [Multimodal Content](#multimodal-content)
6. [Validation Rules](#validation-rules)
7. [Quality Metrics](#quality-metrics)
8. [Export Formats](#export-formats)
9. [Complete Examples](#complete-examples)

---

## 🎯 **ROOT INTERFACE: WorkflowData**

```typescript
interface WorkflowData {
  // Identifiers
  workflow_id: string;              // Unique workflow identifier
  url: string;                      // Full n8n.io URL
  
  // Extraction metadata
  extracted_at: string;             // ISO 8601 timestamp
  extraction_version: string;       // Scraper version (e.g., "2.1.1")
  extraction_time_seconds: number;  // Time taken to extract
  
  // Three-layer data structure
  basic_metadata: BasicMetadata;    // Layer 1: Page metadata
  workflow_content: WorkflowContent;// Layer 2: Workflow JSON
  explainer_content?: ExplainerContent; // Layer 3: Tutorial content (optional)
  
  // Quality scoring
  completeness_score: number;       // 0-100 score
  quality_metrics: QualityMetrics;  // Detailed quality data
}
```

---

## 📊 **LAYER 1: BASIC METADATA**

### **BasicMetadata Interface**

```typescript
interface BasicMetadata {
  // Core information
  title: string;                    // Workflow title
  description?: string;             // Short description
  author?: string;                  // Creator username
  
  // Categorization
  categories: Category[];           // Primary and secondary categories
  node_tags: NodeTag[];            // Integration badges
  tags: string[];                  // General tags
  
  // Setup and engagement
  setup_instructions?: SetupInstructions;
  engagement_metrics?: EngagementMetrics;
  
  // Timestamps
  published_at?: string;           // Publication date (ISO 8601)
  updated_at?: string;             // Last update date (ISO 8601)
}
```

### **Category Interface**

```typescript
interface Category {
  name: string;                    // Category name
  type: 'primary' | 'secondary';   // Category type
  slug?: string;                   // URL-friendly slug
}
```

**Example:**
```json
{
  "categories": [
    {
      "name": "AI",
      "type": "primary",
      "slug": "ai"
    },
    {
      "name": "Productivity",
      "type": "secondary",
      "slug": "productivity"
    }
  ]
}
```

### **NodeTag Interface**

```typescript
interface NodeTag {
  integration_name: string;        // e.g., "Telegram", "OpenAI"
  node_type: string;              // Full node type identifier
  icon_url?: string;              // Badge icon URL
  category?: string;              // Node category
}
```

**Example:**
```json
{
  "node_tags": [
    {
      "integration_name": "Telegram",
      "node_type": "n8n-nodes-base.telegram",
      "icon_url": "https://n8n.io/icons/telegram.svg",
      "category": "Communication"
    },
    {
      "integration_name": "OpenAI",
      "node_type": "n8n-nodes-base.openAi",
      "icon_url": "https://n8n.io/icons/openai.svg",
      "category": "AI"
    }
  ]
}
```

### **SetupInstructions Interface**

```typescript
interface SetupInstructions {
  sections: InstructionSection[];  // Ordered instruction sections
  prerequisites?: string[];        // Required setup items
  estimated_time?: string;         // e.g., "15 minutes"
  difficulty?: 'beginner' | 'intermediate' | 'advanced';
}

interface InstructionSection {
  heading: string;                 // Section title
  content: string;                 // Instruction text
  code_blocks?: CodeBlock[];      // Optional code snippets
  images?: string[];              // Reference to image URLs
}

interface CodeBlock {
  language: string;                // e.g., "javascript", "json"
  code: string;                    // Code content
  description?: string;            // What the code does
}
```

**Example:**
```json
{
  "setup_instructions": {
    "sections": [
      {
        "heading": "1. Create Telegram Bot",
        "content": "Open Telegram and search for @BotFather. Send /newbot and follow the prompts to create your bot. Save the bot token provided.",
        "images": ["setup-botfather.png"]
      },
      {
        "heading": "2. Configure OpenAI API",
        "content": "Get your API key from OpenAI dashboard and add it to n8n credentials.",
        "code_blocks": [
          {
            "language": "json",
            "code": "{\n  \"api_key\": \"sk-...\"\n}",
            "description": "OpenAI credentials format"
          }
        ]
      }
    ],
    "prerequisites": [
      "Telegram account",
      "OpenAI API key",
      "n8n instance (cloud or self-hosted)"
    ],
    "estimated_time": "15 minutes",
    "difficulty": "intermediate"
  }
}
```

### **EngagementMetrics Interface**

```typescript
interface EngagementMetrics {
  views?: number;                  // View count
  upvotes?: number;                // Upvote count
  downloads?: number;              // Download/use count
  comments?: number;               // Comment count
}
```

---

## ⚙️ **LAYER 2: WORKFLOW CONTENT**

### **WorkflowContent Interface**

```typescript
interface WorkflowContent {
  // Complete workflow JSON from n8n
  workflow_json: WorkflowJSON;
  
  // Parsed and structured data
  nodes: NodeConfiguration[];
  connections: ConnectionMap;
  settings?: WorkflowSettings;
  
  // Statistics
  node_count: number;
  connection_count: number;
  node_types_used: string[];
}
```

### **WorkflowJSON Interface**

```typescript
interface WorkflowJSON {
  name: string;
  nodes: N8nNode[];
  connections: N8nConnections;
  settings?: WorkflowSettings;
  staticData?: any;
  tags?: string[];
  pinData?: any;
  versionId?: string;
}

interface N8nNode {
  id: string;
  name: string;
  type: string;
  typeVersion: number;
  position: [number, number];
  parameters: Record<string, any>;
  credentials?: Record<string, CredentialReference>;
  disabled?: boolean;
  notes?: string;
  notesInFlow?: boolean;
  color?: string;
  executeOnce?: boolean;
  continueOnFail?: boolean;
  retryOnFail?: boolean;
  maxTries?: number;
  waitBetweenTries?: number;
  alwaysOutputData?: boolean;
  onError?: 'stopWorkflow' | 'continueRegularOutput' | 'continueErrorOutput';
}

interface CredentialReference {
  id: string;
  name: string;
}

interface N8nConnections {
  [sourceNodeName: string]: {
    [outputType: string]: Array<Array<{
      node: string;
      type: string;
      index: number;
    }>>;
  };
}

interface WorkflowSettings {
  executionOrder?: 'v0' | 'v1';
  saveDataErrorExecution?: 'all' | 'none';
  saveDataSuccessExecution?: 'all' | 'none';
  saveManualExecutions?: boolean;
  callerPolicy?: string;
  timezone?: string;
}
```

### **NodeConfiguration Interface**

```typescript
interface NodeConfiguration {
  // Core identification
  id: string;
  name: string;
  type: string;
  type_version: number;
  
  // Position and visual
  position: {
    x: number;
    y: number;
  };
  
  // Configuration
  parameters: ParameterValue;
  credentials?: Record<string, CredentialInfo>;
  
  // Behavior settings
  disabled?: boolean;
  notes?: string;
  execution_settings?: NodeExecutionSettings;
}

interface ParameterValue {
  [key: string]: any;  // Flexible parameter structure
}

interface CredentialInfo {
  id: string;
  name: string;
  type: string;
}

interface NodeExecutionSettings {
  continue_on_fail?: boolean;
  retry_on_fail?: boolean;
  max_tries?: number;
  wait_between_tries?: number;
  always_output_data?: boolean;
  on_error?: 'stopWorkflow' | 'continueRegularOutput' | 'continueErrorOutput';
}
```

**Example:**
```json
{
  "nodes": [
    {
      "id": "node1",
      "name": "Telegram Trigger",
      "type": "n8n-nodes-base.telegramTrigger",
      "type_version": 1,
      "position": {
        "x": 250,
        "y": 300
      },
      "parameters": {
        "updates": ["message"],
        "additionalFields": {
          "download": true
        }
      },
      "credentials": {
        "telegramApi": {
          "id": "1",
          "name": "Telegram Bot",
          "type": "telegramApi"
        }
      },
      "notes": "Listens for incoming messages",
      "execution_settings": {
        "continue_on_fail": false,
        "retry_on_fail": true,
        "max_tries": 3
      }
    }
  ]
}
```

### **ConnectionMap Interface**

```typescript
interface ConnectionMap {
  [sourceNodeName: string]: {
    outputs: NodeOutput[];
  };
}

interface NodeOutput {
  output_type: 'main' | 'error';
  output_index: number;
  connections: ConnectionTarget[];
}

interface ConnectionTarget {
  target_node: string;
  target_input_type: string;
  target_input_index: number;
}
```

**Example:**
```json
{
  "connections": {
    "Telegram Trigger": {
      "outputs": [
        {
          "output_type": "main",
          "output_index": 0,
          "connections": [
            {
              "target_node": "AI Agent",
              "target_input_type": "main",
              "target_input_index": 0
            }
          ]
        }
      ]
    },
    "AI Agent": {
      "outputs": [
        {
          "output_type": "main",
          "output_index": 0,
          "connections": [
            {
              "target_node": "Send Reply",
              "target_input_type": "main",
              "target_input_index": 0
            }
          ]
        }
      ]
    }
  }
}
```

---

## 📚 **LAYER 3: EXPLAINER CONTENT**

### **ExplainerContent Interface**

```typescript
interface ExplainerContent {
  // Natural language explanation
  introduction?: string;           // Opening paragraph
  overview?: string;               // High-level description
  
  // Structured tutorial
  tutorial_sections: TutorialSection[];
  
  // Multimodal content
  images: ImageContent[];
  videos: VideoContent[];
  code_snippets: CodeSnippet[];
  
  // Aggregated text for NLP
  full_text: string;               // All text combined
  
  // Metadata
  has_explainer: boolean;          // True if iframe content exists
  extraction_success: boolean;     // True if extraction successful
}
```

### **TutorialSection Interface**

```typescript
interface TutorialSection {
  heading: string;                 // Section title
  level: number;                   // Heading level (1-6)
  content: string;                 // Section text content
  subsections?: TutorialSection[]; // Nested sections
  images?: string[];               // References to image IDs
  videos?: string[];               // References to video IDs
  code_blocks?: string[];          // References to code snippet IDs
}
```

**Example:**
```json
{
  "tutorial_sections": [
    {
      "heading": "How It Works",
      "level": 2,
      "content": "This workflow creates a personal AI assistant named Angie that operates through Telegram. Angie can summarize daily emails, look up calendar entries, remind users of upcoming tasks, and retrieve contact information.",
      "images": ["img_001", "img_002"],
      "subsections": [
        {
          "heading": "Message Processing",
          "level": 3,
          "content": "When a message arrives, the system determines if it's voice or text. Voice messages are transcribed using OpenAI Whisper, while text messages are processed directly.",
          "code_blocks": ["code_001"]
        }
      ]
    }
  ]
}
```

---

## 🖼️ **MULTIMODAL CONTENT**

### **ImageContent Interface**

```typescript
interface ImageContent {
  id: string;                      // Unique image identifier
  url: string;                     // Original image URL
  local_path?: string;             // Local storage path
  alt_text?: string;               // Alt text if available
  
  // OCR extraction
  ocr_text?: string;               // Text extracted via OCR
  ocr_confidence?: number;         // 0-100 confidence score
  ocr_language?: string;           // Detected language
  
  // Metadata
  width?: number;
  height?: number;
  format?: string;                 // e.g., "png", "jpg"
  file_size?: number;              // Bytes
}
```

**Example:**
```json
{
  "images": [
    {
      "id": "img_001",
      "url": "https://n8n.io/workflows/2462/images/setup-telegram.png",
      "local_path": "data/images/2462/setup-telegram.png",
      "alt_text": "Telegram BotFather setup screen",
      "ocr_text": "BotFather: Alright, a new bot. How are we going to call it? Please choose a name for your bot.",
      "ocr_confidence": 95.7,
      "ocr_language": "en",
      "width": 800,
      "height": 600,
      "format": "png",
      "file_size": 156789
    }
  ]
}
```

### **VideoContent Interface**

```typescript
interface VideoContent {
  id: string;                      // Unique video identifier
  platform: 'youtube' | 'vimeo' | 'loom' | 'other';
  video_id: string;                // Platform video ID
  url: string;                     // Full video URL
  embed_url?: string;              // Embed URL
  
  // Metadata
  title?: string;
  description?: string;
  duration?: number;               // Seconds
  thumbnail_url?: string;
  
  // Transcript
  transcript?: string;             // Full video transcript
  transcript_language?: string;
  transcript_confidence?: number;  // 0-100 if available
  
  // Extraction info
  transcript_available: boolean;
  transcript_extraction_success: boolean;
}
```

**Example:**
```json
{
  "videos": [
    {
      "id": "vid_001",
      "platform": "youtube",
      "video_id": "dQw4w9WgXcQ",
      "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
      "embed_url": "https://www.youtube.com/embed/dQw4w9WgXcQ",
      "title": "How to Set Up Your Telegram Bot",
      "description": "Complete tutorial on creating and configuring a Telegram bot for n8n automation",
      "duration": 480,
      "thumbnail_url": "https://i.ytimg.com/vi/dQw4w9WgXcQ/maxresdefault.jpg",
      "transcript": "In this tutorial, I'll show you how to create a Telegram bot from scratch. First, open Telegram and search for @BotFather...",
      "transcript_language": "en",
      "transcript_available": true,
      "transcript_extraction_success": true
    }
  ]
}
```

### **CodeSnippet Interface**

```typescript