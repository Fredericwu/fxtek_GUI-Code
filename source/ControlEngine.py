#!/usr/bin/python
"""
Control Engine Module

Created by Horatio Lo on 2017-12-12.
Copyright (c) 2017-2018 __Loxoll__. All rights reserved.

"""
import unittest
import ControlName

#
#
# Update engine_info and registered database from selected file (.vpd or . cmg)
#    UpdateInfo(self, i, file='vpd')
#
#    1) Get info from engine to file
#       Engine2File(i, file_name = 'vpd') ; telnet to engine and get the info from engine
#                                   vpd (invoked every backgroup tasks, default is 2 seconds)
#                                   cmg (invoked after configuration change)
#                                   exp (invoked when asked for explore, it may take a long time)
#
#    2) Get info from file to database
#       File2DB(self, i, file="vpd") ; find saved file and convert to DB
#           f = FindFile(i, file='vpd')
#           Parsefile(i, f)
#
# Display info from memory to panel
#    DB2Panel_???()
#
# Perform engine's Telnet command, and update the related database from tmp files
#    ExecuteCommand(i, cmd = 'no command', para1 = '', para2 = '', para3 = '' )
#       
#    1) File4Engine
#    2) File2DB
#
import os, sys, time, glob
import datetime, shutil, zipfile
from telnetlib import Telnet
from ftplib import FTP
import shutil
import ControlTCP, ParseEngineVPD
import tkMessageBox

file_name = os.path.basename(__file__)

from ParseINIfile import ParseINIfile
#cfg =ParseINIfile('Config.ini')
#engine_number = int(cfg['General']['HAAP_NO'])*2

TIMEOUT = 1
GOOD = 0
PASSWORD = "guilogin"
TMPCNT = 5

#
# Telnet executive class, service all TCP related requests
#
class xEngine(object):

    def __init__(self):
#        dbg.printDBG2(file_name, "initiate xEngine")
        pass

    def getVPDfromFile(self, engine_idx):
        dbg.printDBG2(file_name, "getVPDfromFile")
        return True
#
# Prepare to keep the last N trace files (for diagnostic purpose). The file should be used are returned. 
#
    def __PreparedTraceFile(self, suffix, path, prefix, engine_ip, N=2):
        dbg.printDBG4(file_name, "____PreparedTraceFile IP= %s, suffix= %s, path= %s, prefix= %s" % (engine_ip, suffix, path, prefix))

        file_count = 0        
        for file in glob.glob(os.path.join(path, prefix+'*'+suffix)): file_count += 1     

        while file_count >= N: # keep only N suffix files
            # find the oldest file
            oldest_file, oldest_time = None, None
            for dirpath, dirs, files in os.walk(path):
                for filename in files:
                    file_path = os.path.join(dirpath, filename)
                    file_time = os.stat(file_path).st_mtime
                    if file_path.endswith(suffix) and file_path.startswith (path + prefix) and \
                        (file_time<oldest_time or oldest_time is None):
                        oldest_file, oldest_time = file_path, file_time
            
            # remove the oldest file
            if os.path.isfile(oldest_file): os.remove(oldest_file)
            
            # count the .vpd files again
            file_count = 0
            for file in glob.glob(os.path.join(path, prefix+'*'+suffix)): file_count += 1

        new_file_name = path + prefix + datetime.datetime.now().strftime('%m%d%H%M%S') + suffix
        f = open(new_file_name, 'w')

        time_stamp = self.__TimeNow()
        f.write( "Telnet to : " + engine_ip + ", Time Stamp : " + time_stamp + "\n")
        f.close()
        
        return new_file_name
        
    def Engine2File(self, engine_idx, file_ext = 'vpd'):
        dbg.printDBG2(file_name, "Engine2File Engine= %s, file_ext= %s" % (engine_idx, file_ext))
        fwv = engine_info[engine_idx]['Firmware'][:5]
        dbg.printDBG4(file_name, "Firmware Version= %s" % fwv)
        
        if SIMMOD == 1: return True
        
        engine_ip = cfg['Engine'+str(engine_idx)]['IP']
        f = self.__PreparedTraceFile('.'+file_ext, './trace/', 'E%s-' % engine_idx, engine_ip)

        try:
            self.tn = Telnet(engine_ip, timeout = TWO_SECOND)
        except:
            return False

        self.logfile = open(f, 'a')
        self.logfile.write(self.tn.read_lazy())
        check_string = "password: "
        s = self.tn.read_until(check_string, timeout = TWO_SECOND)
        self.logfile.write( s)

        if s[-len(check_string):] != check_string:
            dbg.printDBG3(file_name, "telnet time-out, expecting %s, got %s" % (check_string, s[-len(check_string):]))
            self.logfile.close()
            return False

        prompt_num = 0
        if (self.InputToExpect( "%s\r" % PASSWORD, " %s > " % prompt_num)): return False
        prompt_num += 1        
        
        if file_ext == 'vpd':
            if (self.InputToExpect( "7", "CLI>", 'vpd')): return False
            if (self.InputToExpect( "vpd\r", "CLI>", 'vpd')): return False
            if (self.InputToExpect( "mirror\r", "CLI>", 'vpd')): return False
            if (self.InputToExpect( "conmgr engine status\r", "CLI>", 'vpd')): return False
            if (self.InputToExpect( "conmgr drive status\r", "CLI>", 'vpd')): return False
            if (self.InputToExpect( "conmgr initiator status\r", "CLI>", 'vpd')): return False
            if (self.InputToExpect( "port\r", "CLI>", 'vpd')): return False
            if (self.InputToExpect( "engine\r", "CLI>", 'vpd')): return False
#            if (self.InputToExpect( "license status\r", "CLI>", 'vpd')): return False
#            if (self.InputToExpect( "aca\r", "CLI>", 'vpd')): return False        
#            if (self.InputToExpect( "vaai\r", "CLI>", 'vpd')): return False        
            if (self.InputToExpect( "drvstate\r", "CLI>", 'vpd')): return False
            if (self.InputToExpect( "rebuild\r", "CLI>", 'vpd')): return False
            if (self.InputToExpect( "bpt\r", "CLI>", 'vpd')): return False
            if (self.InputToExpect( "2nd new\r", "CLI>", 'vpd')): return False
        elif file_ext == 'cmg':
#
            if fwv == 'V15.7':
                if (self.InputToExpect( "6", "(Y/N)")): return False
                if (self.InputToExpect( "Y", " %s > " % prompt_num)): return False
                prompt_num += 1
            else:
                if (self.InputToExpect( "6", " %s > " % prompt_num)): return False
                prompt_num += 1
#
#        Configure which interface?
#        	A = Port A1
#        	B = Port A2
#        	C = Port B1
#        	D = Port B2
#        	E = Ethernet (port 1)
#        	F = Ethernet (port 2)
#        	M = Cycle serial port end-of-line mode
#        	S = Storage Emulation
#        	X = Toggle shutdown behaviour of host-only ports
#        	      (stay up if no storage or engines seen)
#        	<Enter> = done
#
            if (self.InputToExpect( "A", " %s > " % prompt_num)): return False
            prompt_num += 1
            if (self.InputToExpect( "\r", " %s > " % prompt_num)): return False
            prompt_num += 1
            if (self.InputToExpect( "B", " %s > " % prompt_num)): return False
            prompt_num += 1
            if (self.InputToExpect( "\r", " %s > " % prompt_num)): return False
            prompt_num += 1
            if (self.InputToExpect( "C", " %s > " % prompt_num)): return False
            prompt_num += 1
            if (self.InputToExpect( "\r", " %s > " % prompt_num)): return False
            prompt_num += 1
            if (self.InputToExpect( "D", " %s > " % prompt_num)): return False
            prompt_num += 1
            if (self.InputToExpect( "\r", " %s > " % prompt_num)): return False
            prompt_num += 1
            if (self.InputToExpect( "S", " %s > " % prompt_num)): return False
            prompt_num += 1
            if (self.InputToExpect( "\r", " %s > " % prompt_num)): return False
            prompt_num += 1
            prompt_num += 1         # FW increase the prompt twice here !!!
            if (self.InputToExpect( "\r", " %s > " % prompt_num)): return False
            prompt_num += 1
            if (self.InputToExpect( "7", "CLI>")): return False
            if (self.InputToExpect( "conmgr engine status\r", "CLI>")): return False
            if (self.InputToExpect( "conmgr drive status\r", "CLI>")): return False
            if (self.InputToExpect( "conmgr initiator status\r", "CLI>")): return False
            if (self.InputToExpect( "engine\r", "CLI>")): return False
            if (self.InputToExpect( "drvstate\r", "CLI>")): return False
            if (self.InputToExpect( "license status\r", "CLI>")): return False
