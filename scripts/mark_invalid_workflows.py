#!/usr/bin/env python3
"""
Mark suspected invalid workflows and add them to no-scraping list.

Identifies workflows that are likely invalid/empty pages based on:
- Very short titles (< 10 characters)
- Generic titles (numbers only, "Workflow", "Template", etc.)
- Single-word titles that don't make sense
- Other suspicious patterns

Adds is_valid flag and validation_notes to workflow_metadata table.
"""

import sys
sys.path.insert(0, '/app')

from src.storage.database import get_session
from sqlalchemy import text
from loguru import logger

# Criteria for identifying invalid workflows
INVALID_CRITERIA = {
    'very_short_title': {
        'description': 'Title is very short (< 10 characters)',
        'query': "LENGTH(title) < 10"
    },
    'numeric_only': {
        'description': 'Title is only numbers',
        'query': "title ~ '^[0-9]+$'"
    },
    'generic_words': {
        'description': 'Title is a generic word',
        'query': "title IN ('Workflow', 'Template', 'Untitled', 'Test', 'Demo', 'Example', 'Setup', 'Intro', 'Basic', 'UPDATE', 'Links', 'Idea', 'Why?', 'Goal', 'Start', 'End')"
    },
    'single_emoji': {
        'description': 'Title is just an emoji or very short with emoji',
        'query': "LENGTH(REGEXP_REPLACE(title, '[^a-zA-Z0-9]', '', 'g')) < 5"
    }
}

