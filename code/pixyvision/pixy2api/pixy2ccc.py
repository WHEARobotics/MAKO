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
 *         Class to interact with the Color Connected Components algorithm on the Pixy2.

"""

import time
import pixy2api.pixy2


class Pixy2CCC(object):
    """Color Connected Components Class."""
    # Define some helpful constants.
    CCC_MAX_SIGNATURE = 7
    CCC_RESPONSE_BLOCKS = 0x21 # Byte in response to request for blocks. TODO: verify these comments are accurate.
    CCC_REQUEST_BLOCKS = 0x20  # Byte used in request for blocks.

    # Defines for sigmap:
    # You can bitwise OR these together to make a custom sigmap.
    # Sigmaps tell Pixy2 which of the signatures (pre-defined colors)
    # to look for in the image.
    # For example, if you are only interested in receiving blocks with
    # signatures 1 and 5, you could use a sigmap of Pixy2CCC.CCC_SIG1 | Pixy2CCC.CCC_SIG5
    # TODO: suggest to Java author update to above comment.  He has "PIXY_SIG1", but the code is "CCC_SIG1".
    CCC_SIG1 = 0x01
    CCC_SIG2 = 0x02
    CCC_SIG3 = 0x04
    CCC_SIG4 = 0x08
    CCC_SIG5 = 0x10
    CCC_SIG6 = 0x20
    CCC_SIG7 = 0x40
    CCC_COLOR_CODES = 0x80

    CCC_SIG_ALL = 0xFF # All bits or 'ed together

    def __init__(self, pixy):
        """Constructs Pixy2 Color Connected Components tracker.
        :param pixy - parent Pixy2 object that holds this Pixy2CCC object."""
        self.pixy = pixy
        self.blocks = None # TODO: would an empty list be better?

    def getBlocks(self, wait=True, sigmap=0xFF, maxBlocks=0xFF):
        """Gets signature Blocks from Pixy2.
        Defaults to waiting for a response, getting blocks from all signatures, and a maximum of all 256 blocks.
        Returned data should be retrieved from the cache with getBlockCache().
        :param wait -   Boolean that indicates whether to wait until a signature is detected, or return immediately.
        :param sigmap - Signature map to look for.
        :param maxBlocks - Maximum number of blocks to look for (0-255).
        :returns Number of blocks found, or Pixy2 error code.
        """
        start = time.time() # Get time in seconds so we can check on timeouts.

        while True:
            # Fill in the request data (using the Pixy2 object's fields).
            self.pixy.payload_buffer[0] = self.pixy.clip_unsigned_byte(sigmap)
            self.pixy.payload_buffer[1] = self.pixy.clip_unsigned_byte(maxBlocks)
            self.pixy.length = 2
            self.pixy.type = Pixy2CCC.CCC_REQUEST_BLOCKS

            # Send request.
            self.pixy.sendPacket()
            res = self.pixy.receivePacket()
            if res == pixy2api.pixy2.Pixy2.PIXY_RESULT_OK:
                if self.pixy.type == Pixy2CCC.CCC_RESPONSE_BLOCKS:
                    self.blocks = [] # Clear, creating an empty list.
                    for i in range(0, self.pixy.length - 13, 14):
                        b = Pixy2CCC.Block(((self.pixy.response_buffer[i+1] & 0xFF) << 8) | (self.pixy.response_buffer[i] & 0xFF),
                                           ((self.pixy.response_buffer[i+3] & 0xFF) << 8) | (self.pixy.response_buffer[i+2] & 0xFF),
                                           ((self.pixy.response_buffer[i+5] & 0xFF) << 8) | (self.pixy.response_buffer[i+4] & 0xFF),
                                           ((self.pixy.response_buffer[i+7] & 0xFF) << 8) | (self.pixy.response_buffer[i+6] & 0xFF),
                                           ((self.pixy.response_buffer[i+9] & 0xFF) << 8) | (self.pixy.response_buffer[i+8] & 0xFF),
                                           ((self.pixy.response_buffer[i+11] & 0xFF) << 8) | (self.pixy.response_buffer[i+10] & 0xFF),
                                           (self.pixy.response_buffer[i+12] & 0xFF), (self.pixy.response_buffer[i+13] & 0xFF))
                        self.blocks.append(b)
                    return len(self.blocks)
                elif self.pixy.type == pixy2api.pixy2.Pixy2.PIXY_TYPE_RESPONSE_ERROR:
                    # Deal with busy and program changing states from Pixy2 (we'll wait).
                    if self.pixy.response_buffer[0] == pixy2api.pixy2.Pixy2.PIXY_RESULT_BUSY:
                        if not wait:
                            return pixy2api.pixy2.Pixy2.PIXY_RESULT_BUSY # New data not available yet.
                    elif self.pixy.response_buffer[0] == pixy2api.pixy2.Pixy2.PIXY_RESULT_PROG_CHANGING:
                        return self.pixy.response_buffer[0]
            else:
                return pixy2api.pixy2.Pixy2.PIXY_RESULT_ERROR
            if time.time() - start > 0.5:
                # Half a second timeout.
                return pixy2api.pixy2.Pixy2.PIXY_RESULT_ERROR
            # If we are waiting for frame data, pause for 500 microseconds to allow Pixy2 to process
            time.sleep(0.0005)

    def getBlockCache(self):
        """Gets a list of signature Blocks from the cache.
        getBlocks() must be executed first to get the actual data from Pixy2.
        :returns list of Blocks."""
        return self.blocks

    class Block(object):
        """Inner class that encapsulates a color connected block."""

        def __init__(self, signature, x, y, width, height, angle, index, age):
            """Constructs block instance.
            :param signature - Block signature (color) or color code number.  Signatures are 0-7.
                               Color codes are larger than 7.
            :param x         - X value of center of block in pixels (0 on left of image, 315 at right)
            :param y         - Y value of center of block in pixels (0 on top of image, 207 at bottom)
            :param width     - Width of block in pixels  (0 to full screen).
            :param height    - Height of block in pixels (0 to full screen).
            :param angle     - Angle of a color code in degrees (-359 - 360).  Not applicable to a regular signature (value will be 0).
            :param index     - Tracking index of the block.  A block will keep this index until it is no longer visible. (0-255)
            :param age       - Number of frames that a given block (index) has been tracked.  When it reaches 255, it remains at 255.
            """
            self.signature = signature
            self.x = x
            self.y = y
            self.width = width
            self.height = height
            self.angle = angle
            self.index = index
            self.age = age

        def print(self):
            """Print the block's data to the console."""
            print(self.toString())

        def toString(self):
            """Create a string from the block data.
            :returns the string"""
            if self.signature > Pixy2CCC.CCC_MAX_SIGNATURE:
                # The block has a color code.
                # Java version converts signature number to an octal string, but hexadecimal is easier to use.
                out = 'CC block sig: 0x{:4X} ({} decimal) x: {} y: {} width: {} height: {} angle: {} index: {} age: {}'\
                    .format(self.signature, self.signature, self.x, self.y, self.width, self.height, self.angle, self.index, self.age)
            else:
                # Regular block.  Angle is always zero, so no need to print.
                out = 'CC block sig: {} x: {} y: {} width: {} height: {} index: {} age: {}'\
                    .format(self.signature, self.x, self.y, self.width, self.height, self.index, self.age)
            return out

        # Define a bunch of "getter" functions that are kind of redundant for Python, since you can just access example_block.signature, etc.
        # But for compatibility with the Java version, here they are:
        def getSignature(self):
            """:returns Block signature."""
            return self.signature

        def getX(self):
            """:returns Block x value."""
            return self.x

        def getY(self):
            """:returns Block y value."""
            return self.y

        def getWidth(self):
            """:returns Block width."""
            return self.width

        def getHeight(self):
            """:returns Block height."""
            return self.height

        def getAngle(self):
            """:returns Block angle."""
            return self.angle

        def getIndex(self):
            """:returns Block index."""
            return self.index

        def getAge(self):
            """:returns Block age."""
            return self.age
