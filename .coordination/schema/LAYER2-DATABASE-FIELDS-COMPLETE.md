# 📊 LAYER 2 ENHANCED - COMPLETE DATABASE FIELDS

**Layer:** Layer 2 - Workflow JSON Extractor (Enhanced)  
**Purpose:** Extract complete workflow technical data for AI training  
**Date:** October 13, 2025  
**Version:** 2.0 (Enhanced with Iframe Parsing)

---

## 🎯 OVERVIEW

Layer 2 Enhanced extracts **100% complete workflow data** from two sources:
1. **API** (Primary + Fallback) - 85% of data
2. **Iframe** (Demo workflow) - 15% of data

**Total Fields:** 50+ fields across multiple categories

---

## 📋 FIELD CATEGORIES

1. **Core Workflow Fields** (from API)
2. **Node Fields** (from API + Iframe)
3. **Connection Fields** (from API)
4. **Phase 1 Fields** (Node Metadata from Iframe)
5. **Phase 2 Fields** (Visual Layout from Iframe)
6. **Phase 3 Fields** (Enhanced Text from Iframe)
7. **Phase 4 Fields** (Media Content from Iframe)
8. **Metadata Fields** (Extraction metadata)

---

## 1️⃣ CORE WORKFLOW FIELDS (API)

### **Field: `workflow_id`**
- **Type:** `string`
- **Source:** API
- **Description:** Unique identifier for the workflow
- **Example:** `"2462"`
- **Required:** Yes
- **AI Training Use:** Primary key, workflow identification

---

### **Field: `name`**
- **Type:** `string`
- **Source:** API
- **Description:** Human-readable workflow name
- **Example:** `"Angie, Personal AI Assistant with Telegram Voice and Text"`
- **Required:** Yes
- **AI Training Use:** Natural language understanding, workflow naming patterns

---

### **Field: `description`**
- **Type:** `string`
- **Source:** API
- **Description:** Detailed workflow description
- **Example:** `"A personal AI assistant that operates through Telegram with voice and text support"`
- **Required:** No
- **AI Training Use:** Semantic understanding, use case learning

---

### **Field: `workflow.meta.instanceId`**
- **Type:** `string`
- **Source:** API
- **Description:** Unique instance identifier for the workflow
- **Example:** `"04ddf1130268840c229f501edc57936c3c131339e8b0cdd696fcf3a7c69e696e"`
- **Required:** No
- **AI Training Use:** Workflow versioning, instance tracking

---

### **Field: `workflow.meta.templateId`**
- **Type:** `string`
- **Source:** API
- **Description:** Template ID if workflow is from template
- **Example:** `"2462"`
- **Required:** No
- **AI Training Use:** Template relationship tracking

---

### **Field: `workflow.meta.templateCredsSetupCompleted`**
- **Type:** `boolean`
- **Source:** API
- **Description:** Whether credential setup is complete
- **Example:** `true`
- **Required:** No
- **AI Training Use:** Workflow readiness status

---

### **Field: `workflow.settings`**
- **Type:** `object`
- **Source:** API
- **Description:** Workflow-level settings and configurations
- **Example:** `{"executionOrder": "v1", "saveManualExecutions": true}`
- **Required:** No
- **AI Training Use:** Workflow behavior configuration

---

### **Field: `workflow.staticData`**
- **Type:** `object`
- **Source:** API
- **Description:** Static data shared across workflow executions
- **Example:** `{"node:Telegram": {"lastMessageId": 12345}}`
- **Required:** No
- **AI Training Use:** State management patterns

---

### **Field: `workflow.pinData`**
- **Type:** `object`
- **Source:** API
- **Description:** Pinned test data for nodes
- **Example:** `{}`
- **Required:** No
- **AI Training Use:** Testing and debugging patterns

---

### **Field: `categories`**
- **Type:** `array[string]`
- **Source:** API
- **Description:** Workflow category tags
- **Example:** `["AI", "Communication", "Productivity"]`
- **Required:** No
- **AI Training Use:** Workflow classification, use case categorization

---

