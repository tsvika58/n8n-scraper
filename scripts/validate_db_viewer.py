#!/usr/bin/env python3
"""
Validate DB Viewer for 7 Video Workflows

Test that all 7 workflows are properly displayed in the DB viewer.
"""

import subprocess
import time

# The 7 test workflows
TEST_WORKFLOWS = ['6270', '8642', '8527', '8237', '7639', '5170', '2462']

def test_workflow_detail(workflow_id):
    """Test a specific workflow detail page."""
    try:
        result = subprocess.run(['curl', '-s', f'http://localhost:8080/workflow/{workflow_id}'], 
                              capture_output=True, text=True, timeout=10)
        
        if result.returncode != 0:
            return False, f"HTTP error: {result.returncode}"
        
        content = result.stdout
        
        # Check for key elements
        checks = [
            ('Quality:', 'Quality score displayed'),
            ('Videos Found:', 'Video count displayed'),
            ('Transcripts:', 'Transcript count displayed'),
            ('L3 Content Quality:', 'L3 quality displayed'),
            ('primary_explainer', 'Video classification displayed')
        ]
        
        missing = []
        for check, description in checks:
            if check not in content:
                missing.append(description)
        
        if missing:
            return False, f"Missing: {', '.join(missing)}"
        
        return True, "All elements present"
        
    except Exception as e:
        return False, f"Exception: {str(e)}"

def test_main_page():
    """Test the main workflows page."""
    try:
        result = subprocess.run(['curl', '-s', 'http://localhost:8080/workflows'], 
                              capture_output=True, text=True, timeout=10)
        
        if result.returncode != 0:
            return False, f"HTTP error: {result.returncode}"
        
        content = result.stdout
        
        # Check if we can find our workflows
        found_workflows = []
        for workflow_id in TEST_WORKFLOWS:
            if workflow_id in content:
                found_workflows.append(workflow_id)
        
        if len(found_workflows) < 5:  # At least 5 should be visible
            return False, f"Only found {len(found_workflows)} workflows: {found_workflows}"
        
        return True, f"Found {len(found_workflows)} workflows: {found_workflows}"
        
    except Exception as e:
        return False, f"Exception: {str(e)}"

def main():
    """Main validation function."""
    print("🌐 VALIDATING DB VIEWER FOR 7 VIDEO WORKFLOWS")
    print("=" * 60)
    
    # Test main page
    print("📋 Testing main workflows page...")
    main_ok, main_msg = test_main_page()
    print(f"   {'✅' if main_ok else '❌'} {main_msg}")
    
    if not main_ok:
        print("❌ Main page validation failed")
        return False
    
    print()
    
    # Test each workflow detail page
    print("📄 Testing workflow detail pages...")
    all_ok = True
    
    for workflow_id in TEST_WORKFLOWS:
        print(f"   Testing {workflow_id}...", end=" ")
        detail_ok, detail_msg = test_workflow_detail(workflow_id)
        print(f"{'✅' if detail_ok else '❌'} {detail_msg}")
        
        if not detail_ok:
            all_ok = False
    
    print()
    
    if all_ok:
        print("🎉 DB VIEWER VALIDATION SUCCESSFUL!")
        print("✅ All 7 video workflows properly displayed")
        return True
    else:
        print("❌ DB VIEWER VALIDATION FAILED")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)

