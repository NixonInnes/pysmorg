import threading
from unittest.mock import Mock, call

from pysmorg.observable.object import ObservableObject, ObservableProperty

class SampleObservable(ObservableObject):
    prop_a = ObservableProperty(default=0)
    prop_b = ObservableProperty(default="")

class SampleObservableWithCallback(ObservableObject):
    prop_c = ObservableProperty(default="initial")

    def on_prop_c_changed(self, old, new):
        self.on_prop_c_changed_called = (old, new)

    def __init__(self):
        super().__init__()
        self.on_prop_c_changed_called = None


def test_observer_no_value_called_on_property_change():
    """
    Test that a no-value observer is called when the property changes.
    """
    obj = SampleObservable()
    mock_no_value = Mock()

    # Define an observer that takes no parameters
    def observer_no_value():
        mock_no_value()

    obj.add_observer('prop_a', observer_no_value)

    # Change the property
    obj.prop_a = 10

    # Assert that observer was called once
    mock_no_value.assert_called_once_with()


def test_observer_new_value_called_on_property_change():
    """
    Test that a new-value observer is called with the new value when the property changes.
    """
    obj = SampleObservable()
    mock_new_value = Mock()

    # Define an observer that takes one parameter (new value)
    def observer_new_value(new_value):
        mock_new_value(new_value)

    obj.add_observer('prop_a', observer_new_value)

    # Change the property
    obj.prop_a = 20

    # Assert that observer was called once with new value
    mock_new_value.assert_called_once_with(20)


def test_observer_new_old_value_called_on_property_change():
    """
    Test that a new-old-value observer is called with old and new values when the property changes.
    """
    obj = SampleObservable()
    mock_new_old_value = Mock()

    # Define an observer that takes two parameters (old and new values)
    def observer_new_old_value(old_value, new_value):
        mock_new_old_value(old_value, new_value)

    obj.add_observer('prop_a', observer_new_old_value)

    # Change the property
    obj.prop_a = 30

    # Assert that observer was called once with old and new values
    mock_new_old_value.assert_called_once_with(0, 30)


def test_observers_with_different_signatures():
    """
    Test that observers with different signatures are called appropriately when the property changes.
    """
    obj = SampleObservable()
    mock_no_value = Mock()
    mock_new_value = Mock()
    mock_new_old_value = Mock()

    # Define observers with different signatures
    def observer_no_value():
        mock_no_value()

    def observer_new_value(new_value):
        mock_new_value(new_value)

    def observer_new_old_value(old_value, new_value):
        mock_new_old_value(old_value, new_value)

    obj.add_observer('prop_b', observer_no_value)
    obj.add_observer('prop_b', observer_new_value)
    obj.add_observer('prop_b', observer_new_old_value)

    # Change the property
    obj.prop_b = "Hello"

    # Assert that all observers were called appropriately
    mock_no_value.assert_called_once_with()
    mock_new_value.assert_called_once_with("Hello")
    mock_new_old_value.assert_called_once_with("", "Hello")


def test_observer_not_called_if_no_change():
    """
    Test that observers are not called if the property value does not change.
    """
    obj = SampleObservable()
    mock_new_old_value = Mock()

    # Define an observer that takes two parameters
    def observer_new_old_value(old_value, new_value):
        mock_new_old_value(old_value, new_value)

    obj.add_observer('prop_a', observer_new_old_value)

    # Set to the same value
    obj.prop_a = 0

    # Assert that observer was not called
    mock_new_old_value.assert_not_called()


def test_observer_removed_not_called():
    """
    Test that an observer is not called after it has been removed.
    """
    obj = SampleObservable()
    mock_new_value = Mock()

    # Define an observer that takes one parameter
    def observer_new_value(new_value):
        mock_new_value(new_value)

    obj.add_observer('prop_a', observer_new_value)

    # Remove observer
    obj.remove_observer('prop_a', observer_new_value)

    # Change the property
    obj.prop_a = 100

    # Assert that observer was not called
    mock_new_value.assert_not_called()


def test_multiple_observers_called():
    """
    Test that multiple observers for the same property are all called correctly.
    """
    obj = SampleObservable()
    mock_no_value = Mock()
    mock_new_value = Mock()
    mock_new_old_value = Mock()

    # Define observers with different signatures
    def observer_no_value():
        mock_no_value()

    def observer_new_value(new_value):
        mock_new_value(new_value)

    def observer_new_old_value(old_value, new_value):
        mock_new_old_value(old_value, new_value)

    obj.add_observer('prop_a', observer_no_value)
    obj.add_observer('prop_a', observer_new_value)
    obj.add_observer('prop_a', observer_new_old_value)

    # Change the property
    obj.prop_a = 50

    # Assert that all observers were called appropriately
    mock_no_value.assert_called_once_with()
    mock_new_value.assert_called_once_with(50)
    mock_new_old_value.assert_called_once_with(0, 50)


