"""
Database schema for validation and quality scores - SCRAPE-004
Stores quality assessment data and validation issues
"""

from sqlalchemy import create_engine, Column, String, Integer, Float, Text, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict
import logging

logger = logging.getLogger(__name__)

Base = declarative_base()


class QualityScore(Base):
    """Quality score model for workflows."""
    __tablename__ = 'quality_scores'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    workflow_id = Column(String, nullable=False, unique=True)
    overall_score = Column(Float, nullable=False)
    classification = Column(String, nullable=False)  # Excellent/Good/Fair/Poor
    layer1_score = Column(Float)
    layer2_score = Column(Float)
    layer3_score = Column(Float)
    consistency_score = Column(Float)
    validation_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<QualityScore(workflow={self.workflow_id}, score={self.overall_score}, class={self.classification})>"


class ValidationIssue(Base):
    """Validation issue model."""
    __tablename__ = 'validation_issues'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    workflow_id = Column(String, nullable=False)
    layer = Column(String, nullable=False)  # layer1/layer2/layer3/consistency
    issue_type = Column(String, nullable=False)  # missing_data/invalid_format/incomplete_content
    issue_description = Column(Text, nullable=False)
    severity = Column(String, nullable=False)  # critical/warning/info
    validation_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<ValidationIssue(workflow={self.workflow_id}, layer={self.layer}, severity={self.severity})>"


class ValidationDatabase:
    """Manages validation and quality score database operations."""
    
    def __init__(self, db_path: str = "data/workflows.db"):
        """Initialize database connection."""
        self.db_path = db_path
        
        # Ensure data directory exists
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Create engine and session
        self.engine = create_engine(f'sqlite:///{db_path}')
        self.Session = sessionmaker(bind=self.engine)
        
        logger.info(f"Validation Database initialized at {db_path}")
    
    def create_tables(self):
        """Create validation tables if they don't exist."""
        try:
            Base.metadata.create_all(self.engine)
            logger.info("✅ Validation tables created/verified")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to create tables: {e}")
            return False
    
    def store_quality_score(self, workflow_id: str, overall_score: float,
                           classification: str, layer1_score: float = None,
                           layer2_score: float = None, layer3_score: float = None,
                           consistency_score: float = None) -> bool:
        """Store quality score for a workflow."""
        session = self.Session()
        
        try:
            # Check if score already exists
            existing = session.query(QualityScore).filter_by(
                workflow_id=workflow_id
            ).first()
            
            if existing:
                # Update existing
                existing.overall_score = overall_score
                existing.classification = classification
                existing.layer1_score = layer1_score
                existing.layer2_score = layer2_score
                existing.layer3_score = layer3_score
                existing.consistency_score = consistency_score
                existing.validation_date = datetime.utcnow()
            else:
                # Create new
                score = QualityScore(
                    workflow_id=workflow_id,
                    overall_score=overall_score,
                    classification=classification,
                    layer1_score=layer1_score,
                    layer2_score=layer2_score,
                    layer3_score=layer3_score,
                    consistency_score=consistency_score
                )
                session.add(score)
            
            session.commit()
            return True
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error storing quality score for {workflow_id}: {e}")
            return False
        finally:
            session.close()
    
    def store_validation_issue(self, workflow_id: str, layer: str,
                               issue_type: str, issue_description: str,
                               severity: str = "warning") -> bool:
        """Store a validation issue."""
        session = self.Session()
        
        try:
            issue = ValidationIssue(
                workflow_id=workflow_id,
                layer=layer,
                issue_type=issue_type,
                issue_description=issue_description,
                severity=severity
            )
            session.add(issue)
            session.commit()
            return True
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error storing validation issue: {e}")
            return False
        finally:
            session.close()
    
    def get_quality_scores(self, classification: Optional[str] = None) -> List[Dict]:
        """Get quality scores, optionally filtered by classification."""
        session = self.Session()
        
        try:
            query = session.query(QualityScore)
            if classification:
                query = query.filter_by(classification=classification)
            
            scores = query.all()
            
            return [
                {
                    'workflow_id': s.workflow_id,
                    'overall_score': s.overall_score,
                    'classification': s.classification,
                    'layer1_score': s.layer1_score,
                    'layer2_score': s.layer2_score,
                    'layer3_score': s.layer3_score,
                    'consistency_score': s.consistency_score
                }
                for s in scores
            ]
            
        except Exception as e:
            logger.error(f"Error getting quality scores: {e}")
            return []
        finally:
            session.close()
    
    def get_validation_issues(self, workflow_id: Optional[str] = None,
                              severity: Optional[str] = None) -> List[Dict]:
        """Get validation issues, optionally filtered."""
        session = self.Session()
        
        try:
            query = session.query(ValidationIssue)
            if workflow_id:
                query = query.filter_by(workflow_id=workflow_id)
            if severity:
                query = query.filter_by(severity=severity)
            
            issues = query.all()
            
            return [
                {
                    'workflow_id': i.workflow_id,
                    'layer': i.layer,
                    'issue_type': i.issue_type,
                    'description': i.issue_description,
                    'severity': i.severity
                }
                for i in issues
            ]
            
        except Exception as e:
            logger.error(f"Error getting validation issues: {e}")
            return []
        finally:
            session.close()
    
    def get_stats(self) -> Dict:
        """Get validation statistics."""
        session = self.Session()
        
        try:
            from sqlalchemy import func
            
            total_scores = session.query(QualityScore).count()
            
            if total_scores > 0:
                avg_score = session.query(func.avg(QualityScore.overall_score)).scalar()
                
                # Count by classification
                excellent = session.query(QualityScore).filter_by(classification='Excellent').count()
                good = session.query(QualityScore).filter_by(classification='Good').count()
                fair = session.query(QualityScore).filter_by(classification='Fair').count()
                poor = session.query(QualityScore).filter_by(classification='Poor').count()
            else:
                avg_score = 0
                excellent = good = fair = poor = 0
            
            total_issues = session.query(ValidationIssue).count()
            critical_issues = session.query(ValidationIssue).filter_by(severity='critical').count()
            
            return {
                'total_workflows': total_scores,
                'avg_quality_score': float(avg_score) if avg_score else 0,
                'excellent_count': excellent,
                'good_count': good,
                'fair_count': fair,
                'poor_count': poor,
                'total_issues': total_issues,
                'critical_issues': critical_issues
            }
            
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {'total_workflows': 0, 'error': str(e)}
        finally:
            session.close()


def main():
    """Test database operations."""
    db = ValidationDatabase()
    
    # Create tables
    print("Creating tables...")
    db.create_tables()
    
    # Get stats
    print("\nGetting validation stats...")
    stats = db.get_stats()
    print(f"Total workflows with scores: {stats['total_workflows']}")
    print(f"Average quality score: {stats['avg_quality_score']:.1f}")
    print(f"Total issues: {stats['total_issues']}")


if __name__ == "__main__":
    main()