#            if (self.InputToExpect( "conmgr auto\r", "CLI>")): return False         # to get serial number
            if (self.InputToExpect( "conmgr\r", "CLI>")): return False              # to get serial number
            if (self.InputToExpect( "conmgr read\r", "CLI>")): return False         # to get serial number
            if (self.InputToExpect( "conmgr mode\r", "CLI>")): return False
            if (self.InputToExpect( "sfp a1\r", "CLI>")): return False
            if (self.InputToExpect( "sfp a2\r", "CLI>")): return False
            if (self.InputToExpect( "sfp b1\r", "CLI>")): return False
            if (self.InputToExpect( "sfp b2\r", "CLI>")): return False
            if (self.InputToExpect( "port\r", "CLI>")): return False
            if (self.InputToExpect( "proxy\r", "CLI>")): return False
            if (self.InputToExpect( "video\r", "CLI>")): return False
            if (self.InputToExpect( "timeout\r", "CLI>")): return False
            if (self.InputToExpect( "group\r", "CLI>")): return False
            if (self.InputToExpect( "map\r", "CLI>")): return False
            if (self.InputToExpect( "site\r", "CLI>")): return False
            if (self.InputToExpect( "rtc\r", "CLI>")): return False
            if (self.InputToExpect( "rls\r", "CLI>")): return False
            if fwv != 'V15.7':
                if (self.InputToExpect( "vaai\r", "CLI>")): return False
                if (self.InputToExpect( "aca\r", "CLI>")): return False
                if (self.InputToExpect( "health\r", "CLI>")): return False
                if (self.InputToExpect( "serial\r", "CLI>")): return False
                if (self.InputToExpect( "quorum\r", "CLI>")): return False
    
        if (self.InputToExpect( "exit\r", " %s > " % prompt_num, 'vpd')): return False
        if (self.InputToExpect( "q", "(Y/N)", 'vpd')): return False
        if (self.InputToExpect( "y", "Bye!", 'vpd')): return False
        self.logfile.close()

        return True
#
# Perform engine's Telnet command, and update the related database from tmp files
#    ExecuteCommand(i, cmd = 'no command', para1 = '', para2 = '', para3 = '' )
#       
#    1) File4Engine
#    2) cmd_Explore para1 = port
#    3) File2DB
#        
    def ExecuteCommand(self, i, cmd = 'no command', para1 = '', para2 = '', para3 = '' ):
        dbg.printDBG2(file_name, "ExecuteCommand for Engine%s, cmd= %s, papa1= %s, papa2= %s, para3 = %s" 
            % (i, cmd, para1, para2, para3))

        if SIMMOD == 1:
            p = ParseEngineVPD.ParseEngineVPD()
            print "1111"
            
            p.ParseFile(i, "./trace/E0A1-0107181956.exp", 'exp', para1)
            return True

        engine_ip = cfg['Engine'+str(i)]['IP']
        DEFINED_CMD =  ['cmd_Explore',
                        'cmd_CreateMirror',
                        'cmd_Reboot'
                        ]
#
# Prepare files
#
        if cmd == DEFINED_CMD[0]:   # CLI>explore a1 ; from "ExecuteCommand(i, 'cmd_Explore', 'a1'" )
            f = self.__PreparedTraceFile('.exp', './trace/', 'E%s%s-' % (i, para1), engine_ip)
        elif cmd == DEFINED_CMD[1]:
            f = self.__PreparedTraceFile('.tmp', './trace/', 'E%s-' % i, engine_ip)
            pass

        else:       
            print ("command = ", cmd, "Not Defined")
            return False

        try:
            self.tn = Telnet(engine_ip, timeout = TWO_SECOND)
        except:
            return False

        self.logfile = open(f, 'a')
        self.logfile.write( self.tn.read_lazy())
        check_string = "password: "
        s = self.tn.read_until(check_string, timeout = TWO_SECOND)
        self.logfile.write( s)

        if s[-len(check_string):] != check_string:
            dbg.printDBG3(file_name, "telnet time-out, expecting %s, got %s" % (check_string, s[-len(check_string):]))
            return False
        prompt_num = 0
        if (self.InputToExpect( "%s\r" % PASSWORD, " %s > " % prompt_num, 'vpd')): return False
        prompt_num += 1        
#
# Dispatch commands
#
        if cmd == DEFINED_CMD[0]:   # CLI>explore a1 ; from "ExecuteCommand(i, 'cmd_Explore', 'a1'" )
            if (self.InputToExpect( "7", "CLI>")): return False
            if (self.InputToExpect( "explore %s\r" % para1, "CLI>")): return False

        elif cmd == DEFINED_CMD[1]:
            pass

        if (self.InputToExpect( "exit\r", " %s > " % prompt_num)): return False
        if (self.InputToExpect( "q", "(Y/N)")): return False
        if (self.InputToExpect( "y", "Bye!")): return False
        self.logfile.close()
        
        #
        # Now update the DB
        p = ParseEngineVPD.ParseEngineVPD()
        
        p.ParseFile(i, f, 'exp', para1)
        return True
#
# Telnet CLI to Engine commands
#
    def RebootEngine(self, engine_idx):
        dbg.printDBG2(file_name, "Boot Engine for Engine%s" % engine_idx)

        engine_ip = cfg['Engine'+str(engine_idx)]['IP']
        f = self.__PreparedTraceFile('.tmp', './trace/', 'E%s-' % engine_idx, engine_ip, TMPCNT)

        try:
            self.tn = Telnet(engine_ip, timeout = TWO_SECOND)
        except:
            return False

        self.logfile = open(f, 'a')
        self.logfile.write( self.tn.read_lazy())
        check_string = "password: "
        s = self.tn.read_until(check_string, timeout = TWO_SECOND)
        self.logfile.write( s)

        if s[-len(check_string):] != check_string:
            dbg.printDBG3(file_name, "telnet time-out, expecting %s, got %s" % (check_string, s[-len(check_string):]))
            return False

        if (self.InputToExpect( "%s\r" % PASSWORD, " 0 > ")): return False
        if (self.InputToExpect( "b", "(Y/N)")): return False
        time.sleep(2)                                      # need to wait, otherwise will fail sometimes
        if (self.InputToExpect( "y", "")): return False
        self.logfile.close()
        return True
#
# conmgr drive add ... add a drive to edit buffer
# conmgr drive delete ... delete a drive from edit buffer
# conmgr drive path ... adds or removes a path to a multipath drive, or changes the path weights of a multipath drive path
#
# conmgr drive add <drive_type> <drive_num> [<conn_cnt>] <conn_params>
#
# conmgr drive path add <drive_num> <conn_params>
# conmgr drive path remove <drive_num> <path_num>
#
# Option
# drive_type: [ S | AA | AP]
# Defines the connection between drive and engine. Single path, active-active path, or active-passive path.
# conn_cnt
# Number of connections between engine and drive, this is omitted when drive type is single
# conn_params: <engine_port_id> <storage_wwpn> <storage_lun>[<weight_read> <weight_write>]
#
# CLI>conmgr drive add aa 0 b1 2100-006022-ad0b32 0 1 1
#
# CLI>conmgr
#  1 Drives
#  ==========
#  tnum type port wwpn lun rd wr
#  0 A-A B1 2100-006022-ad0b32 0000-000000000000 1 1
# 
#  0 Engines       our engine number: 65535
#  ===========
#
#  0 Initiators
#  ==============
#
#
# CLI>conmgr drive path add 0 b2 2100-006022-adb036 0 0 0
#
#  1 Drives
#  ==========
#  tnum type port wwpn lun rd wr
#  0 A-A B1 2100-006022-ad0b32 0000-000000000000 1 1
#        B2 2100-006022-adb036 0000-000000000000 0 0
#
# if p.SetManualRegister(i, device, type, port, wwpn, lun_no, tnum) == False:
#
    def SetManualRegister(self, engine_idx, device, ptype, port, wwpn, lun_no, tnum):
        dbg.printDBG4(file_name, "Set Manual Register for Engine%s, device= %s, type= %s, port= %s, wwpn= %s, lun_on= %s, tnum= %s" 
            % (engine_idx, device, ptype, port, wwpn, lun_no, tnum))

        engine_ip = cfg['Engine'+str(engine_idx)]['IP']
        f = self.__PreparedTraceFile('.tmp', './trace/', 'E%s-' % engine_idx, engine_ip, TMPCNT)
        self.response = []

        try:
            self.tn = Telnet(engine_ip, timeout = TWO_SECOND)
        except:
            return False

        self.logfile = open(f, 'a')
        self.logfile.write( self.tn.read_lazy())
        check_string = "password: "
        s = self.tn.read_until(check_string, timeout = TWO_SECOND)
        self.logfile.write( s)

        if s[-len(check_string):] != check_string:
            dbg.printDBG3(file_name, "telnet time-out, expecting %s, got %s" % (check_string, s[-len(check_string):]))
            return False

        if (self.InputToExpect( "%s\r" % PASSWORD, " 0 > ")): return False

        if (self.InputToExpect( "7", "CLI>")): return False
        if (self.InputToExpect( "conmgr read\r", "CLI>")): return False
        if device == 'LUN':
            if (self.InputToExpect( "conmgr drive add %s %s %s %s %s 1 1\r" % (ptype, tnum[1:], port, wwpn, lun_no), "CLI>")): return False
        elif device == 'LUN Path':
            if (self.InputToExpect( "conmgr drive path add %s %s %s %s 1 1\r" % (tnum[1:], port, wwpn, lun_no), "CLI>")): return False
        elif device == 'HBA':
            if (self.InputToExpect( "conmgr initiator add %s %s %s\r" % (tnum[1:], port, wwpn), "CLI>")): return False
        elif device == 'Engine':
            if (self.InputToExpect( "conmgr engine add %s %s %s\r" % (tnum[1:], port, wwpn), "CLI>")): return False
        elif device == 'Engine Path':
            if (self.InputToExpect( "conmgr engine path add %s %s %s\r" % (tnum[1:], port, wwpn), "CLI>")): return False
        else:
            pass
            
        self.return_string = self.response[2]
#        print self.response[2]
        
        if (self.InputToExpect( "conmgr write\r", "CLI>")): return False
        if (self.InputToExpect( "conmgr read\r", "CLI>")): return False
        if (self.InputToExpect( "exit\r", " 1 > ")): return False

        if (self.InputToExpect( "q", "(Y/N)")): return False
        if (self.InputToExpect( "y", "Bye!")): pass
        self.logfile.close()
        return True