def add_validation_columns():
    """Add is_valid and validation_notes columns if they don't exist."""
    with get_session() as session:
        try:
            # Check if columns exist
            result = session.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'workflow_metadata' 
                AND column_name IN ('is_valid', 'validation_notes')
            """))
            existing_columns = [row[0] for row in result]
            
            if 'is_valid' not in existing_columns:
                logger.info("Adding is_valid column...")
                session.execute(text("""
                    ALTER TABLE workflow_metadata 
                    ADD COLUMN is_valid BOOLEAN DEFAULT TRUE
                """))
                session.commit()
                logger.success("Added is_valid column")
            
            if 'validation_notes' not in existing_columns:
                logger.info("Adding validation_notes column...")
                session.execute(text("""
                    ALTER TABLE workflow_metadata 
                    ADD COLUMN validation_notes TEXT
                """))
                session.commit()
                logger.success("Added validation_notes column")
                
        except Exception as e:
            logger.error(f"Error adding columns: {e}")
            session.rollback()
            raise

def identify_invalid_workflows():
    """Identify workflows matching invalid criteria."""
    with get_session() as session:
        all_invalid_ids = set()
        criteria_matches = {}
        
        for criterion_name, criterion_info in INVALID_CRITERIA.items():
            query = f"""
                SELECT workflow_id, title
                FROM workflow_metadata
                WHERE {criterion_info['query']}
            """
            
            result = session.execute(text(query))
            matches = [(row[0], row[1]) for row in result]
            
            if matches:
                criteria_matches[criterion_name] = matches
                all_invalid_ids.update([m[0] for m in matches])
                logger.info(f"{criterion_name}: {len(matches)} workflows")
        
        return all_invalid_ids, criteria_matches

def mark_workflows_invalid(invalid_ids, criteria_matches):
    """Mark workflows as invalid in the database."""
    with get_session() as session:
        # Build validation notes for each workflow
        workflow_notes = {}
        for criterion_name, matches in criteria_matches.items():
            for workflow_id, title in matches:
                if workflow_id not in workflow_notes:
                    workflow_notes[workflow_id] = []
                workflow_notes[workflow_id].append(INVALID_CRITERIA[criterion_name]['description'])
        
        # Update workflows in batches
        batch_size = 100
        invalid_list = list(invalid_ids)
        
        for i in range(0, len(invalid_list), batch_size):
            batch = invalid_list[i:i + batch_size]
            
            for workflow_id in batch:
                notes = '; '.join(workflow_notes.get(workflow_id, ['Unknown reason']))
                
                session.execute(text("""
                    UPDATE workflow_metadata
                    SET is_valid = FALSE,
                        validation_notes = :notes
                    WHERE workflow_id = :workflow_id
                """), {'workflow_id': workflow_id, 'notes': notes})
            
            session.commit()
            logger.info(f"Marked {min(i + batch_size, len(invalid_list))}/{len(invalid_list)} workflows as invalid")

def create_no_scraping_list(invalid_ids):
    """Create a text file with workflow IDs to exclude from scraping."""
    output_file = '/app/data/no-scraping-list.txt'
    
    with open(output_file, 'w') as f:
        f.write("# Workflows marked as invalid - DO NOT SCRAPE\n")
        f.write(f"# Generated: {__import__('datetime').datetime.now().isoformat()}\n")
        f.write(f"# Total: {len(invalid_ids)} workflows\n")
        f.write("#\n")
        f.write("# These workflows have been identified as potentially invalid/empty pages\n")
        f.write("# and should be excluded from scraping operations until manually reviewed.\n")
        f.write("#\n\n")
        
        for workflow_id in sorted(invalid_ids, key=lambda x: int(x)):
            f.write(f"{workflow_id}\n")
    
    logger.success(f"Created no-scraping list: {output_file}")
    return output_file

def generate_report(invalid_ids, criteria_matches):
    """Generate a detailed report of invalid workflows."""
    with get_session() as session:
        print("\n" + "="*70)
        print("INVALID WORKFLOWS REPORT")
        print("="*70)
        print()
        
        print(f"📊 SUMMARY")
        print(f"Total workflows marked as invalid: {len(invalid_ids)}")
        print(f"Percentage of total: {len(invalid_ids)/6022*100:.2f}%")
        print()
        
        print(f"📋 BREAKDOWN BY CRITERIA")
        for criterion_name, matches in criteria_matches.items():
            print(f"  • {INVALID_CRITERIA[criterion_name]['description']}: {len(matches)}")
        print()
        
        print(f"🔍 EXAMPLES (first 20):")
        result = session.execute(text("""
            SELECT workflow_id, title, validation_notes, categories
            FROM workflow_metadata
            WHERE is_valid = FALSE
            ORDER BY workflow_id::integer
            LIMIT 20
        """))
        
        for row in result:
            cats = row[3] if row[3] else []
            print(f"  ID {row[0]}: \"{row[1]}\"")
            print(f"    Reason: {row[2]}")
            print(f"    Categories: {cats}")
            print()
        
        if len(invalid_ids) > 20:
            print(f"  ... and {len(invalid_ids) - 20} more")
        print()
        
        print(f"✅ NEXT STEPS")
        print(f"  1. Review no-scraping-list.txt")
        print(f"  2. Manually validate some examples")
        print(f"  3. Adjust criteria if needed")
        print(f"  4. Exclude these IDs from Layer 2 scraping")
        print()

def main():
    logger.info("Starting invalid workflow identification...")
    
    # Step 1: Add validation columns
    logger.info("Step 1: Adding validation columns...")
    add_validation_columns()
    
    # Step 2: Identify invalid workflows
    logger.info("Step 2: Identifying invalid workflows...")
    invalid_ids, criteria_matches = identify_invalid_workflows()
    
    if not invalid_ids:
        logger.success("No invalid workflows found!")
        return
    
    # Step 3: Mark workflows as invalid
    logger.info("Step 3: Marking workflows as invalid...")
    mark_workflows_invalid(invalid_ids, criteria_matches)
    
    # Step 4: Create no-scraping list
    logger.info("Step 4: Creating no-scraping list...")
    no_scraping_file = create_no_scraping_list(invalid_ids)
    
    # Step 5: Generate report
    logger.info("Step 5: Generating report...")
    generate_report(invalid_ids, criteria_matches)
    
    logger.success(f"✅ Complete! Marked {len(invalid_ids)} workflows as invalid")
    logger.info(f"No-scraping list: {no_scraping_file}")

if __name__ == "__main__":
    main()
