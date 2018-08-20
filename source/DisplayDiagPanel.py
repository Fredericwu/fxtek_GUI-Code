#!/usr/bin/python
"""
Display Diagnosis Panel

Created by Susan Cheng on 2015-06-18.
Copyright (c) 2015-2017 __Loxoll__. All rights reserved.
"""

import ttk, Tkinter
import tkMessageBox

import time, datetime, os
import ControlEngine, ParseEngineVPD
import functools
import threading, thread
import DisplayMenubar

file_name = os.path.basename(__file__)

WIDTH = 30

class DisplayDiagPanel():

    def __init__(self):
        dbg.printDBG1(file_name, "initiate DisplayDiagPanel")

    def startDisplayDiagPanel(self, c, p):
        self.diag_ptr = Tkinter.Toplevel()
        mainframe_width = (self.diag_ptr.winfo_screenwidth() / 2 - 300)
        mainframe_heigth = (self.diag_ptr.winfo_screenheight() / 2 - 250)
        if engine_number == 2:
            self.diag_ptr.geometry("+%d+%d" % (LLINE, 115))
        else:
            self.diag_ptr.geometry("+%d+%d" % (LLINE, 152))
        self.diag_ptr.protocol("WM_DELETE_WINDOW", self.__CloseHandler)
        self.diag_ptr.title('--- %s Diagnosis ---' % p)
        n = ttk.Notebook(self.diag_ptr)
        n.pack(fill='both', expand='yes')
#
        frame_1 = ttk.Frame(self.diag_ptr)
        frame_2 = ttk.Frame(self.diag_ptr)
        frame_3 = ttk.Frame(self.diag_ptr)
        frame_4 = ttk.Frame(self.diag_ptr)
        frame_1.pack()
        frame_2.pack()
        frame_3.pack()
        frame_4.pack()
        # create the pages
        n.add(frame_1, text='Engine Tools')
        n.add(frame_2, text='GUI Tools')
        n.add(frame_3, text='Switch Tools')
        n.add(frame_4, text='Email Setting')
#       
# Action Buttons (Diagnostic Tools)
#
        p = ttk.Frame(frame_1)            
        b0 = ttk.Button(p, text="Get Current & Primary Trace", width = WIDTH, command=self.__GetEngineTrace_NS)
        b1 = ttk.Button(p, text="Get Engine Cur, Pri & 2nd Trace", width = WIDTH, command=self.__GetEngineTrace)
        b2 = ttk.Button(p, text="Update Engine Microcode", width = WIDTH, command=self.__MicrocodeDownload)
        b3 = ttk.Button(p, text="Engine Trace Analysis", width = WIDTH, command=self.__AnalyzeEngineTrace)
        b4 = ttk.Button(p, text="Save Backup Configuration", width = WIDTH, command=self.__BackupConfiguration)
        b5 = ttk.Button(p, text="Restore Backup Configuration", width = WIDTH, command=self.__RestoreConfiguration)
        b0.grid(row=0, column=0)
        b1.grid(row=1, column=0)
        b2.grid(row=0, column=1)
        b3.grid(row=1, column=1)
        b4.grid(row=0, column=2)
        b5.grid(row=1, column=2)
        p.pack()
#
        p = ttk.Frame(frame_2)            
        b0 = ttk.Button(p, text="Get GUI Diagnostic Trace", width = WIDTH, command=self.__GetTrace)
        b0.grid(row=0, column=0)
        p.pack()
#
#
        p = ttk.Frame(frame_3)            
        b0 = ttk.Button(p, text="Switch Diagnostic Utility", width = WIDTH, command=self.__GetSwitchTrace)
        b0.grid(row=0, column=0)
        p.pack()
#
#
        p = ttk.Frame(frame_4)            
        b0 = ttk.Button(p, text="Configure Email Notification", width = WIDTH, command=self.__SetEmailNotification)
        b0.grid(row=0, column=0)
        p.pack()
#
    def __CloseHandler(self):
        diag_global_ptr[STATUS] = STOPPED
        self.diag_ptr.destroy()

    def liftDisplayDiagPanel(self):
        self.diag_ptr.lift()
#
    def __SubmitButtonClick(self):
        ans = tkMessageBox.askokcancel("Add License", "Do you want to add license with the key =  ??")
        
        if ans != True:
            thread.start_new_thread( tkMessageBox.showinfo, ("Add License", "Action has been cancelled."))
            return False
        else:
            tkMessageBox.showinfo("Add License", "License added successfully.")


    def __NotAvailable(self):
        tkMessageBox.showinfo("Connection Manager", "This function is currently not available.")
#
    def __BackupConfiguration(self):
        d = DisplayMenubar.DisplayMenubar()
        d.SaveBackupFile()
#
    def __RestoreConfiguration(self):
        d = DisplayMenubar.DisplayMenubar()
        d.RestoreConfiguration()
#
    def __MicrocodeDownload(self):
        d = DisplayMenubar.DisplayMenubar()
        d.DownLoadCode()
#
    def __GetTrace(self):
        d = DisplayMenubar.DisplayMenubar()
        d.GetTrace()
#
    def __GetEngineTrace_NS(self):
        d = DisplayMenubar.DisplayMenubar()
        d.GetEngineTrace_NS()
#
    def __GetEngineTrace(self):
        d = DisplayMenubar.DisplayMenubar()
        d.GetEngineTrace()
#
    def __GetSwitchTrace(self):
        d = DisplayMenubar.DisplayMenubar()
        d.GetSwitchTrace()
#
    def __AnalyzeEngineTrace(self):
        d = DisplayMenubar.DisplayMenubar()
        d.AnalyzeEngineTrace()
#        
    def __SetEmailNotification(self):
        d = DisplayMenubar.DisplayMenubar()
        d.SetEmailNotification()    
    
if __name__ == '__main__':
#
# Define Global Variables Here
#
    gui_app= DisplayDiagPanel()
    gui_app.startDisplayDiagPanel()

