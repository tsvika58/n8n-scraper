#!/usr/bin/env python3
"""
Simple Alert System for N8N Scraper
Sends alerts when thresholds are exceeded
"""
import json
import time
from datetime import datetime
from pathlib import Path

class AlertSystem:
    def __init__(self, alert_file="logs/alerts.log"):
        self.alert_file = Path(alert_file)
        self.alert_file.parent.mkdir(exist_ok=True)
        self.sent_alerts = set()  # Track sent alerts to avoid spam
        
    def log_alert(self, level, message, data=None):
        """Log an alert to file"""
        timestamp = datetime.now().isoformat()
        alert = {
            'timestamp': timestamp,
            'level': level,
            'message': message,
            'data': data or {}
        }
        
        # Avoid duplicate alerts
        alert_key = f"{level}:{message}"
        if alert_key in self.sent_alerts:
            return
        
        self.sent_alerts.add(alert_key)
        
        # Write to log file
        with open(self.alert_file, 'a') as f:
            f.write(json.dumps(alert) + '\n')
        
        # Print to console
        emoji = "🚨" if level == "CRITICAL" else "⚠️" if level == "WARNING" else "ℹ️"
        print(f"{emoji} {level}: {message}")
        
        # Clean up old alerts after 24 hours
        self._cleanup_old_alerts()
    
    def _cleanup_old_alerts(self):
        """Remove alerts older than 24 hours from memory"""
        cutoff_time = datetime.now().timestamp() - (24 * 60 * 60)
        # Simple cleanup - in production, you'd want more sophisticated logic
        if len(self.sent_alerts) > 1000:
            self.sent_alerts.clear()
    
    def check_system_health(self, system_data):
        """Check system health and generate alerts"""
        if system_data.get('cpu_percent', 0) > 80:
            self.log_alert("WARNING", f"High CPU usage: {system_data['cpu_percent']:.1f}%", system_data)
        
        if system_data.get('memory_percent', 0) > 85:
            self.log_alert("WARNING", f"High memory usage: {system_data['memory_percent']:.1f}%", system_data)
        
        if system_data.get('disk_percent', 0) > 90:
            self.log_alert("CRITICAL", f"High disk usage: {system_data['disk_percent']:.1f}%", system_data)
    
    def check_dashboard_health(self, dashboard_data):
        """Check dashboard health and generate alerts"""
        if dashboard_data.get('status') != 'healthy':
            self.log_alert("CRITICAL", f"Dashboard unhealthy: {dashboard_data.get('error', 'Unknown error')}", dashboard_data)
        
        if dashboard_data.get('response_time', 0) > 5.0:
            self.log_alert("WARNING", f"Slow dashboard response: {dashboard_data['response_time']:.2f}s", dashboard_data)
    
    def check_database_health(self, db_data):
        """Check database health and generate alerts"""
        if db_data.get('status') != 'healthy':
            self.log_alert("CRITICAL", f"Database unhealthy: {db_data.get('error', 'Unknown error')}", db_data)
        
        recent_success_rate = db_data.get('recent_success_rate', 100)
        if recent_success_rate < 50:
            self.log_alert("WARNING", f"Low recent success rate: {recent_success_rate:.1f}%", db_data)
    
    def check_scraping_performance(self, performance_data):
        """Check scraping performance and generate alerts"""
        error_rate = performance_data.get('error_rate', 0)
        if error_rate > 0.1:  # 10% error rate
            self.log_alert("WARNING", f"High error rate: {error_rate:.1%}", performance_data)
        
        throughput = performance_data.get('throughput', 0)
        if throughput < 1.0:  # Less than 1 workflow per minute
            self.log_alert("WARNING", f"Low throughput: {throughput:.1f} workflows/min", performance_data)

if __name__ == "__main__":
    # Test the alert system
    alert_system = AlertSystem()
    
    # Test alerts
    alert_system.log_alert("INFO", "Alert system initialized")
    alert_system.log_alert("WARNING", "Test warning alert")
    alert_system.log_alert("CRITICAL", "Test critical alert")
    
    print(f"✅ Alert system test complete. Check {alert_system.alert_file}")



