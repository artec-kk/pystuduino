# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

from .connector import *

# Action (LED/BUZZER)
#: Constants for turning LED/Buzzer off.
OFF = 0
#: Constants for turning LED/Buzzer on.
ON = 1

# DC motion
#: Constants for rotating DC motor in forward.
FWD = 0
#: Constants for rotating DC motor in backward.
BCK = 1
#: Constants for stopping DC motor with brake.
BRAKE = 2
#: Constants for stopping DC motor without brake.
COAST = 3

# Sync servo action
START = 0
STOP  = 1

# Connector (DC)
#: DC motor connector M1.
M1 = ConnectorDC(0)
#: DC motor connector M2.
M2 = ConnectorDC(1)
# Connector (SERVO)
#: Servomotor connector D2.
D2 = ConnectorServo(0)
#: Servomotor connector D4.
D4 = ConnectorServo(1)
#: Servomotor connector D7.
D7 = ConnectorServo(2)
#: Servomotor connector D8.
D8 = ConnectorServo(3)
#: Servomotor connector D9.
D9 = ConnectorServo(4)
#: Servomotor connector D10.
D10 = ConnectorServo(5)
#: Servomotor connector D11.
D11 = ConnectorServo(6)
#: Servomotor connector D12.
D12 = ConnectorServo(7)
# Connector (SENSOR)
#: Analog sensor connector A0.
A0 = ConnectorSensor(0)
#: Analog sensor connector A1.
A1 = ConnectorSensor(1)
#: Analog sensor connector A2.
A2 = ConnectorSensor(2)
#: Analog sensor connector A3.
A3 = ConnectorSensor(3)
#: Analog sensor connector A4.
A4 = ConnectorSensor(4)
#: Analog sensor connector A5.
A5 = ConnectorSensor(5)
#: Analog sensor connector A6.
A6 = ConnectorSensor(6)
#: Analog sensor connector A7.
A7 = ConnectorSensor(7)

# Sound ID
#: Sound constant for "Do".
DO  = 60
#: Sound constant for "Do#".
DO_ = 61
#: Sound constant for "Re".
RE  = 62
#: Sound constant for "Re#".
RE_ = 63
#: Sound constant for "Mi".
MI  = 64
#: Sound constant for "Fa".
FA  = 65
#: Sound constant for "Fa#".
FA_ = 66
#: Sound constant for "So".
SO  = 67
#: Sound constant for "So#".
SO_ = 68
#: Sound constant for "La".
LA  = 69
#: Sound constant for "La#".
LA_ = 70
#: Sound constant for "Ti".
TI  = 71

