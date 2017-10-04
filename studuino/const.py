# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

from .connector import *

# Action (LED/BUZZER)
OFF = 0
ON = 1

# DC motion
FWD = 0
BCK = 1
BRAKE = 2
COAST = 3

# Sync servo action
START = 0
STOP  = 1

# Connector (DC)
M1 = ConnectorDC(0)
M2 = ConnectorDC(1)
# Connector (SERVO)
D2 = ConnectorServo(0)
D4 = ConnectorServo(1)
D7 = ConnectorServo(2)
D8 = ConnectorServo(3)
D9 = ConnectorServo(4)
D10 = ConnectorServo(5)
D11 = ConnectorServo(6)
D12 = ConnectorServo(7)
# Connector (SENSOR)
A0 = ConnectorSensor(0)
A1 = ConnectorSensor(1)
A2 = ConnectorSensor(2)
A3 = ConnectorSensor(3)
A4 = ConnectorSensor(4)
A5 = ConnectorSensor(5)
A6 = ConnectorSensor(6)
A7 = ConnectorSensor(7)

# Sound ID
DO  = 60
DO_ = 61
RE  = 62
RE_ = 63
MI  = 64
FA  = 65
FA_ = 66
SO  = 67
SO_ = 68
LA  = 69
LA_ = 70
TI  = 71

