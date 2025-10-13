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
  // Basic identification
  id: string;                    // Workflow ID (e.g., "2462")
  url: string;                   // Full n8n.io URL
  scraped_at: string;            // ISO timestamp
  
  // Three-layer data structure
  basic_metadata: BasicMetadata;
  workflow_content: WorkflowContent;
  explainer_content: ExplainerContent;
  
  // Quality and processing info
  extraction_quality: ExtractionQuality;
  processing_metadata: ProcessingMetadata;
}
```

### BasicMetadata

Layer 1: Page-level metadata and categorization.

```typescript
interface BasicMetadata {
  // Core identification
  title: string;                 // Workflow title
  description: string;           // Workflow description
  author: string;                // Creator name
  
  // Categorization
  primary_category: string;      // Main category (e.g., "Automation")
  secondary_categories: string[]; // Additional categories
  node_tags: string[];           // Integration badges
  general_tags: string[];        // User tags
  
  // Content classification
  difficulty_level: 'beginner' | 'intermediate' | 'advanced';
  use_case: string;              // Primary use case description
  industry: string[];            // Target industries
  
  // Engagement metrics
  views: number;                 // View count
  upvotes: number;               // Upvote count
  created_at: string;            // Creation date
  updated_at: string;            // Last update date
  
  // Setup information
  setup_instructions: string;    // Setup guide
  prerequisites: string[];       // Required knowledge/tools
  estimated_setup_time: string;  // Setup time estimate
}
```

### WorkflowContent

Layer 2: Complete workflow structure and configuration.

```typescript
interface WorkflowContent {
  // Workflow structure
  name: string;                  // Workflow name
  nodes: NodeData[];             // All workflow nodes
  connections: ConnectionData[]; // Node connections
  settings: WorkflowSettings;    // Global workflow settings
  
  // Execution info
  trigger_type: string;          // How workflow is triggered
  execution_mode: string;        // Manual/automatic
  error_handling: ErrorHandling; // Error handling config
  
  // Performance metrics
  estimated_execution_time: number; // Seconds
  resource_requirements: ResourceRequirements;
}
```

### NodeData

Individual node configuration and parameters.

```typescript
interface NodeData {
  id: string;                    // Node ID
  name: string;                  // Node name
  type: string;                  // Node type (e.g., "n8n-nodes-base.httpRequest")
  position: Position;            // X,Y coordinates
  
  // Configuration
  parameters: Record<string, any>; // Node-specific parameters
  credentials: CredentialData[];   // Required credentials
  settings: NodeSettings;         // Node settings
  
  // Metadata
  display_name: string;          // Human-readable name
  description: string;           // Node description
  version: string;               // Node version
  category: string;              // Node category
}
```

### ExplainerContent

Layer 3: Tutorial content and multimodal data.

```typescript
interface ExplainerContent {
  // Text content
  introduction: string;          // Workflow introduction
  overview: string;              // High-level overview
  tutorial_sections: TutorialSection[];
  conclusion: string;            // Summary and next steps
  
  // Structured content
  step_by_step: StepByStepGuide[];
  best_practices: string[];      // Best practice tips
  common_pitfalls: string[];     // Common mistakes to avoid
  troubleshooting: TroubleshootingGuide;
  
