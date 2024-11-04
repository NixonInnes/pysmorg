import logging
from unittest.mock import Mock, call
from pysmorg.observable.list import ObservableList, ListModificationType

def test_add_observer_all_notified_on_append():
    """
    Test that an observer subscribed to ALL modification types is notified on append.
    """
    ol = ObservableList([1, 2, 3])
    mock_all_observer = Mock()
    
    ol.add_observer(mock_all_observer, ListModificationType.ALL)
    ol.append(4)
    
    mock_all_observer.assert_called_once()


def test_add_observer_specific_notified_only_on_append():
    """
    Test that an observer subscribed to APPEND is only notified on append operations.
    """
    ol = ObservableList([1, 2, 3])
    mock_append_observer = Mock()
    mock_remove_observer = Mock()
    
    ol.add_observer(mock_append_observer, ListModificationType.APPEND)
    ol.add_observer(mock_remove_observer, ListModificationType.REMOVE)
    
    ol.append(4)
    ol.remove(2)
    
    mock_append_observer.assert_called_once()
    mock_remove_observer.assert_called_once()


def test_observer_not_called_for_other_modifications():
    """
    Test that an observer subscribed to APPEND is not notified on REMOVE operations.
    """
    ol = ObservableList([1, 2, 3])
    mock_append_observer = Mock()
    
    ol.add_observer(mock_append_observer, ListModificationType.APPEND)
    ol.remove(2)
    
    mock_append_observer.assert_not_called()


def test_remove_observer_no_longer_notified():
    """
    Test that removing an observer prevents it from being notified on future modifications.
    """
    ol = ObservableList([1, 2, 3])
    mock_observer = Mock()
    
    ol.add_observer(mock_observer, ListModificationType.APPEND)
    ol.append(4)
    ol.remove_observer(mock_observer, ListModificationType.APPEND)
    ol.append(5)
    
    mock_observer.assert_called_once()


def test_multiple_observers_called():
    """
    Test that multiple observers subscribed to the same modification type are all notified.
    """
    ol = ObservableList([1, 2, 3])
    mock_observer1 = Mock()
    mock_observer2 = Mock()
    
    ol.add_observer(mock_observer1, ListModificationType.APPEND)
    ol.add_observer(mock_observer2, ListModificationType.APPEND)
    
    ol.append(4)
    
    mock_observer1.assert_called_once()
    mock_observer2.assert_called_once()


def test_observer_exception_does_not_stop_others():
    """
    Test that an exception in one observer does not prevent other observers from being notified.
    """
    ol = ObservableList([1, 2, 3])
    mock_observer1 = Mock()
    mock_observer2 = Mock(side_effect=Exception("Test exception"))
    mock_observer3 = Mock()
    
    ol.add_observer(mock_observer1, ListModificationType.APPEND)
    ol.add_observer(mock_observer2, ListModificationType.APPEND)
    ol.add_observer(mock_observer3, ListModificationType.APPEND)
    
    ol.append(4)
    
    mock_observer1.assert_called_once()
    mock_observer2.assert_called_once()
    mock_observer3.assert_called_once()


def test_observer_all_called_on_multiple_modifications():
    """
    Test that an observer subscribed to ALL is called on various modification types.
    """
    ol = ObservableList([1, 2, 3])
    mock_all_observer = Mock()
    
    ol.add_observer(mock_all_observer, ListModificationType.ALL)
    
    ol.append(4)
    ol.remove(2)
    ol.insert(0, 0)
    ol.clear()
    
    assert mock_all_observer.call_count == 4


def test_thread_safety_with_concurrent_appends():
    """
    Test that ObservableList is thread-safe by performing concurrent append operations.
    """
    import threading
    
    ol = ObservableList([])
    mock_observer = Mock()
    
    ol.add_observer(mock_observer, ListModificationType.APPEND)
    
    def append_items(items):
        for item in items:
            ol.append(item)
    
    thread1 = threading.Thread(target=append_items, args=([1, 2, 3],))
    thread2 = threading.Thread(target=append_items, args=([4, 5, 6],))
    
    thread1.start()
    thread2.start()
    
    thread1.join()
    thread2.join()
    
    assert len(ol) == 6
    assert mock_observer.call_count == 6
    expected_calls = [call() for _ in range(6)]
    assert mock_observer.mock_calls == expected_calls


def test_observer_called_multiple_times_on_multiple_changes():
    """
    Test that an observer is called the correct number of times corresponding to multiple modifications.
    """
    ol = ObservableList([1, 2, 3])
    mock_observer = Mock()
    
    ol.add_observer(mock_observer, ListModificationType.APPEND)
    
    ol.append(4)
    ol.append(5)
    ol.append(6)
    
    assert mock_observer.call_count == 3


def test_observer_all_and_specific_called_correctly():
    """
    Test that observers subscribed to ALL and specific modification types are both called appropriately.
    """
    ol = ObservableList([1, 2, 3])
    mock_all_observer = Mock()
    mock_append_observer = Mock()
    
    ol.add_observer(mock_all_observer, ListModificationType.ALL)
    ol.add_observer(mock_append_observer, ListModificationType.APPEND)
    
    ol.append(4)
    
    mock_all_observer.assert_called_once()
    mock_append_observer.assert_called_once()


def test_observer_not_called_after_removal_from_specific_modification():
    """
    Test that removing an observer from a specific modification type does not affect its subscription to other types.
    """
    ol = ObservableList([1, 2, 3])
    mock_all_observer = Mock()
    mock_append_observer = Mock()
    
    ol.add_observer(mock_all_observer, ListModificationType.ALL)
    ol.add_observer(mock_append_observer, ListModificationType.APPEND)
    
    ol.remove_observer(mock_append_observer, ListModificationType.APPEND)
    
    ol.append(4)
    ol.remove(2)
    
    assert mock_all_observer.call_count == 2
    mock_append_observer.assert_not_called()


def test_observer_not_called_if_not_subscribed():
    """
    Test that an observer is not called if it is not subscribed to the corresponding modification type.
    """
    ol = ObservableList([1, 2, 3])
    mock_observer = Mock()
    
    ol.add_observer(mock_observer, ListModificationType.REMOVE)
    
    ol.append(4)
    
    mock_observer.assert_not_called()


def test_observer_subscription_to_multiple_modification_types():
    """
    Test that an observer can subscribe to multiple modification types and is notified accordingly.
    """
    ol = ObservableList([1, 2, 3])
    mock_observer = Mock()
    
    ol.add_observer(mock_observer, ListModificationType.APPEND)
    ol.add_observer(mock_observer, ListModificationType.REMOVE)
    
    ol.append(4)
    ol.remove(2)
    
    assert mock_observer.call_count == 2


def test_observer_not_called_after_all_observers_removed():
    """
    Test that observers are not called after all observers have been removed.
    """
    ol = ObservableList([1, 2, 3])
    mock_observer1 = Mock()
    mock_observer2 = Mock()
    
    ol.add_observer(mock_observer1, ListModificationType.APPEND)
    ol.add_observer(mock_observer2, ListModificationType.APPEND)
    
    ol.remove_observer(mock_observer1, ListModificationType.APPEND)
    ol.remove_observer(mock_observer2, ListModificationType.APPEND)
    
    ol.append(4)
    
    mock_observer1.assert_not_called()
    mock_observer2.assert_not_called()
