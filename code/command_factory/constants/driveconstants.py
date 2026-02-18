"""
Module of constants related to the drivetrain
Units are inches, seconds, and degrees unless otherwise noted.
"""
from dataclasses import dataclass
import math

@dataclass(frozen=True)
class DriveConsts:
    """ Drivetrain related constants"""
    # Neo CAN bus IDs
    CAN_FL: int = 4 # Front left motor
    CAN_FR: int = 3 # Front right
    CAN_BL: int = 2 # Back left
    CAN_BR: int = 1 # Back right

    # Drivetrain geometry, gearing, etc.
    TRACK_HALF_WIDTH: float = 0.18 / 0.0254       # inches (0.36 m track width)
    WHEELBASE_HALF_LENGTH: float = 0.225 / 0.0254 # inches (0.45 m wheelbase)
    GEAR_RATIO: float = 12.75                     # Toughbox micro gearbox ratio
    WHEEL_DIA: float = 4.0                        # 4" diameter

    # Precompute the factor to convert motor revolutions to wheel rim 
    # distance traveled in inches.  The factor 1.414 = sqrt(2) is to
    # correct for the difference between MAKO's omni wheels and a true
    # mecanum wheel-based drive.
    # REV_TO_IN = sqrt(2) * (wheel circumference) / (gear ratio)
    REV_TO_IN = 1.414 * math.pi * WHEEL_DIA / GEAR_RATIO

    # Precompute the factor to convert motor RPM to wheel rim speed in meters/second.
    # RPM_TO_INCHES_S = sqrt(2) * (wheel circumference) / (gear ratio) / (60 seconds/minute)
    RPM_TO_INCHES_S = 1.414 * math.pi * WHEEL_DIA / GEAR_RATIO / 60

    # PID controller constants (gains)
    # Proportional constant only at the moment, all others assumed zero.
    # For X and Y, 1 meter error results in a motor command of 1.0 (full voltage).
    # Converted to 1/0.0254 = 39 inches => full voltage.
    # For rotation, 90 degrees error => full voltage.
    PIDX_KP: float = 1.0 * 0.0254  # X dimension PID controller's proportional constant
    PIDY_KP: float = 1.0 * 0.0254  # Y dimension PID controller's proportional constant
    PID_ROT_KP: float = 1.0/90.0   # Rotation controller's proportional constant.

    # Horizontal (x or y) maxima and tolerances
    HORIZ_MAX_V: float = 39.0  # Maximum velocity in inches/second
    HORIZ_MAX_A: float = 78.0  # Maximum acceleration in inches/second/second
    HORIZ_POS_TOL: float = 4.0 # Position tolerance in inches (within this distance is "close enough")
    HORIZ_VEL_TOL: float = 0.4 # Velocity tolerance in inches/second

    # Rotational maxima and tolerances
    ROT_MAX_V: float = 40.0  # Rotational maximum velocity in degrees/second
    ROT_MAX_A: float = 20.0  # Rotational maximum acceleration in degrees/second/second
    ROT_POS_TOL: float = 5.0 # Rotational position tolerance in degrees
    ROT_VEL_TOL: float = 1.0 # Rotational velocity tolerance in degrees/second
