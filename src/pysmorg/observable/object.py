import inspect
import logging
import threading
from typing import Any
from weakref import WeakKeyDictionary

from .observer import ObserverType, ObserverSignatureType


class ObservableProperty[T]:
    """
    A descriptor class for creating observable properties on an ObservableObject.
    """
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


class ObservableObject:
    """
    A base class for objects that can have observable properties.

    Attributes:
        _lock (RLock): Reentrant lock for thread-safe operations.
        _logger (Logger): Logger instance for logging messages.
        _observables (Dict[str, Any]): A dictionary of the observable property values.

    Example:
        ```python
        class MyClass(ObservableObject):
            my_property = ObservableProperty(0)

            def on_my_property_changed(self, old_value, new_value):
                print(f"my_property changed from {old_value} to {new_value}")

        def my_observer(value):
            print(f"property updated to {value}")

        obj = MyClass()
        obj.add_observer("my_property", my_observer)
        obj.my_property = 42

        # Output: "my_property changed from 0 to 42"
        #         "property updated to 42"
        ```
    """
    def __init__(self) -> None:
        self.__observers: dict[str, WeakKeyDictionary[ObserverType, ObserverSignatureType]] = {}
        self.__dependents: dict[str, list[str]] = {}
        self._observables: dict[str, Any] = {}
        self._logger: logging.Logger = logging.getLogger(self.__class__.__name__)
        self._lock: threading.RLock = threading.RLock()

    def add_observer(self, key: str, observer: ObserverType) -> None:
        """
        Register an observer to be notified of changes to a specific property.

        Args:
            key (str): The property key to observe.
            observer (ObserverType): The observer callable to register.
        """
        with self._lock:
            if key not in self.__observers:
                self.__observers[key] = WeakKeyDictionary()
            
            match len(inspect.signature(observer).parameters):
                case 0:
                    self.__observers[key][observer] = ObserverSignatureType.NoValue
                case 1:
                    self.__observers[key][observer] = ObserverSignatureType.NewValue
                case 2:
                    self.__observers[key][observer] = ObserverSignatureType.NewOldValue
                case _:
                    raise ValueError("Observer must accept zero, one or two parameters")

    def remove_observer(self, key: str, observer: ObserverType) -> None:
        """
        Unregister an observer from a specific property.

        Args:
            key (str): The property key to stop observing.
            observer (ObserverType): The observer callable to unregister.
        """
        with self._lock:
            if key in self.__observers:
                _ = self.__observers[key].pop(observer, None)
                if not self.__observers[key]:
                    del self.__observers[key]
    
    def notify_observers(self, key: str, prev_value: Any, new_value: Any) -> None:
        """
        Notify all observers of a property change. This method is called automatically when a property is set.

        Args:
            key (str): The property key that was changed.
            prev_value (Any): The previous value of the property.
            new_value (Any): The new value of the property.
        """
        with self._lock:
            observers = self.__observers.get(key, {}).copy()
        for observer, callback_type in observers.items():
            match callback_type:
                case ObserverSignatureType.NoValue:
                    args = ()
                case ObserverSignatureType.NewValue:
                    args = (new_value,)
                case ObserverSignatureType.NewOldValue:
                    args = (prev_value, new_value)
                case _:
                    args = ()
            try:
                _ = observer(*args)
            except Exception as e:
                observer_name = getattr(observer, "__name__", repr(observer))
                self._logger.error(f"Error in observer for '{key}', '{observer_name}': {e}")
