import commands2.cmd
import wpimath.geometry

import subsystems.drivesubsystem

class DriveCommands:
    """Container for drive command factories."""

    def __init__(self):
        raise Exception("This is a utility class, don't make instances of it.")
                        
    @staticmethod
    def drive_goal(goal: wpimath.geometry.Pose2d, drive: subsystems.drivesubsystem.DriveSubsystem):
        """
        A command that drives the robot toward a goal pose (position and rotation).
        :param: goal  The pose to drive toward.
        :param: drive The drive subsystem to operate on.
        """
        return commands2.cmd.FunctionalCommand(
            # Initialize by setting the goal.
            lambda: drive.set_goal_pose(goal),

            # Drive while command is executing.
            drive.drive_to_goal,

            # What to do when ending, the parameter interrupt will be true if
            #  the command was interrupted, but we ignore it.  Stop driving.
            lambda interrupt: drive.drive_field_relative(0.0, 0.0, 0.0),

            # Call this to know when to end the command.
            drive.is_at_goal,

            # Require the drive subsystem passed in.
            drive
        )

    @staticmethod
    def drive_idle_wait(delay_seconds: float, drive: subsystems.drivesubsystem.DriveSubsystem):
        """
        A command that idles the drive train for a specified number of seconds.  Using
        this command is preferable to just using commands2.cmd.WaitSeconds() because 
        the latter doesn't update the drivetrain motors, and you will get errors about
        motor safety.
        :param: delay_seconds Amount of time to sit idle.
        :param: drive         The drive subsystem that is being idled.
        """
        return commands2.cmd.deadline(
            # The deadline being the one that will interrupt others.
            commands2.cmd.waitSeconds(delay_seconds),
            # The other commands running in parallel (in this case, only one)
            commands2.cmd.RunCommand(
                lambda: drive.drive_field_relative(0.0, 0.0, 0.0)
            )
        )