"""TEST"""
# pylint: disable=missing-function-docstring, missing-class-docstring, unused-argument

import pathlib
from queue import Queue
import pytest

from core.consumer import Consumer, ConsumerError
from core.interface.ihandler import IHandler


def failure_callback(self) -> None:
    pass


class DummyHandler(IHandler):
    def __init__(self) -> None:
        super().__init__()

    def process(self, source_path: pathlib.Path) -> bool:
        pass

    def status(self) -> str:
        return ""


class TestCoreConsumer:
    def test_consumer_with_valid_parameters(self) -> None:
        queue: Queue = Queue()
        ihandler: IHandler = DummyHandler()
        consumer: Consumer = Consumer(queue, ihandler, failure_callback)

        assert consumer is not None
        assert consumer.is_running() is False

    def test_consumer_with_invalid_qeue(self) -> None:
        queue: Queue = None
        ihandler: IHandler = DummyHandler()

        with pytest.raises(ConsumerError):
            _: Consumer = Consumer(queue, ihandler, failure_callback)

    def test_consumer_with_invalid_handler(self) -> None:
        queue: Queue = Queue()
        ihandler: IHandler = None

        with pytest.raises(ConsumerError):
            _: Consumer = Consumer(queue, ihandler, failure_callback)

    def test_consumer_with_invalid_failure_callback(self) -> None:
        queue: Queue = Queue()
        ihandler: IHandler = DummyHandler()

        with pytest.raises(ConsumerError):
            _: Consumer = Consumer(queue, ihandler, None)

    def test_consumer_with_start(self) -> None:
        queue: Queue = Queue()
        ihandler: IHandler = DummyHandler()
        consumer: Consumer = Consumer(queue, ihandler, failure_callback)

        consumer.start()
        assert consumer.is_running() is True

    def test_consumer_with_start_then_stop(self) -> None:
        queue: Queue = Queue()
        ihandler: IHandler = DummyHandler()
        consumer: Consumer = Consumer(queue, ihandler, failure_callback)

        consumer.start()
        consumer.stop()
        assert consumer.is_running() is False

    def test_consumer_with_start_then_start(self) -> None:
        queue: Queue = Queue()
        ihandler: IHandler = DummyHandler()
        consumer: Consumer = Consumer(queue, ihandler, failure_callback)

        consumer.start()
        consumer.start()

        assert consumer.is_running() is True

    def test_consumer_with_start_then_stop_then_stop(self) -> None:
        queue: Queue = Queue()
        ihandler: IHandler = DummyHandler()
        consumer: Consumer = Consumer(queue, ihandler, failure_callback)

        consumer.start()
        consumer.stop()
        consumer.stop()

        assert consumer.is_running() is False

    def test_consumer_with_stop_when_notstarted(self) -> None:
        queue: Queue = Queue()
        ihandler: IHandler = DummyHandler()
        consumer: Consumer = Consumer(queue, ihandler, failure_callback)

        consumer.stop()

        assert consumer.is_running() is False


# test for failure calback called
