#
# This module animates a set of LED light strips. Each light strip is a
# slightly different color and slowly advances along a color wheel to produce
# a subtle fading of lights.
#
# Written by Jeff Engel. 8/19/2017
#
# Assumed hardware:
#  - ESP8266 (NodeMCU) running MicroPython
#  - Tlc59711 chip connected to the Esp
#         Gnd -> Gnd
#         VCC -> 3V3
#         V+ -> 3V3
#         CI -> D5
#         DI -> D7
#  - 4 RGB light strips connected to the Tlc.
#

import color
import machine
import time
import Tlc59711

# The first 3 lights are separated by 37 degrees each. The fourth light is a
# full 180 degrees away from light 2.
separation = 37
degrees = [0, 360 - separation, 360 - separation * 2, 180 - separation]

# Each light will advance by 26 degrees before the next light advances.
advancement = 26

# Lookup tables for each of the mapped RGB values at 100% intensity.
red_lookup = bytearray(360)
green_lookup = bytearray(360)
blue_lookup = bytearray(360)

# Globals to keep track of the animation state. Each light advances for the specified
# number of frames before switching to the next light.
frames_remaining = advancement
light = 0

class Leds:
    def __init__(self, pin=1, channels=12):
        self.tlc = Tlc59711.Tlc59711(pin, channels)
        for index in range(channels):
            self.tlc.setPWM(index, 0xffff)
    
    def setLED(self, index, red, green, blue):
        self.tlc.setLED(index, 0xff - red, 0xff - green, 0xff - blue)

    def setRGB(self, index, rgb):
        self.tlc.setLED(index, 0xff - rgb[0], 0xff - rgb[1], 0xff - rgb[2])
    
    def write(self):
        self.tlc.write()

leds = Leds()


def tick(timer):
    """Callback that is invoked periodically to advance the animation. Per
    micropython timer callback limitations, no allocations are allowed in this
    function."""

    global red_lookup, green_lookup, blue_lookup, leds, degrees, frames_remaining, light, advancement

    leds.setLED(light, red_lookup[degrees[light]], green_lookup[degrees[light]], blue_lookup[degrees[light]])
    leds.write()

    degrees[light] += 1
    if degrees[light] == 360:
        degrees[light] = 0

    frames_remaining -= 1
    if frames_remaining == 0:
        light += 1
        if light == 4:
            light = 0
        frames_remaining = advancement


def animate():
    """Entrypoint to begin the animation sequence."""

    global red_lookup, green_lookup, blue_lookup, leds, degrees

    # Fade in the lights with an initial value
    for brightness in range(255):
        for light in range(4):
            leds.setRGB(light, color.getRGB(degrees[light], 255, brightness))
        leds.write()
        time.sleep_ms(5)

    # Precompute the RGB values for each degree
    for degree in range(360):
        (red_lookup[degree], green_lookup[degree], blue_lookup[degree]) = \
            color.getRGB(degree, 255, 255)

    # Create a timer that will drive the animation at 5Hz
    timer = machine.Timer(-1)
    timer.init(period=500, mode=machine.Timer.PERIODIC, callback=tick)
    return timer

if __name__ == "__main__":
    animate()
