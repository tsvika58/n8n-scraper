"""
Progress Tracker - Shared state for scraper monitoring

This module provides a centralized way to track scraper progress
that can be monitored from separate processes.

Author: AI Assistant
Date: October 16, 2025
"""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
import pytz


@dataclass
class ScraperProgress:
    """Represents current scraper progress"""
    scraper_id: str
    start_time: float
    total_workflows: int
    completed: int
    failed: int
    current_workflow_id: Optional[str]
    current_status: str
    last_update: float
    errors: list
    
    @property
    def elapsed_seconds(self) -> float:
        """Time elapsed since start"""
        return time.time() - self.start_time
    
    @property
    def success_rate(self) -> float:
        """Success rate as percentage"""
        if self.completed + self.failed == 0:
            return 0.0
        return (self.completed / (self.completed + self.failed)) * 100
    
    @property
    def eta_seconds(self) -> Optional[float]:
        """Estimated time to completion in seconds"""
        if self.completed == 0:
            return None
        avg_time = self.elapsed_seconds / self.completed
        remaining = self.total_workflows - self.completed - self.failed
        return avg_time * remaining
    
    @property
    def progress_percent(self) -> float:
        """Progress as percentage"""
        if self.total_workflows == 0:
            return 0.0
        return ((self.completed + self.failed) / self.total_workflows) * 100


class ProgressTracker:
    """
    Tracks scraper progress using a JSON file as shared state.
    
    This allows monitoring from separate processes without
    direct communication or database queries.
    """
    
    def __init__(self, scraper_id: str, state_file: Optional[Path] = None):
        """
        Initialize progress tracker.
        
        Args:
            scraper_id: Unique identifier for this scraper
            state_file: Path to state file (defaults to /tmp/scraper_progress.json)
        """
        self.scraper_id = scraper_id
        self.state_file = state_file or Path("/tmp/scraper_progress.json")
        self.progress: Optional[ScraperProgress] = None
        
    def start(self, total_workflows: int):
        """Initialize tracking for a new scraper run"""
        self.progress = ScraperProgress(
            scraper_id=self.scraper_id,
            start_time=time.time(),
            total_workflows=total_workflows,
            completed=0,
            failed=0,
            current_workflow_id=None,
            current_status="Starting",
            last_update=time.time(),
            errors=[]
        )
        self._write_state()
    
    def update(self, 
               current_workflow_id: Optional[str] = None,
               status: Optional[str] = None,
               completed_delta: int = 0,
               failed_delta: int = 0,
               error: Optional[str] = None):
        """
        Update progress state.
        
        Args:
            current_workflow_id: Currently processing workflow ID
            status: Current status message
            completed_delta: Number of workflows completed since last update
            failed_delta: Number of workflows failed since last update
            error: Error message to add to error list
        """
        if not self.progress:
            raise ValueError("Must call start() before update()")
        
        if current_workflow_id is not None:
            self.progress.current_workflow_id = current_workflow_id
        
        if status is not None:
            self.progress.current_status = status
        
        self.progress.completed += completed_delta
        self.progress.failed += failed_delta
        
        if error:
            self.progress.errors.append({
                'timestamp': time.time(),
                'workflow_id': current_workflow_id,
                'error': error
            })
            # Keep only last 100 errors
            self.progress.errors = self.progress.errors[-100:]
        
        self.progress.last_update = time.time()
        self._write_state()
    
    def finish(self, status: str = "Completed"):
        """Mark scraping as finished"""
        if self.progress:
            self.progress.current_status = status
            self.progress.last_update = time.time()
            self._write_state()
    
    def _write_state(self):
        """Write current state to file"""
        if not self.progress:
            return
        
        data = asdict(self.progress)
        
        # Create temp file and atomic rename for safety
        temp_file = self.state_file.with_suffix('.tmp')
        with open(temp_file, 'w') as f:
            json.dump(data, f, indent=2)
        temp_file.replace(self.state_file)
    
    @classmethod
    def read_state(cls, state_file: Optional[Path] = None) -> Optional[ScraperProgress]:
        """
        Read current state from file.
        
        Args:
            state_file: Path to state file
            
        Returns:
            ScraperProgress object or None if file doesn't exist
        """
        state_file = state_file or Path("/tmp/scraper_progress.json")
        
        if not state_file.exists():
            return None
        
        try:
            with open(state_file, 'r') as f:
                data = json.load(f)
            return ScraperProgress(**data)
        except Exception as e:
            print(f"Error reading state: {e}")
            return None
    
    @classmethod
    def is_alive(cls, state_file: Optional[Path] = None, timeout: int = 60) -> bool:
        """
        Check if scraper is still running.
        
        Args:
            state_file: Path to state file
            timeout: Seconds without update to consider dead
            
        Returns:
            True if scraper appears to be running
        """
        progress = cls.read_state(state_file)
        if not progress:
            return False
        
        time_since_update = time.time() - progress.last_update
        return time_since_update < timeout


def format_time(seconds: float) -> str:
    """Format seconds into human-readable time"""
    if seconds < 60:
        return f"{seconds:.0f}s"
    elif seconds < 3600:
        return f"{seconds/60:.1f}m"
    else:
        hours = seconds / 3600
        if hours < 24:
            return f"{hours:.1f}h"
        else:
            days = hours / 24
            return f"{days:.1f}d"


def format_progress_bar(completed: int, total: int, width: int = 40) -> str:
    """Create a text progress bar"""
    if total == 0:
        return "[" + " " * width + "]"
    
    filled = int((completed / total) * width)
    bar = "█" * filled + "░" * (width - filled)
    return f"[{bar}]"


def get_jerusalem_time() -> str:
    """Get current time in Jerusalem timezone"""
    jerusalem_tz = pytz.timezone('Asia/Jerusalem')
    return datetime.now(jerusalem_tz).strftime('%Y-%m-%d %H:%M:%S')

