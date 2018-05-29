# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

import serial
import time
import datetime
import threading
import struct
import sys
import pkg_resources

debugOn = False

Resp_STK_OK     = 0x10
Resp_STK_INSYNC = 0x14
Resp_STK_NOSYNC = 0x15

ser = None
LOCK = threading.Lock()

def _open(comPort):
	try:
		global ser
		ser = serial.Serial(comPort, 115200, timeout=0.1)
		ser.write_timeout = 0.5
		while not ser.writable():
			time.sleep(0.01)
		debugPrint('ready')
		time.sleep(1)
		debugPrint('start')
	except serial.serialutil.SerialException:
		print('Could not find the port.')

def _close():
	global ser
	if not ser == None:
		debugPrint('Disconnected.')
		time.sleep(0.1)
		ser.close()

def _send(data):
	global LOCK
	with LOCK:
		try:
			global ser
			ser.write(bytes(i for i in data))
		except:
			debugPrint('write exception')

def _recv(buf, length):
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

def _drain():
	retval = 0
	startTime = datetime.datetime.now()
	while True:
		retval = ser.read(1)
		if not retval is None:
			debugPrint(retval)
		currentTime = datetime.datetime.now()
		if((currentTime - startTime).microseconds > 500000):
			debugPrint('drain timeout')
			break

def _getsync():
	buf = []
	buf.append(0x30)
	buf.append(0x20)

	_send(buf)
	_drain()

	_send(buf)
	_drain()

	_send(buf)
	ret = _recv(buf, 2)
	if ret <= 0:
		return -1
	else:
		return buf

def _setParameters():
	buf = []
	buf.append(0x42)
	buf.append(0x86)
	buf.append(0)
	buf.append(0)
	buf.append(1)
	buf.append(1)
	buf.append(1)
	buf.append(1)
	buf.append(3)
	buf.append(0xff)
	buf.append(0xff)
	buf.append(0xff)
	buf.append(0xff)
	buf.append(0)
	buf.append(0x80)
	buf.append(2)
	buf.append(0)
	buf.append(0)
	buf.append(0)
	buf.append(0x40)
	buf.append(0)
	buf.append(0x20)

	_send(buf)
	ret = _recv(buf, 2)
	return ret

def _setExtendedParameters():
	buf = []
	buf.append(0x45)
	buf.append(0x05)
	buf.append(0x04)
	buf.append(0xd7)
	buf.append(0xc2)
	buf.append(0)
	buf.append(0x20)

	_send(buf)
	ret = _recv(buf, 2)
	return ret

def _enter_programmode():
	buf = [0x50, 0x20]
	_send(buf)
	ret = _recv(buf, 2)
	return ret

def _leave_programmode():
	buf = [0x51, 0x20]
	_send(buf)
	ret = _recv(buf, 2)
	return ret


def _loadaddr(addr):
	buf = []
	buf.append(0x55)    # Cmnd_STK_LOAD_ADDRESS
	buf.append( addr       & 0xff)
	buf.append((addr >> 8) & 0xff)
	buf.append(0x20)    # Sync_CRC_EOP
	#buf = (0x55, addr & 0xff, (addr >> 8) & 0xff, 0x20)
	#print('loadaddr')
	#print(buf)
	_send(buf)
	#ret = recv(buf, 2)
	rbuf = []
	ret = _recv(rbuf, 2)
	return ret

def _paged_write(data):
	buf = []
	send_size = len(data)

	buf.append(0x64)      # Cmnd_STK_PROG_PAGE
	buf.append((send_size >> 8) & 0xff)
	buf.append((send_size ) & 0xff)
	buf.append(0x46)      # 'F' memory type
	buf.extend(data)
	buf.append(0x20)      # Sync_CRC_EOP
	
	# !! data send command !!
	#print(buf)
	_send(buf)
	ret = _recv(buf, 1)
	if(ret <= 0):
		return -1
	if buf[0] == Resp_STK_NOSYNC:
		return -3
	elif not buf[0] == Resp_STK_INSYNC:
		print('protocol error')
		return -4

	return 0

def _transferMain(data):
	page_size = 128
	n_bytes = len(data)

	addr = 0
	while addr < n_bytes:
		tries = 0
		bRetry = True
		buf = []
		while bRetry:
			bRetry = False
			tries = tries + 1

			_loadaddr(addr // 2)
	
			send_size = page_size
			if(addr + send_size > n_bytes):
				send_size -= (addr + send_size) - n_bytes
	
			ret = _paged_write(data[addr:addr+send_size])
			if(ret == -1):
				return -1
			elif ret == -3:
				if tries > 33:
					print('Can\'t get into sync')
					return -3
				if _getsync() < 0:
					return -1
				bRetry = True
				print('Retry')
				continue
			elif ret == -4:
				return -4

		ret = _recv(buf, 1)
		if ret <= 0:
			return -1
		if not buf[0] == Resp_STK_OK:
			print('protocol error')
			return -5
	
		addr = addr + page_size
		print("#", end="")
		sys.stdout.flush()

	print("")

	return 0

def _readHex(buf):
	resource_package = __name__  # Could be any module/package name
	resource_path = '/'.join(('data', 'firmware.hex'))  # Do not use os.path.join(), see below

	# or for a file-like stream:
	template = pkg_resources.resource_stream(resource_package, resource_path)
	for line in template.readlines():
		strLine = str(line, 'ascii')
		if strLine[7:9] == "01":
			debugPrint('skip')
		else:
			tmp = strLine[9:len(strLine)-3]
			for i in range(len(tmp) // 2):
				start = i*2
				stbyte = tmp[start:start+2]
				buf.append(int(stbyte, 16))

def execute(port, hexFile='firmware.hex'):
	tStart = datetime.datetime.now()
	_open(port)
	
	data = []
	_readHex(data)

	print('Start uploading a firmware.')
	for i in range(5):
		debugPrint(('Get sync:', i+1))
		ret = _getsync()
		debugPrint(ret)
		if (not ret == -1) and (ret[0] == 20) and (ret[1] == 16):
			break

	debugPrint('Set Parameters')
	ret = _setParameters()
	debugPrint(ret)
	if ret <= 0:
		_close()
		sys.exit()

	debugPrint('Set Extended Parameters')
	ret = _setExtendedParameters()
	debugPrint(ret)

	debugPrint('Enter programmode')
	ret = _enter_programmode()
	debugPrint(ret)

	debugPrint('Transfer start')
	ret = _transferMain(data)
	if ret < 0:
		print('Upload failed.')
		_close()
		sys.exit()

	print('Successfully upload {} bytes.'.format(len(data)))

	debugPrint('Leave programmode')
	ret = _leave_programmode()
	debugPrint(ret)

	_close()

	elapsedTime = (datetime.datetime.now() - tStart)
	print('elapsed time: {}.{}'.format(elapsedTime.seconds, elapsedTime.microseconds//1000))

def debugPrint(msg):
	if(debugOn):
		print(msg)

if __name__ == '__main__':
	args = sys.argv
	if len(args) != 2:
		print('python upload.py COM*')
		quit()
	#readHex()
	execute(args[1])
