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
    HEIGHT_OFFSET: float = 10.5 # Height of the second stage's lower crosspiece (top surface), in inches.
    
    # Heights in inches
    HOME: float = 0.0
    MID: float = 12.0
