# !/usr/bin/env python3
"""
    Python port of the Pixy2 FRC Java library, which was ported from Pixy2 Arduino.
    Interfaces with the Pixy2 over any provided, compatible link.

    Java port by PseudoResonance (Josh Otake), https://github.com/PseudoResonance/Pixy2JavaAPI

 *         ORIGINAL HEADER -
 *         https://github.com/charmedlabs/pixy2/blob/master/src/host/arduino/libraries/Pixy2/TPixy2.h
 *         ==========================================================================================
 *         begin license header
 *
 *         This file is part of Pixy CMUcam5 or "Pixy" for short
 *
 *         All Pixy source code is provided under the terms of the GNU General
 *         Public License v2 (http://www.gnu.org/licenses/gpl-2.0.html). Those
 *         wishing to use Pixy source code, software and/or technologies under
 *         different licensing terms should contact us at cmucam@cs.cmu.edu.
 *         Such licensing terms are available for all portions of the Pixy
 *         codebase presented here.
 *
 *         end license header
 *
 *         Main Pixy template class. This class takes a link class and uses it
 *         to communicate with Pixy over I2C, SPI, UART or USB using the Pixy
 *         packet protocol.

"""

import enum, time
import wpilib
import pixy2api.pixy2ccc
import pixy2api.links.spilink

# Next steps:
# Test color connected components with more than one object.
# Implement & test the line following class.
# Implement the "changeProg" method so we can start the line follower.
# Implement & test the video class to get the color at an individual pixel.
# Other stuff: servos; I2C and UART links
# Test camera brightness.


