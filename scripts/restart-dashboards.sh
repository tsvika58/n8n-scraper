#!/bin/bash
# Restart dashboards with proper cleanup

echo "🔄 Restarting N8N Scraper Dashboards..."

# Kill all python processes (except PID 1 which keeps container alive)
echo "🛑 Stopping existing processes..."
python -c "
import psutil
import os
for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
    try:
        if proc.info['pid'] != 1 and 'python' in proc.info['name']:
            cmdline = ' '.join(proc.info['cmdline'])
            if 'dashboard' in cmdline or 'db-viewer' in cmdline:
                print(f'   Killing PID {proc.info[\"pid\"]}: {cmdline[:60]}...')
                os.kill(proc.info['pid'], 9)
    except:
        pass
"

# Wait for ports to be released
echo "⏳ Waiting for ports to be released..."
sleep 3

# Check if ports are free
python -c "
import socket
import sys

def check_port(port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('127.0.0.1', port))
    sock.close()
    return result != 0  # True if port is free

port_5002_free = check_port(5002)
port_5004_free = check_port(5004)

if not port_5002_free:
    print('❌ Port 5002 still in use!')
if not port_5004_free:
    print('❌ Port 5004 still in use!')

if not (port_5002_free and port_5004_free):
    print('⚠️  Some ports still in use, forcing cleanup...')
    import os
    os.system('fuser -k 5002/tcp 2>/dev/null || true')
    os.system('fuser -k 5004/tcp 2>/dev/null || true')
    import time
    time.sleep(2)
"

# Start Real-time Dashboard
echo "📊 Starting Real-time Dashboard (port 5002)..."
python /app/scripts/realtime-dashboard.py > /dev/null 2>&1 &
REALTIME_PID=$!
echo "   Started with PID: $REALTIME_PID"

# Start Database Viewer
echo "🗄️  Starting Database Viewer (port 5004)..."
python /app/scripts/db-viewer.py > /dev/null 2>&1 &
VIEWER_PID=$!
echo "   Started with PID: $VIEWER_PID"

# Wait and verify
sleep 5

echo ""
echo "✅ Verifying dashboards..."

# Check if processes are still running
python -c "
import psutil
import sys

realtime_running = False
viewer_running = False

for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
    try:
        cmdline = ' '.join(proc.info['cmdline'])
        if 'realtime-dashboard' in cmdline:
            realtime_running = True
            print(f'   ✅ Realtime Dashboard: PID {proc.info[\"pid\"]}')
        if 'db-viewer' in cmdline:
            viewer_running = True
            print(f'   ✅ Database Viewer: PID {proc.info[\"pid\"]}')
    except:
        pass

if not realtime_running:
    print('   ❌ Realtime Dashboard not running!')
if not viewer_running:
    print('   ❌ Database Viewer not running!')

sys.exit(0 if (realtime_running and viewer_running) else 1)
"

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 Dashboards started successfully!"
    echo ""
    echo "📍 Access Points:"
    echo "   • Real-time: http://localhost:5002"
    echo "   • Database:  http://localhost:5004"
else
    echo ""
    echo "⚠️  Some dashboards failed to start. Check logs."
fi

