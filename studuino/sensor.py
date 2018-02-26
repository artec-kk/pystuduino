# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

DTYPE_1ST = 0 << 6
DTYPE_2ND = 1 << 6
DTYPE_EXT = 2 << 6
MSK_DTYPE = 0xC0

EXT_TYPE_SYNCFINISH = 0x1f
EXT_TYPE_ACK = 0x00
EXT_TYPE_NACK = 0x01
MSK_EXT_DTYPE = 0x3f

class SensorManager:
    def __init__(self):
        self.readState = 0
        self.sensorValue = [-1] * 11;
        self.statWrite = 0    # 0: none 1: waiting -1: NACK
        self.statSyncServo = 0

    def parseData(self, data):
        #print('Num data: ', len(data))
        for i in range(0, len(data)):
            #print(data[i])
            if (data[i] & MSK_DTYPE) == DTYPE_1ST:
                if not self.readState == 0:
                    continue
                self.data1 = data[i]
                self.readState = 1
            elif (data[i] & MSK_DTYPE) == DTYPE_2ND:
                if not self.readState == 1:
                    continue
                self.data2 = data[i]
                port = (self.data1 >> 2) & 0x0f
                val = ((self.data1 & 0x03) << 6) | (self.data2 & 0x3f)
                self.sensorValue[port] = val
                self.readState = 0
                #print('sensor update')
            elif (data[i] & MSK_DTYPE) == DTYPE_EXT:
                if data[i] & MSK_EXT_DTYPE == EXT_TYPE_SYNCFINISH:
                    #print('sync stop')
                    self.statSyncServo = 0
                if data[i] & MSK_EXT_DTYPE == EXT_TYPE_ACK:
                    #print('ACK received.')
                    self.statWrite = 0
                if data[i] & MSK_EXT_DTYPE == EXT_TYPE_NACK:
                    self.statWrite = -1

    def getValue(self, index):
        return self.sensorValue[index]

    def startWaitingWriteResponse(self):
        self.statWrite = 1

    def getWriteFlag(self):
        return self.statWrite

    def startSyncServo(self):
        self.statSyncServo = 1

    def getSyncServoFlag(self):
        return self.statSyncServo
