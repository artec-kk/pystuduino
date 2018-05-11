# -*- coding: utf-8 -*-
from __future__ import division, unicode_literals, print_function
"""
Studuino for Python
"""

import serial
import time
import datetime
import threading
import struct
from . import ble_wrapper
from studuino.sensor import SensorManager

ser = None
sensor = None
fConnected = False
servo_angles = [90] * 8
LOCK = threading.Lock()
LOCK_READ = threading.Lock()
fBLE = False

def start(comPort, baud=115200):
    """
    Connect to the Studuino board and run python script.

    :type comPort: str 
    :type baud: int 
    :param comPort: Serial port name
    :param baud: baud rate (default:115200)
    """
    global ser, sensor, fConnected
    try:
        ser = serial.Serial(comPort, baud, timeout=0)
        ser.write_timeout = 0.3
        #ser.read_timeout = 0.05 
        fConnected = True

        sensor = SensorManager()
        th_read = threading.Thread(target=_sensorRead)
        th_read.setDaemon(True)
        th_read.start()


        while not ser.writable():
            time.sleep(0.01)
        print('ready')
        #ser.read(2)
        print('start')
        time.sleep(2)
    except:
        print('Could not find the port.')

def startBLE(comPort, addr):
    """
    Connect to the Studuino board and run python script.

    :type comPort: str 
    :type addr: str 
    :param comPort: Serial port name
    :param addr: BLE module's MAC address (00:01:02:ab:cd:ef)
    """
    global fBLE, sensor
    fBLE = True

    sensor = SensorManager()
    ble_wrapper.start(comPort, addr)
    ble_wrapper.addReceiveHandler(_handle_ble_receive)
    ble_wrapper.start_sensor_read()
    time.sleep(1)  # The sleep is necessary for ignoring the communication between BLE module and Studuino at establishing the connection.

def stop():
    """
    Disonnect the Studuino board.
    """
    if fBLE:
        stopBLE()
    else:
        global ser, LOCK_READ, fConnected
        if not ser == None:
            fConnected = False
            print('Disconnected.')
            time.sleep(0.1)
            with LOCK_READ:
                ser.close()

def stopBLE():
    ble_wrapper.stop()

def _sensorRead():
    global sensor, fConnected, LOCK_READ
    while fConnected:
        try:
            with LOCK_READ:
                rcv = ser.read(5)
            sensor.parseData(rcv)
        except Exception as ex:
            print('Read error: ', ex)

def _handle_ble_receive(sender, earg):
    global sensor
    rcvData = earg['value']
    sensor.parseData(rcvData)

def __send(data1, data2):
    """
    Send data to the Studuino.

    :type data1: 型
    :type data2: 型
    :param data1: 説明
    :param data2: 説明
    """
    global ser, sensor, LOCK, fBLE
    data3 = (data1 + data2) & 0xff;
    msg = struct.pack(b'BBB', data1, data2, data3)

    if fBLE:
    # BLE
        # Without waiting
        # ble_wrapper.write_command(msg)

        # With waiting
        #sensor.startWaitingWriteResponse()
        #start = datetime.datetime.now()
        #ble_wrapper.write_command(msg)
        #print('before wait: ', start)
        #while (sensor.getWriteFlag() == 1 and (datetime.datetime.now() - start).seconds < 0.1):
            #pass
        #print('after wait: ', datetime.datetime.now())

        # With LOCK
        with LOCK:
            sensor.startWaitingWriteResponse()
            start = datetime.datetime.now()
            ble_wrapper.write_command(msg)
            while (sensor.getWriteFlag() == 1 and (datetime.datetime.now() - start).seconds < 1):
                #print('     waiting...')
                pass
    else:
    # USB
        try:
            with LOCK:
                sensor.startWaitingWriteResponse()
                start = datetime.datetime.now()
                ser.write(msg)
                while (sensor.getWriteFlag() == 1 and (datetime.datetime.now() - start).seconds < 1):
                    pass
        except:
            print('write exception')

def _init(pin, part):
    """
    Initialize the Studuino board.

    :type pin: 型
    :type part: 型
    :param pin: 説明
    :param part: 説明
    """
    data1 = 0xc0 + ((pin >> 1) & 0x0f)
    data2 = ((pin & 0x01) << 6) + part.id
    #print('Initialize', hex(data1), hex(data2))
    __send(data1, data2)

def _led(pin, action):
    """
    Control the LEDs.

    :type pin: 型
    :type action: 型
    :param pin: 説明
    :param action: 説明
    """
    id = pin - 10   # PinID to Axx ID (Axx begins with 10.)
    data1 = 0xb0 + ((id << 1) & 0x0e) + (action & 0x01)
    data2 = 0
    #print('LED', hex(data1), hex(data2))
    __send(data1, data2)

