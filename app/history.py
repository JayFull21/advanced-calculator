from __future__ import annotations

import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv


COLUMNS = ["operation", "a", "b", "result"]


class HistoryManager:
    """Stores calculation events in a pandas DataFrame, persistable to CSV."""

    def __init__(self, csv_path: str | os.PathLike | None = None):
        load_dotenv()
        # Priority: explicit arg > env var > default
        self._csv_path = Path(
            csv_path
            or os.getenv("CALCULATOR_HISTORY_FILE")
            or "history.csv"
        )
        self._df = pd.DataFrame(columns=COLUMNS)

    # ----- mutation -----

    def add(self, event: dict) -> None:
        row = {col: event.get(col) for col in COLUMNS}
        self._df = pd.concat(
            [self._df, pd.DataFrame([row], columns=COLUMNS)],
            ignore_index=True,
        )

    def clear(self) -> None:
        self._df = pd.DataFrame(columns=COLUMNS)

    # ----- access -----

    @property
    def dataframe(self) -> pd.DataFrame:
        return self._df.copy()

    def __len__(self) -> int:
        return len(self._df)

    def last(self) -> dict | None:
        if self._df.empty:
            return None
        return self._df.iloc[-1].to_dict()

    # ----- persistence -----

    def save(self, path: str | os.PathLike | None = None) -> Path:
        target = Path(path) if path else self._csv_path
        target.parent.mkdir(parents=True, exist_ok=True)
        self._df.to_csv(target, index=False)
        return target

    def load(self, path: str | os.PathLike | None = None) -> None:
        source = Path(path) if path else self._csv_path
        if not source.exists():
            raise FileNotFoundError(f"History file not found: {source}")
        self._df = pd.read_csv(source)