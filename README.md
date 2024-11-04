# PySmorg
A smorgasbord of useful python things.

## Observable
PySmorg provides an implementation of the Observer pattern through the ObservableObject and ObservableProperty classes. This allows you to create objects with properties that can be observed for changes, enabling reactive programming paradigms.

### `ObservableObject`
The ObservableObject class serves as a base class that provides observable property functionality. It manages observers, handles thread-safe notifications, and allows for property change callbacks.

#### Features
- Observer Management: Add, remove, and notify observers for specific properties.
- Callback Signatures: Supports observers with zero, one, or two parameters to accommodate different notification needs; i.e. no value, new value and new & old value.
- Thread Safety: Utilizes reentrant locks (`RLock`) to ensure safe concurrent access in multi-threaded applications.
- Weak References: Stores observers using `WeakSet` to prevent memory leaks by allowing garbage collection of unused observers.
- Automatic Callbacks: Optionally define `on_<property>_changed` methods within your class to handle property changes internally.

#### Usage Example
```python
from pysmorg import ObservableObject, ObservableProperty

# Define your observable class
class MyClass(ObservableObject):
    age = ObservableProperty(default=0)
    name = ObservableProperty(default="")

    def __init__(self):
        super().__init__()

    # Optional callback method
    def on_age_changed(self, old, new):
        print(f"Age changed from {old} to {new}")

# Define observer functions
def observer_no_value():
    print("No-value observer triggered.")

def observer_new_value(new_value):
    print(f"New value observer received: {new_value}")

def observer_new_old_value(old_value, new_value):
    print(f"New & old value observer recieved: {old_value}, {new_value}")

# Usage
if __name__ == "__main__":
    obj = MyClass()

    # Add observers to 'age' property
    obj.add_observer('age', observer_no_value)
    obj.add_observer('age', observer_new_value)
    obj.add_observer('age', observer_new_old_value)

    # Change the 'age' property
    obj.age = 25
    obj.age = 30

    # Remove an observer
    obj.remove_observer('age', observer_no_value)

    # Change the 'age' property again
    obj.age = 35

    # Set the 'name' property (no observers added)
    obj.name = "James"

    # Final
    print(f"Final Name: {obj.name}")
    print(f"Final Age: {obj.age}")
```

**Expected output:**
```
Age changed from 0 to 25
No-value observer triggered.
New value observer received: 25
New & old value observer recieved: 0, 25
Age changed from 25 to 30
No-value observer triggered.
New value observer received: 30
New & old value observer recieved: 25, 30
Age changed from 30 to 35
New value observer received: 35
New & old value observer recieved: 30, 35
Name: James
Final Age: 65
```


### `ObservableList`
The `ObservableList` class extends Python's built-in list behavior by allowing observers to monitor and react to changes within the list. It supports various modification types, enabling fine-grained control over how observers are notified about changes.

#### Features
- Observer Management: Add and remove observers for specific list modification types.
- Modification Types: Categorizes list changes (e.g., append, extend, insert, remove, update, clear) to notify relevant observers.
- Thread Safety: Utilizes reentrant locks (`RLock`) to ensure safe concurrent modifications in multi-threaded environments.
- Weak References: Stores observers using `WeakSet` to prevent memory leaks by allowing garbage collection of unused observers.
- Flexible Notifications: Observers can subscribe to all modifications or specific types, providing flexibility in how they react to changes.

#### Usage Example
```python
from pysmorg import ObservableList, ListModificationType

# Define observer functions
def observer_all():
    print("All operations observer triggered.")

def observer_append():
    print(f"Append observer triggered.")

def observer_remove():
    print("Remove observer triggered.")

# Usage
if __name__ == "__main__":
    ol = ObservableList([1, 2, 3])

    # Add observers
    ol.add_observer(observer_all)
    ol.add_observer(observer_append, ListModificationType.APPEND)
    ol.add_observer(observer_remove, ListModificationType.REMOVE)

    # Perform list operations
    ol.append(4)
    ol.remove(2)
```

**Expected Output**
```
All operations observer triggered.
Append observer triggered.

All operations observer triggered.
Remove observer triggered.
```