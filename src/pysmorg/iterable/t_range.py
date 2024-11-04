from collections.abc import Generator
from datetime import datetime, timedelta


def t_range(
    start: datetime,
    stop: datetime,
    step: timedelta | None = None,
    n_steps: int | None = None
) -> Generator[datetime, None, None]:
    """
    A datetime generator that works like `range()` for datetime objects.

    Args:
        start (datetime): The starting datetime.
        stop (datetime): The stopping datetime.
        step (timedelta, optional): The step size between datetimes.
            Either `step` or `n_steps` must be specified, but not both.
        n_steps (int, optional): The number of steps.
            Either `step` or `n_steps` must be specified, but not both.

    Yields:
        datetime: The next datetime in the range.

    Raises:
        ValueError: If neither `step` nor `n_steps` is provided,
                    or if both are provided,
                    or if `n_steps` is not positive,
                    or if `step` is zero,
                    or if `step` direction does not align with `start` and `stop`.
    """
    if (step is None and n_steps is None) or (step is not None and n_steps is not None):
        raise ValueError(
            "t_range() requires either 'step' OR 'n_steps' to be specified, but not both."
        )

    if step is None:
        # n_steps must be provided
        assert n_steps is not None  # For type checker
        
        if n_steps <= 0:
            raise ValueError("'n_steps' must be a positive integer.")

        delta = stop - start
        total_seconds = delta.total_seconds()

        if total_seconds == 0:
            raise ValueError("No range can be generated with 'start' equal to 'stop'.")

        # Determine the direction based on start and stop
        step_direction = 1 if total_seconds > 0 else -1

        # Use absolute total_seconds for step calculation
        step = timedelta(seconds=abs(total_seconds) / n_steps) * step_direction

    else:
        # step is provided
        step_seconds = step.total_seconds()
        if step_seconds == 0:
            raise ValueError("'step' must not be zero.")

        if stop > start and step_seconds <= 0:
            raise ValueError("'step' must be positive when 'start' is before 'stop'.")
        if stop < start and step_seconds >= 0:
            raise ValueError("'step' must be negative when 'start' is after 'stop'.")

    current = start
    if step.total_seconds() > 0:
        while current < stop:
            yield current
            current += step
    else:
        while current > stop:
            yield current
            current += step
