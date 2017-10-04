# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

from six import with_metaclass
from abc import ABCMeta, abstractmethod, abstractproperty
from . import command
from .const import *
from .connector import *


#class Part(metaclass=ABCMeta):
class Part(with_metaclass(ABCMeta, object)):
	@abstractproperty
	def id(self):
		return

	@abstractproperty
	def name(self):
		return

	@abstractmethod
	def canAttach(self, connector):
		return

	def attach(self, connector):
		if self.canAttach(connector):
			self.connector = connector
			command.init(connector.getGlobalId(), self)
			print("Part @%s is attached to connector %d." % (self.name, connector.getGlobalId()))
		else:
			raise InitException(self)
			print("Part @%s can't be attached to connector %d." % (self.name, connector.getGlobalId()))

class DCMotor(Part):
	@property
	def id(self):
		return 0x01

	@property
	def name(self):
		return "DC Motor"

	def canAttach(self, connector):
		#return (connector >= 0 and connector <= 1)
		return isinstance(connector, ConnectorDC) 

	def setPower(self, power):
		self.power = power
		command.dcPower(self.connector.id, power)

	def move(self, motion):
		command.dc(self.connector.id, motion)

	def stop(self, motion):
		command.dc(self.connector.id, motion)

class Servomotor(Part):
	@property
	def id(self):
		return 0x02

	@property
	def name(self):
		return "Servomotor"

	def canAttach(self, connector):
		return isinstance(connector, ConnectorServo) 

	def setAngle(self, angle):
		self.angle = angle
		command.servo(self.connector.getGlobalId(), angle)

	@staticmethod
	def syncMove(servos, angles, delay):
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
	@property
	def id(self):
		return 0x03

	@property
	def name(self):
		return "LED"

	def canAttach(self, connector):
		return (isinstance(connector, ConnectorSensor) and connector.id <= 5)

	def on(self):
		command.led(self.connector.getGlobalId(), ON)

	def off(self):
		command.led(self.connector.getGlobalId(), OFF)

class Buzzer(Part):
	@property
	def id(self):
		return 0x04

	@property
	def name(self):
		return "Buzzer"

	def canAttach(self, connector):
		return (isinstance(connector, ConnectorSensor) and connector.id <= 5)

	def on(self, sound, octave=0, duration=0):
		command.buzzer(self.connector.getGlobalId(), ON, sound + octave*12, duration)

	def off(self):
		command.buzzer(self.connector.getGlobalId(), OFF)

class Sensor(Part):
	def getValue(self):
		return command.getSensor(self.connector.getGlobalId())

class DigitalSensor(Sensor):
	def canAttach(self, connector):
		return (isinstance(connector, ConnectorSensor) and connector.id <= 5)

class AnalogSensor(Sensor):
	def canAttach(self, connector):
		return isinstance(connector, ConnectorSensor)

class LightSensor(AnalogSensor):
	@property
	def id(self):
		return 0x10

	@property
	def name(self):
		return "Light sensor"

class TouchSensor(DigitalSensor):
	@property
	def id(self):
		return 0x11

	@property
	def name(self):
		return "Touch sensor"

class SoundSensor(AnalogSensor):
	@property
	def id(self):
		return 0x12

	@property
	def name(self):
		return "Sound sensor"

class IRPhotoreflector(AnalogSensor):
	@property
	def id(self):
		return 0x13

	@property
	def name(self):
		return "IRPhotoreflector"

class Accelerometer(Sensor):
	@property
	def id(self):
		return 0x14
	@property
	def name(self):
		return "Accelerometer"

	def canAttach(self, connector):
		return (isinstance(connector, ConnectorSensor), connector.id == 4)

	def getValue(self):
		return command.getAccel()

class PushSwitch(DigitalSensor):
	@property
	def id(self):
		return 0x15

	@property
	def name(self):
		return "Push switch"

	def canAttach(self, connector):
		return (isinstance(connector, ConnectorSensor), connector.id <= 3)

class InitException(Exception):
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

