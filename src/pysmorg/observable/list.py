from collections import UserList
from collections.abc import Iterable
from enum import Enum
import logging
import threading
from typing import Self, override
from weakref import WeakSet

from .observer import ObserverNoValueType


class ListModificationType(Enum):
    """
    An enumeration of list modification types that can be observed.
    """
    ALL = 0
    APPEND = 1
    EXTEND = 2
    INSERT = 3
    REMOVE = 4
    UPDATE = 5
    CLEAR = 6


class ObservableList[T](UserList[T]):
    """
    A thread-safe, observable list that notifies registered observers of modifications.

    Attributes:
        data (List[T]): The underlying list storing items.

        _lock (RLock): Reentrant lock for thread-safe operations.
        _logger (Logger): Logger instance for logging messages.

    Example:
        ```python
        ol = ObservableList([1, 2, 3])

        def my_observer():
            print("List modified!")
        
        def my_append_observer():
            print("Item appended!")

        ol.add_observer(my_observer) # Note: This observer will be notified of all modifications.
        ol.add_observer(my_append_observer, ListModificationType.APPEND)

        ol.append(4)

        # Output: "List modified!"
        #         "Item appended!"
        ```
    """

    def __init__(self, initial: list[T] | None = None) -> None:
        super().__init__(initial or [])

        self._logger: logging.Logger = logging.getLogger(self.__class__.__name__)
        self._lock: threading.RLock = threading.RLock()

        self.__observers: dict[ListModificationType, WeakSet[ObserverNoValueType]] = {}

    def add_observer(
        self,
        observer: ObserverNoValueType,
        mod_type: ListModificationType = ListModificationType.ALL,
    ) -> None:
        """
        Register an observer to be notified of specific list modifications.

        Args:
            observer (ObserverNoValueType): The observer callable to register.
            mod_type (ListModificationType, optional): The type of modifications to observe. Defaults to ListModificationType.ALL.
                The following types are supported:
                    - ListModificationType.ALL: Observe all modifications.
                    - ListModificationType.APPEND: Observe append operations.
                    - ListModificationType.EXTEND: Observe extend operations.
                    - ListModificationType.INSERT: Observe insert operations.
                    - ListModificationType.REMOVE: Observe remove operations.
                    - ListModificationType.UPDATE: Observe update operations.
                    - ListModificationType.CLEAR: Observe clear operations.

        Raises:
            ValueError: If the observer is not callable.
        """
        with self._lock:
            if mod_type not in self.__observers:
                self.__observers[mod_type] = WeakSet()
            self.__observers[mod_type].add(observer)

    def remove_observer(
        self,
        observer: ObserverNoValueType,
        mod_type: ListModificationType = ListModificationType.ALL,
    ) -> None:
        """
        Unregister an observer from being notified of specific list modifications.

        Args:
            observer (ObserverNoValueType): The observer callable to unregister.
            mod_type (ListModificationType, optional): The type of modifications to stop observing. Defaults to ListModificationType.ALL.
                The following types are supported:
                    - ListModificationType.ALL: Observe all modifications.
                    - ListModificationType.APPEND: Observe append operations.
                    - ListModificationType.EXTEND: Observe extend operations.
                    - ListModificationType.INSERT: Observe insert operations.
                    - ListModificationType.REMOVE: Observe remove operations.
                    - ListModificationType.UPDATE: Observe update operations.
                    - ListModificationType.CLEAR: Observe clear operations.
        """
        with self._lock:
            if mod_type in self.__observers:
                if observer not in self.__observers[mod_type]:
                    self._logger.warning(
                        f"Observer not found for list modification type {mod_type}"
                    )
                    return
                self.__observers[mod_type].discard(observer)

    def notify_observers(self, mod_type: ListModificationType) -> None:
        """
        Notify all registered observers of a list modification. This is automatically called after a list operation.

        Args:
            mod_type (ListModificationType): The type of modification to notify observers of.
                The following types are supported:
                    - ListModificationType.ALL: Observe all modifications.
                    - ListModificationType.APPEND: Observe append operations.
                    - ListModificationType.EXTEND: Observe extend operations.
                    - ListModificationType.INSERT: Observe insert operations.
                    - ListModificationType.REMOVE: Observe remove operations.
                    - ListModificationType.UPDATE: Observe update operations.
                    - ListModificationType.CLEAR: Observe clear operations.
        """
        with self._lock:
            observers = list(self.__observers.get(ListModificationType.ALL, []))
            if mod_type != ListModificationType.ALL:
                observers.extend(self.__observers.get(mod_type, []))

        for observer in observers:
            try:
                observer()
            except Exception as e:
                observer_name = getattr(observer, "__name__", repr(observer))
                self._logger.error(f"Error in observer for {mod_type}, {observer_name}: {e}")

    @override
    def __setitem__(self, i: int, item: T) -> None: # pyright: ignore[reportIncompatibleMethodOverride]
        with self._lock:
            super().__setitem__(i, item)
        self.notify_observers(ListModificationType.UPDATE)

    @override
    def __delitem__(self, i: int) -> None: # pyright: ignore[reportIncompatibleMethodOverride]
        with self._lock:
            super().__delitem__(i)
        self.notify_observers(ListModificationType.REMOVE)

    @override
    def __iadd__(self, other: Iterable[T]) -> Self:
        with self._lock:
            _ = super().__iadd__(other)
        self.notify_observers(ListModificationType.EXTEND)
        return self

    @override
    def __imul__(self, n: int) -> Self:
        with self._lock:
            _ = super().__imul__(n)
        self.notify_observers(ListModificationType.EXTEND)
        return self

    @override
    def append(self, item: T) -> None:
        with self._lock:
            super().append(item)
        self.notify_observers(ListModificationType.APPEND)

    @override
    def insert(self, i: int, item: T) -> None:
        with self._lock:
            super().insert(i, item)
        self.notify_observers(ListModificationType.INSERT)

    @override
    def pop(self, i: int = -1) -> T:
        with self._lock:
            item = super().pop(i)
        self.notify_observers(ListModificationType.REMOVE)
        return item

    @override
    def remove(self, item: T) -> None:
        with self._lock:
            super().remove(item)
        self.notify_observers(ListModificationType.REMOVE)

    @override
    def clear(self) -> None:
        with self._lock:
            super().clear()
        self.notify_observers(ListModificationType.CLEAR)

    @override
    def reverse(self) -> None:
        with self._lock:
            super().reverse()
        self.notify_observers(ListModificationType.UPDATE)

    @override
    def sort(self, /, *args, **kwds) -> None:
        with self._lock:
            super().sort(*args, **kwds)
        self.notify_observers(ListModificationType.UPDATE)

    @override
    def extend(self, other: Iterable[T]) -> None:
        with self._lock:
            super().extend(other)
        self.notify_observers(ListModificationType.EXTEND)
