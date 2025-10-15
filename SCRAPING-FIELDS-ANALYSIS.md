# N8N Workflow Scraping - Complete Field Analysis

**Analysis Date:** October 12, 2025  
**Database Status:** 6,041 workflows (57 successfully scraped)  
**Pipeline:** 3-Layer E2E Extraction System  

## 📊 **CURRENT DATABASE SCHEMA**

### **Main Workflows Table:**
```sql
workflows (
    id              | integer                     | Primary key
    workflow_id     | character varying(50)       | n8n workflow ID (e.g., "2462")
    url             | text                        | Full n8n.io URL
    extracted_at    | timestamp                   | When we scraped it
    updated_at      | timestamp                   | Last update time
    processing_time | double precision            | Total extraction time
    quality_score   | double precision            | Overall quality (0-100)
    layer1_success  | boolean                     | Metadata extraction success
    layer2_success  | boolean                     | JSON extraction success
    layer3_success  | boolean                     | Content extraction success
    error_message   | text                        | Error details if failed
    retry_count     | integer                     | Number of retry attempts
    last_scraped_at | timestamp                   | Last successful scrape
    created_at      | timestamp                   | Record creation time
)
```

### **Workflow Metadata Table:**
```sql
workflow_metadata (
    id                  | integer                     | Primary key
    workflow_id         | character varying(50)       | Foreign key to workflows
    title               | text                        | Workflow title
    description         | text                        | Workflow description
    use_case            | text                        | Use case description
    author_name         | character varying(255)      | Author name
    author_url          | text                        | Author profile URL
    views               | integer                     | Number of views
    shares              | integer                     | Number of shares
    categories          | jsonb                       | Categories array
    tags                | jsonb                       | Tags array
    workflow_created_at | timestamp                   | When workflow was created
    workflow_updated_at | timestamp                   | When workflow was updated
    extracted_at        | timestamp                   | When we extracted it
    raw_metadata        | jsonb                       | Raw extracted data
)
```

### **Workflow Content Table:**
```sql
workflow_content (
    id                 | integer                     | Primary key
    workflow_id        | character varying(50)       | Foreign key to workflows
    explainer_text     | text                        | Explainer text content
    explainer_html     | text                        | Explainer HTML content
    setup_instructions | text                        | Setup instructions
    use_instructions   | text                        | Usage instructions
    has_videos         | boolean                     | Contains videos
    video_count        | integer                     | Number of videos
    has_iframes        | boolean                     | Contains iframes
    iframe_count       | integer                     | Number of iframes
    raw_content        | jsonb                       | Raw content data
    extracted_at       | timestamp                   | When we extracted it
)
```

### **Workflow Structure Table:**
```sql
workflow_structure (
    id               | integer                     | Primary key
    workflow_id      | character varying(50)       | Foreign key to workflows
    node_count       | integer                     | Number of nodes
    connection_count | integer                     | Number of connections
    node_types       | jsonb                       | Array of node types used
    extraction_type  | character varying(50)       | How we extracted it
    fallback_used    | boolean                     | Whether fallback was used
    workflow_json    | jsonb                       | Complete workflow JSON
    extracted_at     | timestamp                   | When we extracted it
)
```

### **Video Transcripts Table:**
```sql
video_transcripts (
    id          | integer                     | Primary key
    workflow_id | character varying(50)       | Foreign key to workflows
    video_url   | text                        | YouTube video URL
    title       | text                        | Video title
    transcript  | text                        | Full transcript text
    duration    | integer                     | Video duration in seconds
    extracted_at| timestamp                   | When we extracted it
)
```

---

## 🎯 **WHAT WE'RE CURRENTLY SCRAPING**

### **✅ Layer 1: Page Metadata (19 fields)**
From `src/scrapers/layer1_metadata.py`:

1. **Basic Info:**
   - `title` - Workflow title
   - `description` - Workflow description
   - `use_case` - Use case description
   - `author_name` - Author name
   - `author_url` - Author profile URL

2. **Categorization:**
   - `primary_category` - Main category (e.g., "Sales", "Marketing")
   - `secondary_categories` - Additional categories
   - `node_tags` - Node-specific tags
   - `general_tags` - General workflow tags
   - `difficulty_level` - Complexity level

3. **Engagement Metrics:**
   - `views` - Number of views
   - `upvotes` - Number of upvotes/likes
   - `shares` - Number of shares

4. **Dates:**
   - `created_date` - When workflow was created
   - `updated_date` - When workflow was last updated

5. **Technical Info:**
   - `node_count` - Number of nodes
   - `connection_count` - Number of connections
   - `estimated_runtime` - Estimated execution time

6. **Content Flags:**
   - `has_videos` - Contains videos
   - `has_images` - Contains images
   - `has_documentation` - Has documentation

### **✅ Layer 2: Workflow JSON (Complete workflow structure)**
From `src/scrapers/layer2_json.py`:

1. **Workflow Structure:**
   - `workflow_json` - Complete n8n workflow JSON
   - `node_types` - Array of all node types used
   - `node_count` - Total number of nodes
   - `connection_count` - Total connections
   - `extraction_type` - How we extracted it
   - `fallback_used` - Whether fallback method was used