### **Field: `views`**
- **Type:** `integer`
- **Source:** API
- **Description:** Number of times workflow has been viewed
- **Example:** `15234`
- **Required:** No
- **AI Training Use:** Popularity metrics, workflow ranking

---

### **Field: `usedCredentials`**
- **Type:** `array[string]`
- **Source:** API
- **Description:** List of credential types used in workflow
- **Example:** `["telegramApi", "openAiApi", "gmailOAuth2"]`
- **Required:** No
- **AI Training Use:** Authentication patterns, integration requirements

---

### **Field: `communityNodes`**
- **Type:** `array[string]`
- **Source:** API
- **Description:** Community-contributed nodes used in workflow
- **Example:** `["@n8n/n8n-nodes-langchain"]`
- **Required:** No
- **AI Training Use:** Node ecosystem understanding, dependency tracking

---

### **Field: `user`**
- **Type:** `object`
- **Source:** API
- **Description:** Workflow author information
- **Example:** `{"username": "n8n-team", "name": "n8n Team"}`
- **Required:** No
- **AI Training Use:** Author patterns, workflow quality indicators

---

## 2️⃣ NODE FIELDS (API)

### **Field: `workflow.nodes`**
- **Type:** `array[object]`
- **Source:** API
- **Description:** Array of all nodes in the workflow
- **Example:** `[{...node1...}, {...node2...}]`
- **Required:** Yes
- **AI Training Use:** Core workflow structure

---

### **Field: `workflow.nodes[].id`**
- **Type:** `string` (UUID)
- **Source:** API
- **Description:** Unique identifier for the node
- **Example:** `"c70236ea-91ab-4e47-b6f6-63a70ede5d3c"`
- **Required:** Yes
- **AI Training Use:** Node identification, connection mapping

---

### **Field: `workflow.nodes[].name`**
- **Type:** `string`
- **Source:** API
- **Description:** Human-readable node name
- **Example:** `"Google Calendar"`
- **Required:** Yes
- **AI Training Use:** Node naming patterns, semantic understanding

---

### **Field: `workflow.nodes[].type`**
- **Type:** `string`
- **Source:** API
- **Description:** Node type identifier (n8n node type)
- **Example:** `"n8n-nodes-base.googleCalendarTool"`
- **Required:** Yes
- **AI Training Use:** Node type recognition, functionality mapping

---

### **Field: `workflow.nodes[].position`**
- **Type:** `array[number, number]`
- **Source:** API
- **Description:** Node position on canvas [X, Y]
- **Example:** `[2000, 704]`
- **Required:** Yes
- **AI Training Use:** Layout patterns, spatial relationships

---

### **Field: `workflow.nodes[].parameters`**
- **Type:** `object`
- **Source:** API
- **Description:** Node configuration parameters
- **Example:**
```json
{
  "operation": "getAll",
  "calendar": {
    "__rl": true,
    "mode": "list",
    "value": "user@gmail.com"
  },
  "options": {
    "fields": "items(summary, start(dateTime))",
    "timeMin": "={{$fromAI(\"date\",\"YYYY-MM-DDTHH:MM:SS\")}}"
  }
}
```
- **Required:** Yes
- **AI Training Use:** Configuration patterns, parameter usage, n8n expressions

---

### **Field: `workflow.nodes[].typeVersion`**
- **Type:** `number`
- **Source:** API
- **Description:** Version of the node type
- **Example:** `1.1`
- **Required:** Yes
- **AI Training Use:** Node version compatibility, API evolution

---

### **Field: `workflow.nodes[].webhookId`**
- **Type:** `string` (UUID)
- **Source:** API
- **Description:** Webhook identifier for trigger nodes
- **Example:** `"322dce18-f93e-4f86-b9b1-3305519b7834"`
- **Required:** No (only for webhook/trigger nodes)
- **AI Training Use:** Webhook patterns, trigger node identification

---

