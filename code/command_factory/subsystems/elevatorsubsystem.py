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
        self.motor.configure(config, rev.ResetMode.kResetSafeParameters, rev.PersistMode.kPersistParameters)

        # A controller is how we adjust positions.
        self.controller = self.motor.getClosedLoopController()

        self.encoder = self.motor.getEncoder()

        self.bottom_limit = self.motor.getReverseLimitSwitch()

        # Give an initial position in rotations we are trying to get to.
        self.goal_pos = _inches_to_motor_rot(ElevatorConsts.HOME)

        # Make sure we initialize the encoder properly.
        self.initialized: bool = False
        if self.bottom_limit.get():
            self.encoder.setPosition(_inches_to_motor_rot(ElevatorConsts.HOME))
            self.initialized = True

        # This is a trigger that can be used externally.
        self.is_at_height = commands2.button.Trigger(self._is_at_position).debounce(0.5) # Debounce to make sure we are really there, not just passing through.


    ###########################################################################
    # Methods in base classes that we override here                           #
    ###########################################################################

    def periodic(self):
        """
        This method runs once every 20 msec in all modes (including simulation).  
        """
        # Send data to the dashboard
        # TODO: implement shuffleboard
        height = _motor_rot_to_inches(self.encoder.getPosition())
        wpilib.SmartDashboard.putString('DB/String 4', 'elev: {:5.2f}"'.format(height))

    def simulationPeriodic(self):
        """Called in simulation after periodic() to update simulation variables."""
        pass

    ###########################################################################
    # Methods that create commands                                            #
    ###########################################################################

    def set_home(self) -> commands2.Command:
        """Return a command that sets the current position as the home position."""
        return commands2.cmd.run(lambda: self._move_to_position(ElevatorConsts.HOME), self)
    
    def set_mid(self) -> commands2.Command:
        """Return a command that sets the current position as the mid position."""
        return commands2.cmd.run(lambda: self._move_to_position(ElevatorConsts.MID), self)
    
    # Note: an alternate way to do this would be to have a single method that takes the height as an argument, 
    # and then have the command factory methods call it with the appropriate height, as below.
    # This makes the command factory methods more concise, but there is more overall code.

    # def set_home(self) -> commands2.Command:
    #     """Return a command that sets the current position as the home position."""
    #     return self._set_position(ElevatorConsts.HOME)
    
    # def _set_position(self, height: float) -> commands2.Command:
    #     """Return a command that moves the elevator to a given height."""
    #     return commands2.cmd.run(lambda: self._move_to_position(height), self)

    ###########################################################################
    # Methods to use in commands, either created in this class or elsewhere   #
    ###########################################################################

    def _move_to_position(self, height: float):
        """Set the goal to a height and move toward it."""
        # Convert because internally, we use rotations.
        # Also caches the goal position for use in _is_at_position().
        self.goal_pos = _inches_to_motor_rot(height)

        if self.initialized:
            self.controller.setReference(self.goal_pos, rev.SparkMax.ControlType.kPosition)
        else:
            # If not initialized, move downward slowly to find the bottom.
            self.motor.set(-0.1)
            if self.bottom_limit.get():
                self.motor.set(0.0)
                self.encoder.setPosition(_inches_to_motor_rot(ElevatorConsts.HOME))
                self.initialized = True

    def _is_at_position(self) -> bool:
        """Return true if the elevator is at the desired position."""
        return abs(self.encoder.getPosition() - self.goal_pos) < ElevatorConsts.ROT_TOLERANCE


    ###########################################################################
    # Helper methods                                                          #
    ###########################################################################

#==============================================================================
# Simple helper functions that don't need to be in the class.
#==============================================================================
def _motor_rot_to_inches(rot: float) -> float:
    """Convert motor shaft rotations to height in inches."""
    return rot * ElevatorConsts.SPROCKET_CIRC * ElevatorConsts.RIG / ElevatorConsts.GEAR_RATIO + ElevatorConsts.HEIGHT_OFFSET

def _inches_to_motor_rot(height: float) -> float:
    """Convert height to motor shaft position in rotations."""
    return (height - ElevatorConsts.HEIGHT_OFFSET) * ElevatorConsts.GEAR_RATIO / ElevatorConsts.SPROCKET_CIRC / ElevatorConsts.RIG
