from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv

from app.exceptions import DataLoadError


COLUMNS = ["operation", "a", "b", "result", "timestamp"]


class HistoryManager:
    """Stores calculation events in a pandas DataFrame, persistable to CSV."""

    def __init__(
        self,
        csv_path: str | os.PathLike | None = None,
        max_size: int | None = None,
        encoding: str | None = None,
    ):
        load_dotenv()
        # Priority: explicit arg > env var > default
        self._csv_path = Path(
            csv_path
            or os.getenv("CALCULATOR_HISTORY_FILE")
            or "history.csv"
        )
        self._max_size = (
            max_size
            if max_size is not None
            else int(os.getenv("CALCULATOR_MAX_HISTORY_SIZE", "1000"))
        )
        self._encoding = (
            encoding or os.getenv("CALCULATOR_DEFAULT_ENCODING") or "utf-8"
        )
        self._df = pd.DataFrame(columns=COLUMNS)

    # ----- mutation -----

    def add(self, event: dict) -> None:
        row = {col: event.get(col) for col in COLUMNS}
        if row.get("timestamp") is None:
            row["timestamp"] = datetime.now().isoformat(timespec="seconds")
        self._df = pd.concat(
            [self._df, pd.DataFrame([row], columns=COLUMNS)],
            ignore_index=True,
        )
        # Enforce the configured maximum history size (drop oldest first).
        if len(self._df) > self._max_size:
            self._df = self._df.iloc[-self._max_size:].reset_index(drop=True)

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
        self._df.to_csv(target, index=False, encoding=self._encoding)
        return target

    def load(self, path: str | os.PathLike | None = None) -> None:
        source = Path(path) if path else self._csv_path
        if not source.exists():
            raise FileNotFoundError(f"History file not found: {source}")
        try:
            df = pd.read_csv(source, encoding=self._encoding)
        except (pd.errors.ParserError, pd.errors.EmptyDataError, UnicodeDecodeError) as e:
            raise DataLoadError(f"History file is malformed: {source} ({e})")
        missing = [c for c in COLUMNS if c not in df.columns]
        if missing:
            raise DataLoadError(
                f"History file is missing required columns {missing}: {source}"
            )
        self._df = df[COLUMNS]