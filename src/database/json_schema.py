"""
Database schema for workflow JSON data - SCRAPE-003
Stores complete n8n workflow JSON structures
"""

from sqlalchemy import create_engine, Column, String, Integer, Text, DateTime, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from pathlib import Path
from typing import Optional
import json
import logging

logger = logging.getLogger(__name__)

Base = declarative_base()


class WorkflowJSON(Base):
    """Workflow JSON data model."""
    __tablename__ = 'workflow_json'
    
    workflow_id = Column(String, primary_key=True, nullable=False)
    workflow_name = Column(Text, nullable=False)
    node_count = Column(Integer, nullable=False)
    connection_count = Column(Integer, nullable=False)
    workflow_json = Column(Text, nullable=False)  # Stored as JSON string
    extraction_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<WorkflowJSON(id={self.workflow_id}, nodes={self.node_count})>"


class JSONDatabase:
    """Manages workflow JSON database operations."""
    
    def __init__(self, db_path: str = "data/workflows.db"):
        """Initialize database connection."""
        self.db_path = db_path
        
        # Ensure data directory exists
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Create engine and session
        self.engine = create_engine(f'sqlite:///{db_path}')
        self.Session = sessionmaker(bind=self.engine)
        
        logger.info(f"JSON Database initialized at {db_path}")
    
    def create_tables(self):
        """Create workflow_json table if it doesn't exist."""
        try:
            Base.metadata.create_all(self.engine)
            logger.info("✅ workflow_json table created/verified")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to create tables: {e}")
            return False
    
    def store_workflow_json(self, workflow_id: str, workflow_name: str, 
                           node_count: int, connection_count: int, 
                           workflow_json: dict) -> bool:
        """
        Store workflow JSON in database.
        
        Args:
            workflow_id: Workflow ID
            workflow_name: Workflow name
            node_count: Number of nodes
            connection_count: Number of connections
            workflow_json: Complete workflow JSON data
            
        Returns:
            bool: True if successful, False otherwise
        """
        session = self.Session()
        
        try:
            # Check if workflow already exists
            existing = session.query(WorkflowJSON).filter_by(
                workflow_id=workflow_id
            ).first()
            
            if existing:
                # Update existing record
                existing.workflow_name = workflow_name
                existing.node_count = node_count
                existing.connection_count = connection_count
                existing.workflow_json = json.dumps(workflow_json)
                existing.last_updated = datetime.utcnow()
                logger.info(f"Updated existing workflow {workflow_id}")
            else:
                # Create new record
                record = WorkflowJSON(
                    workflow_id=workflow_id,
                    workflow_name=workflow_name,
                    node_count=node_count,
                    connection_count=connection_count,
                    workflow_json=json.dumps(workflow_json)
                )
                session.add(record)
                logger.info(f"Stored new workflow {workflow_id}")
            
            session.commit()
            return True
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error storing workflow {workflow_id}: {e}")
            return False
        finally:
            session.close()
    
    def get_workflow_json(self, workflow_id: str) -> Optional[dict]:
        """
        Retrieve workflow JSON from database.
        
        Args:
            workflow_id: Workflow ID to retrieve
            
        Returns:
            dict: Workflow JSON data or None if not found
        """
        session = self.Session()
        
        try:
            record = session.query(WorkflowJSON).filter_by(
                workflow_id=workflow_id
            ).first()
            
            if record:
                return json.loads(record.workflow_json)
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving workflow {workflow_id}: {e}")
            return None
        finally:
            session.close()
    
    def get_stats(self) -> dict:
        """Get statistics about stored workflow JSONs."""
        session = self.Session()
        
        try:
            from sqlalchemy import func
            
            total_count = session.query(WorkflowJSON).count()
            
            if total_count > 0:
                avg_nodes = session.query(
                    func.avg(WorkflowJSON.node_count)
                ).scalar()
                
                max_nodes = session.query(
                    func.max(WorkflowJSON.node_count)
                ).scalar()
                
                min_nodes = session.query(
                    func.min(WorkflowJSON.node_count)
                ).scalar()
            else:
                avg_nodes = 0
                max_nodes = 0
                min_nodes = 0
            
            return {
                'total_workflows': total_count,
                'avg_node_count': float(avg_nodes) if avg_nodes else 0,
                'max_node_count': max_nodes or 0,
                'min_node_count': min_nodes or 0
            }
            
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {'total_workflows': 0, 'error': str(e)}
        finally:
            session.close()


def main():
    """Test database operations."""
    db = JSONDatabase()
    
    # Create tables
    print("Creating tables...")
    db.create_tables()
    
    # Get stats
    print("\nGetting workflow JSON stats...")
    stats = db.get_stats()
    print(f"Total workflows: {stats['total_workflows']}")
    print(f"Avg nodes: {stats['avg_node_count']:.1f}")


if __name__ == "__main__":
    main()

