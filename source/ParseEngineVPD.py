"""
ParseEngineVPD.py

Copyright (c) 2015-2017 __Loxoll__. All rights reserved.
"""

#
#  cfg = ParseINIfile('Config.ini')
#  ip = cfg['Engine1']['IP']
#
import os

file_name = os.path.basename(__file__)

class ParseEngineVPD(object):
    def __init__(self):
        pass
        
    def initEngineInfo(self, i):
        dbg.printDBG1(file_name, "Initialize Engine Info for Engine%s" % i)
        engine_info[i]['Firmware'] = ''
        engine_info[i]['Revision'] = ''
        engine_info[i]['UniqueID'] = ''
        engine_info[i]['SerialNumber'] = ''
        engine_info[i]['PCBnumber'] = ''
        engine_info[i]['IPaddress'] = ''
        engine_info[i]['Uptime'] = ''
        engine_info[i]['Alert'] = ''
        engine_info[i]['EngineTime'] = ''
        engine_info[i]['Status'] = 'offline'
        engine_info[i]['Master'] = ''
        engine_info[i]['This Engine'] = 'U'
        engine_info[i]['ClusterSN'] = {}
        engine_info[i]['AutoMap'] = ''
        engine_info[i]['Mirror'] = {}
        engine_info[i]['Rebuild'] = {}
        engine_info[i]['Engine'] = {}
        engine_info[i]['Drive'] = {}
        engine_info[i]['DrivesCap'] = {}
        engine_info[i]['Initiator'] = {}
        engine_info[i]['Group'] = {}
        engine_info[i]['Ports'] = {}
        engine_info[i]['BPT'] = {}
        engine_info[i]['Update'] = {}
        engine_info[i]['Selected'] = {}
        engine_info[i]['License'] = []
        engine_info[i]['Special'] = {}
        engine_info[i]['Application'] = {}
        engine_info[i]['Explore'] = {}
        engine_info[i]['DriveSN'] = {}
        engine_info[i]['Registered'] = {}
        engine_info[i]['Analysis'] = {}        
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
#       DB2Panel_???()
#
    def ParseFile(self, i, f, file_ext = 'vpd', port = ''):
        dbg.printDBG2(file_name, "Parse File for Engine%s, file_ext= %s, port= %s" % (i, file_ext, port))

        self.__getLines(f)

        if SIMMOD == 1:
            if self.lines[0][:6] != 'Telnet':
                return False
        
        if file_ext == 'vpd' or file_ext == 'cmg':
            self.__decodeVPD(i)
            self.DecodeMirror(i, self.lines)
            self.__decodeEngine(i)
            self.__decodeDrive(i)
            self.__decodeDriveCap(i)
            self.__decodeInitiator(i)
            self.__decodePorts(i)
            self.__decodeBPT(i)
            self.__decodeMaster(i)
            self.__decodeGroup(i)
            self.__decodeRebuild(i)
#
        if file_ext == 'cmg':
            self.DecodeLicense(i, self.lines)
            self.DecodeSpecialMode(i, self.lines)
            self.DecodeDriveSerialNumber(i, self.lines)
#
        if file_ext == 'exp':
            self.__decodeExplore(i, port)
#
# If fake drive on, add the fake drive to standard drive director 
#
#   {"Mirror": {"33281": ["Operational", "-", "1073741824", "T2045", "OK", "T2046", "OK", "-", "-", "-", "-"]}}
#####   {"Initiator": {"I0001": ["2", "A2", "2100-0024ff-5d272b", "A"]}}
#   {"Initiator": {"I0001": {"2100-0024ff-5d272b": ["2", "A2", , "A"]}}}
#   {"Engine": {"E0001": {"2300-006022-ad0b60": ["B1", "A"]}}} 
#   {'Drive': { "T0000": { "5002-2c1001-33d003": (A1, 0001, A, "sn")}}}
#   {"DrivesCap": { "T2044": ["", "1073741824", "0", "Operational"]}} 
#   {"DrivesSN": { "T2044": ["A-A", "serial number"]}} 
#   {"Group": {"Drive": {"0": ["33537", "33538"],
#                        "3": ["33538", "33539"]},
#              "HBA": {"21": ["5006-022100-ad0c2b"]},
#              "Map": {"2": {"Has": ["33537", "33538"],
#                            "Use": ["5006-022300-ad0c2b"]}, 
#                      "3": {"Has": ["33537", "33538"],
#                            "Use": ["5006-022100-ad0c2b"]}, 
#                     "99": {"Has": ["33025", "33026", "33537", "33538"], 
#                            "Use": []}}}}
#   {'Explore': { "A1": { 'Drive': { "5002-2c1001-33d003": { '0001': ('2929.6GB', 'dg0ld0', '0x010825', 'T0001')}}
#                                                          { '0006': ('2929.6GB', 'dg0ld0', '0x010825', '')}}
#                       { 'Initiator': { '5006-022300-ad0c2b': ('0x020600', 'I0001')}}}}}
#   {"Registered": { "Drive": { "5742-b0f000-4e4012": ["T0000", "T0001", "T0002"], 
#                               "5742-b0f000-4e4022": ["T0000", "T0001", "T0002"]},
#                     "Engine" : {},
#                     "Initiator" : {}}}
#   {"Rebuild": {"33281": ["0", "1", "0x0000", "3.4%", "10", "100", "quick", "0:01:32", "0:43:33"]}}
# 
        for tid in engine_info[i]['DrivesCap']:
            if tid == 'T2044' or tid == 'T2045' or tid == 'T2046' or tid == 'T2047':
                engine_info[i]['Drive'][tid] = {"FakeDrive-E%s" % i: ["NA", tid[1:], "A", ""]}
#
# update registered info
#
        for mode in ['Initiator', 'Drive', 'Engine']:             
            engine_info[i]['Registered'][mode] = {}
            for check_id in sorted( engine_info[i][mode]):
                for wwpn in sorted( engine_info[i][mode][check_id]):
                    if wwpn not in engine_info[i]['Registered'][mode]: engine_info[i]['Registered'][mode][wwpn] = []
                    engine_info[i]['Registered'][mode][wwpn].append(check_id)
#
# Done, put out debug info
#
        if (debug_level >= 4):
            dbg.printDBG4(file_name, "-- print Engine%s info table key_id" % i)
            for key_id in engine_info[i]:
                dbg.printDBG4(file_name, "---- id=%s, Data=%s" % (key_id, engine_info[i][key_id]))
        return True
    def __getLines(self, f):
        vpdfile = open(f, 'r')
        self.lines = vpdfile.readlines()
        self.f_length = len(self.lines)
        vpdfile.close()
        dbg.printDBG4(file_name, "get %s lines from file %s" % (self.f_length, f))
#
# find next "string", from line A to line B, return the line number if found, otherwise, return -1 
#
    def __FindNext(self, string, start_ptr, end_ptr):
        for i in range (start_ptr, end_ptr):
            if self.lines[i].find(string) == -1: continue
            return i
        return -1
