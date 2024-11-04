from collections.abc import Generator
from datetime import datetime, timedelta
import pytest

from pysmorg.iterable.t_range import t_range

# Helper function to collect generator results
def collect(generator: Generator[datetime, None, None]) -> list[datetime]:
    return list(generator)

# Test Cases

def test_positive_step():
    start = datetime(2024, 1, 1, 0, 0, 0)
    stop = datetime(2024, 1, 1, 1, 0, 0)
    step = timedelta(minutes=15)
    expected = [
        datetime(2024, 1, 1, 0, 0, 0),
        datetime(2024, 1, 1, 0, 15, 0),
        datetime(2024, 1, 1, 0, 30, 0),
        datetime(2024, 1, 1, 0, 45, 0),
    ]
    result = collect(t_range(start, stop, step=step))
    assert result == expected

def test_negative_step():
    start = datetime(2024, 1, 1, 1, 0, 0)
    stop = datetime(2024, 1, 1, 0, 0, 0)
    step = timedelta(minutes=-15)
    expected = [
        datetime(2024, 1, 1, 1, 0, 0),
        datetime(2024, 1, 1, 0, 45, 0),
        datetime(2024, 1, 1, 0, 30, 0),
        datetime(2024, 1, 1, 0, 15, 0),
    ]
    result = collect(t_range(start, stop, step=step))
    assert result == expected

def test_n_steps_positive():
    start = datetime(2024, 1, 1, 0, 0, 0)
    stop = datetime(2024, 1, 1, 1, 0, 0)
    n_steps = 4
    expected = [
        datetime(2024, 1, 1, 0, 0, 0),
        datetime(2024, 1, 1, 0, 15, 0),
        datetime(2024, 1, 1, 0, 30, 0),
        datetime(2024, 1, 1, 0, 45, 0),
    ]
    result = collect(t_range(start, stop, n_steps=n_steps))
    assert result == expected

def test_n_steps_negative():
    start = datetime(2024, 1, 1, 1, 0, 0)
    stop = datetime(2024, 1, 1, 0, 0, 0)
    n_steps = 4
    expected = [
        datetime(2024, 1, 1, 1, 0, 0),
        datetime(2024, 1, 1, 0, 45, 0),
        datetime(2024, 1, 1, 0, 30, 0),
        datetime(2024, 1, 1, 0, 15, 0),
    ]
    result = collect(t_range(start, stop, n_steps=n_steps))
    assert result == expected

def test_start_equals_stop_with_step():
    start = datetime(2024, 1, 1, 0, 0, 0)
    stop = datetime(2024, 1, 1, 0, 0, 0)
    step = timedelta(minutes=15)
    result = collect(t_range(start, stop, step=step))
    assert result == []

def test_start_equals_stop_with_n_steps():
    start = datetime(2024, 1, 1, 0, 0, 0)
    stop = datetime(2024, 1, 1, 0, 0, 0)
    n_steps = 4
    with pytest.raises(ValueError, match="No range can be generated with 'start' equal to 'stop'."):
        _ =  list(t_range(start, stop, n_steps=n_steps))

def test_zero_step():
    start = datetime(2024, 1, 1, 0, 0, 0)
    stop = datetime(2024, 1, 1, 1, 0, 0)
    step = timedelta(seconds=0)
    with pytest.raises(ValueError, match="'step' must not be zero."):
        _ = list(t_range(start, stop, step=step))

def test_zero_n_steps():
    start = datetime(2024, 1, 1, 0, 0, 0)
    stop = datetime(2024, 1, 1, 1, 0, 0)
    n_steps = 0
    with pytest.raises(ValueError, match="'n_steps' must be a positive integer."):
        _ = list(t_range(start, stop, n_steps=n_steps))

def test_negative_n_steps():
    start = datetime(2024, 1, 1, 1, 0, 0)
    stop = datetime(2024, 1, 1, 0, 0, 0)
    n_steps = -4
    with pytest.raises(ValueError, match="'n_steps' must be a positive integer."):
        _ = list(t_range(start, stop, n_steps=n_steps))

def test_both_step_and_n_steps():
    start = datetime(2024, 1, 1, 0, 0, 0)
    stop = datetime(2024, 1, 1, 1, 0, 0)
    step = timedelta(minutes=15)
    n_steps = 4
    with pytest.raises(ValueError, match="t_range\\(\\) requires either 'step' OR 'n_steps' to be specified, but not both\\."):
        _ = list(t_range(start, stop, step=step, n_steps=n_steps))

def test_neither_step_n_steps():
    start = datetime(2024, 1, 1, 0, 0, 0)
    stop = datetime(2024, 1, 1, 1, 0, 0)
    with pytest.raises(ValueError, match="t_range\\(\\) requires either 'step' OR 'n_steps' to be specified, but not both\\."):
        _ = list(t_range(start, stop))

def test_step_direction_mismatch_positive():
    # start < stop but step is negative
    start = datetime(2024, 1, 1, 0, 0, 0)
    stop = datetime(2024, 1, 1, 1, 0, 0)
    step = timedelta(minutes=-15)
    with pytest.raises(ValueError, match="'step' must be positive when 'start' is before 'stop'."):
        _ = list(t_range(start, stop, step=step))

