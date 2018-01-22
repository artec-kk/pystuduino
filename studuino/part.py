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
		関数の説明

		:type self: 型
		:param self: 説明
		"""
		return

	@abstractproperty
	def name(self):
		"""
		関数の説明

		:type self: 型
		:param self: 説明
		"""
		return

	@abstractmethod
	def canAttach(self, connector):
		"""
		関数の説明

		:type self: 型
		:type connector: 型
		:param self: 説明
		:param connector: 説明
		"""
		return

	def attach(self, connector):
		"""
		関数の説明

		:type self: 型
		:type connector: 型
		:param self: 説明
		:param connector: 説明
		"""
		if self.canAttach(connector):
			self.connector = connector
			command.init(connector.getGlobalId(), self)
			print("Part @%s is attached to connector %d." % (self.name, connector.getGlobalId()))
		else:
			raise InitException(self)
			print("Part @%s can't be attached to connector %d." % (self.name, connector.getGlobalId()))

class DCMotor(Part):
	"""
	DC Motor Class
	"""
	@property
	def id(self):
		"""
		関数の説明

		:type self: 型
		:param self: 説明
		:rtype: 戻り値の型
		:return: 戻り値の説明
		"""
		return 0x01

	@property
	def name(self):
		"""
		関数の説明

		:type self: 型
		:param self: 説明
		:rtype: 戻り値の型
		:return: 戻り値の説明
		"""
		return "DC Motor"

	def canAttach(self, connector):
		"""
		関数の説明

		:type self: 型
		:type connector: 型
		:param self: 説明
		:param connector: 説明
		:rtype: 戻り値の型
		:return: 戻り値の説明
		"""
		#return (connector >= 0 and connector <= 1)
		return isinstance(connector, ConnectorDC) 

	def setPower(self, power):
		"""
		関数の説明

		:type self: 型
		:type power: 型
		:param self: 説明
		:param power: 説明
		"""
		self.power = power
		command.dcPower(self.connector.id, power)

	def move(self, motion):
		"""
		関数の説明

		:type self: 型
		:type motion: 型
		:param self: 説明
		:param motion: 説明
		"""
		command.dc(self.connector.id, motion)

	def stop(self, motion):
		"""
		関数の説明

		:type self: 型
		:type motion: 型
		:param self: 説明
		:param motion: 説明
		"""
		command.dc(self.connector.id, motion)

class Servomotor(Part):
	"""
	Servo Motor Class
	"""
	@property
	def id(self):
		"""
		関数の説明

		:type self: 型
		:param self: 説明
		:rtype: 戻り値の型
		:return: 戻り値の説明
		"""
		return 0x02

	@property
	def name(self):
		"""
		関数の説明

		:type self: 型
		:param self: 説明
		:rtype: 戻り値の型
		:return: 戻り値の説明
		"""
		return "Servomotor"

	def canAttach(self, connector):
		"""
		関数の説明

		:type self: 型
		:type connector: 型
		:param self: 説明
		:param seconnectorlf: 説明
		:rtype: 戻り値の型
		:return: 戻り値の説明
		"""
		return isinstance(connector, ConnectorServo) 

	def setAngle(self, angle):
		"""
		関数の説明

		:type self: 型
		:type conanglenector: 型
		:param self: 説明
		:param angle: 説明
		"""
		self.angle = angle
		command.servo(self.connector.getGlobalId(), angle)

	@staticmethod
	def syncMove(servos, angles, delay):
		"""
		関数の説明

		:type servos: 型
		:type angles: 型
		:type delay: 型
		:param servos: 説明
		:param angles: 説明
		:param delay: 説明
		"""
		prev_angles = command.getAngles()
		command.syncServo(0, delay)
		deltaMax = 0
		for e1, e2 in zip(servos, angles):
			delta = abs(e2 - prev_angles[e1.id])
			if delta > deltaMax:
				deltaMax = delta
			e1.setAngle(e2)
		command.syncServo(1)

class LED(Part):
	"""
	LED Class
	"""
	@property
	def id(self):
		"""
		関数の説明

		:type self: 型
		:param self: 説明
		:rtype: 戻り値の型
		:return: 戻り値の説明
		"""
		return 0x03

	@property
	def name(self):
		"""
		関数の説明

		:type self: 型
		:param self: 説明
		:rtype: 戻り値の型
		:return: 戻り値の説明
		"""
		return "LED"

	def canAttach(self, connector):
		"""
		関数の説明

		:type self: 型
		:type connector: 型
		:param self: 説明
		:param connector: 説明
		:rtype: 戻り値の型
		:return: 戻り値の説明
		"""
		return (isinstance(connector, ConnectorSensor) and connector.id <= 5)

	def on(self):
		"""
		関数の説明

		:type self: 型
		:param self: 説明
		"""
		command.led(self.connector.getGlobalId(), ON)

	def off(self):
		"""
		関数の説明

		:type self: 型
		:param self: 説明
		"""
		command.led(self.connector.getGlobalId(), OFF)

class Buzzer(Part):
	"""
	Buzzer Class
	"""
	@property
	def id(self):
		"""
		関数の説明

		:type self: 型
		:param self: 説明
		:rtype: 戻り値の型
		:return: 戻り値の説明
		"""
		return 0x04

	@property
	def name(self):
		"""
		関数の説明

		:type self: 型
		:param self: 説明
		:rtype: 戻り値の型
		:return: 戻り値の説明
		"""
		return "Buzzer"

	def canAttach(self, connector):
		"""
		関数の説明

		:type self: 型
		:type connector: 型
		:param self: 説明
		:param connector: 説明
		:rtype: 戻り値の型
		:return: 戻り値の説明
		"""
		return (isinstance(connector, ConnectorSensor) and connector.id <= 5)

	def on(self, sound, octave=0, duration=0):
		"""
		関数の説明

		:type self: 型
		:type sound: 型
		:type octave: 型
		:type duration: 型
		:param self: 説明
		:param sound: 説明
		:param octave: 説明
		:param duration: 説明
		"""
		command.buzzer(self.connector.getGlobalId(), ON, sound + octave*12, duration)

	def off(self):
		"""
		関数の説明

		:type self: 型
		:param self: 説明
		"""
		command.buzzer(self.connector.getGlobalId(), OFF)

class Sensor(Part):
	"""
	Sensor Class
	"""
	def getValue(self):
		"""
		関数の説明

		:type self: 型
		:param self: 説明
		:rtype: 戻り値の型
		:return: 戻り値の説明
		"""
		return command.getSensor(self.connector.getGlobalId())

class DigitalSensor(Sensor):
	"""
	Digital Sensor Class
	"""
	def canAttach(self, connector):
		"""
		関数の説明

		:type self: 型
		:type connector: 型
		:param self: 説明
		:param connector: 説明
		:rtype: 戻り値の型
		:return: 戻り値の説明
		"""
		return (isinstance(connector, ConnectorSensor) and connector.id <= 5)

class AnalogSensor(Sensor):
	"""
	Analog Sensor Class
	"""
	def canAttach(self, connector):
		"""
		関数の説明

		:type self: 型
		:type connector: 型
		:param self: 説明
		:param connector: 説明
		:rtype: 戻り値の型
		:return: 戻り値の説明
		"""
		return isinstance(connector, ConnectorSensor)

class LightSensor(AnalogSensor):
	"""
	Light Sensor Class
	"""
	@property
	def id(self):
		"""
		関数の説明

		:type self: 型
		:param self: 説明
		:rtype: 戻り値の型
		:return: 戻り値の説明
		"""
		return 0x10

	@property
	def name(self):
		"""
		関数の説明

		:type self: 型
		:param self: 説明
		:rtype: 戻り値の型
		:return: 戻り値の説明
		"""
		return "Light sensor"

class TouchSensor(DigitalSensor):
	"""
	Touch Sensor Class
	"""
	@property
	def id(self):
		"""
		関数の説明

		:type self: 型
		:param self: 説明
		:rtype: 戻り値の型
		:return: 戻り値の説明
		"""
		return 0x11

	@property
	def name(self):
		"""
		関数の説明

		:type self: 型
		:param self: 説明
		:rtype: 戻り値の型
		:return: 戻り値の説明
		"""
		return "Touch sensor"

class SoundSensor(AnalogSensor):
	"""
	Sound Sensor Class
	"""
	@property
	def id(self):
		"""
		関数の説明

		:type self: 型
		:param self: 説明
		:rtype: 戻り値の型
		:return: 戻り値の説明
		"""
		return 0x12

	@property
	def name(self):
		"""
		関数の説明

		:type self: 型
		:param self: 説明
		:rtype: 戻り値の型
		:return: 戻り値の説明
		"""
		return "Sound sensor"

class IRPhotoreflector(AnalogSensor):
	"""
	IR photo reflector Class
	"""
	@property
	def id(self):
		"""
		関数の説明

		:type self: 型
		:param self: 説明
		:rtype: 戻り値の型
		:return: 戻り値の説明
		"""
		return 0x13

	@property
	def name(self):
		"""
		関数の説明

		:type self: 型
		:param self: 説明
		:rtype: 戻り値の型
		:return: 戻り値の説明
		"""
		return "IRPhotoreflector"

class Accelerometer(Sensor):
	"""
	Accelerometer Class
	"""
	@property
	def id(self):
		"""
		関数の説明

		:type self: 型
		:param self: 説明
		:rtype: 戻り値の型
		:return: 戻り値の説明
		"""
		return 0x14
	@property
	def name(self):
		"""
		関数の説明

		:type self: 型
		:param self: 説明
		:rtype: 戻り値の型
		:return: 戻り値の説明
		"""
		return "Accelerometer"

	def canAttach(self, connector):
		"""
		関数の説明

		:type self: 型
		:type connector: 型
		:param self: 説明
		:param connector: 説明
		:rtype: 戻り値の型
		:return: 戻り値の説明
		"""
		return (isinstance(connector, ConnectorSensor), connector.id == 4)

	def getValue(self):
		"""
		関数の説明

		:type self: 型
		:param self: 説明
		:rtype: 戻り値の型
		:return: 戻り値の説明
		"""
		return command.getAccel()

class PushSwitch(DigitalSensor):
	"""
	Push switch Class
	"""
	@property
	def id(self):
		"""
		関数の説明

		:type self: 型
		:param self: 説明
		:rtype: 戻り値の型
		:return: 戻り値の説明
		"""
		return 0x15

	@property
	def name(self):
		"""
		関数の説明

		:type self: 型
		:param self: 説明
		:rtype: 戻り値の型
		:return: 戻り値の説明
		"""
		return "Push switch"

	def canAttach(self, connector):
		"""
		関数の説明

		:type self: 型
		:type connector: 型
		:param self: 説明
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

