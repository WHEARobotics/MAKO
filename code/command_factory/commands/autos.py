import commands2
import commands2.cmd

import subsystems.drivesubsystem
from commands.drivecommands import DriveCommands
from constants.fieldconstants import Positions
import subsystems.elevatorsubsystem

class Autos:
    """Class to hold autonomous command factories"""

    def __init__(self):
        raise Exception("This is a utility class, don't make instances of it.")
                        
    @staticmethod
    def side_step(drive: subsystems.drivesubsystem.DriveSubsystem):
        """Autonomous routine that drives forward, waits, then moves left."""
        return commands2.cmd.sequence(
            DriveCommands.drive_goal(Positions.AWAY, drive),
            DriveCommands.drive_idle_wait(5.0, drive),
            DriveCommands.drive_goal(Positions.SIDE, drive)
        )
    
    def forward(drive: subsystems.drivesubsystem.DriveSubsystem):
        """Autonomous routine that drives forward"""
        return commands2.cmd.sequence(
            DriveCommands.drive_goal(Positions.AWAY, drive)
        )
    def forward_elevator(drive: subsystems.drivesubsystem.DriveSubsystem, elevator: subsystems.elevatorsubsystem.ElevatorSubsystem):
        return commands2.cmd.parallel(
            elevator.set_mid(),
            DriveCommands.drive_goal(Positions.AWAY, drive)
        )
           
        