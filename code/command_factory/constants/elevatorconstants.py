"""
Module of constants related to the elevator
Units are inches, seconds, and degrees unless otherwise noted.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class ElevatorConsts:
    """ Elevator related constants"""
    # SparkMax CAN bus ID
    CAN_ID: int = 5 # Motor to raise/lower the elevator
    # Closed loop proportional constant
    K_P: float = 0.01

    # Mechanical constants
    GEAR_RATIO: float = 27
    SPROCKET_CIRC: float = 42 * 5 / 25.4 # Inches (42 teeth * 5 mm pitch/tooth / 25.4 mm/in)
    RIG: float =            2.0 # Rigging design causes the second stage to move at 2x the rate of first stage.
    HEIGHT_OFFSET: float = 10.5 # Height of the second stage's lower crosspiece (top surface), in inches.
    
    # Heights in inches (lowest is 10.5, highest is ~55.5)
    HOME: float = 10.5 # Elevator at its lowest position.
    MID: float  = 34.5

    ROT_TOLERANCE: float= 0.25 # 0.25 rotations is about 0.5 inches, which is good enough for our purposes.
