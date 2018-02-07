# -*- coding: utf-8 -*-
from __future__ import division, unicode_literals, print_function

from studuino import *
import time, datetime


if __name__ == "__main__":
    startBLE('COM8')
    #start('COM5', 115200)

    lsensor = LightSensor()
    lsensor.attach(A7)

    showGraph((lsensor,), True)

    stopBLE()
    #stop()

