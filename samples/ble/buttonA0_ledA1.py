# -*- coding: utf-8 -*-
from __future__ import division, unicode_literals, print_function

from studuino import *
import time, datetime


if __name__ == "__main__":
    startBLE('COM8', '77:14:e4:2f:1b:f4')

    btA0 = PushSwitch()
    led = LED()
    btA0.attach(A0)
    led.attach(A1)

    sTime = datetime.datetime.now()
    while ((datetime.datetime.now() - sTime).seconds < 5):
        va0 = btA0.getValue()
        if(va0 == 0):
            led.on()
        else:
            led.off()
        print('A0: ', va0)

    stopBLE()

