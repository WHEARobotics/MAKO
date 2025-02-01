import commands2
import commands2.button

from constants.operatorinterfaceconstants import UserInterface
from constants.fieldconstants import Positions
from commands.autos import Autos
from commands.drivecommands import DriveCommands
import subsystems.drivesubsystem

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
        self.xbox = commands2.button.CommandXboxController(UserInterface.XBOX_PORT)

        # Configure button bindings.
        self.configureButtonBindings()

        # Configure default commands.
        # Set the drive system to use the xbox controller when no other drive
        # command is scheduled.
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
        """
        Helper method to associate commands with controller buttons.
        """
        self.xbox.a().onTrue(DriveCommands.drive_goal(Positions.HOME, self.drive))
        self.xbox.b().onTrue(DriveCommands.drive_goal(Positions.FACE_NW, self.drive))


    def getAutonomousCommand(self) -> commands2.Command:
        """
        Helper method to select which autonomous routine to run this time.
        :returns: the chosen autonomous command.
        """
        return Autos.side_step(self.drive)
