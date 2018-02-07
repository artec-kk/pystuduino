# -*- coding: utf-8 -*-
from __future__ import division, unicode_literals, print_function

from studuino import *


if __name__ == "__main__":
    startBLE('COM8', '77:14:e4:2f:1b:f4')
    #start('COM5', 115200)


    led = LED()
    led.attach(A0)

    for i in range(5):
        led.on()
        time.sleep(0.5)
        led.off()
        time.sleep(0.5)

    stopBLE()
    #stop()

