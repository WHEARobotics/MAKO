#!/usr/bin/env python3
import commands2
import wpilib


import robotcontainer

"""
MAKO robot using the commands2 framework.  Based largely on the robotpy examples
on Github: https://github.com/robotpy/examples/tree/main/FrisbeeBot being one
of them.
"""

class CommandRobot(commands2.TimedCommandRobot): # Inheriting from TimedCommandRobot as in the example, instead of TimedRobot, as in our XRP example?
    
    def robotInit(self) -> None:
        self.autonomousCommand: typing.Optional[commands2.Command] = None

        # Instantiate the robot container, which is where we declare most of the robot.
        self.container = robotcontainer.RobotContainer()

    def disabledInit(self) -> None:
        pass
    
    def disabledPeriodic(self) -> None:
        pass
    
    def autonomousInit(self) -> None:
        self.autonomousCommand = self.container.getAutonomousCommand()

        # Schedule the autonomous command if it exists.
        if self.autonomousCommand is not None:
            self.autonomousCommand.schedule()
        else:
            print("No autonomous command")

    def autonomousPeriodic(self):
        """Called periodically during autonomous, but not needed if we've scheduled a command?"""
        # TODO: is the above documentation comment accurate?
        pass

    def teleopInit(self) -> None:
        # Make sure autonomous stops running when teleop starts.
        if self.autonomousCommand is not None:
            self.autonomousCommand.cancel()

    def teleopPeriodic(self) -> None:
        """Called periodically during operator control."""
        pass

    def testInit(self) -> None:
        # Cancel all running commands at the start of test mode.
        commands2.CommandScheduler.getInstance().cancelAll()

        


    