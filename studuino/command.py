# -*- coding: utf-8 -*-
from __future__ import division, unicode_literals, print_function

import serial
import time
import threading
import struct

ser = None
servo_angles = [90] * 8
LOCK = threading.Lock()

def start(comPort, baud=38400):
	"""
	Connect to the Studuino board and run python script.

	:param comPort: Serial port assignment
	:param baud: baud rate (default:38400)
	"""
	try:
		global ser
		ser = serial.Serial(comPort, baud)
		ser.write_timeout = 0.3
		ser.read_timeout = 5
		while not ser.writable():
			time.sleep(0.01)
		print('ready')
		ser.read(2)
		print('start')
	except:
		print('Could not find the port.')

def stop():
	"""
	Disonnect the Studuino board.
	"""
	global ser
	if not ser == None:
		print('Disconnected.')
		time.sleep(0.1)
		ser.close()

def __send(data1, data2):
	"""
	Send data to the Studuino.

	:param data1: [ToDo]
	:param data2: [ToDo]
	"""
	global LOCK
	with LOCK:
		msg = struct.pack(b'BB', data1, data2)

		try:
			global ser
			ser.write(msg)
		except:
			print('write exception')

	#ser.timeout = 0.1
	#rcv = ser.read(2)
	#if len(rcv) == 2:
		#print ord(rcv[0]), ord(rcv[1])

def init(pin, part):
	"""
	Initialize the Studuino board.

	:param pin: [ToDo]
	:param part: [ToDo]
	"""
	data1 = 0xc0 + ((pin >> 1) & 0x0f)
	data2 = ((pin & 0x01) << 6) + part.id
	#print('Initialize', hex(data1), hex(data2))
	__send(data1, data2)

def led(pin, action):
	"""
	Control the LEDs.

	:param pin: [ToDo]
	:param action: [ToDo]
	"""
	id = pin - 10   # PinID to Axx ID (Axx begins with 10.)
	data1 = 0xb0 + ((id << 1) & 0x0e) + (action & 0x01)
	data2 = 0
	#print('LED', hex(data1), hex(data2))
	__send(data1, data2)

def buzzer(pin, action, sound=0, duration=0):
	"""
	Control the Buzzers.

	:param pin: [ToDo]
	:param action: [ToDo]
	:param sound: [ToDo]
	:param duration: [ToDo]
	"""
	id = pin - 10   # PinID to Ax ID (Ax begins with 10.)
	data1 = 0xa0 + ((id << 1) & 0x0e) + (action & 0x01)
	data2 = sound & 0x7f 
	#print('Buzzer', hex(data1), hex(data2))
	__send(data1, data2)
	if duration != 0:
		time.sleep(duration)
		__send(data1 & 0xfe, 0)

def dcPower(pin, power):
	"""
	Set power for the DC Motor.

	:param pin: [ToDo]
	:param power: [ToDo]
	"""
	data1 = 0x84 + ((pin << 3) & 0x0f)
	data2 = power & 0x7f
	#print('DC POWER', hex(data1), hex(data2))
	__send(data1, data2)

def dc(pin, motion):
	"""
	Move the DC Motor.

	:param pin: [ToDo]
	:param motion: [ToDo]
	"""
	data1 = 0x80 + ((pin << 3) & 0x0f) + (1 + (motion >> 1 & 0x01))
	data2 = motion & 0x01
	#print('DC Motion', hex(data1), hex(data2))
	__send(data1, data2)

def servo(pin, angle):
	"""
	Move the Servo Motor.

	:param pin: [ToDo]
	:param angle: [ToDo]
	"""
	global servo_angles
	id = pin - 2   # PinID to Dx ID (Dxx begins with 2.)
	servo_angles[id] = angle
	data1 = 0x90 + ((id << 1) & 0x0e) + (angle >> 7 & 0x01)
	data2 = angle & 0x7f 
	#print('Servomotor', hex(data1), hex(data2))
	__send(data1, data2)

# Sync servo action
START = 0
STOP  = 1

def syncServo(action, delay=0):
	"""
	Move the Servo Motor synchronously.

	:param action: [ToDo]
	:param delay: [ToDo]
	"""
	data1 = 0xd0
	data2 = ((action & 0x01) << 6) + delay
	#print('Sync servo', hex(data1), hex(data2))
	__send(data1, data2)
	if action == STOP:
		val = None
		rcv = ser.read()
		if not len(rcv) == 0:
			val = ord(rcv)

def multiServo(pins, angles, delay=0):
	"""
	Move prural Servo Motors synchronously.

	:param pins: [ToDo]
	:param angles: [ToDo]
	:param delay: [ToDo]
	"""
	if not len(pins) == len(angles):
		return

	global servo_angles

	syncServo(START, delay)
	deltaMax = 0
	for e1, e2 in zip(pins, angles):
		delta = abs(e2 - servo_angles[e1.id -2])
		if delta > deltaMax:
			deltaMax = delta
		servo(e1.id, e2)
	#print('deltaMax:', deltaMax)
	syncServo(STOP)
	time.sleep(delay * deltaMax / 1000)

def getAngles():
	global servo_angles
	return servo_angles

def getSensor(pin):
	"""
	Get the sensor value.

	:param pin: [ToDo]
	"""
	global ser
	id = pin - 10   # PinID to Axx ID (Axx begins with 10.)
	data1 = 0xd1
	data2 = id
	#print('get sensor', hex(data1), hex(data2))
	__send(data1, data2)
	val = None
	rcv = ser.read()
	if not len(rcv) == 0:
		val = ord(rcv)
	return val

def getAccel():
	"""
	Get the accelerometer value.
	"""
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

