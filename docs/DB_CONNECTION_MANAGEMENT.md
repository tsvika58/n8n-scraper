# Database Connection Management Guide

## Overview
This guide explains how the N8N Scraper manages database connections to prevent redundant connections, ensure proper cleanup, and maintain optimal performance.

## Architecture

### Connection Manager (`src/storage/connection_manager.py`)

The `ConnectionManager` class provides:
- **Connection Pooling**: Reuses connections efficiently
- **Automatic Cleanup**: Closes idle connections
- **Process Tracking**: Prevents duplicate processes
- **Health Checks**: Monitors database connectivity
- **Resource Limits**: Enforces maximum connections

### Key Features

#### 1. Connection Pooling
```python
MAX_CONNECTIONS = 10  # Maximum connections per container
MAX_OVERFLOW = 5      # Additional connections during peak
POOL_TIMEOUT = 30     # Seconds to wait for connection
POOL_RECYCLE = 3600   # Recycle connections after 1 hour
```

**Benefits:**
- Reuses existing connections instead of creating new ones
- Prevents connection exhaustion
- Automatically closes stale connections
- Verifies connections before use (`pool_pre_ping=True`)

#### 2. Process Management

**Prevent Duplicate Processes:**
```python
from src.storage.connection_manager import prevent_duplicate_process

# Check for duplicates (fail if found)
if not prevent_duplicate_process('layer1_5_production_scraper.py'):
    print("Already running!")
    sys.exit(1)

# Or force kill duplicates
prevent_duplicate_process('layer1_5_production_scraper.py', force=True)
```

**Register Processes:**
```python
from src.storage.connection_manager import connection_manager

# Register your process
connection_manager.register_process('my_scraper')

# Unregister when done
connection_manager.unregister_process()
```

#### 3. Automatic Cleanup

**Startup Cleanup:**
```python
from src.storage.connection_manager import startup_cleanup

# Run before starting any scraper
startup_cleanup()
# - Cleans up zombie processes
# - Checks connection pool health
# - Verifies database connectivity
```

**Shutdown Cleanup:**
```python
from src.storage.connection_manager import shutdown_cleanup

# Run when shutting down
shutdown_cleanup()
# - Closes all database connections
# - Cleans up zombie processes
# - Unregisters process
```

#### 4. Health Monitoring

**Check Pool Status:**
```python
status = connection_manager.get_pool_status()
print(status)
# {
#     'status': 'active',
#     'size': 10,
#     'checked_in': 8,
#     'checked_out': 2,
#     'overflow': 0,
#     'max_connections': 10,
#     'max_overflow': 5
# }
```

**Health Check:**
```python
if connection_manager.health_check():
    print("✅ Database healthy")
else:
    print("❌ Database unhealthy")
```

**Active Processes:**
```python
processes = connection_manager.get_active_processes()
for proc in processes:
    print(f"PID {proc['pid']}: {proc['name']} - {proc['status']}")
```

## Usage

### Method 1: Safe Startup Script (Recommended)

Use the safe startup script that handles all cleanup automatically:

```bash
# Start L1.5 scraper
docker exec n8n-scraper-app python /app/scripts/start_scraper_safe.py \
    layer1_5_production_scraper.py --all

# Start L3 scraper
docker exec n8n-scraper-app python /app/scripts/start_scraper_safe.py \
    run_layer3_production.py --test
```

**What it does:**
1. ✅ Runs startup cleanup
2. ✅ Checks for duplicate processes (kills if found)
3. ✅ Registers the process
4. ✅ Launches the scraper
5. ✅ Runs shutdown cleanup when done

### Method 2: Manual Integration

Integrate connection management into your scraper:

```python
#!/usr/bin/env python3
import sys
sys.path.append('/app')

from src.storage.connection_manager import (
    connection_manager,
    prevent_duplicate_process,
    startup_cleanup,
    shutdown_cleanup
)
import atexit
import signal

def signal_handler(signum, frame):
    shutdown_cleanup()
    sys.exit(0)

def main():
    # Register signal handlers
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    atexit.register(shutdown_cleanup)
    
    # Startup cleanup
    startup_cleanup()
    
    # Prevent duplicates
    if not prevent_duplicate_process('my_scraper.py', force=True):
        sys.exit(1)
    
    # Register process
    connection_manager.register_process('my_scraper')
    
    try:
        # Your scraper code here
        with connection_manager.get_session() as session:
            result = session.execute(text("SELECT * FROM workflows"))
            # ...
    
    finally:
        # Cleanup
        shutdown_cleanup()

if __name__ == "__main__":
    main()
```