### **Field: `workflow.nodes[].credentials`**
- **Type:** `object`
- **Source:** API
- **Description:** Credentials used by this node
- **Example:**
```json
{
  "openAiApi": {
    "id": "8gccIjcuf3gvaoEr",
    "name": "OpenAi account"
  }
}
```
- **Required:** No (only for nodes requiring auth)
- **AI Training Use:** Authentication patterns, credential management

---

### **Field: `workflow.nodes[].onError`**
- **Type:** `string`
- **Source:** API
- **Description:** Error handling behavior
- **Example:** `"continueErrorOutput"`
- **Required:** No
- **AI Training Use:** Error handling patterns, workflow resilience

---

## 3️⃣ CONNECTION FIELDS (API)

### **Field: `workflow.connections`**
- **Type:** `object`
- **Source:** API
- **Description:** Connection mappings between nodes
- **Example:**
```json
{
  "SerpAPI": {
    "ai_tool": [
      [
        {
          "node": "AI Agent",
          "type": "ai_tool",
          "index": 0
        }
      ]
    ]
  }
}
```
- **Required:** Yes
- **AI Training Use:** Data flow patterns, node relationships, workflow logic

---

### **Field: `workflow.connections[source_node][output_type][][].node`**
- **Type:** `string`
- **Source:** API
- **Description:** Target node name for connection
- **Example:** `"AI Agent"`
- **Required:** Yes (for each connection)
- **AI Training Use:** Node dependency patterns

---

### **Field: `workflow.connections[source_node][output_type][][].type`**
- **Type:** `string`
- **Source:** API
- **Description:** Connection type (main, ai_tool, ai_memory, etc.)
- **Example:** `"ai_tool"`
- **Required:** Yes (for each connection)
- **AI Training Use:** Connection type patterns, data flow types

---

### **Field: `workflow.connections[source_node][output_type][][].index`**
- **Type:** `integer`
- **Source:** API
- **Description:** Output index for multi-output nodes
- **Example:** `0`
- **Required:** Yes (for each connection)
- **AI Training Use:** Multi-output handling patterns

---

## 4️⃣ PHASE 1 FIELDS (Node Metadata from Iframe)

### **Field: `workflow.nodes[].iframe_data`**
- **Type:** `object`
- **Source:** Iframe (Phase 1)
- **Description:** Node metadata extracted from demo iframe
- **Example:**
```json
{
  "name": "When chat message received",
  "type": "@n8n/n8n-nodes-langchain.chatTrigger",
  "id": null,
  "test_id": "canvas-node",
  "source": "iframe"
}
```
- **Required:** No (enhancement)
- **AI Training Use:** Cross-validation with API, UI context

---

### **Field: `iframe_data.nodes`**
- **Type:** `array[object]`
- **Source:** Iframe (Phase 1)
- **Description:** All node elements found in iframe (includes handles)
- **Example:** `[{...node1...}, {...node2...}]` (39 elements for complex workflow)
- **Required:** No
- **AI Training Use:** Complete node inventory, UI element understanding

---

### **Field: `iframe_data.text_content`**
- **Type:** `object`
- **Source:** Iframe (Phase 1)
- **Description:** Basic text content from iframe
- **Example:**
```json
{
  "all_text": "When chat message received\nMemory\nSimple Memory...",
  "all_text_length": 116,
  "text_blocks": [
    {"text": "I can answer most questions...", "length": 45}
  ],
  "input_hints": ["Enter your response..."]
}
```
- **Required:** No
- **AI Training Use:** UI text patterns, user guidance

---

### **Field: `iframe_data.images`**
- **Type:** `array[object]`
- **Source:** Iframe (Phase 1)
- **Description:** Basic images from iframe (node icons)
- **Example:**
```json
[
  {
    "src": "/icons/@n8n/n8n-nodes-langchain/dist/nodes/llms/LMChatOpenAi/openAiLight.svg",
    "alt": "",
    "type": "node_icon",
    "source": "iframe"
  }
]
```
- **Required:** No
- **AI Training Use:** Icon recognition, visual-textual associations

---

## 5️⃣ PHASE 2 FIELDS (Visual Layout from Iframe)

