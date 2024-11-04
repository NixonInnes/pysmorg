from _typeshed import SupportsKeysAndGetItem
from collections import UserDict
from enum import Enum
import logging
import threading
from typing import Self, override
from weakref import WeakSet

from .observer import ObserverNoValueType


class DictModificationType(Enum):
    """
    An enumeration of dictionary modification types that can be observed.
    """
    ALL = 0
    UPDATED = 1
    EXTEND = 2
    REMOVE = 3
    CLEAR = 4


# TODO: Review and update the override methods to ensure they are complete.
# TODO: Can this support ObserverNewValueType and ObserverNewOldValueType?
class ObservableDict[K, V](UserDict[K, V]):
    """
    A thread-safe, observable dictionary that notifies registered observers of modifications.

    Attributes:
        data (Dict[K, V]): The underlying dictionary storing items.

        _lock (RLock): Reentrant lock for thread-safe operations.
        _logger (Logger): Logger instance for logging messages.
    """
    def __init__(self, initial: dict[K, V] | None = None) -> None:
        super().__init__(initial or {})

        self._logger: logging.Logger = logging.getLogger(self.__class__.__name__)
        self._lock: threading.RLock = threading.RLock()

        self.__observers: dict[DictModificationType, WeakSet[ObserverNoValueType]] = {
            DictModificationType.ALL: WeakSet()
        }

    def add_observer(self, observer: ObserverNoValueType, mod_type: DictModificationType = DictModificationType.ALL) -> None:
        """
        Register an observer to be notified of dictionary modifications.

        Args:
            observer (ObserverNoValueType): The observer callable to register.
            modification_type (DictModificationType): The type of modification to observe.
        """
        with self._lock:
            if mod_type not in self.__observers:
                self.__observers[mod_type] = WeakSet()

            self.__observers[mod_type].add(observer)
    
    def remove_observer(self, observer: ObserverNoValueType, mod_type: DictModificationType = DictModificationType.ALL) -> None:
        """
        Unregister an observer from dictionary modifications.

        Args:
            observer (ObserverNoValueType): The observer callable to unregister.
            modification_type (DictModificationType): The type of modification to stop observing.
        """
        with self._lock:
            if mod_type in self.__observers:
                if observer not in self.__observers[mod_type]:
                    self._logger.warning(f"Observer not found for modification type {mod_type}")
                    return
                self.__observers[mod_type].discard(observer)

    def notify_observers(self, mod_type: DictModificationType) -> None:
        """
        Notify all observers of a dictionary modification.

        Args:
            mod_type (DictModificationType): The type of modification that occurred.
        """
        with self._lock:
            observers = list(self.__observers.get(DictModificationType.ALL, []))
            if mod_type != DictModificationType.ALL:
                observers.extend(self.__observers.get(mod_type, []))

        for observer in observers:
            try:
                observer()
            except Exception as e:
                observer_name = getattr(observer, "__name__", repr(observer))
                self._logger.error(f"Error in observer for {mod_type}, {observer_name}: {e}")

    @override
    def __setitem__(self, key: K, value: V) -> None:
        with self._lock:
            super().__setitem__(key, value)
        self.notify_observers(DictModificationType.UPDATED)
    
    @override
    def __delitem__(self, key: K) -> None:
        with self._lock:
            super().__delitem__(key)
        self.notify_observers(DictModificationType.REMOVE)

    @override
    def __ior__(self, other: SupportsKeysAndGetItem[K, V]) -> Self:
        with self._lock:
            _ = super().__ior__(other)
        # TODO: Review the type of modification to notify observers of
        self.notify_observers(DictModificationType.EXTEND)
        return self
    
    @override
    def clear(self) -> None:
        with self._lock:
            super().clear()
        self.notify_observers(DictModificationType.CLEAR)

    @override
    def pop(self, key: K, default: V | None = None) -> V | None:
        with self._lock:
            value = super().pop(key, default)
        self.notify_observers(DictModificationType.REMOVE)
        return value

    @override
    def popitem(self) -> tuple[K, V]:
        with self._lock:
            key, value = super().popitem()
        self.notify_observers(DictModificationType.REMOVE)
        return key, value
