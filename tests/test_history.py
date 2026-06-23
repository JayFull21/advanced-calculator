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
        assert hm.last() == event

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