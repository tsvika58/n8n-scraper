#!/usr/bin/env python3
"""
Debug session tracking
"""
import subprocess
import time

print("🔍 DEBUGGING SESSION TRACKING")
print("="*60)

# Check recent workflows in database
print("\n📍 Checking recent workflows...")
result = subprocess.run([
    "docker", "exec", "n8n-scraper-app", 
    "psql", "-h", "n8n-scraper-database", "-U", "n8n_scraper", "-d", "n8n_scraper",
    "-c", """
    SELECT 
        workflow_id,
        extracted_at,
        quality_score,
        error_message,
        NOW() - extracted_at as time_ago
    FROM workflows 
    WHERE extracted_at > NOW() - INTERVAL '10 minutes'
    ORDER BY extracted_at DESC 
    LIMIT 10;
    """
], capture_output=True, text=True)

print(result.stdout)

# Check session stats query
print("\n📍 Checking session stats query...")
result = subprocess.run([
    "docker", "exec", "n8n-scraper-app", 
    "psql", "-h", "n8n-scraper-database", "-U", "n8n_scraper", "-d", "n8n_scraper",
    "-c", """
    SELECT 
        COUNT(*) FILTER (WHERE quality_score > 0) as session_success,
        COUNT(*) FILTER (WHERE error_message IS NOT NULL AND error_message != '') as session_failed,
        0 as session_empty,
        COUNT(*) as session_total
    FROM workflows 
    WHERE extracted_at > NOW() - INTERVAL '5 minutes';
    """
], capture_output=True, text=True)

print(result.stdout)

# Check API response
print("\n📍 Checking API response...")
result = subprocess.run([
    "curl", "-s", "http://localhost:5001/api/stats"
], capture_output=True, text=True)

if result.returncode == 0:
    import json
    try:
        data = json.loads(result.stdout)
        live_data = data.get('live_scraping', {})
        print(f"is_active: {live_data.get('is_active')}")
        print(f"session_success: {live_data.get('current_session_success')}")
        print(f"session_failed: {live_data.get('current_session_failed')}")
        print(f"session_total: {live_data.get('current_session_total')}")
        print(f"concurrent_count: {live_data.get('concurrent_count')}")
    except:
        print("Failed to parse API response")
else:
    print("Failed to get API response")