def test_step_direction_mismatch_negative():
    # start > stop but step is positive
    start = datetime(2024, 1, 1, 1, 0, 0)
    stop = datetime(2024, 1, 1, 0, 0, 0)
    step = timedelta(minutes=15)
    with pytest.raises(ValueError, match="'step' must be negative when 'start' is after 'stop'."):
        _ = list(t_range(start, stop, step=step))

def test_n_steps_with_zero_delta():
    # start == stop, n_steps provided
    start = datetime(2024, 1, 1, 0, 0, 0)
    stop = datetime(2024, 1, 1, 0, 0, 0)
    n_steps = 4
    with pytest.raises(ValueError, match="No range can be generated with 'start' equal to 'stop'."):
        _ = list(t_range(start, stop, n_steps=n_steps))

def test_n_steps_calculation_positive():
    # Ensure step is correctly calculated with n_steps
    start = datetime(2024, 1, 1, 0, 0, 0)
    stop = datetime(2024, 1, 1, 1, 0, 0)
    n_steps = 4
    step = timedelta(seconds=(stop - start).total_seconds() / n_steps)
    expected = [
        start + step * i for i in range(n_steps)
    ]
    result = collect(t_range(start, stop, n_steps=n_steps))
    assert result == expected

def test_n_steps_calculation_negative():
    # Ensure step is correctly calculated with n_steps for negative range
    start = datetime(2024, 1, 1, 1, 0, 0)
    stop = datetime(2024, 1, 1, 0, 0, 0)
    n_steps = 4
    step = timedelta(seconds=(stop - start).total_seconds() / n_steps)
    expected = [
        start + step * i for i in range(n_steps)
    ]
    result = collect(t_range(start, stop, n_steps=n_steps))
    assert result == expected

def test_step_precision():
    # Test with steps that result in floating point seconds
    start = datetime(2024, 1, 1, 0, 0, 0)
    stop = datetime(2024, 1, 1, 0, 0, 1)  # 1 second
    n_steps = 3
    expected = [
        datetime(2024, 1, 1, 0, 0, 0),
        datetime(2024, 1, 1, 0, 0, 0, 333333),
        datetime(2024, 1, 1, 0, 0, 0, 666666),
    ]
    result = collect(t_range(start, stop, n_steps=n_steps))
    # Comparing microseconds with some tolerance
    for res, exp in zip(result, expected):
        assert res == exp

def test_large_range():
    # Test with a large range to ensure performance and correctness
    start = datetime(2024, 1, 1, 0, 0, 0)
    stop = datetime(2024, 1, 2, 0, 0, 0)  # 1 day
    step = timedelta(hours=6)
    expected = [
        datetime(2024, 1, 1, 0, 0, 0),
        datetime(2024, 1, 1, 6, 0, 0),
        datetime(2024, 1, 1, 12, 0, 0),
        datetime(2024, 1, 1, 18, 0, 0),
    ]
    result = collect(t_range(start, stop, step=step))
    assert result == expected

def test_generator_behavior():
    # Ensure t_range returns a generator
    start = datetime(2024, 1, 1, 0, 0, 0)
    stop = datetime(2024, 1, 1, 1, 0, 0)
    step = timedelta(minutes=15)
    gen = t_range(start, stop, step=step)
    assert hasattr(gen, '__iter__') and hasattr(gen, '__next__')

def test_step_not_multiple_of_delta():
    # Ensure that if step does not exactly divide the delta, the last step is excluded
    start = datetime(2024, 1, 1, 0, 0, 0)
    stop = datetime(2024, 1, 1, 1, 0, 0)
    step = timedelta(minutes=17)
    expected = [
        datetime(2024, 1, 1, 0, 0, 0),
        datetime(2024, 1, 1, 0, 17, 0),
        datetime(2024, 1, 1, 0, 34, 0),
        datetime(2024, 1, 1, 0, 51, 0),
    ]
    result = collect(t_range(start, stop, step=step))
    assert result == expected

def test_n_steps_one():
    # Test with n_steps=1, should yield only the start
    start = datetime(2024, 1, 1, 0, 0, 0)
    stop = datetime(2024, 1, 1, 1, 0, 0)
    n_steps = 1
    expected = [start]
    result = collect(t_range(start, stop, n_steps=n_steps))
    assert result == expected

def test_n_steps_large_number():
    # Test with a large number of steps
    start = datetime(2024, 1, 1, 0, 0, 0)
    stop = datetime(2024, 1, 1, 0, 1, 0)  # 1 minute
    n_steps = 60
    result = collect(t_range(start, stop, n_steps=n_steps))
    expected = [start + timedelta(seconds=i) for i in range(n_steps)]
    assert result == expected

