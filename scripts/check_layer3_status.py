#!/usr/bin/env python3
"""Check Layer 3 status and recent activity"""

import sys
sys.path.append('/app')

from src.storage.database import get_session
from sqlalchemy import text
from datetime import datetime, timedelta

with get_session() as session:
    # Check recent Layer 3 activity
    result = session.execute(text("""
        SELECT 
            COUNT(*) FILTER (WHERE layer3_success = true) as completed,
            COUNT(*) FILTER (WHERE layer3_extracted_at > NOW() - INTERVAL '5 minutes') as last_5min,
            COUNT(*) FILTER (WHERE layer3_extracted_at > NOW() - INTERVAL '1 minute') as last_1min,
            MAX(layer3_extracted_at) as last_update,
            COUNT(*) FILTER (WHERE layer3_success = false) as failed,
            COUNT(*) as total_records
        FROM workflow_content
    """)).fetchone()
    
    print('=' * 80)
    print('LAYER 3 ACTIVITY CHECK')
    print('=' * 80)
    print(f'Total records in workflow_content: {result[5]}')
    print(f'Total completed (layer3_success=true): {result[0]}')
    print(f'Updates in last 5 minutes: {result[1]}')
    print(f'Updates in last 1 minute: {result[2]}')
    print(f'Last update timestamp: {result[3]}')
    print(f'Total failed: {result[4]}')
    
    # Check what's being processed
    print('\n' + '=' * 80)
    print('LAYER 3 PROCESSING STATUS')
    print('=' * 80)
    status = session.execute(text("""
        SELECT 
            COUNT(*) FILTER (WHERE layer3_success IS NULL) as not_started,
            COUNT(*) FILTER (WHERE layer3_success = true) as success,
            COUNT(*) FILTER (WHERE layer3_success = false) as failed
        FROM workflow_content
    """)).fetchone()
    
    print(f'Not started: {status[0]}')
    print(f'Successful: {status[1]}')
    print(f'Failed: {status[2]}')
    
    # Check most recent successful extractions
    print('\n' + '=' * 80)
    print('RECENT SUCCESSFUL LAYER 3 EXTRACTIONS (Last 10)')
    print('=' * 80)
    recent = session.execute(text("""
        SELECT 
            workflow_id, 
            layer3_extracted_at,
            video_count,
            transcript_count,
            quality_score
        FROM workflow_content
        WHERE layer3_success = true
        ORDER BY layer3_extracted_at DESC
        LIMIT 10
    """)).fetchall()
    
    if recent:
        for rec in recent:
            print(f'Workflow {rec[0]}: {rec[1]} | Videos: {rec[2]}, Transcripts: {rec[3]}, Quality: {rec[4]}')
    else:
        print('No successful extractions found')