### Method 3: Using Existing Database Module

The connection manager is integrated into the existing `database.py`:

```python
from src.storage.database import get_session

# This now uses the connection manager automatically
with get_session() as session:
    result = session.execute(text("SELECT * FROM workflows"))
```

## Best Practices

### 1. Always Use Context Managers
```python
# ✅ GOOD - Automatic cleanup
with connection_manager.get_session() as session:
    result = session.execute(text("SELECT * FROM workflows"))

# ❌ BAD - Manual cleanup required
session = connection_manager.get_session()
result = session.execute(text("SELECT * FROM workflows"))
session.close()  # Easy to forget!
```

### 2. Run Cleanup on Startup
```python
# ✅ GOOD - Clean state
startup_cleanup()
# Your scraper code

# ❌ BAD - May have stale connections
# Your scraper code (no cleanup)
```

### 3. Handle Signals Gracefully
```python
# ✅ GOOD - Proper cleanup on interrupt
import signal
import atexit

signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)
atexit.register(shutdown_cleanup)

# ❌ BAD - Connections left open on Ctrl+C
# No signal handlers
```

### 4. Prevent Duplicate Processes
```python
# ✅ GOOD - Check before starting
if not prevent_duplicate_process('my_scraper.py', force=True):
    sys.exit(1)

# ❌ BAD - Multiple instances competing for resources
# No duplicate check
```

## Monitoring

### Check Active Connections

```bash
# From host
docker exec n8n-scraper-app python -c "
from src.storage.connection_manager import get_database_connection_count
print(f'Active connections: {get_database_connection_count()}')
"
```

### Check Pool Status

```bash
docker exec n8n-scraper-app python -c "
from src.storage.connection_manager import connection_manager
import json
print(json.dumps(connection_manager.get_pool_status(), indent=2))
"
```

### Check Active Processes

```bash
docker exec n8n-scraper-app python -c "
from src.storage.connection_manager import connection_manager
import json
processes = connection_manager.get_active_processes()
print(json.dumps(processes, indent=2))
"
```

### Health Check

```bash
docker exec n8n-scraper-app python -c "
from src.storage.connection_manager import connection_manager
if connection_manager.health_check():
    print('✅ Database healthy')
else:
    print('❌ Database unhealthy')
"
```

## Troubleshooting

### Problem: "Too many connections"

**Cause:** Connection pool exhausted

**Solution:**
```python
# Check pool status
status = connection_manager.get_pool_status()
print(f"Checked out: {status['checked_out']}/{status['max_connections']}")

# Clean up idle connections
connection_manager.cleanup_idle_connections()
```

### Problem: "Process already running"

**Cause:** Duplicate process detected

**Solution:**
```bash
# Force kill duplicate and start
docker exec n8n-scraper-app python /app/scripts/start_scraper_safe.py \
    layer1_5_production_scraper.py --all
# (Uses force=True internally)
```

### Problem: Zombie processes accumulating

**Cause:** Processes not properly cleaned up

**Solution:**
```python
from src.storage.connection_manager import cleanup_zombie_processes

# Manual cleanup
zombie_count = cleanup_zombie_processes()
print(f"Cleaned up {zombie_count} zombies")
```

### Problem: Stale connections

**Cause:** Connections idle for too long

**Solution:**
```python
# Connections automatically recycled after 1 hour
# Or manually refresh:
connection_manager.cleanup_idle_connections()
```

## Configuration

### Environment Variables

```bash
# Database connection
DATABASE_URL=postgresql://user:pass@host:5432/db

# Connection pool (optional - defaults shown)
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=5
DB_POOL_TIMEOUT=30
DB_POOL_RECYCLE=3600
```

### Adjusting Limits

Edit `src/storage/connection_manager.py`:

```python
class ConnectionManager:
    MAX_CONNECTIONS = 10  # Increase for more concurrent scrapers
    MAX_OVERFLOW = 5      # Increase for burst capacity
    POOL_TIMEOUT = 30     # Increase if connections slow
    POOL_RECYCLE = 3600   # Decrease for more frequent refresh
```

## Integration Checklist

When creating a new scraper:

- [ ] Import connection manager utilities
- [ ] Add signal handlers (SIGTERM, SIGINT)
- [ ] Register atexit cleanup
- [ ] Run `startup_cleanup()` before scraping
- [ ] Check for duplicates with `prevent_duplicate_process()`
- [ ] Register process with `connection_manager.register_process()`
- [ ] Use `with connection_manager.get_session()` for queries
- [ ] Run `shutdown_cleanup()` when done
- [ ] Test with safe startup script

## Examples

### Complete Scraper Template

```python
#!/usr/bin/env python3
"""
My Scraper - Template with proper connection management
"""

import sys
import signal
import atexit
sys.path.append('/app')

from src.storage.connection_manager import (
    connection_manager,
    prevent_duplicate_process,
    startup_cleanup,
    shutdown_cleanup
)
from sqlalchemy import text
from loguru import logger


def signal_handler(signum, frame):
    """Handle shutdown signals"""
    logger.info("Shutting down...")
    shutdown_cleanup()
    sys.exit(0)


async def main():
    """Main scraper logic"""
    
    # Setup
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    atexit.register(shutdown_cleanup)
    
    # Startup cleanup
    startup_cleanup()
    
    # Prevent duplicates
    if not prevent_duplicate_process('my_scraper.py', force=True):
        logger.error("Failed to start - duplicate process")
        sys.exit(1)
    
    # Register
    connection_manager.register_process('my_scraper')
    
    try:
        # Your scraping logic
        logger.info("Starting scraper...")
        
        with connection_manager.get_session() as session:
            workflows = session.execute(text("""
                SELECT workflow_id, url FROM workflows LIMIT 10
            """)).fetchall()
            
            for workflow_id, url in workflows:
                logger.info(f"Processing {workflow_id}...")
                # Your extraction logic here
        
        logger.info("✅ Scraping complete")
    
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        raise
    
    finally:
        shutdown_cleanup()


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

### Quick Health Check Script

```python
#!/usr/bin/env python3
"""Quick health check for database connections"""

import sys
sys.path.append('/app')

from src.storage.connection_manager import (
    connection_manager,
    get_database_connection_count
)

print("🔍 Database Connection Health Check")
print("=" * 50)

# Health check
healthy = connection_manager.health_check()
print(f"Database: {'✅ Healthy' if healthy else '❌ Unhealthy'}")

# Pool status
status = connection_manager.get_pool_status()
print(f"\nConnection Pool:")
print(f"  Size: {status['size']}")
print(f"  Checked In: {status['checked_in']}")
print(f"  Checked Out: {status['checked_out']}")
print(f"  Overflow: {status['overflow']}")
print(f"  Max: {status['max_connections']} + {status['max_overflow']}")

# Active connections
conn_count = get_database_connection_count()
print(f"\nTotal Active Connections: {conn_count}")

# Active processes
processes = connection_manager.get_active_processes()
print(f"\nActive Processes: {len(processes)}")
for proc in processes:
    print(f"  - PID {proc['pid']}: {proc['name']}")
    print(f"    Status: {proc['status']}")
    print(f"    CPU: {proc['cpu_percent']:.1f}%")
    print(f"    Memory: {proc['memory_mb']:.1f} MB")

print("=" * 50)
```

## Summary

The connection management system ensures:

1. ✅ **No redundant connections** - Connection pooling reuses connections
2. ✅ **No duplicate processes** - Automatic detection and prevention
3. ✅ **Proper cleanup** - Automatic cleanup on startup and shutdown
4. ✅ **Health monitoring** - Real-time status and health checks
5. ✅ **Resource limits** - Enforced maximum connections per container
6. ✅ **Zombie cleanup** - Automatic cleanup of dead processes

**Use the safe startup script for hassle-free scraping:**
```bash
docker exec n8n-scraper-app python /app/scripts/start_scraper_safe.py \
    your_scraper.py --args
```