#
    def RemoveManualRegister(self, engine_idx, tnum):
        dbg.printDBG4(file_name, "Remove Manual Register for Engine%s, tnum= %s" % (engine_idx, tnum))

        engine_ip = cfg['Engine'+str(engine_idx)]['IP']
        f = self.__PreparedTraceFile('.tmp', './trace/', 'E%s-' % engine_idx, engine_ip, TMPCNT)

        try:
            self.tn = Telnet(engine_ip, timeout = TWO_SECOND)
        except:
            return False

        self.logfile = open(f, 'a')
        self.logfile.write( self.tn.read_lazy())
        check_string = "password: "
        s = self.tn.read_until(check_string, timeout = TWO_SECOND)
        self.logfile.write( s)

        if s[-len(check_string):] != check_string:
            dbg.printDBG3(file_name, "telnet time-out, expecting %s, got %s" % (check_string, s[-len(check_string):]))
            return False

        if (self.InputToExpect( "%s\r" % PASSWORD, " 0 > ")): return False

        if (self.InputToExpect( "7", "CLI>")): return False
        if (self.InputToExpect( "conmgr read\r", "CLI>")): return False
        if tnum[:1] == 'T':
            if (self.InputToExpect( "conmgr drive delete %s\r" % tnum[1:], "CLI>")): return False
        elif tnum[:1] == 'I':
            if (self.InputToExpect( "conmgr initiator delete %s\r" % tnum[1:], "CLI>")): return False
        elif tnum[:1] == 'E':
            if (self.InputToExpect( "conmgr engine delete %s\r" % tnum[1:], "CLI>")): return False
        else:
            pass
        if (self.InputToExpect( "conmgr write\r", "CLI>")): return False
        if (self.InputToExpect( "conmgr read\r", "CLI>")): return False
        if (self.InputToExpect( "exit\r", " 1 > ")): return False

        if (self.InputToExpect( "q", "(Y/N)")): return False
        if (self.InputToExpect( "y", "Bye!")): pass
        self.logfile.close()
        return True
#
    def ChangeMapStructure(self, engine_idx, cmd, mirror_structure, lun, host_group, ):  
        dbg.printDBG2(file_name, "Engine%s ChangeMapStructure: %s, %s, %s, %s" % (engine_idx, cmd, mirror_structure, lun, host_group))
        
        engine_ip = cfg['Engine'+str(engine_idx)]['IP']
        f = self.__PreparedTraceFile('.tmp', './trace/', 'E%s-' % engine_idx, engine_ip, TMPCNT)

        try:
            self.tn = Telnet(engine_ip, timeout = TWO_SECOND)
        except:
            return False

        self.logfile = open(f, 'a')
        self.logfile.write( self.tn.read_lazy())
        check_string = "password: "
        s = self.tn.read_until(check_string, timeout = TWO_SECOND)
        self.logfile.write( s)

        if s[-len(check_string):] != check_string:
            dbg.printDBG3(file_name, "telnet time-out, expecting %s, got %s" % (check_string, s[-len(check_string):]))
            return False

        if (self.InputToExpect( "%s\r" % PASSWORD, " 0 > ")): return False
        if (self.InputToExpect( "7", "CLI>")): return False

        if cmd == 'Delete':   # 'Delete'
            if (self.InputToExpect( "map %s delete\r" % mirror_structure, "CLI>")): return False
        elif cmd == 'Skip':
            if (self.InputToExpect( "map %s 0xffff\r" % mirror_structure, "CLI>")): return False        
        elif cmd == 'Add':
            if lun != '':
                if (self.InputToExpect( "map %s %s\r" % (mirror_structure, lun), "CLI>")): return False
            if host_group != '':
                if (self.InputToExpect( "map %s apply %s\r" % (mirror_structure, host_group), "CLI>")): return False                
        
        if (self.InputToExpect( "exit\r", " 1 > ")): return False
        if (self.InputToExpect( "q", "(Y/N)")): return False
        if (self.InputToExpect( "y", "Bye!")): return False
        self.logfile.close()
        return True
#
    def ChangeHostGroup(self, engine_idx, cmd, group_num, hba):  
        dbg.printDBG2(file_name, "Engine%s ChangeHostGroup: %s, %s, %s" % (engine_idx, cmd, group_num, hba))
        
        engine_ip = cfg['Engine'+str(engine_idx)]['IP']
        f = self.__PreparedTraceFile('.tmp', './trace/', 'E%s-' % engine_idx, engine_ip, TMPCNT)

        try:
            self.tn = Telnet(engine_ip, timeout = TWO_SECOND)
        except:
            return False

        self.logfile = open(f, 'a')
        self.logfile.write( self.tn.read_lazy())
        check_string = "password: "
        s = self.tn.read_until(check_string, timeout = TWO_SECOND)
        self.logfile.write( s)

        if s[-len(check_string):] != check_string:
            dbg.printDBG3(file_name, "telnet time-out, expecting %s, got %s" % (check_string, s[-len(check_string):]))
            return False

        if (self.InputToExpect( "%s\r" % PASSWORD, " 0 > ")): return False
        if (self.InputToExpect( "7", "CLI>")): return False
        if cmd == 'Add':
            if (self.InputToExpect( "group hba %s %s\r" % (group_num, hba), "CLI>")): return False
        else:   # 'Delete'
            if (self.InputToExpect( "group hba %s delete\r" % group_num, "CLI>")): return False            
        
        if (self.InputToExpect( "exit\r", " 1 > ")): return False
        if (self.InputToExpect( "q", "(Y/N)")): return False
        if (self.InputToExpect( "y", "Bye!")): return False
        self.logfile.close()
        return True
#
    def ChangeRebuild(self, engine_idx, lun, cmd, value, member=0):  
        dbg.printDBG2(file_name, "Engine%s ChangeRebuild: %s, %s, %s, %s" % (engine_idx, lun, cmd, value, member))
        
        engine_ip = cfg['Engine'+str(engine_idx)]['IP']
        f = self.__PreparedTraceFile('.tmp', './trace/', 'E%s-' % engine_idx, engine_ip, TMPCNT)

        try:
            self.tn = Telnet(engine_ip, timeout = TWO_SECOND)
        except:
            return False

        self.logfile = open(f, 'a')
        self.logfile.write( self.tn.read_lazy())
        check_string = "password: "
        s = self.tn.read_until(check_string, timeout = TWO_SECOND)
        self.logfile.write( s)

        if s[-len(check_string):] != check_string:
            dbg.printDBG3(file_name, "telnet time-out, expecting %s, got %s" % (check_string, s[-len(check_string):]))
            return False

            list_of_cmd = ["Speed", "Pause", "Resume", "Abort", "Permit", "IOPS"]   

        if (self.InputToExpect( "%s\r" % PASSWORD, " 0 > ")): return False
        if (self.InputToExpect( "7", "CLI>")): return False
        if cmd == 'Speed':
            if (self.InputToExpect( "rebuild speed %s %s %s\r" % (lun, member, value), "CLI>")): return False
        elif cmd == 'IOPS':
            if (self.InputToExpect( "rebuild iops %s %s %s\r" % (lun, member, value), "CLI>")): return False
        elif cmd == 'Abort':
            if (self.InputToExpect( "rebuild abort %s %s\r" % (lun, member), "CLI>")): return False
        elif cmd == 'Pause':
            if (self.InputToExpect( "rebuild pause %s %s\r" % (lun, member), "CLI>")): return False
        elif cmd == 'Resume':
            if (self.InputToExpect( "rebuild resume %s %s\r" % (lun, member), "CLI>")): return False
        elif cmd == 'Permit':
            if (self.InputToExpect( "rebuild permit %s %s\r" % (lun, member), "CLI>")): return False
        else:
            pass
        
        if (self.InputToExpect( "exit\r", " 1 > ")): return False
        if (self.InputToExpect( "q", "(Y/N)")): return False
        if (self.InputToExpect( "y", "Bye!")): return False
        self.logfile.close()
        return True
#
#
    def ChangeDRB(self, engine_idx, cmd, value):  
        dbg.printDBG2(file_name, "Engine%s ChangeRebuild: %s, %s" % (engine_idx, cmd, value))
        
        engine_ip = cfg['Engine'+str(engine_idx)]['IP']
        f = self.__PreparedTraceFile('.tmp', './trace/', 'E%s-' % engine_idx, engine_ip, TMPCNT)

        try:
            self.tn = Telnet(engine_ip, timeout = TWO_SECOND)
        except:
            return False

        self.logfile = open(f, 'a')
        self.logfile.write( self.tn.read_lazy())
        check_string = "password: "
        s = self.tn.read_until(check_string, timeout = TWO_SECOND)
        self.logfile.write( s)

        if s[-len(check_string):] != check_string:
            dbg.printDBG3(file_name, "telnet time-out, expecting %s, got %s" % (check_string, s[-len(check_string):]))
            return False

            list_of_cmd = ["Speed", "Pause", "Resume", "Abort", "Permit", "IOPS"]   

        if (self.InputToExpect( "%s\r" % PASSWORD, " 0 > ")): return False
        if (self.InputToExpect( "7", "CLI>")): return False
        if cmd == 'Default Speed':
            if (self.InputToExpect( "rebuild default speed %s\r" % value, "CLI>")): return False
        elif cmd == 'Default IOPS':
            if (self.InputToExpect( "rebuild default iops %s\r" % value, "CLI>")): return False
        else:
            pass
        
        if (self.InputToExpect( "exit\r", " 1 > ")): return False
        if (self.InputToExpect( "q", "(Y/N)")): return False
        if (self.InputToExpect( "y", "Bye!")): return False
        self.logfile.close()
        return True
