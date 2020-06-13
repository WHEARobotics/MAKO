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
import pixy2api.links.spilink

# Next steps:
# Implement Link and SPILink. Java version has two-stage initialization/open/close.  Python SPI/I2C/SerialPort have no close() method.
#    We can simplify by just passing link type and link arg to the Pixy constructor.
#    One good thing about Pixy2.init() is that it tries to connect to the link, and if timeout, returns an error code.
#    But it might be better to just raise an execption and catch it in main code.  Examples don't use the errors.
#    Or do all the object creation in Pixy2.__init__() (and the link __inits__), and then call Pixy2.init() to try to connect, read version.
# Implement checksum verification.
# Create the Version class.

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
                            I2C: 0 (or anything else) for the on-board I2C, 1 for the MXP connector.
                            UART: 0 for onboard, 1-3 for USB, 4 for MXP connector.
        """
        if link_type == Pixy2.LinkType.SPI:
            self.link = pixy2api.links.spilink.SPILink(link_sel)
        # elif link_type == Pixy2.LinkType.I2C:
        #     self.link = links.I2CLink(link_arg)
        # else:
        #     # link_type == Pixy2.LinkType.UART
        #     self.link = links.UARTLink(link_arg)

        # Stuff from my initial proof-of-concept code
        #self.spi = wpilib.SPI(wpilib.SPI.Port.kOnboardCS0)
        self.response_buffer = bytearray(Pixy2.PIXY_BUFFERSIZE + Pixy2.PIXY_SEND_HEADER_SIZE)

        # Stuff from Java port
#        self.link = link
        self.length = 0 # Object global that sets the length of data sent to Pixy2.
        self.type = 0   # Command type sent to Pixy2.
        # Initializes send/return buffer and payload buffer
#        buffer = bytearray(PIXY_BUFFERSIZE + PIXY_SEND_HEADER_SIZE)
        self.payload_buffer = bytearray(Pixy2.PIXY_BUFFERSIZE)
        # Initializes tracker objects.
        # self.ccc = Pixy2CCC(self)
        # self.line = Pixy2Line(self)
        # self.video = Pixy2Video(self)

    def init(self):
        """Begins communication with Pixy2.  Call before doing any operations.
        If successful, keeps track of the hardware/firmware version on the Pixy2.
        :returns Pixy2 error code."""
        timeout = wpilib.Timer()
        timeout.start()
        while (not timeout.hasElapsed(5)):
            # Try for 5 seconds.
            if (self.getVersion() >= 0):
                #self.getResolution()
                # TODO: implement getResolution()
                return Pixy2.PIXY_RESULT_OK
            time.sleep(0.000025) # 25 microcseconds
        return Pixy2.PIXY_RESULT_ERROR

    def getVersion(self):
        """Get Pixy2 version and store in self.version; return error -- mashing everything together for a first attempt."""
        self.length = 0
        self.type = Pixy2.PIXY_TYPE_REQUEST_VERSION
        self.sendPacket()
        res = self.receivePacket()
        if res == Pixy2.PIXY_RESULT_OK: # TODO: suggest that the constant be used in the Java version, rather than 0.
            # Diagnostics:
            print(res, self.response_buffer)
            if self.type == Pixy2.PIXY_TYPE_RESPONSE_VERSION:
                self.version = Pixy2.Version(self.response_buffer)
                self.version.print()
                return self.length  # Success
            elif type == Pixy2.PIXY_TYPE_RESPONSE_ERROR:
                return Pixy2.PIXY_RESULT_BUSY
        return Pixy2.PIXY_RESULT_ERROR # Some kind of bitstream error


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
        write_buffer[4:] = self.payload_buffer[0:self.length] # TODO: need to copy in the self.payload_buffer.
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
            print(buf)
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
            print(buf)
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
            print(self.to_string())

        def to_string(self):
            """Create a string from the version info.
            :returns the string"""
            return 'hardwar ver: 0x{} firmware ver: {}.{}.{} {}'.format(self.hardware, self.firmware_major, self.firmware_minor, self.firmware_build, self.firmware_type)

        def get_hardware(self):
            """Get hardware info.
            :returns hardware version as an integer."""
            return self.hardware

        def get_firmware_major(self):
            """Get firmware info.
            :returns firmware major version as an integer."""
            return self.firmware_major

        def get_firmware_minor(self):
            """Get firmware info.
            :returns firmware minor version as an integer."""
            return self.firmware_minor

        def get_firmware_build(self):
            """Get firmware info.
            :returns firmware build number as an integer."""
            return self.firmware_build

        def get_firmware_type_string(self):
            """Get firmware type info.
            :returns firmware type as a string."""
            return self.firmware_type
