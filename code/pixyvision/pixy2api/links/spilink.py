# !/usr/bin/env python3
"""
    Python port of the Pixy2 FRC Java library, which was ported from Pixy2 Arduino.

    SPI Link interface for connecting to Pixy2.
"""
import wpilib
import pixy2api.links.link

class SPILink(pixy2api.links.link.Link):
    """Link for communicating over Serial Peripheral Interface (SPI)."""
    PIXY_SPI_CLOCKRATE = 2000000 # In Hz.

    def __init__(self, link_arg):
        """:param link_arg is one of 0-3 for the onboard chip selects,
                                     4   for the MXP expansion header chip select."""

        # Translate from the argument to a chip select value.
        if link_arg == 1:
            spi_port = wpilib.SPI.Port.kOnboardCS1
        elif link_arg == 2:
            spi_port = wpilib.SPI.Port.kOnboardCS2
        elif link_arg == 3:
            spi_port = wpilib.SPI.Port.kOnboardCS3
        elif link_arg == 4:
            spi_port = wpilib.SPI.Port.kMXP
        else:
            spi_port = wpilib.SPI.Port.kOnboardCS0
        # Use the value to open the port and configure it.
        self.spi = wpilib.SPI(spi_port)
        self.spi.setClockRate(SPILink.PIXY_SPI_CLOCKRATE)
        self.spi.setMSBFirst()
        self.spi.setSampleDataOnTrailingEdge()
        self.spi.setClockActiveLow()
        self.spi.setChipSelectActiveLow()

    # def open(self, link_arg):
    #     """Why do I have an open() method rather than just using __init__()?"""
    #     pass
    #
    # def close(self):
    #     """Closes the SPI port."""
    #     self.spi.close() # wpilib.SPI has no such method...

    def receive(self, buf, chksum = None):
        """Receives and reads number of bytes to fill the buffer over SPI.
        :param buf    Byte buffer to fill with return value.
        :param chksum An optional Checksum object.  Without it, there will be no checking.

        :returns length of value read, or error."""
        if chksum is not None:
            chksum.reset()
        retval = self.spi.read(False, buf) # TODO: Java uses False; my initial code uses True.  Which do we want?
        if chksum is not None:
            for ch in buf:
                chksum.update(ch & 0xFF)
        return retval


    def send(self, buf):
        """Writes and sends buffer over SPI.
        :param buf    Byte buffer to send (sends all bytes in the buffer).

        :returns length of bytes sent."""
        return self.spi.write(buf)