  // Multimodal content
  images: ImageData[];           // Tutorial images
  videos: VideoData[];           // Video content
  code_snippets: CodeSnippet[];  // Code examples
}
```

---

## 📊 METADATA STRUCTURES

### Categories

```typescript
interface CategoryData {
  primary: string;               // Main category
  secondary: string[];           // Additional categories
  node_types: string[];          // Node type categories
  use_cases: string[];           // Use case categories
  industries: string[];          // Industry categories
}
```

### Tags

```typescript
interface TagData {
  integration_tags: string[];    // Integration badges
  user_tags: string[];           // User-defined tags
  system_tags: string[];         // System-generated tags
  difficulty_tags: string[];     // Difficulty indicators
  feature_tags: string[];        // Feature indicators
}
```

### Setup Instructions

```typescript
interface SetupInstructions {
  overview: string;              // Setup overview
  prerequisites: Prerequisite[]; // Required items
  step_by_step: SetupStep[];     // Detailed steps
  configuration: ConfigStep[];   // Configuration steps
  testing: TestingStep[];        // Testing instructions
  troubleshooting: string[];     // Common issues
}
```

---

## 🔧 WORKFLOW CONTENT

### N8nWorkflowJSON

Complete n8n workflow JSON structure.

```typescript
interface N8nWorkflowJSON {
  name: string;                  // Workflow name
  nodes: N8nNode[];             // n8n node definitions
  connections: N8nConnections;   // Node connections
  active: boolean;              // Workflow active status
  settings: N8nWorkflowSettings; // Workflow settings
  staticData: any;              // Static data
  pinData: any;                 // Pinned data
  versionId: string;            // Version ID
  id: string;                   // Workflow ID
  meta: N8nWorkflowMeta;        // Workflow metadata
}
```

### ConnectionMap

Node connection mapping and flow structure.

```typescript
interface ConnectionMap {
  [sourceNodeId: string]: {
    [outputIndex: string]: {
      [targetNodeId: string]: {
        [inputIndex: string]: boolean;
      };
    };
  };
}
```

### Node Configuration

Complete node parameter and credential configuration.

```typescript
interface NodeConfiguration {
  node_type: string;             // Full node type identifier
  display_name: string;          // Human-readable name
  parameters: Record<string, any>; // All node parameters
  credentials: CredentialReference[]; // Required credentials
  settings: NodeSettings;        // Node-specific settings
  position: Position;            // Node position
  type: string;                  // Node type
  typeVersion: number;           // Node type version
  webhookId?: string;            // Webhook ID (if applicable)
}
```

---

## 🎨 EXPLAINER CONTENT

### TutorialSection

Structured tutorial content with hierarchy.

```typescript
interface TutorialSection {
  id: string;                    // Section ID
  title: string;                 // Section title
  content: string;               // Section content
  subsections: TutorialSection[]; // Nested sections
  order: number;                 // Display order
  level: number;                 // Hierarchy level
}
```

### StepByStepGuide

Detailed step-by-step instructions.

```typescript
interface StepByStepGuide {
  step_number: number;           // Step number
  title: string;                 // Step title
  description: string;           // Step description
  instructions: string[];        // Detailed instructions
  expected_result: string;       // Expected outcome
  tips: string[];                // Helpful tips
  warnings: string[];            // Important warnings
}
```

### TroubleshootingGuide

Common issues and solutions.

```typescript
interface TroubleshootingGuide {
  common_issues: Issue[];        // Common problems
  error_messages: ErrorSolution[]; // Error solutions
  performance_tips: string[];    // Performance optimization
  debugging_steps: string[];     // Debugging process
}
```

---

## 🖼️ MULTIMODAL CONTENT

### ImageData

Tutorial images with OCR text extraction.

```typescript
interface ImageData {
  id: string;                    // Image ID
  url: string;                   // Original URL
  local_path: string;            // Local file path
  alt_text: string;              // Alt text description
  ocr_text: string;              // Extracted text
  ocr_confidence: number;        // OCR confidence score
  caption: string;               // Image caption
  context: string;               // Usage context
  dimensions: ImageDimensions;   // Image size
}
```

### VideoData

Video content with transcript extraction.

```typescript
interface VideoData {
  id: string;                    // Video ID
  url: string;                   // Video URL
  platform: string;              // Platform (YouTube, etc.)
  title: string;                 // Video title
  description: string;            // Video description
  duration: number;              // Duration in seconds
  transcript: string;            // Full transcript
  transcript_confidence: number; // Transcript confidence
  thumbnail_url: string;         // Thumbnail URL
  metadata: VideoMetadata;       // Additional metadata
}
```

### CodeSnippet

Code examples and snippets.

```typescript
interface CodeSnippet {
  id: string;                    // Snippet ID
  language: string;              // Programming language
  code: string;                  // Code content
  description: string;            // Code description
  context: string;               // Usage context
  line_numbers: boolean;         // Include line numbers
  syntax_highlighting: boolean;  // Apply highlighting
}
```

---

## ✅ VALIDATION RULES

### Field Validation

```typescript
interface ValidationRules {
  // Required fields
  required_fields: string[];
  
