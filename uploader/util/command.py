# -*- coding: utf-8 -*-
from __future__ import division, unicode_literals, print_function

import serial
import time
import datetime
import threading
import struct

ser = None
servo_angles = [90] * 8
LOCK = threading.Lock()

def start(comPort, baud=38400, timeout=0.1):
	try:
		global ser
		ser = serial.Serial(comPort, baud, timeout=timeout)
		ser.write_timeout = 0.5
		#ser.read_timeout = 0.5
		while not ser.writable():
			time.sleep(0.01)
		print('ready')
		time.sleep(1)
		print('start')
	except:
		print('Could not find the port.')

def stop():
	global ser
	if not ser == None:
		print('Disconnected.')
		time.sleep(0.1)
		ser.close()

def send(data):
	global LOCK
	with LOCK:
		for elm in data:
			msg = struct.pack(b'B', elm)
			try:
				global ser
				ser.write(msg)
			except:
				print('write exception')

def recv(size=0):
	global LOCK
	with LOCK:
		ret = []
		remain = size
		ser.timeout = None
		data = ser.read()
		#if not data == struct.pack(b'B', 0x14):
			#return -1
		ret.append(data)
		
		while remain > 0:
			data = ser.read()
			ret.append(data)
			remain = remain - 1

		data = ser.read()
		#if not data == struct.pack(b'B', 0x10):
			#return -1
		ret.append(data)

		return ret

def recv(buf, length):
	global LOCK
	with LOCK:
		retval = 0
		totalRetval = 0
		startTime = datetime.datetime.now()
		ser.timeout = 0.1
	
		while True:
			tmpbuf = ser.read(length)
			retval = len(tmpbuf)
			if(retval > 0):
				buf[totalRetval:totalRetval+retval] = tmpbuf
				totalRetval = totalRetval + retval
				startTime = datetime.datetime.now()
			if(totalRetval >= length):
				break
	
			endTime = datetime.datetime.now()
			if((endTime - startTime).microseconds > 250000):
				break
	
		return retval

def drain():
	retval = 0
	startTime = datetime.datetime.now()
	while True:
		retval = ser.read(1)
		if not retval is None:
			print(retval)
		currentTime = datetime.datetime.now()
		if((currentTime - startTime).microseconds > 500000):
			print('drain timeout')
			break

def init(pin, part):
	data1 = 0xc0 + ((pin >> 1) & 0x0f)
	data2 = ((pin & 0x01) << 6) + part.id
	#print('Initialize', hex(data1), hex(data2))
	__send(data1, data2)

# Sync servo action
START = 0
STOP  = 1

def getSensor(pin):
	global ser
	id = pin - 10   # PinID to Axx ID (Axx begins with 10.)
	data1 = 0xd1
	data2 = id
	#print('get sensor', hex(data1), hex(data2))
	#send(data1, data2)
	val = None
	rcv = ser.read()
	if not len(rcv) == 0:
		val = ord(rcv)
	return val

def getAccel():
	global ser
	id = 14 - 10   # PinID(14) to Axx ID (Axx begins with 10.)
	data1 = 0xd1
	data2 = id
	#print('get sensor', hex(data1), hex(data2))
	__send(data1, data2)
	val = None
	rcv = ser.read(3)
	if len(rcv) == 3:
		#print(rcv)
		val = struct.unpack(b'BBB', rcv)
	return val

