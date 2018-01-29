# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

import numpy as np
import matplotlib.pyplot as plt
import multiprocessing
import threading
import time
from .const import *
from .part import *

from . import command

job = None
th_data = None
stop_event = None
stop_flag = None

class _PlotArea:
	"""
	クラスの説明
	"""
	def __init__(self, ax, x, num):
		self.ax = ax
		self.x = x
		self.y = []
		self.lines = []
		self.labels = []

		self.ax.legend(loc='upper left')

		for i in range(num):
			tmp_y = np.zeros_like(x)
			self.y.append(tmp_y)
			tmp_l, = ax.plot(x, tmp_y)
			self.lines.append(tmp_l)

	def setLabel(self, labels):
		"""
		関数の説明

		:type self: 型
		:type labels: 型
		:param self: 型
		:param labels: 型
		"""
		self.labels = labels

	def update(self, index, val):
		"""
		関数の説明

		:type self: 型
		:type index: 型
		:type val: 型
		:param self: 型
		:param index: 型
		:param val: 型
		"""
		add = np.array([val])
		self.y[index] = np.r_[self.y[index][1:], add]
		self.lines[index].set_label('%s: %d' % (self.labels[index], val))
		self.lines[index].set_data(self.x, self.y[index])

		self.ax.legend(loc='upper left')
		self.ax.set_xlim((self.x.min(), self.x.max()))

class _IOStat:
	"""
	クラスの説明
	"""
	def __init__(self):
		self.inited = {}

	def set(self, port, part):
		"""
		関数の説明

		:type port: 型
		:type part: 型
		:param port: 説明
		:param part: 説明
		"""
		if not port in self.inited:
			self.inited[port] = part

	def __filterDigital(self, x):
		"""
		関数の説明

		:type x: 型
		:param x: 説明
		:rtype: 戻り値の型
		:return: 戻り値の説明
		"""
		return isinstance(x[1], DigitalSensor)

	def __filterAnalog(self, x):
		"""
		関数の説明

		:type x: 型
		:param x: 説明
		:rtype: 戻り値の型
		:return: 戻り値の説明
		"""
		return isinstance(x[1], AnalogSensor)

	def __filterAccel(self, x):
		"""
		関数の説明

		:type x: 型
		:param x: 説明
		:rtype: 戻り値の型
		:return: 戻り値の説明
		"""
		return isinstance(x[1], Accelerometer)

	def getDigital(self):
		"""
		関数の説明

		:rtype: 戻り値の型
		:return: 戻り値の説明
		"""
		return list(filter(self.__filterDigital, self.inited.items()))
	
	def getAnalog(self):
		"""
		関数の説明

		:rtype: 戻り値の型
		:return: 戻り値の説明
		"""
		return list(filter(self.__filterAnalog, self.inited.items()))
	
	def getAccel(self):
		"""
		関数の説明

		:rtype: 戻り値の型
		:return: 戻り値の説明
		"""
		return list(filter(self.__filterAccel, self.inited.items()))

	def getNumOfTypes(self):
		"""
		関数の説明

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

class _Graph:
	"""
	Graph for displaying sensor data.
	"""
	size_x = 20

	def __init__(self, io, q):
		self.io = io
		self.q = q

	def update(self, stop_flag):
		io = self.io
		numGraph = io.getNumOfTypes()
		print("Num of graph: %d" % numGraph)
		
		fig = plt.figure(figsize=(6 * numGraph, 5))
		x = np.arange(0, self.size_x, 1)
		pos = 0
		graphD = None
		graphA = None
		graphACC = None
	
		if not len(io.getDigital()) == 0:
			graphD = _PlotArea(fig.add_subplot(1, numGraph, pos + 1), x, len(io.getDigital()))
			for elm in io.getDigital():
				lbl = 'A' + str(elm[0].id) + ' ' + str(elm[1].name)
				graphD.labels.append(lbl)
			graphD.ax.set_ylim(-0.5, 1.5)
			pos = pos + 1

		if not len(io.getAnalog()) == 0:
			graphA = _PlotArea(fig.add_subplot(1, numGraph, pos + 1), x, len(io.getAnalog()))
			for elm in io.getAnalog():
				lbl = 'A' + str(elm[0].id) + ' ' + str(elm[1].name)
				graphA.labels.append(lbl)
			graphA.ax.set_ylim(0, 100)
			pos = pos + 1

		if not len(io.getAccel()) == 0:
			graphACC = _PlotArea(fig.add_subplot(1, numGraph, pos + 1), x, 3)
			graphACC.setLabel(['Acc X', 'Acc Y', 'Acc Z'])
			graphACC.ax.set_ylim(0, 100)
			pos = pos + 1
		
		while not stop_flag.is_set():
			try:
				x += 1

				if not graphD == None:
					sensorList = io.getDigital()
					for i, (port, elm) in enumerate(sensorList):
						#val = command.getSensor(port + 10)
						self.q.send([elm,])
						if self.q.poll(0.1):
							add = self.q.recv()
							val = add[0]
							graphD.update(i, val)
				if not graphA == None:
					sensorList = io.getAnalog()
					for i, (port, elm) in enumerate(sensorList):
						#val = command.getSensor(port + 10)
						self.q.send([elm,])
						if self.q.poll(0.1):
							add = self.q.recv()
							val = add[0]
							graphA.update(i, val)
				if not graphACC == None:
					sensorList = io.getAccel()
					for i, (port, elm) in enumerate(sensorList):
						self.q.send([elm,])
						if self.q.poll(0.1):
							add = self.q.recv()
							val = add[0]
							#val = (50, 50, 50)
							for i in range(len(val)):
								graphACC.update(i, val[i])

				plt.pause(0.01)
			#except KeyboardInterrupt:
			#	print("Keyboard interrupt@Graph update()")
			#	plt.close()
			#	break
			except:
				print("Exception in Graph update.")
				plt.close()
				#global stop_event
				#stop_event.set()
				break
			

def __sensorUpdate(q):
	"""
	関数の説明

	:type q: 型
	:param q: 説明
	"""
	global stop_event
	while not stop_event.is_set():
		#print("sensor update")
		try:
			if q.poll():
				#print("queue pool")
				rcv = q.recv()
				val = rcv[0].getValue()
				#print("queue send")
				q.send([val,])
		except KeyboardInterrupt:
			print("Keyboard interrupt@sensor update()")
			break
		except:
			print("Exception@sensorUpdate")
			break
	q.close()

def showGraph(sensors, wait=False):
	"""
	Open the graph window.

	:type sensors: Part[]
	:type wait: bool
	:param sensors: Array of Part objects to be displayed.
        :param wait: default: False
	"""
	io = _IOStat()

	for elm in sensors:
		io.set(elm.connector, elm)

	# Process for updating graph.
	global job, stop_flag
	data_conn, graph_conn = multiprocessing.Pipe()
	stop_flag = multiprocessing.Event()
	gr = _Graph(io, graph_conn)
	job = multiprocessing.Process(target=gr.update, args=(stop_flag,))
	job.start()

	# Thread for getting sensor data.
	global th_data, stop_event
	stop_event = threading.Event()
	th_data = threading.Thread(target=__sensorUpdate, args=(data_conn,))
	th_data.setDaemon(True);
	th_data.start()

	if wait:
		try:
			while True:
				pass
		except KeyboardInterrupt:
			print("Keyboard Interrupt@showGraph")
			hideGraph()
			command.stop()

def hideGraph():
	"""
	Close the graph window.
	"""
	global job, th_data, stop_event
	stop_event.set()
	#print('th_data join')
	th_data.join()
	stop_flag.set()
	#print('job join')
	job.join()

