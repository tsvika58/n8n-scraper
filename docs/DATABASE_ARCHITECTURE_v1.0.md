# 📊 DATABASE ARCHITECTURE v1.0

**Project:** n8n Workflow Scraper  
**Database:** SQLite (single file)  
**Location:** `/data/workflows.db`  
**Version:** 1.0  
**Last Updated:** October 10, 2025

---

## ✅ **CONFIRMED: SINGLE DATABASE ARCHITECTURE**

**Answer to your question:** 

**YES - The inventory database IS the target database that we use and update throughout development and production scraping.**

**One database file, progressively enriched:**
- ✅ Currently has: 6,022 workflows in `workflow_inventory` table
- ✅ Will add: Layer 2 JSON data in additional tables
- ✅ Will add: Layer 3 content data in additional tables
- ✅ Will add: Metadata, tags, relationships, etc.

**This is the master database that grows with each scraping layer.**

---

## 🎯 **DATABASE PHILOSOPHY**

### **Single Source of Truth**
- One SQLite database file
- All workflow data in one place
- Progressive enrichment model
- Each layer adds more data to the same workflows

### **Development → Production Continuity**
- Same database structure in development and production
- Validation tasks add sample data
- Production tasks fill complete data
- No migration needed between dev and prod

---

## 📊 **CURRENT DATABASE STATE**

**File:** `/data/workflows.db`  
**Size:** ~2-3 MB (with 6,022 workflows)  
**Format:** SQLite 3  
**Status:** ✅ Operational

### **Existing Tables:**

#### **1. workflow_inventory** ✅ POPULATED
```sql
CREATE TABLE workflow_inventory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workflow_id TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    url TEXT NOT NULL,
    discovered_date TEXT NOT NULL
);

-- Current status: 6,022 records (from SCRAPE-002B)
-- Indexes: 2 (primary key + unique on workflow_id)
```

**Purpose:** Master inventory of all n8n.io workflows  
**Populated By:** SCRAPE-002B ✅  
**Status:** Complete with 6,022 workflows

---

## 🔄 **PROGRESSIVE ENRICHMENT MODEL**

### **How It Works:**

```
SCRAPE-002B → Adds workflow_inventory (6,022 rows)
     ↓
SCRAPE-003 → Adds workflow_json table (linked to inventory)
     ↓
SCRAPE-005 → Adds workflow_content table (linked to inventory)
     ↓
SCRAPE-006 → Adds OCR/transcript data (linked to inventory)
     ↓
Future → Adds analysis, tags, relationships, etc.
```

**Key Concept:** Each layer adds MORE data about the SAME workflows

---

## 📋 **PLANNED TABLE STRUCTURE**

### **Layer 1: Inventory** ✅ DONE

**Table:** `workflow_inventory`  
**Records:** 6,022  
**Status:** Complete

---

### **Layer 2: Workflow JSON** 🔄 NEXT (SCRAPE-003)

```sql
CREATE TABLE workflow_json (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workflow_id TEXT UNIQUE NOT NULL,
    json_data TEXT NOT NULL,          -- Complete workflow JSON
    node_count INTEGER,                -- Number of nodes in workflow
    connection_count INTEGER,          -- Number of connections
    has_webhook BOOLEAN DEFAULT 0,     -- Has webhook trigger
    has_schedule BOOLEAN DEFAULT 0,    -- Has schedule trigger
    extraction_date TEXT NOT NULL,
    json_size_bytes INTEGER,           -- Size of JSON data
    FOREIGN KEY (workflow_id) REFERENCES workflow_inventory(workflow_id)
);

CREATE INDEX idx_workflow_json_id ON workflow_json(workflow_id);
```

**Purpose:** Complete workflow structure and configuration  
**Populated By:** SCRAPE-003 (validation) + production scale  
**Links To:** workflow_inventory.workflow_id

---

### **Layer 3: Workflow Content** 🔄 LATER (SCRAPE-005)

```sql
CREATE TABLE workflow_content (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workflow_id TEXT UNIQUE NOT NULL,
    description TEXT,                  -- Workflow description
    full_text TEXT,                    -- All text content aggregated
    author TEXT,                       -- Workflow author
    category TEXT,                     -- Primary category
    tags TEXT,                         -- Comma-separated tags
    views INTEGER DEFAULT 0,           -- View count
    difficulty TEXT,                   -- Easy/Medium/Hard
    has_images BOOLEAN DEFAULT 0,      -- Has images
    has_videos BOOLEAN DEFAULT 0,      -- Has videos
    image_count INTEGER DEFAULT 0,     -- Number of images
    video_count INTEGER DEFAULT 0,     -- Number of videos
    extraction_date TEXT NOT NULL,
    FOREIGN KEY (workflow_id) REFERENCES workflow_inventory(workflow_id)
);

CREATE INDEX idx_workflow_content_id ON workflow_content(workflow_id);
CREATE INDEX idx_workflow_content_category ON workflow_content(category);
```

