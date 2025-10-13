#!/usr/bin/env python3
"""
Validate workflow URLs to identify empty/404 pages.

Tests URLs from the database to see if they return valid pages or errors.
"""

import sys
sys.path.insert(0, '/app')

import requests
import time
from src.storage.database import get_session
from sqlalchemy import text
from loguru import logger

def check_url_status(workflow_id, url):
    """Check if a URL returns a valid page."""
    try:
        response = requests.get(url, allow_redirects=True, timeout=10)
        
        # Check for 404 or other errors
        if response.status_code == 404:
            return workflow_id, url, 'NOT_FOUND', response.status_code
        elif response.status_code >= 400:
            return workflow_id, url, 'ERROR', response.status_code
        
        # Check if page content suggests it's empty/deleted
        content = response.text.lower()
        
        if 'workflow not found' in content or 'page not found' in content:
            return workflow_id, url, 'NOT_FOUND_CONTENT', response.status_code
        elif 'this workflow has been deleted' in content:
            return workflow_id, url, 'DELETED', response.status_code
        elif len(content) < 1000:  # Very short page
            return workflow_id, url, 'SUSPICIOUSLY_SHORT', response.status_code
        
        return workflow_id, url, 'OK', response.status_code
        
    except requests.Timeout:
        return workflow_id, url, 'TIMEOUT', None
    except Exception as e:
        return workflow_id, url, f'ERROR: {str(e)[:50]}', None

def validate_urls(workflow_urls):
    """Validate URLs one by one."""
    results = []
    
    for i, (workflow_id, url) in enumerate(workflow_urls, 1):
        result = check_url_status(workflow_id, url)
        results.append(result)
        
        if i % 10 == 0:
            logger.info(f"Validated {i}/{len(workflow_urls)} URLs")
        
        # Small delay to be polite
        time.sleep(0.5)
    
    return results

def get_suspicious_workflows():
    """Get workflows with suspicious characteristics."""
    with get_session() as session:
        result = session.execute(text('''
            SELECT w.workflow_id, w.url, wm.title
            FROM workflows w
            JOIN workflow_metadata wm ON w.workflow_id = wm.workflow_id
            WHERE LENGTH(wm.title) < 10
            ORDER BY w.workflow_id::integer
        '''))
        
        return [(row[0], row[1], row[2]) for row in result]

def main():
    logger.info("Starting URL validation...")
    
    # Get suspicious workflows
    workflows = get_suspicious_workflows()
    logger.info(f"Found {len(workflows)} suspicious workflows to validate")
    
    if not workflows:
        logger.success("No suspicious workflows found!")
        return
    
    # Extract just ID and URL for validation
    workflow_urls = [(wf[0], wf[1]) for wf in workflows]
    
    # Validate URLs
    logger.info("Validating URLs...")
    results = validate_urls(workflow_urls)
    
    # Analyze results
    print("\n" + "="*70)
    print("URL VALIDATION REPORT")
    print("="*70)
    print()
    
    status_counts = {}
    invalid_urls = []
    
    for workflow_id, url, status, status_code in results:
        if status not in status_counts:
            status_counts[status] = 0
        status_counts[status] += 1
        
        if status != 'OK':
            invalid_urls.append((workflow_id, url, status, status_code))
    
    print("📊 STATUS SUMMARY:")
    for status, count in sorted(status_counts.items()):
        print(f"  {status}: {count}")
    print()
    
    if invalid_urls:
        print(f"❌ INVALID/PROBLEMATIC URLs ({len(invalid_urls)}):")
        print()
        for workflow_id, url, status, status_code in invalid_urls[:20]:
            print(f"  ID {workflow_id}: {status} (HTTP {status_code})")
            print(f"    {url}")
            print()
        
        if len(invalid_urls) > 20:
            print(f"  ... and {len(invalid_urls) - 20} more")
        print()
        
        # Save to file
        output_file = '/app/data/invalid-urls.txt'
        with open(output_file, 'w') as f:
            f.write("# Workflows with invalid/problematic URLs\n")
            f.write(f"# Total: {len(invalid_urls)}\n\n")
            for workflow_id, url, status, status_code in invalid_urls:
                f.write(f"{workflow_id}\t{status}\t{status_code}\t{url}\n")
        
        logger.success(f"Saved invalid URLs to: {output_file}")
    else:
        print("✅ All URLs are valid!")
    
    print()

if __name__ == "__main__":
    main()

