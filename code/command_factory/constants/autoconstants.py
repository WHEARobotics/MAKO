from dataclasses import dataclass

@dataclass(frozen=True)
class AutoConsts: 
    SIDE_STEP = 1
    FORWARD = 2
    FORWARD_ELEVATOR = 3
