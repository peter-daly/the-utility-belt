import pytest

from theutilitybelt.collections.queue import BoundedQueue, Queue


def test_queue_get_raises_error_when_empty():
    q = Queue[int]()
    with pytest.raises(IndexError):
        q.get()


def test_queue_is_empty():
    q = Queue[int]()
    assert q.is_empty()

    q.put(1)
    assert not q.is_empty()


def test_queue_queue_is_fifo():
    q = Queue[int]()
    q.put(1)
    q.put(2)
    q.put(3)

    assert q.get() == 1
    assert q.get() == 2
    assert q.get() == 3


def test_bounded_queue_get_raises_error_when_empty():
    q = BoundedQueue[int]()
    with pytest.raises(IndexError):
        q.get()


def test_bounded_queue_is_empty():
    q = BoundedQueue[int]()
    assert q.is_empty()

    q.put(1)
    assert not q.is_empty()

    q.get()
    assert q.is_empty()


def test_bounded_queue_queue_is_fifo():
    q = BoundedQueue[int]()
    q.put(1)
    q.put(2)
    q.put(3)

    assert q.get() == 1
    assert q.get() == 2
    assert q.get() == 3


def test_bounded_queue_raises_overflow_error():
    q = BoundedQueue[int](size=2)
    q.put(1)
    q.put(2)

    with pytest.raises(OverflowError):
        q.put(3)


def test_head_and_tail_refresh_correctly():
    q = BoundedQueue[int](size=4)
    q.put(1)
    q.put(2)
    q.put(3)
    q.put(4)
    q.get()
    q.put(5)

    assert q._count == 4
    assert q._head == 1
    assert q._tail == 1
