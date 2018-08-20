"""
Copyright (c) 2015-2016 __Loxoll__. All rights reserved.
"""
#
# This module is designed to manage all TCP related activities. No other module needs to understand TCP protocol. 
#     Foe each HA-AP engine, TCP socket needs to be connected and remain connected until the GUI program closed.
#     for that reason, each engine should starts its own instance of xTCP, to service upper level applications such
#     as xSDU.
#
import sys, time, os
from array import *
import socket               # Imports socket module
from binascii import hexlify

file_name = os.path.basename(__file__)
#
# TCP executive class, service all TCP related requests 
#

IP_PORT = 25000

class xTCP(object):
    
    data = array('B',[0 for x in range(0x400)])
    
    def __init__(self):
        dbg.printDBG1(file_name, "initiate xTCP")
#
# TCP server, echo the data back for testing
    def startTCPserver(self):
        
        print TCP_info
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        host = TCP_info["server"]
        if host == "": host = socket.gethostname()

        print "IP :", host, " Port :", TCP_info["port"]
        s.bind((host, int(TCP_info["port"])))
        s.listen(1)                 # Sets socket to listening state with a  queue
                                    #      of 1 connection
        print "Listening for TCP connections.. "
        q, addr = s.accept()     # Accepts incoming request from client and returns
        print 'Connected with ' + addr[0] + ':' + str(addr[1])

        while 1:
            data = q.recv(0x400)
#            print hexlify(data)
            q.send(data)         # echo back the received data for test
#
        q.close()    
        s.close()
        print "Terminated TCP connections" 
#
# abort the TCP server
    def sendAPI(self):       
#       
        BUFFER_SIZE = 0x400
        
        s = socket.socket()
        s.settimeout(5)   # 5 seconds
        try:
            s.connect((API_info["server"], int(API_info["port"])))
            print "IP :", API_info["server"], " Port :", API_info["port"]
        except socket.error, exc:
            print "Try to connect to IP : \"%s\", Port : %s" % (API_info["server"], API_info["port"])
            print "But, got exception socket error : %s" % exc
#
        if API_info["slot1_1"] != "":
            s.send( self.str_to_4bytes(API_info["slot1_1"])+
                    self.str_to_4bytes(API_info["slot1_2"])+
                    self.str_to_4bytes(API_info["slot1_3"])+
                    self.str_to_2bytes(API_info["slot1_4"])+
                    self.str_to_2bytes(API_info["slot1_5"])+
                    self.str_to_8bytes(API_info["slot1_6"])+
                    500*(self.str_to_2bytes("0000")))
            print self.str_to_4bytes(API_info["slot1_1"])+      \
                    self.str_to_4bytes(API_info["slot1_2"])+    \
                    self.str_to_4bytes(API_info["slot1_3"])+    \
                    self.str_to_2bytes(API_info["slot1_4"])+    \
                    self.str_to_2bytes(API_info["slot1_5"])+    \
                    self.str_to_8bytes(API_info["slot1_6"])
            print "Response :", hexlify(s.recv(BUFFER_SIZE))
        #
        if API_info["slot2_1"] != "":
            s.send( self.str_to_4bytes(API_info["slot2_1"])+
                    self.str_to_4bytes(API_info["slot2_2"])+
                    self.str_to_4bytes(API_info["slot2_3"])+
                    self.str_to_2bytes(API_info["slot2_4"])+
                    self.str_to_2bytes(API_info["slot2_5"])+
                    self.str_to_8bytes(API_info["slot2_6"])+
                    500*(self.str_to_2bytes("0000")))
            print self.str_to_4bytes(API_info["slot2_1"])+      \
                    self.str_to_4bytes(API_info["slot2_2"])+    \
                    self.str_to_4bytes(API_info["slot2_3"])+    \
                    self.str_to_2bytes(API_info["slot2_4"])+    \
                    self.str_to_2bytes(API_info["slot2_5"])+    \
                    self.str_to_8bytes(API_info["slot2_6"])
            print "Response :", hexlify(s.recv(BUFFER_SIZE))

        #
        if API_info["slot3_1"] != "":
            s.send( self.str_to_4bytes(API_info["slot3_1"])+
                    self.str_to_4bytes(API_info["slot3_2"])+
                    self.str_to_4bytes(API_info["slot3_3"])+
                    self.str_to_2bytes(API_info["slot3_4"])+
                    self.str_to_2bytes(API_info["slot3_5"])+
                    self.str_to_8bytes(API_info["slot3_6"])+
                    500*(self.str_to_2bytes("0000")))
            print self.str_to_4bytes(API_info["slot3_1"])+      \
                    self.str_to_4bytes(API_info["slot3_2"])+    \
                    self.str_to_4bytes(API_info["slot3_3"])+    \
                    self.str_to_2bytes(API_info["slot3_4"])+    \
                    self.str_to_2bytes(API_info["slot3_5"])+    \
                    self.str_to_8bytes(API_info["slot3_6"])
            print "Response :", hexlify(s.recv(BUFFER_SIZE))

        s.close()
