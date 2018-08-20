"""
Copyright (c) 2015-2016 __Loxoll__. All rights reserved.
"""
#
# This module is designed to manage all SDU related activities. No other module needs to understand SDU protocol. 
#     Foe each HA-AP engine, SDU needs to sign on and remain sign-on until the GUI program closed. for that reason,
#     Each engine should starts its own instance of xSDU, to service upper level applications such as WatchHAAP
#     and CinfigHAAP.
#
#
import sys
from struct import *
from array import *
from binascii import hexlify
 
from ParseUtil import ParseUtil
from ControlTCP import xTCP

file_name = os.path.basename(__file__)

#cfg = ParseUtil('Config.ini')


CMD_SIGN_ON                 = 0x100
CMD_SIGN_OFF                = 0x101
CMD_ABORT                   = 0x102
CMD_SIGN_ON_FORCE           = 0x103


CMD_SET_SIGNON_PATH_INFO    = 0x110
CMD_RETRIEVE_SIGNON_PATH_INFO   = 0x111

CMD_QUERY_UPLOAD            = 0x200
#    /* ARG0 = which block to upload. ARG1 = node number */
CMD_UPLOAD                  = 0x201
#    /* ARG0 = offset into data. ARG1 = #bytes in this block */
#    /* ARG2/3 = SLIC UID */
CMD_SERIAL_UPLOAD           = 0x202   #/* SCSI read serial port */
QUERY_DB1_ENTRY             = 0x240
QUERY_SLIC_I_ENTRY          = 0x241

CMD_QUERY_LOCAL_ENGINE_IP_INFO  = 0x263

CMD_QUERY_CHANGE            = 0x900
#    /* ARG0 = subtype: 0 = general, 1 = HS statistics, 2 = DS statistics */
#    /* ARG2/3 = SLIC UID */

#
# SDU executive class, service all SDU related requests 
#
class xSDU(object):

    def __init__(self):
        dbg.printDBG1(file_name, "initiate xSDU")
#
# Define the parameters needed for the life of the instance (to manage the HA-AP engine through SDU)
        self.sendBuffer = array('B',[0 for x in range(0x400)])
        self.receiveBuffer = array('B',[0 for x in range(0x400)])
        self.sequence_num = 0

# Connect the TCP socket to this engine, and keep it open until the program close
        self.stcp = xTCP()
        self.stcp.startTCPclient()
        
# Sign On the specified engine when initializee the instance
        self.sendSDU(cmd=CMD_SIGN_ON)
#
# Methods for upper level applications
#    getInfo () - get engine's updated status 
#    putConfig () - configure engine
#   
    def getInfo(self):
        self.receivedBuffer = self.sendSDU(cmd=CMD_QUERY_CHANGE)
        magic, seq_num, opcode, status, rv1, rv2 = self.decodeSDU()
        print "\n", hex(magic), hex(seq_num), hex(opcode), hex(status), hex(rv1), hex(rv2)
        print hexlify(self.y)

    def putConfig(self):
        pass
#
# Internal functions to service the Methods for applications
#
    def sendSDU(self, cmd):
        self.encodeSDU(opcode = cmd)
        self.sequence_num += 1        
        print hexlify(self.sendBuffer)
        return self.stcp.get_data_from_TCP(self.sendBuffer)        
#
# Internal sub-functions to service other internal functions
#
    def encodeSDU(self, magic=0x5555aaaa, opcode=CMD_SIGN_ON, arg0=0, arg1=0):
        self.sendBuffer[:4] = self.int_to_bytes(magic)
        self.sendBuffer[4:8] = self.int_to_bytes(self.sequence_num)
        self.sendBuffer[8:12] = self.int_to_bytes(opcode)
        self.sendBuffer[12:16] = self.int_to_bytes(arg0)
        self.sendBuffer[16:20] = self.int_to_bytes(arg1)
#        self.sendBuffer[20:28] = self.str_to_bytes(cfg['Engine0']['WWN'])
        self.sendBuffer[28:32] = self.get_checksum(28)
        for i in range (32, 0x400): self.sendBuffer[i] = 0
      
    def decodeSDU(self):
        magic = self.int_from_bytes(self.receiveBuffer[:4])        
        seq_num = self.int_from_bytes(self.receiveBuffer[4:8])
        opcode = self.int_from_bytes(self.receiveBuffer[8:12])
        status = self.int_from_bytes(self.receiveBuffer[12:16])
        if self.verify_checksum(16, self.receiveBuffer) != 0: print "CheckSum Error..."
        rv1 = self.int_from_bytes(self.receiveBuffer[20:24])
        rv2 = self.int_from_bytes(self.receiveBuffer[24:28])
        WWN = self.str_from_bytes(self.receiveBuffer[20:28])
        return (magic, seq_num, opcode, status, rv1, rv2)
        
    def int_from_bytes(self, *args):
        return (((((ord(args[0][3]) << 8) + ord(args[0][2])) << 8) + ord(args[0][1])) << 8) + ord(args[0][0])        
#        return (((((ord(args[0][0]) << 8) + ord(args[0][1])) << 8) + ord(args[0][2])) << 8) + ord(args[0][3])        

    def str_from_bytes(self, a):
        s = ""
        for i in range (8): s += format(ord(a[i]), '02x')
        return s.upper()

    def int_to_bytes(self, i):
        return array('B', [(i & (0xff << pos*8)) >> pos*8 for pos in range(0, 4, 1)])
#        return array('B', [(i & (0xff << pos*8)) >> pos*8 for pos in range(3, -1, -1)])

    def str_to_bytes(self, s):
        d = {'0':0,'1':1,'2':2,'3':3,'4':4,'5':5,'6':6,'7':7,'8':8,'9':9, \
             'A':10, 'a':10, 'B':11, 'b':11, 'C':12, 'c':12, 'D':13, 'd':13, 'E':14, 'e':14, 'F':15, 'f':15}
        return array('B', [(d[s[0+2*pos]]*16 + d[s[1+2*pos]]) for pos in range(0, 8)])

    def get_checksum(self, max):
        max = max/4
        t = array('B', [0 for x in range(4)])
        for j in range (0, 4):
            t[j] = 0
            for p in range (0, max):            
                t[j] = int(t[j]) ^ int(self.sendBuffer[j+p*4])
        return t
       
    def verify_checksum(self, max, test_array):
        max = max/4
        t = array('B', [0 for x in range(4)])
        for j in range (0, 4):
            t[j] = 0
            for p in range (0, max+1):            
                t[j] = t[j] ^ ord(test_array[j+p*4])
        for j in range(1, 4): t[0] |= t[j]
        return t[0] 


    def prepareSDUC(self):
        pass


    def executeSDUC(self):
        pass


    def receiveSDUC(self):
        pass


    def prepareSDUS(self):
        pass


    def executeSDUS(self):
        pass


    def receiveSDUS(self):
        pass



if __name__ == '__main__':
    p = xSDU()
    p.encodeSDU()
    p.decodeSDU()
    sys.exit()

