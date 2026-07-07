"""Interactive REPL for the Advanced Calculator."""
from __future__ import annotations

import logging
import sys

from app.calculator import Calculator
from app.colors import error, info, success, warning
from app.exceptions import DataLoadError, ValidationError
from app.factory import OperationFactory
from app.logger import configure_logging
from app.observer import AutoSaveObserver, LoggingObserver


HELP_TEXT = """\
Commands:
  <op> <a> <b>   Run a calculation (e.g. 'add 2 3')
  history        Show calculation history
  clear          Clear history
  undo           Undo last action
  redo           Redo last undone action
  save [path]    Save history to CSV (uses default path if omitted)
  load [path]    Load history from CSV
  help           Show this message
  exit / quit    Leave the REPL

Available operations: {ops}
"""


class CalculatorREPL:
    def __init__(self, calc: Calculator | None = None):
        self.calc = calc or Calculator()
        self.calc.attach(LoggingObserver())
        if self.calc.config.auto_save:
            self.calc.attach(AutoSaveObserver(self.calc))

    def run(self, input_fn=input, output_fn=print) -> None:
        output_fn(info("Advanced Calculator. Type 'help' for commands."))
        while True:
            try:
                raw = input_fn(">>> ")
            except (EOFError, KeyboardInterrupt):
                output_fn("")
                return
            if not self.handle(raw, output_fn):
                return

    def handle(self, raw: str, output_fn=print) -> bool:
        """Process one line. Return False to exit the loop, True to continue."""
        line = raw.strip()
        if not line:
            return True

        parts = line.split()
        cmd = parts[0].lower()

        if cmd in {"exit", "quit"}:
            output_fn(info("Goodbye!"))
            return False
        if cmd == "help":
            output_fn(info(HELP_TEXT.format(
                ops=", ".join(sorted(OperationFactory.valid_operations()))
            )))
            return True
        if cmd == "history":
            df = self.calc.get_history()
            output_fn(info("(empty)" if df.empty else df.to_string(index=False)))
            return True
        if cmd == "clear":
            self.calc.clear_history()
            output_fn(success("History cleared."))
            return True
        if cmd == "undo":
            try:
                self.calc.undo()
                output_fn(success("Undone."))
            except IndexError:
                output_fn(warning("Nothing to undo."))
            return True
        if cmd == "redo":
            try:
                self.calc.redo()
                output_fn(success("Redone."))
            except IndexError:
                output_fn(warning("Nothing to redo."))
            return True
        if cmd == "save":
            path = parts[1] if len(parts) > 1 else None
            saved_to = self.calc.save_history(path)
            output_fn(success(f"Saved to {saved_to}"))
            return True
        if cmd == "load":
            path = parts[1] if len(parts) > 1 else None
            try:
                self.calc.load_history(path)
                output_fn(success("History loaded."))
            except (FileNotFoundError, DataLoadError) as e:
                output_fn(error(str(e)))
            return True

        if len(parts) != 3:
            output_fn(warning("Unknown command. Type 'help' for usage."))
            return True
        op, a, b = parts
        try:
            result = self.calc.calculate(op, a, b)
            output_fn(success(f"= {result}"))
        except ValidationError as e:
            output_fn(error(f"Error: {e}"))
        return True


def main() -> int:  # pragma: no cover
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    configure_logging()
    CalculatorREPL().run()
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())