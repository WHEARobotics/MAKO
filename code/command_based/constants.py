"""
Module of frozen classes that are used as constants by different parts of the
code.  
"""
from dataclasses import dataclass
from wpimath.geometry import Pose2d, Translation2d, Rotation2d

# Positions used in commands
@dataclass(frozen=True)
class Positions:
    """Poses to be used in commands"""
    HOME = Pose2d() # 0, 0, facing forward
    AWAY = Pose2d(
        Translation2d(2.0, 0.0),  # 2.0 meters straight forward from home
        Rotation2d() # Facing forward
    )
    SIDE = Pose2d(
        Translation2d(2.0, 1.0),  # 2.0 meters forward, 1.0 meter to the left of home
        Rotation2d() # Facing forward
    )

# User Interface (UI) and control
@dataclass(frozen=True) # Tells Python that this class's variables can't be changed.
class UserInterface:
    """Constants related to human interaction."""
    DRIVE_SLOWER = 4 # Factor to divide the drive commands to slow things down for safety.
    XBOX_PORT = 2    # USB port number for the Xbox controller on Rod's computer.


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
    PIDX_KP = 1       # X dimension PID controller's proportional constant
    PIDY_KP = 1       # Y dimension PID controller's proportional constant
    PID_ROT_KP = 1    # Rotation controller's proportional constant.
    # Horizontal (x or y) maxima and tolerances
    HORIZ_MAX_V = 1   # Maximum velocity in meters/second
    HORIZ_MAX_A = 2  # Maximum acceleration in meters/second/second
    HORIZ_POS_TOL = 0.1 # Position tolerance in meters (within this distance is "close enough")
    HORIZ_VEL_TOL = 0.01 # Velocity tolerance in meters/second
    # Rotational maxima and tolerances
    # TODO: Confirm these are radians, radians/sec, radians/sec^2?
    ROT_MAX_V = 0.1   # Rotational maximum velocity
    ROT_MAX_A = 0.1   # Rotational maximum acceleration
    ROT_POS_TOL = 0.1 # Rotational position tolerance
    ROT_VEL_TOL = 0.1 # Rotational velocity tolerance
