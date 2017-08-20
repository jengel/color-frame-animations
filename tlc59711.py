#
# This is a micropython driver for the TLC59711 microprocessor. Modelled after
# the Adafruit-provided C++ Arduino library for the Adafruit 24-channel PWM/LED
# driver.
#
# Written by Jeff Engel. 8/19/2017
#
# Sample usage:
#
#  # Set all LEDs to MAXIMUM POWER!!
#  tlc = Tlc59711()
#  for light in range(4):
#      tlc.setLED(light, 0xff, 0xff, 0xff)
#  tlc.write()
#

import machine

class Tlc59711:
    def __init__(self, pin=1, channels=12):
        # Global RGB brightness levels, 7 bits each
        self.brightness = [0x7f, 0x7f, 0x7f]

        # Command buffer
        assert(channels % 12 == 0)
        self.channels = channels
        self.command = bytearray(4 + 2 * channels)

        # SPI sink
        self.spi = machine.SPI(pin, baudrate=10000000, polarity=0, phase=0)
        self._updateheader()

    def _updateheader(self):
        # Magic word for write
        header = 0x25

        header <<= 5
        #OUTTMG = 1, EXTGCK = 0, TMGRST = 1, DSPRPT = 1, BLANK = 0 -> 0x16
        header |= 0x16

        # Red brightness
        header <<= 7
        header |= self.brightness[0]

        # Green brightness
        header <<= 7
        header |= self.brightness[1]

        # Blue brightness
        header <<= 7
        header |= self.brightness[2]

        # Copy header to command buffer
        self.command[0] = (header >> 24) & 0xff
        self.command[1] = (header >> 16) & 0xff
        self.command[2] = (header >>  8) & 0xff
        self.command[3] = (header      ) & 0xff
    
    def setPWM(self, channel, value):
        """Set a single channel to a 16-bit value (0-65535)"""
        assert channel >= 0 and channel < self.channels
        assert value & 0xffff == value
        # N.B.: The indexing is backwards because the most significant byte is
        #       sent first.
        index = 4 + (2 * (self.channels - channel - 1))
        self.command[index] = (value >> 8) & 0xff
        self.command[index + 1] = value & 0xff

    def setLED16(self, index, red, green, blue):
        """Set a RGB LED to a 16-bit value (0-65535)"""
        self.setPWM(index * 3, red)
        self.setPWM(index * 3 + 1, green)
        self.setPWM(index * 3 + 2, blue)

    def setLED(self, index, red, green, blue):
        """Set a RGB LED to an 8-bit value (0-255)"""
        self.setPWM(index * 3, (red << 8) | red)
        self.setPWM(index * 3 + 1, (green << 8) | green)
        self.setPWM(index * 3 + 2, (blue << 8) | blue)

    def setBrightness(self, red, green, blue):
        """Update the global RGB brightness levels (0-127)"""
        assert red & 0x7f == red
        self.brightness[0] = red
        assert green & 0x7f == green
        self.brightness[1] = green
        assert blue & 0x7f == blue
        self.brightness[2] = blue
        self._updateheader()

    def write(self):
        """Send the current values to the device"""
        self.spi.write(self.command)