### **Field: `iframe_data.visual_layout`**
- **Type:** `object`
- **Source:** Iframe (Phase 2)
- **Description:** Complete visual layout data
- **Required:** No
- **AI Training Use:** Workflow layout generation, spatial intelligence

---

### **Field: `visual_layout.node_positions`**
- **Type:** `array[object]`
- **Source:** Iframe (Phase 2)
- **Description:** Precise position data for all node elements
- **Example:**
```json
[
  {
    "node_name": "Google Calendar",
    "x": 1040.7698364257812,
    "y": 435.95269775390625,
    "width": 19.96063232421875,
    "height": 19.960601806640625,
    "transform": "none",
    "css_position": "static",
    "source": "iframe"
  }
]
```
- **Required:** No
- **AI Training Use:** CRITICAL - Spatial relationships, layout patterns, optimal positioning

---

### **Field: `visual_layout.node_positions[].node_name`**
- **Type:** `string`
- **Source:** Iframe (Phase 2)
- **Description:** Name of the node
- **Example:** `"Google Calendar"`
- **Required:** Yes (for each position)
- **AI Training Use:** Node identification

---

### **Field: `visual_layout.node_positions[].x`**
- **Type:** `float`
- **Source:** Iframe (Phase 2)
- **Description:** X coordinate (horizontal position in pixels)
- **Example:** `1040.7698364257812`
- **Required:** Yes (for each position)
- **AI Training Use:** CRITICAL - Horizontal layout patterns, left-to-right flow

---

### **Field: `visual_layout.node_positions[].y`**
- **Type:** `float`
- **Source:** Iframe (Phase 2)
- **Description:** Y coordinate (vertical position in pixels)
- **Example:** `435.95269775390625`
- **Required:** Yes (for each position)
- **AI Training Use:** CRITICAL - Vertical layout patterns, top-to-bottom flow

---

### **Field: `visual_layout.node_positions[].width`**
- **Type:** `float`
- **Source:** Iframe (Phase 2)
- **Description:** Node width in pixels
- **Example:** `19.96063232421875`
- **Required:** Yes (for each position)
- **AI Training Use:** Node sizing patterns, visual hierarchy

---

### **Field: `visual_layout.node_positions[].height`**
- **Type:** `float`
- **Source:** Iframe (Phase 2)
- **Description:** Node height in pixels
- **Example:** `19.960601806640625`
- **Required:** Yes (for each position)
- **AI Training Use:** Node sizing patterns, visual hierarchy

---

### **Field: `visual_layout.node_positions[].transform`**
- **Type:** `string`
- **Source:** Iframe (Phase 2)
- **Description:** CSS transform applied to node
- **Example:** `"matrix(1, 0, 0, 1, -8, -8)"` or `"none"`
- **Required:** Yes (for each position)
- **AI Training Use:** Advanced positioning, CSS transformations

---

### **Field: `visual_layout.node_positions[].css_position`**
- **Type:** `string`
- **Source:** Iframe (Phase 2)
- **Description:** CSS position type (static, absolute, relative, fixed)
- **Example:** `"absolute"`
- **Required:** Yes (for each position)
- **AI Training Use:** Positioning strategy patterns

---

### **Field: `visual_layout.canvas_state`**
- **Type:** `object`
- **Source:** Iframe (Phase 2)
- **Description:** Canvas/viewport state
- **Example:**
```json
{
  "transform": "matrix(1, 0, 0, 1, 0, 0)",
  "zoom": "1",
  "width": 709,
  "height": 520,
  "scrollLeft": 0,
  "scrollTop": 0
}
```
- **Required:** No
- **AI Training Use:** CRITICAL - Canvas organization, zoom patterns, viewport management

---

### **Field: `visual_layout.canvas_state.zoom`**
- **Type:** `string`
- **Source:** Iframe (Phase 2)
- **Description:** Canvas zoom level
- **Example:** `"1"` (100%), `"0.8"` (80%), `"1.2"` (120%)
- **Required:** Yes
- **AI Training Use:** CRITICAL - Zoom patterns for workflow complexity

---

