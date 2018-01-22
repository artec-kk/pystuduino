# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

import numpy as np
import matplotlib.pyplot as plt
import multiprocessing
import threading
import time

from . import command
from . import iostat

job = None
th_data = None
stop_event = None
stop_flag = None

class PlotArea:
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

class Graph:
	"""
	クラスの説明
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
			graphD = PlotArea(fig.add_subplot(1, numGraph, pos + 1), x, len(io.getDigital()))
			for elm in io.getDigital():
				lbl = 'A' + str(elm[0].id) + ' ' + str(elm[1].name)
				graphD.labels.append(lbl)
			graphD.ax.set_ylim(-0.5, 1.5)
			pos = pos + 1

		if not len(io.getAnalog()) == 0:
			graphA = PlotArea(fig.add_subplot(1, numGraph, pos + 1), x, len(io.getAnalog()))
			for elm in io.getAnalog():
				lbl = 'A' + str(elm[0].id) + ' ' + str(elm[1].name)
				graphA.labels.append(lbl)
			graphA.ax.set_ylim(0, 100)
			pos = pos + 1

		if not len(io.getAccel()) == 0:
			graphACC = PlotArea(fig.add_subplot(1, numGraph, pos + 1), x, 3)
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
	関数の説明

	:type sensors: 型
	:type wait: 型
	:param sensors: 説明
	:param wait: 説明
	"""
	io = iostat.IOStat()

	for elm in sensors:
		io.set(elm.connector, elm)

	# Process for updating graph.
	global job, stop_flag
	data_conn, graph_conn = multiprocessing.Pipe()
	stop_flag = multiprocessing.Event()
	gr = Graph(io, graph_conn)
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
	関数の説明 [ToDo]
	"""
	global job, th_data, stop_event
	stop_event.set()
	#print('th_data join')
	th_data.join()
	stop_flag.set()
	#print('job join')
	job.join()

