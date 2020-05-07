# !/usr/bin/env python3
"""
    WHEA Robotics code for the MAKO robot project.
"""

import wpilib
from rev.color import ColorSensorV3
from rev.color import ColorMatch

class MAKORobot(wpilib.TimedRobot):
    def robotInit(self):
        """This function is called upon program startup.
           Initialize shared variables and objects.
        """
        self.print_timer = wpilib.Timer() # A timer to help us print info periodically; still need to start it.

        # REV Robotics color sensor creation and configuration, including a color matching object.
        # Product is: https://www.revrobotics.com/rev-31-1557/.  This page has a link to the Java/C++ APIs.
        # Presently (2020-05-04), the RobotPy documentation is limited.
        self.colorSensor = ColorSensorV3(wpilib.I2C.Port.kOnboard)

        # Define a set of target colors to match against by their normalized RGB values.
        self.BlueTarget = wpilib.Color(0.133, 0.351, 0.516)
        self.PurpleTarget = wpilib.Color(0.234, 0.360, 0.406)
        self.PinkTarget = wpilib.Color(0.427, 0.374, 0.199)
        self.YellowTarget = wpilib.Color(0.326, 0.583, 0.092)

        # A ColorMatch object has methods to check for matching colors.
        self.colormatcher = ColorMatch()
        # Add our target values to colormatcher
        self.colormatcher.addColorMatch(self.BlueTarget)
        self.colormatcher.addColorMatch(self.PurpleTarget)
        self.colormatcher.addColorMatch(self.PinkTarget)
        self.colormatcher.addColorMatch(self.YellowTarget)

    def disabledInit(self):
        """This function gets called once when the robot is disabled.
           In the past, we have not used this function, but it could occasionally
           be useful.  In this case, we reset some SmartDashboard values.
        """
        wpilib.SmartDashboard.putString('DB/String 0', '')
        wpilib.SmartDashboard.putNumber('DB/Slider 0', 0)
        wpilib.SmartDashboard.putBoolean('DB/LED 0', False)

    def disabledPeriodic(self):
        """Another function we have not used in the past.  Adding for completeness."""
        pass

    def autonomousInit(self):
        """This function is run once each time the robot enters autonomous mode."""
        pass

    def autonomousPeriodic(self):
        """This function is called periodically during autonomous."""
        pass

    def teleopInit(self):
        """This function is run once each time the robot enters teleop mode."""
        self.print_timer.start() # Now it starts counting.

    def teleopPeriodic(self):
        """This function is called periodically during teleop."""
        detected_color = self.colorSensor.getColor() # color is an object with three fields for the different colors
        confidence = 0.0 # "confidence" is a dummy variable for Python.  The C function "matchClosestColor()" modifies it, but Python can't do that.
        matched_color = self.colormatcher.matchClosestColor(detected_color, confidence)
        if self.isEqualColor(matched_color, self.BlueTarget):
            match_string = 'blue'
        else:
            match_string = 'other'

        # The timer's hasPeriodPassed() method returns true if the time has passed, and updates
        # the timer's internal "start time".  This period is 1.0 seconds.
        if self.print_timer.hasPeriodPassed(1.0):
            # Send a string representing the red component to a field called 'DB/String 0' on the SmartDashboard.
            # The default driver station dashboard's "Basic" tab has some pre-defined keys/fields
            # that it looks for, which is why I chose these.
            wpilib.SmartDashboard.putString('DB/String 0', 'red:   {:5.3f}'.format(detected_color.red))
            wpilib.SmartDashboard.putString('DB/String 1', 'green: {:5.3f}'.format(detected_color.green))
            wpilib.SmartDashboard.putString('DB/String 2', 'blue:  {:5.3f}'.format(detected_color.blue))
            wpilib.SmartDashboard.putString('DB/String 3', 'matches: {}'.format(match_string))
            wpilib.SmartDashboard.putNumber('DB/Slider 0', 4)
            wpilib.SmartDashboard.putBoolean('DB/LED 0', True)

            # You can use your mouse to move the DB/Slider 1 slider on the dashboard, and read
            # the value it shows with the command below.  0.0 below is the default value, should
            # the key 'Db/Slider 1' not exist in the SmartDashboard table (for instance, a typo).
            user_value = wpilib.SmartDashboard.getNumber('DB/Slider 1', 0.0)
            # Send info to the logger and thus console.
            # Note the string format: the part in {} gets replaced by the value of the variable
            # user_value, and is formatted as a floating point (the "f"), with 4 digits and 2 digits
            # after the decimal place. https://docs.python.org/3/library/string.html#formatstrings
            self.logger.info('Slider 1 is {:4.2f}'.format(user_value))

    def isEqualColor(self, a, b):
        """Returns true if the two colors are equal."""
        return ((a.red == b.red) and (a.green == b.green) and (a.blue == b.blue))


# The following little bit of code allows us to run the robot program.
# The special variable __name__ contains the name of the module that it is in,
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
