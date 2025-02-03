"""
Class to interact with MAKO's elevator as a command-
based Subsystem.  The class's method definitions are organized groups in the
following order:

* __init()__: The standard object initialization method.
* Methods of Subsystem class that we are overriding
* Command factory methods: methods that return Commands that only use the
      drive system.
* Methods that can be used in commands, either by the factories, or by other
     classes (for instance in the "commands" folder).
* Helper methods used by the above: measuring speed, distance, etc.
"""

# Import standard Python modules.
import math

# Import WPILib and other robotics modules.
import commands2
import rev
import wpilib
import wpilib.drive
import wpimath.geometry
import wpimath.kinematics
from wpimath.controller import ProfiledPIDController
from wpimath.trajectory import TrapezoidProfile

# Import our modules.
from constants.elevatorconstants import ElevatorConsts

#==============================================================================
# The drive subsystem class
#==============================================================================

class ElevatorSubsystem(commands2.Subsystem):
    def __init__(self) -> None:
        super().__init__() # Call the Subsystem class's (the "super" part) init.

        # ---------------------------------------------------------------------
        # Set up motors, their encoders, and the drivetrain.
        # ---------------------------------------------------------------------

        # Create the motor
        self.motor = rev.SparkMax(ElevatorConsts.CAN_ID, rev.SparkMax.MotorType.kBrushless)

        # Get a configuration object.
        config = rev.SparkMaxConfig()
        # Basic parts of the configuration.
        config.inverted(False)
        config.IdleMode(rev.SparkMax.IdleMode.kBrake)
        # Feedback loop.
        config.closedLoop.pid(ElevatorConsts.K_P, 0.0, 0.0)


        # Apply it to the motor.
        self.motor.configure(config, rev.SparkMax.ResetMode.kResetSafeParameters, rev.SparkMax.PersistMode.kPersistParameters)

        # A controller is how we adjust positions.
        self.controller = self.motor.getClosedLoopController()

        self.encoder = self.motor.getEncoder()
        self.encoder.setPosition(0)

        # Set the state tracking.
        # TODO: Improve the initialization.
        # Position in rotations we are trying to get to.
        self.goal_pos = _inches_to_motor_rot(ElevatorConsts.HOME)
        self.initialized: bool = True

    ###########################################################################
    # Methods in base classes that we override here                           #
    ###########################################################################

    def periodic(self):
        """
        This method runs once every 20 msec in all modes (including simulation).  
        """
        # Send data to the dashboard
        # TODO: implement shuffleboard
        wpilib.SmartDashboard.putString('DB/String 4', 'elev: {:5.2f}'.format(self.encoder.getPosition()))

    def simulationPeriodic(self):
        """Called in simulation after periodic() to update simulation variables."""
        pass

    ###########################################################################
    # Methods that create commands                                            #
    ###########################################################################

    ###########################################################################
    # Methods to use in commands, either created in this class or elsewhere   #
    ###########################################################################

    def set_goal_height_inches(self, height: float):
        """Set the goal in inches that the elevator drives toward"""
        # Convert because internally, we use rotations.
        self.goal_pos = _inches_to_motor_rot(height)

    def move_to_goal(self):
        """Move toward the goal position"""
        # self.motor.set(rev.SparkMax.ControlType.kPosition, self.goal_pos)
        self.controller.setReference(self.goal_pos, rev.SparkMax.ControlType.kPosition)

    def is_at_goal(self) -> bool:
        False # Never end unless interrupted.

    ###########################################################################
    # Helper methods                                                          #
    ###########################################################################

#==============================================================================
# Simple helper functions that don't need to be in the class.
#==============================================================================
def _motor_rot_to_inches(rot: float) -> float:
    """Convert motor shaft rotations to height in inches."""
    return rot * ElevatorConsts.SPROCKET_CIRC / ElevatorConsts.GEAR_RATIO

def _inches_to_motor_rot(height: float) -> float:
    """Convert height to motor shaft position in rotations."""
    return height * ElevatorConsts.GEAR_RATIO / ElevatorConsts.SPROCKET_CIRC
