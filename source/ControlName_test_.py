"""
Control Name Module

Created by Susan Cheng on 2016-12-30.
Copyright (c) 2015-2017 __Loxoll__. All rights reserved.
"""
#
# This module is designed to service all Name File related functions. Name File contains all the names defined by 
# user. Name File will be associated by Engine PCB Serial Number and matched back when the GUI starts.
#
import ttk, Tkinter
import tkMessageBox

import os, glob, datetime, shutil, zipfile, time
import base64
import hashlib
import ParseEngineVPD

file_name = os.path.basename(__file__)

class xName(object):
    def __init__(self):
        dbg.printDBG2(file_name, "initiate xName")
#
    def SaveCurrentName(self, i):
        for sn in engine_info[i]['ClusterSN']:
            self.__SaveName(i, "E%s.nam" % sn)
        tkMessageBox.showinfo("Engine Data", "Engine%s's Name Info has been saved to all clustered engines!" % i)
#
    def __SaveName(self, i, file_name):
        datapath = './data/'
        if not os.path.exists(datapath): os.makedirs(datapath)
        data_file_name = datapath + file_name

        f = open(data_file_name, 'w')

        for nid in name_info[i]:
            f.write( base64.b64encode(nid) + "\n")
            f.write( base64.b64encode(name_info[i][nid]) + "\n")    # make new name file
#
        f.close()
# Add hash number to end of the file
        h = hashlib.md5()
        f = open(data_file_name, 'rb')
        h.update(f.read())
        f = open(data_file_name, 'a')
        f.write(h.hexdigest())
        f.close()
#
    def UpdateCurrentName(self, i):
        pass
#
    def ReadSavedName(self, i):
        datapath = './data/'
        file_name = "E%s.nam" % engine_info[i]['SerialNumber']
        data_file_name = datapath + file_name

        if not os.path.isfile(data_file_name): return True    
        if self.__CheckHash(file_name) != True: return False
        
        lines = []
        f = open(datapath+file_name, 'r')
        lines = f.readlines()
        f.close()

        if lines == [] or len(lines) < 3: return True

        for j in range (0, len(lines)-1, 2):
            name_info[i][base64.b64decode(lines[j][:-1])] = base64.b64decode(lines[j+1][:-1])
#
    def __CheckHash(self, file):
        datapath = './data/'
        f = open(datapath+file, 'r')
        lines = f.readlines()
        f.close()

        # Verify the hash number
        f = open("./data/temp.dat", 'w')
        for i in range (len(lines)-1):
            f.write( lines[i])
        f.close()
        #
        h = hashlib.md5()
        f = open("./data/temp.dat", 'rb')
        h.update(f.read())
        s = h.hexdigest()
        f.close()
        os.remove("./data/temp.dat")
        #        
        if lines[len(lines)-1] == s: return True
        else: return False
#

    def DeleteSavedName(self, i):
        pass
#

if __name__ == '__main__':
    
    print "Save Name File"
    run()

    raw_input('Done')
    sys.exit()

