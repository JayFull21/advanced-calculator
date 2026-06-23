import logging
import pytest
from app.observer import Observer, Subject, LoggingObserver, HistoryObserver


class TestObserverBase:
    def test_cannot_instantiate_abstract_observer(self):
        with pytest.raises(TypeError):
            Observer()


class _Spy(Observer):
    def __init__(self):
        self.calls = []

    def update(self, event):
        self.calls.append(event)


class TestSubject:
    def test_attach_and_notify(self):
        subj = Subject()
        spy = _Spy()
        subj.attach(spy)
        subj.notify({"x": 1})
        assert spy.calls == [{"x": 1}]

    def test_attach_is_idempotent(self):
        subj = Subject()
        spy = _Spy()
        subj.attach(spy)
        subj.attach(spy)
        subj.notify({"x": 1})
        assert len(spy.calls) == 1

    def test_detach_stops_notifications(self):
        subj = Subject()
        spy = _Spy()
        subj.attach(spy)
        subj.detach(spy)
        subj.notify({"x": 1})
        assert spy.calls == []

    def test_detach_unknown_observer_is_safe(self):
        subj = Subject()
        spy = _Spy()
        # Should not raise even though spy was never attached
        subj.detach(spy)

    def test_multiple_observers_all_notified(self):
        subj = Subject()
        a, b = _Spy(), _Spy()
        subj.attach(a)
        subj.attach(b)
        subj.notify({"v": 7})
        assert a.calls == [{"v": 7}]
        assert b.calls == [{"v": 7}]


class TestLoggingObserver:
    def test_logs_calculation(self, caplog):
        caplog.set_level(logging.INFO, logger="calculator")
        obs = LoggingObserver()
        obs.update({"operation": "add", "a": 2, "b": 3, "result": 5})
        assert "add" in caplog.text
        assert "5" in caplog.text

    def test_accepts_custom_logger(self, caplog):
        custom = logging.getLogger("my_custom_logger")
        caplog.set_level(logging.INFO, logger="my_custom_logger")
        obs = LoggingObserver(logger=custom)
        obs.update({"operation": "multiply", "a": 4, "b": 5, "result": 20})
        assert "multiply" in caplog.text


class TestHistoryObserver:
    def test_records_events(self):
        obs = HistoryObserver()
        e1 = {"operation": "add", "a": 1, "b": 2, "result": 3}
        e2 = {"operation": "subtract", "a": 5, "b": 1, "result": 4}
        obs.update(e1)
        obs.update(e2)
        assert obs.records == [e1, e2]

    def test_starts_empty(self):
        assert HistoryObserver().records == []


class TestSubjectWithRealObservers:
    def test_subject_notifies_real_observers(self):
        subj = Subject()
        hist = HistoryObserver()
        subj.attach(hist)
        event = {"operation": "divide", "a": 10, "b": 2, "result": 5}
        subj.notify(event)
        assert hist.records == [event]