### **✅ Layer 3: Explainer Content (Rich content)**
From `src/scrapers/layer3_explainer.py`:

1. **Content Extraction:**
   - `explainer_text` - Plain text explainer
   - `explainer_html` - HTML explainer content
   - `setup_instructions` - Setup instructions
   - `use_instructions` - Usage instructions

2. **Media Analysis:**
   - `video_count` - Number of videos
   - `iframe_count` - Number of iframes
   - `has_videos` - Boolean flag
   - `has_iframes` - Boolean flag

### **✅ Multimodal Processing:**
From `src/scrapers/multimodal_processor.py`:

1. **Image Processing:**
   - OCR text extraction from images
   - Image analysis and categorization

### **✅ Video Transcripts:**
From `src/scrapers/transcript_extractor.py`:

1. **Video Content:**
   - `video_url` - YouTube video URL
   - `title` - Video title
   - `transcript` - Full transcript text
   - `duration` - Video duration

---

## 🔍 **CATEGORIES ANALYSIS**

### **❌ Current Issue: Categories Not Populated**
Based on database analysis:
- **Categories field exists** in `workflow_metadata.categories` (jsonb)
- **Tags field exists** in `workflow_metadata.tags` (jsonb)
- **But all are empty arrays `[]`** in current data

### **✅ What We Should Be Extracting:**
From n8n.io workflow pages, we should extract:

1. **Categories (Primary/Secondary):**
   - Sales
   - Marketing
   - Operations
   - Development
   - Customer Support
   - Data Processing
   - Automation
   - Integration
   - etc.

2. **Tags (Node-specific and General):**
   - Node types (e.g., "HTTP Request", "Google Sheets", "Slack")
   - Use cases (e.g., "Lead Generation", "Data Sync", "Notification")
   - Complexity (e.g., "Beginner", "Intermediate", "Advanced")

---

## 📋 **COMPLETE FIELD INVENTORY**

### **✅ Fields We ARE Scraping (47 total):**

#### **Core Workflow Data (8 fields):**
- workflow_id, url, extracted_at, updated_at, processing_time, quality_score, error_message, retry_count

#### **Layer 1 Metadata (19 fields):**
- title, description, use_case, author_name, author_url, primary_category, secondary_categories, node_tags, general_tags, difficulty_level, views, upvotes, shares, created_date, updated_date, node_count, connection_count, estimated_runtime, has_videos, has_images, has_documentation

#### **Layer 2 Structure (6 fields):**
- workflow_json, node_types, node_count, connection_count, extraction_type, fallback_used

#### **Layer 3 Content (6 fields):**
- explainer_text, explainer_html, setup_instructions, use_instructions, video_count, iframe_count

#### **Video Transcripts (4 fields):**
- video_url, title, transcript, duration

#### **Multimodal (4 fields):**
- OCR text, image analysis, media categorization, content flags

### **❓ Fields We MIGHT NOT Be Scraping:**

1. **Advanced Metadata:**
   - Workflow version history
   - Fork/clone relationships
   - Community ratings beyond upvotes
   - Detailed node configuration
   - Execution statistics
   - Performance metrics

2. **Extended Content:**
   - Comments/discussions
   - Related workflows
   - User reviews
   - Implementation examples
   - Troubleshooting guides

3. **Technical Details:**
   - Node configuration details
   - Credential requirements
   - API endpoint details
   - Rate limiting information
   - Error handling patterns

---

## 🚨 **CRITICAL FINDING: Categories Not Being Extracted**

### **Problem:**
- Database has `categories` and `tags` fields
- But all workflows show empty arrays `[]`
- This means our Layer 1 extraction isn't capturing categories/tags

### **Impact:**
- Cannot categorize workflows (Sales, Marketing, etc.)
- Cannot filter by use case or complexity
- Missing key metadata for AI training

### **Solution Needed:**
1. **Debug Layer 1 extraction** - Why aren't categories being captured?
2. **Fix category extraction** - Ensure we get proper categorization
3. **Re-scrape existing workflows** - Update with proper categories
4. **Validate extraction** - Confirm categories are being stored

---

## 🎯 **RECOMMENDATIONS**

### **Immediate Actions:**
1. **Fix category extraction** in Layer 1 metadata extractor
2. **Validate existing data** - Check why categories are empty
3. **Re-scrape sample workflows** to test category extraction
4. **Update database viewer** to show categories properly

### **Long-term Enhancements:**
1. **Add more metadata fields** (version history, forks, ratings)
2. **Enhance content extraction** (comments, discussions)
3. **Add technical analysis** (performance metrics, complexity scoring)
4. **Implement workflow relationships** (related workflows, dependencies)

---

## 📊 **CURRENT EXTRACTION STATUS**

- **Total Fields Available:** ~47 fields across 5 tables
- **Successfully Extracted:** 57 workflows (0.90%)
- **Fields Working:** Most fields except categories/tags
- **Critical Issue:** Categories and tags not being extracted
- **Data Quality:** Good for successfully scraped workflows

**Next Priority:** Fix category extraction to enable proper workflow categorization and filtering.





