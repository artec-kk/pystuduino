# -*- coding: utf-8 -*-
from __future__ import division, unicode_literals, print_function

from studuino import *


if __name__ == "__main__":
    startBLE('COM8', '77:14:e4:2f:1b:f4')

    buzzer = Buzzer()
    buzzer.attach(A1)

    for sound in range(48, 109):
        buzzer.on(sound % 12, sound // 12)
        time.sleep(0.01)

    buzzer.off()

    stopBLE()

