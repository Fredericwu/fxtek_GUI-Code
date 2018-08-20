"""
Control Switch Module

Created by Susan Cheng on 2015-11-27.
Copyright (c) 2015-2016 __Loxoll__. All rights reserved.
"""
#
# This module is designed to manage all FC Switch related activities.
#
import os, sys, time, glob
import datetime
from telnetlib import Telnet
import tkMessageBox

file_name = os.path.basename(__file__)

class xSwitch(object):

    def __init__(self):
        dbg.printDBG2(file_name, "initiate xSwitch")

    def getInfoFromSwitch(self, clear_count = False):
        dbg.printDBG2(file_name, "getInfoFromSwitch clear = %s" % clear_count)
        self.tracepath = './trace/'

        for k, d in switch_info.iteritems():
            if k[:-1] == "sip" and d != "":
                self.switch_ip = d
                self.prefix = 'X%s-' % k[3]

                # count the .xtc files
                xtc_file_count = 0
                for file in glob.glob(os.path.join(self.tracepath, self.prefix+'*.xtc')): xtc_file_count += 1     

                while xtc_file_count >= 2: # keep only 10 .xtc files
                # find the oldest file
                    oldest_file, oldest_time = None, None
                    for dirpath, dirs, files in os.walk(self.tracepath):
                        for filename in files:
                            file_path = os.path.join(dirpath, filename)
                            file_time = os.stat(file_path).st_mtime
                            if file_path.endswith(".xtc") and file_path.startswith (self.tracepath + self.prefix) and \
                                (file_time<oldest_time or oldest_time is None):
                                oldest_file, oldest_time = file_path, file_time
            
                    # remove the oldest file
                    if os.path.isfile(oldest_file): os.remove(oldest_file)
            
                    # count the .xtc files again
                    xtc_file_count = 0
                    for file in glob.glob(os.path.join(self.tracepath, self.prefix+'*.xtc')): xtc_file_count += 1

                self.xtc_file_name = self.tracepath + self.prefix + datetime.datetime.now().strftime('%m%d%H%M%S') + '.xtc'
                self.f = open(self.xtc_file_name, 'w')
        
                time_stamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
                self.f.write( "Switch Vendor : " + switch_info["switch_type"] + "\n")
                self.f.write( "Telnet to : " + self.switch_ip + ", Time Stamp : " + time_stamp + "\n")
                self.f.close()

                try:
                    self.tn = Telnet(self.switch_ip, timeout = TWO_SECOND)
                except:
                    dbg.printDBG3(file_name, "telnet time-out : %s" % self.switch_ip)
                    print "Telnet time-out! ", self.switch_ip
                    return False
                #
                self.logfile = open( self.xtc_file_name, 'a')
                self.logfile.write( self.tn.read_lazy())
#
                if switch_info["switch_type"] == "Brocade": return self.__GetBrocadeTrace(clear_count)
                elif switch_info["switch_type"] == "Cisco": return self.__GetCiscoTrace(clear_count)
                elif switch_info["switch_type"] == "QLogic": return self.__GetQLogicTrace(clear_count)
                elif switch_info["switch_type"] == "Test": return self.__GetLoxollTrace(clear_count)
#
    def checkSwitchError(self):
        switch_err = {}
        for k, d in switch_info.iteritems():
            if k[:-1] == "sip" and d != "":
                f = self.__getXTCfile(int(k[-1:]))
                if switch_info["switch_type"] == "Brocade":
                    if self.__GetBrocadeError(f) == False: return False
                elif switch_info["switch_type"] == "Cisco": 
                    if self.__GetCiscoError(f) == False: return False
                elif switch_info["switch_type"] == "QLogic": 
                    if self.__GetQLogicError(f) == False: return False
                elif switch_info["switch_type"] == "Test": 
                    if self.__GetLoxollError(f) == False: return False
        return True

    def __getXTCfile(self, index):

        tracepath = './trace/'
        if not os.path.exists(tracepath):
            dbg.printDBG1 (file_name, 'no tracepath error')
        prefix = 'X%s-' % index
        
        # count the .xtc files
        xtc_file_count = 0
        for file in glob.glob(os.path.join(tracepath, prefix+'*.xtc')): xtc_file_count += 1

        # find the newest file
        newest_file, newest_time = None, None
        for dirpath, dirs, files in os.walk(tracepath):
            for filename in files:
                file_path = os.path.join(dirpath, filename)
                file_time = os.stat(file_path).st_mtime
                if file_path.endswith(".xtc") and file_path.startswith (tracepath + prefix) and \
                    (file_time>newest_time or newest_time is None):
                    newest_file, newest_time = file_path, file_time
        return newest_file
    
    def __GetLoxollTrace(self, clear_count):

        PROMPT1 = " > "
        PROMPT2 = "CL>"
        if switch_info["prompt1"] != "": PROMPT1 = switch_info["prompt1"][1:-1]
        if switch_info["prompt2"] != "": PROMPT2 = switch_info["prompt2"][1:-1]

        if (self.InputToExpect( "", "password: ", 2) == False): self.logfile.close(); return False
        if (self.InputToExpect( switch_info["sww"]+"\r", PROMPT1) == False): self.logfile.close(); return False
        if (self.InputToExpect( "7", PROMPT2) == False): self.logfile.close(); return False
        if (self.InputToExpect( "vpd\r", PROMPT2) == False): self.logfile.close(); return False
        if (self.InputToExpect( "mirror\r", PROMPT2) == False): self.logfile.close(); return False
        if (self.InputToExpect( "conmgr engine status\r", PROMPT2) == False): self.logfile.close(); return False
        if (self.InputToExpect( "conmgr drive status\r", PROMPT2) == False): self.logfile.close(); return False
        if (self.InputToExpect( "conmgr initiator status\r", PROMPT2) == False): self.logfile.close(); return False
        if (self.InputToExpect( "port\r", PROMPT2) == False): self.logfile.close(); return False
        if (self.InputToExpect( "engine\r", PROMPT2) == False): self.logfile.close(); return False
        if (self.InputToExpect( "license status\r", PROMPT2) == False): self.logfile.close(); return False
        if (self.InputToExpect( "drvstate\r", PROMPT2) == False): self.logfile.close(); return False
        if (self.InputToExpect( "2nd new\r", PROMPT2) == False): self.logfile.close(); return False
        if (self.InputToExpect( "exit\r", PROMPT1) == False): self.logfile.close(); return False
        if (self.InputToExpect( "q", "(Y/N)") == False): self.logfile.close(); return False
        if (self.InputToExpect( "y", "Bye!") == False): self.logfile.close(); return False
        self.logfile.close(); return True
#
    def __GetBrocadeTrace(self, clear_count):
        print "Brocade", switch_info["suu"], switch_info["sww"]
        PROMPT1 = "> "
        PROMPT2 = "> "
        if switch_info["prompt1"] != "": PROMPT1 = switch_info["prompt1"][1:-1]
        if switch_info["prompt2"] != "": PROMPT2 = switch_info["prompt2"][1:-1]

        if (self.InputToExpect( "", "login: ", 30) == False): self.logfile.close(); return False
        if (self.InputToExpect( switch_info["suu"]+"\r", "Password: ", 5) == False): self.logfile.close(); return False
        if (self.InputToExpect( switch_info["sww"]+"\r", PROMPT1, 30) == False): self.logfile.close(); return False
        if (self.InputToExpect( "switchshow\r", PROMPT1) == False): self.logfile.close(); return False
        if (self.InputToExpect( "cfgshow\r", PROMPT1) == False): self.logfile.close(); return False
        if (self.InputToExpect( "porterrshow\r", PROMPT1) == False): self.logfile.close(); return False
#
#        print self.section
        lines = self.section.split("\n")
        length = len(lines)
        switch_name = lines[length-1].split(":")[0]             # swd77:root> 
        port_number = int(lines[length-2].split(":")[0])+1      # 23:    0 ...
#        print switch_name, port_number
        for i in range (port_number):
            if (self.InputToExpect( "portshow %s\r" % i, PROMPT1) == False): self.logfile.close(); return False
            if clear_count == True:
                if (self.InputToExpect( "portstatsclear %s\r" % i, PROMPT1) == False): self.logfile.close(); return False
        if (self.InputToExpect( "logout\r", "", 10) == False): self.logfile.close(); return False
        self.logfile.close(); return True
