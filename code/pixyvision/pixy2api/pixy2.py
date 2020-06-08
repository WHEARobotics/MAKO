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

class Pixy2():
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

    def __init__(self, link):
        """Constructs Pixy2 object wit supplied communication link."""
        # Stuff from my initial proof-of-concept code
        self.spi = wpilib.SPI(wpilib.SPI.Port.kOnboardCS0)
        self.response_buffer = bytearray(Pixy2.PIXY_BUFFERSIZE + Pixy2.PIXY_SEND_HEADER_SIZE)

        # Stuff from Java port
        self.link = link
        self.length = 0 # Object global that sets the length of data sent to Pixy2.
        self.type = 0   # Command type sent to Pixy2.
        # Initializes send/return buffer and payload buffer
#        buffer = bytearray(PIXY_BUFFERSIZE + PIXY_SEND_HEADER_SIZE)
#        buffer_payload = bytearray(PIXY_BUFFERSIZE)
        # Initializes tracker objects.
        # self.ccc = Pixy2CCC(self)
        # self.line = Pixy2Line(self)
        # self.video = Pixy2Video(self)

    # def init(self, argument):
    #     """Initializes Pixy2 and waits for startup to complete
    #        @param argument Argument to setup {@link Link}"""
    #     # Opens link
    #     ret = self.link.open(argument)
    #     if ret >= 0:
    #         # Tries to connect, times out if unable to communicate after 5 seconds.
    #         #for
    #         pass

    def getVersion(self):
        """Get Pixy2 version and store in self.version; return error -- mashing everything together for a first attempt."""
        self.length = 0
        self.type = Pixy2.PIXY_TYPE_REQUEST_VERSION
        self.sendPacket()
        res = self.receivePacket()
        # Diagnostics:
        print(res, self.response_buffer)

        # TODO: create the Version class and use this code below.
    #     if self.receivePacket() == Pixy2.PIXY_RESULT_OK: # TODO: suggest that the constant be used in the Java version, rather than 0.
    #         if self.type == PIXY_TYPE_RESPONSE_VERSION:
    #             self.version # new Version(buffer)
    #             return self.length  # Success
    #         elif type == PIXY_TYPE_RESPONSE_ERROR:
    #             return PIXY_RESULT_BUSY
    #     return PIXY_RESULT_ERROR # Some kind of bitstream error
    #

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
            # Java code, TODO: use spilinklreceive
            #res = self.receive(c, 1, 0)
            res = self.spi.read(False, c)
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
                time.sleep(0.000025)
                # try:
                #     pass
                #     # TODO: sleep for 25 microseconds.
                # except something about interrupted exception:
                attempts += 1
                i = 0
            i += 1

    def sendPacket(self):
        """Sends packet to Pixy2.  Need to set self.type and self.length beforehand, as well as putting data in self.payload_buffer."""
        write_buffer = bytearray(Pixy2.PIXY_SEND_HEADER_SIZE + self.length) # For Python functions, need to set the buffer the length of the data.
        write_buffer[0] = (Pixy2.PIXY_NO_CHECKSUM_SYNC & 0xff)
        write_buffer[1] = ((Pixy2.PIXY_NO_CHECKSUM_SYNC >> 8) & 0xff)
        write_buffer[2] = self.type
        write_buffer[3] = self.length
        # TODO: need to copy in the self.payload_buffer.
        self.spi.write(write_buffer)  # This method writes out all the bytes in the buffer.
        # TODO: for port, need to use the link, and return either bytes sent or error

    def receivePacket(self):
        """Receives a packet from Pixy2 and puts it in the object global response_buffer for further processing."""
        res = self.getSync() # Search for the syncronization word, and also decide if it represents a checksum-type packet.
        if res < 0:
            return res
        if self.m_cs:
            # Checksum sync
            cs_calc = Pixy2.Checksum()
            buf = bytearray(4) # Checksum packets have 4 bytes.
            # This reads in the length of self.buffer, with "True" initiating a transfer.
            self.spi.read(True, buf) # TODO: shift to using link
            # res = self.receive(self.buffer, 4, 0)
            if res < 0:
                return res
            self.type = buf[0] & 0xFF
            self.length = buf[1] & 0xFF
            csSerial = ((buf[3] & 0xFF) << 8) | (buf[2] & 0xFF)
            buf = bytearray(self.length)
            res = self.spi.read(True, buf)  # TODO: shift to using link and checking the checksum.
            # res = self.receive(self.buffer, self.length, cs_calc)
            if res < 0:
                return res
            # TODO: add the checksum verification from Java.
        else:
            # Not a checksum sync.
            buf = bytearray(2) # Non-Checksum packet headers have only 2 bytes.
            self.spi.read(True, buf) # TODO: shift to using link
            #res = self.receive(self.buffer, 4, 0)
            if res < 0:
                return res
            self.type = buf[0] & 0xFF
            self.length = buf[1] & 0xFF
            buf = bytearray(self.length)
            res = self.spi.read(True, buf)  # TODO: shift to using link.
            if res < 0:
                return res
        # If execution has reached here, there have been no errors to cause early return.
        self.response_buffer[0:self.length] = buf[:] # Put the response into the buffer.
        return Pixy2.PIXY_RESULT_OK

    #
    # # TODO: This method belongs in SPILink.py
    # def receive(self, buf, length_rec, checksum):
    #     if self.cs != 0:
    #         self.resetChecksum()
    #     self.spi.read(False, buf, length_rec)
    #     for val in range(length_rec):
    #         csb = buf[i] & 0xFF
    #         self.updateChecksum(csb)
    #     return length_rec
    #

    class Checksum():
        """Class to hold checksums."""

        def __init__(self):
            self.cs = 0

        def update(self, b):
            """Add a byte to the checksum."""
            self.cs += b

        def get(self):
            return self.cs

        def reset(self):
            self.cs = 0

