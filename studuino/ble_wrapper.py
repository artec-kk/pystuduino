# -*- coding: utf-8 -*-
from __future__ import division, unicode_literals, print_function

from .bglib import BGLib
import serial
import threading
import sys
import time
from datetime import datetime

fConnection = False
fProcedureStarted = False
fRecv = False
fAccel = False
fInSync = False
idxAccel = 0
rcvAccel = [0, 0, 0]

LOCK = threading.Lock()

def timeout_handler(sender, args):
    print( "BGAPI parser timed out.",)
    print( " Make sure the BLE device is in a known/idle state.")

def handle_connection_status(sender, earg):
    global fConnection
    val = earg['flags']
    # print( "Connection state flag: ", val)
    if val == 9:
        fConnection = True

def handle_procedure_completed(sender, earg):
    global fProcedureStarted
    result = earg['result']
    chrhandler = earg['chrhandle']
    # print( 'Procedure : ', result)
    if result == 0:
        fProcedureStarted = False

def handle_write_command(sender, earg):
    global fProcedureStarted
    result = earg['result']
    # print( 'Procedure : ', result)
    if result == 0:
        fProcedureStarted = False

def handle_receive(sender, earg):
    global rcvData, fRecv, fAccel, idxAccel, rcvAccel, fInSync
    rcvData = earg['value']
    # print('handle_receive', rcvData)
    if fAccel:
        rcvAccel[idxAccel] = rcvData[0]
        idxAccel = idxAccel + 1
        if idxAccel == 3:
            idxAccel = 0
            fAccel = False
    if rcvData[0] == 0x80:
        fRecv = True
    if rcvData[0] == 0x9f:
        fInSync = False

def write_command(data):
    global ser, ble, fRecv, LOCK
    ble.send_command(ser, ble.ble_cmd_attclient_write_command(0, 14, data))
    fRecv = False
    while (not fRecv):
        with LOCK:
            ble.check_activity(ser)

def get_sensor(data):
    global rcvData, fRecv
    fRecv = False
    write_command(data)
    # Wait until the connection is established.
    while (not fRecv):
        ble.check_activity(ser)
        time.sleep(0.01)
    return rcvData

def get_accel(data):
    global fAccel, rcvAccel, fRecv
    fAccel = True
    write_command(data)
    # Wait until the connection is established.
    while (fAccel):
        ble.check_activity(ser)
        time.sleep(0.01)
    return rcvAccel

def _sensorRead():
    global ble, ser, LOCK
    while True:
        with LOCK:
            ble.check_activity(ser)
        time.sleep(0.01)

def start_sensor_read():
    th_read = threading.Thread(target=_sensorRead)
    th_read.setDaemon(True)
    th_read.start()

def main():
    if len(sys.argv) != 2:
        print( "Usage: python %s port" % sys.argv[0])
        quit()

    port = sys.argv[1]
    start(port)

def start(port, address):
    global ble, ser, fConnection, fProcedureStarted
    ble = BGLib()
    ble.packet_mode = False
    ble.debug = False

    arr_addr = []
    arr_tmp = address.split(':')
    for i in range(len(arr_tmp) - 1, -1, -1):
        arr_addr.append(int(arr_tmp[i], 16))


    # add handler for BGAPI timeout condition (hopefully won't happen)
    ble.on_timeout += timeout_handler

    # Add Function
    ble.ble_evt_connection_status += handle_connection_status
    ble.ble_evt_attclient_procedure_completed += handle_procedure_completed
    ble.ble_rsp_attclient_write_command += handle_write_command
    ble.ble_evt_attclient_attribute_value += handle_receive

#    if len(sys.argv) != 2:
#        print( "Usage: python %s port" % sys.argv[0])
#        quit()