### **Field: `visual_layout.canvas_state.width`**
- **Type:** `integer`
- **Source:** Iframe (Phase 2)
- **Description:** Canvas viewport width in pixels
- **Example:** `709`
- **Required:** Yes
- **AI Training Use:** Viewport sizing patterns

---

### **Field: `visual_layout.canvas_state.height`**
- **Type:** `integer`
- **Source:** Iframe (Phase 2)
- **Description:** Canvas viewport height in pixels
- **Example:** `520`
- **Required:** Yes
- **AI Training Use:** Viewport sizing patterns

---

### **Field: `visual_layout.canvas_state.scrollLeft`**
- **Type:** `integer`
- **Source:** Iframe (Phase 2)
- **Description:** Horizontal scroll offset
- **Example:** `0`
- **Required:** Yes
- **AI Training Use:** Canvas pan patterns

---

### **Field: `visual_layout.canvas_state.scrollTop`**
- **Type:** `integer`
- **Source:** Iframe (Phase 2)
- **Description:** Vertical scroll offset
- **Example:** `0`
- **Required:** Yes
- **AI Training Use:** Canvas pan patterns

---

### **Field: `visual_layout.spatial_metrics`**
- **Type:** `object`
- **Source:** Iframe (Phase 2) - Calculated
- **Description:** Calculated spatial metrics for the workflow
- **Example:**
```json
{
  "total_nodes": 39,
  "bounding_box": {
    "min_x": 446.77,
    "max_x": 1039.73,
    "min_y": 195.95,
    "max_y": 435.95,
    "width": 592.96,
    "height": 240.00
  },
  "center_of_mass": {
    "x": 743.25,
    "y": 315.95
  },
  "density": 0.000275
}
```
- **Required:** No
- **AI Training Use:** CRITICAL - Workflow complexity metrics, organization patterns

---

### **Field: `spatial_metrics.total_nodes`**
- **Type:** `integer`
- **Source:** Calculated (Phase 2)
- **Description:** Total number of positioned nodes
- **Example:** `39`
- **Required:** Yes
- **AI Training Use:** Workflow size/complexity indicator

---

### **Field: `spatial_metrics.bounding_box`**
- **Type:** `object`
- **Source:** Calculated (Phase 2)
- **Description:** Bounding box containing all nodes
- **Example:** `{"min_x": 446.77, "max_x": 1039.73, "width": 592.96, "height": 240.00}`
- **Required:** Yes
- **AI Training Use:** CRITICAL - Workflow size, canvas usage patterns

---

### **Field: `spatial_metrics.center_of_mass`**
- **Type:** `object`
- **Source:** Calculated (Phase 2)
- **Description:** Geometric center of all nodes
- **Example:** `{"x": 743.25, "y": 315.95}`
- **Required:** Yes
- **AI Training Use:** Workflow balance, centering patterns

---

### **Field: `spatial_metrics.density`**
- **Type:** `float`
- **Source:** Calculated (Phase 2)
- **Description:** Node density (nodes per square pixel)
- **Example:** `0.000275`
- **Required:** Yes
- **AI Training Use:** CRITICAL - Workflow organization efficiency, spacing patterns

---

## 6️⃣ PHASE 3 FIELDS (Enhanced Text from Iframe)

### **Field: `iframe_data.enhanced_content`**
- **Type:** `object`
- **Source:** Iframe (Phase 3)
- **Description:** Enhanced explanatory content with categorization
- **Required:** No
- **AI Training Use:** NLP training, semantic understanding

---

### **Field: `enhanced_content.all_text_blocks`**
- **Type:** `array[object]`
- **Source:** Iframe (Phase 3)
- **Description:** ALL text blocks from iframe (>5 chars)
- **Example:**
```json
[
  {
    "text": "When chat message received",
    "length": 29,
    "tag": "span",
    "classes": "_nodeLabel_z1mvy_234",
    "category": "text",
    "source": "iframe"
  },
  {
    "text": "I can answer most questions about building workflows in n8n...",
    "length": 62,
    "tag": "p",
    "classes": "help-text",
    "category": "paragraph",
    "source": "iframe"
  }
]
```
- **Required:** No
- **AI Training Use:** HIGH - Multiple text representations, semantic diversity

