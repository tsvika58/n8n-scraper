#!/usr/bin/env python3
"""
Database Initialization Script
Creates SQLite database with schema for n8n workflow scraper.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database.schema import init_db, Base
from sqlalchemy import inspect


def setup():
    """Initialize database with schema"""
    
    print("🔧 Initializing n8n Workflow Scraper Database...")
    print()
    
    # Create data directory
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    print(f"✅ Data directory: {data_dir.absolute()}")
    
    # Initialize database
    database_url = "sqlite:///data/workflows.db"
    print(f"📊 Database URL: {database_url}")
    print()
    
    engine = init_db(database_url, echo=True)
    print()
    print("✅ Database initialized successfully!")
    print()
    
    # Verify tables
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    print(f"📋 Tables created: {len(tables)}")
    for table in tables:
        columns = inspector.get_columns(table)
        print(f"  ├── {table}: {len(columns)} columns")
        for col in columns[:3]:  # Show first 3 columns
            print(f"  │   ├── {col['name']}: {col['type']}")
        if len(columns) > 3:
            print(f"  │   └── ... and {len(columns) - 3} more columns")
    
    print()
    print(f"📁 Database location: {Path('data/workflows.db').absolute()}")
    print()
    print("🎉 Setup complete! Ready to start scraping.")
    print()
    print("Next steps:")
    print("  1. Activate virtual environment: source venv/bin/activate")
    print("  2. Run tests: pytest")
    print("  3. Start scraping: python -m src.orchestrator.pipeline")


if __name__ == "__main__":
    try:
        setup()
    except Exception as e:
        print(f"❌ Error during setup: {e}")
        sys.exit(1)