#
    def __GetQLogicTrace(self, clear_count):
        print "QLogic", switch_info["suu"], switch_info["sww"]
        PROMPT1 = "#> "
        PROMPT2 = "#> "
        if switch_info["prompt1"] != "": PROMPT1 = switch_info["prompt1"][1:-1]
        if switch_info["prompt2"] != "": PROMPT2 = switch_info["prompt2"][1:-1]

        if (self.InputToExpect( "", "login: ", 5) == False): self.logfile.close(); return False
        if (self.InputToExpect( switch_info["suu"]+"\n", "Password: ", 5) == False): self.logfile.close(); return False
        if (self.InputToExpect( switch_info["sww"]+"\n", PROMPT1) == False): self.logfile.close(); return False

        lines = self.section.split("\n")
        length = len(lines)
        for i in range (length):
            if lines[i].find('HostName') != -1: break
        switch_name = lines[i].split()[1]                   # HostName            5600
        start_idx = i + 1
        for i in range (start_idx, length):   
            if lines[i].find('LicensedPorts') != -1: break
        port_number = lines[i].split()[1]                   # LicensedPorts       20

        if (self.InputToExpect( "admin start\r", PROMPT2) == False): self.logfile.close(); return False
        for i in range (int(port_number)):
            if (self.InputToExpect( "show port %s\r" % i, PROMPT2) == False): self.logfile.close(); return False

        if clear_count == True:
            if (self.InputToExpect( "set port clear\r", PROMPT2) == False): self.logfile.close(); return False

        if (self.InputToExpect( "admin end\r", PROMPT1) == False): self.logfile.close(); return False
        if (self.InputToExpect( "quit\r", "bye.") == False): self.logfile.close(); return False
        self.logfile.close(); return True
#
    def __GetCiscoTrace(self, clear_count):
        print "Cisco", switch_info["suu"], switch_info["sww"]
        if (self.InputToExpect( "", "login: ", 2) == False): self.logfile.close(); return False
        if (self.InputToExpect( switch_info["suu"]+"\r", "password: ", 2) == False): self.logfile.close(); return False
        if (self.InputToExpect( switch_info["sww"]+"\r", "#") == False): self.logfile.close(); return False
        if (self.InputToExpect( "show fcs port\r", "#") == False): self.logfile.close(); return False
        if (self.InputToExpect( "show fcs statistics\r", "#") == False): self.logfile.close(); return False

        if clear_count == True:
#            if (self.InputToExpect( "set port clear\r", ">") == False): self.logfile.close(); return False
            pass

        if (self.InputToExpect( "quit", "Bye!") == False): self.logfile.close(); return False
        self.logfile.close(); return True
#
    def InputToExpect(self, put_string, check_string, time_out = 10):
        self.tn.write(put_string)
        self.logfile.write(put_string)  #!!!
        try:
            self.section = self.tn.read_until(check_string, timeout = time_out)
        except EOFError as e:
            self.logfile.write(self.section+"!!!")  #!!!
            self.logfile.write("Connection closed: %s" % e)
            return False
            
        self.logfile.write(self.section+"!!!")  #!!!
        if check_string in self.section:
            return True
        else:
            self.logfile.write("telnet check, expecting \"%s\", got \"%s\"" % (check_string, self.section[-(len(check_string)+5):]))
            dbg.printDBG3(file_name, 
                "telnet time-out, expecting \"%s\", got \"%s\"" % (check_string, self.section[-len(check_string):]))
            return False
#
    def __GetQLogicError(self, file):
#
        self.start_idx = 0
        self.__getLines(file)
        output_string = "QLogic Port Error Switch%s\n" % file[9:-4]

#   LicensedPorts       12
        if self.__findItem("LicensedPorts") == False: return False
        port_count = int(self.items[1])
        self.switch_err = [0 for x in range(port_count)]
        for i in range(port_count): self.switch_err[i] = {}
        
        for i in range(port_count):
#   SANbox (admin) #> !!!show port 0
            if self.__findItem("show port %s" % i) == False: return False
#       ALInit             0                   LIP_F8_F7          0                 
            if self.__CheckError(i, "ALInit") == False: return False
#       ALInitError        0                   LinkFailures       0            
            if self.__CheckError(i, "ALInitError") == False: return False
#       BadFrames          0                   Login              0             
            if self.__CheckError(i, "BadFrames") == False: return False
#       BBCR_FrameFailures 0                   Logout             0                 
            if self.__CheckError(i, "BBCR_FrameFailures") == False: return False
#       BBCR_RRDYFailures  0                   LongFramesIn       0                 
            if self.__CheckError(i, "BBCR_RRDYFailures") == False: return False
#       Class2FramesIn     0                   LoopTimeouts       0                 
            if self.__CheckError(i, "Class2FramesIn") == False: return False
#       Class2FramesOut    0                   LossOfSync         0                 
            if self.__CheckError(i, "Class2FramesOut") == False: return False
#       Class2WordsIn      0                   LostFrames         0                 
            if self.__CheckError(i, "Class2WordsIn") == False: return False
#       Class2WordsOut     0                   LostRRDYs          0                 
            if self.__CheckError(i, "Class2WordsOut") == False: return False
#       Class3FramesIn     0                   PrimSeqErrors      0                 
            if self.__CheckError(i, "Class3FramesIn") == False: return False
#       Class3FramesOut    0                   RxLinkResets       0                 
            if self.__CheckError(i, "Class3FramesOut") == False: return False
#       Class3Toss         0                   RxOfflineSeq       0                 
            if self.__CheckError(i, "Class3Toss") == False: return False
#       Class3WordsIn      0                   ShortFramesIn      0                 
            if self.__CheckError(i, "Class3WordsIn") == False: return False
#       Class3WordsOut     0                   TotalErrors        0                 
            if self.__CheckError(i, "Class3WordsOut") == False: return False
#       DecodeErrors       0                   TotalLinkResets    0                 
            if self.__CheckError(i, "DecodeErrors") == False: return False
#       EpConnects         0                   TotalLIPsRecvd     0                 
            if self.__CheckError(i, "EpConnects") == False: return False
#       FBusy              0                   TotalLIPsXmitd     0                 
            if self.__CheckError(i, "FBusy") == False: return False
#       FlowErrors         0                   TotalOfflineSeq    1                 
            if self.__CheckError(i, "FlowErrors") == False: return False
#       FReject            0                   TotalRxFrames      0                 
            if self.__CheckError(i, "FReject") == False: return False
#       InvalidCRC         0                   TotalRxWords       0                 
            if self.__CheckError(i, "InvalidCRC") == False: return False
#       InvalidDestAddr    0                   TotalTxFrames      0                 
            if self.__CheckError(i, "InvalidDestAddr") == False: return False
#       LIP_AL_PD_AL_PS    0                   TotalTxWords       0                 
            if self.__CheckError(i, "LIP_AL_PD_AL_PS") == False: return False
#       LIP_F7_AL_PS       0                   TxLinkResets       0                 
            if self.__CheckError(i, "LIP_F7_AL_PS") == False: return False
#       LIP_F7_F7          0                   TxOfflineSeq       1                 
            if self.__CheckError(i, "LIP_F7_F7") == False: return False
#       LIP_F8_AL_PS       0
            if self.__CheckError(i, "LIP_F8_AL_PS", last = True) == False: return False
#
        for i in range(port_count):
            output_string = output_string + "\tPort %s: \n" % i
            for item in self.switch_err[i]:
                output_string = output_string + "\t\t%s = %s\n" % (item, self.switch_err[i][item])
        tkMessageBox.showinfo("Switch Diag Information", output_string)
        return True
#
    def __GetBrocadeError(self, file):
#
        self.start_idx = 0
        self.__getLines(file)
        output_string = "Brocade Port Error Switch%s\n" % file[9:-4]

#   LicensedPorts       12
        if self.__findItem("LicensedPorts") == False: return False
        port_count = int(self.items[1])
        self.switch_err = [0 for x in range(port_count)]
        for i in range(port_count): self.switch_err[i] = {}

        for i in range(port_count):
#   ?????:root> portshow 11
            if self.__findItem("portshow %s" % i) == False: return False
#       Interrupts:        0          Link_failure: 0          Frjt:         0          
            if self.__CheckError(i, "Interrupts:") == False: return False
#       Unknown:           0          Loss_of_sync: 0          Fbsy:         0          
            if self.__CheckError(i, "Unknown:") == False: return False
#       Lli:               75         Loss_of_sig:  0          
            if self.__CheckError(i, "Lli:") == False: return False
#       Proc_rqrd:         37         Protocol_err: 0          
            if self.__CheckError(i, "Proc_rqrd:") == False: return False
#       Timed_out:         0          Invalid_word: 0          
            if self.__CheckError(i, "Timed_out:") == False: return False
#       Rx_flushed:        0          Invalid_crc:  0          
            if self.__CheckError(i, "Rx_flushed:") == False: return False
#       Tx_unavail:        0          Delim_err:    0          
            if self.__CheckError(i, "Tx_unavail:") == False: return False
#       Free_buffer:       0          Address_err:  0          
            if self.__CheckError(i, "Free_buffer:") == False: return False
#       Overrun:           0          Lr_in:        2          
            if self.__CheckError(i, "Overrun:") == False: return False