#
    def sendLPS(self):       
#
# Please provide a Python script that opens a socket to the 
# engine's port 25002, then opens a second one without explicitly closing the first.
#
        BUFFER_SIZE = 0x400
        
        s = socket.socket()
        s.settimeout(5)   # 5 seconds
        try:
            print "connecting 1... IP :", LPS_info["server"], " Port :", LPS_info["port"]
            s.connect((LPS_info["server"], int(LPS_info["port"])))
        except socket.error, exc:
            print "Try to connect to IP : \"%s\", Port : %s" % (LPS_info["server"], LPS_info["port"])
            print "But, got exception socket error : %s" % exc
            print "closed 1... IP :", LPS_info["server"], " Port :", LPS_info["port"]
            s.close()
#
        t = socket.socket()
        t.settimeout(5)   # 5 seconds
        try:
            print "connecting 2... IP :", LPS_info["server"], " Port :", LPS_info["port"]
            t.connect((LPS_info["server"], int(LPS_info["port"])))
        except socket.error, exc:
            print "Try to connect to IP : \"%s\", Port : %s" % (LPS_info["server"], LPS_info["port"])
            print "But, got exception socket error : %s" % exc
            print "closed 2... IP :", LPS_info["server"], " Port :", LPS_info["port"]
            t.close()
#
        time.sleep(5)
        print "closed 1... IP :", LPS_info["server"], " Port :", LPS_info["port"]
        s.close()
        print "closed 2... IP :", LPS_info["server"], " Port :", LPS_info["port"]
        t.close()
#
    def str_to_8bytes(self, s):
        d = {'0':0,'1':1,'2':2,'3':3,'4':4,'5':5,'6':6,'7':7,'8':8,'9':9, \
            'A':10, 'a':10, 'B':11, 'b':11, 'C':12, 'c':12, 'D':13, 'd':13, 'E':14, 'e':14, 'F':15, 'f':15}
        return array('B', [(d[s[0+2*pos]]*16 + d[s[1+2*pos]]) for pos in range(0, 8)])
#
    def str_to_4bytes(self, s):
        d = {'0':0,'1':1,'2':2,'3':3,'4':4,'5':5,'6':6,'7':7,'8':8,'9':9, \
            'A':10, 'a':10, 'B':11, 'b':11, 'C':12, 'c':12, 'D':13, 'd':13, 'E':14, 'e':14, 'F':15, 'f':15}
        return array('B', [(d[s[0+2*pos]]*16 + d[s[1+2*pos]]) for pos in range(0, 4)])
#
    def str_to_2bytes(self, s):
        d = {'0':0,'1':1,'2':2,'3':3,'4':4,'5':5,'6':6,'7':7,'8':8,'9':9, \
            'A':10, 'a':10, 'B':11, 'b':11, 'C':12, 'c':12, 'D':13, 'd':13, 'E':14, 'e':14, 'F':15, 'f':15}
        return array('B', [(d[s[0+2*pos]]*16 + d[s[1+2*pos]]) for pos in range(0, 2)])
    
# TCP client...
    def startTCPclient(self):

        host = socket.gethostname()
        self.talk_to_engine=socket.socket(socket.AF_INET, socket.SOCK_STREAM)      # Creates a socket
        self.talk_to_engine.settimeout(10)
        self.talk_to_engine.connect(host, IP_PORT)

    def get_data_from_TCP(self, send):

        self.talk_to_engine.send(send)
        return self.talk_to_engine.recv(0x400)


network = '192.168.1.'

def PingEngine (engine_ip):
#    print engine_ip
    PORT = "25000"
#    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sh = socket.socket()
    sh.settimeout(1)    ## set a timeout of 1 sec
    for i in range (0, 1): # try once
        result = sh.connect_ex((engine_ip, int(PORT)))  # connect to the remote host on port 25000
                                                    ## (port 25000 is always open for HA-AP engine)
#        print ".... ", result
        if result > 0:
            dbg.printDBG2(file_name, "can not connect to engine: %s port: %s, retry=%s" %(engine_ip, PORT, i))
        else:           # everything is OK!
            dbg.printDBG2(file_name, "connected to engine: %s port: %s, retry=%s" %(engine_ip, PORT, i))
            sh.close()
            return True
    sh.close()
    return False

def ScanAllEngine():
    dbg.printDBG1(file_name, "invoke ScanAllEngine")

    print ""
    for ip in xrange(1,256):    ## 'ping' addresses 192.168.1.1 to .1.255
        addr = network + str(ip)
        if PingEngine(addr):
            print '%s \t- %s' %(addr, getfqdn(addr))    ## the function 'getfqdn' returns the remote hostname
    print    ## just print a blank line


if __name__ == '__main__':
    
    print "I'm scanning the local network for connected HA-AP engine."
    print "This might take some time, depending on the number of the PC's found. Please wait..."
    run()

    raw_input('Done')
    sys.exit()

