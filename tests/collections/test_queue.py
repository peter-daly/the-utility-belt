import pytest

from theutilitybelt.collections.utils import Queue


def test_get_raises_error_when_empty():
    q = Queue[int]()
    with pytest.raises(IndexError):
        q.get()


def test_is_empty():
    q = Queue[int]()
    assert q.is_empty()

    q.put(1)
    assert not q.is_empty()


def test_queue_is_fifo():
    q = Queue[int]()
    q.put(1)
    q.put(2)
    q.put(3)

    assert q.get() == 1
    assert q.get() == 2
    assert q.get() == 3
