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

import enum
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
        self.link = link
        # Initializes send/return buffer and payload buffer
        buffer = bytearray(PIXY_BUFFERSIZE + PIXY_SEND_HEADER_SIZE)
        buffer_payload = bytearray(PIXY_BUFFERSIZE)
        # Initializes tracker objects.
        # self.ccc = Pixy2CCC(self)
        # self.line = Pixy2Line(self)
        # self.video = Pixy2Video(self)

    def init(self, argument):
        """Initializes Pixy2 and waits for startup to complete
           @param argument Argument to setup {@link Link}"""
        # Opens link
        ret = self.link.open(argument)
        if ret >= 0:
            # Tries to connect, times out if unable to communicate after 5 seconds.
            #for
            pass