**Purpose:** Descriptive content and metadata  
**Populated By:** SCRAPE-005 (validation) + production scale  
**Links To:** workflow_inventory.workflow_id

---

### **Layer 4: Media Assets** 🔄 OPTIONAL (SCRAPE-006)

```sql
CREATE TABLE workflow_images (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workflow_id TEXT NOT NULL,
    image_url TEXT NOT NULL,
    local_path TEXT,                   -- Downloaded image path
    alt_text TEXT,                     -- Image alt text
    ocr_text TEXT,                     -- OCR extracted text
    image_type TEXT,                   -- screenshot/diagram/icon
    extraction_date TEXT NOT NULL,
    FOREIGN KEY (workflow_id) REFERENCES workflow_inventory(workflow_id)
);

CREATE TABLE workflow_videos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workflow_id TEXT NOT NULL,
    video_url TEXT NOT NULL,
    video_platform TEXT,               -- youtube/vimeo/etc
    transcript TEXT,                   -- Video transcript
    duration_seconds INTEGER,
    extraction_date TEXT NOT NULL,
    FOREIGN KEY (workflow_id) REFERENCES workflow_inventory(workflow_id)
);
```

**Purpose:** Images and videos with OCR/transcripts  
**Populated By:** SCRAPE-006 (optional)  
**Links To:** workflow_inventory.workflow_id

---

### **Layer 5: Node Details** 🔄 FUTURE

```sql
CREATE TABLE workflow_nodes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workflow_id TEXT NOT NULL,
    node_id TEXT NOT NULL,
    node_name TEXT NOT NULL,
    node_type TEXT NOT NULL,           -- n8n-nodes-base.slack, etc.
    node_version TEXT,
    parameters TEXT,                   -- JSON of node parameters
    position_x INTEGER,
    position_y INTEGER,
    FOREIGN KEY (workflow_id) REFERENCES workflow_inventory(workflow_id)
);

CREATE INDEX idx_nodes_workflow ON workflow_nodes(workflow_id);
CREATE INDEX idx_nodes_type ON workflow_nodes(node_type);
```

**Purpose:** Detailed node analysis for pattern recognition  
**Populated By:** Future analysis task  
**Links To:** workflow_inventory.workflow_id

---

## 🔗 **RELATIONSHIP MODEL**

```
workflow_inventory (6,022 workflows)
    |
    ├── workflow_json (one-to-one)
    |       └── Complete JSON structure
    |
    ├── workflow_content (one-to-one)
    |       └── Descriptive metadata
    |
    ├── workflow_images (one-to-many)
    |       └── Multiple images per workflow
    |
    ├── workflow_videos (one-to-many)
    |       └── Multiple videos per workflow
    |
    └── workflow_nodes (one-to-many)
            └── Multiple nodes per workflow
```

**All linked by:** `workflow_id` (foreign key to inventory)

---

## 📊 **QUERY EXAMPLES**

### **Complete Workflow Data:**
```sql
SELECT 
    i.workflow_id,
    i.title,
    i.url,
    j.node_count,
    j.connection_count,
    c.description,
    c.category,
    c.tags,
    c.views
FROM workflow_inventory i
LEFT JOIN workflow_json j ON i.workflow_id = j.workflow_id
LEFT JOIN workflow_content c ON i.workflow_id = c.workflow_id
WHERE i.workflow_id = '2462';
```

### **Workflows by Category:**
```sql
SELECT 
    i.title,
    i.url,
    c.category,
    c.views,
    j.node_count
FROM workflow_inventory i
JOIN workflow_content c ON i.workflow_id = c.workflow_id
JOIN workflow_json j ON i.workflow_id = j.workflow_id
WHERE c.category LIKE '%Sales%'
ORDER BY c.views DESC
LIMIT 50;
```

### **Progress Tracking:**
```sql
-- How many workflows have each layer completed?
SELECT 
    (SELECT COUNT(*) FROM workflow_inventory) as total_workflows,
    (SELECT COUNT(*) FROM workflow_json) as have_json,
    (SELECT COUNT(*) FROM workflow_content) as have_content,
    (SELECT COUNT(*) FROM workflow_images) as have_images;
```

---

## 🎯 **VALIDATION vs PRODUCTION**

### **During Validation (Current Phase):**
- ✅ workflow_inventory: ALL 6,022 workflows
- 🔄 workflow_json: 20-30 sample workflows (SCRAPE-003)
- 🔄 workflow_content: 20-30 sample workflows (SCRAPE-005)

