"""
    Utilities and classes to handle color functions.
    Class Color_Handler performs simple matching.
    Class Color_Password performs a password function that you activate by showing it colors.
    Class Color_Password2 builds on the above with an arbitrary length password defined at initialization.

    Note that you should only instantiate a single one of these classes at a time to avoid
    contentions talking to the physical color sensor.
"""

import enum
import wpilib
from rev.color import ColorSensorV3
from rev.color import ColorMatch

# Define a set of target colors to match against by their normalized RGB values.
# Note that by convention, names in ALL CAPS are meant to be constants.  In Python,
# you can change them in the program, but shouldn't.
BLUE_TARGET = wpilib.Color(0.133, 0.351, 0.516)
PURPLE_TARGET = wpilib.Color(0.234, 0.360, 0.406)
PINK_TARGET = wpilib.Color(0.427, 0.374, 0.199)
YELLOW_TARGET = wpilib.Color(0.326, 0.583, 0.092)
BENCH_TARGET = wpilib.Color(0.270, 0.495, 0.235) # Rod's lab bench tan anti-static mat.

###############################################
# Some helper functions for the module.
###############################################
def is_equal_color(a, b):
    """Returns true if the two colors are equal."""
    return ((a.red == b.red) and (a.green == b.green) and (a.blue == b.blue))

def get_color_string(color):
    """Returns a string describing one of our target colors, but not the lab bench."""
    if is_equal_color(color, BLUE_TARGET):
        match_string = 'blue'
    elif is_equal_color(color, PURPLE_TARGET):
        match_string = 'purple'
    elif is_equal_color(color, PINK_TARGET):
        match_string = 'pink'
    elif is_equal_color(color, YELLOW_TARGET):
        match_string = 'yellow'
    else:
        match_string = 'other'
    return match_string

###############################################
# Classes below here.
###############################################

class Color_Handler():
    """A class that gets colors, matches them, and checks for patterns."""

    def __init__(self):
        """The __init__() method gets called when an object of a class is created."""

        # REV Robotics color sensor creation and configuration, including a color matching object.
        # Product is: https://www.revrobotics.com/rev-31-1557/.  This page has a link to the Java/C++ APIs.
        # Presently (2020-05-04), the RobotPy documentation is limited.
        self.colorSensor = ColorSensorV3(wpilib.I2C.Port.kOnboard)

        # A ColorMatch object has methods to check for matching colors.
        self.colormatcher = ColorMatch()
        # Add our target values to colormatcher
        self.colormatcher.addColorMatch(BLUE_TARGET)
        self.colormatcher.addColorMatch(PURPLE_TARGET)
        self.colormatcher.addColorMatch(PINK_TARGET)
        self.colormatcher.addColorMatch(YELLOW_TARGET)
        self.colormatcher.addColorMatch(BENCH_TARGET)

    def get_and_match(self):
        """
        Take a color reading and match it to our list of targets.
        Return the detected color values and its closest match in a tuple.
        return value: (detected_color, closest_color)
        """
        detected_color = self.colorSensor.getColor() # color is an object with three fields for the different colors
        confidence = 0.0 # "confidence" is a dummy variable for Python.  The C function "matchClosestColor()"
                         # modifies confidence to return a value for the current computation, but Python can't modify parameters like that.
        matched_color = self.colormatcher.matchClosestColor(detected_color, confidence)
        return (detected_color, matched_color) # Note we are returning a tuple, with two values.

###############################################