#
#        CLI>vpd
#
#        ****** Storage Mirroring Engine VPD ******
#
#        Product Type : FCE4400
#
#        Apple Release
#          128 HBA support
#          All active/passive drives are assumed to be FastT compatible.
#        Firmware V15.1.10	VCMSVMIR Official Release
#        Revision Data : Vicom(release), Sep 17 2012 16:56:07
#        (C) 1995-2012 Vicom Systems, Inc. All Rights Reserved.
#        Redboot(tm) version: 0.2.0.6
#
#        Unique ID          : 00000060-220929D4
#        Unit Serial Number : 00600532
#        PCB Number         : 00600532
#        MAC address        : 0.60.22.9.29.D4
#        IP address         : 192.168.201.40
#
#        Uptime             : 190d 22:19:24
#
#        Alert: None
#        Wednesday, 11/20/2013, 09:21:27
#
#        Port  Node Name           Port Name
#        A1    2000-006022-0929d4  2100-006022-0929d4
#        A2    2000-006022-0929d4  2200-006022-0929d4
#        B1    2000-006022-0929d4  2300-006022-0929d4
#        B2    2000-006022-0929d4  2400-006022-0929d4
#
    def __decodeVPD(self, eng_number):

        info = self.lines[0].split()

        if len(info) == 8: print info

        engine_info[eng_number]['Update']['date'] = info[7]
        engine_info[eng_number]['Update']['time'] = info[8]

        for start_idx in range(self.f_length):   # find the last entry
            if self.lines[start_idx].find("CLI>vpd") != -1: break  # found next CLI command, reached the end of this session
        start_idx = start_idx + 1

        if start_idx == self.f_length:
            dbg.printDBG2(file_name, "!!!! vpd not found from Engine%s" % eng_number)
            return False

        else:
            engine_info[eng_number]['Status'] = 'ONLINE'
            engine_info[eng_number]['Master'] = ' '

            for i in range (start_idx, self.f_length):
                if not self.lines[i].startswith('Firmware'): continue
                info = self.lines[i].split()
                engine_info[eng_number]['Firmware'] = info[1] + " " + info[2]
                start_idx = i + 1
                break

            for i in range (start_idx, self.f_length):
                if not self.lines[i].startswith('Revision'): continue
                info = self.lines[i].split()
                engine_info[eng_number]['Revision'] = info[-4] + "-" + info[-3] + "-" + info[-2] + ", " + info[-1]
                start_idx = i + 1
                break

            for i in range (start_idx, self.f_length):
                if not self.lines[i].startswith('Unique ID'): continue
                info = self.lines[i].split()
                engine_info[eng_number]['UniqueID'] = info[-1]
                start_idx = i + 1
                break

            for i in range (start_idx, self.f_length):
                if not self.lines[i].startswith('Unit Serial Number'): continue
                info = self.lines[i].split()
                engine_info[eng_number]['SerialNumber'] = info[-1]
                start_idx = i + 1
                break

            for i in range (start_idx, self.f_length):
                if not self.lines[i].startswith('PCB Number'): continue
                info = self.lines[i].split()
                engine_info[eng_number]['PCBnumber'] = info[-1]
                start_idx = i + 1
                break

            for i in range (start_idx, self.f_length):
                if not self.lines[i].startswith('IP address'): continue
                info = self.lines[i].split()
                engine_info[eng_number]['IPaddress'] = info[-1]
                start_idx = i + 1
                break

            for i in range (start_idx, self.f_length):
                if not self.lines[i].startswith('Uptime'): continue
                info = self.lines[i].split()
                engine_info[eng_number]['Uptime'] = info[-2].replace(':', '') +" "+ info[-1]
                start_idx = i + 1
                break

            for i in range (start_idx, self.f_length):
                if not self.lines[i].startswith('Alert'): continue     # look for Firmware version
                info = self.lines[i].split()
                if info[1] == "None":
                    engine_info[eng_number]['Alert'] = info[1]
                else:
                    engine_info[eng_number]['Alert'] = "AH"+info[1]                    
                start_idx = i + 1
                break

            date_list = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            for i in range (start_idx, self.f_length):
                info = self.lines[i].split()
                if info == [] or not info[0][:-1] in date_list: continue     # look for date
                engine_info[eng_number]["EngineTime"] = info[0][:-1]+info[1][:-1]+info[2]
                break
#
        if (debug_level >= 4):
            dbg.printDBG4(file_name, "-- decode VPD for Engine%s uptime= %s" % (eng_number, engine_info[eng_number]['Uptime']))
        return True
#
    def DecodeSpecialMode(self, eng_number, lines):
#
# ** Storage Emulation Options **
# Current inquiry option is <SDD>
# Entry inquiry option was <SDD>
# Storage emulation options:
#    D = Loxoll (default)
#    S = SDD
#    ? = show settings as changed
#    <Esc> = restore entry settings (discard changes)
#    <Enter> = accept and exit
#
        start_idx = 0
        for start_idx in range(len(lines)):   
            if lines[start_idx].find("Current inquiry option is") != -1: break  # found next CLI command, reached the end of this session
        start_idx = start_idx + 1

        if start_idx == len(lines):
            dbg.printDBG2(file_name, "!!!! Storage Emulation status not found from Engine%s" % eng_number)
            return False

        else:
            info = self.lines[start_idx-1].split()
            engine_info[eng_number]['Special']['Storage Emulation'] = info[4][1:-1]
#
# CLI>vaai
#
# VAAI support is currently enabled
#
        start_idx = 0
        for start_idx in range(len(lines)):   # find the last entry
            if lines[start_idx].find("CLI>vaai") != -1: break  # found next CLI command, reached the end of this session
        start_idx = start_idx + 1
            
        if start_idx == len(lines):
            dbg.printDBG2(file_name, "!!!! VAAI Status not found from Engine%s" % eng_number)
            return False

        else:
            info = self.lines[start_idx+1].split()
            if info[4] == 'enabled':
                engine_info[eng_number]['Special']['VAAI'] = 'ON'
            else:
                engine_info[eng_number]['Special']['VAAI'] = 'OFF'
#
# CLI>aca
#
# ACA support is currently enabled
#
        start_idx = 0
        for start_idx in range(len(lines)):   # find the last entry
            if lines[start_idx].find("CLI>aca") != -1: break  # found next CLI command, reached the end of this session
        start_idx = start_idx + 1
            
        if start_idx == len(lines):
            dbg.printDBG2(file_name, "!!!! ACA Status not found from Engine%s" % eng_number)
            return False

        else:
            info = self.lines[start_idx+1].split()
            if info[4] == 'enabled':
                engine_info[eng_number]['Special']['ACA'] = 'ON'
            else:
                engine_info[eng_number]['Special']['ACA'] = 'OFF'
#
# CLI>video
#
# Video Mode On
#
        start_idx = 0
        for start_idx in range(len(lines)):   # find the last entry
            if lines[start_idx].find("CLI>video") != -1: break  # found next CLI command, reached the end of this session
        start_idx = start_idx + 1
            
        if start_idx == len(lines):
            dbg.printDBG2(file_name, "!!!! Video Status not found from Engine%s" % eng_number)
            return False

        else:
            info = self.lines[start_idx+1].split()
            if info[2] == 'On':
                engine_info[eng_number]['Special']['Video Mode'] = 'ON'
            else:
                engine_info[eng_number]['Special']['Video Mode'] = 'OFF'
#
# CLI>timeout
#
# Command timeouts are currently disabled
#   ("timeout off")
# Last mirror members are treated the same as other drives
#
        start_idx = 0
        for start_idx in range(len(lines)):   # find the last entry
            if lines[start_idx].find("CLI>timeout") != -1: break  # found next CLI command, reached the end of this session
        start_idx = start_idx + 1
            
        if start_idx == len(lines):
            dbg.printDBG2(file_name, "!!!! Storage Command Timeout Status not found from Engine%s" % eng_number)
            return False

        else:
            info = self.lines[start_idx+1].split()
            if info[4] == 'disabled':
                engine_info[eng_number]['Special']['Storage Cmd Timeout'] = 'OFF'
            else:
                engine_info[eng_number]['Special']['Storage Cmd Timeout'] = 'ON'
#
# CLI>site
#
# Site isolation protection is currently disabled
#
        start_idx = 0
        for start_idx in range(len(lines)):   # find the last entry
            if lines[start_idx].find("CLI>site") != -1: break  # found next CLI command, reached the end of this session
        start_idx = start_idx + 1
            
        if start_idx == len(lines):
            dbg.printDBG2(file_name, "!!!! Site Isolation Status not found from Engine%s" % eng_number)
            return False

        else:
            info = self.lines[start_idx+1].split()
            if info[5] == 'disabled':
                engine_info[eng_number]['Special']['Site Isolation'] = 'OFF'
            else:
                engine_info[eng_number]['Special']['Site Isolation'] = 'ON'
#
# CLI>quorum
#
# Site isolation quorum client is currently disabled
#
        start_idx = 0
        for start_idx in range(len(lines)):   # find the last entry
            if lines[start_idx].find("CLI>quorum") != -1: break  # found next CLI command, reached the end of this session
        start_idx = start_idx + 1
            
        if start_idx == len(lines):
            dbg.printDBG2(file_name, "!!!! Quorum Service Status not found from Engine%s" % eng_number)
            return False

        else:
            info = self.lines[start_idx+1].split()
            if info[6] == 'disabled':
                engine_info[eng_number]['Special']['Quorum Service'] = 'OFF'
            else:
                engine_info[eng_number]['Special']['Quorum Service'] = 'ON'
#
# CLI>health
#
# Overall system health is good
#
        start_idx = 0
        for start_idx in range(len(lines)):   # find the last entry
            if lines[start_idx].find("CLI>health") != -1: break  # found next CLI command, reached the end of this session
        start_idx = start_idx + 1
            
        if start_idx == len(lines):
            dbg.printDBG2(file_name, "!!!! System Health Status not found from Engine%s" % eng_number)
            return False

        else:
            info = self.lines[start_idx+1].split()
            if info[4] == 'good':
                engine_info[eng_number]['Special']['System Health'] = 'GOOD'
            else:
                engine_info[eng_number]['Special']['System Health'] = 'NO GOOD'
