# Pytest Dashboard 🧪

A beautiful real-time test monitoring dashboard for pytest, inspired by jest-dashboard and adapted for Python projects.

## ✨ Features

- 🎯 **Real-time Test Tracking**: Live updates as tests run
- 📊 **Visual Statistics**: Beautiful terminal UI with test counts and metrics
- 🎨 **Color-coded Results**: Easy-to-read pass/fail indicators
- 📈 **Coverage Reporting**: Real-time coverage percentage updates
- ⚡ **Performance Metrics**: Track test duration and timing
- 🔍 **Failed Test Tracking**: See which tests failed in real-time
- 🎭 **Multiple Modes**: Fast mode, filtered tests, coverage reports

## 🚀 Quick Start

### Installation

First, install the required dependencies:

```bash
pip install rich
```

This is already included in `requirements-dev.txt`, so if you've run `make install-dev`, you're ready!

### Make the script executable

```bash
chmod +x pytest-dashboard.py
```

### Basic Usage

```bash
# Run all tests with dashboard
./pytest-dashboard.py

# Or use python directly
python pytest-dashboard.py
```

## 📋 Usage Modes

### 🎯 Default Mode (with coverage)
Run all tests with coverage reporting:

```bash
./pytest-dashboard.py
```

### ⚡ Fast Mode (no coverage)
Run tests quickly without coverage:

```bash
./pytest-dashboard.py --fast
```

### 🔍 Filtered Tests
Run specific tests using keyword matching:

```bash
# Run only tests matching "layer3"
./pytest-dashboard.py -k layer3

# Run tests from specific path
./pytest-dashboard.py tests/unit/

# Run tests matching marker
./pytest-dashboard.py -m integration
```

### 🚫 No Coverage Mode
Run with verbose output but no coverage:

```bash
./pytest-dashboard.py --no-cov
```

## 🎨 Dashboard Features

### Live Statistics Panel
- ✅ **Passed Tests**: Real-time count of passing tests
- ❌ **Failed Tests**: Track failing tests as they happen
- ⏭️ **Skipped Tests**: See which tests are skipped
- 📊 **Total Count**: Overall test execution progress
- 🎯 **Coverage**: Live coverage percentage (color-coded)
- 🧪 **Current Test**: See which test is currently running

### Progress Panel
- Visual progress bar showing completion percentage
- Failed test list (last 5 failures shown)
- Real-time updates as tests execute

### Header
- Status indicator with emoji (⏳ idle, 🔄 running, ✅ completed, ❌ failed)
- Live duration timer (MM:SS format)
- Blinking indicator when tests are running

## 📊 Integration with Makefile

Add these commands to your Makefile for easy access:

```makefile
# Run tests with dashboard
test-dash:
	./pytest-dashboard.py

# Run fast tests with dashboard
test-fast-dash:
	./pytest-dashboard.py --fast

# Run specific test file with dashboard
test-file-dash:
	./pytest-dashboard.py tests/unit/test_layer1_metadata.py
```

## 🔧 Advanced Usage

### Custom Pytest Arguments

The dashboard passes through standard pytest arguments:

```bash
# Run with verbose output
./pytest-dashboard.py -v

# Run tests matching keyword
./pytest-dashboard.py -k "test_metadata"

# Run specific test markers
./pytest-dashboard.py -m "not slow"

# Run specific test file
./pytest-dashboard.py tests/unit/test_layer3_explainer.py
```

### Integration with CI/CD

```yaml
# GitHub Actions example
- name: Run tests with dashboard
  run: |
    pip install rich
    python pytest-dashboard.py --fast
```

## 🎯 Comparison with Jest Dashboard

| Feature | Jest Dashboard | Pytest Dashboard |
|---------|---------------|------------------|
| Real-time updates | ✅ | ✅ |
| Coverage tracking | ✅ | ✅ |
| Failed test list | ✅ | ✅ |
| Progress bar | ✅ | ✅ |
| Color-coded output | ✅ | ✅ |
| Language | JavaScript | Python |
| UI Library | blessed | rich |
| Test Runner | Jest | pytest |

## 🛠️ Technical Details

### Dependencies
- **rich**: Beautiful terminal UI library for Python
- **pytest**: Testing framework (already in project)

### Output Parsing
The dashboard parses pytest's verbose output in real-time to extract:
- Test pass/fail status
- Current running test
- Coverage percentages
- Test counts and metrics

### Performance
- Minimal overhead on test execution
- Updates UI at 4 FPS for smooth animation
- Non-blocking output parsing

## 📈 Example Output

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
│ 🧪 Current      tests/unit/test_layer3_explainer.py   │
╰───────────────────────────────────────────────────────╯

╭───────────────────── Progress ────────────────────────╮
│ ████████████████████████████████░░░░░░░░ 81.2%        │
│                                                        │
│ Failed Tests:                                          │
│   ❌ tests/unit/test_layer1_metadata.py::test_parse   │
│   ❌ tests/integration/test_layer3_integration.py...  │
╰───────────────────────────────────────────────────────╯
```

## 🔍 Troubleshooting

### Dashboard not updating?
Make sure pytest is outputting verbose mode (`-v` flag is included by default).

### Coverage not showing?
Ensure you have `pytest-cov` installed:
```bash
pip install pytest-cov
```

### Colors not displaying?
Check your terminal supports ANSI colors. Most modern terminals do, including:
- macOS Terminal
- iTerm2
- VS Code integrated terminal
- Cursor IDE terminal

## 🤝 Memory Alignment

This implementation follows the established pattern from jest-dashboard [[memory:9604042]]:
- Beautiful, readable output format
- Real-time progress visibility
- Visual indicators (emojis, colors, progress bars)
- No silent mode that hides progress

Aligns with testing memory [[memory:9751166]] and [[memory:9747532]]:
- Always shows live test output
- Never hides or silences test progress
- User can see tests running in real-time
- Clear indication of test progress or stuck tests

## 📄 License

MIT License - Same as jest-dashboard

## 🙏 Acknowledgments

- Inspired by the jest-dashboard project
- Built with the excellent Rich library by Will McGugan
- Designed for the n8n-scraper project

---

**Happy Testing with Beautiful Dashboards! 🧪✨**