class Color_Password():
    """
    A class that performs a password function based on showing colors to the sensor.
    After initialization, call the check() method from robot.py's telop_periodic().
    This password is hard coded into the check() function: blue, purple, yellow with no gaps between.
    """

    class PWDStates(enum.Enum):
        """
        A set of legal states for the state machine that searches for a password.
        This "inner class" is only used by class Color_Password.
        Note that although we have integer values as part of the definition, you can't
        treat them like integers:  PWDStates.WAITING + PWDStates.FIRST_COLOR is invalid.
        To create an enumeration, you subclass enum.Enum, and define member values.
        See comment in __init__() about why we chose to use an enumeration.
        See also https://docs.python.org/3/library/enum.html.
        """
        WAITING = 0           # Waiting to detect the first color of the 3-color password.
        FIRST_COLOR = 1       # First color detected.
        SECOND_COLOR = 2      # Second color detected.
        PASSWORD_COMPLETE = 3 # All three colors have been seen in order.

    def __init__(self):
        """The __init__() method gets called when an object of a class is created."""

        # REV Robotics color sensor creation and configuration, including a color matching object.
        # Product is: https://www.revrobotics.com/rev-31-1557/.  This page has a link to the Java/C++ APIs.
        # Presently (2020-05-04), the RobotPy documentation is limited.
        self.colorSensor = ColorSensorV3(wpilib.I2C.Port.kOnboard)

        # A ColorMatch object has methods to check for matching colors.
        self.colormatcher = ColorMatch()
        # Add our target values to colormatcher
        self.colormatcher.addColorMatch(BLUE_TARGET)
        self.colormatcher.addColorMatch(PURPLE_TARGET)
        self.colormatcher.addColorMatch(PINK_TARGET)
        self.colormatcher.addColorMatch(YELLOW_TARGET)
        self.colormatcher.addColorMatch(BENCH_TARGET)

        # A state variable to keep track of how much of the password has been entered.
        # The state could be represented many ways:
        #   integers: 0 represents "waiting", 1 represents "first color seen", ...
        #   named constant integers: WAITING = 0, FIRST_COLOR = 1, ...
        #   strings that describe the state: "waiting", "first color", ...
        #   an enumeration, which is what we are doing here.  Enumerations allow you to define
        #     a unique set of constant values.  Because they are unique, they are less susceptible
        #     to typos than any of the other options above.
        self.pwd_state = self.PWDStates.WAITING # Start waiting for the first color in the sequence.

    def check(self):
        """
        Call this method from teleop_periodic().  It will check the color and progress through
        a state machine that keeps track of how much of the password has been entered.  The password
        must be entered by switching directly between colors.  If the sensor detects a background
        color between the valid colors, it will reset to the initial "waiting" state.
        This can be a problem because if there are two colors visible to the sensor, it might match
        a third color.  (Rod's blue and lab bench can read as purple.)

        :return: (password_complete, detected_color, matched_color) - a tuple with a boolean and a two color objects
                  password_complete: True if all 3 colors were seen in order.
                  detected_color: the actual RGB values seen by the sensor at the moment.
                  matched_color: the closest color matched.
        """
        password_complete = False # Initialize this temporary value.  Only change it if the password has been found.
        detected_color = self.colorSensor.getColor() # color is an object with three fields for the different colors
        confidence = 0.0 # "confidence" is a dummy variable for Python.  The C function "matchClosestColor()"
                         # modifies confidence to return a value for the current computation, but Python can't modify parameters like that.
        matched_color = self.colormatcher.matchClosestColor(detected_color, confidence)

        # Do something different depending on what state the password detection process is in. The options are
        # generally: reset to WAITING, stay in same state, and progress to the next one.
        if self.pwd_state == self.PWDStates.WAITING:
            # From waiting, only the first color of the password matters.
            if is_equal_color(matched_color, BLUE_TARGET):
                self.pwd_state = self.PWDStates.FIRST_COLOR
                print('Blue found.') # Print for diagnostics.

        elif self.pwd_state == self.PWDStates.FIRST_COLOR:
            if is_equal_color(matched_color, PURPLE_TARGET):
                # Found the second color of the password.
                self.pwd_state = self.PWDStates.SECOND_COLOR
                print('Purple found.')  # Print for diagnostics.
            elif not is_equal_color(matched_color, BLUE_TARGET):
                # If the color were still blue, we would stay in the FIRST_COLOR state,
                # but it isn't, so reset to waiting.
                self.pwd_state = self.PWDStates.WAITING
                print('Found was not blue or purple: {:5.3f}, {:5.3f}, {:5.3f}; resetting.'.format(detected_color.red, detected_color.green, detected_color.blue))  # Print for diagnostics.

        elif self.pwd_state == self.PWDStates.SECOND_COLOR:
            if is_equal_color(matched_color, YELLOW_TARGET):
                # Found the third and final color of the password.
                self.pwd_state = self.PWDStates.PASSWORD_COMPLETE
                password_complete = True # Change the return value to signal password has been found.
                print('Yellow found; password found.')  # Print for diagnostics.
            elif not is_equal_color(matched_color, PURPLE_TARGET):
                # If the color were still yellow, we would stay in the SECOND_COLOR state,
                # but it isn't, so reset to waiting.
                self.pwd_state = self.PWDStates.WAITING
                print('Found was not purple or yellow: {:5.3f}, {:5.3f}, {:5.3f}; resetting.'.format(detected_color.red, detected_color.green, detected_color.blue))  # Print for diagnostics.

        elif self.pwd_state == self.PWDStates.PASSWORD_COMPLETE:
            if is_equal_color(matched_color, YELLOW_TARGET):
                # Still seeing yellow, password is still complete; signal that.
                password_complete = True
            else:
                self.pwd_state = self.PWDStates.WAITING
                print('Waiting for new password.')  # Print for diagnostics.

        else:
            # It is always a good idea to have a catch-all, in case someone accidentally assigns an incorrect
            # value to self.pwd_state, for instance a string.
            print('Color_Password.check(): invalid state:', self.pwd_state) # Print an error message (there are other ways to handle errors).
            self.pwd_state = self.PWDStates.WAITING  # Reset to the initial state.

        return (password_complete, detected_color, matched_color) # We are returning a tuple, with three values.

###############################################

