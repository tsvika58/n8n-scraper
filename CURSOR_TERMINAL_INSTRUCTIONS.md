# 🎯 Running Pytest Dashboard in Cursor Terminal

## ✅ **Recommended Method: Manual New Terminal**

Since AppleScript automation requires special permissions, here's the **easiest way** to run the dashboard in a new Cursor terminal tab:

### **Quick Steps:**

1. **Open New Terminal in Cursor:**
   - Press `Cmd+Shift+\`` (backtick) OR
   - Click the `+` icon in the terminal panel OR
   - Use Command Palette (`Cmd+Shift+P`) → "Terminal: Create New Terminal"

2. **Navigate to Project:**
   ```bash
   cd "/Users/tsvikavagman/Desktop/Code Projects/shared-tools/n8n-scraper"
   ```

3. **Activate Virtual Environment:**
   ```bash
   source venv/bin/activate
   ```

4. **Run Dashboard:**
   ```bash
   # Full test suite with coverage
   python pytest-dashboard-visible.py -v --cov=src --cov-report=term-missing
   
   # Fast tests (stop on first failure)
   python pytest-dashboard-visible.py -v -x
   
   # Unit tests only
   python pytest-dashboard-visible.py -v tests/unit/
   
   # Integration tests only
   python pytest-dashboard-visible.py -v tests/integration/
   
   # Specific test file
   python pytest-dashboard-visible.py -v tests/test_logging.py
   ```

---

## 🚀 **One-Line Command for Cursor Terminal**

Copy and paste this into a **new Cursor terminal**:

```bash
cd "/Users/tsvikavagman/Desktop/Code Projects/shared-tools/n8n-scraper" && source venv/bin/activate && python pytest-dashboard-visible.py -v --cov=src --cov-report=term-missing
```

---

## 📋 **Create Cursor Task (Recommended!)**

You can create a **Cursor task** for easy access:

1. Open Command Palette (`Cmd+Shift+P`)
2. Search for "Tasks: Configure Task"
3. Add this configuration:

```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "🧪 Pytest Dashboard (Full)",
      "type": "shell",
      "command": "cd '/Users/tsvikavagman/Desktop/Code Projects/shared-tools/n8n-scraper' && source venv/bin/activate && python pytest-dashboard-visible.py -v --cov=src --cov-report=term-missing",
      "presentation": {
        "reveal": "always",
        "panel": "new",
        "focus": true
      },
      "problemMatcher": []
    },
    {
      "label": "🧪 Pytest Dashboard (Fast)",
      "type": "shell",
      "command": "cd '/Users/tsvikavagman/Desktop/Code Projects/shared-tools/n8n-scraper' && source venv/bin/activate && python pytest-dashboard-visible.py -v -x",
      "presentation": {
        "reveal": "always",
        "panel": "new",
        "focus": true
      },
      "problemMatcher": []
    }
  ]
}
```

Then run with `Cmd+Shift+P` → "Tasks: Run Task" → "🧪 Pytest Dashboard"

---

## 🛠️ **Alternative: Use Make Commands**

If you prefer `make` commands, you can still use them but they'll run in the chat output:

```bash
cd "/Users/tsvikavagman/Desktop/Code Projects/shared-tools/n8n-scraper"
make test-dash        # Full suite
make test-dash-fast   # Fast mode
make test-dash-unit   # Unit tests only
```

---

## 🎨 **What You'll See:**

```
╔══════════════════════════════════════════════════════════════════════════════╗
║                    🧪 PYTEST LIVE DASHBOARD                    ║
╚══════════════════════════════════════════════════════════════════════════════╝

============================= test session starts ==============================
platform darwin -- Python 3.11.1, pytest-8.4.2, pluggy-1.6.0

════════════════════════════════════════════════════════════════════════════════
🔄 Running: 00:05   ⠸ LIVE   📊 Tests: ✅ 12 ❌ 0 ⏭️  0 | Total: 12
🎯 Coverage: 14.0%   🧪 Current: tests/test_logging.py::test_log_...
════════════════════════════════════════════════════════════════════════════════
Press Ctrl+C to stop tests
```

**Features:**
- ✅ Sticky bottom bar with live stats
- ✅ Animated spinner showing test progress
- ✅ Real-time test counts (passed/failed/skipped)
- ✅ Live timer showing elapsed time
- ✅ Coverage percentage tracking
- ✅ Current test name display
- ✅ Clean exit back to terminal

---

## 💡 **Pro Tips:**

1. **Keep Terminal Open:** The dashboard terminal stays open after tests complete
2. **Multiple Tabs:** You can run multiple dashboards in different terminals
3. **Keyboard Shortcuts:** Use `Cmd+Shift+\`` to quickly open new terminals
4. **Focus Management:** New terminals automatically get focus
5. **Clean Exit:** Dashboard returns control to terminal - no hanging!

---

## 🐛 **Troubleshooting:**

### "ModuleNotFoundError: No module named 'rich'"
Make sure virtual environment is activated:
```bash
source venv/bin/activate
```

### "pytest: command not found"
Ensure you're in the project directory and venv is activated:
```bash
cd "/Users/tsvikavagman/Desktop/Code Projects/shared-tools/n8n-scraper"
source venv/bin/activate
```

### Dashboard not showing
Make sure you're using `pytest-dashboard-visible.py`, not the old versions:
```bash
python pytest-dashboard-visible.py -v tests/
```