#
# CLI>map
#
# Auto-application of Map 0 to all HBAs is enabled (vs. Auto-application of Map 0 to all HBAs is disabled)
#
# No mappable drives currently defined
#
        start_idx = 0
        for start_idx in range(len(lines)):   # find the last entry
            if lines[start_idx].find("CLI>map") != -1: break  # found next CLI command, reached the end of this session
        start_idx = start_idx + 1
            
        if start_idx == len(lines):
            dbg.printDBG2(file_name, "!!!! Map Status not found from Engine%s" % eng_number)
            return False

        else:
            info = self.lines[start_idx+1].split()
            if info[8] == 'enabled':
                engine_info[eng_number]['Special']['Auto Map'] = 'ON'
            else:
                engine_info[eng_number]['Special']['Auto Map'] = 'OFF'
#
# CLI>conmgr mode
#
# auto-configuration is based on inquiry page 0x83 serial number
#
# auto-configuration is based on WWNN/LUN
#
        start_idx = 0
        for start_idx in range(len(lines)):   # find the last entry
            if lines[start_idx].find("CLI>conmgr mode") != -1: break  # found next CLI command, reached the end of this session
        start_idx = start_idx + 1
            
        if start_idx == len(lines):
            dbg.printDBG2(file_name, "!!!! conmgr mode not found from Engine%s" % eng_number)
            return False

        else:
            info = self.lines[start_idx+1].split()
            if info[4] == 'inquiry':
                engine_info[eng_number]['Special']['pg83 MPIO'] = 'ON'
            else:
                engine_info[eng_number]['Special']['pg83 MPIO'] = 'OFF'
#
# Update the Application dictionary (build from the special mode)
#
# IBM AIX Application
#
        if (engine_info[eng_number]['Special']['ACA'] == 'ON' and engine_info[eng_number]['Special']['Storage Emulation'] == 'SDD'):
            engine_info[eng_number]['Application']['IBM AIX Support'] = 'ON'
        else:
            engine_info[eng_number]['Application']['IBM AIX Support'] = 'OFF'
#
# VMware Application
#        
        if (engine_info[eng_number]['Special']['VAAI'] == 'ON'):
            engine_info[eng_number]['Application']['VMware Support'] = 'ON'
        else:
            engine_info[eng_number]['Application']['VMware Support'] = 'OFF'
#
#  Video Application
#        
        if (engine_info[eng_number]['Special']['Video Mode'] == 'ON'):
            engine_info[eng_number]['Application']['Video Support'] = 'ON'
        else:
            engine_info[eng_number]['Application']['Video Support'] = 'OFF'
#
#  Auto Map Application
#        
        if (engine_info[eng_number]['Special']['Auto Map'] == 'ON'):
            engine_info[eng_number]['Application']['Auto Map Mode'] = 'ON'
        else:
            engine_info[eng_number]['Application']['Auto Map Mode'] = 'OFF'
#
#  Storage MPIO, pg83 mode vs. wwnn mode Application
#        
#        if (engine_info[eng_number]['Special']['pg83 MPIO'] == 'ON'):
#            engine_info[eng_number]['Application']['MPIO Use Serial Number'] = 'ON'
#        else:
#            engine_info[eng_number]['Application']['MPIO Use Serial Number'] = 'OFF'
#
#  Site Isolation Protection
#        
#        if (engine_info[eng_number]['Special']['Site Isolation'] == 'ON'):
#            engine_info[eng_number]['Application']['Site Isolation Protection'] = 'ON'
#        else:
#            engine_info[eng_number]['Application']['Site Isolation Protection'] = 'OFF'
#
        if (debug_level >= 4):
            dbg.printDBG4(file_name, "-- decode Special Mode for Engine%s, engine_info[Special]= %s" % (eng_number, engine_info[eng_number]['Special']))
        return True
#
# CLI>license status
#
# Installed licenses:
#   8 Gb FC Port Speed
#   2-way Mirroring
#   128 HBA Support
#   16 Mirror Support
#   16 Lifetime Mirror WWNNs
#
# Mask words: 4, 80000000, 40008, 0
#
# Loxoll bundle
#
# CLI>
#
    def DecodeLicense(self, eng_number, lines):

        for start_idx in range(len(lines)):   # find the last entry
            if lines[start_idx].find("license status") != -1: break  # found next CLI command, reached the end of this session
        start_idx = start_idx + 1
            
        for end_idx in range(start_idx, len(lines)):   # find the last entry
            if lines[end_idx].find("CLI>") != -1: break  # found next CLI command, reached the end of this session

        if start_idx == len(lines):
            dbg.printDBG2(file_name, "!!!! License Status not found from Engine%s" % eng_number)
            return False

        else:
            for i in range (start_idx, end_idx):
                if not lines[i].startswith('Installed'): continue
                start_idx = i + 1
                break
                
            engine_info[eng_number]['License'] = []
            for i in range (start_idx, end_idx):
                info = lines[i].lstrip().replace('\n', '').replace('\r', '')
                if info == '': break     # completed
                engine_info[eng_number]['License'].append(info)
#
        if (debug_level >= 4):
            dbg.printDBG4(file_name, "-- decode License for Engine%s engine_info[\'License\']= %s" % (eng_number, engine_info[eng_number]['License']))
        return True
#
#
#   mirror
#
#   Mirror(hex)    state       Map         Capacity  Members
#    33537(0x8301) Operational   0       5860118025  3 (OK )  0 (OK )
#    33538(0x8302) Operational   1      35160968250  4 (OK )  1 (OK )
#    33539(0x8303) Operational   2      35160968250  5 (OK )  2 (OK )
#    33540(0x8304) Operational   3      35160968250  8 (OK )  6 (OK )
#    33541(0x8305) Operational   4      35160968250  9 (OK )  7 (OK )
#
#Mirror(hex)    state       Map         Capacity  Members
# 33281(0x8201) Operational  -         390625536  0 (OK )  3 (OK ) 
# 33282(0x8202) Operational  -         585937920  1 (OK )  4 (OK ) 
# 33283(0x8203) Operational  -        4296875520  2 (OK )  5 (OK ) 
# 33537(0x8301) Unknown       0        390625536  0 (UN )  6 (OK )  3 (UN ) 
#
#
#CLI>mirror
#
#Mirror(hex)    state       Map         Capacity  Members
#
# 33537(0x8301) has_undef     0       1073741824  510 (EXP) 
# 33282(0x8202) Operational   -        458188800    2 (OK )
#
# '-' indicates not mapped to any initiator
# ['=', 'indicates', 'an', 'async', 'copy', 'member,', 'and', '>', 'indicates', 'an', 'async', 'copy', 'source', 'member']
#
#
#Mirror(hex)    state       Map         Capacity  Members
# 33281(0x8201) Operational   0        419430400 >0 (OK ) =4 (OK ) 
# 33282(0x8202) Operational   1        419430400 >1 (OK ) =5 (OK ) 
# 33283(0x8203) Operational   2        419430400 >2 (OK ) =6 (OK ) 
# 33284(0x8204) Operational   3        419430400 >3 (OK ) =7 (OK ) 
# 33285(0x8205) Operational   4         41943040  8 (OK )  10 (OK ) 
# 33286(0x8206) Operational   5         41943040 >9 (OK ) =11 (OK ) 
#
#= indicates an async copy member and > indicates an async copy source member
#
#CLI>mirror
#
#No mirrors defined
#
#CLI>exit
#
# {"Mirror": {"33281": ["Operational", "-", "1073741824", "T2045", "OK", "T2046", "OK", "-", "-", "-", "-"]}}
#
    def DecodeMirror(self, eng_number, lines):
        for start_idx in range(len(lines)):   # find the last entry
            if lines[start_idx].find("CLI>mirror") != -1: break  # found next CLI command, reached the end of this session
        start_idx = start_idx + 1
            
        for end_idx in range(start_idx, len(lines)):   # find the last entry
            if lines[end_idx].find("CLI>") != -1: break  # found next CLI command, reached the end of this session

        if start_idx == len(lines):
            dbg.printDBG2(file_name, "!!!! mirror info not found from Engine%s" % eng_number)
            return False

        else:
            engine_info[eng_number]['Mirror'] = {}
            for i in range (start_idx, end_idx):
                if not lines[i].startswith('Mirror(hex)'): continue
                start_idx = i + 1
                break
            
            if start_idx == end_idx:
                print engine_info[eng_number]['Mirror']
                return
            
            for i in range (start_idx, end_idx):
                
                lines[i] = lines[i].replace("(OK )","(OK)").replace("(UN )","(UN)").replace(">","").replace("=","")
                
                info = lines[i].split()                
                if info == []: continue     # skip empty line
                if info[0] == "'-'": continue
                if info[0] == "=": continue
                if info[0] == "No": continue
                
                m1 = m2 = m3 = m4 = "-"
                n1 = n2 = n3 = n4 = "-"
                
                if len(info) == 12:         # four-way mirror
                    n4 = 'T%0.4d' % int(info[10])
                    m4 = info[11][1:-1]
                if len(info) >= 10:         # three-way mirror
                    n3 = 'T%0.4d' % int(info[8])
                    m3 = info[9][1:-1]
                if len(info) >= 8:          # two-way mirror
                    n2 = 'T%0.4d' % int(info[6])
                    m2 = info[7][1:-1]
                if len(info) >= 6:          # one-way mirror
                    n1 = 'T%0.4d' % int(info[4])
                    m1 = info[5][1:-1]
                
                engine_info[eng_number]['Mirror'][info[0][:5]] = (info[1], info[2], info[3], n1, m1, n2, m2, n3, m3, n4, m4)
        #
        if (debug_level >= 4):
            dbg.printDBG4(file_name, "-- decode Mirror for Engine%s, engine_info[\'Mirror\']:" % eng_number)
            for mirror_set in sorted(engine_info[eng_number]['Mirror']):
                dbg.printDBG4(file_name, "---- id=%s, Data=%s" % (mirror_set, engine_info[eng_number]['Mirror'][mirror_set]))

        return True