#
    def ChangeAutoMap(self, engine_idx, selected_mode):  
        dbg.printDBG2(file_name, "Engine%s ChangeAutoMap: %s" % (engine_idx, selected_mode))
        
        if selected_mode == "Auto Map: Disable":
            selected_mode = 'off'
        else:
            selected_mode = 'on'
        
        engine_ip = cfg['Engine'+str(engine_idx)]['IP']
        f = self.__PreparedTraceFile('.tmp', './trace/', 'E%s-' % engine_idx, engine_ip, TMPCNT)

        try:
            self.tn = Telnet(engine_ip, timeout = TWO_SECOND)
        except:
            return False

        self.logfile = open(f, 'a')
        self.logfile.write( self.tn.read_lazy())
        check_string = "password: "
        s = self.tn.read_until(check_string, timeout = TWO_SECOND)
        self.logfile.write( s)

        if s[-len(check_string):] != check_string:
            dbg.printDBG3(file_name, "telnet time-out, expecting %s, got %s" % (check_string, s[-len(check_string):]))
            return False

        if (self.InputToExpect( "%s\r" % PASSWORD, " 0 > ")): return False
        if (self.InputToExpect( "7", "CLI>")): return False
        if (self.InputToExpect( "map auto %s\r" % selected_mode, "CLI>")): return False
        if (self.InputToExpect( "exit\r", " 1 > ")): return False
        if (self.InputToExpect( "q", "(Y/N)")): return False
        if (self.InputToExpect( "y", "Bye!")): return False
        self.logfile.close()
        return True
#
    def ChangeConmgrMode(self, engine_idx, selected_mode):  
        dbg.printDBG2(file_name, "Engine%s ChangeConmgrMode: %s" % (engine_idx, selected_mode))
        
        engine_ip = cfg['Engine'+str(engine_idx)]['IP']
        f = self.__PreparedTraceFile('.tmp', './trace/', 'E%s-' % engine_idx, engine_ip, TMPCNT)

        try:
            self.tn = Telnet(engine_ip, timeout = TWO_SECOND)
        except:
            return False

        self.logfile = open(f, 'a')
        self.logfile.write( self.tn.read_lazy())
        check_string = "password: "
        s = self.tn.read_until(check_string, timeout = TWO_SECOND)
        self.logfile.write( s)

        if s[-len(check_string):] != check_string:
            dbg.printDBG3(file_name, "telnet time-out, expecting %s, got %s" % (check_string, s[-len(check_string):]))
            return False

        if (self.InputToExpect( "%s\r" % PASSWORD, " 0 > ")): return False
        if (self.InputToExpect( "7", "CLI>")): 
            return False
        if (self.InputToExpect( "conmgr read\r", "CLI>")): return False
        if (self.InputToExpect( "conmgr mode %s\r" % selected_mode[-4:], "CLI>")): return False
        if (self.InputToExpect( "conmgr write\r", "CLI>")): return False
        if (self.InputToExpect( "exit\r", " 1 > ")): return False
        if (self.InputToExpect( "q", "(Y/N)")): return False
        if (self.InputToExpect( "y", "Bye!")): return False
        self.logfile.close()
        return True
#
    def ChangeEngineNumber(self, engine_idx, selected_num):  
        dbg.printDBG2(file_name, "Engine%s ChangeEngineNumber: %s" % (engine_idx, selected_num))
        
        engine_ip = cfg['Engine'+str(engine_idx)]['IP']
        f = self.__PreparedTraceFile('.tmp', './trace/', 'E%s-' % engine_idx, engine_ip, TMPCNT)

        try:
            self.tn = Telnet(engine_ip, timeout = TWO_SECOND)
        except:
            return False

        self.logfile = open(f, 'a')
        self.logfile.write( self.tn.read_lazy())
        check_string = "password: "
        s = self.tn.read_until(check_string, timeout = TWO_SECOND)
        self.logfile.write( s)

        if s[-len(check_string):] != check_string:
            dbg.printDBG3(file_name, "telnet time-out, expecting %s, got %s" % (check_string, s[-len(check_string):]))
            return False

        if (self.InputToExpect( "%s\r" % PASSWORD, " 0 > ")): return False
        if (self.InputToExpect( "7", "CLI>")): 
            return False
        if (self.InputToExpect( "conmgr read\r", "CLI>")): return False
        if (self.InputToExpect( "conmgr engine set %s\r" % selected_num, "CLI>")): return False
        if (self.InputToExpect( "conmgr write\r", "CLI>")): return False
        if (self.InputToExpect( "exit\r", " 1 > ")): return False
        if (self.InputToExpect( "q", "(Y/N)")): return False
        if (self.InputToExpect( "y", "Bye!")): return False
        self.logfile.close()
        return True
#
    def EraseCmgfromEngine(self, engine_idx):
        dbg.printDBG2(file_name, "EraseCmgfromEngine")

        engine_ip = cfg['Engine'+str(engine_idx)]['IP']
        f = self.__PreparedTraceFile('.tmp', './trace/', 'E%s-' % engine_idx, engine_ip, TMPCNT)

        try:
            self.tn = Telnet(engine_ip, timeout = TWO_SECOND)
        except:
            return False

        self.logfile = open(f, 'a')
        self.logfile.write( self.tn.read_lazy())
        check_string = "password: "
        s = self.tn.read_until(check_string, timeout = TWO_SECOND)
        self.logfile.write( s)

        if s[-len(check_string):] != check_string:
            dbg.printDBG3(file_name, "telnet time-out, expecting %s, got %s" % (check_string, s[-len(check_string):]))
            return False

        if (self.InputToExpect( "%s\r" % PASSWORD, " 0 > ")): return False
        if (self.InputToExpect( "9", "(Y/N)")): return False
        if (self.InputToExpect( "y", " > ")): return False
        if (self.InputToExpect( "b", "(Y/N)")): return False
        time.sleep(2)                                      # need to wait, otherwise will fail sometimes
        if (self.InputToExpect( "Y", "")): return False
        self.logfile.close()
        return True
        
        """
        if (self.InputToExpect( "7", "CLI>")): 
            return False
        if (self.InputToExpect( "conmgr erase\r", "CLI>")): return False
        if (self.InputToExpect( "conmgr write\r", "CLI>")): return False
        if (self.InputToExpect( "conmgr engine status\r", "CLI>")): return False
        if (self.InputToExpect( "conmgr drive status\r", "CLI>")): return False
        if (self.InputToExpect( "conmgr initiator status\r", "CLI>")): return False
        if (self.InputToExpect( "exit\r", " 1 > ")): return False
        if (self.InputToExpect( "q", "(Y/N)")): return False
        if (self.InputToExpect( "y", "Bye!")): return False
        self.logfile.close()
        return True
        """
#
    def AutoCmgfromEngine(self, engine_idx, tp):
        dbg.printDBG4(file_name, "AutoCmgfromEngine for Engine%s, type= %s" % (engine_idx, tp))

        engine_ip = cfg['Engine'+str(engine_idx)]['IP']
        f = self.__PreparedTraceFile('.tmp', './trace/', 'E%s-' % engine_idx, engine_ip, TMPCNT)

        try:
            self.tn = Telnet(engine_ip, timeout = TWO_SECOND)
        except:
            return False

        self.logfile = open(f, 'a')
        self.logfile.write( self.tn.read_lazy())
        check_string = "password: "
        s = self.tn.read_until(check_string, timeout = TWO_SECOND)
        self.logfile.write( s)

        if s[-len(check_string):] != check_string:
            dbg.printDBG3(file_name, "telnet time-out, expecting %s, got %s" % (check_string, s[-len(check_string):]))
            return False

        if (self.InputToExpect( "%s\r" % PASSWORD, " 0 > ")): return False
        if (self.InputToExpect( "7", "CLI>")): 
            return False
        if tp != 'Engine':
            if (self.InputToExpect( "conmgr auto %s \r" % tp.lower(), "CLI>")): return False
            if (self.InputToExpect( "conmgr write\r", "CLI>")): return False
            if (self.InputToExpect( "conmgr engine status\r", "CLI>")): return False
            if (self.InputToExpect( "conmgr drive status\r", "CLI>")): return False
            if (self.InputToExpect( "conmgr initiator status\r", "CLI>")): return False
            if (self.InputToExpect( "drvstate\r", "CLI>")): return False
            if (self.InputToExpect( "exit\r", " 1 > ")): return False
            if (self.InputToExpect( "q", "(Y/N)")): return False
            if (self.InputToExpect( "y", "Bye!")): return False
            self.logfile.close()
            return True
        else:   # config Engines now
            if (self.InputToExpect( "conmgr auto %s \r" % tp.lower(), "CLI>")): return False
            if (self.InputToExpect( "alert_halt 990\r", "CLI>")): return False            
            if (self.InputToExpect( "conmgr write\r", "CLI>")): return False
            if (self.InputToExpect( "conmgr engine status\r", "CLI>")): return False
            if (self.InputToExpect( "conmgr drive status\r", "CLI>")): return False
            if (self.InputToExpect( "conmgr initiator status\r", "CLI>")): return False
            if (self.InputToExpect( "drvstate\r", "CLI>")): return False
            if (self.InputToExpect( "exit\r", " 1 > ")): return False
            if (self.InputToExpect( "q", "(Y/N)")): return False
            if (self.InputToExpect( "y", "Bye!")): return False
            self.logfile.close()
            return True
