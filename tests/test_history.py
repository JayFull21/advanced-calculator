import pandas as pd
import pytest
from app.history import HistoryManager, COLUMNS


@pytest.fixture
def event():
    return {"operation": "add", "a": 1, "b": 2, "result": 3}


class TestAddAndAccess:
    def test_empty_on_init(self, tmp_path):
        hm = HistoryManager(csv_path=tmp_path / "h.csv")
        assert len(hm) == 0
        assert hm.last() is None

    def test_add_event(self, tmp_path, event):
        hm = HistoryManager(csv_path=tmp_path / "h.csv")
        hm.add(event)
        assert len(hm) == 1
        last = hm.last()
        assert last["operation"] == event["operation"]
        assert last["result"] == event["result"]
        assert last["timestamp"] is not None  # stamped automatically

    def test_dataframe_has_expected_columns(self, tmp_path, event):
        hm = HistoryManager(csv_path=tmp_path / "h.csv")
        hm.add(event)
        assert list(hm.dataframe.columns) == COLUMNS

    def test_dataframe_returns_copy(self, tmp_path, event):
        hm = HistoryManager(csv_path=tmp_path / "h.csv")
        hm.add(event)
        df = hm.dataframe
        df.drop(df.index, inplace=True)
        # Original should be untouched
        assert len(hm) == 1

    def test_clear(self, tmp_path, event):
        hm = HistoryManager(csv_path=tmp_path / "h.csv")
        hm.add(event)
        hm.clear()
        assert len(hm) == 0


class TestPersistence:
    def test_save_creates_file(self, tmp_path, event):
        path = tmp_path / "out.csv"
        hm = HistoryManager(csv_path=path)
        hm.add(event)
        result_path = hm.save()
        assert result_path.exists()

    def test_save_creates_missing_parent_dirs(self, tmp_path, event):
        path = tmp_path / "nested" / "dirs" / "h.csv"
        hm = HistoryManager(csv_path=path)
        hm.add(event)
        hm.save()
        assert path.exists()

    def test_roundtrip_save_and_load(self, tmp_path, event):
        path = tmp_path / "h.csv"
        hm1 = HistoryManager(csv_path=path)
        hm1.add(event)
        hm1.add({"operation": "multiply", "a": 3, "b": 4, "result": 12})
        hm1.save()

        hm2 = HistoryManager(csv_path=path)
        hm2.load()
        assert len(hm2) == 2
        assert hm2.last()["result"] == 12

    def test_load_missing_file_raises(self, tmp_path):
        hm = HistoryManager(csv_path=tmp_path / "nope.csv")
        with pytest.raises(FileNotFoundError):
            hm.load()

    def test_save_to_explicit_path(self, tmp_path, event):
        hm = HistoryManager(csv_path=tmp_path / "default.csv")
        hm.add(event)
        other = tmp_path / "other.csv"
        hm.save(other)
        assert other.exists()


class TestEnvConfig:
    def test_env_var_sets_default_path(self, tmp_path, monkeypatch):
        target = tmp_path / "from_env.csv"
        monkeypatch.setenv("CALCULATOR_HISTORY_FILE", str(target))
        hm = HistoryManager()
        hm.add({"operation": "add", "a": 1, "b": 1, "result": 2})
        hm.save()
        assert target.exists()

    def test_explicit_path_overrides_env(self, tmp_path, monkeypatch):
        monkeypatch.setenv("CALCULATOR_HISTORY_FILE", str(tmp_path / "env.csv"))
        explicit = tmp_path / "explicit.csv"
        hm = HistoryManager(csv_path=explicit)
        hm.add({"operation": "add", "a": 1, "b": 1, "result": 2})
        hm.save()
        assert explicit.exists()
        assert not (tmp_path / "env.csv").exists()

class TestTimestampAndMaxSize:
    def test_timestamp_added_automatically(self, tmp_path, event):
        hm = HistoryManager(csv_path=tmp_path / "h.csv")
        hm.add(event)
        assert hm.last()["timestamp"] is not None

    def test_existing_timestamp_preserved(self, tmp_path):
        hm = HistoryManager(csv_path=tmp_path / "h.csv")
        hm.add({"operation": "add", "a": 1, "b": 2, "result": 3,
                "timestamp": "2026-01-01T00:00:00"})
        assert hm.last()["timestamp"] == "2026-01-01T00:00:00"

    def test_timestamp_column_saved_to_csv(self, tmp_path, event):
        path = tmp_path / "h.csv"
        hm = HistoryManager(csv_path=path)
        hm.add(event)
        hm.save()
        header = path.read_text().splitlines()[0]
        assert "timestamp" in header

    def test_max_size_drops_oldest(self, tmp_path):
        hm = HistoryManager(csv_path=tmp_path / "h.csv", max_size=2)
        for i in range(4):
            hm.add({"operation": "add", "a": i, "b": 0, "result": i})
        assert len(hm) == 2
        assert hm.last()["a"] == 3  # newest kept
        assert hm.dataframe.iloc[0]["a"] == 2  # oldest two dropped

    def test_max_size_from_env(self, tmp_path, monkeypatch):
        monkeypatch.setenv("CALCULATOR_MAX_HISTORY_SIZE", "3")
        hm = HistoryManager(csv_path=tmp_path / "h.csv")
        for i in range(5):
            hm.add({"operation": "add", "a": i, "b": 0, "result": i})
        assert len(hm) == 3


class TestMalformedFiles:
    def test_malformed_csv_raises_data_load_error(self, tmp_path):
        from app.exceptions import DataLoadError
        bad = tmp_path / "bad.csv"
        bad.write_text('a,b\n"unclosed quote,1\nx,"y,2,3\n"broken')
        hm = HistoryManager(csv_path=bad)
        with pytest.raises(DataLoadError, match="malformed"):
            hm.load()

    def test_empty_csv_raises_data_load_error(self, tmp_path):
        from app.exceptions import DataLoadError
        empty = tmp_path / "empty.csv"
        empty.write_text("")
        hm = HistoryManager(csv_path=empty)
        with pytest.raises(DataLoadError, match="malformed"):
            hm.load()

    def test_missing_columns_raises_data_load_error(self, tmp_path):
        from app.exceptions import DataLoadError
        wrong = tmp_path / "wrong.csv"
        wrong.write_text("foo,bar\n1,2\n")
        hm = HistoryManager(csv_path=wrong)
        with pytest.raises(DataLoadError, match="missing required columns"):
            hm.load()