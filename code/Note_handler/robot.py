import wpilib
import wpilib.drive
import wpimath
import rev
from rev import CANSparkLowLevel

class Myrobot(wpilib.TimedRobot):
    '''Simple robot to drive motors for Note-handling manipulators for 2024.
       Initially written for MAKO, but could easily be changed.
    '''

    def robotInit(self):
        self.xbox = wpilib.XboxController(0)
        # MAKO's left-side motor controllers
        self.motor2 = rev.CANSparkMax(2, rev._rev.CANSparkLowLevel.MotorType.kBrushless)
        self.motor4 = rev.CANSparkMax(4, rev._rev.CANSparkLowLevel.MotorType.kBrushless)                 #"Channel" is ID of CANSparkMax Motorcontroller on CAN bus

    def disabledInit(self):
        pass

    def disabledPeriodic(self):
        pass

    def disabledExit(self):
        pass

    def autonomousInit(self):
        pass

    def autonomousPeriodic(self):
        pass

    def autonomousExit(self):
        pass

    def teleopInit(self):
        pass

    def teleopPeriodic(self):
        # Get control values so we can manipulate them if desired.
        left = self.xbox.getLeftY()
        right = self.xbox.getRightY()

        # Command motor operation.
        self.motor2.set(left)
        self.motor4.set(right)

    def teleopExit(self):
        pass

if __name__ == '__main__':
    wpilib.run(Myrobot)
