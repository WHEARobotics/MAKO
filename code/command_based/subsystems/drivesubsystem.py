import wpilib
import wpilib.drive
import commands2
import math

import rev
import wpimath.geometry

import constants

class DriveSubsystem(commands2.Subsystem):
    def __init__(self) -> None:
        super().__init__()

        # Create and configure the drive train controllers and motors, all Rev. Robotics SparkMaxes driving NEO motors.
        self.drive_rr = rev.CANSparkMax(1, rev.CANSparkMax.MotorType.kBrushless)
        self.drive_rf = rev.CANSparkMax(3, rev.CANSparkMax.MotorType.kBrushless)
        self.drive_lr = rev.CANSparkMax(2, rev.CANSparkMax.MotorType.kBrushless)
        self.drive_lf = rev.CANSparkMax(4, rev.CANSparkMax.MotorType.kBrushless)

        # Inversion configuration for the 2022 WPILib MecanumDrive code, which removed internal inversion for right-side motors.
        self.drive_rr.setInverted(True) # 
        self.drive_rf.setInverted(True) # 
        self.drive_lr.setInverted(False) # 
        self.drive_lf.setInverted(False) # 

        # Set all motors to coast mode when idle/neutral.
        # Note that this is "IdleMode" rather than the "NeutralMode" nomenclature used by CTRE CANTalons.
        self.drive_rr.setIdleMode(rev.CANSparkMax.IdleMode.kCoast)
        self.drive_rf.setIdleMode(rev.CANSparkMax.IdleMode.kCoast)
        self.drive_lr.setIdleMode(rev.CANSparkMax.IdleMode.kCoast)
        self.drive_lf.setIdleMode(rev.CANSparkMax.IdleMode.kCoast)

        # Now that we have motors, we can set up an object that will handle mecanum drive.
        # From the documentation, North, East, and Down are the three axes.
        # Positive X is forward, Positive Y is right, Positive Z is down.  Clockwise rotation around Z (as viewed from ___) is positive.
        self.drivetrain = wpilib.drive.MecanumDrive(self.drive_lf, self.drive_lr, self.drive_rf, self.drive_rr)

        # TODO: get encoders for each motor.

        # The gyro is also part of the drive system, since it helps keep it on track.
        self.gyro = wpilib.ADXRS450_Gyro()

    def get_heading(self) -> wpimath.geometry.Rotation2d:
        """Return the heading, that is the angle the robot is facing, as a Rotation2d object."""
        return wpimath.geometry.Rotation2d(self.gyro.getAngle() * math.pi / 180)

    def drive_field_relative(self, right: float, forward: float, rot_cw: float):
        """Drive in a direction relative to the field (or the operator assuming the 
           robot starts facing away from the operator).
           :param: right   move rightward from the driver's perspective.
           :param: forward move away from the driver.
           :param: rot_cw  rotate the robot clockwise as viewed from above. 
           (positive = clockwise, though that makes the angle go negative by proper math.)
        """
        heading = self.get_heading()
        self.drivetrain.driveCartesian(right / constants.DRIVE_SLOWER, forward / constants.DRIVE_SLOWER, rot_cw / constants.DRIVE_SLOWER, heading)
        # Send the heading angle to the dashboard
        wpilib.SmartDashboard.putString('DB/String 0', 'Angle +=CCW: {:5.1f}'.format(-heading.degrees()))

    