#
#
#    conmgr engine status
#
#      1 Engines
#    ===========
#     tnum port wwpn               status
#        2 B1   2300-006022-0929d6 A
#          B2   2400-006022-0929d6 A
#
# CLI>conmgr engine status
#
#  0 Engines
# ===========
#
# CLI>
#
    def __decodeEngine(self, eng_number):

        engine_number = 0
        engine_info[eng_number]['Engine'] = {}

        for start_idx in range(self.f_length):   # find the last entry
            if self.lines[start_idx].find("CLI>conmgr engine status") != -1: break  # found next CLI command, reached the end of this session
        start_idx = start_idx + 1
            
        if start_idx == self.f_length:
            dbg.printDBG2(file_name, "!!!! engine status not found from Engine%s" % eng_number)
            return False
        #
        else:
            for i in range (start_idx, self.f_length):
                if self.lines[i].find('Engine') == -1: continue
                info = self.lines[i].split()
                engine_number = int(info[0])
                start_idx = i + 1
                break
                
            for end_idx in range(start_idx, self.f_length):   # find the last entry
                if self.lines[end_idx].find("CLI>") != -1: break  # found next CLI command, reached the end of this session
#                                
            if engine_number != 0:
                for i in range (start_idx, end_idx):
                    if self.lines[i].find("tnum") == -1: continue
                    start_idx = i + 1
                    break
#
                for i in range (start_idx, end_idx):
                    info = self.lines[i].split()
                    if info == []: continue     # skip empty lines
#
                    if info[0].isdigit() == True:
                        engine_id = 'E%0.4d' % int(info[0])
                        engine_info[eng_number]['Engine'][engine_id] = {}
                        engine_info[eng_number]['Engine'][engine_id][info[2]] = (info[1], info[3])
                    else:
                        engine_info[eng_number]['Engine'][engine_id][info[1]] = (info[0], info[2])
#
        if (debug_level >= 4):
            dbg.printDBG4(file_name, "-- decode Engine for Engine%s engine_info[\'Engine\']=" % eng_number)
            dbg.printDBG4(file_name, "---- info=%s" % engine_info[eng_number]['Engine'])
#
#
#------------------------------------------------------------------------------------------
#
#    conmgr drive status
#
#     10 Drives
#    ==========
#     tnum port wwpn               lun               status                  RE-stat
#        0 B1   5002-2c1001-46a000 0000-000000000000 A                       A
#          B2   5002-2c1001-46a001 0000-000000000000 A
#        1 B1   5002-2c1001-46a000 0001-000000000000 A                       A
#          B2   5002-2c1001-46a001 0001-000000000000 A
#        2 B1   5002-2c1001-46a000 0002-000000000000 A                       A
#          B2   5002-2c1001-46a001 0002-000000000000 A
#        3 B1   5002-2c1001-33d000 0000-000000000000 A                       A
#          B2   5002-2c1001-33d001 0000-000000000000 A
#        4 B1   5002-2c1001-33d000 0001-000000000000 A                       A
#          B2   5002-2c1001-33d001 0001-000000000000 A
#        5 B1   5002-2c1001-33d000 0002-000000000000 A                       A
#          B2   5002-2c1001-33d001 0002-000000000000 A
#        6 B1   5002-2c1001-46a002 0000-000000000000 A                       A
#          B2   5002-2c1001-46a003 0000-000000000000 A
#        7 B1   5002-2c1001-46a002 0001-000000000000 A                       A
#          B2   5002-2c1001-46a003 0001-000000000000 A
#        8 B1   5002-2c1001-33d002 0000-000000000000 A                       A
#          B2   5002-2c1001-33d003 0000-000000000000 A
#        9 B1   5002-2c1001-33d002 0001-000000000000 A                       A
#          B2   5002-2c1001-33d003 0001-000000000000 A
#
#------------------------------------------------------------------------------------------
#
# CLI>conmgr drive status
#
#
#
#  4 Drives
#
#==========
#
# tnum port wwpn               lun               status                  RE-stat
#
#    1 A1   2100-006022-112250 0000-000000000000 U                       N
#
#    2 A2   2200-006022-112250 0000-000000000000 U                       N
#
#    3 B1   2300-006022-112250 0000-000000000000 U                       N
#
#    4 B2   2400-006022-112250 0000-000000000000 U                       N
#
#------------------------------------------------------------------------------------------
#
#
#   {'Drive': { "T0000": { "5002-2c1001-33d003": (A1, 0001, A, "")}}}
#
    def __decodeDrive(self, eng_number):

        drive_number = 0
        engine_info[eng_number]['Drive'] = {}
        
        for start_idx in range(self.f_length):
            if self.lines[start_idx].find("CLI>conmgr drive status") != -1: break

        if start_idx+1 == self.f_length:
            dbg.printDBG2(file_name, "!!!! drive status not found from Engine%s" % eng_number)
            return False

        else:
            for i in range (start_idx, self.f_length):
                if self.lines[i].find('Drive') == -1: continue
                info = self.lines[i].split()
                drive_number = int(info[0])
                start_idx = i + 1
                break
                
            if i == self.f_length:
                return False
                
            for end_idx in range(start_idx, self.f_length):   # find the last entry
                if self.lines[end_idx].find("CLI>") != -1: break  # found next CLI command, reached the end of this session
#            
            if drive_number == 0:
                engine_info[eng_number]['Drive']={}
            else:
                for i in range (start_idx, end_idx):
                    if self.lines[i].find("tnum") == -1: continue
                    start_idx = i + 1
                    break
#
                for i in range (start_idx, end_idx):
                    info = self.lines[i].split()
                    if info == []: continue     # skip empty lines

#
# 0 B1   5742-b0f000-4e4012 0001-000000000000 A                      A
#   B2   5742-b0f000-4e4022 0001-000000000000 A                      
# 1 B1   5742-b0f000-4e4032 0001-000000000000 I                      
#
# 'Drive': {
#     "T0000": {
#         "5742-b0f000-4e4012": [
#             "B1", 
#             "0001", 
#             "A", 
#             "A"
#         ], 
#         "5742-b0f000-4e4022": [
#             "B2", 
#             "0001", 
#             "A", 
#             "A"
#         ], 
#         "5742-b0f000-4e4032": [
#             "B1", 
#             "0001", 
#             "A", 
#             "A"
#         ]
#     }, 
# 
                    if info[0].isdigit() == True:
                        if len(info) == 5: re_status = ''
                        else: re_status = info[5]
                        target_id = 'T%0.4d' % int(info[0])
                        engine_info[eng_number]['Drive'][target_id] = {}
                        engine_info[eng_number]['Drive'][target_id][info[2]] = (info[1], info[3][:4], info[4], re_status)
                    else:
                        engine_info[eng_number]['Drive'][target_id][info[1]] = (info[0], info[2][:4], info[3], re_status)
#
        if (debug_level >= 4):
            dbg.printDBG4(file_name, "-- print Engine%s drives table" % eng_number)
            for drive_set in sorted(engine_info[eng_number]['Drive']):
                dbg.printDBG4(file_name, "---- id=%s, data=%s" % (drive_set, engine_info[eng_number]['Drive'][drive_set]))

#        print "parse==", eng_number, engine_info[eng_number]['Drive']

#
#CLI>drvstate
#
#
#Resource drives:
#    Target #        Capacity (LBA)  I/O cnt  State
#    --------        --------------  -------  -----
#           0             390625536        0  Operational
#           1             585937920        0  Operational
#           2             195313152        0  Operational
#           3             976562688        0  Operational
#           4             195313152        0  Operational
#           5             409594304        0  Operational
#           6             614385868        0  Operational
#           7             204800000        0  Operational
#           8            1023997952        0  Operational
#
#Complex drives:
#    Target #   Subtype   I/O cnt  State
#    --------  ---------  -------  -----
#      0x8201   Mirror          0  Operational
#      0x8301   Mirror          0  Operational
#      0x8302   Mirror          0  Operational
#
#Extended complex drives:
#    None defined
#
#------------------------------------------------------------------------------------------
#
#CLI>drvstate
#
#
#Resource drives:
#    None defined

