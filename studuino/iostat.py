# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

from .const import *
from .part import *

class IOStat:
	def __init__(self):
		self.inited = {}

	def set(self, port, part):
		if not port in self.inited:
			self.inited[port] = part

	def __filterDigital(self, x):
		return isinstance(x[1], DigitalSensor)

	def __filterAnalog(self, x):
		return isinstance(x[1], AnalogSensor)

	def __filterAccel(self, x):
		return isinstance(x[1], Accelerometer)

	def getDigital(self):
		return list(filter(self.__filterDigital, self.inited.items()))
	
	def getAnalog(self):
		return list(filter(self.__filterAnalog, self.inited.items()))
	
	def getAccel(self):
		return list(filter(self.__filterAccel, self.inited.items()))

	def getNumOfTypes(self):
		num = 0
		if len(self.getDigital()) > 0:
			num += 1
		if len(self.getAnalog()) > 0:
			num += 1
		if len(self.getAccel()) > 0:
			num += 1
		return num