#
    def SetNewMode(self, engine_idx, line, application, state):
        dbg.printDBG2(file_name, "Set New Mode for engine%s, application=%s, state=%s" % (engine_idx, application, state))
        
#        if self.__ReadyConfigTelnetCLI(engine_idx) == False:
#            self.logfile.close()
#            return False
            
        if application == 'IBM AIX Support':
            dbg.printDBG2(file_name, "Turn %s IBM AIX Support" % state)
            #
            # Set ACA mode
            if (self.InputToExpect_cfg("aca %s\r" % state.lower(), "CLI>")): return False
            #
            # Set SDD mode
            prompt_num = 1
            if (self.InputToExpect( "exit\r", " %s > " % prompt_num)): return False
            prompt_num += 1
            if (self.InputToExpect( "6", " %s > " % prompt_num)): return False
            prompt_num += 1
            #
            #        Configure which interface?
            #        	A = Port A1
            #        	B = Port A2
            #        	C = Port B1
            #        	D = Port B2
            #        	E = Ethernet (port 1)
            #        	F = Ethernet (port 2)
            #        	M = Cycle serial port end-of-line mode
            #        	S = Storage Emulation
            #        	X = Toggle shutdown behaviour of host-only ports
            #        	      (stay up if no storage or engines seen)
            #        	<Enter> = done
            #
            if (self.InputToExpect( "S", " %s > " % prompt_num)): return False
            prompt_num += 1
            if state == 'ON':
                if (self.InputToExpect( "S", " %s > " % prompt_num)): return False
            else:
                if (self.InputToExpect( "D", " %s > " % prompt_num)): return False
            prompt_num += 1
            
            if (self.InputToExpect( "\r", " %s > " % prompt_num)): return False
            prompt_num += 1
            if (self.InputToExpect( "\r", " %s > " % prompt_num)): return False
            prompt_num += 1
            prompt_num += 1         # FW increase the prompt twice here !!!
            if (self.InputToExpect( "q", "(Y/N)")): return False
            if (self.InputToExpect( "y", "Bye!")): return False
        
        elif application == 'VMware Support':
            #
            # Set VMware mode
            if (self.InputToExpect_cfg("vaai %s\r" % state.lower(), "CLI>")): return False
            if self.__CloseConfigTelnetCLI(engine_idx) == False:
                self.logfile.close()            
                return False
            
        elif application == 'Video Support':
            #
            # Set Video mode
            if (self.InputToExpect_cfg("video %s\r" % state.lower(), "CLI>")): return False
            if self.__CloseConfigTelnetCLI(engine_idx) == False:
                self.logfile.close()            
                return False

        elif application == 'Auto Map Mode':
            #
            # Set Auto Map Mode
            if (self.InputToExpect_cfg("map auto %s\r" % state.lower(), "CLI>")): return False
            if self.__CloseConfigTelnetCLI(engine_idx) == False:
                self.logfile.close()            
                return False

        elif application == 'Site Isolation Protection':
            if state == 'OFF':
                if (self.InputToExpect_cfg("site erase\r", "CLI>")): return False
            else:   # need more work to set the Site Isolation Protection
                if self.__CloseConfigTelnetCLI(engine_idx) == False:
                    pass
                self.logfile.close()            
                return False
                
            if self.__CloseConfigTelnetCLI(engine_idx) == False:
                self.logfile.close()            
                return False

        elif application == 'MPIO Use Serial Number':
            if SIMMOD == 1:
                self.logfile.close()            
                return False
                
            if state == 'OFF':
                if (self.InputToExpect_cfg("conmgr mode wwnn\r", "CLI>")): return False
            else:   # need more work to set the Site Isolation Protection
                if (self.InputToExpect_cfg("conmgr mode pg83\r", "CLI>")): return False
                
            if self.__CloseConfigTelnetCLI(engine_idx) == False:
                self.logfile.close()            
                return False
            
        else:
            return
#
        self.logfile.close()
        return True
#
    def SetNewLicense(self, engine_idx, feature, key):
        dbg.printDBG1(file_name, "SetNewLicense engine%s, feature=%s, key=%s" % (engine_idx, feature, key))

        if self.__ReadyConfigTelnetCLI(engine_idx) == False:
            self.logfile.close()
            return False
#
# CLI>license install 3 2550346468
#
        if (self.InputToExpect_cfg("license install %s %s\r" % (feature, key), "CLI>")): return False
#
# CLI>license status
#
        if (self.InputToExpect_cfg( "license status\r", "CLI>")): return False
#
# update engine_info["License"]
#
        p = ParseEngineVPD.ParseEngineVPD()
        p.DecodeLicense(engine_idx, self.response)
#
        if self.__CloseConfigTelnetCLI(engine_idx) == False:
            self.logfile.close()            
            return False

        self.logfile.close()
        return True
#
    def SetCreateMirror(self, engine_idx, pid, sid, b_mode=""):
        dbg.printDBG1(file_name, "SetCreateMirror engine%s, primary=%s, secondary=%s, type=%s" % (engine_idx, pid, sid, b_mode))
#
# 13.	Only the master engine can create mirror drives. 
#       To identify which engine is the master, telnet to any engine within the cluster and type 7 
#       to go to engine CLI, and then type "engine" to display the engine attributes.
# 14.	On master engine, issue Telnet CLI "mirror create 0" to create a mirror structure that contains a single mirror member with drive ID #0 (a LUN from Storage A).
# 15.	On master engine, issue "mirror" to view the mirror structure information. (Note: the target number for the first mirror drive is specified on the left side as a 5 digit number).
# 16.	On master engine, issue "mirror create 1" to create the second single member mirror structure.
#
# Note: The next steps of the installation will be adding the second LUN (from Storage B) as second member to the one-member mirrors. If the wrong LUNs are mapped, the mirror pairs will not be configured as you expect. Assure that you verify the LUN IDs carefully before implementing these commands.
#
# 30.	On master engine, type "mirror add x y" where - 
#	x is the ID (for example, 33537) of the mirror structure (only single member at this point)  
#	y is the ID of the LUN you will be adding to mirror set x
#
# Note: The background data synchronization will be started automatically in 60 seconds after the mirror structure adds a new member (a LUN from Storage B). Data will be copied from Storage A to Storage B.
#
        if SIMMOD == 1:
            print engine_idx, pid, sid, b_mode
            return

        if self.__ReadyConfigTelnetCLI(engine_idx) == False:
            self.logfile.close()
            return False
#
# CLI>mirror create 2044
#
# Mirror drive 0x8201 (33281) created
#
# CLI>mirror add  T2047 no_rebuild
#
# T2047 is not a valid mirror
#
# CLI>mirror
#
# Mirror(hex)    state       Map         Capacity  Members
#  33281(0x8201) Operational  -        1073741824  2044 (OK ) 
# 
# '-' indicates not mapped to any initiator
#
# CLI>mirror create <pid>
# Mirror drive 0x8301(33537) created
#
        if (self.InputToExpect_cfg( "mirror create %s\r" % pid[1:], "CLI>")): return False
        for j in range(len(self.response)):
            if self.response[j].find("created") != -1: break
        info = self.response[j].split()
#
# CLI>mirror add 33537 <sid> no_rebuild
#
        if sid != '':
            if (self.InputToExpect_cfg( "mirror add %s %s %s\r" % (info[3][1:-1], sid[1:], b_mode), "CLI>")): return False
#
# update engine_info["Mirror"]
#
        if (self.InputToExpect_cfg( "mirror\r", "CLI>")): return False
        self.response[0] = 'CLI>mirror'     # to match the need of DecodeMirror function
#
        p = ParseEngineVPD.ParseEngineVPD()
        p.DecodeMirror(engine_idx, self.response)

        if self.__CloseConfigTelnetCLI(engine_idx) == False:
            self.logfile.close()            
            return False

        self.logfile.close()
        return True
#
    def SetAddMirror(self, engine_idx, mid, sid, b_mode=""):
        dbg.printDBG1(file_name, "SetAddMirror engine%s, mirror id=%s, secondary=%s" % (engine_idx, mid, sid))

        if SIMMOD == 1:
            print engine_idx, pid, sid, b_mode
            return

        if self.__ReadyConfigTelnetCLI(engine_idx) == False:
            self.logfile.close()
            return False
#
# CLI>mirror add 33537 <sid> no_rebuild
#
        if sid != '':
            if (self.InputToExpect_cfg( "mirror add %s %s %s\r" % (mid, sid[1:], b_mode), "CLI>")): return False
#
# update engine_info["Mirror"]
#
        if (self.InputToExpect_cfg( "mirror\r", "CLI>")): return False
        self.response[0] = 'CLI>mirror'     # to match the need of DecodeMirror function
#
        p = ParseEngineVPD.ParseEngineVPD()
        p.DecodeMirror(engine_idx, self.response)

        if self.__CloseConfigTelnetCLI(engine_idx) == False:
            self.logfile.close()            
            return False

        self.logfile.close()
        return True
        

    def SetBreakMirror(self, engine_idx, mid):
        dbg.printDBG1(file_name, "SetBreakMirror engine%s, mirror drive =%s" % (engine_idx, mid))

        if SIMMOD == 1:
            print engine_idx, mid
            return

        if self.__ReadyConfigTelnetCLI(engine_idx) == False:
            self.logfile.close()
            return False
