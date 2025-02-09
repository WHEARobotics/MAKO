import commands2
import commands2.button
from wpilib import SendableChooser,SmartDashboard
from wpilib.shuffleboard import Shuffleboard, BuiltInWidgets

from constants.operatorinterfaceconstants import UserInterface
from constants.fieldconstants import Positions
from constants.elevatorconstants import ElevatorConsts
from commands.autos import Autos
from commands.drivecommands import DriveCommands
from commands.elevatorcommands import ElevatorCommands
from constants.autoconstants import AutoConsts
import subsystems.drivesubsystem
import subsystems.elevatorsubsystem

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
        self.elevator = subsystems.elevatorsubsystem.ElevatorSubsystem()

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
                    -self.xbox.getLeftY() / UserInterface.DRIVE_SLOWER, # Pushing joystick forward produces a negative number.
                    -self.xbox.getLeftX() / UserInterface.DRIVE_SLOWER, # Pushing joystick left produces a negative number.
                    -self.xbox.getRightX() / UserInterface.DRIVE_SLOWER   # Pushing jouystick left produces a negative number, but we want + for CCW/turn left.
                ),
                # The subsystem required by the command.
                self.drive,
            )
        )

        # Default for the elevator is to move to the last goal that had been set,
        # basically, holding it in place.
        self.elevator.setDefaultCommand(
            commands2.RunCommand(
                self.elevator.move_to_goal,
                self.elevator,
            )
        )

        
        #Make a tab in shuffle board
        self.tab = Shuffleboard.getTab("Test")

        #Auto chooser
        self.auto_chooser = SendableChooser()

        self.auto_chooser.setDefaultOption("Side Step", AutoConsts.SIDE_STEP)  #Autos.side_step(self.drive)
        
        #Add options
        self.auto_chooser.addOption("Drive Forward", AutoConsts.FORWARD) # Autos.forward(self.drive)

        self.auto_chooser.addOption("Drive Forward + elevator mid", AutoConsts.FORWARD_ELEVATOR) # Autos.forward_elevator(self.drive, self.elevator)

        #Add chooser to tab
        SmartDashboard.putData("Auto Commmand Selector", self.auto_chooser)

    def configureButtonBindings(self):
        """
        Helper method to associate commands with controller buttons.
        """
        self.xbox.a().onTrue(DriveCommands.drive_goal(Positions.HOME, self.drive))
        self.xbox.b().onTrue(DriveCommands.drive_goal(Positions.FACE_NW, self.drive))
        self.xbox.leftBumper().onTrue(ElevatorCommands.move_goal(ElevatorConsts.HOME, self.elevator))
        self.xbox.rightBumper().onTrue(ElevatorCommands.move_goal(ElevatorConsts.MID, self.elevator))


    def getAutonomousCommand(self) -> commands2.Command:
        """
        Helper method to select which autonomous routine to run this time.
        :returns: the chosen autonomous command.
        """
        auto_reader = self.auto_chooser.getSelected()
        
        if auto_reader == AutoConsts.SIDE_STEP:
            return Autos.side_step(self.drive)
        elif auto_reader == AutoConsts.FORWARD:
            return Autos.forward(self.drive)
        elif auto_reader == AutoConsts.FORWARD_ELEVATOR:
            return Autos.forward_elevator(self.drive, self.elevator)
        
