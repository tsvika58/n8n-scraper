# Database Viewer Guide

## Overview
The N8N Scraper Database Viewer provides a real-time, interactive interface for monitoring scraped workflows with sortable columns and clickable workflow details.

## Features

### 🎯 Core Features
- **Sortable Columns**: Click any column header to sort workflows
- **Clickable Workflow IDs**: Direct links to detailed workflow pages
- **Numerical Sorting**: Proper integer sorting for workflow IDs (not string sorting)
- **Real-time Statistics**: Live counts and metrics
- **Search Functionality**: Filter by workflow ID or URL
- **Pagination**: Navigate large datasets efficiently

### 📊 Sortable Columns
1. **Workflow ID** - Numerical sorting (1, 2, 3... not 1, 10, 100)
2. **URL** - Alphabetical sorting
3. **Quality Score** - Numerical percentage
4. **Processing Time** - Execution duration
5. **Extracted At** - Timestamp sorting

### 🎨 UI Indicators
- **Sort Arrow**: `↕` (neutral), `↑` (ascending), `↓` (descending)
- **Active Column**: Blue highlight
- **Hover Effect**: Gray highlight on sortable columns
- **Status Badges**: Visual indicators for scraping status

## Access Points

### Main Dashboard
- **URL**: http://localhost:5004
- **Features**: Workflow list, statistics, search, pagination, sorting

### Workflow Details
- **URL**: http://localhost:5004/workflow/{workflow_id}
- **Example**: http://localhost:5004/workflow/2462
- **Features**: Complete workflow data including metadata, JSON, content, transcripts

### API Endpoints
- `/api/workflows?sort={column}&order={asc|desc}&page={n}&search={query}`
- `/api/stats` - Database statistics
- `/api/workflow/{id}` - Individual workflow data

## Technical Implementation

### Database Connection
```python
DB_CONFIG = {
    'host': 'n8n-scraper-database',
    'port': 5432,
    'database': 'n8n_scraper',
    'user': 'scraper_user',
    'password': 'scraper_pass'
}
```

### Numerical Sorting
Uses PostgreSQL `CAST(workflow_id AS INTEGER)` for proper numerical ordering:
```sql
ORDER BY CAST(workflow_id AS INTEGER) DESC
```

### Files
- **Main Script**: `scripts/db-viewer.py`
- **Port**: 5004
- **Architecture**: Python HTTP server with JavaScript frontend

## Usage Examples

### Sort by Workflow ID (Ascending)
Click "Workflow ID" header once → Shows 1, 2, 3, 4, 6, 8, 11, 13...

### Sort by Workflow ID (Descending)
Click "Workflow ID" header twice → Shows 2462, 499, 498, 497, 496...

### View Workflow Details
Click any workflow ID number → Opens detailed page with complete data

### Search Workflows
1. Enter workflow ID or URL fragment in search box
2. Click "Search" or press Enter
3. Results update automatically

## Maintenance

### Restart Database Viewer
```bash
docker exec n8n-scraper-app python -c "import os; os.system('killall python 2>/dev/null || true')"
docker exec -d n8n-scraper-app python /app/scripts/db-viewer.py
```

### Check if Running
```bash
curl http://localhost:5004/api/stats
```

### View Logs
```bash
docker logs n8n-scraper-app | grep "Database Viewer"
```

## Troubleshooting

### Port Already in Use
```bash
# Kill existing process
docker exec n8n-scraper-app python -c "import psutil; [p.kill() for p in psutil.process_iter() if 'db-viewer' in ' '.join(p.cmdline())]"
```

### Database Connection Issues
Ensure database is running:
```bash
docker exec n8n-scraper-database pg_isready
```

### Sorting Not Working
- Clear browser cache
- Check API response: `curl "http://localhost:5004/api/workflows?sort=workflow_id&order=asc"`
- Verify numerical sorting: IDs should be 1, 2, 3... not 1, 10, 100...

## Performance

### Current Metrics
- **Workflows**: 101 in database
- **Page Load**: ~200ms
- **Sort Speed**: ~100ms
- **Search**: Real-time filtering

### Optimization
- Pagination: 50 workflows per page
- Lazy loading: Only visible data fetched
- Caching: Browser caches static assets
- Index: Database indexed on workflow_id

## Future Enhancements
- [ ] Export to CSV
- [ ] Bulk operations
- [ ] Advanced filtering
- [ ] Custom columns
- [ ] Dark mode
- [ ] Mobile responsive view