#Complex drives:
#    None defined
#
#Extended complex drives:
#    None defined
#
    def __decodeDriveCap(self, eng_number):

        drive_number = 0
        
        for start_idx in range(self.f_length):
            if self.lines[start_idx].find("CLI>drvstate") != -1: break

        if start_idx+1 == self.f_length:
            dbg.printDBG2(file_name, "!!!! drvstate not found from Engine%s" % eng_number)
            return False

        else:
            for i in range (start_idx, self.f_length):
                if self.lines[i].find("Resource drives") == -1: continue
                start_idx = i + 1
                break
                
            if i == self.f_length:
                return False
                
            for end_idx in range(start_idx, self.f_length):   # find the last entry
                if self.lines[end_idx].find("Complex drives") != -1: break  # found the end of this session
                if self.lines[end_idx].find("DISCARDED <<<") != -1: break  # found >>> CHARACTERS DISCARDED <<<
            end_idx -= 1
#            
            info = self.lines[start_idx].split()
            if info[0] == "None":
                engine_info[eng_number]['DrivesCap']={}
            else:
                start_idx += 2
#
                for i in range (start_idx, end_idx):
                    info = self.lines[i].split()
                    if info[0].isdigit() == True:
                        target_id = 'T%0.4d' % int(info[0])
                        engine_info[eng_number]['DrivesCap'][target_id] = ('', info[1], info[2], info[3])
#
        if (debug_level >= 4):
            dbg.printDBG4(file_name, "-- print Engine%s drives Capacity table" % eng_number)
            for drive_set in sorted(engine_info[eng_number]['DrivesCap']):
                dbg.printDBG4(file_name, "---- id=%s, data=%s" % (drive_set, engine_info[eng_number]['DrivesCap'][drive_set]))    
#
#    conmgr initiator status
#
#     34 Initiators
#    ==============
#     tnum type port wwpn               status
#        0    0 A2   1000-0000c9-b81778 A
#        1    0 A2   1000-0000c9-b8168a A
#        2    0 A1   1000-00062b-14f21c A
#        3    0 A1   1000-00062b-14f23c A
#        4    0 A2   1000-00062b-14f240 A
#        5    0 A1   1000-00062b-15bb44 A
#        6    0 A2   1000-00062b-14f054 A
#        7    0 A1   1000-00062b-14ec64 A
#        8    0 A1   1000-00062b-14f480 I
#        9    0 A2   1000-00062b-14d5c0 A
#       10    0 A1   1000-00062b-14f4e0 A
#       11    0 A2   1000-00062b-14f4e4 A
#       12    0 A1   2100-001086-02f1b6 A
#       13    0 A2   2100-001086-02f1dc A
#       14    0 A2   2100-001b32-8b1302 I
#       15    0 A1   2100-001b32-158d0c A
#       16    0 A1   2100-001b32-107924 I
#       17    0 A1   2100-001b32-11e64d A
#       18    0 A2   2100-001b32-11df4e A
#       19    0 A1   2100-001b32-11c250 A
#       20    0 A2   2100-001b32-8a5fb5 A
#       21    0 A2   2100-0024ff-613f22 A
#       22    0 A1   2100-00e08b-9e5a4a A
#       23    0 A2   2101-001b32-a64cf8 I
#       24    0 A2   5001-438018-6b5448 A
#       25    0 A2   2100-0024ff-4881ca A
#       26    0 A2   2100-0024ff-4880a8 I
#       27    0 A2   2100-001b32-02bde4 I
#       28    0 A2   2101-001b32-22bde4 I
#       29    0 A2   2100-001b32-107924 A
#       30    0 A1   2100-001b32-8b1302 A
#       31    0 A2   2100-0024ff-48809e I
#       32    0 A1   1000-00062b-14f481 A
#       33    0 A2   2100-0024ff-4881cb I
#
#####   {"Initiator": {"I0001": ["2", "A2", "2100-0024ff-5d272b", "A"]}}
#   {"Initiator": {"I0001": {"2100-0024ff-5d272b": ["2", "A2", , "A"]}}}
#
    def __decodeInitiator(self, eng_number):

        initiator_number = 0

        for start_idx in range(self.f_length):
            if self.lines[start_idx].find("CLI>conmgr initiator status") != -1: break
        start_idx = start_idx + 1

        if start_idx == self.f_length:
            dbg.printDBG2(file_name, "!!!! initiator status not found from Engine%s" % eng_number)
            return False
        #
        else:
            for i in range (start_idx, self.f_length):
                if self.lines[i].find('Initiator') == -1: continue
                info = self.lines[i].split()
                initiator_number = int(info[0])
                start_idx = i + 1
                break
                
            for end_idx in range(start_idx, self.f_length):   # find the last entry
                if self.lines[end_idx].find("CLI>") != -1: break  # found next CLI command, reached the end of this session
#                       
                for i in range (start_idx, end_idx):
                    info = self.lines[i].split()
                    if info == []: continue     # skip empty lines
#
            if initiator_number == 0:
                engine_info[eng_number]['Initiator'] = {}
            else:
                for i in range (start_idx, end_idx):
                    if self.lines[i].find("tnum") == -1: continue
                    start_idx = i + 1
                    break
#
                for i in range (start_idx, end_idx):

                    info = self.lines[i].split()
                    if info == []: continue     # skip empty lines
#
                    initiator_id = 'I%0.4d' % int(info[0])
                    engine_info[eng_number]['Initiator'][initiator_id] = {}
                    engine_info[eng_number]['Initiator'][initiator_id][info[3]] = (info[1], info[2], '', info[4])
#
        if (debug_level >= 4):
            dbg.printDBG4(file_name, "-- print Engine%s initiator table" % eng_number)
            for initiator_set in sorted(engine_info[eng_number]['Initiator']):
                dbg.printDBG4(file_name, "---- id=%s, data=%s" % (initiator_set, engine_info[eng_number]['Initiator'][initiator_set]))
#
#
# Port  Node Name           Port Name
# A1    2000-006022-0929d4  2100-006022-0929d4
# A2    2000-006022-0929d4  2200-006022-0929d4
# B1    2000-006022-0929d4  2300-006022-0929d4
# B2    2000-006022-0929d4  2400-006022-0929d4
#
#
# CLI>port
#
# Port A1 enabled, link active at 4 Gb/s
# Port A2 enabled, link active at 4 Gb/s
# Port B1 enabled, link active at 4 Gb/s
# Port B2 enabled, link active at 4 Gb/s
#
# CLI>port
#
# Port A1 enabled, link inactive
# Port A2 enabled, link inactive
# Port B1 enabled, link inactive
# Port B2 enabled, link inactive
#
# CLI>port
#
# Port A1 enabled, link active at 4 Gb/s
# Port A2 enabled, link active at 4 Gb/s
# Port B1 disabled
# Port B2 enabled, link active at 4 Gb/s
#

    def __decodePorts(self, eng_number):
#
# Get WWNN/WWPN
        for start_idx in range(self.f_length):
            if self.lines[start_idx].startswith("Port  Node Name"): break
        start_idx = start_idx + 1
        for end_idx in range(start_idx, self.f_length):   # find the last entry
            if self.lines[end_idx].find("CLI>") != -1: break  # found next CLI command, reached the end of this session

        if start_idx == self.f_length:
            dbg.printDBG2(file_name, "!!!! port name not found from Engine%s" % eng_number)
            return False

        else:
            wwname = {}
            for i in range (start_idx, end_idx):
                info = self.lines[i].split()
                if info == []: continue     # skip empty lines
                wwname[info[0]] = [info[0], info[1], info[2]]
#
# Get Port Status
        for start_idx in range(self.f_length):
            if self.lines[start_idx].find("CLI>port") != -1: break
        start_idx = start_idx + 1
        for end_idx in range(start_idx, self.f_length):   # find the last entry
            if self.lines[end_idx].find("CLI>") != -1: break  # found next CLI command, reached the end of this session

        if start_idx == self.f_length:
            dbg.printDBG2(file_name, "!!!! port status not found from Engine%s" % eng_number)
            return False
        
        else:
            for i in range (start_idx, end_idx):
                if self.lines[i].find("Port") == -1: continue
                info = self.lines[i].split()
                if info[2] == "disabled": 
                    engine_info[eng_number]['Ports'][info[1]] = (wwname[info[1]][1], wwname[info[1]][2], info[1], info[2], "disabled")
                elif info[4] == "active":
                    engine_info[eng_number]['Ports'][info[1]] = (wwname[info[1]][1], wwname[info[1]][2], info[1], info[2][:-1], info[6]+" Gb/s")
                elif info[4] == "inactive":
                    engine_info[eng_number]['Ports'][info[1]] = (wwname[info[1]][1], wwname[info[1]][2], info[1], info[2][:-1], "inactive")
