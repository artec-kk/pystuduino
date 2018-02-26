# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

from six import with_metaclass
from abc import ABCMeta, abstractmethod, abstractproperty
from . import command
from .const import *
from .connector import *


#class Part(metaclass=ABCMeta):
class Part(with_metaclass(ABCMeta, object)):
	"""
	Parts Class
	"""
	@abstractproperty
	def id(self):
		"""
		Part ID

		"""
		return

	@abstractproperty
	def name(self):
		"""
		Part name

		"""
		return

	@abstractmethod
	def _canAttach(self, connector):
		"""
		関数の説明

		:type connector: 型
		:param connector: 説明
		"""
		return

	def attach(self, connector):
		"""
		Attach the part to the specified connector.

		:type connector: Connector
		:param connector: A Connector object defined in studuino.connector.
		"""
		if self._canAttach(connector):
			self.connector = connector
			#command._init(connector._getGlobalId(), self)
			print("Part @%s is attached to connector %d." % (self.name, connector._getGlobalId()))
		else:
			raise InitException(self)
			print("Part @%s can't be attached to connector %d." % (self.name, connector._getGlobalId()))

class DCMotor(Part):
	"""
	DC Motor Class
	"""
	@property
	def id(self):
		"""
		DC motor's part ID

		:rtype: int
		:return: DC motor's part ID.
		"""
		return 0x01

	@property
	def name(self):
		"""
		関数の説明

		:rtype: str
		:return: "DC Motor"
		"""
		return "DC Motor"

	def _canAttach(self, connector):
		"""
		関数の説明

		:type connector: 型
		:param connector: 説明
		:rtype: bool
		:return: Whether this part is connectable to the specified connector.
		"""
		#return (connector >= 0 and connector <= 1)
		return isinstance(connector, ConnectorDC) 

	def setPower(self, power):
		"""
		Set the DC motor's power.

		:type power: int
		:param power: DC motor power [0-100].
		"""
		self.power = power
		command._dcPower(self.connector.id, power)

	def move(self, motion):
		"""
		Rotate the dc motor by specified motion type.

		:type motion: int
		:param motion: The number representing the motion type. [FWD|BCK]
		"""
		command._dc(self.connector.id, motion)

	def stop(self, motion):
		"""
		Stop the dc motor by specified motion type.

		:type motion: int
		:param motion: The number representing the motion type. [BRAKE|COAST]
		"""
		command._dc(self.connector.id, motion)

class Servomotor(Part):
	"""
	Servo Motor Class
	"""
	@property
	def id(self):
		"""
		Servomotor's part ID

		:rtype: int
		:return: 0x02
		"""
		return 0x02

	@property
	def name(self):
		"""
		Servomotor's part name

		:rtype: str
		:return: "Servomotor"
		"""
		return "Servomotor"

	def _canAttach(self, connector):
		"""
		関数の説明

		:type connector: 型
		:param connector: 説明
		:rtype: bool
		:return: 戻り値の説明
		"""
		return isinstance(connector, ConnectorServo) 

	def setAngle(self, angle):
		"""
		Set the servomotor's angle

		:type angle: int
		:param angle: Servomotor's angle in degree.
		"""
		self.angle = angle
		command._servo(self.connector._getGlobalId(), angle)

	@staticmethod
	def syncMove(servos, angles, delay):
		"""
		関数の説明

		:type servos: int[]
		:type angles: int[]
		:type delay: int
		:param servos: Array of servomotor port.
		:param angles: Array of servomotor angle.
		:param delay: Delay time per 1 degree [milliseconds].
		"""
		#print('syncmove')
		prev_angles = command._getAngles()
		command._syncServo(0, delay)
		deltaMax = 0
		for e1, e2 in zip(servos, angles):
			delta = abs(e2 - prev_angles[e1.id])
			if delta > deltaMax:
				deltaMax = delta
			e1.setAngle(e2)
		command._syncServo(1)

class LED(Part):
	"""
	LED Class
	"""
	@property
	def id(self):
		"""
		LED's part ID

		:rtype: int
		:return: 0x03
		"""
		return 0x03

	@property
	def name(self):
		"""
		LED's part name

		:rtype: str
		:return: "LED"
		"""
		return "LED"

	def _canAttach(self, connector):
		"""
		関数の説明

		:type connector: 型
		:param connector: 説明
		:rtype: 戻り値の型
		:return: 戻り値の説明
		"""
		return (isinstance(connector, ConnectorSensor) and connector.id <= 5)

	def on(self):
		"""
		Turning the LED on.

		"""
		command._led(self.connector._getGlobalId(), ON)

	def off(self):
		"""
		Turning the LED off.

		"""
		command._led(self.connector._getGlobalId(), OFF)

class Buzzer(Part):
	"""
	Buzzer Class
	"""
	@property
	def id(self):
		"""
		Buzzer's part ID

		:rtype: int
		:return: 0x04
		"""
		return 0x04

	@property
	def name(self):
		"""
		Buzzer's part name

		:rtype: str
		:return: "Buzzer"
		"""
		return "Buzzer"

	def _canAttach(self, connector):
		"""
		関数の説明

		:type connector: 型
		:param connector: 説明
		:rtype: 戻り値の型
		:return: 戻り値の説明
		"""
		return (isinstance(connector, ConnectorSensor) and connector.id <= 5)

	def on(self, sound, octave=0, duration=0):
		"""
		Play the specified type of sound.

		:type sound: int
		:type octave: int
		:type duration: int
		:param sound: Sound ID registered int studuino.const.
		:param octave: Octaves of the sound [0-8].
		:param duration: Duration of the sound in milliseconds.
		"""
		command._buzzer(self.connector._getGlobalId(), ON, sound + octave*12, duration)

	def off(self):
		"""
		Stop the buzzer.

		"""
		command._buzzer(self.connector._getGlobalId(), OFF)

