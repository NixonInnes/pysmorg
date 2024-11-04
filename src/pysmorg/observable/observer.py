from enum import Enum
from typing import Any, Callable


ObserverNoValueType = Callable[[], None]
ObserverNewValueType = Callable[[Any], None]
ObserverNewOldValueType = Callable[[Any, Any], None]
ObserverType = ObserverNoValueType | ObserverNewValueType | ObserverNewOldValueType

class ObserverSignatureType(Enum):
    NoValue = 0
    NewValue = 1
    NewOldValue = 2