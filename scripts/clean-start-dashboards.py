#!/usr/bin/env python3
"""
Clean start for dashboards - handles port conflicts properly
"""

import psutil
import os
import time
import signal
import subprocess

def kill_process_on_port(port):
    """Kill any process using the specified port"""
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            # Get connections separately (not in iter attrs)
            connections = proc.connections()
            for conn in connections:
                if hasattr(conn.laddr, 'port') and conn.laddr.port == port:
                    cmdline = ' '.join(proc.info['cmdline'])
                    print(f"   🛑 Killing PID {proc.info['pid']} using port {port}: {cmdline[:50]}...")
                    os.kill(proc.info['pid'], signal.SIGKILL)
                    return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, AttributeError):
            pass
    return False

def is_port_free(port):
    """Check if port is free"""
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('127.0.0.1', port))
    sock.close()
    return result != 0

def main():
    print("🔄 Clean Dashboard Startup")
    print("=" * 60)
    
    # Ports to check
    ports = {5002: "Real-time Dashboard", 5004: "Database Viewer"}
    
    # Kill processes on these ports
    print("\n🛑 Cleaning up ports...")
    for port, name in ports.items():
        if not is_port_free(port):
            print(f"   Port {port} in use by {name}")
            kill_process_on_port(port)
        else:
            print(f"   Port {port} is free ✅")
    
    # Wait for cleanup
    print("\n⏳ Waiting for cleanup...")
    time.sleep(3)
    
    # Verify ports are free
    all_free = True
    for port in ports.keys():
        if not is_port_free(port):
            print(f"   ❌ Port {port} still in use!")
            all_free = False
    
    if not all_free:
        print("\n❌ Could not free all ports. Manual intervention needed.")
        return 1
    
    print("   ✅ All ports freed")
    
    # Start dashboards
    print("\n🚀 Starting dashboards...")
    
    # Start Real-time Dashboard
    print("   📊 Starting Real-time Dashboard (5002)...")
    proc1 = subprocess.Popen(
        ["python", "/app/scripts/realtime-dashboard.py"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    print(f"      PID: {proc1.pid}")
    
    # Start Database Viewer
    print("   🗄️  Starting Database Viewer (5004)...")
    proc2 = subprocess.Popen(
        ["python", "/app/scripts/db-viewer.py"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    print(f"      PID: {proc2.pid}")
    
    # Wait for startup
    print("\n⏳ Waiting for startup...")
    time.sleep(10)
    
    # Verify they're running
    print("\n✅ Verifying...")
    
    both_running = True
    
    # Check Real-time Dashboard
    if is_port_free(5002):
        print("   ❌ Real-time Dashboard (5002) - NOT listening")
        both_running = False
    else:
        print("   ✅ Real-time Dashboard (5002) - Listening")
    
    # Check Database Viewer
    if is_port_free(5004):
        print("   ❌ Database Viewer (5004) - NOT listening")
        both_running = False
    else:
        print("   ✅ Database Viewer (5004) - Listening")
    
    if both_running:
        print("\n🎉 All dashboards operational!")
        print("\n📍 Access Points:")
        print("   • Real-time: http://localhost:5002")
        print("   • Database:  http://localhost:5004")
        return 0
    else:
        print("\n⚠️  Some dashboards failed. Check errors above.")
        return 1

if __name__ == "__main__":
    exit(main())