#       Suspended:         0          Lr_out:       13         
            if self.__CheckError(i, "Suspended:") == False: return False
#       Parity_err:        0          Ols_in:       2          
            if self.__CheckError(i, "Parity_err:") == False: return False
#       2_parity_err:      0          Ols_out:      2          
            if self.__CheckError(i, "2_parity_err:") == False: return False
#       CMI_bus_err:       0          
            if self.__CheckError(i, "CMI_bus_err:", last = True) == False: return False

        for i in range(port_count):
            output_string = output_string + "\tPort %s: \n" % i
            for item in self.switch_err[i]:
                output_string = output_string + "\t\t%s = %s\n" % (item, self.switch_err[i][item])
        tkMessageBox.showinfo("Switch Diag Information", output_string)
        return True
        pass
#
    def __GetCiscoError(self, file):
        pass
#
    def __GetLoxollError(self, file):
        pass
#
    def __CheckError(self, port, error, last = False):
        if self.__findItem(error) == False: return False
        if self.items[1] != "0": self.switch_err[port][self.items[0]] = int(self.items[1])
        if last == True: return True
        if self.items[3] != "0": self.switch_err[port][self.items[2]] = int(self.items[3])
        return True        
#
    def __getLines(self, f):
        vpdfile = open(f, 'r')
        self.lines = vpdfile.readlines()
        self.f_length = len(self.lines)
        vpdfile.close()
        dbg.printDBG4(file_name, "get %s lines from file %s" % (self.f_length, f))

    def __findItem(self, key):        
        for i in range(self.start_idx, self.f_length):
            if self.lines[i].find(key) != -1: break
        self.items = self.lines[i].split()
        self.start_idx = i + 1
        if self.start_idx == self.f_length:
            dbg.printDBG2(file_name, "!!!! Item \"%s\" not found" % key)
            return False
        return True