#
        if (debug_level >= 4):
            dbg.printDBG4(file_name, "-- print Engine%s port table" % eng_number)
            for port_set in sorted(engine_info[eng_number]['Ports']):
                dbg.printDBG4(file_name, "---- id=%s, data=%s" % (port_set, engine_info[eng_number]['Ports'][port_set]))
#
# CLI>bpt
# Port A1 (0) Bad Port Table:
#   No Entries
# Port A2 (1) link is down
# Port B1 (2) Bad Port Table:
#   0x010825
# Port B2 (3) Bad Port Table:
#   No Entries
#
# Bad Port Table protection mode is set to protect:
#   The last operational member of each mirror
#
    def __decodeBPT(self, eng_number):
#
# Get Port Status
        for start_idx in range(self.f_length):
            if self.lines[start_idx].find("CLI>bpt") != -1: break
        start_idx = start_idx + 1
        for end_idx in range(start_idx, self.f_length):   # find the last entry
            if self.lines[end_idx].find("CLI>") != -1: break  # found next CLI command, reached the end of this session

        if start_idx == self.f_length:
            dbg.printDBG2(file_name, "!!!! Bad Port Table not found from Engine%s" % eng_number)
            return False
        
        else:
            for i in range (start_idx, end_idx):
                if self.lines[i].find("Port") == -1: continue
                info = self.lines[i].split()
                if info[3] == "Bad":
                    info_next = self.lines[i+1].split()
                    if info_next[0] == 'No':
                        engine_info[eng_number]['BPT'][info[1]] = (0, "No Entries")
                    else:
                        engine_info[eng_number]['BPT'][info[1]] = (0, info_next[0])
                elif info[3] == "link":
                    engine_info[eng_number]['BPT'][info[1]] = (0, "link down")
                else:
                    continue

        if (debug_level >= 4):
            dbg.printDBG4(file_name, "-- print Engine%s bad port table" % eng_number)
            for port_set in sorted(engine_info[eng_number]['BPT']):
                dbg.printDBG4(file_name, "---- id=%s, data=%s" % (port_set, engine_info[eng_number]['BPT'][port_set]))
#
#CLI>engine
#
#   Engine  Status  Serial-Nr  IP-Addr           Firmware
#
#>> 0  (M)  Online  11340742   192.168.212. 53   VCMSVMIR 15.7.3.0 OR
#
#CLI>engine
#
#   Engine  Status  Serial #  IP Addresses (1/2)                Firmware
#   --------------------------------------------------------------------
#   1  (M)  Online     ... further info not available
#>> 2       Online  11340522  192.168.1.46/192.168.1.56         15.9.7.5 OR
#
#CLI>engine
#
#   Engine  Status  Serial #  IP Addresses (1/2)                Firmware
#   --------------------------------------------------------------------
#>> 1  (M)  Online  11340638  192.168.1.47/192.168.1.57         15.9.7.5 OR
#   2       Online  11340522  192.168.1.46/192.168.1.56         15.9.7.5 OR
#
#   {'ClusterSN': { '11403015': ('1', 'This Engine', 'Online', 'M', '10.1.0.34', '20.20.20.1')}}
#
    def __decodeMaster(self, eng_number):
        engine_info[eng_number]['Master'] = ''
        engine_info[eng_number]['This Engine'] = 'U'
        engine_info[eng_number]['ClusterSN'] = {}
#
        for start_idx in range(self.f_length):
            if self.lines[start_idx].find("CLI>engine") != -1: break
        start_idx = start_idx + 1
        for end_idx in range(start_idx, self.f_length):   # find the last entry
            if self.lines[end_idx].find("CLI>") != -1: break  # found next CLI command, reached the end of this session
            
        if start_idx == self.f_length:
            dbg.printDBG2(file_name, "!!!! engine status not found from Engine%s" % eng_number)
            return False

        else:
            start_idx = self.__FindNext('--------', start_idx, end_idx) + 1
            for i in range(start_idx, end_idx):
                info = self.lines[i].split()
                if info == []: continue
                if info[0] == '>>' and info[2] == '(M)':    # >> 1 (M)  Online  11340638  192.168.1.47/192.168.1.57 15.9.7.5 OR
                    engine_info[eng_number]['Master'] = "M"  
                    engine_info[eng_number]['This Engine'] = info[1]
                    engine_info[eng_number]['ClusterSN'][info[4]] = \
                        (info[1], 'This Engine', info[3], 'M', info[5].split('/')[0], info[5].split('/')[1]) 
                    
                elif info[0] == '>>':                       # >> 2      Online  11340638  192.168.1.47/192.168.1.57 15.9.7.5 OR
                    engine_info[eng_number]['This Engine'] = info[1]
                    engine_info[eng_number]['ClusterSN'][info[3]] = \
                        (info[1], 'This Engine', info[2], '', info[4].split('/')[0], info[4].split('/')[1])
                elif info[1] == '(M)':                      #    1 (M)  Online  11340638  192.168.1.47/192.168.1.57 15.9.7.5 OR
                    if info[3].isdigit() == True:
                        engine_info[eng_number]['ClusterSN'][info[3]] = \
                            (info[1], '', info[2], '', info[4].split('/')[0], info[4].split('/')[1])
                    else:                                   #    1 (M)  Online     ... further info not available
                        pass
                else:                                       
                                                            
                    if info[1] == 'Offline': continue
                    elif info[2] == '...': continue         #    2      Online     ... further info not available
                    else:                                   #    2      Online  11340522  192.168.1.46/192.168.1.56 15.9.7.5 OR
                        engine_info[eng_number]['ClusterSN'][info[2]] = \
                            (info[0], '', info[1], '', info[3].split('/')[0], info[3].split('/')[1])
#
    def __decodeGroup(self, eng_number):
#
# first to decode CLI>group
#
# CLI>group
#
# No HBA Groups defined
# No Drive Groups defined
#
# CLI>group
# HBA Groups:
#  21: 5006-022100-ad0c2b
#
# Drive Groups:
#  0: 0x8301 0x8302
#  3: 0x8301 0x8302
#
        for start_idx in range(self.f_length):
            if self.lines[start_idx].find("CLI>group") != -1: break
        start_idx = start_idx + 1
        for end_idx in range(start_idx, self.f_length):   # find the last entry
            if self.lines[end_idx].find("CLI>") != -1: break  # found next CLI command, reached the end of this session
            
        if start_idx == self.f_length:
            dbg.printDBG2(file_name, "!!!! Group info not found from Engine%s" % eng_number)
            return False

        else:
            for i in range (start_idx, end_idx):
                if self.lines[i].find("HBA Groups") == -1: continue
                info = self.lines[i].split()
                start_idx = i + 1
                break
                
            engine_info[eng_number]['Group']['HBA'] = {}
            engine_info[eng_number]['Group']['Drive'] = {}

            if info[0]=="No": pass      # No HBA Groups defined
            else:
                for i in range (start_idx, end_idx):
                    info = self.lines[i].split()
                    if info == []: continue
                    if info[0] == 'Drive' or info[0] == 'No':
                        start_idx = i + 1
                        break
                    engine_info[eng_number]['Group']['HBA'][info[0][:-1]] = []
                    for j in range (1, len(info)): engine_info[eng_number]['Group']['HBA'][info[0][:-1]].append(info[j])
            #
            if info[0]=="No": pass      # No Drive Groups defined
            else:
                for i in range (start_idx, end_idx):
                    info = self.lines[i].split()
                    if info == []: continue
                    engine_info[eng_number]['Group']['Drive'][info[0][:-1]] = []
                    
                    for j in range (1, len(info)):                              # convert from hex to decimal
                        engine_info[eng_number]['Group']['Drive'][info[0][:-1]].append(str(int(info[j], 16)))
