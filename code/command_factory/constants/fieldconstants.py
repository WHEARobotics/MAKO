"""
Module of constants of locations on the field.
Units are inches, seconds, and degrees unless otherwise noted.
"""
from dataclasses import dataclass
from wpimath.geometry import Pose2d, Translation2d, Rotation2d

# Positions used in commands
@dataclass(frozen=True)
class Positions:
    """Poses to be used in commands"""
    HOME = Pose2d() # 0, 0, facing forward
    AWAY = Pose2d(
        Translation2d(78.0, 0.0),  # 78 inches or 2.0 meters straight forward from home
        Rotation2d() # Facing forward
    )
    SIDE = Pose2d(
        Translation2d(78.0, 39.0),  # 78 inches = 2.0 meters forward, 39 inches = 1.0 meter to the left of home
        Rotation2d() # Facing forward
    )
    FACE_NW = Pose2d(
        Translation2d(0.0, 0.0),  # 0.0 meters forward, 0.0 meter to the left of home
        Rotation2d().fromDegrees(45) # Facing forward
    )
