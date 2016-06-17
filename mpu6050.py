#!/usr/bin/python
#coding:utf-8

import serial
import struct

# SerName = "/dev/cu.usbserial";
SerName = "/dev/cu.usbserial-AL0172VQ";
BPS = 115200;

DATAFIRSTBYTE       = 0xA7;
DATASECONDBYTE      = 0x7A;

def gyroDPS(data):
    pass

dataCmdDict = {
        0x60: "All Gyro ACC Angle",
        0x70: "gyroDPS",
        0x71: "ACC",
        0x72: "Angle",
        0x73: "Mag",
        0x74: "Temperature",
        0x75: "Altitude",
};

cmdBufHeaderList    = [0xD6, 0x6D, 0x00, 0x00];

CMDRESET            = 0x01;
CMDAUTOOUTPUT       = 0x06;
CMDONOUTPUT         = 0x08;
CMDOFFOUTPUT        = 0x09;
CMDONALL            = 0x20;
CMDOFFALL           = 0x21;
CMDONANGLE          = 0x24;
CMDOFFANGLE         = 0x25;

class Gump_Uart(object):
    ser = 0;

    def __init(self):
        pass

    def openPort(self, name, bps):
        self.ser = serial.Serial(name, bps);

    def waitStart(self):
        data = 0;
        # print "wait Start Flag";
        while (data != DATAFIRSTBYTE):
            data = struct.unpack("B", self.ser.read(1))[0];
            # print "read first data=0x%x" % (data)
        while (data != DATASECONDBYTE):
            data = struct.unpack("B", self.ser.read(1))[0];
            # print "read second data=0x%x" % (data)

    def checkSum(self, pack):
        calcsum = 0x00;
        length = len(pack);
        readformat = "{:d}B".format(length);
        buf = struct.unpack(readformat, pack);
        for i in buf:
            calcsum ^= i;
        # print length, calcsum;
        if calcsum == 0:
            return True;
        else :
            return False;

    def readData(self):
        data = [];
        (cmdtype, length) = struct.unpack("2B", self.ser.read(2));
        if (length > 6) and (length < 20):
            packet = self.ser.read(length);
            if self.checkSum(packet) == True:
                readformat = "<{:d}h".format((length-1)/2);
                data = struct.unpack(readformat, packet[1:]);
            # print readformat, data;
        # print "cmd header type=0x%0x length=%d" % (cmdtype, length);
        return cmdtype, data;

    def sendCmd(self, data1, data2):
        cmdBufHeaderList[2] = data1;
        cmdBufHeaderList[3] = data2;
        print cmdBufHeaderList;
        self.ser.write(cmdBufHeaderList);

    def sendOnOutput(self):
        self.sendCmd(CMDONOUTPUT, CMDONOUTPUT);

    def sendAutoOutput(self):
        self.sendCmd(CMDAUTOOUTPUT, CMDAUTOOUTPUT);

    def sendAllOutput(self):
        self.sendCmd(CMDONALL, CMDONALL);

    def sendReset(self):
        self.sendCmd(CMDRESET, CMDRESET);


if __name__ == '__main__':
    mpu6050 = Gump_Uart();
    mpu6050.openPort(SerName, BPS);
    # mpu6050.sendAutoOutput();
    mpu6050.sendOnOutput();
    # mpu6050.sendReset();
    mpu6050.sendAllOutput();
    # for i in range(100):
    while True:
        mpu6050.waitStart();
        cmdtype, data = mpu6050.readData();
        print dataCmdDict[cmdtype], repr(data);
