from enum import Enum
import inspect
import logging
import threading
from typing import Any, Callable
from weakref import WeakKeyDictionary

class CallbackSignatureType(Enum):
    NoValue = 0
    NewValue = 1
    NewOldValue = 2

class ObservableProperty[T]:
    def __init__(self, default: T = None) -> None:
        self.name: str | None = None
        self.default: T = default

    def __set_name__(self, owner: "ObservableObject", name: str):
        self.name = name

    def __get__(self, instance: "ObservableObject", owner: type["ObservableObject"]) -> T:
        if self.name is None:
            raise AttributeError("ObservableProperty must be assigned to a class attribute")
        with instance._lock:
            return instance._observables.get(self.name, self.default)

    def __set__(self, instance: "ObservableObject", value: T) -> None:
        if self.name is None:
            raise AttributeError("ObservableProperty must be assigned to a class attribute")

        with instance._lock:
            prev_value = instance._observables.get(self.name, self.default)
            if prev_value == value: # No change
                return
            instance._observables[self.name] = value

        if hasattr(instance, f"on_{self.name}_changed"):
            getattr(instance, f"on_{self.name}_changed")(prev_value, value)
        instance.notify_observers(self.name, prev_value, value)

    
ObserverNoValueType = Callable[[], None]
ObserverNewValueType = Callable[[Any], None]
ObserverNewOldValueType = Callable[[Any, Any], None]
ObserverType = ObserverNoValueType | ObserverNewValueType | ObserverNewOldValueType


class ObservableObject:
    def __init__(self) -> None:
        self.__observers: dict[str, WeakKeyDictionary[ObserverType, CallbackSignatureType]] = {}
        self.__dependents: dict[str, list[str]] = {}
        self._observables: dict[str, Any] = {}
        self._logger = logging.getLogger(self.__class__.__name__)
        self._lock: threading.RLock = threading.RLock()

    def add_observer(self, key: str, observer: ObserverType) -> None:
        with self._lock:
            if key not in self.__observers:
                self.__observers[key] = WeakKeyDictionary()
            
            match len(inspect.signature(observer).parameters):
                case 0:
                    self.__observers[key][observer] = CallbackSignatureType.NoValue
                case 1:
                    self.__observers[key][observer] = CallbackSignatureType.NewValue
                case 2:
                    self.__observers[key][observer] = CallbackSignatureType.NewOldValue
                case _:
                    raise ValueError("Observer must accept zero, one or two parameters")

    def remove_observer(self, key: str, observer: ObserverType) -> None:
        with self._lock:
            if key in self.__observers:
                _ = self.__observers[key].pop(observer, None)
                if not self.__observers[key]:
                    del self.__observers[key]
    
    def notify_observers(self, key: str, prev_value: Any, new_value: Any) -> None:
        with self._lock:
            observers = self.__observers.get(key, {}).copy()
        for observer, callback_type in observers.items():
            match callback_type:
                case CallbackSignatureType.NoValue:
                    args = ()
                case CallbackSignatureType.NewValue:
                    args = (new_value,)
                case CallbackSignatureType.NewOldValue:
                    args = (prev_value, new_value)
                case _:
                    args = ()
            try:
                _ = observer(*args)
            except Exception as e:
                self._logger.error(f"Error in observer for '{key}', '{observer.__name__}': {e}")
