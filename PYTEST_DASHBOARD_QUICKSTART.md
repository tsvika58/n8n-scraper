# Pytest Dashboard - Quick Start Guide 🚀

## TL;DR - Just Run It!

### 🎯 **BEST METHOD: Use Cursor Tasks** (Opens in New Terminal Tab!)

1. Press `Cmd+Shift+P` (Command Palette)
2. Type "Run Task"
3. Select **"🧪 Pytest Dashboard - Full Suite"**
4. **Dashboard opens in a NEW terminal tab!** ✨

### 📋 **One-Line Command** (For New Terminal)

Open new terminal (`Cmd+Shift+\``) and paste:

```bash
cd "/Users/tsvikavagman/Desktop/Code Projects/shared-tools/n8n-scraper" && source venv/bin/activate && python pytest-dashboard-visible.py -v --cov=src --cov-report=term-missing
```

### 🛠️ **Make Commands** (Runs in Chat Output)

```bash
# All tests with beautiful dashboard
make test-dash

# Fast mode (stop on first failure)
make test-dash-fast

# Unit tests only
make test-dash-unit

# Integration tests only
make test-dash-integration
```

> **Note**: Cursor Tasks open in proper terminal tabs. Make commands run in chat output (you need to expand to see).

## What You Get

```
╔══════════════════════════════════════════════════════════════╗
║ 🔄 Pytest Dashboard | Duration: 00:45 ● LIVE                ║
╚══════════════════════════════════════════════════════════════╝

╭─────────────────── Test Statistics ───────────────────╮
│ ✅ Passed       15                                     │
│ ❌ Failed       2                                      │
│ ⏭️  Skipped     1                                      │
│ 📊 Total        18                                     │
│ 🎯 Coverage     85.3%                                  │
│ 🧪 Current      tests/unit/test_layer3...             │
╰───────────────────────────────────────────────────────╯

╭───────────────────── Progress ────────────────────────╮
│ ████████████████████████████████░░░░░░░░ 81.2%        │
╰───────────────────────────────────────────────────────╯
```

## Available Commands

| Command | Description |
|---------|-------------|
| `make test-dash` | Run all tests with dashboard + coverage |
| `make test-dash-fast` | Run tests fast (no coverage, stop on first fail) |
| `make test-dash-unit` | Run only unit tests with dashboard |
| `make test-dash-integration` | Run only integration tests with dashboard |

## Direct Python Usage

```bash
# All tests
./pytest-dashboard.py

# Specific test file
./pytest-dashboard.py tests/unit/test_layer1_metadata.py

# Filter by keyword
./pytest-dashboard.py -k "metadata"

# Fast mode
./pytest-dashboard.py --fast

# No coverage
./pytest-dashboard.py --no-cov
```

## Why Use Dashboard vs Regular pytest?

### Regular pytest:
```
test_layer1_metadata.py::test_extract_basic_info PASSED
test_layer1_metadata.py::test_extract_with_tags PASSED
test_layer3_explainer.py::test_analyze_nodes FAILED
...
(lots of text scrolling)
```

### Dashboard:
- ✅ **See progress at a glance** - Visual stats always visible
- 🎯 **Real-time coverage** - Watch your coverage percentage grow
- ⏱️ **Live timer** - Know exactly how long tests are running
- 📊 **Clear metrics** - Pass/fail counts updated instantly
- 🎨 **Beautiful UI** - Professional terminal interface
- 🚨 **Failed test tracking** - See which tests failed in real-time

## Perfect For:

- 👀 **Watching tests run** - Know if they're progressing or stuck [[memory:9751166]]
- 📈 **Coverage tracking** - See coverage improve as tests complete
- 🐛 **Debugging** - Spot failed tests immediately
- 🎯 **Focus mode** - Beautiful UI keeps you engaged
- 📊 **Presentations** - Show test runs professionally

## Installation

Already done! The `rich` library is in `requirements.txt` and installed in `venv/`.

If you need to set up the virtual environment:
```bash
# Create venv (if not exists)
python -m venv venv

# Activate it
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

The Makefile commands automatically activate the venv for you!

## Pro Tips

1. **Use fast mode during development:**
   ```bash
   make test-dash-fast
   ```

2. **Run specific test categories:**
   ```bash
   ./pytest-dashboard.py -m unit
   ./pytest-dashboard.py -m integration
   ```

3. **Test specific files while coding:**
   ```bash
   ./pytest-dashboard.py tests/unit/test_layer1_metadata.py
   ```

4. **Watch for failures:**
   The dashboard shows failed tests in the progress panel as they happen!

## Keyboard Shortcuts

- `Ctrl+C` - Stop tests and show summary
- Tests will show live updates automatically
- Dashboard refreshes 4 times per second

## Troubleshooting

**Dashboard not showing colors?**
- Make sure you're using a modern terminal (iTerm2, VS Code terminal, Cursor IDE terminal)

**Want to see raw pytest output?**
- Use regular `make test` or `pytest` commands
- Dashboard shows parsed, beautified version

**Coverage not appearing?**
- Dashboard parses coverage from pytest-cov
- Make sure `pytest-cov` is installed (it's in requirements.txt)

## Comparison

| Feature | `make test` | `make test-dash` |
|---------|-------------|------------------|
| Test execution | ✅ | ✅ |
| Coverage reports | ✅ | ✅ |
| Raw output | ✅ | ❌ |
| Beautiful UI | ❌ | ✅ |
| Real-time stats | ❌ | ✅ |
| Progress bar | ❌ | ✅ |
| Live timer | ❌ | ✅ |
| Failed test list | ❌ | ✅ |
| Visual appeal | ⭐ | ⭐⭐⭐⭐⭐ |

## Next Steps

1. Try it now: `make test-dash`
2. See full docs: `PYTEST_DASHBOARD_README.md`
3. Star the repo if you love it! ⭐

---

**Built with ❤️ for the n8n-scraper project**

