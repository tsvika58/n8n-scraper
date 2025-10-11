# Pytest Dashboard - Usage Guide

## 🚀 Quick Start

### Run in NEW Terminal (Recommended)
Opens a dedicated terminal window in Cursor so you can watch tests while working:

```bash
# All tests with coverage (opens new terminal)
make test-dash

# Fast mode (opens new terminal)
make test-dash-fast

# Unit tests only (opens new terminal)
make test-dash-unit

# Integration tests only (opens new terminal)
make test-dash-integration
```

### Run in Current Terminal
If you prefer to run tests in your current terminal:

```bash
# All tests with coverage (current terminal)
make test-dash-here

# Fast mode (current terminal)
make test-dash-fast-here

# Or use the script directly
./test-with-timer.sh -v tests/test_logging.py
```

## 📺 What You See

When you run `make test-dash`, a new terminal opens showing:

```
╔══════════════════════════════════════════════════════════════════════╗
║                   🧪 Pytest Dashboard - New Terminal                 ║
╚══════════════════════════════════════════════════════════════════════╝

📂 Project: n8n-scraper
🔄 Running: ./test-with-timer.sh -v --cov=src --cov-report=term-missing

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🚀 Running Pytest with Live Output
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

============================= test session starts ==============================
tests/test_logging.py::test_setup_logging_default PASSED                 [  8%]
tests/test_logging.py::test_setup_logging_levels PASSED                  [ 16%]
...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Tests Completed Successfully!
⏱️  Duration: 0m 45s
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Press any key to close this terminal...
```

## ✨ Features

### 1. Dedicated Terminal Window
- ✅ Opens in new terminal automatically
- ✅ Takes focus so you see it immediately
- ✅ Stays open after tests complete
- ✅ Can minimize and continue working

### 2. Real-Time Output
- ✅ See every test as it runs (never gets stuck)
- ✅ Live progress percentages
- ✅ Immediate feedback on failures
- ✅ Coverage reports after completion

### 3. Beautiful Formatting
- ✅ Colored banners and headers
- ✅ Success/failure indicators
- ✅ Duration timing
- ✅ Professional appearance

### 4. Flexible Usage
- ✅ Run in new terminal (default)
- ✅ Run in current terminal (if preferred)
- ✅ Works with all pytest arguments
- ✅ Easy Makefile commands

## 📋 Command Reference

| Command | Description | Terminal |
|---------|-------------|----------|
| `make test-dash` | All tests + coverage | New window |
| `make test-dash-fast` | Fast mode (stop on fail) | New window |
| `make test-dash-unit` | Unit tests only | New window |
| `make test-dash-integration` | Integration tests | New window |
| `make test-dash-here` | All tests + coverage | Current |
| `make test-dash-fast-here` | Fast mode | Current |
| `./test-with-timer.sh -v [path]` | Custom args | Current |

## 🎯 Use Cases

### During Development
```bash
# Run fast tests in new terminal while you keep coding
make test-dash-fast

# Your main terminal stays available for other commands
# The test terminal shows live progress
```

### Debugging
```bash
# Run specific test file in new terminal
./test-in-new-terminal.sh -v tests/unit/test_layer1_metadata.py

# Watch it run, see where it fails
# Terminal stays open showing full output
```

### Full Test Suite
```bash
# Run all tests with coverage in new terminal
make test-dash

# Minimize the test terminal
# Keep working while tests run
# Check back later to see results
```

### Quick Checks
```bash
# Run in current terminal when you want to stay focused
make test-dash-here
```

## 🔧 Advanced Usage

### Custom Pytest Arguments
```bash
# Run specific tests by keyword
./test-in-new-terminal.sh -v -k "metadata"

# Run with specific marker
./test-in-new-terminal.sh -v -m "integration"

# Run specific file
./test-in-new-terminal.sh -v tests/test_database.py
```

### Direct Script Usage
```bash
# Use test-with-timer.sh directly in current terminal
./test-with-timer.sh -v --cov=src tests/unit/

# Or use test-in-new-terminal.sh to open new window
./test-in-new-terminal.sh -v tests/integration/
```

## 💡 Pro Tips

1. **Keep Test Terminal Visible**: Position it on a second monitor or split screen
2. **Use Fast Mode**: During development, use `-x` flag to stop on first failure
3. **Filter Tests**: Use `-k` to run only relevant tests while coding
4. **Check Coverage**: Full runs show coverage percentages
5. **Never Gets Stuck**: You ALWAYS see real-time output [[memory:9751166]]

## 🐛 Troubleshooting

### Terminal doesn't open?
- Make sure Cursor is running
- Check that the script is executable: `chmod +x test-in-new-terminal.sh`

### Want to run in current terminal instead?
- Use `make test-dash-here` commands
- Or call `./test-with-timer.sh` directly

### Tests not showing output?
- The scripts use unbuffered output
- You should ALWAYS see pytest output in real-time
- If stuck, press Ctrl+C and try again

## 📊 Comparison

| Method | New Terminal | Real-time Output | Duration Timer | Auto-focus |
|--------|--------------|------------------|----------------|------------|
| `make test` | ❌ | ✅ | ❌ | ❌ |
| `make test-dash` | ✅ | ✅ | ✅ | ✅ |
| `make test-dash-here` | ❌ | ✅ | ✅ | ❌ |
| `pytest` directly | ❌ | ✅ | ❌ | ❌ |

## 🎓 Examples

### Example 1: Continuous Development
```bash
# Open test terminal once
make test-dash-fast

# Keep coding in main terminal
# Glance at test terminal for results
# Terminal stays open showing last run
```

### Example 2: Full Test Run
```bash
# Run complete suite with coverage
make test-dash

# Minimize test terminal
# Continue working
# Check back after 2-3 minutes
# Terminal shows complete results
```

### Example 3: Debugging Specific Test
```bash
# Run one test file to debug
./test-in-new-terminal.sh -v tests/unit/test_layer1_metadata.py

# Watch it execute line by line
# See exactly where it fails
# Terminal stays open with full stack trace
```

## ✅ Benefits

1. **Never Lose Test Output**: Dedicated terminal preserves all output
2. **Keep Working**: Main terminal stays free for other commands
3. **Visual Feedback**: Immediately see when tests start running
4. **Professional**: Beautiful formatting and clear results
5. **Flexible**: Choose new terminal or current terminal as needed
6. **Reliable**: Always shows real-time output, never gets stuck

---

**Try it now:** `make test-dash-fast`





