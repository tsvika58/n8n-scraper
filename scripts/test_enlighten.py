#!/usr/bin/env python3
"""
Test enlighten library
"""
import time
import enlighten

def test_enlighten():
    """Test if enlighten works"""
    print("Testing enlighten library...")
    
    # Initialize enlighten manager
    manager = enlighten.get_manager()
    
    # Create progress bar
    pbar = manager.counter(total=10, desc='Testing', unit='items')
    
    # Create status bar
    status_bar = manager.status_bar(
        status_format='{fill}{status}{fill}{elapsed}',
        justify=enlighten.Justify.CENTER,
        status='Testing...',
        color='blue'
    )
    
    try:
        for i in range(10):
            print(f"Processing item {i+1}")
            status_bar.update(status=f"Processing item {i+1}")
            pbar.update()
            time.sleep(0.5)
    
    finally:
        manager.stop()
    
    print("Enlighten test completed!")

if __name__ == "__main__":
    test_enlighten()
