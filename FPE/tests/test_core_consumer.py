"""TEST"""
# pylint: disable=missing-function-docstring, missing-class-docstring, unused-argument

from queue import Queue
import pytest

from core.consumer import Consumer, ConsumerError
from core.interface.ihandler import IHandler


def failure_callback(self) -> None:
    pass


class DummyHandler(IHandler):
    def __init__(self) -> None:
        super().__init__()


class TestCoreConsumer:
    # test for valid creation.

    def test_consumer_with_valid_parameters(self) -> None:
        queue: Queue = Queue()
        ihandler: IHandler = DummyHandler()
        consumer: Consumer = Consumer(queue, ihandler, failure_callback)

        assert consumer is not None
        assert consumer.is_running() is False

    # test for invalid queue

    def test_consumer_with_invalid_qeue(self) -> None:
        queue: Queue = None
        ihandler: IHandler = DummyHandler()

        with pytest.raises(ConsumerError):
            _: Consumer = Consumer(queue, ihandler, failure_callback)

    # test for invalid ihandler
    def test_consumer_with_invalid_handler(self) -> None:
        queue: Queue = Queue()
        ihandler: IHandler = None

        with pytest.raises(ConsumerError):
            _: Consumer = Consumer(queue, ihandler, failure_callback)

    # test for invalid failure function

    def test_consumer_with_invalid_failure_callback(self) -> None:
        queue: Queue = Queue()
        ihandler: IHandler = DummyHandler()

        with pytest.raises(ConsumerError):
            _: Consumer = Consumer(queue, ihandler, None)


# test for start when in initial state
# test for start stop
# test for start start
# test for start stop stop
# test for stop when not started
# test for failure calback called
