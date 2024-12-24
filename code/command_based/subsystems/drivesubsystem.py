# Import standard Python modules.
import math

# Import WPILib and other robotics modules.
import commands2
import rev
import wpilib
import wpilib.drive
import wpimath.geometry
import wpimath.kinematics

# Import our modules.
import constants

class DriveSubsystem(commands2.Subsystem):
    def __init__(self) -> None:
        super().__init__()

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
        self.drive_fl = rev.CANSparkMax(4, rev.CANSparkMax.MotorType.kBrushless)
        self.drive_fr = rev.CANSparkMax(3, rev.CANSparkMax.MotorType.kBrushless)
        self.drive_bl = rev.CANSparkMax(2, rev.CANSparkMax.MotorType.kBrushless)
        self.drive_br = rev.CANSparkMax(1, rev.CANSparkMax.MotorType.kBrushless)

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
        front_left_location = wpimath.geometry.Translation2d(constants.TRACK_HALF_WIDTH, constants.WHEELBASE_HALF_LENGTH)
        front_right_location = wpimath.geometry.Translation2d(constants.TRACK_HALF_WIDTH, -constants.WHEELBASE_HALF_LENGTH)
        back_left_location = wpimath.geometry.Translation2d(-constants.TRACK_HALF_WIDTH, constants.WHEELBASE_HALF_LENGTH)
        back_right_location = wpimath.geometry.Translation2d(-constants.TRACK_HALF_WIDTH, -constants.WHEELBASE_HALF_LENGTH)

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


    # TODO: implement a sendable for telemetry
    # def initSendable(self, builder):
    #     """
    #     Overrides the method inherited from the Sendable class to create a
    #     system that automatically updates the dashboard.
    #     """
    #     builder.setSmartDashboardType('MAKOCommand')
    #     # builder.addStringProperty('DB/String 0', self.get_heading_string)
    #     builder.addDoubleProperty('angle', self.gyro.getAngle, None)

    def periodic(self):
        """
        This method runs once every 20 msec in all modes (except simulation).  
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

    def simulationPeriodic(self):
        """Similar to periodic(), but for simulation"""
        pass

    #########################################################
    # Methods to use in commands                            #
    #########################################################

    def drive_field_relative(self, right: float, forward: float, rot_cw: float):
        """Drive in a direction relative to the field (or the driver assuming the 
           robot starts facing the same direction as the driver is facing).
           :param: right   move rightward from the driver's perspective.
           :param: forward move away from the driver.
           :param: rot_cw  rotate the robot clockwise as viewed from above. 
           (positive = clockwise, though that makes the angle go negative by proper math.)
        """
        heading_degrees = self.pose.rotation().degrees()
        drive_heading = wpimath.geometry.Rotation2d.fromDegrees(-heading_degrees)
        #heading = self.gyro.getRotation2d()

        # From the documentation, North, East, and Down are the three axes.
        # Positive X is forward, Positive Y is right, Positive Z is down.  Clockwise rotation around Z (as viewed from ___) is positive.
        self.drivetrain.driveCartesian(
            right / constants.DRIVE_SLOWER, forward / constants.DRIVE_SLOWER, 
            rot_cw / constants.DRIVE_SLOWER, drive_heading)

    #########################################################
    # Helper methods                                        #
    #########################################################

    # def get_heading(self) -> wpimath.geometry.Rotation2d:
    #     """
    #     Get the heading, that is the angle the robot is facing, as a Rotation2d 
    #     object.
    #     :returns: The heading.  Note that when converted to degrees, the 
    #     Rotation2d will be negative for a counterclockwise rotation, opposite
    #     what you would expect.
    #     """
    #     return wpimath.geometry.Rotation2d(self.gyro.getAngle() * math.pi / 180)

    # def get_heading_string(self):
    #     return 'Angle +=CCW: {:5.1f}'.format(-self.get_heading().degrees())
    
    # def get_heading_degrees(self) -> float:
    #     return self.gyro.getAngle()
    
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
        rev_to_m = 1.414 * math.pi * constants.DRIVE_WHEEL_DIA / constants.DRIVE_GEAR_RATIO

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
        rpm_to_m_s = 1.414 * math.pi * constants.DRIVE_WHEEL_DIA / constants.DRIVE_GEAR_RATIO / 60

        # Fill in the positions converting to wheel rim speed traveled in meters.
        front_left_speed = self.front_left_encoder.getVelocity() * rpm_to_m_s
        front_right_speed = self.front_right_encoder.getVelocity() * rpm_to_m_s
        rear_left_speed = self.back_left_encoder.getVelocity() * rpm_to_m_s
        rear_right_speed = self.back_right_encoder.getVelocity() * rpm_to_m_s

        return wpimath.kinematics.MecanumDriveWheelSpeeds(
            front_left_speed, front_right_speed, rear_left_speed, rear_right_speed)
        
