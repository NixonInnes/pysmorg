# PySmorg
A smorgasbord of useful python things.

## Iterable

### `t_range`
` t_range` is a generator function that emulates Python's built-in `range()` function for `datetime` objects. It allows you to iterate over a sequence of datetimes by specifying a start and stop datetime, and either a step `timedelta` or a number of steps (`n_steps`). This functionality is particularly useful for generating datetime sequences for scheduling, time series data generation, and other time-based iterations.

#### Features
- Flexible Step Definition: Specify the step size directly using a `timedelta`, or define the number of steps (`n_steps`) to automatically calculate the step.
- Supports Both Directions: Generate sequences that move forward (start < stop) with positive steps or backward (start > stop) with negative steps.
- Edge Case Handling: Properly handles scenarios where the start and stop datetimes are the same, or when steps do not evenly divide the total duration.
- Generator Efficiency: Efficiently generates datetimes on-the-fly without storing the entire range in memory.
- Error Handling: Raises appropriate exceptions for invalid inputs, such as specifying both `step` and `n_steps`, non-positive `n_steps`, or mismatched step directions.

#### Usage Example

```python
from datetime import datetime, timedelta
from pysmorg.iterable import t_range

# Example 1: Using step
start_time = datetime(2024, 1, 1, 0, 0, 0)
stop_time = datetime(2024, 1, 1, 1, 0, 0)
step_duration = timedelta(minutes=15)

print("Example 1: Using step")
for dt in t_range(start_time, stop_time, step=step_duration):
    print(dt)

# Output:
# 2024-01-01 00:00:00
# 2024-01-01 00:15:00
# 2024-01-01 00:30:00
# 2024-01-01 00:45:00

# Example 2: Using n_steps
start_time = datetime(2024, 1, 1, 0, 0, 0)
stop_time = datetime(2024, 1, 1, 1, 0, 0)
number_of_steps = 4

for dt in t_range(start_time, stop_time, n_steps=number_of_steps):
    print(dt)

# Output:
# 2024-01-01 00:00:00
# 2024-01-01 00:15:00
# 2024-01-01 00:30:00
# 2024-01-01 00:45:00

# Example 3: Generating a reverse range with negative step
start_time = datetime(2024, 1, 1, 1, 0, 0)
stop_time = datetime(2024, 1, 1, 0, 0, 0)
step_duration = timedelta(minutes=-15)

for dt in t_range(start_time, stop_time, step=step_duration):
    print(dt)

# Output:
# 2024-01-01 01:00:00
# 2024-01-01 00:45:00
# 2024-01-01 00:30:00
# 2024-01-01 00:15:00
```

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
from pysmorg.observable import ObservableObject, ObservableProperty

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
from pysmorg.observable import ObservableList, ListModificationType

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