---

### **Field: `enhanced_content.all_text_blocks[].text`**
- **Type:** `string`
- **Source:** Iframe (Phase 3)
- **Description:** The actual text content
- **Example:** `"When chat message received"`
- **Required:** Yes (for each block)
- **AI Training Use:** NLP training, text understanding

---

### **Field: `enhanced_content.all_text_blocks[].length`**
- **Type:** `integer`
- **Source:** Iframe (Phase 3)
- **Description:** Character count of text
- **Example:** `29`
- **Required:** Yes (for each block)
- **AI Training Use:** Text importance weighting

---

### **Field: `enhanced_content.all_text_blocks[].tag`**
- **Type:** `string`
- **Source:** Iframe (Phase 3)
- **Description:** HTML tag name
- **Example:** `"span"`, `"p"`, `"div"`, `"button"`, `"label"`, `"h1"`
- **Required:** Yes (for each block)
- **AI Training Use:** Text context understanding, HTML structure patterns

---

### **Field: `enhanced_content.all_text_blocks[].classes`**
- **Type:** `string`
- **Source:** Iframe (Phase 3)
- **Description:** CSS classes applied to element
- **Example:** `"_nodeLabel_z1mvy_234 _trigger_z1mvy_145"`
- **Required:** Yes (for each block)
- **AI Training Use:** UI component identification, styling patterns

---

### **Field: `enhanced_content.all_text_blocks[].category`**
- **Type:** `string` (enum)
- **Source:** Iframe (Phase 3) - Calculated
- **Description:** Categorized text type
- **Possible Values:**
  - `"heading"` - Headers (h1-h6)
  - `"paragraph"` - Long text (>100 chars)
  - `"text"` - General text
  - `"button_text"` - Button labels
  - `"label"` - Form labels
  - `"help_text"` - Help and hints
  - `"description"` - Descriptive content
  - `"instruction"` - Step-by-step instructions
  - `"error_message"` - Errors and warnings
- **Example:** `"paragraph"`
- **Required:** Yes (for each block)
- **AI Training Use:** HIGH - Text type understanding, context-aware responses

---

### **Field: `enhanced_content.total_text_length`**
- **Type:** `integer`
- **Source:** Iframe (Phase 3) - Calculated
- **Description:** Total character count across all text blocks
- **Example:** `23928` (complex workflow), `7102` (simple workflow)
- **Required:** Yes
- **AI Training Use:** Content richness metric, workflow documentation quality

---

### **Field: `enhanced_content.help_texts`**
- **Type:** `array[object]`
- **Source:** Iframe (Phase 3)
- **Description:** Help texts from title, aria-label, tooltip attributes
- **Example:**
```json
[
  {"type": "title", "text": "Click to configure node"},
  {"type": "aria-label", "text": "Node settings"},
  {"type": "tooltip", "text": "This node processes incoming messages"}
]
```
- **Required:** No
- **AI Training Use:** HIGH - User guidance patterns, contextual help generation

---

### **Field: `enhanced_content.error_messages`**
- **Type:** `array[string]`
- **Source:** Iframe (Phase 3)
- **Description:** Error messages and warnings from iframe
- **Example:** `["Configuration required", "Missing credentials"]`
- **Required:** No
- **AI Training Use:** Error handling patterns, troubleshooting guidance

---

## 7️⃣ PHASE 4 FIELDS (Media Content from Iframe)

### **Field: `iframe_data.media_content`**
- **Type:** `object`
- **Source:** Iframe (Phase 4)
- **Description:** Complete media content from iframe
- **Required:** No
- **AI Training Use:** Multimodal training, visual understanding

---

### **Field: `media_content.videos`**
- **Type:** `array[object]`
- **Source:** Iframe (Phase 4)
- **Description:** Video elements (YouTube, Vimeo, direct)
- **Example:**
```json
[
  {
    "type": "iframe",
    "source": "https://www.youtube.com/embed/abc123",
    "platform": "youtube",
    "source_type": "iframe"
  }
]
```
- **Required:** No
- **AI Training Use:** Video tutorial identification, multimodal learning