def test_setting_multiple_properties_notifies_correct_observers():
    """
    Test that setting multiple properties notifies only the observers of the changed property.
    """
    obj = SampleObservable()
    mock_observer_a = Mock()
    mock_observer_b = Mock()

    # Define observers with appropriate signatures
    def observer_a(old_value, new_value):
        mock_observer_a(old_value, new_value)

    def observer_b(old_value, new_value):
        mock_observer_b(old_value, new_value)

    obj.add_observer('prop_a', observer_a)
    obj.add_observer('prop_b', observer_b)

    # Change prop_a
    obj.prop_a = 1

    # Change prop_b
    obj.prop_b = "World"

    # Assert observer_a was called with old and new values
    mock_observer_a.assert_called_once_with(0, 1)

    # Assert observer_b was called with old and new values
    mock_observer_b.assert_called_once_with("", "World")


def test_observer_exception_does_not_stop_others():
    """
    Test that an exception in one observer does not prevent other observers from being notified.
    """
    obj = SampleObservable()
    mock_observer1 = Mock()
    mock_observer2 = Mock(side_effect=Exception("Test exception"))
    mock_observer3 = Mock()

    # Define observers with appropriate signatures
    def observer1(old_value, new_value):
        mock_observer1(old_value, new_value)

    def observer2(old_value, new_value):
        mock_observer2(old_value, new_value)

    def observer3(old_value, new_value):
        mock_observer3(old_value, new_value)

    obj.add_observer('prop_a', observer1)
    obj.add_observer('prop_a', observer2)
    obj.add_observer('prop_a', observer3)

    # Change the property
    obj.prop_a = 2

    # Assert that observer1 was called
    mock_observer1.assert_called_once_with(0, 2)
    # Assert that observer2 was called and raised an exception
    mock_observer2.assert_called_once_with(0, 2)
    # Assert that observer3 was called despite the exception in observer2
    mock_observer3.assert_called_once_with(0, 2)


def test_thread_safety():
    """
    Test that the ObservableObject is thread-safe by performing concurrent property modifications.
    """
    obj = SampleObservable()
    mock_observer = Mock()

    # Define an observer that takes two parameters
    def observer_new_old_value(old_value, new_value):
        mock_observer(old_value, new_value)

    obj.add_observer('prop_a', observer_new_old_value)

    def set_prop_a(values):
        for val in values:
            obj.prop_a = val

    # Define two threads that set prop_a
    thread1 = threading.Thread(target=set_prop_a, args=([1, 2, 3],))
    thread2 = threading.Thread(target=set_prop_a, args=([4, 5, 6],))

    thread1.start()
    thread2.start()

    thread1.join()
    thread2.join()

    # The observer should have been called for each unique change
    # Since thread interleaving is possible, the exact order is not guaranteed
    # The final value should be 6

    # Total number of changes should be 6
    assert mock_observer.call_count == 6

    # Check that the final value is 6
    assert obj.prop_a == 6


def test_on_property_changed_method_called():
    """
    Test that the on_<property>_changed method is called appropriately when the property changes.
    """
    obj = SampleObservableWithCallback()
    obj.prop_c = "changed"

    # Check that on_prop_c_changed was called with correct arguments
    assert obj.on_prop_c_changed_called == ("initial", "changed")


def test_on_property_changed_method_not_called_if_no_change():
    """
    Test that the on_<property>_changed method is not called if the property does not change.
    """
    obj = SampleObservableWithCallback()
    obj.prop_c = "initial"  # Set to the same value

    # Check that on_prop_c_changed was not called
    assert obj.on_prop_c_changed_called is None


def test_observer_called_multiple_times_on_multiple_changes():
    """
    Test that an observer is called multiple times when the property changes multiple times.
    """
    obj = SampleObservable()
    mock_new_value = Mock()

    # Define an observer that takes one parameter
    def observer_new_value(new_value):
        mock_new_value(new_value)

    obj.add_observer('prop_a', observer_new_value)

    # Change the property multiple times
    obj.prop_a = 10
    obj.prop_a = 20
    obj.prop_a = 30

    # Assert that observer was called three times with correct values
    assert mock_new_value.call_count == 3
    mock_new_value.assert_has_calls([
        call(10),
        call(20),
        call(30),
    ], any_order=False)


def test_removing_one_observer_does_not_affect_others():
    """
    Test that removing one observer does not affect other observers.
    """
    obj = SampleObservable()
    mock_observer1 = Mock()
    mock_observer2 = Mock()

    # Define observers
    def observer1(new_value):
        mock_observer1(new_value)

    def observer2(new_value):
        mock_observer2(new_value)

    obj.add_observer('prop_a', observer1)
    obj.add_observer('prop_a', observer2)

    # Remove observer1
    obj.remove_observer('prop_a', observer1)

    # Change the property
    obj.prop_a = 100

    # Assert that observer1 was not called, observer2 was called
    mock_observer1.assert_not_called()
    mock_observer2.assert_called_once_with(100)