#
# second to decode CLI>map
#
        for start_idx in range(self.f_length):
            if self.lines[start_idx].find("CLI>map") != -1: break
        start_idx = start_idx + 1
        for end_idx in range(start_idx, self.f_length):   # find the last entry
            if self.lines[end_idx].find("CLI>") != -1: break  # found next CLI command, reached the end of this session
            
        if start_idx == self.f_length:
            dbg.printDBG2(file_name, "!!!! Group info not found from Engine%s" % eng_number)
            return False

        else:
            for i in range (start_idx, end_idx):
                if self.lines[i].find("Map 0") == -1: continue
                info = self.lines[i].split()
                start_idx = i + 1
                break
                
            engine_info[eng_number]['Group']['Map'] = {}

            if info[8]=="enabled":
            #
            # CLI>map
            #
            # Auto-application of Map 0 to all HBAs is enabled
            #
            # No mappable drives currently defined
            #
            # CLI>map
            #
            # Auto-application of Map 0 to all HBAs is enabled
            #
            # Map applied to all HBAs:
            # 0x8201 0x8202
            #
                engine_info[eng_number]['AutoMap'] = 'Enabled'
                engine_info[eng_number]['Group']['Map']['0'] = {}
                engine_info[eng_number]['Group']['Map']['0']['Raw Data'] \
                    = self.lines[i].replace('\r', '').replace('\n','').lstrip()
                engine_info[eng_number]['Group']['Map']['0']['Include'] = []

                engine_info[eng_number]['Group']['Map']['0']['Used By'] = []
                for init_id in engine_info[eng_number]['Initiator']:
                    engine_info[eng_number]['Group']['Map']['0']['Used By'].append(init_id)                
                
                for i in range (start_idx, end_idx):
                    info = self.lines[i].split()
                    if info == []: continue
                    if info[0] == 'No':     # (No mappable drives currently defined)
                        return           
                    else:                   # (Map applied to all HBAs:)
                        break
                start_idx = i + 1
                for i in range (start_idx, end_idx):
                    info = self.lines[i].split()
                    for j in range (len(info)):
                        engine_info[eng_number]['Group']['Map']['0']['Include'].append(str(int(info[j], 16)))
            else:
            #
            # CLI>map
            # 
            # Auto-application of Map 0 to all HBAs is disabled
            # 
            # Defined LUN Maps:
            #   0:
            #      Raw data:
            #        drive group 0
            #      Groups resolved, any duplicates ignored:
            #        0x8201 (33281), 0x8203 (33283)
            #      Used by this engine for:
            #        5555-666677-778889
            #   1:
            #      Raw data:
            #        drive group 1
            #      Groups resolved, any duplicates ignored:
            #        0x8202 (33282), 0x8203 (33283)
            #      Used by this engine for:
            #        2100-001086-024753
            #
                engine_info[eng_number]['AutoMap'] = 'Disabled'
                for i in range (start_idx, end_idx):
                    info = self.lines[i].split()
                    if info == []: continue
                    if info[0][-1:] != ':': continue
                    map_num = info[0][:-1]
                    engine_info[eng_number]['Group']['Map'][map_num] = {}
                    engine_info[eng_number]['Group']['Map'][map_num]['Raw Data'] = ''
                    engine_info[eng_number]['Group']['Map'][map_num]['Include'] = []
                    engine_info[eng_number]['Group']['Map'][map_num]['Used By'] = []
                
                    if len(info) != 1:
                        print "!!! FW version not supported !!!"
                        return
                    
                    j = self.__FindNext('Raw data:', i, end_idx)
                    if j == -1: return False
                    else:
                        engine_info[eng_number]['Group']['Map'][map_num]['Raw Data'] \
                            = self.lines[j+1].replace('\r', '').replace('\n','').lstrip()
                        
                    j = self.__FindNext('Groups resolved', j, end_idx)
                    
                    if j == -1: return False
                    else:
                        j += 1              # next line
                        for n in range(j, end_idx):
                            info = self.lines[n].split()
                            if info[0][:2] != '0x': break 
                            for k in range (1, len(info), 2):
                                engine_info[eng_number]['Group']['Map'][map_num]['Include'].append(info[k].replace(',', '')[1:-1])
                        j = n
                    #
                    j = self.__FindNext('Used by', j, end_idx)
                    if j == -1: return False
                    else:
                        j += 1              # next line
                        for n in range(j, end_idx):
                            info = self.lines[n].split()
                            if info == [] or info[0][-1:] == ':': break 
                            for k in range (len(info)):
                                engine_info[eng_number]['Group']['Map'][map_num]['Used By'].append(info[k].replace(',', ''))
                        j = n
                    i = j
            
            """ (Old format, keep for reference)
                for i in range (start_idx, end_idx):
                    info = self.lines[i].split()
                    if info == []: continue
                    if info[0][-1:] != ':': continue
                    map_num = info[0][:-1]
                    engine_info[eng_number]['Group']['Map'][map_num] = {}
                    engine_info[eng_number]['Group']['Map'][map_num]['Raw Data'] = ''
                    engine_info[eng_number]['Group']['Map'][map_num]['Include'] = []
                    engine_info[eng_number]['Group']['Map'][map_num]['Used By'] = []
                    
                    if len(info) != 1:
                    #  2: 0x8301 (33537), 0x8302 (33538)
                    # Used by this engine for: 5006-022300-ad0c2b
                    #  3: drive group 3 (groups shown)
                    #   0x8301 (33537), 0x8302 (33538) (groups resolved)
                    # Used by this engine for: 5006-022100-ad0c2b
                    #  99: 0x8101 (33025), 0x8102 (33026), 0x8301 (33537)
                    #    0x8302 (33538)
                    # Not used by any HBA on this engine
                    #            
                        for j in range (1, len(info), 2):
                            if info[j][:2] != '0x': break
                            engine_info[eng_number]['Group']['Map'][map_num]['Include'].append(str(int(info[j], 16)))
                        
                        i += 1              # next line
                        info = self.lines[i].split()
                        if info == []: continue
                        if info[0] != 'Used':   # continue the 'Include'
                        
                            for j in range (0, len(info), 2):
                                if info[j][:2] != '0x': break
                                engine_info[eng_number]['Group']['Map'][map_num]['Include'].append(str(int(info[j], 16)))
                        
                            i += 1              # next line
                            info = self.lines[i].split()
                            if info == []: continue
                            if info[0] != 'Used':
                                i -= 1
                                continue
                            for j in range (5, len(info), 1):
                                engine_info[eng_number]['Group']['Map'][map_num]['Used By'].append(info[j])
                        else:           # Used by this engine for:
                            for j in range (5, len(info), 1):
                                engine_info[eng_number]['Group']['Map'][map_num]['Used By'].append(info[j])                        
                    #
                (Old format, keep for reference)
            """
#
#        print engine_info[eng_number]['Group']['Map']
#
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
#   {'Drive': {"T0000": {"5002-2c1001-33d003": (A1, 0001, "A", "A")}}}
#   {'Explore': { "A1": { 'Drive': { "5002-2c1001-33d003": { '0001': ('2929.6GB', 'dg0ld0', '0x010825', 'T0001')}}
#                                                          { '0006': ('2929.6GB', 'dg0ld0', '0x010825', '')}}
#                       { 'Initiator': { '5006-022300-ad0c2b': ('0x020600', 'I0001')}}}}}
#
    def __decodeExplore(self, eng_number, port = ''):
#
# Find the "explore <port>" and decode the file. If port is blank, find the first "explore" in the file
# 
        for start_idx in range(self.f_length):
            if self.lines[start_idx].find("CLI>explore %s" % port) != -1: break

        if start_idx+1 == self.f_length:
            dbg.printDBG2(file_name, "!!!! Group info not found from Engine%s" % eng_number)
            return False

        info = self.lines[start_idx].split()
        current_port = info[1]

        for end_idx in range(start_idx+1, self.f_length):   # find the last entry
            if self.lines[end_idx].find("CLI>") != -1: break  # found next CLI command, reached the end of this session
        
        for i in range (start_idx, end_idx):
            if self.lines[i].find("FC port") == -1 and self.lines[i].find("Error") == -1: continue
            info = self.lines[i].split()
            start_idx = i + 1
            break
            
        engine_info[eng_number]['Explore'][current_port] = {}
            
        if info[0]=="Error":
            return      # Error -1: link down ; next please

        line_count = 0
        for i in range (start_idx, end_idx):
            info = self.lines[start_idx+line_count].split()
            line_count += 1
            if info == []: continue
            if len(info) == 3: break   # "x ports reported"    
            wwpn = info[1]
            if info[3] == 'Target':
                if 'Drive' not in engine_info[eng_number]['Explore'][current_port]:
                    engine_info[eng_number]['Explore'][current_port]['Drive'] = {}
                engine_info[eng_number]['Explore'][current_port]['Drive'][wwpn] = {}
                
                for j in range (start_idx+line_count, end_idx):
                    info1 = self.lines[j].split()
                    if info1 == []: continue
                    if info1[0] == "LUNS:": continue
                    if info1[0].isdigit() != True or len(info1) != 4: break
