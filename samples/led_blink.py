# -*- coding: utf-8 -*-
from __future__ import division, unicode_literals, print_function

from studuino import *


if __name__ == "__main__":
    start('COM3')
    time.sleep(2)

    led = LED()
    led.attach(A0)

    for i in range(5):
        led.on()
        time.sleep(0.5)
        led.off()
        time.sleep(0.5)

    stop()

