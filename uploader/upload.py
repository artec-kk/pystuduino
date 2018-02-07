# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

from util import *
import struct
import sys

args = sys.argv

Resp_STK_OK     = 0x10
Resp_STK_INSYNC = 0x14
Resp_STK_NOSYNC = 0x15

data = []

def lineRead(line):
	for i in range(len(line) // 2):
		start = i*2
		stbyte = line[start:start+2]
		data.append(int(stbyte, 16))

def getsync():
	buf = []
	buf.append(0x30)
	buf.append(0x20)

	send(buf)
	drain()

	send(buf)
	drain()

	send(buf)
	#ret = recv()
	ret = recv(buf, 2)
	if ret <= 0:
		return -1
	else:
		return buf

def check_firmware_ver():
	send((0x41, 0x81, 0x20))
	major = recv(1)
	send((0x41, 0x82, 0x20))
	minor = recv(1)
	return (major, minor)

def setParameters():
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
	#buf.append(0x40)    # Try page size 64
	buf.append(0x80)
	buf.append(2)
	buf.append(0)
	buf.append(0)
	buf.append(0)
	buf.append(0x40)
	buf.append(0)
	buf.append(0x20)

	send(buf)
	ret = recv(buf, 2)
	#print(buf[:2])
	return ret

def setExtendedParameters():
	buf = []
	buf.append(0x45)
	buf.append(0x05)
	buf.append(0x04)
	buf.append(0xd7)
	buf.append(0xc2)
	buf.append(0)
	buf.append(0x20)

	send(buf)
	ret = recv(buf, 2)
	return ret

def enter_programmode():
	buf = [0x50, 0x20]
	send(buf)
	ret = recv(buf, 2)
	return ret

def read_signature():
	send((0x75, 0x20))
	ret = recv(3)
	return ret

def leave_programmode():
	buf = [0x51, 0x20]
	send(buf)
	ret = recv(buf, 2)
	return ret


def loadaddr(addr):
	buf = []
	buf.append(0x55)    # Cmnd_STK_LOAD_ADDRESS
	buf.append( addr       & 0xff)
	buf.append((addr >> 8) & 0xff)
	buf.append(0x20)    # Sync_CRC_EOP
	print('loadaddr')
	#print(buf)
	send(buf)
	ret = recv(buf, 2)
	return ret

def paged_write():
	#page_size = 64      # Try page size 64
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

			loadaddr(addr // 2)
	
			send_size = page_size
			if(addr + send_size > n_bytes):
				send_size -= (addr + send_size) - n_bytes
	
			buf.append(0x64)      # Cmnd_STK_PROG_PAGE
			buf.append((send_size >> 8) & 0xff)
			buf.append((send_size ) & 0xff)
			buf.append(0x46)      # 'F' memory type
			buf.extend(data[addr:addr+send_size])
			buf.append(0x20)      # Sync_CRC_EOP
	
			# !! data send command !!
			#print(buf)
			send(buf)
			ret = recv(buf, 1)
			if(ret <= 0):
				return -1
			if buf[0] == Resp_STK_NOSYNC:
				if tries > 33:
					print('Can\'t get into sync')
					return -3
				if getsync() < 0:
					return -1
				bRetry = True
				buf = []
				print('Retry')
				continue
			elif not buf[0] == Resp_STK_INSYNC:
				print('protocol error')
				return -4

		ret = recv(buf, 1)
		if ret <= 0:
			return -1
		if not buf[0] == Resp_STK_OK:
			print('protocol error')
			return -5
	
		addr = addr + page_size

	return n_bytes

def readHex():
	file = 'firmware.hex'
	if len(args) > 1:
		file = args[1]
	f = open(file)
	lines = f.readlines()
	for line in lines:
		if line[7:9] == "01":
			print('skip')
		else:
			lineRead(line[9:len(line)-3])

	f.close()

if __name__ == '__main__':
	readHex()
	start('COM5', 115200)

	#print('Get sync')
	#ret = getsync()
	#print(ret)

	for i in range(5):
		print('Get sync:', i+1)
		ret = getsync()
		print(ret)
		if (not ret == -1) and (ret[0] == 20) and (ret[1] == 16):
			break

	#print('Get firmware ver')
	#ret = check_firmware_ver()
	#print(ret)

	print('Set Parameters')
	ret = setParameters()
	print(ret)
	if ret <= 0:
		stop()
		sys.exit()

	print('Set Extended Parameters')
	ret = setExtendedParameters()
	print(ret)

	print('Enter programmode')
	ret = enter_programmode()
	print(ret)

	#print('Read signature')
	#ret = read_signature()
	#print(ret)

	ret = paged_write()
	print(ret)
	print('Succeeded')
	if ret <= 0:
		stop()
		sys.exit()

	print('Leave programmode')
	ret = leave_programmode()
	print(ret)

	stop()


	#data = struct.unpack('BBB', b'0x000102')
	#print(data)
	#print(struct.pack(b'BBB', 1, 2, 3))

	#send(data)