class Pixy2(object):
    PIXY_BUFFERSIZE = 0x104
    PIXY_SEND_HEADER_SIZE = 4
    PIXY_MAX_PROGNAME = 33
    PIXY_DEFAULT_ARGVAL = 0x80000000
    PIXY_CHECKSUM_SYNC = 0xc1af
    PIXY_NO_CHECKSUM_SYNC = 0xc1ae

    # Packet types
    PIXY_TYPE_REQUEST_CHANGE_PROG = 0x02
    PIXY_TYPE_REQUEST_RESOLUTION = 0x0c
    PIXY_TYPE_RESPONSE_RESOLUTION = 0x0d
    PIXY_TYPE_REQUEST_VERSION = 0x0e
    PIXY_TYPE_RESPONSE_VERSION = 0x0f
    PIXY_TYPE_RESPONSE_RESULT = 0x01
    PIXY_TYPE_RESPONSE_ERROR = 0x03
    PIXY_TYPE_REQUEST_BRIGHTNESS = 0x10
    PIXY_TYPE_REQUEST_SERVO = 0x12
    PIXY_TYPE_REQUEST_LED = 0x14
    PIXY_TYPE_REQUEST_LAMP = 0x16
    PIXY_TYPE_REQUEST_FPS = 0x18

    # Return result values
    PIXY_RESULT_OK = 0
    PIXY_RESULT_ERROR = -1
    PIXY_RESULT_BUSY = -2
    PIXY_RESULT_CHECKSUM_ERROR = -3
    PIXY_RESULT_TIMEOUT = -4
    PIXY_RESULT_BUTTON_OVERRIDE = -5
    PIXY_RESULT_PROG_CHANGING = -6

    # RC - servo values
    PIXY_RCS_MIN_POS = 0
    PIXY_RCS_MAX_POS = 1000
    PIXY_RCS_CENTER_POS = ((PIXY_RCS_MAX_POS - PIXY_RCS_MIN_POS) / 2)

    class LinkType(enum.Enum):
        SPI = 0
        I2C = 1
        UART = 2

    def __init__(self, link_type, link_sel = 0):
        """Constructs Pixy2 object with link type and selection of which of that type.
        :argument link_type one of variants of the LinkType enumeration.
        :argument link_sel  An integer to select which SPI chip select, I2C port, or UART port to use.
                            SPI: 0-3 for CS0-3 on the roboRIO's main SPI port, 4 for the roboRIO MXP connector.
                                 For CS0-3, configure Pixy2 to use SPI with SS. (slave select, AKA chip select, or CS).  Connect CS to the main port's CSx.
                                 For MXP, configure Pixy2 to use "Arduino ICSP SPI" (which doesn't use a chip select).  Leave the CS pin disconnected.
                            I2C: 0 (or anything else) for the on-board I2C, 1 for the MXP connector.
                            UART: 0 for onboard, 1-3 for USB, 4 for MXP connector.
        Call init() after creation and before anything else to start communication with Pixy2.
        """
        if link_type == Pixy2.LinkType.SPI:
            self.link = pixy2api.links.spilink.SPILink(link_sel)
        # elif link_type == Pixy2.LinkType.I2C:
        #     self.link = links.I2CLink(link_arg)
        # else:
        #     # link_type == Pixy2.LinkType.UART
        #     self.link = links.UARTLink(link_arg)

        self.length = 0 # Object global that sets the length of data sent to Pixy2.
        self.type = 0   # Command type sent to Pixy2.
        self.frame_height = 0
        self.frame_width = 0
        self.version = None  # Start with an empty version.
        # Initializes send/return buffer and payload buffer
        self.response_buffer = bytearray(Pixy2.PIXY_BUFFERSIZE + Pixy2.PIXY_SEND_HEADER_SIZE)
        self.payload_buffer = bytearray(Pixy2.PIXY_BUFFERSIZE)
        # Initializes tracker objects.
        self.ccc = pixy2api.pixy2ccc.Pixy2CCC(self)
        # self.line = Pixy2Line(self)
        # self.video = Pixy2Video(self)

    #--------------------------------------------------------------------------------------
    # Methods that are part of the public interface.

    def init(self):
        """Begins communication with Pixy2.  Call before doing any operations.
        If successful, keeps track of the hardware/firmware version on the Pixy2.
        :returns Pixy2 error code.
        """
        timeout = wpilib.Timer()
        timeout.start()
        while (not timeout.hasElapsed(5)):
            # Try for 5 seconds.
            if (self.getVersion() >= 0):
                self.getResolution()
                print('resolution: {} x {}'.format(self.frame_width, self.frame_height))
                return Pixy2.PIXY_RESULT_OK
            time.sleep(0.000025) # 25 microcseconds
        return Pixy2.PIXY_RESULT_ERROR

    def getVersion(self):
        """Get Pixy2 version and store in self.version; return error -- mashing everything together for a first attempt.
        :returns PIXY result/error code.
        """
        self.length = 0
        self.type = Pixy2.PIXY_TYPE_REQUEST_VERSION
        self.sendPacket()
        res = self.receivePacket()
        if res == Pixy2.PIXY_RESULT_OK: # TODO: suggest that the constant be used in the Java version, rather than 0.
            # Diagnostics:
            # print(res, self.response_buffer)
            if self.type == Pixy2.PIXY_TYPE_RESPONSE_VERSION:
                self.version = Pixy2.Version(self.response_buffer)
                self.version.print()
                return self.length  # Success
            elif type == Pixy2.PIXY_TYPE_RESPONSE_ERROR:
                return Pixy2.PIXY_RESULT_BUSY
        return Pixy2.PIXY_RESULT_ERROR # Some kind of bitstream error

    def getVersionInfo(self):
        """Gets stored Pixy2 Version info, or retrieves it if not present.
        :returns - a Pixy2.Version object"""

    def getResolution(self):
        """Get the camera resolution from the Pixy2 and store it in object variables.
        :returns PIXY result/error code.
        """
        self.length = 1
        self.payload_buffer[0] = 0 # Adds empty byte to payload as placeholder for future queries.
        self.type = Pixy2.PIXY_TYPE_REQUEST_RESOLUTION
        self.sendPacket()
        res = self.receivePacket()
        if res == Pixy2.PIXY_RESULT_OK: # TODO: suggest that the constant be used in the Java version, rather than 0.
            if self.type == Pixy2.PIXY_TYPE_RESPONSE_RESOLUTION:
                self.frame_width = ((self.response_buffer[1] & 0xFF) << 8) | (self.response_buffer[0] & 0xFF)
                self.frame_height = ((self.response_buffer[3] & 0xFF) << 8) | (self.response_buffer[2] & 0xFF)
                return Pixy2.PIXY_RESULT_OK
            else:
                return Pixy2.PIXY_RESULT_ERROR
        else:
            return Pixy2.PIXY_RESULT_ERROR

    def getFrameWidth(self):
        """Get the width of the Pixy's visual frame after initialization.
        prerequisite - must have called init().
        """
        return self.frame_width

    def getFrameHeight(self):
        """Get the height of the Pixy's visual frame after initialization.
        prerequisite - must have called init().
        """
        return self.frame_height

    def getCCC(self):
        """Get Pixy2 Color Connected Components tracker."""
        return self.ccc

    # TODO: need to implement these classes so we can have them to return.
    def getLine(self):
        """Get Pixy2 line tracker."""
        return self.line

    def getVideo(self):
        """Get Pixy2 video tracker."""
        return self.video

    def changeProg(self, prog):
        """Sends change program packet to Pixy2.
        From the Pixy wiki: https://docs.pixycam.com/wiki/doku.php?id=wiki:v2:ccc_api#member-functions
        "Firmware versions 3.0.11 and greater will automatically switch to the color_connected_components program when making requests through the color connected components API."
        Therefore, I haven't implemented this function yet.
        """
        # TODO: implement this method.
        pass

    def setCameraBrightness(self, brightness):
        """Sets Pixy2 camera brightness between 0-255.
        :param brightness - integer 0-255 representing camera brightness.
        :returns Pixy2 error code.
        """
        # Set up the data for the call to Pixy2.
        self.payload_buffer[0] = self.clip_unsigned_byte(int(brightness))
        self.length = 1 # One byte to send.
        self.type = Pixy2.PIXY_TYPE_REQUEST_BRIGHTNESS
        self.sendPacket()
        res = self.receivePacket()
        # TODO: suggest that the constant be used in the Java version, rather than 0 in the "if" below.
        if res == Pixy2.PIXY_RESULT_OK and self.type == Pixy2.PIXY_TYPE_RESPONSE_RESULT and self.length == 4:
            res = ((self.response_buffer[3] & 0xFF) << 24) | ((self.response_buffer[2] & 0xFF) << 16) \
                  | ((self.response_buffer[1] & 0xFF) << 8) | (self.response_buffer[0] & 0xFF)
            return res
        else:
            return Pixy2.PIXY_RESULT_ERROR

    def setServos(self, pan, tilt):
        """Sets Pixy2 servo positions between 0-1000.
        :param pan  - integer 0-1000 for pan servo position.
        :param tilt - integer 0-1000 for tilt servo position.
        :returns Pixy2 error code.
        """
        # TODO: implement
        pass

    # TODO: I initially saw some odd behavior.  Now not reproducing it. Here is what I saw:
    # red 128 (128,0,0) -> LED was green
    # green 128 (0,128,0) -> blue
    # green 64 (0,64,0) -> magenta???
    # blue 128 (0,0,128)-> yellow
    # sometimes... it seems inconsistent.

    def setLED(self, color=None, rgb=None, red=255, green=255, blue=255):
        """Set the LED to a specified color, using one of three parameter types.  Choose between
        :param color - a wpilib.Color object with fields red, green, blue.  If more than one set of
                       optional parameters are supplied, this one is prioritized.  Note that Color
                       objects use floats in the range 0-1 to represent the red, green, and blue values.
        :param rgb   - a 24-bit (or more, but the rest will be ignored) unsigned integer, where the
                       the least significant byte is blue, the next is green, and the highest is red.
        :param red
        :param green
        :param blue - This set must be supplied together, or the default will be used 0-255 for each.
        :returns Pixy2 error code.
        """
        # Choose which color type to use.
        if color is not None:
            r = self.clip_unsigned_byte(int(color.red * 256))
            g = self.clip_unsigned_byte(int(color.green * 256))
            b = self.clip_unsigned_byte(int(color.blue * 256))
        elif rgb is not None:
            r = (rgb >> 16) & 0xFF
            g = (rgb >> 8) & 0xFF
            b = rgb & 0xFF
        else:
            # Since default values are defined, there should always be something to use.
            r = self.clip_unsigned_byte(red)
            g = self.clip_unsigned_byte(green)
            b = self.clip_unsigned_byte(blue)

        # Set up the data for the call to Pixy2.
        self.payload_buffer[0] = r
        self.payload_buffer[1] = g
        self.payload_buffer[2] = b
        self.length = 3 # Three bytes to send.
        self.type = Pixy2.PIXY_TYPE_REQUEST_LED
        self.sendPacket()
        res = self.receivePacket()
        # TODO: suggest that the constant be used in the Java version, rather than 0 in the "if" below.
        if res == Pixy2.PIXY_RESULT_OK and self.type == Pixy2.PIXY_TYPE_RESPONSE_RESULT and self.length == 4:
            res = ((self.response_buffer[3] & 0xFF) << 24) | ((self.response_buffer[2] & 0xFF) << 16) \
                  | ((self.response_buffer[1] & 0xFF) << 8) | (self.response_buffer[0] & 0xFF)
            return res
        else:
            return Pixy2.PIXY_RESULT_ERROR

    def clip_unsigned_byte(self, input):
        """Limits the input integer to the range of an unsigned byte (0-255).
        :param input - integer (or if a float, coerced to an integer).
        :returns the value clipped to the range 0-255.
        """
        retval = int(input)
        if retval > 255:
            retval = 255
        elif retval < 0:
            retval = 0
        return retval

    def setLamp(self, white_on, rgb_on):
        """Turn Pixy2 light sources on or off.
        :param white_on - for the white light source: 1 for on, 0 for off.
        :param rgb_on   - for the RGB color LED: 1 for on, 0 for off.
        :returns positive integer for success, or Pixy2 error code.
        """
        self.length = 2
        self.payload_buffer[0] = white_on & 0xFF
        self.payload_buffer[1] = rgb_on & 0xFF
        self.type = Pixy2.PIXY_TYPE_REQUEST_LAMP
        self.sendPacket()
        res = self.receivePacket()
        # TODO: suggest that the constant be used in the Java version, rather than 0 in the "if" below.
        if res == Pixy2.PIXY_RESULT_OK and self.type == Pixy2.PIXY_TYPE_RESPONSE_RESULT and self.length == 4:
            res = ((self.response_buffer[3] & 0xFF) << 24) | ((self.response_buffer[2] & 0xFF) << 16) \
                  | ((self.response_buffer[1] & 0xFF) << 8) | (self.response_buffer[0] & 0xFF)
            return res
        else:
            return Pixy2.PIXY_RESULT_ERROR

    def getFPS(self):
        """Gets Pixy2 camera framerate between 2-62 fps.
        :returns framerate or Pixy2 error code.
        """
        self.length = 0 # No arguments.
        self.type = Pixy2.PIXY_TYPE_REQUEST_FPS
        self.sendPacket()
        res = self.receivePacket()
        # TODO: suggest that the constant be used in the Java version, rather than 0 in the "if" below.
        if res == Pixy2.PIXY_RESULT_OK and self.type == Pixy2.PIXY_TYPE_RESPONSE_RESULT and self.length == 4:
            res = ((self.response_buffer[3] & 0xFF) << 24) | ((self.response_buffer[2] & 0xFF) << 16) \
                  | ((self.response_buffer[1] & 0xFF) << 8) | (self.response_buffer[0] & 0xFF)
            return res
        else:
            return Pixy2.PIXY_RESULT_ERROR


    #--------------------------------------------------------------------------------------
    # Methods that are not intended as part of the public interface.
    # I have kept the Java names for consistency, rather than prefix the names with "_".

    def getSync(self):
        """Looks for Pixy2 communication synchronization bytes to find the start of message.
        Side effect: sets self.m_cs to denote whether this is a checksum packet (True) or not.
        :returns PIXY_RESULT_OK if sync found, or PIXY_RESULT_ERROR if not.
        """
        c = bytearray(1) # A single character
        attempts = 0
        cprev = 0
        i = 0
        while(True):
            res = self.link.receive(c)
            if res >= Pixy2.PIXY_RESULT_OK:
                ret = c[0] & 0xFF
                # Since we're using little endian, previous byte is least significant byte.
                start = cprev
                # Current byte is most significant byte.
                start |= ret << 8
                cprev = ret
                if start == Pixy2.PIXY_CHECKSUM_SYNC:
                    self.m_cs = True
                    return Pixy2.PIXY_RESULT_OK
                if start == Pixy2.PIXY_NO_CHECKSUM_SYNC:
                    self.m_cs = False
                    return Pixy2.PIXY_RESULT_OK
            if i >= 4:
                if attempts >= 4:
                    return Pixy2.PIXY_RESULT_ERROR
                time.sleep(0.000025) # Sleep for 25 microseconds.
                attempts += 1
                i = 0
            i += 1

    def sendPacket(self):
        """Sends packet to Pixy2.  Need to set self.type and self.length beforehand, as well as putting data in self.payload_buffer."""
        write_buffer = bytearray(Pixy2.PIXY_SEND_HEADER_SIZE + self.length) # For Python functions (vs. Java), need to set the buffer the length of the data.
        write_buffer[0] = (Pixy2.PIXY_NO_CHECKSUM_SYNC & 0xff)
        write_buffer[1] = ((Pixy2.PIXY_NO_CHECKSUM_SYNC >> 8) & 0xff)
        write_buffer[2] = self.type
        write_buffer[3] = self.length
        write_buffer[4:] = self.payload_buffer[0:self.length] # Copy in the self.payload_buffer.
        return self.link.send(write_buffer)

    def receivePacket(self):
        """Receives a packet from Pixy2 and puts it in the object global response_buffer for further processing."""
        res = self.getSync() # Search for the syncronization word, and also decide if it represents a checksum-type packet.
        if res < 0:
            return res
        if self.m_cs:
            # Checksum sync
            cs_calc = Pixy2.Checksum()
            buf = bytearray(4) # Checksum packets have 4 bytes.
            # This reads in the length of the buffer.
            res = self.link.receive(buf)
