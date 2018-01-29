# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

from six import with_metaclass
from abc import ABCMeta, abstractmethod, abstractproperty

#class Connector(metaclass=ABCMeta):
class Connector(with_metaclass(ABCMeta, object)):
	"""
	Base class of connectors.
	"""
	@abstractproperty
	def _offset(self):
		return

	def __init__(self, id):
		self.id = id

	"""
	Returning the global ID of the connector.

	:rtype: int
	:rparam: Global ID of the connector.
	"""
	def _getGlobalId(self):
		return (self._offset + self.id)

class ConnectorDC(Connector):
	"""
	DC motor connector
	"""
	@property
	def _offset(self):
		return 0

class ConnectorServo(Connector):
	"""
	Servomotor connector
	"""
	@property
	def _offset(self):
		return 2

class ConnectorSensor(Connector):
	"""
	Sensor connector
	"""
	@property
	def _offset(self):
		return 10



if __name__ == '__main__':
	M1 = ConnectorDC(0)
	M2 = ConnectorDC(1)
	D2 = ConnectorServo(0)
	D4 = ConnectorServo(1)
	D7 = ConnectorServo(2)
	D8 = ConnectorServo(3)
	D9 = ConnectorServo(4)
	D10 = ConnectorServo(5)
	D11 = ConnectorServo(6)
	D12 = ConnectorServo(7)
	A0 = ConnectorSensor(0)
	A1 = ConnectorSensor(1)
	A2 = ConnectorSensor(2)
	A3 = ConnectorSensor(3)
	A4 = ConnectorSensor(4)
	A5 = ConnectorSensor(5)
	A6 = ConnectorSensor(6)
	A7 = ConnectorSensor(7)


	for elm in (M1, M2, D2, D4, D7, D8, D9, D10, D11, D12, A0, A1, A2, A3, A4, A5, A6, A7):
		print("Connector GID:%d ID:%d" % (elm._getGlobalId(), elm.id))