#
#   Set up LUN info  
#   {'Drive': {"T0000": {"5002-2c1001-33d003": (A1, 0001, "A", "A")}}}
#   {'Explore': { "A1": { 'Drive': { "5002-2c1001-33d003": { '0001': ('2929.6GB', 'dg0ld0', '0x010825', 'T0001')}}
#                                                          { '0006': ('2929.6GB', 'dg0ld0', '0x010825', '')}}
#                       { 'Initiator': { '5006-022300-ad0c2b': ('0x020600', 'I0001')}}}}}
#
                    ser_number = info1[3]
                    lun_number = info1[0]
                    target_id = ''
                    for tid in engine_info[eng_number]['Drive']:
                        if wwpn in engine_info[eng_number]['Drive'][tid]:
                            if engine_info[eng_number]['Drive'][tid][wwpn][1] == lun_number:
                                target_id = tid
                    engine_info[eng_number]['Explore'][current_port]['Drive'][wwpn][lun_number]= \
                        (info1[1]+info1[2], info1[3], info[0], target_id)
                    line_count += 1
                
            elif info[3] == 'Initiator':
                initiator_id = ''
                wwpn = info[1]
                for iid in engine_info[eng_number]['Initiator']:
                    for check_wwpn in engine_info[eng_number]['Initiator'][iid]:
                        if check_wwpn == wwpn:
                            initiator_id = iid
                            break
                
                engine_info[eng_number]['Explore'][current_port]['Initiator'] = {}
                engine_info[eng_number]['Explore'][current_port]['Initiator'][wwpn] = (info[0], initiator_id)
#
    def DecodeDriveSerialNumber(self, eng_number, lines):
#
# CLI>conmgr
# 
# 4 Drives
# ==========
# tnum type port wwpn lun rd wr
# 0 A-A B2 2602-000155-600145 0000-000000000000 1 1
# B1 2603-000155-600145 0000-000000000000 1 1
# B1 2606-000155-600145 0000-000000000000 1 1
# B2 2607-000155-600145 0000-000000000000 1 1
# ser-nr: 0x22eb000155a069b2
#
# 1 A-A B2 2602-000155-600145 0001-000000000000 1 1
# B1 2603-000155-600145 0001-000000000000 1 1
# B1 2606-000155-600145 0001-000000000000 1 1
# B2 2607-000155-600145 0001-000000000000 1 1
# ser-nr: 0x2299000155dae234
#
# 2 A-A B1 5000-612024-534000 0000-000000000000 1 1
# B2 5000-612024-534001 0000-000000000000 1 1
# ser-nr: dg0ld0
# 
# 3 A-A B1 5000-612024-534000 0001-000000000000 1 1
# B2 5000-612024-534001 0001-000000000000 1 1
# ser-nr: dg0ld1
#
# 0 Engines our engine number: 1
# ===========
# 
# 0 Initiators
# ==============
#
        """
CLI>conmgr

  7 Drives
==========
 tnum type port wwpn               lun                rd  wr
    0 A-A  B1   2603-000155-600145 0000-000000000000   1   1
           B2   2607-000155-600145 0000-000000000000   1   1
    1 A-A  B1   2603-000155-600145 0001-000000000000   1   1
           B2   2607-000155-600145 0001-000000000000   1   1
    2 A-A  B1   2603-000155-600145 0002-000000000000   1   1
           B2   2607-000155-600145 0002-000000000000   1   1
    3 A-A  B1   2603-000155-600145 0003-000000000000   1   1
           B2   2607-000155-600145 0003-000000000000   1   1
    4 A-A  B2   5000-612024-534000 0000-000000000000   1   1
           B1   5000-612024-534001 0000-000000000000   1   1
    5 A-A  B2   5000-612024-534000 0001-000000000000   1   1
           B1   5000-612024-534001 0001-000000000000   1   1
    6 A-A  B2   5000-612024-534000 0002-000000000000   1   1
           B1   5000-612024-534001 0002-000000000000   1   1

  1 Engines        our engine number:     2
===========
 tnum port wwpn
    1 B1   2300-006022-ad0b5e
      B2   2400-006022-ad0b5e

  2 Initiators
==============
 tnum type port wwpn
    0    0 A2   2100-001086-024753
    1    0 A1   5555-666677-778889
        """
#
#   {"DrivesSN": { "T2044": ["A-A", "serial number"]}} 
#
        for start_idx in range(self.f_length):
            if self.lines[start_idx].find("CLI>conmgr") != -1:
                if len( self.lines[start_idx].split()) == 1: break
        start_idx = start_idx + 1
        for end_idx in range(start_idx, self.f_length):   # find the last entry
            if self.lines[end_idx].find("CLI>") != -1: break  # found next CLI command, reached the end of this session
            
        if start_idx == self.f_length:
            dbg.printDBG2(file_name, "!!!! Serial Number info not found from Engine%s" % eng_number)
            return False

        else:
#
# get drive count
#
            for i in range (start_idx, end_idx):
                if self.lines[i].find("Drive") == -1: continue
                info = self.lines[i].split()
                if info == []: continue
                start_idx = i + 1
                break    
            drive_count = info[0]
            if drive_count == 0: return
#
            for i in range (start_idx, end_idx):
                if self.lines[i].find("tnum") == -1: continue
                start_idx = i + 1
                break
# get drive ID
#
            for k in range (int(drive_count)):
                for i in range (start_idx, end_idx):
                    info = self.lines[i].split()
                    if info == []: continue
                    start_idx = i + 1
                    break
                drive_id = 'T%0.4d' % int(info[0])
                type = info[1]
#
# get serial number of the drive ID
#
                ser_number = ''
                for i in range (start_idx, end_idx):
                    info = self.lines[i].split()
                    if info == []: continue
                    if self.lines[i].find("ser-nr:") == -1 and info[0].isdigit() != True: continue
                    break
                start_idx = i + 1
                if info[0].isdigit() != True: ser_number = info[1]
                else: start_idx = i                           # no serial number case
#
# record serial number of the drive ID
#
                engine_info[eng_number]['DriveSN'][drive_id] = [type, ser_number]
#
# CLI>rebuild
#
# No rebuilds performed on this engine
#
# No rebuilds in this SAN
#
# no degrades ready to rebuild found
#
#
# CLI>rebuild
#
# Rebuilds performed on this engine:
# Lcl Glbl Mirror Member State Done Type   Speed  IOPS Async  Time
#                                          MB/s        Pass #
# ----------------------------------------------------------------------
#  0    0  0x8201 0x07ff run   0.0% full   10.00   100 N/A    0h 00m 02s
#
#
# Rebuilds in this SAN:
#  Nr Eng Mirror Member  Done MB/s IOPS Type   Time (active)  Time (remaining)
# ----------------------------------------------------------------------------
#   0   0 0x8201 0x07ff  0.0% 10   100  full      0h 00m 02s  ???
#   0   0 0x8201 0x07ff  1.3% 10   100  full      0h 13m 08s    16h 37m 07s
#
#
# No degrades ready to rebuild found
#
#
#   {"Rebuild": {"33281": ["0", "1", "0x0000", "3.4%", "10", "100", "quick", "0:01:32", "0:43:33"]}}
#
    def __decodeRebuild(self, eng_number):

        for start_idx in range(self.f_length):
            if self.lines[start_idx].find("CLI>rebuild") != -1: break
        start_idx = start_idx + 1

        if start_idx == self.f_length:
            dbg.printDBG2(file_name, "!!!! rebuild status not found from Engine%s" % eng_number)
            return False
        #
        for i in range(start_idx, self.f_length):
            if self.lines[i].find("in this SAN") != -1: break
        start_idx = i + 1
                        
        for i in range(start_idx, self.f_length):   # find the last entry
            if self.lines[i].find("CLI>") != -1: break  # found next CLI command, reached the end of this session
        end_idx = i
#
        engine_info[eng_number]['Rebuild'] = {}

        for i in range (start_idx, end_idx):
            info = self.lines[i].split()
            if info == []: continue
            if info[0].isdigit() == True:
                if len(info) == 12:
                    idx, engine, mid, member, done, mbps, iops, rebuild_type, at0, at1, at2, rt0 = info
                    remain_time = info[11]
                else:
                    idx, engine, mid, member, done, mbps, iops, rebuild_type, at0, at1, at2, rt0, rt1, rt2 = info
                    remain_time = '%s:%s:%s' % (rt0[:-1], rt1[:-1], rt2[:-1])
                mid = str(int(mid, 16))
                active_time = '%s:%s:%s' % (at0[:-1], at1[:-1], at2[:-1])
                engine_info[eng_number]['Rebuild'][mid] = (idx, engine, member, done, mbps, iops, rebuild_type, active_time, remain_time)
#
        if (debug_level >= 4):
            dbg.printDBG4(file_name, "-- print Engine%s rebuild table" % eng_number)
            for mid in sorted(engine_info[eng_number]['Rebuild']):
                dbg.printDBG4(file_name, "---- id=%s, data=%s" % (mid, engine_info[eng_number]['Rebuild'][mid]))
#
#        print eng_number, engine_info[eng_number]['Rebuild']
#