  // Type constraints
  string_constraints: {
    min_length: number;
    max_length: number;
    pattern?: string;
  };
  
  // Numeric constraints
  numeric_constraints: {
    min_value: number;
    max_value: number;
    integer_only: boolean;
  };
  
  // Array constraints
  array_constraints: {
    min_items: number;
    max_items: number;
    unique_items: boolean;
  };
}
```

### Quality Validation

```typescript
interface QualityValidation {
  completeness_score: number;    // 0-100 completeness
  data_quality_score: number;    // 0-100 data quality
  consistency_score: number;     // 0-100 consistency
  validation_errors: ValidationError[];
  warnings: ValidationWarning[];
}
```

---

## 📊 QUALITY METRICS

### Completeness Scoring

```typescript
interface CompletenessScore {
  basic_metadata: number;        // Layer 1 completeness
  workflow_content: number;      // Layer 2 completeness
  explainer_content: number;     // Layer 3 completeness
  overall_score: number;         // Overall completeness
  missing_fields: string[];      // Missing required fields
  incomplete_sections: string[]; // Incomplete sections
}
```

### Data Quality Metrics

```typescript
interface DataQualityMetrics {
  accuracy_score: number;        // Data accuracy (0-100)
  consistency_score: number;     // Data consistency (0-100)
  completeness_score: number;    // Data completeness (0-100)
  validity_score: number;        // Data validity (0-100)
  overall_quality: number;       // Overall quality score
}
```

---

## 📤 EXPORT FORMATS

### JSON Export

Complete dataset in JSON format.

```json
{
  "workflows": [
    {
      "id": "2462",
  "url": "https://n8n.io/workflows/2462",
      "scraped_at": "2025-10-09T10:30:00Z",
      "basic_metadata": { /* ... */ },
      "workflow_content": { /* ... */ },
      "explainer_content": { /* ... */ },
      "extraction_quality": { /* ... */ }
    }
  ],
  "metadata": {
    "total_workflows": 2100,
    "scraped_at": "2025-10-09T10:30:00Z",
    "version": "1.0.0"
  }
}
```

### JSONL Export

Training-optimized line-delimited JSON.

```jsonl
{"id": "2462", "title": "Angie, Personal AI Assistant", "content": "..."}
{"id": "8237", "title": "Email Automation", "content": "..."}
{"id": "8527", "title": "Data Processing", "content": "..."}
```

### CSV Export

Metadata summary in CSV format.

```csv
id,title,author,primary_category,difficulty_level,views,upvotes,completeness_score
2462,Angie Personal AI Assistant,John Doe,Automation,intermediate,1250,45,92
8237,Email Automation,Jane Smith,Marketing,beginner,890,23,88
8527,Data Processing,Bob Johnson,Data,advanced,2100,67,95
```

### Parquet Export

Columnar format for analytics.

```typescript
// Optimized for analytics and ML
interface ParquetSchema {
  id: string;
  title: string;
  description: string;
  categories: string[];
  tags: string[];
  node_count: number;
  connection_count: number;
  complexity_score: number;
  completeness_score: number;
  // ... additional fields
}
```

---

## 📝 COMPLETE EXAMPLES

### Minimal Workflow Example

```json
{
  "id": "2462",
  "url": "https://n8n.io/workflows/2462",
  "scraped_at": "2025-10-09T10:30:00Z",
  "basic_metadata": {
    "title": "Angie, Personal AI Assistant",
    "description": "AI assistant for personal productivity",
    "author": "John Doe",
    "primary_category": "Automation",
    "secondary_categories": ["AI", "Productivity"],
    "node_tags": ["OpenAI", "Telegram", "Webhook"],
    "general_tags": ["ai", "assistant", "personal"],
    "difficulty_level": "intermediate",
    "use_case": "Personal AI assistant for daily tasks",
    "industry": ["Personal", "Productivity"],
    "views": 1250,
    "upvotes": 45,
    "created_at": "2025-09-15T08:00:00Z",
    "updated_at": "2025-10-01T14:30:00Z",
    "setup_instructions": "Configure OpenAI API key and Telegram bot token",
    "prerequisites": ["OpenAI API access", "Telegram bot"],
    "estimated_setup_time": "15 minutes"
  },
  "workflow_content": {
    "name": "Angie Personal AI Assistant",
    "nodes": [
      {
        "id": "webhook-trigger",
        "name": "Webhook Trigger",
        "type": "n8n-nodes-base.webhook",
        "position": {"x": 100, "y": 200},
        "parameters": {
          "httpMethod": "POST",
          "path": "angie-webhook"
        }
      }
    ],
    "connections": {
      "webhook-trigger": {
        "main": [
          [
            {
              "node": "openai-node",
              "type": "main",
              "index": 0
            }
          ]
        ]
      }
    },
    "trigger_type": "webhook",
    "execution_mode": "automatic",
    "estimated_execution_time": 5
  },
  "explainer_content": {
    "introduction": "This workflow creates a personal AI assistant named Angie...",
    "overview": "Angie helps with daily tasks through Telegram integration...",
    "tutorial_sections": [
      {
        "id": "setup",
        "title": "Setup Instructions",
        "content": "First, you'll need to configure your OpenAI API key...",
        "order": 1,
        "level": 1
      }
    ],
    "step_by_step": [
      {
        "step_number": 1,
        "title": "Configure OpenAI Node",
        "description": "Set up the OpenAI node with your API key",
        "instructions": [
          "Open the OpenAI node configuration",
          "Enter your API key in the credentials field",
          "Set the model to 'gpt-3.5-turbo'"
        ],
        "expected_result": "OpenAI node is configured and ready"
      }
    ],
    "images": [
      {
        "id": "setup-screenshot",
        "url": "https://n8n.io/images/setup.png",
        "local_path": "/media/images/2462_setup.png",
        "alt_text": "OpenAI node configuration",
        "ocr_text": "API Key: sk-...",
        "ocr_confidence": 0.95,
        "caption": "OpenAI node setup screen"
      }
    ],
    "videos": [
      {
        "id": "tutorial-video",
        "url": "https://youtube.com/watch?v=example",
        "platform": "YouTube",
        "title": "Angie AI Assistant Setup",
        "duration": 300,
        "transcript": "Welcome to this tutorial on setting up Angie...",
        "transcript_confidence": 0.92
      }
    ]
  },
  "extraction_quality": {
    "completeness_score": 92,
    "data_quality_score": 88,
    "consistency_score": 95,
    "overall_score": 92,
    "missing_fields": [],
    "warnings": []
  }
}
```

### Rich Workflow Example

```json
{
  "id": "8237",
  "url": "https://n8n.io/workflows/8237",
  "scraped_at": "2025-10-09T10:35:00Z",
  "basic_metadata": {
    "title": "Advanced Email Marketing Automation",
    "description": "Comprehensive email marketing workflow with segmentation and personalization",
    "author": "Jane Smith",
    "primary_category": "Marketing",
    "secondary_categories": ["Email", "Automation", "CRM"],
    "node_tags": ["HubSpot", "Mailchimp", "Google Sheets", "Webhook"],
    "general_tags": ["email", "marketing", "automation", "crm"],
    "difficulty_level": "advanced",
    "use_case": "Automated email marketing campaigns with lead scoring",
    "industry": ["Marketing", "SaaS", "E-commerce"],
    "views": 2100,
    "upvotes": 67,
    "created_at": "2025-08-20T09:15:00Z",
    "updated_at": "2025-09-28T16:45:00Z",
    "setup_instructions": "Configure HubSpot and Mailchimp integrations, set up Google Sheets for data storage",
    "prerequisites": ["HubSpot account", "Mailchimp account", "Google Sheets access"],
    "estimated_setup_time": "45 minutes"
  },
  "workflow_content": {
    "name": "Email Marketing Automation",
    "nodes": [
      {
        "id": "webhook-trigger",
        "name": "Lead Webhook",
        "type": "n8n-nodes-base.webhook",
        "position": {"x": 100, "y": 200},
        "parameters": {
          "httpMethod": "POST",
          "path": "lead-capture"
        }
      },
      {
        "id": "hubspot-lookup",
        "name": "HubSpot Contact Lookup",
        "type": "n8n-nodes-base.hubspot",
        "position": {"x": 300, "y": 200},
        "parameters": {
          "operation": "get",
          "resource": "contact",
          "contactId": "={{$json.contact_id}}"
        }
      },
      {
        "id": "lead-scoring",
        "name": "Lead Scoring Logic",
        "type": "n8n-nodes-base.function",
        "position": {"x": 500, "y": 200},
        "parameters": {
          "functionCode": "// Lead scoring algorithm\nconst score = calculateLeadScore($input.all());\nreturn { lead_score: score };"
        }
      },
      {
        "id": "mailchimp-segment",
        "name": "Mailchimp Segment",
        "type": "n8n-nodes-base.mailchimp",
        "position": {"x": 700, "y": 200},
        "parameters": {
          "operation": "addMember",
          "listId": "{{$json.list_id}}",
          "emailAddress": "{{$json.email}}",
          "tags": "{{$json.tags}}"
        }
      }
    ],
    "connections": {
      "webhook-trigger": {
        "main": [
          [
            {
              "node": "hubspot-lookup",
              "type": "main",
              "index": 0
            }
          ]
        ]
      },
      "hubspot-lookup": {
        "main": [
          [
            {
              "node": "lead-scoring",
              "type": "main",
              "index": 0
            }
          ]
        ]
      },
      "lead-scoring": {
        "main": [
          [
            {
              "node": "mailchimp-segment",
              "type": "main",
              "index": 0
            }
          ]
        ]
      }
    },
    "trigger_type": "webhook",
    "execution_mode": "automatic",
    "estimated_execution_time": 15
  },
  "explainer_content": {
    "introduction": "This advanced email marketing automation workflow demonstrates sophisticated lead scoring and segmentation techniques...",
    "overview": "The workflow captures leads via webhook, enriches them with HubSpot data, applies scoring logic, and segments them in Mailchimp...",
    "tutorial_sections": [
      {
        "id": "overview",
        "title": "Workflow Overview",
        "content": "This workflow implements a complete lead-to-customer journey...",
        "order": 1,
        "level": 1
      },
      {
        "id": "setup",
        "title": "Setup Instructions",
        "content": "Configure your integrations and customize the scoring logic...",
        "order": 2,
        "level": 1
      },
      {
        "id": "scoring",
        "title": "Lead Scoring Logic",
        "content": "The scoring algorithm considers multiple factors...",
        "order": 3,
        "level": 1,
        "subsections": [
          {
            "id": "scoring-factors",
            "title": "Scoring Factors",
            "content": "Email engagement, website behavior, demographic data...",
            "order": 1,
            "level": 2
          }
        ]
      }
    ],
    "step_by_step": [
      {
        "step_number": 1,
        "title": "Configure Webhook Endpoint",
        "description": "Set up the webhook to receive lead data",
        "instructions": [
          "Copy the webhook URL from the trigger node",
          "Configure your lead capture form to send data to this URL",
          "Test the webhook with sample data"
        ],
        "expected_result": "Webhook receives lead data successfully",
        "tips": ["Use a tool like Postman to test the webhook"],
        "warnings": ["Ensure the webhook URL is secure and not publicly accessible"]
      },
      {
        "step_number": 2,
        "title": "Set Up HubSpot Integration",
        "description": "Connect to HubSpot for contact enrichment",
        "instructions": [
          "Create a HubSpot app and get API credentials",
          "Configure the HubSpot node with your credentials",
          "Test the connection by looking up a known contact"
        ],
        "expected_result": "HubSpot node successfully retrieves contact data"
      }
    ],
    "best_practices": [
      "Always validate incoming webhook data",
      "Implement error handling for API failures",
      "Use rate limiting to avoid hitting API limits",
      "Monitor workflow execution for performance issues"
    ],
    "common_pitfalls": [
      "Forgetting to handle API rate limits",
      "Not validating data before processing",
      "Missing error handling for failed API calls",
      "Not testing with real data before deployment"
    ],
    "troubleshooting": {
      "common_issues": [
        {
          "issue": "HubSpot API returns 401 error",
          "solution": "Check your API credentials and permissions"
        },
        {
          "issue": "Mailchimp segmentation fails",
          "solution": "Verify the list ID and member data format"
        }
      ],
      "error_messages": [
        {
          "error": "Contact not found in HubSpot",
          "solution": "Add validation to check if contact exists before processing"
        }
      ]
    },
    "images": [
      {
        "id": "workflow-diagram",
        "url": "https://n8n.io/images/workflow-8237.png",
        "local_path": "/media/images/8237_workflow.png",
        "alt_text": "Email marketing workflow diagram",
        "ocr_text": "Lead Capture → HubSpot → Scoring → Mailchimp",
        "ocr_confidence": 0.98,
        "caption": "Complete workflow flow diagram"
      },
      {
        "id": "scoring-logic",
        "url": "https://n8n.io/images/scoring-8237.png",
        "local_path": "/media/images/8237_scoring.png",
        "alt_text": "Lead scoring algorithm visualization",
        "ocr_text": "Score = (Email Opens × 2) + (Website Visits × 3) + (Form Submissions × 5)",
        "ocr_confidence": 0.94,
        "caption": "Lead scoring algorithm breakdown"
      }
    ],
    "videos": [
      {
        "id": "setup-tutorial",
        "url": "https://youtube.com/watch?v=email-marketing-setup",
        "platform": "YouTube",
        "title": "Email Marketing Automation Setup",
        "duration": 1200,
        "transcript": "In this comprehensive tutorial, we'll set up an advanced email marketing automation workflow...",
        "transcript_confidence": 0.96
      },
      {
        "id": "scoring-explanation",
        "url": "https://youtube.com/watch?v=lead-scoring-explained",
        "platform": "YouTube",
        "title": "Lead Scoring Algorithm Explained",
        "duration": 600,
        "transcript": "Let's dive deep into the lead scoring algorithm and how to customize it for your business...",
        "transcript_confidence": 0.93
      }
    ],
    "code_snippets": [
      {
        "id": "scoring-function",
        "language": "javascript",
        "code": "function calculateLeadScore(contactData) {\n  let score = 0;\n  \n  // Email engagement (40% weight)\n  if (contactData.email_opens > 5) score += 20;\n  if (contactData.email_clicks > 2) score += 20;\n  \n  // Website behavior (35% weight)\n  if (contactData.page_views > 10) score += 15;\n  if (contactData.time_on_site > 300) score += 20;\n  \n  // Demographic fit (25% weight)\n  if (contactData.company_size === 'enterprise') score += 15;\n  if (contactData.industry === 'technology') score += 10;\n  \n  return Math.min(score, 100);\n}",
        "description": "Lead scoring algorithm implementation",
        "context": "This function calculates a lead score based on engagement, behavior, and demographic data"
      }
    ]
  },
  "extraction_quality": {
    "completeness_score": 95,
    "data_quality_score": 92,
    "consistency_score": 98,
    "overall_score": 95,
    "missing_fields": [],
    "warnings": ["Video transcript confidence below 95%"]
  }
}
```

---

## 🔍 VALIDATION IMPLEMENTATION

### Pydantic Models

```python
from pydantic import BaseModel, Field, HttpUrl, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class DifficultyLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"