### **During Production (Later Phase):**
- ✅ workflow_inventory: ALL 6,022 workflows (already complete)
- 🔄 workflow_json: ALL 6,022 workflows (production scale)
- 🔄 workflow_content: ALL 6,022 workflows (production scale)

**Same database. Same tables. Just more rows.**

---

## 📁 **FILE STRUCTURE**

```
/data/
├── workflows.db              # Main database (SQLite)
├── images/                   # Downloaded images (optional)
│   ├── 2462_screenshot.png
│   └── 2462_diagram.png
├── videos/                   # Video metadata (optional)
│   └── 2462_tutorial.json
└── exports/                  # Export files
    ├── workflows_complete.json
    └── workflows_complete.csv
```

---

## 🔄 **BACKUP STRATEGY**

### **During Development:**
- Database backed up after each major task completion
- Location: `.coordination/backups/`
- Format: `workflows_YYYYMMDD_HHMMSS.db`

### **During Production:**
- Hourly backups during scraping
- Daily full backups
- Keep last 7 daily backups

---

## 🎯 **SIZE PROJECTIONS**

### **Current Size:**
- workflow_inventory only: ~2-3 MB (6,022 rows)

### **Projected Size (All Layers):**

**Layer 2 (JSON):**
- Average JSON size: 50-100 KB per workflow
- Total: 6,022 × 75 KB = ~450 MB
- **Database size: ~453 MB**

**Layer 3 (Content):**
- Average content: 5-10 KB per workflow
- Total: 6,022 × 7.5 KB = ~45 MB
- **Database size: ~498 MB**

**Layer 4 (Images - if stored in DB):**
- If images stored as paths only: +5 MB
- If images stored as BLOB: +500 MB
- **Recommendation:** Store paths only

**Total Projected Size:** ~500-600 MB (manageable for SQLite)

---

## ✅ **ADVANTAGES OF SINGLE DATABASE**

1. **Simple Architecture:**
   - One file to manage
   - Easy backups
   - Easy sharing

2. **Strong Relationships:**
   - Foreign keys enforce integrity
   - Easy joins across layers
   - Consistent workflow_id references

3. **Progressive Enrichment:**
   - Add data incrementally
   - No migration between dev/prod
   - Validate small, scale large

4. **Easy Queries:**
   - SQL joins across all layers
   - Complex analysis queries simple
   - Great for data exploration

5. **Portable:**
   - Single file can be copied anywhere
   - Works on any platform with SQLite
   - Easy to share complete dataset

---

## 🚨 **IMPORTANT NOTES**

### **Database Location:**
**Always use:** `/data/workflows.db`

**Never use:**
- ❌ Temporary databases
- ❌ Multiple database files
- ❌ In-memory databases (unless testing)

### **Workflow ID:**
**Primary key across all tables:** `workflow_id` (TEXT)

**Format:** Numeric string from URL (e.g., "2462")

**Always:**
- ✅ Use workflow_id as foreign key
- ✅ Link all tables to workflow_inventory
- ✅ Ensure workflow exists in inventory before adding data

### **Data Integrity:**
**Rules:**
1. Workflow must exist in inventory before adding to other tables
2. workflow_id must be unique in inventory
3. All foreign keys enforced
4. No orphaned records allowed

---

## 📝 **DEVELOPMENT WORKFLOW**

### **For Each Scraping Task:**

1. **Query Inventory:**
   ```sql
   SELECT workflow_id, title, url 
   FROM workflow_inventory 
   LIMIT 20;  -- For validation
   ```

2. **Extract Data:**
   - Use workflow_id from inventory
   - Extract layer-specific data
   - Prepare for storage

3. **Store in Layer Table:**
   ```sql
   INSERT INTO workflow_json (workflow_id, json_data, ...)
   VALUES (?, ?, ...);
   ```

4. **Verify:**
   ```sql
   SELECT COUNT(*) FROM workflow_json 
   WHERE workflow_id IN (SELECT workflow_id FROM workflow_inventory);
   ```

---

## ✅ **ANSWER TO YOUR QUESTION**

**Q: Can the inventory database be the target database which we will use and update through development and production?**

**A: YES - 100% Confirmed**

- ✅ Single database: `/data/workflows.db`
- ✅ workflow_inventory table already has 6,022 workflows
- ✅ Each scraping task adds new tables linked to inventory
- ✅ Same database used in validation and production
- ✅ Progressive enrichment: more data about same workflows
- ✅ No migration needed between phases

**This IS the production database. We're building it progressively.**

---

**Version:** 1.0  
**Date:** October 10, 2025  
**Status:** Architecture Confirmed  
**Next:** SCRAPE-003 adds workflow_json table