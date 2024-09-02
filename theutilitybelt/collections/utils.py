from collections import deque
from typing import Generic, TypeVar

TItem = TypeVar("TItem")


class Queue(Generic[TItem]):
    def __init__(self, max_size: int | None = None):
        self._items = deque(maxlen=max_size)

    def put(self, item: TItem):
        self._items.append(item)

    def get(self) -> TItem:
        return self._items.popleft()

    def is_empty(self) -> bool:
        return len(self._items) == 0

    def safe_get(self) -> TItem | None:
        if self.is_empty():
            return None

        return self.get()
