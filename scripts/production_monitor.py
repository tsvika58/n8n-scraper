#!/usr/bin/env python3
"""
Production Monitoring Script for N8N Scraper
Monitors system health, database status, and scraping performance
"""
import time
import json
import requests
import psutil
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.storage.database import get_session
from src.storage.repository import WorkflowRepository

class ProductionMonitor:
    def __init__(self):
        self.dashboard_url = "http://localhost:5001"
        self.alert_thresholds = {
            'cpu_percent': 80,
            'memory_percent': 85,
            'disk_percent': 90,
            'error_rate': 0.1,  # 10% error rate
            'response_time': 5.0,  # 5 seconds
        }
        
    def check_system_health(self):
        """Check system resource usage"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'disk_percent': disk.percent,
                'memory_available_gb': memory.available / (1024**3),
                'disk_free_gb': disk.free / (1024**3),
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {'error': str(e), 'timestamp': datetime.now().isoformat()}
    
    def check_dashboard_health(self):
        """Check dashboard API health"""
        try:
            response = requests.get(f"{self.dashboard_url}/api/stats", timeout=10)
            if response.status_code == 200:
                data = response.json()
                return {
                    'status': 'healthy',
                    'response_time': response.elapsed.total_seconds(),
                    'is_active': data['live_scraping']['is_active'],
                    'total_workflows': data['overall_progress']['total_workflows'],
                    'success_rate': data['overall_progress']['completion_percentage'],
                    'timestamp': datetime.now().isoformat()
                }
            else:
                return {'status': 'unhealthy', 'status_code': response.status_code}
        except Exception as e:
            return {'status': 'error', 'error': str(e), 'timestamp': datetime.now().isoformat()}
    
    def check_database_health(self):
        """Check database connection and recent activity"""
        try:
            with get_session() as session:
                repository = WorkflowRepository(session)
                
                # Get recent activity (last hour)
                from sqlalchemy import text
                recent_time = datetime.now() - timedelta(hours=1)
                recent_workflows = session.execute(text("""
                    SELECT 
                        COUNT(*) as total,
                        COUNT(*) FILTER (WHERE quality_score > 0) as successful,
                        COUNT(*) FILTER (WHERE error_message IS NOT NULL) as failed
                    FROM workflows 
                    WHERE extracted_at > :recent_time
                """), {'recent_time': recent_time}).fetchone()
                
                return {
                    'status': 'healthy',
                    'recent_total': recent_workflows.total or 0,
                    'recent_successful': recent_workflows.successful or 0,
                    'recent_failed': recent_workflows.failed or 0,
                    'recent_success_rate': (recent_workflows.successful / recent_workflows.total * 100) if recent_workflows.total > 0 else 0,
                    'timestamp': datetime.now().isoformat()
                }
        except Exception as e:
            return {'status': 'error', 'error': str(e), 'timestamp': datetime.now().isoformat()}
    
    def check_containers_health(self):
        """Check Docker container health"""
        try:
            import subprocess
            result = subprocess.run(['docker', 'ps', '--format', 'json'], 
                                  capture_output=True, text=True, timeout=10)
            
            containers = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    container = json.loads(line)
                    containers.append({
                        'name': container.get('Names', ''),
                        'status': container.get('Status', ''),
                        'health': 'healthy' if 'healthy' in container.get('Status', '') else 'unknown'
                    })
            
            return {
                'status': 'healthy',
                'containers': containers,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {'status': 'error', 'error': str(e), 'timestamp': datetime.now().isoformat()}
    
    def generate_alerts(self, system_health, dashboard_health, db_health):
        """Generate alerts based on thresholds"""
        alerts = []
        
        # System alerts
        if system_health.get('cpu_percent', 0) > self.alert_thresholds['cpu_percent']:
            alerts.append(f"🚨 High CPU usage: {system_health['cpu_percent']:.1f}%")
        
        if system_health.get('memory_percent', 0) > self.alert_thresholds['memory_percent']:
            alerts.append(f"🚨 High memory usage: {system_health['memory_percent']:.1f}%")
        
        if system_health.get('disk_percent', 0) > self.alert_thresholds['disk_percent']:
            alerts.append(f"🚨 High disk usage: {system_health['disk_percent']:.1f}%")
        
        # Dashboard alerts
        if dashboard_health.get('status') != 'healthy':
            alerts.append(f"🚨 Dashboard unhealthy: {dashboard_health.get('error', 'Unknown error')}")
        
        if dashboard_health.get('response_time', 0) > self.alert_thresholds['response_time']:
            alerts.append(f"🚨 Slow dashboard response: {dashboard_health['response_time']:.2f}s")
        
        # Database alerts
        if db_health.get('status') != 'healthy':
            alerts.append(f"🚨 Database unhealthy: {db_health.get('error', 'Unknown error')}")
        
        recent_success_rate = db_health.get('recent_success_rate', 100)
        if recent_success_rate < 50:  # Less than 50% success rate
            alerts.append(f"🚨 Low recent success rate: {recent_success_rate:.1f}%")
        
        return alerts
    
    def run_monitoring_cycle(self):
        """Run a complete monitoring cycle"""
        print(f"🔍 Production Monitor - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        # Collect health data
        system_health = self.check_system_health()
        dashboard_health = self.check_dashboard_health()
        db_health = self.check_database_health()
        container_health = self.check_containers_health()
        
        # Display system status
        print("💻 System Health:")
        if 'error' not in system_health:
            print(f"  • CPU: {system_health['cpu_percent']:.1f}%")
            print(f"  • Memory: {system_health['memory_percent']:.1f}% ({system_health['memory_available_gb']:.1f}GB free)")
            print(f"  • Disk: {system_health['disk_percent']:.1f}% ({system_health['disk_free_gb']:.1f}GB free)")
        else:
            print(f"  ❌ Error: {system_health['error']}")
        
        # Display dashboard status
        print("\n📊 Dashboard Health:")
        if dashboard_health.get('status') == 'healthy':
            print(f"  • Status: ✅ Healthy")
            print(f"  • Response time: {dashboard_health['response_time']:.2f}s")
            print(f"  • Active scraping: {'Yes' if dashboard_health['is_active'] else 'No'}")
            print(f"  • Total workflows: {dashboard_health['total_workflows']}")
            print(f"  • Success rate: {dashboard_health['success_rate']:.1f}%")
        else:
            print(f"  ❌ Status: {dashboard_health.get('status', 'Unknown')}")
        
        # Display database status
        print("\n🗄️ Database Health:")
        if db_health.get('status') == 'healthy':
            print(f"  • Status: ✅ Healthy")
            print(f"  • Recent workflows (1h): {db_health['recent_total']}")
            print(f"  • Recent success rate: {db_health['recent_success_rate']:.1f}%")
        else:
            print(f"  ❌ Status: {db_health.get('error', 'Unknown error')}")
        
        # Display container status
        print("\n🐳 Container Health:")
        if container_health.get('status') == 'healthy':
            for container in container_health['containers']:
                if 'n8n-scraper' in container['name']:
                    status_icon = "✅" if container['health'] == 'healthy' else "⚠️"
                    print(f"  • {container['name']}: {status_icon} {container['status']}")
        else:
            print(f"  ❌ Error: {container_health.get('error', 'Unknown error')}")
        
        # Generate and display alerts
        alerts = self.generate_alerts(system_health, dashboard_health, db_health)
        if alerts:
            print("\n🚨 ALERTS:")
            for alert in alerts:
                print(f"  {alert}")
        else:
            print("\n✅ No alerts - All systems healthy")
        
        print("\n" + "=" * 60)
        
        return {
            'system': system_health,
            'dashboard': dashboard_health,
            'database': db_health,
            'containers': container_health,
            'alerts': alerts,
            'timestamp': datetime.now().isoformat()
        }

def main():
    """Main monitoring function"""
    monitor = ProductionMonitor()
    
    if len(sys.argv) > 1 and sys.argv[1] == '--continuous':
        # Continuous monitoring mode
        print("🔄 Starting continuous monitoring (Ctrl+C to stop)...")
        try:
            while True:
                monitor.run_monitoring_cycle()
                time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            print("\n🛑 Monitoring stopped by user")
    else:
        # Single check mode
        monitor.run_monitoring_cycle()

if __name__ == "__main__":
    main()
