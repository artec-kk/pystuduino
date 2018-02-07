# -*- coding: utf-8 -*-
from __future__ import division, unicode_literals, print_function

from studuino import *


if __name__ == "__main__":
    startBLE('COM8', '77:14:e4:2f:1b:f4')

    sv1 = Servomotor()
    sv1.attach(D9)
    sv1.setAngle(90)
    time.sleep(1)
    sv1.setAngle(0)
    time.sleep(1)
    sv1.setAngle(180)

    stopBLE()

