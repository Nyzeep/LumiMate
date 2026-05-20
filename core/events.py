from __future__ import annotations

from collections.abc import Callable
from threading import RLock
from typing import Any


class EventHook:
    """Small thread-safe signal replacement for the Python runtime."""

    def __init__(self) -> None:
        self._callbacks: list[Callable[..., Any]] = []
        self._lock = RLock()

    def connect(self, callback: Callable[..., Any]) -> None:
        with self._lock:
            if callback not in self._callbacks:
                self._callbacks.append(callback)

    def disconnect(self, callback: Callable[..., Any]) -> None:
        with self._lock:
            self._callbacks = [item for item in self._callbacks if item is not callback]

    def emit(self, *args: Any, **kwargs: Any) -> None:
        with self._lock:
            callbacks = list(self._callbacks)
        for callback in callbacks:
            callback(*args, **kwargs)