def _buzzer(pin, action, sound=0, duration=0):
    """
    Control the Buzzers.

    :type pin: 型
    :type action: 型
    :type sound: 型
    :type duration: 型
    :param pin: 説明
    :param action: 説明
    :param sound: 説明
    :param duration: 説明
    """
    id = pin - 10   # PinID to Ax ID (Ax begins with 10.)
    data1 = 0xa0 + ((id << 1) & 0x0e) + (action & 0x01)
    data2 = sound & 0x7f 
    #print('Buzzer', hex(data1), hex(data2))
    __send(data1, data2)
    if duration != 0:
        time.sleep(duration)
        __send(data1 & 0xfe, 0)

def _dcPower(pin, power):
    """
    Set power for the DC Motor.

    :type pin: 型
    :type power: 型
    :param pin: 説明
    :param power: 説明
    """
    data1 = 0x84 + ((pin << 3) & 0x0f)
    data2 = power & 0x7f
    #print('DC POWER', hex(data1), hex(data2))
    __send(data1, data2)

def _dc(pin, motion):
    """
    Move the DC Motor.

    :type pin: 型
    :type motion: 型
    :param pin: 説明
    :param motion: 説明
    """
    data1 = 0x80 + ((pin << 3) & 0x0f) + (1 + (motion >> 1 & 0x01))
    data2 = motion & 0x01
    #print('DC Motion', hex(data1), hex(data2))
    __send(data1, data2)

def _servo(pin, angle):
    """
    Move the Servo Motor.

    :type pin: 型
    :type angle: 型
    :param pin: 説明
    :param angle: 説明
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

def _syncServo(action, delay=0):
    """
    Move the Servo Motor synchronously.

    :type action: 型
    :type delay: 型
    :param action: 説明
    :param delay: 説明
    """
    global fBLE
    data1 = 0xd0
    data2 = ((action & 0x01) << 6) + delay
    #print('Sync servo', hex(data1), hex(data2))
    __send(data1, data2)
    if action == START:
        sensor.startSyncServo()
    if action == STOP:
        if fBLE:
            ble_wrapper.waitSyncFinish()
        while sensor.getSyncServoFlag() == 1:
            pass

def _multiServo(pins, angles, delay=0):
    """
    Move prural Servo Motors synchronously.

    :type pins: 型
    :type angles: 型
    :type delay: 型
    :param pins: 説明
    :param angles: 説明
    :param delay: 説明
    """
    if not len(pins) == len(angles):
        return

    global servo_angles

    _syncServo(START, delay)
    deltaMax = 0
    for e1, e2 in zip(pins, angles):
        delta = abs(e2 - servo_angles[e1.id -2])
        if delta > deltaMax:
            deltaMax = delta
        _servo(e1.id, e2)
    #print('deltaMax:', deltaMax)
    _syncServo(STOP)
    time.sleep(delay * deltaMax / 1000)

def _getAngles():
    """
    説明を書いてください

    rtype: 戻り値の型
    return: 戻り値の説明
    """
    global servo_angles
    return servo_angles

"""
def _getSensor():
    global ser
    val = None
    rcv = ser.read()
    if not len(rcv) == 0:
        val = ord(rcv)
    return val
    """

def _initSensor(pin, snstype):
    data1 = 0xd1
    data2 = snstype << 4 | pin
    __send(data1, data2)

def _getSensorValue(pin):
    global sensor
    return sensor.getValue(pin)

def _getSensorValue_(pin):
    """
    Get the sensor value.

    :type pin: 型
    :param pin: 説明
    :rtype: 戻り値の型
    :return: 戻り値の説明
    """
    global ser, fBLE
    id = pin - 10   # PinID to Axx ID (Axx begins with 10.)
    data1 = 0xd1
    data2 = id
    #print('get sensor', hex(data1), hex(data2))
    val = None
    if fBLE:
    # BLE
        val = ble_wrapper.get_sensor((data1, data2))
        return val[0]
    else:
    # USB
        __send(data1, data2)
        rcv = ser.read()
        if not len(rcv) == 0:
            val = ord(rcv)
        return val

def _getAccel():
    """
    Get the accelerometer value.

    :rtype: 戻り値の型
    :return: 戻り値の説明
    """
    global ser, fBLE
    id = 14 - 10   # PinID(14) to Axx ID (Axx begins with 10.)
    data1 = 0xd1
    data2 = id
    #print('get sensor', hex(data1), hex(data2))
    val = None
    if fBLE:
    # BLE
        rcv = ble_wrapper.get_accel((data1, data2))
        val = rcv
    else:
    # USB
        __send(data1, data2)
        rcv = ser.read(3)
        if len(rcv) == 3:
            #print(rcv)
            val = struct.unpack(b'BBB', rcv)
    return val

