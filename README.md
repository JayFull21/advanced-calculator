# Advanced Calculator

A modular command-line calculator built in Python for IS601. It supports ten arithmetic operations through an interactive REPL, with undo/redo, persistent history, configurable behavior via environment variables, file logging, and color-coded output — all backed by a 100%-coverage test suite enforced in CI.

## Features

- **Ten operations**: add, subtract, multiply, divide, power, root, modulus, integer division, percentage, and absolute difference
- **Design patterns**:
  - **Factory** — `OperationFactory` creates operation instances by name
  - **Strategy** — each operation is an interchangeable `Operation` subclass
  - **Memento** — undo/redo via history snapshots (`CalculationMemento` + `HistoryCaretaker`)
  - **Observer** — `LoggingObserver` logs every calculation; `AutoSaveObserver` saves history to CSV after each one
  - **Facade** — the `Calculator` class provides one simple interface over validation, operations, history, and notifications
- **History management** — pandas-backed history with operation, operands, result, and timestamp columns; save/load to CSV; configurable max size
- **Configuration** — all behavior tunable through a `.env` file
- **Robust error handling** — custom exceptions (`ValidationError`, `OperationError`, `ConfigurationError`, `DataLoadError`) with clear messages; malformed or missing CSV files are handled gracefully
- **File logging** — all events written to a configurable log file with timestamps and levels
- **Color-coded output** (optional feature) — results in green, errors in red, warnings in yellow, info in cyan via colorama



## Configuration

The application reads settings from a `.env` file in the project root (loaded with python-dotenv). Copy the example file to get started:

```bash
cp .env.example .env
```

| Variable | Description | Default |
|---|---|---|
| `CALCULATOR_LOG_DIR` | Directory for log files | `logs` |
| `CALCULATOR_LOG_FILE` | Full log file path (overrides log dir) | `logs/calculator.log` |
| `CALCULATOR_HISTORY_DIR` | Directory for history files | `data` |
| `CALCULATOR_HISTORY_FILE` | Full history CSV path (overrides history dir) | `data/history.csv` |
| `CALCULATOR_MAX_HISTORY_SIZE` | Max history entries kept (oldest dropped first) | `1000` |
| `CALCULATOR_AUTO_SAVE` | Auto-save history after every calculation | `true` |
| `CALCULATOR_PRECISION` | Decimal places results are rounded to | `10` |
| `CALCULATOR_MAX_INPUT_VALUE` | Largest allowed input (absolute value) | `1e12` |
| `CALCULATOR_DEFAULT_ENCODING` | Encoding for file operations | `utf-8` |

Every variable has a sensible default, so the app runs fine with no `.env` at all. Invalid values (e.g. a negative history size) raise a `ConfigurationError` at startup.



### Commands

| Command | Description |
|---|---|
| `add`, `subtract`, `multiply`, `divide` | Basic arithmetic |
| `power`, `root`, `modulus`, `int_divide`, `percent`, `abs_diff` | Advanced operations |
| `history` | Show calculation history |
| `clear` | Clear history |
| `undo` | Undo the last calculation |
| `redo` | Redo the last undone calculation |
| `save [path]` | Save history to CSV (default path if omitted) |
| `load [path]` | Load history from CSV |
| `help` | Show available commands |
| `exit` / `quit` | Leave the REPL |

History is auto-saved to CSV after every calculation (when `CALCULATOR_AUTO_SAVE=true`), and every event is logged to the configured log file.

## Continuous Integration

A GitHub Actions workflow (`.github/workflows/tests.yml`) runs on every push and pull request to `main`. It checks out the code, sets up Python, installs dependencies, and runs the test suite with coverage — the build fails if coverage drops below 100%.

## Project Structure

```
advanced-calculator/
├── app/
│   ├── calculator.py          # Facade: ties everything together
│   ├── calculator_config.py   # Env-driven configuration
│   ├── colors.py              # Colorama output helpers
│   ├── exceptions.py          # Custom exception hierarchy
│   ├── factory.py             # Operation factory
│   ├── history.py             # Pandas-backed history manager
│   ├── input_validators.py    # Input validation
│   ├── logger.py              # File logging setup
│   ├── memento.py             # Undo/redo state snapshots
│   ├── observer.py            # Logging + auto-save observers
│   ├── operations.py          # Strategy classes for each operation
│   └── repl.py                # Command-line interface
├── tests/                     # Full pytest suite (100% coverage)
├── .github/workflows/         # CI pipeline
├── .env.example               # Configuration template
└── requirements.txt
```