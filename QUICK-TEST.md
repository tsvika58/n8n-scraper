# Quick Dashboard Test Instructions

## What Was Fixed
The dashboard now properly tracks live scraping sessions by:
1. Monitoring workflows extracted in the last 5 minutes as the "current session"
2. Setting `is_active = true` when there's session activity
3. Showing real-time progress during and after scraping (persists for 5 minutes)

## Run the Test

### Step 1: Restart Dashboard
```bash
docker exec n8n-scraper-app pkill -f realtime-dashboard
sleep 2
docker exec n8n-scraper-app python /app/scripts/realtime-dashboard-enhanced.py &
```

### Step 2: Open Dashboard
Open http://localhost:5001 in your browser

### Step 3: Run Live Test
```bash
sleep 3
docker exec n8n-scraper-app python /app/scripts/simple_live_test.py
```

### Step 4: Watch Dashboard
You should see:
- **Status Badge**: Changes from "IDLE" to "● SCRAPING"
- **Live Progress Bar**: Shows green (success) segments appearing
- **Workflow Count**: Shows "5 / 5 workflows" or current progress
- **Legend**: Updates with success/failed/empty/pending counts

### Step 5: After Test Completes
- Stats persist for 5 minutes showing the session results
- After 5 minutes, dashboard returns to idle state

## Expected Results

### During Scraping (30-40 seconds)
```
LIVE SCRAPING STATUS: ● SCRAPING (X concurrent)
Progress: [████░░░░░] X / 5 workflows
✅ Success: X  ❌ Failed: 0  🗑️ Empty: 0  ⏳ Pending: X
```

### After Scraping (5 minutes)
```
LIVE SCRAPING STATUS: ● SCRAPING (0 concurrent)
Progress: [████████] 5 / 5 workflows
✅ Success: 5  ❌ Failed: 0  🗑️ Empty: 0  ⏳ Pending: 0
```

### Idle (after 5 minutes)
```
LIVE SCRAPING STATUS: IDLE
Progress: [░░░░░░░░] 0 / 0 workflows
✅ Success: 0  ❌ Failed: 0  🗑️ Empty: 0  ⏳ Pending: 0
```

## Troubleshooting

### Dashboard shows idle during test
- Wait 5 seconds after starting dashboard before running test
- Check dashboard is actually running: `docker exec n8n-scraper-app ps aux | grep realtime`

### No workflows being scraped
- Check database connection
- Verify test script is using correct workflow IDs

### Session stats not persisting
- Check system time is correct
- Verify PostgreSQL is running: `docker ps | grep postgres`




