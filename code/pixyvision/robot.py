# !/usr/bin/env python3
"""
    WHEA Robotics code for the MAKO robot project.
"""

import wpilib

class MAKORobot(wpilib.TimedRobot):
    def robotInit(self):
        """This function is called upon program startup as part of WPILIB/FRC/RobotPy.
           In it, we should initialize the robot's shared variables and objects.
        """
        self.print_timer = wpilib.Timer() # A timer to help us print info periodically; still need to start it.
        self.spi = wpilib.SPI(wpilib.SPI.Port.kOnboardCS0)
        # Packet stuff
        self.type = 0
        self.length = 0
        self.buffer = bytearray(22) #0x108)
        self.bufferPayload = bytearray(0x104)

        self.cs = 0 # checksum for updateChecksum().

        self.version = 0


    def disabledInit(self):
        """This function gets called once when the robot is disabled.
           In the past, we have not used this function, but it could occasionally
           be useful.  In this case, we reset some SmartDashboard values.
        """

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
            self.logger.info('Another value is {:4.2f}'.format(0.33))
            self.getVersion()

    def updateChecksum(self, b):
        """b is a byte"""
        self.cs += b

    def getChecksum(self):
        return self.cs

    def resetChecksum(self):
        self.cs = 0

    def getVersion(self):
        """Get Pixy2 version and store in self.version; return error -- mashing everything together for a first attempt."""
        self.length = 0
        self. type = 0x0E # PIXY_TYPE_REQUEST_VERSION
        self.buffer[0] = 0xAE # (PIXY_NO_CHECKSUM_SYNC & 0xff)
        self.buffer[1] = 0xC1 # ((PIXY_NO_CHECKSUM_SYNC >> 8) & 0xff)
        self.buffer[2] = 0x0E # PIXY_TYPE_REQUEST_VERSION # type
        self.buffer[3] = 0 # length of payload
        buf = bytes(self.buffer[0:4])
        self.spi.write(buf)# This writes out the bytes in the length of buf
        self.spi.read(False, self.buffer) # This reads in the length of self.buffer
        print(self.buffer)
        # for i in range(6):
        #     print('0x{:02X} '.format(self.buffer[i]))
        # print('\r\n')

    #     if self.receivePacket() == 0:
    #         if self.type == PIXY_TYPE_RESPONSE_RESOLUTION:
    #             self.version = 1 # new Version(buffer)
    #             return self.length  # Success
    #         elif type == PIXY_TYPE_RESPONSE_ERROR:
    #             return PIXY_RESULT_BUSY
    #     return PIXY_RESULT_ERROR # Some kind of bitstream error
    #
    # def receivePacket(self):
    #     res = self.getSync()
    #     if res < 0:
    #         return res
    #     if self.m_cs:
    #         res = self.receive(self.buffer, 4, 0)
    #         if res < 0:
    #             return res
    #         self.type = self.buffer[0] & 0xFF
    #         self.length = self.buffer[1] & 0xFF
    #         csSerial = ((self.buffer[3] & 0xFF) << 8) | (self.buffer[2] & 0xFF)
    #         res = self.receive(self.buffer, self.length, csCalc)
    #
    #
    #     return 0
    #
    # def receive(self, buf, length_rec, checksum):
    #     if self.cs != 0:
    #         self.resetChecksum()
    #     self.spi.read(False, buf, length_rec)
    #     for val in range(length_rec):
    #         csb = buf[i] & 0xFF
    #         self.updateChecksum(csb)
    #     return length_rec
    #
    # def getSync(self):
    #     c = bytearray(1) # A single character
    #     attempts = 0
    #     cprev = 0
    #     i = 0
    #     while(True):
    #         res = self.receive(c, 1, 0)
    #         if res >= PIXY_RESULT_OK:
    #             ret = c[0] & 0xFF
    #             # Since we're using little endian, previous byte is least significant byte.
    #             start = cprev
    #             # Current byte is most significant byte.
    #             start |= ret << 8
    #             cprev = ret
    #             if start == PIXY_CHECKSUM_SYNC:
    #                 self.m_cs = True
    #                 return PIXY_RESULT_OK
    #             if start == PIXY_NO_CHECKSUM_SYNC:
    #                 self.m_cs = True
    #                 return PIXY_RESULT_OK
    #         if i >= 4:
    #             if attempts >= 4:
    #                 return PIXY_RESULT_ERROR
    #             # try:
    #             #     pass
    #             #     # TODO: sleep for 25 microseconds.
    #             # except something about interrupted exception:
    #             attempts += 1
    #             i = 0
    #         i += 1


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