"""
Switch Vendor : QLogic
Telnet to : 192.168.212.56, Time Stamp : 20151202102341

Firmware V7.4.0.10.0

switch login: !!!Password: !!!

  Establishing connection...   Please wait.

       *****************************************************
       *                                                   *
       *       Command Line Interface SHell  (CLISH)       *
       *                                                   *
       *****************************************************

       SystemDescription   SANbox 5800 FC Switch
       HostName            <undefined>
       EthIPv4NetworkAddr  192.168.212.56
       EthIPv6NetworkAddr  fe80::2c0:ddff:fe1f:34ba
       MACAddress          00:c0:dd:1f:34:ba
       WorldWideName       10:00:00:c0:dd:1f:34:ba
       ChassisSerialNumber 1149H01155
       SymbolicName        SANbox
       ActiveSWVersion     V7.4.0.10.0
       ActiveTimestamp     Fri Jul 25 16:19:59 2008
       POSTStatus          Passed
       LicensedPorts       12
       SwitchMode          Full Fabric

  The alarm log is empty.


  Warning:  Your user account password has not been changed
            It is strongly recommended that you do so before proceeding

SANbox #> !!!admin start

SANbox (admin) #> !!!show port 0

  Port Number: 0 
  ------------
  AdminState       Online              PortWWN          20:00:00:c0:dd:1f:34:ba
  AsicNumber       0                   POSTFaultCode    00000000          
  AsicPort         0                   POSTStatus       Passed            
  ConfigType       F                   RunningType      F                 
  DownstreamISL    False               MediaPartNumber  Unknown           
  EpConnState      None                MediaRevision    Unknown           
  EpIsoReason      NotApplicable       MediaType        NotInstalled      
  IOStreamGuard    Disabled            MediaVendor      Unknown           
  Licensed         True                MediaVendorID    Unknown           
  LinkSpeed        Auto                SupportedSpeeds  1, 2, 4, 8Gb/s    
  LinkState        Inactive            SymbolicName     Port0             
  LoginStatus      NotLoggedIn         SyncStatus       SyncLost          
  MaxCredit        16                  TestFaultCode    00000000          
  MediaSpeeds      Unknown             TestStatus       NeverRun          
  OperationalState Offline             UpstreamISL      False             
  PerfTuningMode   Normal              XmitterEnabled   True              
  PortID           030000            

  ALInit             0                   LIP_F8_F7          0                 
  ALInitError        0                   LinkFailures       0                 
  BadFrames          0                   Login              0                 
  BBCR_FrameFailures 0                   Logout             0                 
  BBCR_RRDYFailures  0                   LongFramesIn       0                 
  Class2FramesIn     0                   LoopTimeouts       0                 
  Class2FramesOut    0                   LossOfSync         0                 
  Class2WordsIn      0                   LostFrames         0                 
  Class2WordsOut     0                   LostRRDYs          0                 
  Class3FramesIn     0                   PrimSeqErrors      0                 
  Class3FramesOut    0                   RxLinkResets       0                 
  Class3Toss         0                   RxOfflineSeq       0                 
  Class3WordsIn      0                   ShortFramesIn      0                 
  Class3WordsOut     0                   TotalErrors        0                 
  DecodeErrors       0                   TotalLinkResets    0                 
  EpConnects         0                   TotalLIPsRecvd     0                 
  FBusy              0                   TotalLIPsXmitd     0                 
  FlowErrors         0                   TotalOfflineSeq    1                 
  FReject            0                   TotalRxFrames      0                 
  InvalidCRC         0                   TotalRxWords       0                 
  InvalidDestAddr    0                   TotalTxFrames      0                 
  LIP_AL_PD_AL_PS    0                   TotalTxWords       0                 
  LIP_F7_AL_PS       0                   TxLinkResets       0                 
  LIP_F7_F7          0                   TxOfflineSeq       1                 
  LIP_F8_AL_PS       0                 

SANbox (admin) #> !!!show port 1

  Port Number: 1 
  ------------
  AdminState       Online              PortWWN          20:01:00:c0:dd:1f:34:ba
  AsicNumber       0                   POSTFaultCode    00000000          
  AsicPort         2                   POSTStatus       Passed            
  ConfigType       F                   RunningType      F                 
  DownstreamISL    False               MediaPartNumber  Unknown           
  EpConnState      None                MediaRevision    Unknown           
  EpIsoReason      NotApplicable       MediaType        NotInstalled      
  IOStreamGuard    Disabled            MediaVendor      Unknown           
  Licensed         True                MediaVendorID    Unknown           
  LinkSpeed        Auto                SupportedSpeeds  1, 2, 4, 8Gb/s    
  LinkState        Inactive            SymbolicName     Port1             
  LoginStatus      NotLoggedIn         SyncStatus       SyncLost          
  MaxCredit        16                  TestFaultCode    00000000          
  MediaSpeeds      Unknown             TestStatus       NeverRun          
  OperationalState Offline             UpstreamISL      False             
  PerfTuningMode   Normal              XmitterEnabled   True              
  PortID           030100            

  ALInit             0                   LIP_F8_F7          0                 
  ALInitError        0                   LinkFailures       0                 
  BadFrames          0                   Login              0                 
  BBCR_FrameFailures 0                   Logout             0                 
  BBCR_RRDYFailures  0                   LongFramesIn       0                 
  Class2FramesIn     0                   LoopTimeouts       0                 
  Class2FramesOut    0                   LossOfSync         0                 
  Class2WordsIn      0                   LostFrames         0                 
  Class2WordsOut     0                   LostRRDYs          0                 
  Class3FramesIn     0                   PrimSeqErrors      0                 
  Class3FramesOut    0                   RxLinkResets       0                 
  Class3Toss         0                   RxOfflineSeq       0                 
  Class3WordsIn      0                   ShortFramesIn      0                 
  Class3WordsOut     0                   TotalErrors        0                 
  DecodeErrors       0                   TotalLinkResets    0                 
  EpConnects         0                   TotalLIPsRecvd     0                 
  FBusy              0                   TotalLIPsXmitd     0                 
  FlowErrors         0                   TotalOfflineSeq    1                 
  FReject            0                   TotalRxFrames      0                 
  InvalidCRC         0                   TotalRxWords       0                 
  InvalidDestAddr    0                   TotalTxFrames      0                 
  LIP_AL_PD_AL_PS    0                   TotalTxWords       0                 
  LIP_F7_AL_PS       0                   TxLinkResets       0                 
  LIP_F7_F7          0                   TxOfflineSeq       1                 
  LIP_F8_AL_PS       0                 

SANbox (admin) #> !!!show port 2

  Port Number: 2 
  ------------
  AdminState       Online              PortWWN          20:02:00:c0:dd:1f:34:ba
  AsicNumber       0                   POSTFaultCode    00000000          
  AsicPort         4                   POSTStatus       Passed            
  ConfigType       F                   RunningType      F                 
  DownstreamISL    False               MediaPartNumber  Unknown           
  EpConnState      None                MediaRevision    Unknown           
  EpIsoReason      NotApplicable       MediaType        NotInstalled      
  IOStreamGuard    Disabled            MediaVendor      Unknown           
  Licensed         True                MediaVendorID    Unknown           
  LinkSpeed        8Gb/s               SupportedSpeeds  1, 2, 4, 8Gb/s    
  LinkState        Inactive            SymbolicName     Port2             
  LoginStatus      NotLoggedIn         SyncStatus       SyncLost          
  MaxCredit        16                  TestFaultCode    00000000          
  MediaSpeeds      Unknown             TestStatus       NeverRun          
  OperationalState Offline             UpstreamISL      False             
  PerfTuningMode   Normal              XmitterEnabled   True              
  PortID           030200            

  ALInit             0                   LIP_F8_F7          0                 
  ALInitError        0                   LinkFailures       0                 
  BadFrames          0                   Login              0                 
  BBCR_FrameFailures 0                   Logout             0                 
  BBCR_RRDYFailures  0                   LongFramesIn       0                 
  Class2FramesIn     0                   LoopTimeouts       0                 
  Class2FramesOut    0                   LossOfSync         0                 
  Class2WordsIn      0                   LostFrames         0                 
  Class2WordsOut     0                   LostRRDYs          0                 
  Class3FramesIn     0                   PrimSeqErrors      0                 
  Class3FramesOut    0                   RxLinkResets       0                 
  Class3Toss         0                   RxOfflineSeq       0                 
  Class3WordsIn      0                   ShortFramesIn      0                 
  Class3WordsOut     0                   TotalErrors        0                 
  DecodeErrors       0                   TotalLinkResets    0                 
  EpConnects         0                   TotalLIPsRecvd     0                 
  FBusy              0                   TotalLIPsXmitd     0                 
  FlowErrors         0                   TotalOfflineSeq    1                 
  FReject            0                   TotalRxFrames      0                 
  InvalidCRC         0                   TotalRxWords       0                 
  InvalidDestAddr    0                   TotalTxFrames      0                 
  LIP_AL_PD_AL_PS    0                   TotalTxWords       0                 
  LIP_F7_AL_PS       0                   TxLinkResets       0                 
  LIP_F7_F7          0                   TxOfflineSeq       1                 
  LIP_F8_AL_PS       0                 

SANbox (admin) #> !!!show port 3

  Port Number: 3 
  ------------
  AdminState       Online              PortWWN          20:03:00:c0:dd:1f:34:ba
  AsicNumber       0                   POSTFaultCode    00000000          
  AsicPort         6                   POSTStatus       Passed            
  ConfigType       F                   RunningType      F                 
  DownstreamISL    False               MediaPartNumber  Unknown           
  EpConnState      None                MediaRevision    Unknown           
  EpIsoReason      NotApplicable       MediaType        NotInstalled      
  IOStreamGuard    Disabled            MediaVendor      Unknown           
  Licensed         True                MediaVendorID    Unknown           
  LinkSpeed        Auto                SupportedSpeeds  1, 2, 4, 8Gb/s    
  LinkState        Inactive            SymbolicName     Port3             
  LoginStatus      NotLoggedIn         SyncStatus       SyncLost          
  MaxCredit        16                  TestFaultCode    00000000          
  MediaSpeeds      Unknown             TestStatus       NeverRun          
  OperationalState Offline             UpstreamISL      False             
  PerfTuningMode   Normal              XmitterEnabled   True              
  PortID           030300            

  ALInit             0                   LIP_F8_F7          0                 
  ALInitError        0                   LinkFailures       0                 
  BadFrames          0                   Login              0                 
  BBCR_FrameFailures 0                   Logout             0                 
  BBCR_RRDYFailures  0                   LongFramesIn       0                 
  Class2FramesIn     0                   LoopTimeouts       0                 
  Class2FramesOut    0                   LossOfSync         0                 
  Class2WordsIn      0                   LostFrames         0                 
  Class2WordsOut     0                   LostRRDYs          0                 
  Class3FramesIn     0                   PrimSeqErrors      0                 
  Class3FramesOut    0                   RxLinkResets       0                 
  Class3Toss         0                   RxOfflineSeq       0                 
  Class3WordsIn      0                   ShortFramesIn      0                 
  Class3WordsOut     0                   TotalErrors        0                 
  DecodeErrors       0                   TotalLinkResets    0                 
  EpConnects         0                   TotalLIPsRecvd     0                 
  FBusy              0                   TotalLIPsXmitd     0                 
  FlowErrors         0                   TotalOfflineSeq    1                 
  FReject            0                   TotalRxFrames      0                 
  InvalidCRC         0                   TotalRxWords       0                 
  InvalidDestAddr    0                   TotalTxFrames      0                 
  LIP_AL_PD_AL_PS    0                   TotalTxWords       0                 
  LIP_F7_AL_PS       0                   TxLinkResets       0                 
  LIP_F7_F7          0                   TxOfflineSeq       1                 
  LIP_F8_AL_PS       0                 

SANbox (admin) #> !!!show port 4

  Port Number: 4 
  ------------
  AdminState       Online              PortWWN          20:04:00:c0:dd:1f:34:ba
  AsicNumber       0                   POSTFaultCode    00000000          
  AsicPort         8                   POSTStatus       Passed            
  ConfigType       FL                  RunningType      Unknown           
  DownstreamISL    False               MediaPartNumber  Unknown           
  EpConnState      None                MediaRevision    Unknown           
  EpIsoReason      NotApplicable       MediaType        NotInstalled      
  IOStreamGuard    Enabled             MediaVendor      Unknown           
  Licensed         True                MediaVendorID    Unknown           
  LinkSpeed        Auto                SupportedSpeeds  1, 2, 4, 8Gb/s    
  LinkState        Inactive            SymbolicName     Port4             
  LoginStatus      NotLoggedIn         SyncStatus       SyncLost          
  MaxCredit        16                  TestFaultCode    00000000          
  MediaSpeeds      Unknown             TestStatus       NeverRun          
  OperationalState Offline             UpstreamISL      False             
  PerfTuningMode   Normal              XmitterEnabled   True              
  PortID           030400            

  ALInit             1                   LIP_F8_F7          0                 
  ALInitError        0                   LinkFailures       0                 
  BadFrames          0                   Login              0                 
  BBCR_FrameFailures 0                   Logout             0                 
  BBCR_RRDYFailures  0                   LongFramesIn       0                 
  Class2FramesIn     0                   LoopTimeouts       0                 
  Class2FramesOut    0                   LossOfSync         0                 
  Class2WordsIn      0                   LostFrames         0                 
  Class2WordsOut     0                   LostRRDYs          0                 
  Class3FramesIn     0                   PrimSeqErrors      0                 
  Class3FramesOut    0                   RxLinkResets       0                 
  Class3Toss         0                   RxOfflineSeq       0                 
  Class3WordsIn      0                   ShortFramesIn      0                 
  Class3WordsOut     0                   TotalErrors        0                 
  DecodeErrors       0                   TotalLinkResets    0                 
  EpConnects         0                   TotalLIPsRecvd     0                 
  FBusy              0                   TotalLIPsXmitd     2                 
  FlowErrors         0                   TotalOfflineSeq    0                 
  FReject            0                   TotalRxFrames      0                 
  InvalidCRC         0                   TotalRxWords       0                 
  InvalidDestAddr    0                   TotalTxFrames      0                 
  LIP_AL_PD_AL_PS    0                   TotalTxWords       0                 
  LIP_F7_AL_PS       0                   TxLinkResets       0                 
  LIP_F7_F7          0                   TxOfflineSeq       0                 
  LIP_F8_AL_PS       0                 

SANbox (admin) #> !!!show port 5

  Port Number: 5 
  ------------
  AdminState       Online              PortWWN          20:05:00:c0:dd:1f:34:ba
  AsicNumber       0                   POSTFaultCode    00000000          
  AsicPort         10                  POSTStatus       Passed            
  ConfigType       FL                  RunningType      Unknown           
  DownstreamISL    False               MediaPartNumber  Unknown           
  EpConnState      None                MediaRevision    Unknown           
  EpIsoReason      NotApplicable       MediaType        NotInstalled      
  IOStreamGuard    Disabled            MediaVendor      Unknown           
  Licensed         True                MediaVendorID    Unknown           
  LinkSpeed        Auto                SupportedSpeeds  1, 2, 4, 8Gb/s    
  LinkState        Inactive            SymbolicName     Port5             
  LoginStatus      NotLoggedIn         SyncStatus       SyncLost          
  MaxCredit        16                  TestFaultCode    00000000          
  MediaSpeeds      Unknown             TestStatus       NeverRun          
  OperationalState Offline             UpstreamISL      False             
  PerfTuningMode   Normal              XmitterEnabled   True              
  PortID           030500            

  ALInit             1                   LIP_F8_F7          0                 
  ALInitError        0                   LinkFailures       0                 
  BadFrames          0                   Login              0                 
  BBCR_FrameFailures 0                   Logout             0                 
  BBCR_RRDYFailures  0                   LongFramesIn       0                 
  Class2FramesIn     0                   LoopTimeouts       0                 
  Class2FramesOut    0                   LossOfSync         0                 
  Class2WordsIn      0                   LostFrames         0                 
  Class2WordsOut     0                   LostRRDYs          0                 
  Class3FramesIn     0                   PrimSeqErrors      0                 
  Class3FramesOut    0                   RxLinkResets       0                 
  Class3Toss         0                   RxOfflineSeq       0                 
  Class3WordsIn      0                   ShortFramesIn      0                 
  Class3WordsOut     0                   TotalErrors        0                 
  DecodeErrors       0                   TotalLinkResets    0                 
  EpConnects         0                   TotalLIPsRecvd     0                 
  FBusy              0                   TotalLIPsXmitd     2                 
  FlowErrors         0                   TotalOfflineSeq    0                 
  FReject            0                   TotalRxFrames      0                 
  InvalidCRC         0                   TotalRxWords       0                 
  InvalidDestAddr    0                   TotalTxFrames      0                 
  LIP_AL_PD_AL_PS    0                   TotalTxWords       0                 
  LIP_F7_AL_PS       0                   TxLinkResets       0                 
  LIP_F7_F7          0                   TxOfflineSeq       0                 
  LIP_F8_AL_PS       0                 

SANbox (admin) #> !!!show port 6

  Port Number: 6 
  ------------
  AdminState       Online              PortWWN          20:06:00:c0:dd:1f:34:ba
  AsicNumber       0                   POSTFaultCode    00000000          
  AsicPort         12                  POSTStatus       Passed            
  ConfigType       FL                  RunningType      Unknown           
  DownstreamISL    False               MediaPartNumber  Unknown           
  EpConnState      None                MediaRevision    Unknown           
  EpIsoReason      NotApplicable       MediaType        NotInstalled      
  IOStreamGuard    Disabled            MediaVendor      Unknown           
  Licensed         True                MediaVendorID    Unknown           
  LinkSpeed        8Gb/s               SupportedSpeeds  1, 2, 4, 8Gb/s    
  LinkState        Inactive            SymbolicName     Port6             
  LoginStatus      NotLoggedIn         SyncStatus       SyncLost          
  MaxCredit        16                  TestFaultCode    00000000          
  MediaSpeeds      Unknown             TestStatus       NeverRun          
  OperationalState Offline             UpstreamISL      False             
  PerfTuningMode   Normal              XmitterEnabled   True              
  PortID           030600            

  ALInit             1                   LIP_F8_F7          0                 
  ALInitError        0                   LinkFailures       0                 
  BadFrames          0                   Login              0                 
  BBCR_FrameFailures 0                   Logout             0                 
  BBCR_RRDYFailures  0                   LongFramesIn       0                 
  Class2FramesIn     0                   LoopTimeouts       0                 
  Class2FramesOut    0                   LossOfSync         0                 
  Class2WordsIn      0                   LostFrames         0                 
  Class2WordsOut     0                   LostRRDYs          0                 
  Class3FramesIn     0                   PrimSeqErrors      0                 
  Class3FramesOut    0                   RxLinkResets       0                 
  Class3Toss         0                   RxOfflineSeq       0                 
  Class3WordsIn      0                   ShortFramesIn      0                 
  Class3WordsOut     0                   TotalErrors        0                 
  DecodeErrors       0                   TotalLinkResets    0                 
  EpConnects         0                   TotalLIPsRecvd     0                 
  FBusy              0                   TotalLIPsXmitd     2                 
  FlowErrors         0                   TotalOfflineSeq    0                 
  FReject            0                   TotalRxFrames      0                 
  InvalidCRC         0                   TotalRxWords       0                 
  InvalidDestAddr    0                   TotalTxFrames      0                 
  LIP_AL_PD_AL_PS    0                   TotalTxWords       0                 
  LIP_F7_AL_PS       0                   TxLinkResets       0                 
  LIP_F7_F7          0                   TxOfflineSeq       0                 
  LIP_F8_AL_PS       0                 

SANbox (admin) #> !!!show port 7

  Port Number: 7 
  ------------
  AdminState       Online              PortWWN          20:07:00:c0:dd:1f:34:ba
  AsicNumber       0                   POSTFaultCode    00000000          
  AsicPort         14                  POSTStatus       Passed            
  ConfigType       FL                  RunningType      Unknown           
  DownstreamISL    False               MediaPartNumber  Unknown           
  EpConnState      None                MediaRevision    Unknown           
  EpIsoReason      NotApplicable       MediaType        NotInstalled      
  IOStreamGuard    Disabled            MediaVendor      Unknown           
  Licensed         True                MediaVendorID    Unknown           
  LinkSpeed        Auto                SupportedSpeeds  1, 2, 4, 8Gb/s    
  LinkState        Inactive            SymbolicName     Port7             
  LoginStatus      NotLoggedIn         SyncStatus       SyncLost          
  MaxCredit        16                  TestFaultCode    00000000          
  MediaSpeeds      Unknown             TestStatus       NeverRun          
  OperationalState Offline             UpstreamISL      False             
  PerfTuningMode   Normal              XmitterEnabled   True              
  PortID           030700            

  ALInit             1                   LIP_F8_F7          0                 
  ALInitError        0                   LinkFailures       0                 
  BadFrames          0                   Login              0                 
  BBCR_FrameFailures 0                   Logout             0                 
  BBCR_RRDYFailures  0                   LongFramesIn       0                 
  Class2FramesIn     0                   LoopTimeouts       0                 
  Class2FramesOut    0                   LossOfSync         0                 
  Class2WordsIn      0                   LostFrames         0                 
  Class2WordsOut     0                   LostRRDYs          0                 
  Class3FramesIn     0                   PrimSeqErrors      0                 
  Class3FramesOut    0                   RxLinkResets       0                 
  Class3Toss         0                   RxOfflineSeq       0                 
  Class3WordsIn      0                   ShortFramesIn      0                 
  Class3WordsOut     0                   TotalErrors        0                 
  DecodeErrors       0                   TotalLinkResets    0                 
  EpConnects         0                   TotalLIPsRecvd     0                 
  FBusy              0                   TotalLIPsXmitd     2                 
  FlowErrors         0                   TotalOfflineSeq    0                 
  FReject            0                   TotalRxFrames      0                 
  InvalidCRC         0                   TotalRxWords       0                 
  InvalidDestAddr    0                   TotalTxFrames      0                 
  LIP_AL_PD_AL_PS    0                   TotalTxWords       0                 
  LIP_F7_AL_PS       0                   TxLinkResets       0                 
  LIP_F7_F7          0                   TxOfflineSeq       0                 
  LIP_F8_AL_PS       0                 

SANbox (admin) #> !!!show port 8

  Port Number: 8 
  ------------
  AdminState       Online              PortWWN          20:08:00:c0:dd:1f:34:ba
  AsicNumber       0                   POSTFaultCode    00000000          
  AsicPort         16                  POSTStatus       Passed            
  ConfigType       GL                  RunningType      Unknown           
  DownstreamISL    False               MediaPartNumber  Unknown           
  EpConnState      None                MediaRevision    Unknown           
  EpIsoReason      NotLicensed         MediaType        NotInstalled      
  IOStreamGuard    Disabled            MediaVendor      Unknown           
  Licensed         False               MediaVendorID    Unknown           
  LinkSpeed        Auto                SupportedSpeeds  1, 2, 4, 8Gb/s    
  LinkState        Inactive            SymbolicName     Port8             
  LoginStatus      NotLoggedIn         SyncStatus       SyncLost          
  MaxCredit        16                  TestFaultCode    00000000          
  MediaSpeeds      Unknown             TestStatus       NeverRun          
  OperationalState Downed              UpstreamISL      False             
  PerfTuningMode   Normal              XmitterEnabled   False             
  PortID           030800            

  ALInit             0                   LIP_F8_F7          0                 
  ALInitError        0                   LinkFailures       0                 
  BadFrames          0                   Login              0                 
  BBCR_FrameFailures 0                   Logout             0                 
  BBCR_RRDYFailures  0                   LongFramesIn       0                 
  Class2FramesIn     0                   LoopTimeouts       0                 
  Class2FramesOut    0                   LossOfSync         0                 
  Class2WordsIn      0                   LostFrames         0                 
  Class2WordsOut     0                   LostRRDYs          0                 
  Class3FramesIn     0                   PrimSeqErrors      0                 
  Class3FramesOut    0                   RxLinkResets       0                 
  Class3Toss         0                   RxOfflineSeq       0                 
  Class3WordsIn      0                   ShortFramesIn      0                 
  Class3WordsOut     0                   TotalErrors        0                 
  DecodeErrors       0                   TotalLinkResets    0                 
  EpConnects         0                   TotalLIPsRecvd     0                 
  FBusy              0                   TotalLIPsXmitd     0                 
  FlowErrors         0                   TotalOfflineSeq    1                 
  FReject            0                   TotalRxFrames      0                 
  InvalidCRC         0                   TotalRxWords       0                 
  InvalidDestAddr    0                   TotalTxFrames      0                 
  LIP_AL_PD_AL_PS    0                   TotalTxWords       0                 
  LIP_F7_AL_PS       0                   TxLinkResets       0                 
  LIP_F7_F7          0                   TxOfflineSeq       1                 
  LIP_F8_AL_PS       0                 

SANbox (admin) #> !!!show port 9

  Port Number: 9 
  ------------
  AdminState       Online              PortWWN          20:09:00:c0:dd:1f:34:ba
  AsicNumber       0                   POSTFaultCode    00000000          
  AsicPort         18                  POSTStatus       Passed            
  ConfigType       GL                  RunningType      Unknown           
  DownstreamISL    False               MediaPartNumber  Unknown           
  EpConnState      None                MediaRevision    Unknown           
  EpIsoReason      NotLicensed         MediaType        NotInstalled      
  IOStreamGuard    Disabled            MediaVendor      Unknown           
  Licensed         False               MediaVendorID    Unknown           
  LinkSpeed        Auto                SupportedSpeeds  1, 2, 4, 8Gb/s    
  LinkState        Inactive            SymbolicName     Port9             
  LoginStatus      NotLoggedIn         SyncStatus       SyncLost          
  MaxCredit        16                  TestFaultCode    00000000          
  MediaSpeeds      Unknown             TestStatus       NeverRun          
  OperationalState Downed              UpstreamISL      False             
  PerfTuningMode   Normal              XmitterEnabled   False             
  PortID           030900            

  ALInit             0                   LIP_F8_F7          0                 
  ALInitError        0                   LinkFailures       0                 
  BadFrames          0                   Login              0                 
  BBCR_FrameFailures 0                   Logout             0                 
  BBCR_RRDYFailures  0                   LongFramesIn       0                 
  Class2FramesIn     0                   LoopTimeouts       0                 
  Class2FramesOut    0                   LossOfSync         0                 
  Class2WordsIn      0                   LostFrames         0                 
  Class2WordsOut     0                   LostRRDYs          0                 
  Class3FramesIn     0                   PrimSeqErrors      0                 
  Class3FramesOut    0                   RxLinkResets       0                 
  Class3Toss         0                   RxOfflineSeq       0                 
  Class3WordsIn      0                   ShortFramesIn      0                 
  Class3WordsOut     0                   TotalErrors        0                 
  DecodeErrors       0                   TotalLinkResets    0                 
  EpConnects         0                   TotalLIPsRecvd     0                 
  FBusy              0                   TotalLIPsXmitd     0                 
  FlowErrors         0                   TotalOfflineSeq    1                 
  FReject            0                   TotalRxFrames      0                 
  InvalidCRC         0                   TotalRxWords       0                 
  InvalidDestAddr    0                   TotalTxFrames      0                 
  LIP_AL_PD_AL_PS    0                   TotalTxWords       0                 
  LIP_F7_AL_PS       0                   TxLinkResets       0                 
  LIP_F7_F7          0                   TxOfflineSeq       1                 
  LIP_F8_AL_PS       0                 

SANbox (admin) #> !!!show port 10

  Port Number: 10
  ------------
  AdminState       Online              PortWWN          20:0a:00:c0:dd:1f:34:ba
  AsicNumber       0                   POSTFaultCode    00000000          
  AsicPort         1                   POSTStatus       Passed            
  ConfigType       GL                  RunningType      Unknown           
  DownstreamISL    False               MediaPartNumber  Unknown           
  EpConnState      None                MediaRevision    Unknown           
  EpIsoReason      NotLicensed         MediaType        NotInstalled      
  IOStreamGuard    Disabled            MediaVendor      Unknown           
  Licensed         False               MediaVendorID    Unknown           
  LinkSpeed        Auto                SupportedSpeeds  1, 2, 4, 8Gb/s    
  LinkState        Inactive            SymbolicName     Port10            
  LoginStatus      NotLoggedIn         SyncStatus       SyncLost          
  MaxCredit        16                  TestFaultCode    00000000          
  MediaSpeeds      Unknown             TestStatus       NeverRun          
  OperationalState Downed              UpstreamISL      False             
  PerfTuningMode   Normal              XmitterEnabled   False             
  PortID           030a00            

  ALInit             0                   LIP_F8_F7          0                 
  ALInitError        0                   LinkFailures       0                 
  BadFrames          0                   Login              0                 
  BBCR_FrameFailures 0                   Logout             0                 
  BBCR_RRDYFailures  0                   LongFramesIn       0                 
  Class2FramesIn     0                   LoopTimeouts       0                 
  Class2FramesOut    0                   LossOfSync         0                 
  Class2WordsIn      0                   LostFrames         0                 
  Class2WordsOut     0                   LostRRDYs          0                 
  Class3FramesIn     0                   PrimSeqErrors      0                 
  Class3FramesOut    0                   RxLinkResets       0                 
  Class3Toss         0                   RxOfflineSeq       0                 
  Class3WordsIn      0                   ShortFramesIn      0                 
  Class3WordsOut     0                   TotalErrors        0                 
  DecodeErrors       0                   TotalLinkResets    0                 
  EpConnects         0                   TotalLIPsRecvd     0                 
  FBusy              0                   TotalLIPsXmitd     0                 
  FlowErrors         0                   TotalOfflineSeq    1                 
  FReject            0                   TotalRxFrames      0                 
  InvalidCRC         0                   TotalRxWords       0                 
  InvalidDestAddr    0                   TotalTxFrames      0                 
  LIP_AL_PD_AL_PS    0                   TotalTxWords       0                 
  LIP_F7_AL_PS       0                   TxLinkResets       0                 
  LIP_F7_F7          0                   TxOfflineSeq       1                 
  LIP_F8_AL_PS       0                 

SANbox (admin) #> !!!show port 11

  Port Number: 11
  ------------
  AdminState       Online              PortWWN          20:0b:00:c0:dd:1f:34:ba
  AsicNumber       0                   POSTFaultCode    00000000          
  AsicPort         3                   POSTStatus       Passed            
  ConfigType       GL                  RunningType      Unknown           
  DownstreamISL    False               MediaPartNumber  Unknown           
  EpConnState      None                MediaRevision    Unknown           
  EpIsoReason      NotLicensed         MediaType        NotInstalled      
  IOStreamGuard    Disabled            MediaVendor      Unknown           
  Licensed         False               MediaVendorID    Unknown           
  LinkSpeed        Auto                SupportedSpeeds  1, 2, 4, 8Gb/s    
  LinkState        Inactive            SymbolicName     Port11            
  LoginStatus      NotLoggedIn         SyncStatus       SyncLost          
  MaxCredit        16                  TestFaultCode    00000000          
  MediaSpeeds      Unknown             TestStatus       NeverRun          
  OperationalState Downed              UpstreamISL      False             
  PerfTuningMode   Normal              XmitterEnabled   False             
  PortID           030b00            

  ALInit             0                   LIP_F8_F7          0                 
  ALInitError        0                   LinkFailures       0                 
  BadFrames          0                   Login              0                 
  BBCR_FrameFailures 0                   Logout             0                 
  BBCR_RRDYFailures  0                   LongFramesIn       0                 
  Class2FramesIn     0                   LoopTimeouts       0                 
  Class2FramesOut    0                   LossOfSync         0                 
  Class2WordsIn      0                   LostFrames         0                 
  Class2WordsOut     0                   LostRRDYs          0                 
  Class3FramesIn     0                   PrimSeqErrors      0                 
  Class3FramesOut    0                   RxLinkResets       0                 
  Class3Toss         0                   RxOfflineSeq       0                 
  Class3WordsIn      0                   ShortFramesIn      0                 
  Class3WordsOut     0                   TotalErrors        0                 
  DecodeErrors       0                   TotalLinkResets    0                 
  EpConnects         0                   TotalLIPsRecvd     0                 
  FBusy              0                   TotalLIPsXmitd     0                 
  FlowErrors         0                   TotalOfflineSeq    1                 
  FReject            0                   TotalRxFrames      0                 
  InvalidCRC         0                   TotalRxWords       0                 
  InvalidDestAddr    0                   TotalTxFrames      0                 
  LIP_AL_PD_AL_PS    0                   TotalTxWords       0                 
  LIP_F7_AL_PS       0                   TxLinkResets       0                 
  LIP_F7_F7          0                   TxOfflineSeq       1                 
  LIP_F8_AL_PS       0                 

SANbox (admin) #> !!!admin end

SANbox #> !!!quit
Good bye.!!!

--------------------------

Brocade:
Fabric OS (swd77)
Fabos Version 7.2.1

swd77 login: root
Password: 
Disclaimer for Root and Factory Accounts Usage!

This Fibre Channel switch is equipped with Root and Factory accounts
that are intended for diagnostics and debugging purposes solely by 
the Equipment vendor's trained engineers. Improper use of the 
functionality made available through the Root or Factory account could
cause significant harm and disruption to the operation of the SAN fabric.

Your use of the functionality made available through the Root or Factory
account is at your sole risk and you assume all liability resulting from
such use. The Equipment vendor shall have no liability for any losses 
or damages arising from or relating to the use of the Root or Factory
account (and the functionality enabled thereby) by anyone other than 
the Equipment vendor's authorized engineers.

Proceeding with the usage of this switch as the Root or Factory user
explicitly indicates your agreement to the terms of this disclaimer.

swd77:root> cfgshow
Defined configuration:
 cfg:   RSS_njzy
                RSS1B1_Stor; Serv1H0P0_RSS1A1; Serv1H1P0_RSS1A1; Solaris_Stor
 zone:  RSS1B1_Stor
                RSS1B1; Stor1A0; Stor1B0
 zone:  Serv1H0P0_RSS1A1
                RSS1A1; Serv1H0P0
 zone:  Serv1H1P0_RSS1A1
                RSS1A1; Serv1H1P0
 zone:  Solaris_Stor
                1,1; 1,3; 1,5; 1,7; 1,8; 1,9; 1,10; 1,12; 1,13; 1,14
 alias: RSS1A1  1,11
 alias: RSS1B1  1,15
 alias: Serv1H0P0
                1,2
 alias: Serv1H1P0
                1,6
 alias: Stor1A0 1,1
 alias: Stor1B0 1,5

Effective configuration:
 cfg:   RSS_njzy
 zone:  RSS1B1_Stor
                1,15
                1,1
                1,5
 zone:  Serv1H0P0_RSS1A1
                1,11
                1,2
 zone:  Serv1H1P0_RSS1A1
                1,11
                1,6
 zone:  Solaris_Stor
                1,1
                1,3
                1,5
                1,7
                1,8
                1,9
                1,10
                1,12
                1,13
                1,14

swd77:root> switchshow
switchName:     swd77
switchType:     71.2
switchState:    Online   
switchMode:     Native
switchRole:     Principal
switchDomain:   1
switchId:       fffc01
switchWwn:      10:00:50:eb:1a:4c:49:f0
zoning:         ON (RSS_njzy)
switchBeacon:   OFF

Index Port Address Media Speed       State   Proto
==================================================
   0   0   010000   id    N8       No_Light    FC  
   1   1   010100   id    N8       Online      FC  F-Port  50:06:0e:80:10:35:a6:b1 
   2   2   010200   id    N8       Online      FC  F-Port  21:00:00:24:ff:55:2c:8d 
   3   3   010300   id    N4       Online      FC  F-Port  21:00:00:e0:8b:89:fb:7d 
   4   4   010400   id    N8       No_Light    FC  
   5   5   010500   id    N8       Online      FC  F-Port  50:06:0e:80:10:35:a6:b9 
   6   6   010600   id    N8       Online      FC  F-Port  21:00:00:24:ff:4c:fa:03 
   7   7   010700   id    N4       Online      FC  F-Port  21:00:00:24:ff:06:67:67 
   8   8   010800   id    N8       No_Light    FC  
   9   9   010900   id    N8       No_Light    FC  
  10  10   010a00   id    N8       No_Light    FC  
  11  11   010b00   id    N8       Online      FC  F-Port  21:00:00:60:22:ad:0b:9c 
  12  12   010c00   id    N8       No_Light    FC  
  13  13   010d00   id    N8       No_Light    FC  
  14  14   010e00   id    N8       No_Light    FC  
  15  15   010f00   id    N8       Online      FC  F-Port  23:00:00:60:22:ad:0b:9c 
  16  16   011000   id    N8       No_Light    FC  (No POD License) Disabled
  17  17   011100   --    N8       No_Module   FC  (No POD License) Disabled
  18  18   011200   --    N8       No_Module   FC  (No POD License) Disabled
  19  19   011300   --    N8       No_Module   FC  (No POD License) Disabled
  20  20   011400   id    N8       No_Light    FC  (No POD License) Disabled
  21  21   011500   --    N8       No_Module   FC  (No POD License) Disabled
  22  22   011600   --    N8       No_Module   FC  (No POD License) Disabled
  23  23   011700   --    N8       No_Module   FC  (No POD License) Disabled
swd77:root> porterrshow
          frames      enc    crc    crc    too    too    bad    enc   disc   link   loss   loss   frjt   fbsy    c3timeout    pcs
       tx     rx      in    err    g_eof  shrt   long   eof     out   c3    fail    sync   sig                   tx    rx     err
  0:    0      0      0      0      0      0      0      0      0      0      0      0      0      0      0      0      0      0   
  1:    1.7g   2.0g   0      0      0      0      0      0      0      6      0      0      0      0      0      0      0      0   
  2:    1.3g 932.1m   0      0      0      0      0      0      0     12      0      0      0      0      0      0      0      0   
  3:  727.1m   1.8g   0      0      0      0      0      0      0      0      0      0      0      0      0      0      0      0   
  4:    0      0      0      0      0      0      0      0      0      0      0      0      0      0      0      0      0      0   
  5:    1.7g   2.0g   0      0      0      0      0      0      0      0      0      0      0      0      0      0      0      0   
  6:    1.3g 933.1m   0      0      0      0      0      0      0      1.0k   0      0      0      0      0      1.0k   0      0   
  7:    2.1g 959.2m   0      0      0      0      0      0      0      0      0      0      0      0      0      0      0      0   
  8:    0      0      0      0      0      0      0      0      0      0      0      0      0      0      0      0      0      0   
  9:    0      0      0      0      0      0      0      0      0      0      0      0      0      0      0      0      0      0   
 10:    0      0      0      0      0      0      0      0      0      0      0      0      0      0      0      0      0      0   
 11:    1.8g   2.6g   0      0      0      0      0      0     34      1.0k   1      0      1      0      0      0      1.0k   0   
 12:    0      0      0      0      0      0      0      0      0      0      0      0      0      0      0      0      0      0   
 13:    0      0      0      0      0      0      0      0      0      0      0      0      0      0      0      0      0      0   
 14:    0      0      0      0      0      0      0      0      0      0      0      0      0      0      0      0      0      0   
 15:    1.2g 630.1m   0      0      0      0      0      0     34      0      1      0      1      0      0      0      0      0   
 16:    0      0      0      0      0      0      0      0      0      0      0      0      0      0      0      0      0      0   
 17:    0      0      0      0      0      0      0      0      0      0      0      0      0      0      0      0      0      0   
 18:    0      0      0      0      0      0      0      0      0      0      0      0      0      0      0      0      0      0   
 19:    0      0      0      0      0      0      0      0      0      0      0      0      0      0      0      0      0      0   
 20:    0      0      0      0      0      0      0      0      0      0      0      0      0      0      0      0      0      0   
 21:    0      0      0      0      0      0      0      0      0      0      0      0      0      0      0      0      0      0   
 22:    0      0      0      0      0      0      0      0      0      0      0      0      0      0      0      0      0      0   
 23:    0      0      0      0      0      0      0      0      0      0      0      0      0      0      0      0      0      0   
swd77:root> portshow 1
portIndex:   1
portName: port1
portHealth: No Fabric Watch License

Authentication: None
portDisableReason: None
portCFlags: 0x1
portFlags: 0x24b03       PRESENT ACTIVE F_PORT G_PORT U_PORT LOGICAL_ONLINE LOGIN NOELP LED ACCEPT FLOGI
LocalSwcFlags: 0x0
portType:  18.0
POD Port: Port is licensed
portState: 1    Online   
Protocol: FC
portPhys:  6    In_Sync         portScn:   32   F_Port    
port generation number:    0
state transition count:    1          

portId:    010100
portIfId:    43020015
portWwn:   20:01:50:eb:1a:4c:49:f0
portWwn of device(s) connected:
        50:06:0e:80:10:35:a6:b1
Distance:  normal
portSpeed: N8Gbps

Credit Recovery: Inactive
Aoq: Inactive
FAA: Inactive
F_Trunk: Inactive
LE domain: 0
FC Fastwrite: OFF
Interrupts:        0          Link_failure: 0          Frjt:         0          
Unknown:           0          Loss_of_sync: 0          Fbsy:         0          
Lli:               23         Loss_of_sig:  0          
Proc_rqrd:         25         Protocol_err: 0          
Timed_out:         0          Invalid_word: 0          
Rx_flushed:        0          Invalid_crc:  0          
Tx_unavail:        0          Delim_err:    0          
Free_buffer:       0          Address_err:  0          
Overrun:           0          Lr_in:        2          
Suspended:         0          Lr_out:       1          
Parity_err:        0          Ols_in:       0          
2_parity_err:      0          Ols_out:      2          
CMI_bus_err:       0          

Port part of other ADs: No
swd77:root> portshow 2
portIndex:   2
portName: port2
portHealth: No Fabric Watch License

Authentication: None
portDisableReason: None
portCFlags: 0x1
portFlags: 0x20b03       PRESENT ACTIVE F_PORT G_PORT U_PORT LOGICAL_ONLINE LOGIN NOELP ACCEPT FLOGI
LocalSwcFlags: 0x0
portType:  18.0
POD Port: Port is licensed
portState: 1    Online   
Protocol: FC
portPhys:  6    In_Sync         portScn:   32   F_Port    
port generation number:    0
state transition count:    1          

portId:    010200
portIfId:    43020013
portWwn:   20:02:50:eb:1a:4c:49:f0
portWwn of device(s) connected:
        21:00:00:24:ff:55:2c:8d
Distance:  normal
portSpeed: N8Gbps

Credit Recovery: Inactive
Aoq: Inactive
FAA: Inactive
F_Trunk: Inactive
LE domain: 0
FC Fastwrite: OFF
Interrupts:        0          Link_failure: 0          Frjt:         0          
Unknown:           0          Loss_of_sync: 0          Fbsy:         0          
Lli:               24         Loss_of_sig:  0          
Proc_rqrd:         37         Protocol_err: 0          
Timed_out:         0          Invalid_word: 0          
Rx_flushed:        0          Invalid_crc:  0          
Tx_unavail:        0          Delim_err:    0          
Free_buffer:       0          Address_err:  0          
Overrun:           0          Lr_in:        2          
Suspended:         0          Lr_out:       2          
Parity_err:        0          Ols_in:       2          
2_parity_err:      0          Ols_out:      2          
CMI_bus_err:       0          

Port part of other ADs: No
swd77:root> portshow 5
portIndex:   5
portName: port5
portHealth: No Fabric Watch License

Authentication: None
portDisableReason: None
portCFlags: 0x1
portFlags: 0x20b03       PRESENT ACTIVE F_PORT G_PORT U_PORT LOGICAL_ONLINE LOGIN NOELP ACCEPT FLOGI
LocalSwcFlags: 0x0
portType:  18.0
POD Port: Port is licensed
portState: 1    Online   
Protocol: FC
portPhys:  6    In_Sync         portScn:   32   F_Port    
port generation number:    0
state transition count:    1          

portId:    010500
portIfId:    43020014
portWwn:   20:05:50:eb:1a:4c:49:f0
portWwn of device(s) connected:
        50:06:0e:80:10:35:a6:b9
Distance:  normal
portSpeed: N8Gbps

Credit Recovery: Inactive
Aoq: Inactive
FAA: Inactive
F_Trunk: Inactive
LE domain: 0
FC Fastwrite: OFF
Interrupts:        0          Link_failure: 0          Frjt:         0          
Unknown:           0          Loss_of_sync: 0          Fbsy:         0          
Lli:               27         Loss_of_sig:  0          
Proc_rqrd:         26         Protocol_err: 0          
Timed_out:         0          Invalid_word: 0          
Rx_flushed:        0          Invalid_crc:  0          
Tx_unavail:        0          Delim_err:    0          
Free_buffer:       0          Address_err:  0          
Overrun:           0          Lr_in:        2          
Suspended:         0          Lr_out:       2          
Parity_err:        0          Ols_in:       0          
2_parity_err:      0          Ols_out:      2          
CMI_bus_err:       0          

Port part of other ADs: No
swd77:root> portshow 6
portIndex:   6
portName: port6
portHealth: No Fabric Watch License

Authentication: None
portDisableReason: None
portCFlags: 0x1
portFlags: 0x20b03       PRESENT ACTIVE F_PORT G_PORT U_PORT LOGICAL_ONLINE LOGIN NOELP ACCEPT FLOGI
LocalSwcFlags: 0x0
portType:  18.0
POD Port: Port is licensed
portState: 1    Online   
Protocol: FC
portPhys:  6    In_Sync         portScn:   32   F_Port    
port generation number:    0
state transition count:    1          

portId:    010600
portIfId:    43020012
portWwn:   20:06:50:eb:1a:4c:49:f0
portWwn of device(s) connected:
        21:00:00:24:ff:4c:fa:03
Distance:  normal
portSpeed: N8Gbps

Credit Recovery: Inactive
Aoq: Inactive
FAA: Inactive
F_Trunk: Inactive
LE domain: 0
FC Fastwrite: OFF
Interrupts:        0          Link_failure: 0          Frjt:         0          
Unknown:           0          Loss_of_sync: 0          Fbsy:         0          
Lli:               75         Loss_of_sig:  0          
Proc_rqrd:         37         Protocol_err: 0          
Timed_out:         0          Invalid_word: 0          
Rx_flushed:        0          Invalid_crc:  0          
Tx_unavail:        0          Delim_err:    0          
Free_buffer:       0          Address_err:  0          
Overrun:           0          Lr_in:        2          
Suspended:         0          Lr_out:       13         
Parity_err:        0          Ols_in:       2          
2_parity_err:      0          Ols_out:      2          
CMI_bus_err:       0          

Port part of other ADs: No
swd77:root> portshow 11
portIndex:  11
portName: port11
portHealth: No Fabric Watch License

Authentication: None
portDisableReason: None
portCFlags: 0x1
portFlags: 0x24b03       PRESENT ACTIVE F_PORT G_PORT U_PORT LOGICAL_ONLINE LOGIN NOELP LED ACCEPT FLOGI
LocalSwcFlags: 0x0
portType:  18.0
POD Port: Port is licensed
portState: 1    Online   
Protocol: FC
portPhys:  6    In_Sync         portScn:   32   F_Port    
port generation number:    8
state transition count:    3          

portId:    010b00
portIfId:    43020009
portWwn:   20:0b:50:eb:1a:4c:49:f0
portWwn of device(s) connected:
        21:00:00:60:22:ad:0b:9c
Distance:  normal
portSpeed: N8Gbps

Credit Recovery: Inactive
Aoq: Inactive
FAA: Inactive
F_Trunk: Inactive
LE domain: 0
FC Fastwrite: OFF
Interrupts:        0          Link_failure: 1          Frjt:         0          
Unknown:           0          Loss_of_sync: 0          Fbsy:         0          
Lli:               26         Loss_of_sig:  1          
Proc_rqrd:         1041       Protocol_err: 0          
Timed_out:         0          Invalid_word: 34         
Rx_flushed:        0          Invalid_crc:  0          
Tx_unavail:        0          Delim_err:    0          
Free_buffer:       0          Address_err:  0          
Overrun:           0          Lr_in:        3          
Suspended:         0          Lr_out:       3          
Parity_err:        0          Ols_in:       3          
2_parity_err:      0          Ols_out:      2          
CMI_bus_err:       0          

Port part of other ADs: No
swd77:root> portshow 15
portIndex:  15
portName: port15
portHealth: No Fabric Watch License

Authentication: None
portDisableReason: None
portCFlags: 0x1
portFlags: 0x24b03       PRESENT ACTIVE F_PORT G_PORT U_PORT LOGICAL_ONLINE LOGIN NOELP LED ACCEPT FLOGI
LocalSwcFlags: 0x0
portType:  18.0
POD Port: Port is licensed
portState: 1    Online   
Protocol: FC
portPhys:  6    In_Sync         portScn:   32   F_Port    
port generation number:    6
state transition count:    3          

portId:    010f00
portIfId:    43020008
portWwn:   20:0f:50:eb:1a:4c:49:f0
portWwn of device(s) connected:
        23:00:00:60:22:ad:0b:9c
Distance:  normal
portSpeed: N8Gbps

Credit Recovery: Inactive
Aoq: Inactive
FAA: Inactive
F_Trunk: Inactive
LE domain: 0
FC Fastwrite: OFF
Interrupts:        0          Link_failure: 1          Frjt:         0          
Unknown:           0          Loss_of_sync: 0          Fbsy:         0          
Lli:               28         Loss_of_sig:  1          
Proc_rqrd:         33         Protocol_err: 0          
Timed_out:         0          Invalid_word: 34         
Rx_flushed:        0          Invalid_crc:  0          
Tx_unavail:        0          Delim_err:    0          
Free_buffer:       0          Address_err:  0          
Overrun:           0          Lr_in:        3          
Suspended:         0          Lr_out:       3          
Parity_err:        0          Ols_in:       3          
2_parity_err:      0          Ols_out:      2          
CMI_bus_err:       0          

Port part of other ADs: No
"""