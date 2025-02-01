"""
Module of constants related to the drivetrain  
"""
from dataclasses import dataclass

@dataclass(frozen=True)
class DriveConsts:
    """ Drivetrain related constants"""
    # Neo CAN bus IDs
    CAN_FL: int = 4 # Front left motor
    CAN_FR: int = 3 # Front right
    CAN_BL: int = 2 # Back left
    CAN_BR: int = 1 # Back right

    # Drivetrain geometry, gearing, etc.
    TRACK_HALF_WIDTH: float = 0.18       # meters (36 cm track width)
    WHEELBASE_HALF_LENGTH: float = 0.225 # meters (45 cm wheelbase)
    GEAR_RATIO: float = 12.75      # Toughbox micro gearbox ratio
    WHEEL_DIA: float = 4.0 * 0.0254  # 4" diameter in meters

    # PID controller constants (gains)
    # Proportional constant only at the moment, all others assumed zero.
    PIDX_KP: float = 1.0       # X dimension PID controller's proportional constant
    PIDY_KP: float = 1.0       # Y dimension PID controller's proportional constant
    PID_ROT_KP: float = 2.0/180.0 # Rotation controller's proportional constant.

    # Horizontal (x or y) maxima and tolerances
    HORIZ_MAX_V: float = 1.0    # Maximum velocity in meters/second
    HORIZ_MAX_A: float = 2.0    # Maximum acceleration in meters/second/second
    HORIZ_POS_TOL: float = 0.1  # Position tolerance in meters (within this distance is "close enough")
    HORIZ_VEL_TOL: float = 0.01 # Velocity tolerance in meters/second

    # Rotational maxima and tolerances
    # Degrees, degrees/second, and degrees/sec^2
    ROT_MAX_V: float = 40.0   # Rotational maximum velocity
    ROT_MAX_A: float = 20.0   # Rotational maximum acceleration
    ROT_POS_TOL: float = 5.0 # Rotational position tolerance
    ROT_VEL_TOL: float = 1.0 # Rotational velocity tolerance