#
# CLI>mirror split <mid>
# Mirror drive 0x8301(33537) splitted
#
        if (self.InputToExpect_cfg( "mirror split %s\r" % mid, "CLI>")): return False
#
# update engine_info["Mirror"]
#
        if (self.InputToExpect_cfg( "mirror\r", "CLI>")): return False
        self.response[0] = 'CLI>mirror'     # to match the need of DecodeMirror function
        
        engine_info[engine_idx]['Mirror'] = {}
        p = ParseEngineVPD.ParseEngineVPD()
        p.DecodeMirror(engine_idx, self.response)

        if self.__CloseConfigTelnetCLI(engine_idx) == False:
            self.logfile.close()            
            return False

        self.logfile.close()
        return True

    def SetPrepTrace(self, engine_idx, ss):
        dbg.printDBG3(file_name, "SetPrepTrace %s %s" % (engine_idx, ss))

        if self.__ReadyConfigTelnetCLI(engine_idx) == False:
            self.logfile.close()            
            return False

        if SIMMOD == 1: 
            self.logfile.close()            
            return True

        if (self.InputToExpect_cfg( "ftpprep " + ss + "\r", "CLI>")): return False
#        print self.response

        if self.__CloseConfigTelnetCLI(engine_idx) == False:
            self.logfile.close()            
            return False

        self.logfile.close()
        return True
        
    def __CloseConfigTelnetCLI(self, engine_idx):
        if SIMMOD == 1: return True
        if (self.InputToExpect( "exit\r", " 1 > ")): return False
        if (self.InputToExpect( "q", "(Y/N)")): return False
        if (self.InputToExpect( "y", "Bye!")): return False
        return True
        
    def __ReadyConfigTelnetCLI(self, engine_idx):
        engine_ip = cfg['Engine'+str(engine_idx)]['IP']
        f = self.__PreparedTraceFile('.tmp', './trace/', 'E%s-' % engine_idx, engine_ip, TMPCNT)
        
        try:
            self.tn = Telnet(engine_ip, timeout = 2)
        except:
            self.logfile.write( "....time-out, %s\n" % self.engine_ip)
            if SIMMOD == 1: return True
            return False

        self.logfile = open(f, 'a')
        self.logfile.write( self.tn.read_lazy())
        check_string = "password: "
        s = self.tn.read_until(check_string, timeout = 2)

        self.logfile.write( s)

        if s[-len(check_string):] != check_string:
            dbg.printDBG3(file_name, "telnet time-out, expecting %s, got %s" % (check_string, s[-len(check_string):]))
            return False

        if (self.InputToExpect( "%s\r" % PASSWORD, " 0 > ")): return False
        if (self.InputToExpect( "7", "CLI>")): return False
        return True
#
    def saveTrace(self, engine_idx, ss):
        self.tracepath = './trace/'
        self.engine_ip = cfg['Engine'+str(engine_idx)]['IP']

        if not os.path.exists(self.tracepath): os.makedirs(self.tracepath)
        
        if SIMMOD == 1:
            fname = "_test.txt"
            lname = ss + "_" + self.engine_ip + fname
            lf = open("./trace/" + lname, "wb")

            time_stamp = self.__TimeNow()
            lf.write( "Test Diagnostic File, created on" + time_stamp + "\n\n")
            lf.close()
            return
        
        userName = "adminftp"
        password = ''
        directory = "/mbtrace"

#        os.chdir("./trace")         #changes the active dir - this is where downloaded files will be saved to
        ftp = FTP(self.engine_ip)
        ftp.login(userName, password)
        ftp.cwd(directory)
        
        line = []
        ftp.retrlines("LIST", line.append)
        words = line[0].split(None, 8)
        fname = words[-1].lstrip()

        lname = ss + "_" + self.engine_ip + fname[8:]
        lf = open("./trace/" + lname, "wb")
        ftp.retrbinary('RETR %s' % fname, lf.write)
        lf.close()
#
# retrive cm.cfg, san.cfg, automap.cfg, and zip it into ./data/ directory
#
    def BackupConfiguration(self, engine_idx):
        path = './data/'
        engine_ip = cfg['Engine'+str(engine_idx)]['IP']

        if not os.path.exists(path): os.makedirs(path)
        
        userName = "adminftp"
        password = ''
        directory = "/bin_conf/"

        ftp = FTP(engine_ip)
        ftp.login(userName, password)
        ftp.cwd(directory)
        
        line = []
        ftp.retrlines("LIST", line.append)
        
        for i in range (len(line)):
            info = line[i].split()
            file_to_get = info[-1]

            file_to_save = path + file_to_get
        
            f = open(file_to_save, "wb")
            ftp.retrbinary('RETR %s' % file_to_get, f.write)
            f.close()

        included_extenstions = ['cfg'];
            
        if not os.path.exists(path): os.makedirs(path)
        zip_file_name = path + 'N%s%s' % (engine_info[engine_idx]['SerialNumber'], engine_info[engine_idx]['Firmware'][:-6]) \
                + datetime.datetime.now().strftime('T%Y%m%d%H%M%S.zip')
        zip_trace = zipfile.ZipFile(zip_file_name, 'w')

        file_names = [fn for fn in os.listdir(path) if any([fn.endswith(ext) for ext in included_extenstions])];

        for fn in file_names:
            zip_trace.write(path+fn, directory+fn)
            os.remove (path+fn)
#
# unzip the cm.cfg, san.cfg, automap.cfg under the directory ./data/bin_conf/ and restore to engine
#
    def RestoreConfiguration(self, engine_idx, zip_file):
        path = './data/'
        engine_ip = cfg['Engine'+str(engine_idx)]['IP']
        
        userName = "adminftp"
        password = ''
        directory = "/bin_conf/"
#
# unzip cfg file
#
        f = path+zip_file
        z = zipfile.ZipFile(f, 'r')
        z.extractall(path)
        z.close()
        
        bin_conf = os.listdir(path[:-1]+directory)
#
# ftp restore back to engine
#
        ftp = FTP(engine_ip)
        ftp.login(userName, password)
        ftp.cwd(directory)
        
        for file_to_put in sorted (bin_conf, reverse=True):
            print "put file", file_to_put
            f = open(path[:-1]+directory+file_to_put, "rb")
            ftp.storbinary('STOR %s' % file_to_put, f)
            f.close()

        ftp.close()
        shutil.rmtree(path[:-1]+directory[:-1])
        return True
#
    def downloadCode(self, engine_idx, code_name):
        self.engine_ip = cfg['Engine'+str(engine_idx)]['IP']
        userName = "adminftp"
        password = ''
        directory = "/mbflash"
        codepath = './mcode/'
        
        try:
            self.ftp = FTP(self.engine_ip, timeout = 2)
        except:
            dbg.printDBG2(file_name, "Can't connect to engine %s" % self.engine_ip)
            return TIMEOUT

        try:
            shutil.copyfile(codepath+code_name, 'fwimage')
        except:
            dbg.printDBG2(file_name, "Can't find file %s" % code_name)
            return TIMEOUT

        try:
            self.ftp.login(userName, password)
        except:
            dbg.printDBG2(file_name, "Can't login %s, will try vicomftp" % userName)
            return TIMEOUT

        self.ftp.cwd(directory)
        
        try:
            self.ftp.storbinary('STOR fwimage', open('fwimage', 'rb'))
        except:
            os.remove ("fwimage")
            self.ftp.close()
            return TIMEOUT
        self.ftp.close()
        os.remove ("fwimage")
        return GOOD
#
    def InputToExpect(self, put_string, check_string, file_ext = 'cmg'):
        self.tn.write(put_string)
        s = self.tn.read_until(check_string, timeout = 2)
        self.logfile.write(s)
        
        self.response = s.splitlines()
        length = len(self.response)
        
        if self.response == [] and check_string == '':
            return GOOD      # this is for warm reboot case
        
        if s[-len(check_string):] != check_string:
            dbg.printDBG2(file_name, "telnet time-out, expecting %s, got %s" % (check_string, s[-len(check_string):]))
            if s[-14:] == "Proceed? (Y/N)":     # Another session owns the CLI.  Proceed? (Y/N)
                if CLI_CUT == 1:
                    # proceed after sleep for one second
                    dbg.printDBG3 (file_name, "Telnet CLI conflict, sleep for 2 sec, then cut in")
#                    print "
                    if file_ext == 'vpd': time.sleep(5)  # Telnet conflict, wait longer for vpd (5 sec), then cut in"
                    else: time.sleep(2)                 #   otherwise, cut in in 2 seconds
                    self.tn.write("Y")
                    s = self.tn.read_until(check_string, timeout = 2)
                    self.logfile.write(s)
                else:
                    return TIMEOUT                
            else:
                return TIMEOUT                

        elif self.response[length-1].find("DISCARDED <<<") != -1:       # >>> CHARACTERS DISCARDED <<<
            self.tn.write("\r")
            s = self.tn.read_until(check_string, timeout = 2)
            self.logfile.write(s)
        return GOOD
    #
    def InputToExpect_cfg(self, put_string, check_string):   # if encounter Telnet conflict, cut in after 1 second delay...
        if SIMMOD == 1:
            print "CLI>", put_string
            if put_string[:13] == "mirror create":
                self.response = ["Mirror drive 0x8301(33537) created", "", "CLI>"]
            elif put_string[:10] == "mirror add":
                self.response = ["Mirror drive 0x8301(33537) added", "", "CLI>"]
            elif put_string[:6] == "mirror":
                self.response = ["CLI>mirror", "", "Mirror(hex) state Map Capacity Members", 
                                "33537(0x8301) Operational 0 3906249216 0 (OK ) 3 (OK )", "", 
                                "33538(0x8302) Operational 1 3906249216 1 (OK ) 4 (OK )", "", 
                                "33281(0x8201) Operational 2 3906249216 11 (RBL) 15 (OK )", "", 
                                "CLI>"]
            return GOOD

        self.tn.write(put_string)        
        s = self.tn.read_until(check_string, timeout = 2)
        self.logfile.write(s)
        
        self.response = s.splitlines()
                
        if s[-len(check_string):] != check_string:
            dbg.printDBG2(file_name, "telnet time-out, expecting %s, got %s" % (check_string, s[-len(check_string):]))
            if s[-14:] == "Proceed? (Y/N)":                                 # Another session owns the CLI.  Proceed? (Y/N)
                # proceed after sleep for one second
                dbg.printDBG3 (file_name, "Telnet CLI conflict, sleep for 2 sec, then cut in")
