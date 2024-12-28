"""
Class to interact with MAKO's omni-wheel holonomic drive system as a command-
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
from constants import UserInterface, DriveConsts

#==============================================================================
# The drive subsystem class
#==============================================================================

class DriveSubsystem(commands2.Subsystem):
    def __init__(self) -> None:
        super().__init__() # Call the Subsystem class's (the "super" part) init.

        # ---------------------------------------------------------------------
        # The gyro is part of the drive system, since it helps keep the drive
        # moving the way we want.  Reset the gyro at boot in case the gyro has 
        # been powered for a while, because it drifts.
        # ---------------------------------------------------------------------
        self.gyro = wpilib.ADXRS450_Gyro()
        self.gyro.reset()

        # ---------------------------------------------------------------------
        # Set up motors, their encoders, and the drivetrain.
        # ---------------------------------------------------------------------

        # Create and configure the drive train controllers and motors, all 
        # REV Robotics SparkMaxes driving NEO motors.
        self.drive_fl = rev.CANSparkMax(DriveConsts.CAN_FL, rev.CANSparkMax.MotorType.kBrushless)
        self.drive_fr = rev.CANSparkMax(DriveConsts.CAN_FR, rev.CANSparkMax.MotorType.kBrushless)
        self.drive_bl = rev.CANSparkMax(DriveConsts.CAN_BL, rev.CANSparkMax.MotorType.kBrushless)
        self.drive_br = rev.CANSparkMax(DriveConsts.CAN_BR, rev.CANSparkMax.MotorType.kBrushless)

        # Inversion configuration for the 2022+ WPILib MecanumDrive code, which
        # removed internal inversion for right-side motors.
        self.drive_fl.setInverted(False) # 
        self.drive_fr.setInverted(True) # 
        self.drive_bl.setInverted(False) # 
        self.drive_br.setInverted(True) # 

        # Set all motors to coast mode when idle/neutral.
        # Note that this is "IdleMode" rather than the "NeutralMode" 
        # nomenclature used by CTRE CANTalons.
        self.drive_fl.setIdleMode(rev.CANSparkMax.IdleMode.kCoast)
        self.drive_fr.setIdleMode(rev.CANSparkMax.IdleMode.kCoast)
        self.drive_bl.setIdleMode(rev.CANSparkMax.IdleMode.kCoast)
        self.drive_br.setIdleMode(rev.CANSparkMax.IdleMode.kCoast)

        # Now that we have motors, we can set up an object that will handle mecanum drive.
        self.drivetrain = wpilib.drive.MecanumDrive(self.drive_fl, self.drive_bl, self.drive_fr, self.drive_br)

        # Get encoders for each motor.
        self.front_left_encoder = self.drive_fl.getEncoder()
        self.front_right_encoder = self.drive_fr.getEncoder()
        self.back_left_encoder = self.drive_bl.getEncoder()
        self.back_right_encoder = self.drive_br.getEncoder()
        # Reset the encoders as they could be at any position after some runs.
        self.front_left_encoder.setPosition(0.0)
        self.front_right_encoder.setPosition(0.0)
        self.back_left_encoder.setPosition(0.0)
        self.back_right_encoder.setPosition(0.0)

        # ---------------------------------------------------------------------
        # Set up odometry, that is figuring out how far we have driven. Example:
        # https://github.com/robotpy/examples/blob/main/MecanumBot/drivetrain.py
        # ---------------------------------------------------------------------

        # The "pose" or position and rotation of the robot.  Usually, we will use
        # odometry to estimate this, but we keep it as a member variable to carry
        # carry between different method calls.  Start at zero, facing +x direction,
        # which for poses, is like Translation2d, +x = forward.
        self.pose = wpimath.geometry.Pose2d()

        # Wheel locations, noting that Translation2d assumes +x is forward and +y is left.
        front_left_location = wpimath.geometry.Translation2d(DriveConsts.TRACK_HALF_WIDTH, DriveConsts.WHEELBASE_HALF_LENGTH)
        front_right_location = wpimath.geometry.Translation2d(DriveConsts.TRACK_HALF_WIDTH, -DriveConsts.WHEELBASE_HALF_LENGTH)
        back_left_location = wpimath.geometry.Translation2d(-DriveConsts.TRACK_HALF_WIDTH, DriveConsts.WHEELBASE_HALF_LENGTH)
        back_right_location = wpimath.geometry.Translation2d(-DriveConsts.TRACK_HALF_WIDTH, -DriveConsts.WHEELBASE_HALF_LENGTH)

        # A kinematics object helps convert between wheel speeds and chassis 
        # velocity/rotation and back.
        self.kinematics = wpimath.kinematics.MecanumDriveKinematics(
            front_left_location, front_right_location, back_left_location, 
            back_right_location)
        
        # An odometry object does the calculations to estimate how far the 
        # robot has moved. 
        self.odometry = wpimath.kinematics.MecanumDriveOdometry(
            self.kinematics, self.gyro.getRotation2d(), 
            self.get_current_distances(), initialPose=self.pose)

        # ---------------------------------------------------------------------
        # Create PID controllers for each of the three axes (x=forward, y=left,
        # rotation CCW).  These will help us drive to desired positions.
        # A Profiled PID constrains the velocity and acceleration.
        # Tolerances let us determine when we are at the goal position.
        # ---------------------------------------------------------------------

        # Controller for the x direction (+ forward, away from the driver)
        self.x_controller = ProfiledPIDController(
            DriveConsts.PIDX_KP, 0, 0,
            TrapezoidProfile.Constraints(DriveConsts.HORIZ_MAX_V, DriveConsts.HORIZ_MAX_A)
        )
        self.x_controller.setTolerance(DriveConsts.HORIZ_POS_TOL, DriveConsts.HORIZ_VEL_TOL)

        # Controller for the y direction (+ left, viewed by the driver)
        self.y_controller = ProfiledPIDController(
            DriveConsts.PIDY_KP, 0, 0,
            TrapezoidProfile.Constraints(DriveConsts.HORIZ_MAX_V, DriveConsts.HORIZ_MAX_A)
        )
        self.y_controller.setTolerance(DriveConsts.HORIZ_POS_TOL, DriveConsts.HORIZ_VEL_TOL)

        # Controller for the rotation direction (+ counterclockwise, viewed from above)
        # Continuous input enabled so that we can turn left or right, whichever is shorter.
        self.rot_controller = ProfiledPIDController(
            DriveConsts.PID_ROT_KP, 0, 0,
            TrapezoidProfile.Constraints(DriveConsts.ROT_MAX_V, DriveConsts.ROT_MAX_A)
        )
        self.rot_controller.setTolerance(DriveConsts.ROT_POS_TOL, DriveConsts.ROT_VEL_TOL)
        self.rot_controller.enableContinuousInput(-180, 180)


    ###########################################################################
    # Methods in base classes that we override here                           #
    ###########################################################################

    def periodic(self):
        """
        This method runs once every 20 msec in all modes (including simulation).  
        Since we don't want to interfere with various commands that may be 
        running, it is best to only put sensing and telemetry functionality here.
        But the WPILib docs say that subsystem periodic() are called before
        any commands run, so this is a good place to get the gyro angle once
        (a small optimization).
        (https://docs.wpilib.org/en/stable/docs/software/commandbased/command-scheduler.html)
        """
        # Compute (estimate) robot position and store it.
        self.pose = self.odometry.update(self.gyro.getRotation2d(), self.get_current_distances())

        # Send the heading angle to the dashboard
        # TODO: implement shuffleboard
        wpilib.SmartDashboard.putString('DB/String 0', 'Angle +=CCW: {:5.1f}'.format(self.pose.rotation().degrees()))
        wpilib.SmartDashboard.putString('DB/String 1', 'x/forward (m): {:5.2f}'.format(self.pose.X()))
        wpilib.SmartDashboard.putString('DB/String 2', 'y/left    (m): {:5.2f}'.format(self.pose.Y()))
        wpilib.SmartDashboard.putString('DB/String 3', 'FR enc: {:5.2f}'.format(self.front_right_encoder.getPosition()))

    def simulationPeriodic(self):
        """Called in simulation after periodic() to update simulation variables."""
        pass

    # TODO: implement a sendable for telemetry
    # def initSendable(self, builder):
    #     """
    #     Overrides the method inherited from the Sendable class to create a
    #     system that automatically updates the dashboard.
    #     """
    #     builder.setSmartDashboardType('MAKOCommand')
    #     # builder.addStringProperty('DB/String 0', self.get_heading_string)
    #     builder.addDoubleProperty('angle', self.gyro.getAngle, None)


    ###########################################################################
    # Methods that create commands                                            #
    ###########################################################################

    # def drive_to_pose_command(self) -> commands2.Command:
    #     return self.startEnd()

    ###########################################################################
    # Methods to use in commands, either created in this class or elsewhere   #
    ###########################################################################

    def drive_field_relative(self, forward: float, left: float, rot_ccw: float):
        """Drive in a direction relative to the field (or the driver assuming the 
           robot starts facing the same direction as the driver is facing).
           :param: forward move away from the driver. (+x direction in Pose)
           :param: left    move leftward from the driver's perspective. (+y in Pose)
           :param: rot_ccw positive to rotate the robot counterclockwise as 
                   viewed from above. 
        """
        # Negate the reported heading by converting to degrees, negating, and
        # creating a new Rotation2d object.
        heading_degrees = self.pose.rotation().degrees()
        drive_heading = wpimath.geometry.Rotation2d.fromDegrees(-heading_degrees)

        # driveCartesian's documentation does not match its behavior, at least 
        # with this omni wheel drive.  Forward is OK, but right/left seems inverted,
        # as does the rotation, which is why we negated above.
        self.drivetrain.driveCartesian(forward, -left, -rot_ccw, drive_heading)

    def drive_to_goal(self):
        """
        Drive from present pose toward another pose on the field.
        Uses the goal set by set_goal_pose().  Call that method once first.
        """
        # Calculate the "gas pedal" values for each axis.
        present_x = self.pose.X()
        pid_output_x = self.x_controller.calculate(present_x)
        clamped_x = clamp(pid_output_x, -1.0, 1.0) # Drive expects between -1 and 1.

        present_y = self.pose.Y()
        pid_output_y = self.y_controller.calculate(present_y)
        clamped_y = clamp(pid_output_y, -1.0, 1.0)

        # TODO: rotation

        # Send the values to the drive train.
        self.drive_field_relative(clamped_x, clamped_y, 0.0)

    def set_goal_pose(self, goal_pose: wpimath.geometry.Pose2d):
        """
        Set the goal for upcoming use of PID controllers.
        Call this before using drive_to_goal().
        :param: goal_pose The desired pose to drive to.
        """
        # Reset the PID loops, because we're starting a new trajectory.
        self.reset_pids()

        # Extract each axis to set the goal for the corresponding controller.
        goal_x = goal_pose.X()
        self.x_controller.setGoal(goal_x)
        goal_y = goal_pose.Y()
        self.y_controller.setGoal(goal_y)
        # TODO: rotation (not as safe to test when tethered)


    def is_at_goal(self) -> bool:
        """
        Used with PID loops to determine if the robot is at the target/goal
        position.
        :returns: True if all three axes (X, Y, rotation) are at the goal.
        """
        # Different versions combining different axes for testing:
        # temp = self.x_controller.atGoal() and self.y_controller.atGoal() and self.rot_controller.atGoal()
        temp = self.x_controller.atGoal() and self.y_controller.atGoal()
        return temp


    ###########################################################################
    # Helper methods                                                          #
    ###########################################################################

    def get_current_distances(self)-> wpimath.kinematics.MecanumDriveWheelPositions:
        """
        Returns the current distances measured by the drivetrain.
        :returns: MecanumDriveWheelPositions with rim distances in meters.
        """
        # Start with an empty positions object that will be returned.
        pos = wpimath.kinematics.MecanumDriveWheelPositions()

        # Precompute the factor to convert motor revolutions to wheel rim 
        # distance traveled in meters.  The factor 1.414 = sqrt(2) is to
        # correct for the difference between MAKO's omni wheels and a true
        # mecanum wheel-based drive.
        # rev_to_m = sqrt(2) * (wheel circumference) / (gear ratio)
        rev_to_m = 1.414 * math.pi * DriveConsts.WHEEL_DIA / DriveConsts.GEAR_RATIO

        # Fill in the positions.
        pos.frontLeft = self.front_left_encoder.getPosition() * rev_to_m
        pos.frontRight = self.front_right_encoder.getPosition() * rev_to_m
        pos.rearLeft = self.back_left_encoder.getPosition() * rev_to_m
        pos.rearRight = self.back_right_encoder.getPosition() * rev_to_m

        return pos


    def get_current_speeds(self)-> wpimath.kinematics.MecanumDriveWheelSpeeds:
        """
        Returns the current speeds measured by the drivetrain.
        :returns: MecanumDriveWheelSpeeds with rim speeds in meters/second.
        """

        # Precompute the factor to convert motor RPM to wheel rim speed in meters/second.
        # rpm_to_m_s = sqrt(2) * (wheel circumference) / (gear ratio) / (60 seconds/minute)
        rpm_to_m_s = 1.414 * math.pi * DriveConsts.WHEEL_DIA / DriveConsts.GEAR_RATIO / 60

        # Fill in the positions converting to wheel rim speed traveled in meters.
        front_left_speed = self.front_left_encoder.getVelocity() * rpm_to_m_s
        front_right_speed = self.front_right_encoder.getVelocity() * rpm_to_m_s
        rear_left_speed = self.back_left_encoder.getVelocity() * rpm_to_m_s
        rear_right_speed = self.back_right_encoder.getVelocity() * rpm_to_m_s

        return wpimath.kinematics.MecanumDriveWheelSpeeds(
            front_left_speed, front_right_speed, rear_left_speed, rear_right_speed)
    
    def get_heading_continuous_degrees(self) -> float:
        """
        Get the present robot heading in degrees, constrained to be between 
        -180 and +180 degrees, suitable for use with a continuous controller.
        :returns: heading in degrees within (-180, 180]
        """
        angle = self.pose.rotation().degrees()
        return wpimath.inputModulus(angle, -180, 180)
        
    def reset_pids(self):
        """
        Reset the state of PID controllers. Useful when starting a new command.
        """
        # Note that this assumes velocities are zero, and so won't work as well
        # if we schedule a command while moving.  To optimize, we'll need to 
        # figure out estimated speeds from odometry and call the version of
        # reset() with two parameters.
        self.x_controller.reset(self.pose.X())
        self.y_controller.reset(self.pose.Y())
        self.rot_controller.reset(self.pose.rotation().degrees())


#==============================================================================
# Simple helper functions that don't need to be in the class.
#==============================================================================
def clamp(val, minval, maxval): 
    """Returns a number clamped to minval and maxval."""
    return max(min(val, maxval), minval)

