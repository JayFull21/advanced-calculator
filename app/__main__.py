"""Allow running the calculator REPL via `python -m app`."""
from app.repl import main

if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())