#                print "Telnet conflict, sleep for 2 sec, then cut in"
                time.sleep(2)
                self.tn.write("Y")
                s = self.tn.read_until(check_string, timeout = 2)
                self.logfile.write(s)

            else:
                return TIMEOUT
        return GOOD
#
    def DetectEngine(self, i):
        if SIMMOD:          # test mode
            f = self.FindFile(i)
            if f == None or f == False: return False
            
            myfile = open(f, 'r')
            lines = []
            lines = myfile.readlines()
            myfile.close()
#            print "SIM mode, read from file", f, "lengine =", len(lines)
            
            if len(lines) >= 2:
                dbg.printDBG2(file_name, "Engine%s is ready from VPD file" % i)
                return True
            else:
                dbg.printDBG2(file_name, "Engine%s is NOT ready from VPD file" % i)
                return False
        else:               # real mode
            if ControlTCP.PingEngine(cfg['Engine'+str(i)]['IP']) == True:
                dbg.printDBG2(file_name, "Engine%s is ready" % i)
                return True
            else:
                engine_info[i]['Status'] = 'offline'
                engine_info[i]['Master'] = ''
                dbg.printDBG2(file_name, "Engine%s is NOT ready" % i)
                return False
#
# Update engine_info and registered database from selected file (.vpd or . cmg)
#
# UpdateInfo(i, file='vpd') ; xxxGetEngineVPD(i)
#
# 1) Get info from engine to file
#       Engine2File(i, file_name = 'vpd') ; xxxgetVPDfromEngine - telnet to engine and get the info from engine
#                                   vpd (invoked every backgroup tasks, default is 2 seconds)
#                                   cmg (invoked after configuration change)
#                                   exp (invoked when asked for explore, it may take a long time)
#
# 2) Get info from file to database
#       File2DB(i, file="vpd") ; find saved file and convert to DB
#           f = FindFile(i, file='vpd') ; __getVPDfile, __getCMGfile, 
#           Parsefile(i, f) ; updateEngineInfo(i, f), updateCmgInfo(i, f)
#
# Display info from memory to panel
#       DB2Panel_???() ;
#           __DB2Panel_MST(i) ; __DB2Panel_MST(i)
#           __DB2Panel_PST(i) ; __DB2Panel_PST(i)
#           __DB2Panel_SST(i) ; __DB2Panel_SST(i)
#
    def UpdateInfo(self, i, file_ext = "vpd", para1 = ''):
        dbg.printDBG2 (file_name, "UpdateInfo called for Engine%s, file_ext= %s, para1=%s" % (i, file_ext, para1))
        port = para1
        
        if SIMMOD == 1:
            if self.File2DB(i, file_ext, para1) != True:
                dbg.printDBG3(file_name, "Engine%s can not update %s" % (i, file_ext))
                return False
            return True
            
        if self.Engine2File(i, file_ext) != True:
            dbg.printDBG3(file_name, "Engine%s can not update %s" % (i, file_ext))
            return False

        if self.File2DB(i, file_ext, para1) != True:
            dbg.printDBG3(file_name, "Engine%s can not update %s" % (i, file_ext))
            return False
        return True
            
    def File2DB(self, i, file_ext = 'vpd', port = ''):
        f = self.FindFile(i, file_ext, port)

        if self.__InAlertHalt(f) == True: return False
#        if current_engine[i] == ('off', 'on'):
#            self.getEXPfromEngine(i)    # update EXP file too (only when engine from off2on)

        p = ParseEngineVPD.ParseEngineVPD()
        if p.ParseFile(i, f, file_ext, port) != True: return False
        
        dbg.printDBG3(file_name, "Engine'%s %s updated" % (i, file_ext))
        return True
#
    def GetEngineLicense(self, eng_number):
        dbg.printDBG2 (file_name, "GetEngineLicense called for Engine%s" % eng_number)
        f = self.FindFile(eng_number)
        vpdfile = open(f, 'r')
        lines = vpdfile.readlines()
        vpdfile.close()
        dbg.printDBG4(file_name, "get %s lines from file %s" % (len(lines), f))
#
        for start_idx in range(len(lines)):
            if lines[start_idx].find("CLI>license status") != -1: break
        start_idx = start_idx + 1

        if start_idx == len(lines):
            dbg.printDBG2(file_name, "!!!! initiator status not found from Engine%s" % eng_number)
            return False
        #
        else:
            for i in range (start_idx, len(lines)):
                if lines[i].find("Installed") == -1: continue
                start_idx = i + 1
                break
                
            for end_idx in range(start_idx, len(lines)):   # find the last entry
                if lines[end_idx].find('CLI>') != -1: break  # found next CLI command, reached the end of this session
        #
        lines = lines[start_idx:end_idx]
        
        if (debug_level >= 4):
            dbg.printDBG4(file_name, "-- print Engine%s license info" % eng_number)
            dbg.printDBG4(file_name, "---- %s" % lines)

        return lines
#
# CLI>explore b1
#
# FC port WWPN WWNN Port type
# 0x010825 5000-612024-534000 5000-612024-534400 Target
# LUNS:
# 0000 2929.6 GB dg0ld0
# 0001 1953.1 GB dg0ld1
# 0x010900 2603-000155-600145 2500-000155-600145 Target
# LUNS:
# 0000 1862.6 GB 22eb000155a069b2
# 0001 1862.6 GB 2299000155dae234
# 0x010a00 2602-000155-600145 2500-000155-600145 Target
# LUNS:
# 0000 1862.6 GB 22eb000155a069b2
# 0001 1862.6 GB 2299000155dae234
# 3 ports reported
# Explore of port B1 complete!
#
# CLI>explore a1
#
# FC port WWPN WWNN Port type
# 0x020600 5006-022300-ad0c2b 5006-022000-ad0c2b Initiator
# 1 ports reported
# Explore of port A1 complete!
#
# CLI>explore A1
#
# Error -1: link down     
# Explore of port A1 complete!
#
# CLI>
#
    def GetExploreInfo(self, eng_number, port):
        dbg.printDBG2 (file_name, "GetExploreInfo called for Engine%s, port=%s" % (eng_number, port))
        f = self.FindFile(eng_number, 'exp', port)
        if f == False: return False
        expfile = open(f, 'r')
        lines = expfile.readlines()
        expfile.close()
        dbg.printDBG4(file_name, "get %s lines from file %s" % (len(lines), f))
#
        for start_idx in range(len(lines)):
            if lines[start_idx].find("CLI>explore") != -1: break
        start_idx = start_idx + 1

        if start_idx == len(lines):
            dbg.printDBG2(file_name, "!!!! explore status not found from Engine%s" % eng_number)
            return False
        #
        else:
            for i in range (start_idx, len(lines)):
                if lines[i].find("FC port") == -1 and lines[i].find("Error") == -1: continue
                start_idx = i + 1
                break
                
            for end_idx in range(start_idx, len(lines)):   # find the last entry
                if lines[end_idx].startswith('Explore of port %s complete!' % port): break
        
        lines = lines[start_idx:end_idx-1]

        exp_out = []
        template_port = "{0:4} {1:8} {2:16}"
        template_lun = "{0:8} {1:>8} {2:8}"

        if lines == []:
            exp_out.append(template_port.format("Link Down", "", ""))
            return exp_out

        exp_out.append(template_port.format("Type", "FCport", "WWPN"))        
        for i in range(len(lines)):
            info = lines[i].split()
            if info == []: continue     # skip empty lines
                
            if info[0][:2] == "0x":
                if info[3] == "Initiator":
                    exp_out.append(template_port.format(">Ini",info[0],info[1]))
                elif info[3] == 'Drive':
                    exp_out.append(template_port.format(">Tgt",info[0],info[1]))
                elif info[3] == "Vicom" or info[3] == "Loxoll":
                    exp_out.append(template_port.format(">Eng",info[0],info[1]))
                else:
                    exp_out.append(template_port.format(">???",info[0],info[1]))

            elif info[0][:1] == "0" and info[0][:2] != "0x":
                if info[1] == "Error":
                    exp_out.append(template_lun.format("..LUN"+info[0][1:],"Special LUN",""))
                else:
                    exp_out.append(template_lun.format("..LUN"+info[0][1:],info[1]+info[2],"SN:.."+info[3][-8:]))
        
        if (debug_level >= 4):
            dbg.printDBG4(file_name, "-- print Engine%s port %s explore info" % (eng_number, port))
            dbg.printDBG4(file_name, "---- %s" % lines)
            
        return exp_out
