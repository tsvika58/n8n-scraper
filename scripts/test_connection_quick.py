#!/usr/bin/env python3
"""Quick test to verify database and scraper connectivity."""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

print("🧪 Testing N8N Scraper Setup...")
print()

# Test 1: Database Connection
print("1️⃣  Testing database connection...")
try:
    from src.storage.database import get_session
    from sqlalchemy import text
    with get_session() as session:
        result = session.execute(text("SELECT 1")).scalar()
        assert result == 1
        print("   ✅ Database connection successful")
except Exception as e:
    print(f"   ❌ Database connection failed: {e}")
    sys.exit(1)

# Test 2: Import Core Modules
print("2️⃣  Testing core module imports...")
try:
    from src.scrapers.layer1_metadata import PageMetadataExtractor
    from src.orchestrator.workflow_orchestrator import WorkflowOrchestrator
    from src.storage.repository import WorkflowRepository
    print("   ✅ All modules imported successfully")
except Exception as e:
    print(f"   ❌ Module import failed: {e}")
    sys.exit(1)

# Test 3: Repository
print("3️⃣  Testing repository...")
try:
    from src.storage.repository import WorkflowRepository
    with get_session() as session:
        repo = WorkflowRepository(session)
        stats = repo.get_statistics()
        print(f"   ✅ Repository working")
        print(f"      • Workflows in database: {stats.get('total_workflows', 0)}")
except Exception as e:
    print(f"   ❌ Repository test failed: {e}")
    sys.exit(1)

print()
print("="*60)
print("✅ ALL TESTS PASSED - Ready to run 500-workflow scraper!")
print("="*60)
print()
print("📊 Monitoring Dashboards:")
print("   • Realtime Dashboard: http://localhost:5001")
print("   • Database Viewer: http://localhost:5004")
print("   • pgAdmin: http://localhost:8080")
print()
print("🚀 To run the scraper:")
print("   source venv/bin/activate")
print("   python scripts/run_500_workflows_metadata.py")
print()

