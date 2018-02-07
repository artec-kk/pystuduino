# -*- coding: utf-8 -*-
from __future__ import division, unicode_literals, print_function

from studuino import *
import time, datetime


if __name__ == "__main__":
    startBLE('COM8', '77:14:e4:2f:1b:f4')

    btA1 = PushSwitch()
    btA2 = PushSwitch()
    btA1.attach(A1)
    btA2.attach(A2)

    sTime = datetime.datetime.now()
    while ((datetime.datetime.now() - sTime).seconds < 5):
        va1 = btA1.getValue()
        va2 = btA2.getValue()
        print('A1: ', va1, ' | A2: ', va2)

    stopBLE()

