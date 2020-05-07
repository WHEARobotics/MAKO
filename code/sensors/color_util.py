"""
    Utilities and classes to handle color functions.
"""

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

# Some helper functions for the module.
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
            Return the detected color and its closest match in a tuple.
        """
        detected_color = self.colorSensor.getColor() # color is an object with three fields for the different colors
        confidence = 0.0 # "confidence" is a dummy variable for Python.  The C function "matchClosestColor()"
                         # modifies confidence to return a value for the current computation, but Python can't modify parameters like that.
        matched_color = self.colormatcher.matchClosestColor(detected_color, confidence)
        return (detected_color, matched_color) # Note we are returning a tuple, with two values.


