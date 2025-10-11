"""
Database schema for workflow inventory - SCRAPE-002B
Creates and manages the workflow_inventory table
"""

from sqlalchemy import create_engine, Column, String, Text, DateTime, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

Base = declarative_base()


class WorkflowInventoryEntry(Base):
    """Workflow inventory entry model."""
    __tablename__ = 'workflow_inventory'
    
    workflow_id = Column(String, primary_key=True, nullable=False)
    title = Column(Text, nullable=False)
    url = Column(Text, nullable=False, unique=True)
    discovered_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_verified = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Indexes for fast searching
    __table_args__ = (
        Index('idx_workflow_id', 'workflow_id'),
        Index('idx_title', 'title'),
    )
    
    def __repr__(self):
        return f"<WorkflowInventory(id={self.workflow_id}, title='{self.title}')>"


class InventoryDatabase:
    """Manages workflow inventory database operations."""
    
    def __init__(self, db_path: str = "data/workflows.db"):
        """Initialize database connection."""
        self.db_path = db_path
        
        # Ensure data directory exists
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Create engine and session
        self.engine = create_engine(f'sqlite:///{db_path}')
        self.Session = sessionmaker(bind=self.engine)
        
        logger.info(f"Database initialized at {db_path}")
    
    def create_tables(self):
        """Create all tables if they don't exist."""
        try:
            Base.metadata.create_all(self.engine)
            logger.info("✅ workflow_inventory table created/verified")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to create tables: {e}")
            return False
    
    def store_workflows(self, workflows: list) -> dict:
        """
        Store workflows in database.
        
        Args:
            workflows: List of workflow dicts with keys: workflow_id, title, url, discovered_date
            
        Returns:
            dict with success status and stats
        """
        session = self.Session()
        stats = {
            'total_attempted': len(workflows),
            'stored': 0,
            'duplicates_skipped': 0,
            'errors': 0
        }
        
        try:
            for wf in workflows:
                try:
                    # Check if workflow already exists
                    existing = session.query(WorkflowInventoryEntry).filter_by(
                        workflow_id=wf['workflow_id']
                    ).first()
                    
                    if existing:
                        # Update last_verified timestamp
                        existing.last_verified = datetime.utcnow()
                        stats['duplicates_skipped'] += 1
                    else:
                        # Create new entry
                        entry = WorkflowInventoryEntry(
                            workflow_id=wf['workflow_id'],
                            title=wf['title'],
                            url=wf['url'],
                            discovered_date=datetime.fromisoformat(wf['discovered_date'])
                        )
                        session.add(entry)
                        stats['stored'] += 1
                        
                except Exception as e:
                    logger.error(f"Error storing workflow {wf.get('workflow_id')}: {e}")
                    stats['errors'] += 1
                    continue
            
            # Commit all changes
            session.commit()
            logger.info(f"✅ Stored {stats['stored']} new workflows, "
                       f"skipped {stats['duplicates_skipped']} duplicates, "
                       f"{stats['errors']} errors")
            
            return {
                'success': True,
                'stats': stats
            }
            
        except Exception as e:
            session.rollback()
            logger.error(f"❌ Database transaction failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'stats': stats
            }
        finally:
            session.close()
    
    def get_inventory_stats(self) -> dict:
        """Get statistics about the inventory."""
        session = self.Session()
        
        try:
            total_count = session.query(WorkflowInventoryEntry).count()
            
            # Get ID ranges
            if total_count > 0:
                # Convert workflow_id to int for min/max
                from sqlalchemy import func, cast, Integer
                
                min_id = session.query(
                    func.min(cast(WorkflowInventoryEntry.workflow_id, Integer))
                ).scalar()
                
                max_id = session.query(
                    func.max(cast(WorkflowInventoryEntry.workflow_id, Integer))
                ).scalar()
            else:
                min_id = None
                max_id = None
            
            return {
                'total_workflows': total_count,
                'min_workflow_id': str(min_id) if min_id else None,
                'max_workflow_id': str(max_id) if max_id else None
            }
            
        except Exception as e:
            logger.error(f"Error getting inventory stats: {e}")
            return {
                'total_workflows': 0,
                'error': str(e)
            }
        finally:
            session.close()
    
    def check_duplicates(self) -> dict:
        """Check for duplicate workflow IDs."""
        session = self.Session()
        
        try:
            from sqlalchemy import func
            
            # Find workflow_ids that appear more than once
            duplicates = session.query(
                WorkflowInventoryEntry.workflow_id,
                func.count(WorkflowInventoryEntry.workflow_id).label('count')
            ).group_by(
                WorkflowInventoryEntry.workflow_id
            ).having(
                func.count(WorkflowInventoryEntry.workflow_id) > 1
            ).all()
            
            return {
                'duplicate_count': len(duplicates),
                'duplicates': [{'workflow_id': d[0], 'count': d[1]} for d in duplicates]
            }
            
        except Exception as e:
            logger.error(f"Error checking duplicates: {e}")
            return {
                'duplicate_count': 0,
                'error': str(e)
            }
        finally:
            session.close()
    
    def get_sample_workflows(self, limit: int = 100) -> list:
        """Get sample workflows from inventory."""
        session = self.Session()
        
        try:
            workflows = session.query(WorkflowInventoryEntry).limit(limit).all()
            
            return [
                {
                    'workflow_id': wf.workflow_id,
                    'title': wf.title,
                    'url': wf.url,
                    'discovered_date': wf.discovered_date.isoformat()
                }
                for wf in workflows
            ]
            
        except Exception as e:
            logger.error(f"Error getting sample workflows: {e}")
            return []
        finally:
            session.close()


def main():
    """Test database operations."""
    db = InventoryDatabase()
    
    # Create tables
    print("Creating tables...")
    db.create_tables()
    
    # Get stats
    print("\nGetting inventory stats...")
    stats = db.get_inventory_stats()
    print(f"Total workflows: {stats['total_workflows']}")
    print(f"ID range: {stats.get('min_workflow_id')} - {stats.get('max_workflow_id')}")
    
    # Check duplicates
    print("\nChecking for duplicates...")
    dup_check = db.check_duplicates()
    print(f"Duplicates found: {dup_check['duplicate_count']}")


if __name__ == "__main__":
    main()