class Color_Password2():
    """
    A class that performs a password function based on showing colors to the sensor.
    The interface is similar to Color_Password, except that the password is initialized
    with a list of password colors, and can be arbitrarily long.

    After initialization, call the check() method from robot.py's telop_periodic().
    """

    def __init__(self, pwd=[BLUE_TARGET, PURPLE_TARGET, YELLOW_TARGET]):
        """
        Use an optional parameter to initialize the password list.  The default value,
        given above, is used if no parameter is supplied.

        :param pwd: list of wpilib.Color objects for the password. Must have at least 2 elements.
        """
        # Validate the supplied password.
        if len(pwd) == 0 or len(pwd) == 1:
            self.pwd_list = [BLUE_TARGET, PURPLE_TARGET, YELLOW_TARGET] # Use the default if the list is too short.
        else:
            self.pwd_list = pwd # Otherwise save the parameter into a member variable.

        # A state variable to keep track of how much of the password has been entered.
        # Because the password is kept in a list, it is convenient to use an index into the list.
        # The index points to the _next_ color we are looking for, so 0 means the initial color of
        # the password has not been found.
        self.pwd_index = 0

        # REV Robotics color sensor creation and configuration, including a color matching object.
        # Product is: https://www.revrobotics.com/rev-31-1557/.  This page has a link to the Java/C++ APIs.
        # Presently (2020-05-04), the RobotPy documentation is limited.
        self.colorSensor = ColorSensorV3(wpilib.I2C.Port.kOnboard)

        # A ColorMatch object has methods to check for matching colors.
        self.colormatcher = ColorMatch()
        # Add our target values to colormatcher
        self.colormatcher.addColorMatch(BLUE_TARGET)
        self.colormatcher.addColorMatch(PURPLE_TARGET)
        self.colormatcher.addColorMatch(PINK_TARGET)
        self.colormatcher.addColorMatch(YELLOW_TARGET)
        self.colormatcher.addColorMatch(BENCH_TARGET)

    def check(self):
        """
        Call this method from teleop_periodic().  It will check the color and progress through
        a state machine that keeps track of how much of the password has been entered.  The password
        must be entered by switching directly between colors.  If the sensor detects a background
        color between the valid colors, it will reset to the initial "waiting" state.
        This can be a problem because if there are two colors visible to the sensor, it might match
        a third color.  (Rod's blue and lab bench can read as purple.)

        :return: (password_complete, detected_color, matched_color) - a tuple with a boolean and a two color objects
                  password_complete: True if all 3 colors were seen in order.
                  detected_color: the actual RGB values seen by the sensor at the moment.
                  matched_color: the closest color matched.
        """
        password_complete = False # Initialize this temporary value.  Only change it if the password has been found.
        detected_color = self.colorSensor.getColor() # color is an object with three fields for the different colors
        confidence = 0.0 # "confidence" is a dummy variable for Python.  The C function "matchClosestColor()"
                         # modifies confidence to return a value for the current computation, but Python can't modify parameters like that.
        matched_color = self.colormatcher.matchClosestColor(detected_color, confidence)

        # Do something different depending on what state the password detection process is in. The options are
        # generally: reset to WAITING, stay in same state, and progress to the next one.
        if self.pwd_index == 0:
            # Handle the initial state differently than the rest.
            if is_equal_color(matched_color, self.pwd_list[self.pwd_index]):
                print('Color {} found.'.format(self.pwd_index))
                self.pwd_index += 1 # Increment index so that next time we will check for the next color.

        elif self.pwd_index == len(self.pwd_list):
            # Also handle the "found" case differently, because we cannot index beyond the end of the list.
            if is_equal_color(matched_color, self.pwd_list[self.pwd_index-1]):
                password_complete = True
            else:
                self.pwd_index = 0 # A new color that isn't the end has been observed; reset the password checker.
                print('Waiting for new password.')  # Print for diagnostics.

        elif self.pwd_index > len(self.pwd_list):
            # It is always a good idea to have a catch-all, in case someone accidentally assigns an incorrect
            # value to self.pwd_index, in this case longer than the length of the list.
            print('Color_Password2.check(): invalid state:', self.pwd_index)  # Print an error message (there are other ways to handle errors).
            self.pwd_index = 0  # Reset to the initial state.

        else:
            # Handle the rest of the cases, somewhere in the middle of the password.
            if is_equal_color(matched_color, self.pwd_list[self.pwd_index]):
                print('Color {} found.'.format(self.pwd_index))
                self.pwd_index += 1 # Increment index so that next time we will check for the next color.
                if self.pwd_index == len(self.pwd_list):
                    password_complete = True # Signal we found the last one.
                    print('Password found.')
            elif not is_equal_color(matched_color, self.pwd_list[self.pwd_index-1]):
                # We compare to the value for index-1, meaning the color previously found (no change)
                # The reason we treat the index==0 case differently is because we don't want
                # to use -1 as an index.
                print('Found an invalid color {:5.3f}, {:5.3f}, {:5.3f}; resetting.'.format(detected_color.red, detected_color.green, detected_color.blue))
                self.pwd_index = 0

        return (password_complete, detected_color, matched_color) # We are returning a tuple, with three values.
