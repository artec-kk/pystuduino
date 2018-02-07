# -*- coding: utf-8 -*-
from __future__ import division, unicode_literals, print_function

from studuino import *


if __name__ == "__main__":
    startBLE('COM8', '77:14:e4:2f:1b:f4')

    dc1 = DCMotor()
    dc2 = DCMotor()
    dc1.attach(M1)
    dc2.attach(M2)

    dc1.setPower(100)
    dc2.setPower(100)

    dc1.move(FWD)
    dc2.move(FWD)
    time.sleep(1)

    dc1.stop(COAST)
    dc2.stop(COAST)
    time.sleep(1)

    dc1.move(BCK)
    dc2.move(BCK)
    time.sleep(1)

    dc1.stop(BRAKE)
    dc2.stop(BRAKE)
    time.sleep(1)

    dc1.move(FWD)
    dc2.move(BCK)

    for speed in range(100, -1, -1):
        dc1.setPower(speed)
        dc2.setPower(speed)
        time.sleep(0.1)

    stopBLE()

