"""
Load Extracted Workflows into Database

Loads the 10 extracted workflow JSON files into the SQLite database.

Author: Developer-1 (Dev1)
Date: October 10, 2025
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.database.schema import Workflow, get_session
from loguru import logger


def load_workflows_to_db():
    """Load all 10 extracted workflows into the database."""
    logger.info("🚀 Loading extracted workflows into database...")
    
    # Create session
    session = get_session()
    
    try:
        # Find all workflow JSON files
        sample_dir = project_root / ".coordination" / "testing" / "results" / "SCRAPE-002-sample-extractions"
        workflow_files = sorted(sample_dir.glob("workflow_*.json"))
        
        logger.info(f"Found {len(workflow_files)} workflow files")
        
        loaded_count = 0
        
        for workflow_file in workflow_files:
            with open(workflow_file, 'r') as f:
                data = json.load(f)
            
            workflow_id = data.get('workflow_id')
            logger.info(f"Loading workflow {workflow_id}...")
            
            # Check if workflow already exists
            existing = session.query(Workflow).filter_by(workflow_id=workflow_id).first()
            if existing:
                logger.warning(f"Workflow {workflow_id} already exists, skipping")
                continue
            
            # Create workflow object
            workflow = Workflow(
                workflow_id=workflow_id,
                workflow_url=data.get('url'),
                title=data.get('title', 'Unknown Title'),
                author=data.get('author', 'Unknown Author'),
                primary_category=data.get('primary_category', 'Uncategorized'),
                secondary_categories=data.get('secondary_categories', []),
                node_tags=data.get('node_tags', []),
                general_tags=data.get('general_tags', []),
                description=data.get('description', ''),
                use_case=data.get('use_case', ''),
                difficulty_level=data.get('difficulty_level', 'intermediate'),
                views=data.get('views', 0),
                upvotes=data.get('upvotes', 0),
                created_date=datetime.fromisoformat(data['created_date']) if data.get('created_date') else None,
                updated_date=datetime.fromisoformat(data['updated_date']) if data.get('updated_date') else None,
                setup_instructions=data.get('setup_instructions', ''),
                prerequisites=data.get('prerequisites', []),
                estimated_setup_time=data.get('estimated_setup_time', ''),
                scrape_date=datetime.now(),
                layer1_success=True,
                layer1_time=float(data.get('extraction_time', '0s').replace('s', '')),
                success=True
            )
            
            session.add(workflow)
            loaded_count += 1
            logger.success(f"✅ Loaded workflow {workflow_id}")
        
        # Commit all changes
        session.commit()
        logger.success(f"🎉 Successfully loaded {loaded_count} workflows into database")
        
        # Verify
        total_count = session.query(Workflow).count()
        logger.info(f"📊 Total workflows in database: {total_count}")
        
    except Exception as e:
        session.rollback()
        logger.error(f"❌ Error loading workflows: {e}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    load_workflows_to_db()

