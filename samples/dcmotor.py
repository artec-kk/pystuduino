# -*- coding: utf-8 -*-
from __future__ import division, unicode_literals, print_function

from studuino import *


if __name__ == "__main__":
    start('COM3')
    time.sleep(2)

    dc1 = DCMotor()
    dc2 = DCMotor()
    dc1.attach(M1)
    dc2.attach(M1)
    dc1.setPower(70)
    dc2.setPower(70)
    dc1.move(FWD)
    dc2.move(FWD)
    time.sleep(1)
    dc1.stop(COAST)
    dc2.stop(COAST)

    stop()

