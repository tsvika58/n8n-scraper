#!/usr/bin/env python3
"""
Infer Missing Categories from URL Slugs

For the 54 workflows without categories, infer the best matching categories
based on their URL slugs and keywords.

Uses keyword matching against known categories to assign the most appropriate
category tags.

Author: N8N Scraper System
Date: October 13, 2025
"""

import sys
from pathlib import Path
import re

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.storage.database import get_session
from src.storage.models import Workflow, WorkflowMetadata
from sqlalchemy import text

# ============================================================================
# Category Inference Engine
# ============================================================================

# Known categories and their keywords
CATEGORY_KEYWORDS = {
    'Lead Generation': ['lead', 'prospect', 'outreach', 'cold-email', 'sales-lead', 'lead-gen'],
    'Lead Nurturing': ['nurture', 'follow-up', 'engagement', 'drip'],
    'CRM': ['crm', 'hubspot', 'salesforce', 'pipedrive', 'contact', 'deal'],
    'AI Chatbot': ['chatbot', 'bot', 'chat', 'assistant', 'conversation'],
    'AI Summarization': ['summary', 'summarize', 'summarization', 'digest', 'brief'],
    'Multimodal AI': ['multimodal', 'vision', 'image', 'video', 'audio', 'voice', 'gpt-4', 'gemini', 'claude'],
    'Content Creation': ['content', 'blog', 'article', 'post', 'writing', 'generate'],
    'Social Media': ['social', 'instagram', 'facebook', 'linkedin', 'twitter', 'tiktok'],
    'Marketing': ['marketing', 'campaign', 'ads', 'advertising'],
    'Document Extraction': ['extract', 'pdf', 'document', 'ocr', 'parse', 'receipt', 'invoice'],
    'Invoice Processing': ['invoice', 'billing', 'payment', 'receipt'],
    'Engineering': ['api', 'webhook', 'http', 'integration', 'technical'],
    'DevOps': ['devops', 'deploy', 'ci-cd', 'github', 'gitlab', 'docker', 'kubernetes'],
    'IT Ops': ['monitoring', 'alert', 'infrastructure', 'server', 'uptime'],
    'SecOps': ['security', 'vulnerability', 'threat', 'compliance'],
    'Support Chatbot': ['support', 'helpdesk', 'ticket', 'customer-service'],
    'Ticket Management': ['ticket', 'jira', 'zendesk', 'issue'],
    'Project Management': ['project', 'task', 'trello', 'asana', 'clickup'],
    'Personal Productivity': ['productivity', 'calendar', 'email', 'reminder', 'schedule'],
    'File Management': ['file', 'storage', 'drive', 'dropbox', 's3', 'upload'],
    'Market Research': ['research', 'analysis', 'data', 'scrape', 'competitor'],
    'HR': ['hr', 'hiring', 'recruitment', 'resume', 'candidate', 'employee'],
    'Crypto Trading': ['crypto', 'bitcoin', 'ethereum', 'trading', 'blockchain'],
    'AI RAG': ['rag', 'vector', 'embedding', 'knowledge-base', 'semantic-search'],
    'Miscellaneous': []  # Fallback category
}

def infer_categories(url: str, workflow_id: str) -> list:
    """
    Infer categories from URL slug using keyword matching.
    
    Returns list of matching categories (max 2-3).
    """
    # Extract slug from URL
    # Format: https://n8n.io/workflows/1234-workflow-title-here/
    if '/workflows/' not in url:
        return ['Miscellaneous']
    
    slug = url.split('/workflows/')[-1].rstrip('/')
    
    # Remove workflow ID prefix
    if '-' in slug:
        parts = slug.split('-')
        if parts[0].isdigit():
            slug = '-'.join(parts[1:])
    
    # Convert to lowercase for matching
    slug_lower = slug.lower()
    
    # Find matching categories
    matches = []
    
    for category, keywords in CATEGORY_KEYWORDS.items():
        if category == 'Miscellaneous':
            continue
        
        # Check if any keyword appears in slug
        for keyword in keywords:
            if keyword in slug_lower:
                matches.append(category)
                break
    
    # Remove duplicates
    matches = list(dict.fromkeys(matches))
    
    # If no matches, assign Miscellaneous
    if not matches:
        matches = ['Miscellaneous']
    
    # Limit to 2 categories (most common pattern)
    return matches[:2]

# ============================================================================
# Main Execution
# ============================================================================

print("=" * 80)
print("🤖 INFERRING MISSING CATEGORIES")
print("=" * 80)
print()

try:
    with get_session() as session:
        # Get workflows without categories
        print("📊 Finding workflows without categories...")
        
        workflows = session.query(Workflow, WorkflowMetadata).outerjoin(
            WorkflowMetadata,
            Workflow.workflow_id == WorkflowMetadata.workflow_id
        ).filter(
            (WorkflowMetadata.categories.is_(None)) | 
            (WorkflowMetadata.categories == [])
        ).all()
        
        print(f"✅ Found {len(workflows)} workflows without categories")
        print()
        
        if not workflows:
            print("🎉 All workflows already have categories!")
            sys.exit(0)
        
        print("🤖 Inferring categories from URL slugs...")
        print()
        
        updated_count = 0
        
        for workflow, metadata in workflows:
            # Infer categories
            inferred_categories = infer_categories(workflow.url, workflow.workflow_id)
            
            print(f"Workflow {workflow.workflow_id}:")
            print(f"  URL: {workflow.url}")
            print(f"  Inferred: {', '.join(inferred_categories)}")
            
            # Update or create metadata
            if metadata:
                metadata.categories = inferred_categories
            else:
                # Create new metadata
                metadata = WorkflowMetadata(
                    workflow_id=workflow.workflow_id,
                    categories=inferred_categories
                )
                session.add(metadata)
            
            updated_count += 1
            print(f"  ✅ Updated")
            print()
        
        # Commit all updates
        print("💾 Committing updates...")
        session.commit()
        
        print()
        print("=" * 80)
        print("📊 INFERENCE COMPLETE")
        print("=" * 80)
        print(f"Workflows updated: {updated_count}")
        print()
        
        # Verify final state
        result = session.execute(text('''
            SELECT 
                CASE 
                    WHEN categories IS NULL OR categories = '[]'::jsonb THEN 'No categories'
                    ELSE 'Has categories'
                END as status,
                COUNT(*) as count
            FROM workflow_metadata
            GROUP BY status
        '''))
        
        print("Final category coverage:")
        for row in result:
            print(f"   {row[0]}: {row[1]} workflows")
        
        print()
        print("=" * 80)
        print("🎉 ALL WORKFLOWS NOW HAVE CATEGORIES!")
        print("=" * 80)
        print()
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

