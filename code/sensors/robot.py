# !/usr/bin/env python3
"""
    WHEA Robotics code for the MAKO robot project.
"""

import wpilib
import color_util # Imports definitions in the file color_util.py that we created (same folder).

class MAKORobot(wpilib.TimedRobot):
    def robotInit(self):
        """This function is called upon program startup as part of WPILIB/FRC/RobotPy.
           In it, we should initialize the robot's shared variables and objects.
        """
        self.print_timer = wpilib.Timer() # A timer to help us print info periodically; still need to start it.
        self.color_pwd = color_util.Color_Password2() # A class that looks for a password based on colors.

        # Gyro measures rate of rotation, and plugs into the "SPI" port on the roboRIO
        # https://wiki.analog.com/first/adxrs450_gyro_board_frc
        # Positive rotation is clockwise.
        self.gyro = wpilib.ADXRS450_Gyro() # Calibration happens during initialization, so keep the robot still when powering on.
        # It is best to let the robot warm up so that the sensor reaches a steady temperature before calibrating it.  This may not
        # always be possible in a match situation.  For reference, Rod measured the amount of drift during a 2:30 match by just letting
        # the robot sit still.  I rebooted robot code between measurements, so that recalibration and zeroing would happen.
        # First turned on, and then repeated 2.5-minute tests: 9.9, 1.8, 3.0, 16.8 (!), 1.6, 8.0 degrees.
        # Similar test, after the robot had been on 1/2 hour:  2.4, 1.9, -2.0, 0.3, 0.3, 0.7 degrees.

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
        (password, detected, closest_match) = self.color_pwd.check() # Note that this method returns two colors:
                                                                       # The detected one and its closest match.
        match_descr = color_util.get_color_string(closest_match) # Turn into a string.

        # The timer's hasPeriodPassed() method returns true if the time has passed, and updates
        # the timer's internal "start time".  This period is 1.0 seconds.
        if self.print_timer.hasPeriodPassed(1.0):
            # Send a string representing the red component to a field called 'DB/String 0' on the SmartDashboard.
            # The default driver station dashboard's "Basic" tab has some pre-defined keys/fields
            # that it looks for, which is why I chose these.
            wpilib.SmartDashboard.putString('DB/String 0', 'red:   {:5.3f}'.format(detected.red))
            wpilib.SmartDashboard.putString('DB/String 1', 'green: {:5.3f}'.format(detected.green))
            wpilib.SmartDashboard.putString('DB/String 2', 'blue:  {:5.3f}'.format(detected.blue))
            wpilib.SmartDashboard.putString('DB/String 3', 'matches: {}'.format(match_descr))
            wpilib.SmartDashboard.putNumber('DB/Slider 0', 4)
            wpilib.SmartDashboard.putBoolean('DB/LED 0', password) # Light the virtual LED if the password has been entered properly.
            wpilib.SmartDashboard.putString('DB/String 5', 'Angle: {:5.1f}'.format(self.gyro.getAngle()))

            # You can use your mouse to move the DB/Slider 1 slider on the dashboard, and read
            # the value it shows with the command below.  0.0 below is the default value, should
            # the key 'Db/Slider 1' not exist in the SmartDashboard table (for instance, a typo).
            user_value = wpilib.SmartDashboard.getNumber('DB/Slider 1', 0.0)
            # Send info to the logger and thus console.
            # Note the string format: the part in {} gets replaced by the value of the variable
            # user_value, and is formatted as a floating point (the "f"), with 4 digits and 2 digits
            # after the decimal place. https://docs.python.org/3/library/string.html#formatstrings
            #self.logger.info('Slider 1 is {:4.2f}'.format(user_value))


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
