import commands2
import wpilib

import subsystems.drivesubsystem
from constants import UserInterface

class RobotContainer:
    """
    This class is where the bulk of the robot should be declared. Since Command-based is a
    "declarative" paradigm, very little robot logic should actually be handled in the :class:`.Robot`
    periodic methods (other than the scheduler calls). Instead, the structure of the robot (including
    subsystems, commands, and button mappings) should be declared here.
    """

    def __init__(self) -> None:
        """The container for the robot.  Contains subsystems, I/O devices, and commands."""
        # Robot's subsystems
        self.drive = subsystems.drivesubsystem.DriveSubsystem()

        # Driver controller(s)
        self.xbox = wpilib.XboxController(2)

        # Configure button bindings.
        self.configureButtonBindings()

        # Configure default commands.
        # Set the drive to use the xbox controller by default.
        self.drive.setDefaultCommand(
            commands2.RunCommand(
                lambda: self.drive.drive_field_relative(
                    -self.xbox.getRightY() / UserInterface.DRIVE_SLOWER, # Pushing joystick forward produces a negative number.
                    -self.xbox.getRightX() / UserInterface.DRIVE_SLOWER, # Pushing joystick left produces a negative number.
                    -self.xbox.getLeftX() / UserInterface.DRIVE_SLOWER   # Pushing jouystick left produces a negative number, but we want + for CCW/turn left.
                ),
                # The subsystem required by the command.
                self.drive,
            )
        )

    def configureButtonBindings(self):
        pass

    def getAutonomousCommand(self) -> commands2.Command:
        return None