---

### **Field: `media_content.videos[].platform`**
- **Type:** `string` (enum)
- **Source:** Iframe (Phase 4)
- **Description:** Video platform
- **Possible Values:** `"youtube"`, `"vimeo"`, `"direct"`
- **Example:** `"youtube"`
- **Required:** Yes (for each video)
- **AI Training Use:** Platform-specific handling patterns

---

### **Field: `media_content.images`**
- **Type:** `array[object]`
- **Source:** Iframe (Phase 4)
- **Description:** All images with enhanced metadata
- **Example:**
```json
[
  {
    "src": "/icons/@n8n/n8n-nodes-langchain/dist/nodes/llms/LMChatOpenAi/openAiLight.svg",
    "alt": "",
    "width": "20",
    "height": "20",
    "type": "node_icon",
    "source": "iframe"
  }
]
```
- **Required:** No
- **AI Training Use:** Icon recognition, visual asset management

---

### **Field: `media_content.images[].type`**
- **Type:** `string` (enum)
- **Source:** Iframe (Phase 4) - Calculated
- **Description:** Categorized image type
- **Possible Values:**
  - `"node_icon"` - Node type icons
  - `"screenshot"` - Workflow screenshots
  - `"diagram"` - Conceptual diagrams
  - `"logo"` - Brand logos
  - `"content_image"` - General images
- **Example:** `"node_icon"`
- **Required:** Yes (for each image)
- **AI Training Use:** Image type recognition, appropriate asset selection

---

### **Field: `media_content.svgs`**
- **Type:** `array[object]`
- **Source:** Iframe (Phase 4)
- **Description:** SVG elements (icons, diagrams, UI elements)
- **Example:**
```json
[
  {
    "type": "svg",
    "viewBox": "0 0 24 24",
    "classes": "icon-class",
    "source": "iframe"
  }
]
```
- **Required:** No
- **AI Training Use:** Vector graphic understanding, icon patterns

---

### **Field: `media_content.video_count`**
- **Type:** `integer`
- **Source:** Iframe (Phase 4) - Calculated
- **Description:** Total number of videos
- **Example:** `1`
- **Required:** Yes
- **AI Training Use:** Media richness metric

---

### **Field: `media_content.image_count`**
- **Type:** `integer`
- **Source:** Iframe (Phase 4) - Calculated
- **Description:** Total number of images
- **Example:** `9`
- **Required:** Yes
- **AI Training Use:** Media richness metric

---

### **Field: `media_content.svg_count`**
- **Type:** `integer`
- **Source:** Iframe (Phase 4) - Calculated
- **Description:** Total number of SVG elements
- **Example:** `63` (complex workflow)
- **Required:** Yes
- **AI Training Use:** UI complexity metric

---

## 8️⃣ METADATA FIELDS (Extraction Metadata)

### **Field: `extraction_time`**
- **Type:** `float`
- **Source:** Calculated
- **Description:** Total extraction time in seconds
- **Example:** `25.039364`
- **Required:** Yes
- **AI Training Use:** Performance metrics, workflow complexity indicator

---

### **Field: `completeness`**
- **Type:** `object`
- **Source:** Calculated
- **Description:** Completeness metrics for each source
- **Example:**
```json
{
  "api_only": 85.0,
  "iframe_only": 15.0,
  "merged": 100.0
}
```
- **Required:** Yes
- **AI Training Use:** Data quality metrics

---

### **Field: `sources`**
- **Type:** `object`
- **Source:** Combined
- **Description:** Complete data from each source
- **Example:** `{"api": {...}, "iframe": {...}}`
- **Required:** Yes
- **AI Training Use:** Source tracking, data provenance

---