#
    def GetConmgrDriveInfo(self, eng_number):
        dbg.printDBG2 (file_name, "GetConmgrInfo called for Engine%s" % eng_number)
        f = self.FindFile(eng_number, 'cmg')
        if f == False: return False
        cmgfile = open(f, 'r')
        lines = cmgfile.readlines()
        cmgfile.close()
        dbg.printDBG4(file_name, "get %s lines from file %s" % (len(lines), f))
#
        for start_idx in range(len(lines)):
            if lines[start_idx].find("CLI>conmgr drive status") != -1: break
        start_idx = start_idx + 1

        if start_idx == len(lines):
            dbg.printDBG2(file_name, "!!!! explore status not found from Engine%s" % eng_number)
            return False
        #
        else:
            for i in range (start_idx, len(lines)):
                if lines[i].find('Drive') == -1: continue
                start_idx = i + 1
                break
                
            for i in range (start_idx, len(lines)):
                if lines[i].startswith("====="): continue
                start_idx = i + 1
                break
                    
            for end_idx in range(start_idx, len(lines)):   # find the last entry
                if lines[end_idx].find("CLI>") != -1: break
        
        return lines[start_idx:end_idx-1]
#
    def GetConmgrEngineInfo(self, eng_number):
        dbg.printDBG2 (file_name, "GetConmgrInfo called for Engine%s" % eng_number)
        f = self.FindFile(eng_number, 'cmg')
        if f == False: return False
        cmgfile = open(f, 'r')
        lines = cmgfile.readlines()
        cmgfile.close()
        dbg.printDBG4(file_name, "get %s lines from file %s" % (len(lines), f))
#
# get "CLI>engine"s Master Engine info
#
# CLI>engine
#
#    Engine  Status  Serial-Nr  IP-Addr           Firmware
#    1  (M)  Online     ... further info not available
#    2       Online     ... further info not available
#    3       Online     ... further info not available
# >> 4       Online  11340740   172. 16. 90. 61   LXLLHAAP 15.9.3.10 # 1
#
        temp_save = {}

        for start_idx in range(len(lines)):
            if lines[start_idx].find("CLI>engine") != -1: break
        start_idx = start_idx + 1

        if start_idx == len(lines):
            dbg.printDBG2(file_name, "!!!! CLI>engine not found from Engine%s" % eng_number)
            return False
        #
        else:
            for i in range (start_idx, len(lines)):
                if lines[i].find('Engine') == -1: continue
                start_idx = i + 1
                break
            for end_idx in range(start_idx, len(lines)):   # find the last entry
                if lines[end_idx].find("CLI>") != -1: break
                
            for i in range (start_idx, end_idx):
                if lines[i].find("(M)") == -1: continue
                info = lines[i].split()
                temp_save[info[0]] = '(M)'
#
# get "conmgr engine status"
#
        for start_idx in range(len(lines)):
            if lines[start_idx].find("CLI>conmgr engine status") != -1: break
        start_idx = start_idx + 1

        if start_idx == len(lines):
            dbg.printDBG2(file_name, "!!!! explore status not found from Engine%s" % eng_number)
            return False
        #
        else:
            for i in range (start_idx, len(lines)):
                if lines[i].find('Engine') == -1: continue
                start_idx = i + 1
                break
                
            for i in range (start_idx, len(lines)):
                if lines[i].startswith("====="): continue
                start_idx = i + 1
                break
                
            for end_idx in range(start_idx, len(lines)):   # find the last entry
                if lines[end_idx].find("CLI>") != -1: break
                
            for k in range(start_idx, end_idx):
                info = lines[k].split()
                if info == []: continue
                
                if info[0] in temp_save:
                    lines[k] = lines[k]+" (M)"      # merge in the Master engine info
                else:
                    lines[k] = lines[k]+" -"        # merge in the Master engine info
                    
        return lines[start_idx:end_idx-1]
#
    def GetConmgrInitiatorInfo(self, eng_number):
        dbg.printDBG2 (file_name, "GetConmgrInfo called for Engine%s" % eng_number)
        f = self.FindFile(eng_number, 'cmg')
        if f == False: return False
        cmgfile = open(f, 'r')
        lines = cmgfile.readlines()
        cmgfile.close()
        dbg.printDBG4(file_name, "get %s lines from file %s" % (len(lines), f))
#
        for start_idx in range(len(lines)):
            if lines[start_idx].find("CLI>conmgr initiator status") != -1: break
        start_idx = start_idx + 1

        if start_idx == len(lines):
            dbg.printDBG2(file_name, "!!!! explore status not found from Engine%s" % eng_number)
            return False
        #
        else:
            for i in range (start_idx, len(lines)):
                if lines[i].find('Initiator') == -1: continue
                start_idx = i + 1
                break

            for i in range (start_idx, len(lines)):
                if lines[i].startswith("====="): continue
                start_idx = i + 1
                break
                
            for end_idx in range(start_idx, len(lines)):   # find the last entry
                if lines[end_idx].find("CLI>") != -1: break
        
        return lines[start_idx:end_idx-1]

    def FindFile(self, engine_idx, file_ext = 'vpd', port = 'A1'):

        tracepath = './trace/'
        if not os.path.exists(tracepath):
            dbg.printDBG1 (file_name, 'no tracepath error')
        
        if file_ext == 'exp': prefix = 'E%s%s-' % (engine_idx, port)
        else: prefix = 'E%s-' % engine_idx
        
        # count the .vpd files
        file_count = 0
        for file in glob.glob(os.path.join(tracepath, prefix+'*.%s' % file_ext)): file_count += 1
        if file_count == 0: return False

        # find the newest file
        newest_file, newest_time = None, None
        for dirpath, dirs, files in os.walk(tracepath):
            for filename in files:
                file_path = os.path.join(dirpath, filename)
                file_time = os.stat(file_path).st_mtime
                if file_path.endswith('.'+file_ext) and file_path.startswith (tracepath + prefix) and \
                    (file_time>newest_time or newest_time is None):
                    newest_file, newest_time = file_path, file_time
        return newest_file

    def xx__getEXPfile(self, engine_idx, port):

        tracepath = './trace/'
        if not os.path.exists(tracepath):
            dbg.printDBG1 (file_name, 'no tracepath error')
        prefix = 'E%s%s-' % (engine_idx, port)
        
        # count the .exp files
        exp_file_count = 0
        for file in glob.glob(os.path.join(tracepath, prefix+'*.exp')): exp_file_count += 1

        if exp_file_count == 0: return False
        
        # find the newest file
        newest_file, newest_time = None, None
        for dirpath, dirs, files in os.walk(tracepath):
            for filename in files:
                file_path = os.path.join(dirpath, filename)
                file_time = os.stat(file_path).st_mtime
                if file_path.endswith(".exp") and file_path.startswith (tracepath + prefix) and \
                    (file_time>newest_time or newest_time is None):
                    newest_file, newest_time = file_path, file_time
        return newest_file
#
    def xxgetCMGfile(self, engine_idx):

        tracepath = './trace/'
        if not os.path.exists(tracepath):
            dbg.printDBG1 (file_name, 'no tracepath error')
        prefix = 'E%s-' % engine_idx
        
        # count the .cmg files
        cmg_file_count = 0
        for file in glob.glob(os.path.join(tracepath, prefix+'*.cmg')): cmg_file_count += 1

        if cmg_file_count == 0: return False
        
        # find the newest file
        newest_file, newest_time = None, None
        for dirpath, dirs, files in os.walk(tracepath):
            for filename in files:
                file_path = os.path.join(dirpath, filename)
                file_time = os.stat(file_path).st_mtime
                if file_path.endswith(".cmg") and file_path.startswith (tracepath + prefix) and \
                    (file_time>newest_time or newest_time is None):
                    newest_file, newest_time = file_path, file_time
        return newest_file

#
    def __InAlertHalt(self, vpdfile):
        if vpdfile == False: return True    # assume it's in AH
        vpdfile = open(vpdfile, 'r')
        lines = vpdfile.readlines()
        vpdfile.close()
        if (len(lines) > 21) and (lines[21].find("AH_CLI") == -1):
#            print "not in Alert Halt"
            return False
        else:
#            print "Yas, in Alert Halt"
            return True

    def __TimeNow(self):
        return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

if __name__ == '__main__':
    import zipfile
    import datetime
    
    time_now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-7]
    time_now = time_now.replace(' ', '-')
    time_now = time_now.replace(':', '-')
#
# Get the Company Name for the release name.zip
# 
    myfile = open('DisplayDashboard.py', 'r')
    lines = myfile.readlines()
    myfile.close()    
    for idx in range(len(lines)):
        if lines[idx].startswith('COMPANY'): break
    if idx == len(lines):
        company = 'Loxoll'
    else:
        info = lines[idx].split()
        company = info[2][1:-1]
#    
    zip = zipfile.ZipFile("%sTRC-%s.zip" % (company, time_now), 'w')

    t = xEngine()

    for i in range(engine_number):
        if t.SetPrepTrace( i, "trace") == True:
            t.saveTrace( i, "trace")
            
            if t.SetPrepTrace( i, "coredump primary all") == True:
                t.saveTrace( i, "primary")

            if t.SetPrepTrace( i, "coredump secondary all") == True:
                t.saveTrace( i, "secondary")
                print "complete...%s" % cfg['Engine'+str(i)]['IP']
        
    for root, dirs, files in os.walk("./trace"):
        for fn in files:
            if fn[-4:] == '.txt':
                target_file = os.path.join(root, fn)
                zip.write(target_file)

    os.system("rm ./trace/*.txt")
    sys.exit()
