#!/usr/bin/python
#coding:utf-8

import serial
import struct

SerName = "/dev/cu.usbserial";
BPS = 115200;

DATAFIRSTBYTE       = 0xA7;
DATASECONDBYTE      = 0x7A;

def gyroDPS(data):
    pass

dataCmdDict = {
        0x70: gyroDPS,
};

class Gump_Uart(object):
    ser = 0;

    def __init(self):
        pass

    def openport(self, name, bps):
        self.ser = serial.Serial(name, bps);

    def waitstart(self):
        data = 0;
        while (data != DATAFIRSTBYTE):
            data = struct.unpack("B", self.ser.read(1))[0];
            print "read first data=0x%x" % (data)
        while (data != DATASECONDBYTE):
            data = struct.unpack("B", self.ser.read(1))[0];
            print "read second data=0x%x" % (data)

    def readdata(self):
        data = [];
        length = struct.unpack("B", self.ser.read(1))[0];
        if (length > 6) and (length < 20):
            packet = self.ser.read(length);
            readformat = "{:d}B".format(length);
            data = struct.unpack(readformat, packet);


if __name__ == '__main__':
    mpu6050 = Gump_Uart();
    mpu6050.openport(SerName, BPS);
    mpu6050.waitstart();
    data = mpu6050.readdata();
    print repr(data);
