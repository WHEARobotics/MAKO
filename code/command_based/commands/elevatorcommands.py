import commands2.cmd
import wpimath.geometry

import subsystems.elevatorsubsystem

class ElevatorCommands:
    """Container for elevator command factories."""

    def __init__(self):
        raise Exception("This is a utility class, don't make instances of it.")
                        
    @staticmethod
    def move_goal(goal: float, elev: subsystems.elevatorsubsystem.ElevatorSubsystem):
        """
        A command that moves the elevator toward a goal height in inches.
        :param: goal  The height to move toward.
        :param: elev  The elevator subsystem to operate on.
        """
        return commands2.cmd.FunctionalCommand(
            # Initialize by setting the goal.
            lambda: elev.set_goal_height_inches(goal),

            # Move while command is executing.
            elev.move_to_goal,

            # What to do when ending, the parameter "interrupt" will be true if
            #  the command was interrupted, but we ignore it.  Don't do anything.
            lambda interrupt: None,

            # Call this to know when to end the command.
            elev.is_at_goal,

            # Require the elevator subsystem that is passed in.
            elev
        )

