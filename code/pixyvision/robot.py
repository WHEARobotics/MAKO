# !/usr/bin/env python3
"""
    WHEA Robotics code for the MAKO robot project.
"""

import time
import wpilib
import pixy2api.pixy2

class MAKORobot(wpilib.TimedRobot):
    def robotInit(self):
        """This function is called upon program startup as part of WPILIB/FRC/RobotPy.
           In it, we should initialize the robot's shared variables and objects.
        """
        self.print_timer = wpilib.Timer() # A timer to help us print info periodically; still need to start it.
        self.pixy = pixy2api.pixy2.Pixy2(pixy2api.pixy2.Pixy2.LinkType.SPI, 0)
        self.pixy.init() # Need to call init() to start communication with the Pixy2.
        print('FPS: {}'.format(self.pixy.getFPS()))
        #print('lamp white: {}'.format(self.pixy.setLamp(1,0)))
        print('led rgb: {}'.format(self.pixy.setLED(red=0,green=255,blue=0)))
        print('lamp on rgb: {}'.format(self.pixy.setLamp(0,1)))

    def disabledInit(self):
        """This function gets called once when the robot is disabled.
           In the past, we have not used this function, but it could occasionally
           be useful.  In this case, we reset some SmartDashboard values.
        """
        pass

    def disabledPeriodic(self):
        """Another function we have not used in the past.  Adding for completeness."""
        pass

    def autonomousInit(self):
        """This function is run once each time the robot enters autonomous mode."""
        self.gyro.reset()  # Reset at the beginning of a match, because the robot could have been sitting for a while, gyro drifting.
        pass

    def autonomousPeriodic(self):
        """This function is called periodically during autonomous."""
        pass

    def teleopInit(self):
        """This function is run once each time the robot enters teleop mode."""
        self.print_timer.start() # Now it starts counting.

    def teleopPeriodic(self):
        """This function is called periodically during teleop."""

        # The timer's hasPeriodPassed() method returns true if the time has passed, and updates
        # the timer's internal "start time".  This period is 1.0 seconds.
        if self.print_timer.hasPeriodPassed(1.0):
            # Send a string representing the red component to a field called 'DB/String 0' on the SmartDashboard.
            # The default driver station dashboard's "Basic" tab has some pre-defined keys/fields
            # that it looks for, which is why I chose these.
            wpilib.SmartDashboard.putString('DB/String 0', 'some value{:5.3f}'.format(0.25))
            # Send info to the logger and thus console.
            # Note the string format: the part in {} gets replaced by the value of the variable
            # user_value, and is formatted as a floating point (the "f"), with 4 digits and 2 digits
            # after the decimal place. https://docs.python.org/3/library/string.html#formatstrings
            #self.logger.info('Another value is {:4.2f}'.format(0.33))
            num_blocks = self.pixy.getCCC().getBlocks(wait=False, sigmap=0x01, maxBlocks=10)
            if num_blocks > 0:
                blocks = self.pixy.getCCC().getBlockCache()
                print('blocks: {} {}'.format(num_blocks, blocks[0].toString()))
            else:
                print('blocks: {}'.format(num_blocks))

# The following little bit of code allows us to run the robot program.
# In Python, the special variable __name__ contains the name of the module that it is in,
# or since this file is 'robot.py', it would ordinarily be 'robot'.  The exception
# is when you are executing the module, as in you typed "python robot.py" at a command
# prompt.  In that case, the variable is given the special string value '__main__' to
# denote that it is the main module that is being executed.  And that is effectively
# what RobotPy does: when it boots, it executes the file robot.py.
# When that happens, it will read the class definition above, and then come to this
# statement, and the "if" will be true.  Therefore, it will execute wpilib.run(classname),
# where classname is the robot class we have defined, in this case MAKORobot.  The
# wpilib.run() function does the necessary stuff to call robotInit(), autonomousInit(), etc.
# See: https://stackoverflow.com/questions/419163/what-does-if-name-main-do
if __name__ == '__main__':
    wpilib.run(MAKORobot)
