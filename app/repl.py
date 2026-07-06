"""Interactive REPL for the Advanced Calculator."""
from __future__ import annotations

import logging
import os
import sys

from dotenv import load_dotenv

from app.calculator import Calculator
from app.exceptions import ValidationError
from app.factory import OperationFactory
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
        load_dotenv()
        self.calc = calc or Calculator()
        self.calc.attach(LoggingObserver())
        if self._auto_save_enabled():
            self.calc.attach(AutoSaveObserver(self.calc))

    @staticmethod
    def _auto_save_enabled() -> bool:
        """Read CALCULATOR_AUTO_SAVE from the environment (default: true)."""
        raw = os.getenv("CALCULATOR_AUTO_SAVE", "true")
        return raw.strip().lower() in {"1", "true", "yes", "on"}

    def run(self, input_fn=input, output_fn=print) -> None:
        output_fn("Advanced Calculator. Type 'help' for commands.")
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
            output_fn("Goodbye!")
            return False
        if cmd == "help":
            output_fn(HELP_TEXT.format(
                ops=", ".join(sorted(OperationFactory.valid_operations()))
            ))
            return True
        if cmd == "history":
            df = self.calc.get_history()
            output_fn("(empty)" if df.empty else df.to_string(index=False))
            return True
        if cmd == "clear":
            self.calc.clear_history()
            output_fn("History cleared.")
            return True
        if cmd == "undo":
            try:
                self.calc.undo()
                output_fn("Undone.")
            except IndexError:
                output_fn("Nothing to undo.")
            return True
        if cmd == "redo":
            try:
                self.calc.redo()
                output_fn("Redone.")
            except IndexError:
                output_fn("Nothing to redo.")
            return True
        if cmd == "save":
            path = parts[1] if len(parts) > 1 else None
            saved_to = self.calc.save_history(path)
            output_fn(f"Saved to {saved_to}")
            return True
        if cmd == "load":
            path = parts[1] if len(parts) > 1 else None
            try:
                self.calc.load_history(path)
                output_fn("History loaded.")
            except FileNotFoundError as e:
                output_fn(str(e))
            return True

        if len(parts) != 3:
            output_fn("Unknown command. Type 'help' for usage.")
            return True
        op, a, b = parts
        try:
            result = self.calc.calculate(op, a, b)
            output_fn(f"= {result}")
        except ValidationError as e:
            output_fn(f"Error: {e}")
        return True


def main() -> int:  # pragma: no cover
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    CalculatorREPL().run()
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())