# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

from .const import *
from .part import *

class IOStat:
	"""
	クラスの説明
	"""
	def __init__(self):
		self.inited = {}

	def set(self, port, part):
		"""
		関数の説明

		:type self: 型
		:type port: 型
		:type part: 型
		:param self: 説明
		:param port: 説明
		:param part: 説明
		"""
		if not port in self.inited:
			self.inited[port] = part

	def __filterDigital(self, x):
		"""
		関数の説明

		:type self: 型
		:type x: 型
		:param self: 説明
		:param x: 説明
		:rtype: 戻り値の型
		:return: 戻り値の説明
		"""
		return isinstance(x[1], DigitalSensor)

	def __filterAnalog(self, x):
		"""
		関数の説明

		:type self: 型
		:type x: 型
		:param self: 説明
		:param x: 説明
		:rtype: 戻り値の型
		:return: 戻り値の説明
		"""
		return isinstance(x[1], AnalogSensor)

	def __filterAccel(self, x):
		"""
		関数の説明

		:type self: 型
		:type x: 型
		:param self: 説明
		:param x: 説明
		:rtype: 戻り値の型
		:return: 戻り値の説明
		"""
		return isinstance(x[1], Accelerometer)

	def getDigital(self):
		"""
		関数の説明

		:type self: 型
		:param self: 説明
		:rtype: 戻り値の型
		:return: 戻り値の説明
		"""
		return list(filter(self.__filterDigital, self.inited.items()))
	
	def getAnalog(self):
		"""
		関数の説明

		:type self: 型
		:param self: 説明
		:rtype: 戻り値の型
		:return: 戻り値の説明
		"""
		return list(filter(self.__filterAnalog, self.inited.items()))
	
	def getAccel(self):
		"""
		関数の説明

		:type self: 型
		:param self: 説明
		:rtype: 戻り値の型
		:return: 戻り値の説明
		"""
		return list(filter(self.__filterAccel, self.inited.items()))

	def getNumOfTypes(self):
		"""
		関数の説明

		:type self: 型
		:param self: 説明
		:rtype: 戻り値の型
		:return: 戻り値の説明
		"""
		num = 0
		if len(self.getDigital()) > 0:
			num += 1
		if len(self.getAnalog()) > 0:
			num += 1
		if len(self.getAccel()) > 0:
			num += 1
		return num

