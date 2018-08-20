#!/usr/bin/python
"""
Control Diagnostic Module: This module provides all the diagnostic tools.

Created by Susan Cheng on 2014-07-11.
Copyright (c) 2014-2016 __Loxoll__. All rights reserved.
"""

import sys, os, glob
import datetime
import DisplayMenubar

import threading

file_name = os.path.basename(__file__)

threadLock = threading.Lock()
#
# Debug trace executive class, service all debug print related requests 
#
class xDBG(object):

    def __init__(self):
        self.tracepath = './trace/'
        if not os.path.exists(self.tracepath): os.makedirs(self.tracepath)

        # count the .log files
        log_file_count = 0
        for file in glob.glob(os.path.join(self.tracepath, '*.log')): log_file_count += 1     
       
        while log_file_count >= 2: # keep only 10 .log files

            # find the oldest file
            oldest_file, oldest_time = None, None
            for dirpath, dirs, files in os.walk(self.tracepath):
                for filename in files:
                    file_path = os.path.join(dirpath, filename)
                    file_time = os.stat(file_path).st_mtime
                    if file_path.endswith(".log") and (file_time<oldest_time or oldest_time is None):
                        oldest_file, oldest_time = file_path, file_time
            
            # remove the oldest file
            oldest_file = oldest_file[:-4]
            if os.path.isfile(oldest_file+'.log'): os.remove(oldest_file+'.log')
            if os.path.isfile(oldest_file+'.logs'): os.remove(oldest_file+'.logs')
            
            # count the .log files again
            log_file_count = 0
            for file in glob.glob(os.path.join(self.tracepath, '*.log')): log_file_count += 1     

        self.log_file_name = self.tracepath + datetime.datetime.now().strftime('L%Y%m%d%H%M%S')
        if DEVELOPMENT == 0:
            sys.stderr = open(self.log_file_name + ".logs", 'w')
        self.log_file_name = self.log_file_name + '.log'
        self.f = open(self.log_file_name, 'w')
        time_now = datetime.datetime.now().strftime('%Y%m%d-%H:%M:%S.%f')
        self.f.write( "Trace Start : " + time_now + "\n")
        self.f.close()

        self.debug_level_save = 0
#
# Level 0: unconditional message
#
    def printDBG0(self, fn, s):
        time_now = datetime.datetime.now().strftime('%Y%m%d-%H:%M:%S.%f')
        threadLock.acquire()
        self.f = open(self.log_file_name, 'a')
        print >>self.f, "####", time_now, s, " -- ", fn[0:-3]
        self.f.close()
        threadLock.release()
#
# Level 1: initialization and main state changes
#
    def printDBG1(self, fn, s):    
        if (debug_level >= 1):
            time_now = datetime.datetime.now().strftime('%Y%m%d-%H:%M:%S.%f')
            threadLock.acquire()
            self.f = open(self.log_file_name, 'a')
            print >>self.f, ">>>>", time_now, fn[0:-3], ':', s
            self.f.close()
            threadLock.release()
#
# Level 2: modules involved, main logic flow
#           
    def printDBG2(self, fn, s):
        if (debug_level >= 2):
            time_now = datetime.datetime.now().strftime('-%H:%M:%S.%f')
            threadLock.acquire()
            self.f = open(self.log_file_name, 'a')
            print >>self.f, "LV>2", time_now, fn[0:-3], ':', s
            self.f.close()
            threadLock.release()
#
# Level 3: inside modules involved, detail logic flow
#
    def printDBG3(self, fn, s):
        if (debug_level >= 3):
            time_now = datetime.datetime.now().strftime('-%H:%M:%S.%f')
            threadLock.acquire()
            self.f = open(self.log_file_name, 'a')
            print >>self.f, "LV>3", time_now, fn[0:-3], ':', s
            self.f.close()
            threadLock.release()