### **Field: `statistics`**
- **Type:** `object`
- **Source:** Calculated
- **Description:** Extraction statistics
- **Example:**
```json
{
  "api": {
    "total": 3,
    "primary_success": 3,
    "fallback_success": 0,
    "both_failed": 0
  },
  "iframe": {
    "total_attempts": 3,
    "successful": 3,
    "failed": 0,
    "nodes_extracted": 81,
    "text_blocks_extracted": 14,
    "images_extracted": 15
  }
}
```
- **Required:** Yes
- **AI Training Use:** Quality metrics, extraction reliability

---

## 📊 COMPLETE FIELD SUMMARY

### **Total Fields by Category:**

| Category | Fields | Source | AI Value |
|----------|--------|--------|----------|
| **Core Workflow** | 12 | API | ⭐⭐⭐⭐⭐ |
| **Nodes** | 10 per node | API | ⭐⭐⭐⭐⭐ |
| **Connections** | 4 per connection | API | ⭐⭐⭐⭐⭐ |
| **Phase 1 (Metadata)** | 5 | Iframe | ⭐⭐⭐⭐⭐ |
| **Phase 2 (Visual)** | 15 | Iframe | ⭐⭐⭐⭐⭐ |
| **Phase 3 (Text)** | 8 | Iframe | ⭐⭐⭐⭐ |
| **Phase 4 (Media)** | 10 | Iframe | ⭐⭐⭐ |
| **Metadata** | 5 | Calculated | ⭐⭐⭐ |

**Total: 50+ fields per workflow**

---

## 🎯 FIELD USAGE FOR AI TRAINING

### **Workflow Generation:**
```
Input: "Create a Slack notification workflow"

AI Uses:
  • workflow.nodes[].type → Select appropriate nodes
  • workflow.nodes[].parameters → Configure nodes
  • workflow.connections → Connect nodes
  • visual_layout.node_positions → Position optimally
  • enhanced_content.help_texts → Add guidance

Output: Complete, well-organized workflow
```

---

### **Layout Optimization:**
```
Input: Messy workflow JSON

AI Uses:
  • visual_layout.node_positions → Learn optimal positions
  • spatial_metrics.density → Target optimal density
  • spatial_metrics.bounding_box → Size appropriately
  • canvas_state.zoom → Set appropriate zoom

Output: Professionally organized workflow
```

---

### **Natural Language Understanding:**
```
Input: "How do I configure the Telegram node?"

AI Uses:
  • workflow.nodes[].name → Identify node
  • workflow.nodes[].parameters → Show configuration
  • enhanced_content.help_texts → Provide guidance
  • enhanced_content.all_text_blocks → Context

Output: Comprehensive answer
```

---

## 📊 DATA RICHNESS BY WORKFLOW COMPLEXITY

### **Simple Workflow (5 nodes):**
- API Fields: ~60 data points
- Iframe Fields: ~100 data points
- **Total: ~160 data points**

### **Medium Workflow (12 nodes):**
- API Fields: ~150 data points
- Iframe Fields: ~180 data points
- **Total: ~330 data points**

### **Complex Workflow (15 nodes):**
- API Fields: ~200 data points
- Iframe Fields: ~250 data points
- **Total: ~450 data points**

---

## ✅ SUMMARY

**Layer 2 Enhanced extracts 50+ fields per workflow:**

**Technical (Build Workflows):**
- 12 core workflow fields
- 10 fields per node
- 4 fields per connection
- **Value:** CRITICAL for workflow recreation

**Spatial (Generate Layouts):**
- 15 visual layout fields
- Node positions (X/Y, width/height)
- Canvas state (zoom, pan, viewport)
- Spatial metrics (density, bounding box, center)
- **Value:** CRITICAL for optimal layout generation

**Semantic (Natural Language):**
- 8 enhanced text fields
- 154 text blocks (complex workflow)
- 23,928 characters (complex workflow)
- 5 text categories
- **Value:** HIGH for NLP training

**Visual (Multimodal):**
- 10 media fields
- Videos, images, SVGs
- Type categorization
- **Value:** MEDIUM-HIGH for multimodal training

**Total: 50+ fields, ~450 data points per complex workflow**

---

**END OF SCHEMA DOCUMENTATION**