class WorkflowData(BaseModel):
    id: str = Field(..., pattern=r'^\d+$')
    url: HttpUrl
    scraped_at: datetime
    basic_metadata: 'BasicMetadata'
    workflow_content: 'WorkflowContent'
    explainer_content: 'ExplainerContent'
    extraction_quality: 'ExtractionQuality'
    
    @validator('id')
    def validate_id(cls, v):
        if not v.isdigit():
            raise ValueError('ID must be numeric')
        return v

class BasicMetadata(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=10, max_length=1000)
    author: str = Field(..., min_length=1, max_length=100)
    primary_category: str = Field(..., min_length=1, max_length=50)
    secondary_categories: List[str] = Field(default_factory=list)
    node_tags: List[str] = Field(default_factory=list)
    general_tags: List[str] = Field(default_factory=list)
    difficulty_level: DifficultyLevel
    use_case: str = Field(..., min_length=10, max_length=500)
    industry: List[str] = Field(default_factory=list)
    views: int = Field(..., ge=0)
    upvotes: int = Field(..., ge=0)
    created_at: datetime
    updated_at: datetime
    setup_instructions: str = Field(..., min_length=10)
    prerequisites: List[str] = Field(default_factory=list)
    estimated_setup_time: str = Field(..., pattern=r'^\d+\s+(minute|hour)s?$')
    
    @validator('secondary_categories')
    def validate_categories(cls, v):
        if len(v) > 10:
            raise ValueError('Too many secondary categories')
        return v