def test_step_non_divisible_delta():
    # Test with step that does not evenly divide the total delta
    start = datetime(2024, 1, 1, 0, 0, 0)
    stop = datetime(2024, 1, 1, 0, 1, 0)  # 1 minute
    step = timedelta(seconds=7)
    expected = [
        datetime(2024, 1, 1, 0, 0, 0),
        datetime(2024, 1, 1, 0, 0, 7),
        datetime(2024, 1, 1, 0, 0, 14),
        datetime(2024, 1, 1, 0, 0, 21),
        datetime(2024, 1, 1, 0, 0, 28),
        datetime(2024, 1, 1, 0, 0, 35),
        datetime(2024, 1, 1, 0, 0, 42),
        datetime(2024, 1, 1, 0, 0, 49),
        datetime(2024, 1, 1, 0, 0, 56),
    ]
    result = collect(t_range(start, stop, step=step))
    assert result == expected

def test_n_steps_exact_division():
    # Test with n_steps that exactly divides the total delta
    start = datetime(2024, 1, 1, 0, 0, 0)
    stop = datetime(2024, 1, 1, 0, 2, 0)  # 2 minutes
    n_steps = 4
    expected = [
        datetime(2024, 1, 1, 0, 0, 0),
        datetime(2024, 1, 1, 0, 0, 30),
        datetime(2024, 1, 1, 0, 1, 0),
        datetime(2024, 1, 1, 0, 1, 30),
    ]
    result = collect(t_range(start, stop, n_steps=n_steps))
    assert result == expected

def test_n_steps_non_exact_division():
    # Test with n_steps that do not exactly divide the total delta
    start = datetime(2024, 1, 1, 0, 0, 0)
    stop = datetime(2024, 1, 1, 0, 1, 0)  # 1 minute
    n_steps = 3
    expected = [
        datetime(2024, 1, 1, 0, 0, 0),
        datetime(2024, 1, 1, 0, 0, 20),
        datetime(2024, 1, 1, 0, 0, 40),
    ]
    result = collect(t_range(start, stop, n_steps=n_steps))
    assert result == expected

def test_step_microseconds():
    # Test steps with microseconds
    start = datetime(2024, 1, 1, 0, 0, 0, 0)
    stop = datetime(2024, 1, 1, 0, 0, 1, 0)  # 1 second
    step = timedelta(microseconds=300000)  # 0.3 seconds
    expected = [
        datetime(2024, 1, 1, 0, 0, 0, 0),
        datetime(2024, 1, 1, 0, 0, 0, 300000),
        datetime(2024, 1, 1, 0, 0, 0, 600000),
        datetime(2024, 1, 1, 0, 0, 0, 900000),
    ]
    result = collect(t_range(start, stop, step=step))
    assert result == expected

def test_n_steps_with_microseconds():
    # Test n_steps that result in microsecond steps
    start = datetime(2024, 1, 1, 0, 0, 0, 0)
    stop = datetime(2024, 1, 1, 0, 0, 1, 0)  # 1 second
    n_steps = 4
    expected = [
        datetime(2024, 1, 1, 0, 0, 0, 0),
        datetime(2024, 1, 1, 0, 0, 0, 250000),
        datetime(2024, 1, 1, 0, 0, 0, 500000),
        datetime(2024, 1, 1, 0, 0, 0, 750000),
    ]
    result = collect(t_range(start, stop, n_steps=n_steps))
    for res, exp in zip(result, expected):
        assert res == exp

def test_partial_final_step():
    # Ensure that if the final step exceeds stop, it is not included
    start = datetime(2024, 1, 1, 0, 0, 0)
    stop = datetime(2024, 1, 1, 0, 0, 10)
    step = timedelta(seconds=3)
    expected = [
        datetime(2024, 1, 1, 0, 0, 0),
        datetime(2024, 1, 1, 0, 0, 3),
        datetime(2024, 1, 1, 0, 0, 6),
        datetime(2024, 1, 1, 0, 0, 9),
    ]
    result = collect(t_range(start, stop, step=step))
    assert result == expected

def test_generator_exhaustion():
    # Ensure that once the generator is exhausted, it doesn't yield any more items
    start = datetime(2024, 1, 1, 0, 0, 0)
    stop = datetime(2024, 1, 1, 0, 0, 30)
    step = timedelta(seconds=10)
    gen = t_range(start, stop, step=step)
    expected = [
        datetime(2024, 1, 1, 0, 0, 0),
        datetime(2024, 1, 1, 0, 0, 10),
        datetime(2024, 1, 1, 0, 0, 20),
    ]

    # Consume generator
    result: list[datetime] = []
    for dt in gen:
        result.append(dt)
    
    # Check first batch
    assert result == expected
    
    # Try to get next item, should raise StopIteration
    with pytest.raises(StopIteration):
        _ = next(gen)

def test_n_steps_with_float_steps():
    # Testing step calculation when n_steps result in fractional seconds
    start = datetime(2024, 1, 1, 0, 0, 0)
    stop = datetime(2024, 1, 1, 0, 0, 1)  # 1 second
    n_steps = 3
    expected = [
        datetime(2024, 1, 1, 0, 0, 0),
        datetime(2024, 1, 1, 0, 0, 0, 333333),
        datetime(2024, 1, 1, 0, 0, 0, 666666),
    ]
    result = collect(t_range(start, stop, n_steps=n_steps))
    for res, exp in zip(result, expected):
        assert res == exp