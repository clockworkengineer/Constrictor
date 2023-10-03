"""TEST"""
# pylint: disable=missing-function-docstring, missing-class-docstring, unused-argument

import pathlib
from queue import Queue
import time
import pytest

from core.consumer import Consumer, ConsumerError
from core.interface.ihandler import IHandler


failure_called: bool = False


def failure_callback(watcher_name: str) -> None:
    pass


class Event:
    def __init__(self, src_path: str) -> None:
        self.src_path = src_path


class TestConsumerHandler(IHandler):
    def __init__(self) -> None:
        self.exit_on_failure = True

    def process(self, source_path: pathlib.Path) -> bool:
        if str(source_path) != ".":
            return True
        else:
            return False

    def status(self) -> str:
        return ""


class TestCoreConsumer:
    def test_consumer_with_valid_parameters(self) -> None:
        queue: Queue = Queue()
        ihandler: IHandler = TestConsumerHandler()
        consumer: Consumer = Consumer(queue, ihandler, failure_callback)

        assert consumer is not None
        assert consumer.is_running() is False

    def test_consumer_with_invalid_qeue(self) -> None:
        queue: Queue = None  # type: ignore
        ihandler: IHandler = TestConsumerHandler()

        with pytest.raises(ConsumerError):
            _: Consumer = Consumer(queue, ihandler, failure_callback)

    def test_consumer_with_invalid_handler(self) -> None:
        queue: Queue = Queue()
        ihandler: IHandler = None  # type: ignore

        with pytest.raises(ConsumerError):
            _: Consumer = Consumer(queue, ihandler, failure_callback)

    def test_consumer_with_invalid_failure_callback(self) -> None:
        queue: Queue = Queue()
        ihandler: IHandler = TestConsumerHandler()

        with pytest.raises(ConsumerError):
            _: Consumer = Consumer(queue, ihandler, None)  # type: ignore

    def test_consumer_with_start(self) -> None:
        queue: Queue = Queue()
        ihandler: IHandler = TestConsumerHandler()
        consumer: Consumer = Consumer(queue, ihandler, failure_callback)

        consumer.start()
        assert consumer.is_running() is True

    def test_consumer_with_start_then_stop(self) -> None:
        queue: Queue = Queue()
        ihandler: IHandler = TestConsumerHandler()
        consumer: Consumer = Consumer(queue, ihandler, failure_callback)

        consumer.start()
        consumer.stop()
        assert consumer.is_running() is False

    def test_consumer_with_start_then_start(self) -> None:
        queue: Queue = Queue()
        ihandler: IHandler = TestConsumerHandler()
        consumer: Consumer = Consumer(queue, ihandler, failure_callback)

        consumer.start()
        consumer.start()

        assert consumer.is_running() is True

    def test_consumer_with_start_then_stop_then_stop(self) -> None:
        queue: Queue = Queue()
        ihandler: IHandler = TestConsumerHandler()
        consumer: Consumer = Consumer(queue, ihandler, failure_callback)

        consumer.start()
        consumer.stop()
        consumer.stop()

        assert consumer.is_running() is False

    def test_consumer_with_stop_when_notstarted(self) -> None:
        queue: Queue = Queue()
        ihandler: IHandler = TestConsumerHandler()
        consumer: Consumer = Consumer(queue, ihandler, failure_callback)

        consumer.stop()

        assert consumer.is_running() is False

    # test for failure calback called

    # def test_consumer_when_a_processing_error_occures(self) -> None:
    #     queue: Queue = Queue()
    #     ihandler: IHandler = TestConsumerHandler()
    #     consumer: Consumer = Consumer(queue, ihandler, failure_callback)

    #     consumer.start()

    #     queue.put(Event("."))

    #     while consumer.is_running():
    #         time.sleep(0.1)

    #     assert failure_called