class ExtractionQuality(BaseModel):
    completeness_score: int = Field(..., ge=0, le=100)
    data_quality_score: int = Field(..., ge=0, le=100)
    consistency_score: int = Field(..., ge=0, le=100)
    overall_score: int = Field(..., ge=0, le=100)
    missing_fields: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    
    @validator('overall_score')
    def validate_overall_score(cls, v, values):
        if 'completeness_score' in values and 'data_quality_score' in values:
            expected = (values['completeness_score'] + values['data_quality_score']) // 2
            if abs(v - expected) > 5:
                raise ValueError('Overall score should be close to average of completeness and quality scores')
        return v
```

---

## 📊 QUALITY METRICS CALCULATION

### Completeness Scoring Algorithm

```python
def calculate_completeness_score(workflow_data: WorkflowData) -> int:
    """Calculate completeness score based on required fields"""
    total_fields = 0
    present_fields = 0
    
    # Basic metadata fields (weight: 40%)
    basic_required = [
        'title', 'description', 'author', 'primary_category',
        'difficulty_level', 'use_case', 'views', 'upvotes'
    ]
    for field in basic_required:
        total_fields += 1
        if hasattr(workflow_data.basic_metadata, field) and getattr(workflow_data.basic_metadata, field):
            present_fields += 1
    
    # Workflow content fields (weight: 35%)
    workflow_required = ['name', 'nodes', 'connections']
    for field in workflow_required:
        total_fields += 1
        if hasattr(workflow_data.workflow_content, field) and getattr(workflow_data.workflow_content, field):
            present_fields += 1
    
    # Explainer content fields (weight: 25%)
    explainer_required = ['introduction', 'overview', 'tutorial_sections']
    for field in explainer_required:
        total_fields += 1
        if hasattr(workflow_data.explainer_content, field) and getattr(workflow_data.explainer_content, field):
            present_fields += 1
    
    return int((present_fields / total_fields) * 100)
```

---

## 🎯 SUMMARY

This complete dataset schema provides:

1. **Comprehensive Structure** - All three layers of data capture
2. **Type Safety** - Complete TypeScript interfaces and Pydantic models
3. **Validation Rules** - Built-in validation and quality scoring
4. **Export Formats** - Multiple formats for different use cases
5. **Quality Metrics** - Automated completeness and quality scoring
6. **Complete Examples** - Both minimal and rich workflow examples

The schema is designed to capture the full context and complexity of n8n workflows while maintaining consistency and trainability for AI model development.

---

**Version:** 1.0.0  
**Status:** ✅ Complete  
**Next Review:** After implementation testing