#            print(buf)
            if res < 0:
                return res
            self.type = buf[0] & 0xFF
            self.length = buf[1] & 0xFF
            csSerial = ((buf[3] & 0xFF) << 8) | (buf[2] & 0xFF)
            buf = bytearray(self.length)
            res = self.link.receive(buf, cs_calc)
            if res < 0:
                return res
            if csSerial != cs_calc.get():
#                print('Checksum calc failed.')
                return Pixy2.PIXY_RESULT_CHECKSUM_ERROR
        else:
            # Not a checksum sync.
            buf = bytearray(2) # Non-Checksum packet headers have only 2 bytes.
            res = self.link.receive(buf)
#            print(buf)
            if res < 0:
                return res
            self.type = buf[0] & 0xFF
            self.length = buf[1] & 0xFF
            buf = bytearray(self.length)
            res = self.link.receive(buf)
            if res < 0:
                return res
        # If execution has reached here, there have been no errors to cause early return.
        self.response_buffer[0:self.length] = buf[:] # Put the response into the buffer.
        return Pixy2.PIXY_RESULT_OK

    #--------------------------------------------------------------------------------------
    # Inner classes that are part of the public interface.
    # I have kept the Java names for consistency.

    class Version(object):
        """Class to parse and hold Pixy2 version info."""
        def __init__(self, version_buffer):
            """Creates version object.
            :param version_buffer - bytearray of version info returned from Pixy2."""
            self.hardware = ((version_buffer[1] & 0xFF) << 8) | (version_buffer[0] & 0xFF)
            self.firmware_major = version_buffer[2]
            self.firmware_minor = version_buffer[3]
            self.firmware_build = ((version_buffer[5] & 0xFF) << 8) | (version_buffer[4] & 0xFF)
            self.firmware_type = version_buffer[6:16].decode() # decode() decodes the bytes into a Unicode string, default encoding is utf-8.

        def print(self):
            """Print version info to the console."""
            print(self.toString())

        def toString(self):
            """Create a string from the version info.
            :returns the string"""
            return 'hardware ver: 0x{} firmware ver: {}.{}.{} {}'.format(self.hardware, self.firmware_major, self.firmware_minor, self.firmware_build, self.firmware_type)

        def getHardware(self):
            """Get hardware info.
            :returns hardware version as an integer."""
            return self.hardware

        def getFirmwareMajor(self):
            """Get firmware info.
            :returns firmware major version as an integer."""
            return self.firmware_major

        def getFirmwareMinor(self):
            """Get firmware info.
            :returns firmware minor version as an integer."""
            return self.firmware_minor

        def getFirmwareBuild(self):
            """Get firmware info.
            :returns firmware build number as an integer."""
            return self.firmware_build

        def getFirmwareTypeString(self):
            """Get firmware type info.
            :returns firmware type as a string."""
            return self.firmware_type

    #--------------------------------------------------------------------------------------
    # Inner classes that are not intended as part of the public interface.
    # I have kept the Java names for consistency, rather than prefix the names with "_".
    # However, I have changed the classes' method names to either simpler or more Pythonic (snake_case)
    # names since they are not intended to be public.

    class Checksum(object):
        """Class to hold checksums."""

        def __init__(self):
            self.cs = 0

        def update(self, b):
            """Add a byte to the checksum.  Call this with each byte in the response in sequence."""
            self.cs += b

        def get(self):
            return self.cs

        def reset(self):
            self.cs = 0