class Sensor(Part):
	"""
	Sensor Class
	"""
	def getValue(self):
		"""
		Returning the sensor's value.

		:rtype: int
                :return: Sensor value (Digital Sensor:[0|1] Analog Sensor:[0-100])
		"""
		return command._getSensorValue(self.connector.id)

class DigitalSensor(Sensor):
	"""
	Digital Sensor Class
	"""
	def _canAttach(self, connector):
		"""
		関数の説明

		:type connector: 型
		:param connector: 説明
		:rtype: 戻り値の型
		:return: 戻り値の説明
		"""
		return (isinstance(connector, ConnectorSensor) and connector.id <= 5)

	def attach(self, connector):
		Part.attach(self, connector)
		command._initSensor(self.connector.id, 0)

class AnalogSensor(Sensor):
	"""
	Analog Sensor Class
	"""
	def _canAttach(self, connector):
		"""
		関数の説明

		:type connector: 型
		:param connector: 説明
		:rtype: 戻り値の型
		:return: 戻り値の説明
		"""
		return isinstance(connector, ConnectorSensor)

	def attach(self, connector):
		Part.attach(self, connector)
		command._initSensor(self.connector.id, 1)

class LightSensor(AnalogSensor):
	"""
	Light Sensor Class
	"""
	@property
	def id(self):
		"""
		Light sensor's part ID

		:rtype: int
		:return: 0x10
		"""
		return 0x10

	@property
	def name(self):
		"""
		Light sensor's part name

		:rtype: str
		:return: "Light sensor"
		"""
		return "Light sensor"

class TouchSensor(DigitalSensor):
	"""
	Touch Sensor Class
	"""
	@property
	def id(self):
		"""
		Touch sensor's part ID.

		:rtype: int
		:return: 0x11
		"""
		return 0x11

	@property
	def name(self):
		"""
		Touch sensor's part name.

		:rtype: str
		:return: "Touch sensor"
		"""
		return "Touch sensor"

class SoundSensor(AnalogSensor):
	"""
	Sound Sensor Class
	"""
	@property
	def id(self):
		"""
		Sound sensor's part ID.

		:rtype: int
		:return: 0x12
		"""
		return 0x12

	@property
	def name(self):
		"""
		Sound sensor's part name.

		:rtype: str
		:return: "Sound sensor"
		"""
		return "Sound sensor"

class IRPhotoreflector(AnalogSensor):
	"""
	IR photo reflector Class
	"""
	@property
	def id(self):
		"""
		IR Photoreflector's part ID.

		:rtype: int
		:return: 0x13
		"""
		return 0x13

	@property
	def name(self):
		"""
		IR Photoreflector's part name.

		:rtype: str
		:return: "IRPhotorefrector"
		"""
		return "IRPhotoreflector"

class Accelerometer(Sensor):
	"""
	Accelerometer Class
	"""
	@property
	def id(self):
		"""
		Acceoerometer's part ID

		:rtype: int
		:return: 0x14
		"""
		return 0x14
	@property
	def name(self):
		"""
		Acceoerometer's part name

		:rtype: str
		:return: "Accelerometer"
		"""
		return "Accelerometer"

	def _canAttach(self, connector):
		"""
		関数の説明

		:type connector: 型
		:param connector: 説明
		:rtype: 戻り値の型
		:return: 戻り値の説明
		"""
		return (isinstance(connector, ConnectorSensor), connector.id == 4)

	def attach(self, connector):
		Part.attach(self, connector)
		command._initSensor(self.connector.id, 2)

	def getValue(self):
		"""
		Returning the acceleration values.

		:rtype: int[]
		:return: Array of acceleration (x, y, z).
		"""
		return command._getAccel()

class PushSwitch(DigitalSensor):
	"""
	Push switch Class
	"""
	@property
	def id(self):
		"""
		Push switch's part ID

		:rtype: int
		:return: 0x15
		"""
		return 0x15

	@property
	def name(self):
		"""
		Push switch's part name

		:rtype: str
		:return: "Push switch"
		"""
		return "Push switch"

	def _canAttach(self, connector):
		"""
		関数の説明

		:type connector: 型
		:param connector: 説明
		:rtype: 戻り値の型
		:return: 戻り値の説明
		"""
		return (isinstance(connector, ConnectorSensor), connector.id <= 3)

class InitException(Exception):
	"""
	Init exeception Class
	"""
	def __init__(self, value):
		self.value = value


if __name__ == '__main__':
	from . import const
	dc = DCMotor()
	dc.attach(M1)
	sv = Servomotor()
	sv.attach(D2)

	ls = LightSensor()
	ls.attach(A0)
	ls.getValue()

	bt = PushSwitch()
	bt.attach(A1)
	bt.getValue()

	ts = TouchSensor()
	ts.attach(A2)
	ts.getValue()

