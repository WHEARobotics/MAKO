import commands2
import commands2.button
from wpilib import SendableChooser,SmartDashboard
from wpilib.shuffleboard import Shuffleboard, BuiltInWidgets

from constants.operatorinterfaceconstants import UserInterface
from constants.fieldconstants import Positions
from commands.autos import Autos
from commands.drivecommands import DriveCommands
from constants.autoconstants import AutoConsts
import subsystems.drivesubsystem
import subsystems.elevatorsubsystem

class RobotContainer:
    # TODO: subclass sendable and override initSendable.
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

        # Configure button bindings and trigger bindings.
        self.configureButtonBindings()
        self.configureTriggerBindings()

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

        # Default for the elevator is to go home. This will only run at the beginning,
        # as button-triggered commands do not exit.
        self.elevator.setDefaultCommand(
            self.elevator.set_home()
        )
        
        #Make a tab in shuffle board
        # TODO: replace deprecated shuffleboard.
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
        self.xbox.leftBumper().onTrue(self.elevator.set_home().alongWith(commands2.cmd.runOnce(lambda: print("Going home!"))))
        self.xbox.rightBumper().onTrue(self.elevator.set_mid().alongWith(commands2.cmd.runOnce(lambda: print("Going mid!"))))

    def configureTriggerBindings(self):
        """
        Helper method to associate commands with triggers. Triggers are like buttons, but can be based on any boolean condition, not just joystick buttons.
        """
        # Example trigger: when the elevator is at the goal position, print "At goal!" to the console.
        # The trigger is continuously evaluated, but only prints once each time it becomes true.
        self.elevator.is_at_height.onTrue(commands2.cmd.runOnce(lambda: print("At goal!")))

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
        
