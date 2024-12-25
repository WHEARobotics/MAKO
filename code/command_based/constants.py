"""
Module of frozen classes that are used as constants by different parts of the
code.  
"""
from dataclasses import dataclass

# User Interface (UI) and control
@dataclass(frozen=True) # Tells Python that this class's variables can't be changed.
class UserInterface:
    """Constants related to human interaction."""
    DRIVE_SLOWER = 4 # Factor to divide the drive commands to slow things down for safety.


@dataclass(frozen=True)
class DriveConsts:
    """ Drivetrain related constants"""
    # Neo CAN bus IDs
    CAN_FL = 4 # Front left motor
    CAN_FR = 3 # Front right
    CAN_BL = 2 # Back left
    CAN_BR = 1 # Back right

    # Drivetrain geometry, gearing, etc.
    TRACK_HALF_WIDTH = 0.18       # meters (36 cm track width)
    WHEELBASE_HALF_LENGTH = 0.225 # meters (45 cm wheelbase)
    GEAR_RATIO = 12.75      # Toughbox micro
    WHEEL_DIA = 4 * 0.0254  # 4" diameter in meters

    # PID controller constants (gains)
    # Proportional constant only at the moment, all others assumed zero.
    PIDX_KP = 1    # X dimension PID controller's proportional constant
    PIDY_KP = 1    # Y dimension PID controller's proportional constant
    PID_ROT_KP = 1 # Rotation controller's proportional constant.
