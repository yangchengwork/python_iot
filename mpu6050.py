#!/usr/bin/python
#coding:utf-8

import serial
import struct
import time
import Gnuplot
from numpy import *

# SerName = "/dev/cu.usbserial";
# Mac OSX 
# SerName = "/dev/cu.usbserial-AL0172VQ";
# Linux
SerName = "/dev/ttyUSB1";
# Windows 10
# SerName = "/dev/ttyS2";
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

MAXXSIZE            = 500;

class Gump_Uart(object):
    ser = 0;
    accX = [[0, 0]];
    accY = [[0, 0]];
    accZ = [[0, 0]];
    gp = 0;
    plotAccX = 0;
    plotAccY = 0;
    plotAccZ = 0;
    conut = 0;

    def __init(self):
        pass

    def openPort(self, name, bps):
        self.ser = serial.Serial(name, bps);
        self.gp = Gnuplot.Gnuplot(persist=1);
        self.gp("set title x11 size 800,600");
        # self.gp('set yrange [-32767:32768]')
        self.gp('set yrange [-4096:4096]')
        self.count = 0;

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

    def allDataAnsisy(self, data):
        self.count = self.count + 1;
        if self.count >= MAXXSIZE:
            self.accX = self.accX[1:];
            self.accY = self.accY[1:];
            self.accZ = self.accZ[1:];
            self.count = MAXXSIZE - 1;
        i = 0;
        while i < self.count - 1:
            self.accX[i] = [i, self.accX[i+1][1]];
            self.accY[i] = [i, self.accY[i+1][1]];
            self.accZ[i] = [i, self.accZ[i+1][1]];
            i = i + 1;
        self.accX.append([self.count, data[3]]);
        self.accY.append([self.count, data[4]]);
        self.accZ.append([self.count, data[5]]);
        if len(self.accX) > 2:
            # print repr(self.accX), repr(self.accY), repr(self.accZ);
            self.plotAccX = Gnuplot.PlotItems.Data(self.accX, with_="linespoints lt rgb 'red' lw 6 pt 1", title="Acc X");
            self.plotAccY = Gnuplot.PlotItems.Data(self.accY, with_="linespoints lt rgb 'yellow' lw 6 pt 1", title="Acc Y");
            self.plotAccZ = Gnuplot.PlotItems.Data(self.accZ, with_="linespoints lt rgb 'blue' lw 6 pt 1", title="Acc Z");
            self.gp.plot(self.plotAccX, self.plotAccY, self.plotAccZ); 
            # self.gp.plot(self.accX, self.accY, self.accZ); 


if __name__ == '__main__':
    mpu6050 = Gump_Uart();
    mpu6050.openPort(SerName, BPS);
    # mpu6050.sendAutoOutput();
    mpu6050.sendOnOutput();
    # mpu6050.sendReset();
    mpu6050.sendAllOutput();
    # for i in range(100):
    i = 0;
    success = 0;
    fail = 0;
    tt0 = time.time();
    ct0 = time.clock();
    while i < 10000:
        mpu6050.waitStart();
        cmdtype, data = mpu6050.readData();
        if (len(data) > 0) :
            success = success + 1;
            # print dataCmdDict[cmdtype], repr(data);
            if (cmdtype == 0x60) :
                mpu6050.allDataAnsisy(data);
        else :
            fail = fail + 1;
	    if dataCmdDict.has_key(cmdtype):
                print "CRC Error CMD " + dataCmdDict[cmdtype];
	    else:
	        print "cmdtype=0x%02x" % (cmdtype);
        i = i + 1;

    tt1 = time.time();
    ct1 = time.clock();
    print "total read 10K time=%f cputime=%f success=%d fail=%d" % (tt1-tt0, ct1-ct0, success, fail);