#
# Level 4: detailed data
#
    def printDBG4(self, fn, s):
        if (debug_level >= 4):
            time_now = datetime.datetime.now().strftime('-%H:%M:%S.%f')
            threadLock.acquire()
            self.f = open(self.log_file_name, 'a')
            print >>self.f, "LV>4", time_now, fn[0:-3], ':', s
            self.f.close()
            threadLock.release()
            
    def ChangeDebugLevel(self, fn, i):
        global debug_level
        threadLock.acquire()
        self.debug_level_save = debug_level
        debug_level = i
        self.f = open(self.log_file_name, 'a')
        print >>self.f, ">>>> change debug level to", debug_level, " -- ", fn[0:-3]
        self.f.close()
        threadLock.release()

    def RestoreDebugLevel(self, fn):
        global debug_level
        threadLock.acquire()
        debug_level = self.debug_level_save
        self.f = open(self.log_file_name, 'a')
        print >>self.f, ">>>> restore debug level to", debug_level, " -- ", fn[0:-3]
        self.f.close()
        threadLock.release()

#
import ControlEmail
import ZipUtility
import tkMessageBox

class xDiagUtility(object):

    def __init__(self):
        pass
#
    def SendTrace(self, type = "LX"):

        # find the latest LX...zip
        zippath = './zip/'
        if not os.path.exists(zippath):
            dbg.printDBG1 (file_name, '!!!no zippath found')
            tkMessageBox.showerror("Send Trace", "No zip directory found!!")
            return False
        prefix = type
        
        # count the LX.....zip files
        zip_file_count = 0
        for file in glob.glob(os.path.join(zippath, prefix+'*.zip')): zip_file_count += 1
        if zip_file_count ==0: 
            dbg.printDBG1 (file_name, '!!!no zip file found')
            tkMessageBox.showerror("Send Trace", "No zip file found!!")
            return False

        # find the newest file
        newest_file, newest_time = None, None
        for dirpath, dirs, files in os.walk(zippath):
            for filename in files:
                file_path = os.path.join(dirpath, filename)
                file_time = os.stat(file_path).st_mtime
                if file_path.endswith(".zip") and file_path.startswith (zippath + prefix) and \
                    (file_time>newest_time or newest_time is None):
                    newest_file, newest_time = file_path, file_time
        # copy file to the root directory as file to send
        file_to_send = newest_file.replace('/', ' ').split()[-1]
        
        es = cfg['General']['MAILTO']
        
        result = tkMessageBox.askokcancel("Send Trace", "zipped trace file %s will be emailed to %s, OK?" % (file_to_send, es))
        
        if result == True:
            p = DisplayMenubar.DisplayMenubar()
            p.GetEmailInfo()            
            t = ControlEmail.xEmail()
            if t.send_zipped_file(email_info, newest_file, file_to_send) == True:    # send the latest diagnostic trace
                tkMessageBox.showinfo("Send Trace", "The zipped trace file has been sent successfully.")
            else:
                tkMessageBox.showerror("Send Trace", "Failed to email the zipped trace file automatically!"+
                "\rPlease find the zip file in ./zip directory and email it manually.")
        else:
            tkMessageBox.showinfo("Send Trace", "Action has been cancelled.")

    def GetTrace(self):
        p = ZipUtility.ZipUtil()
        fs = p.ZipTrace()
        print "fs = ", fs
        dbg.printDBG1(file_name, "Trace file %s created" % fs)
        tkMessageBox.showinfo(title="Get Trace", message= "Diagnostic trace file %s is created." % fs)
#
# time_stamp; file; message; 
#
if __name__ == '__main__':
    p = xDBG()
    file_name = os.path.basename(__file__)
    p.printDBG1(file_name, "debug 1")
    p.printDBG2(file_name, "debug 2")
    p.printDBG3(file_name, "debug 3")
    for i in range (10):
        p.printDBG4(file_name, "debug 4 - %s" % i)
    
    sys.exit()
