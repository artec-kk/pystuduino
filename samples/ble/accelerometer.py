# -*- coding: utf-8 -*-
from __future__ import division, unicode_literals, print_function

from studuino import *
import time, datetime


if __name__ == "__main__":
    startBLE('COM8', '77:14:e4:2f:1b:f4')
    #start('COM5', 115200)

    acc = Accelerometer()
    acc.attach(A4)

    sTime = datetime.datetime.now()
    while ((datetime.datetime.now() - sTime).seconds < 5):
        val = acc.getValue()
        print(val)

    stopBLE()
    #stop()

