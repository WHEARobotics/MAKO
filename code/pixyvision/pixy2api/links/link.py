# !/usr/bin/env python3
"""
    Python port of the Pixy2 FRC Java library, which was ported from Pixy2 Arduino.

    Link interface for connecting to Pixy2.
"""

class Link(object):
    """Acts as an abstract class that needs to be implemented."""

    # def open(self, link_arg):
    #     """Opens link."""
    #     raise NotImplementedError( "You need to implement open()." )
    #
    # def close(self):
    #     """Closes link."""
    #     raise NotImplementedError( "You need to implement close()." )

    # TODO: Does this interface, with no length parameter (as the Java version has) work for all links?
    def receive(self, buf, chksum = None):
        """Receives and reads specified length of bytes over link.
        :param buf    Byte buffer to fill with return value.
        :param length length of value to read.
        :param chksum An optional Checksum object.  Without it, there will be no checking.

        :returns length of value read."""
        raise NotImplementedError( "You need to implement receive()." )

    # TODO: Does this interface, with no length parameter (as the Java version has) work for all links?
    def send(self, buf):
        """Writes and sends buffer over link.
        :param buf    Byte buffer to fill with return value.

        :returns length of value read."""
        raise NotImplementedError( "You need to implement send()." )
