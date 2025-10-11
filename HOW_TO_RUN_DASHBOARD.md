# 🎯 How to Run Pytest Dashboard in Cursor Terminal

## ✅ **Solution: Use Cursor Tasks**

Your pytest dashboard is now integrated with Cursor's task system!

### **Quick Steps:**

1. **Open Command Palette**
   - Press `Cmd+Shift+P` (or `Ctrl+Shift+P`)

2. **Run Task**
   - Type "Run Task"
   - Select from:
     - 🧪 **Pytest Dashboard - Full Suite** (with coverage)
     - 🧪 **Pytest Dashboard - Fast Mode** (stop on first failure)
     - 🧪 **Pytest Dashboard - Unit Tests**
     - 🧪 **Pytest Dashboard - Integration Tests**
     - 🧪 **Pytest Dashboard - Current File**

3. **Watch It Run!**
   - Dashboard opens in a **NEW terminal tab** at the bottom
   - You'll see the live sticky bar with spinner
   - Tests run with real-time updates
   - Clean exit when complete

---

## 🎨 **What You'll See:**

```
╔══════════════════════════════════════════════════════════════════════════════╗
║                    🧪 PYTEST LIVE DASHBOARD                    ║
╚══════════════════════════════════════════════════════════════════════════════╝

============================= test session starts ==============================

════════════════════════════════════════════════════════════════════════════════
🔄 Running: 00:05   ⠸ LIVE   📊 Tests: ✅ 12 ❌ 0 ⏭️  0 | Total: 12
🎯 Coverage: 14.0%   🧪 Current: tests/test_logging.py::test_log_...
════════════════════════════════════════════════════════════════════════════════
Press Ctrl+C to stop tests
```

**Live Features:**
- ✅ **Sticky Bottom Bar** - Always visible at bottom of terminal
- ✅ **Animated Spinner** - Shows live progress (⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏)
- ✅ **Real-time Stats** - Passed/Failed/Skipped counts update live
- ✅ **Live Timer** - Shows elapsed time (00:05)
- ✅ **Coverage Tracking** - Shows coverage percentage as it builds
- ✅ **Current Test** - Displays which test is running
- ✅ **Clean Exit** - Returns control to terminal when done

---

## 📝 **Available Tasks:**

| Task | Description | Command |
|------|-------------|---------|
| 🧪 Pytest Dashboard - Full Suite | Run all tests with coverage | Default task |
| 🧪 Pytest Dashboard - Fast Mode | Stop on first failure, no coverage | Fast testing |
| 🧪 Pytest Dashboard - Unit Tests | Run only unit tests | tests/unit/ |
| 🧪 Pytest Dashboard - Integration Tests | Run only integration tests | tests/integration/ |
| 🧪 Pytest Dashboard - Current File | Run tests in current file | ${file} |

---

## 🚀 **Keyboard Shortcuts:**

1. **Open Command Palette:** `Cmd+Shift+P`
2. **Open New Terminal:** `Cmd+Shift+\`` (backtick)
3. **Focus Terminal:** `Ctrl+\``
4. **Kill Process:** `Ctrl+C` in terminal

---

## 💡 **Pro Tips:**

1. **Set Default Task:** "Full Suite" is set as default test task
2. **Multiple Terminals:** Run different tasks in separate terminals
3. **Task History:** Recent tasks appear at top of task list
4. **Terminal Focus:** Tasks automatically focus the terminal
5. **Panel Management:** Tasks use `"panel": "new"` to open fresh terminals

---

## 🐛 **Troubleshooting:**

### Can't find tasks?
- Make sure you're in the n8n-scraper workspace
- Check that `.vscode/tasks.json` exists

### Dashboard not showing?
- Ensure virtual environment exists: `python -m venv venv`
- Install dependencies: `pip install -r requirements.txt`

### Tests not running?
- Check you're in the correct directory
- Verify pytest is installed: `pytest --version`

---

## 📚 **More Information:**

- Full guide: [PYTEST_DASHBOARD_QUICKSTART.md](./PYTEST_DASHBOARD_QUICKSTART.md)
- Documentation: [PYTEST_DASHBOARD_README.md](./PYTEST_DASHBOARD_README.md)
- Migration guide: [JEST_TO_PYTEST_DASHBOARD_MIGRATION.md](./JEST_TO_PYTEST_DASHBOARD_MIGRATION.md)

---

## 🎉 **That's It!**

You now have a **jest-dashboard equivalent for Python** that:
- Opens in proper Cursor terminal tabs ✅
- Shows live progress with sticky bar ✅
- Has animated spinner ✅
- Tracks coverage in real-time ✅
- Exits cleanly ✅

**Just press `Cmd+Shift+P` → "Run Task" → "🧪 Pytest Dashboard - Full Suite"**