#    port = sys.argv[1]
    baudrate = 115200

    try:
        ser = serial.Serial(
            port=port, baudrate=baudrate, timeout=1, writeTimeout=1)
    except serial.SerialException as e:
        print( "\n" + ("=" * 20))
        print( "Port error (name='%s', baud='%ld'): %s" % (port, baudrate, e))
        print( "=" * 20)
        quit()

    # flush buffers
    ser.flushInput()
    ser.flushOutput()

    # disconnect if we are connected already
    ble.send_command(ser, ble.ble_cmd_connection_disconnect(0))
    ble.check_activity(ser, 1)

    # stop advertising if we are advertising already
    ble.send_command(ser, ble.ble_cmd_gap_set_mode(0, 0))
    ble.check_activity(ser, 1)

    # stop scanning if we are scanning already
    ble.send_command(ser, ble.ble_cmd_gap_end_procedure())
    ble.check_activity(ser, 1)

    # set advertising parameters
    ble.send_command(
        ser, ble.ble_cmd_gap_set_adv_parameters(0x640, 0x640, 0x07))
    ble.check_activity(ser, 1)

    # set TX power level
    ble.send_command(ser, ble.ble_cmd_hardware_set_txpower(15))
                     # range 0 to 15 (real TX power from -23 to +3dBm)
    ble.check_activity(ser, 1)

    ### connect to Studuino
    print("Connecting to the device.")
    #ble.send_command(ser, ble.ble_cmd_gap_connect_direct((0x77, 0x14, 0xe4, 0x2f, 0x1b, 0xf4), 1, 60, 76, 100, 0))
    ble.send_command(ser, ble.ble_cmd_gap_connect_direct(arr_addr, 1, 60, 76, 100, 0))
    # Wait until the connection is established.
    while (not fConnection):
        ble.check_activity(ser)
        time.sleep(0.01)


    ### Service discover
    # print("Service discover.")
    fProcedureStarted = True
    ble.send_command(ser, ble.ble_cmd_attclient_read_by_group_type(0, 1, 65535, (0x00, 0x28)))
    # Wait until the procedure is done.
    while (fProcedureStarted):
        ble.check_activity(ser)
        time.sleep(0.01)

    ### Characteristics discover
    # print("Charcteristics discover.")
    fProcedureStarted = True
    ble.send_command(ser, ble.ble_cmd_attclient_read_by_type(0, 9, 15, (0x03, 0x28)))
    # Wait until the procedure is done.
    while (fProcedureStarted):
        ble.check_activity(ser)
        time.sleep(0.01)

    ### Descriptor discover
    # print("Descriptor discover.")
    fProcedureStarted = True
    ble.send_command(ser, ble.ble_cmd_attclient_find_information(0, 12, 12))
    # Wait until the procedure is done.
    while (fProcedureStarted):
        ble.check_activity(ser)
        time.sleep(0.01)

    ### Read characteristics notification on
    # print("notification on.")
    fProcedureStarted = True
    ble.send_command(ser, ble.ble_cmd_attclient_read_long(0, 10))
    # Wait until the procedure is done.
    while (fProcedureStarted):
        ble.check_activity(ser)
        time.sleep(0.01)

    ### Set Enable notification 
    # print("set enable notification.")
    fProcedureStarted = True
    ble.send_command(ser, ble.ble_cmd_attclient_write_command(0, 12, (0x01, 0x00)))
    # Wait until the procedure is done.
    while (fProcedureStarted):
        ble.check_activity(ser)
        time.sleep(0.01)

    print("started.")

def stop():
    global ser, ble
    # disconnect if we are connected already
    ble.send_command(ser, ble.ble_cmd_connection_disconnect(0))
    ble.check_activity(ser, 1)

    # stop advertising if we are advertising already
    ble.send_command(ser, ble.ble_cmd_gap_set_mode(0, 0))
    ble.check_activity(ser, 1)

    # stop scanning if we are scanning already
    ble.send_command(ser, ble.ble_cmd_gap_end_procedure())
    ble.check_activity(ser, 1)

    print("stopped")

def addReceiveHandler(handler):
    ble.ble_evt_attclient_attribute_value += handler

def waitSyncFinish():
    global fInSync, LOCK
    fInSync = True
    while fInSync:
        with LOCK:
            ble.check_activity(ser)
            time.sleep(0.01)

if __name__ == "__main__":
    main()
