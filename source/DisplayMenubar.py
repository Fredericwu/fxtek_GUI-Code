#!/usr/bin/python
# coding: utf8
"""
DisplayMenubar.py

Created by Susan Cheng on 2015-06-07.
Copyright (c) 2015-2017 __Loxoll__. All rights reserved.
"""

import ttk, Tkinter
import tkMessageBox

import os, datetime, shutil, zipfile
import base64
import hashlib
import ControlEngine
import thread
import ControlDiag
import ControlTCP
import ControlSwitch
import ControlJSON
import ZipUtility, ControlEmail

file_name = os.path.basename(__file__)

class DisplayMenubar():
    def __init__(self):
        dbg.printDBG1(file_name, "initiate DisplayMenubar")
        self.RSCwindow_started = 0
        self.DLCwindow_started = 0
        self.SENwindow_started = 0
        self.SITwindow_started = 0
        self.TCPwindow_started = 0
        self.APIwindow_started = 0
        self.LPSwindow_started = 0
        self.JSONwindow_started = 0
        self.AETwindow_started = 0
        self.menu_enter = "NO"

    def startDisplayMenubar(self, root):
        menubar = Tkinter.Menu(root)

        # create Diagnostic Tools pulldown menu, and add it to the menu bar
        toolmenu = Tkinter.Menu(menubar, tearoff=0)
#        toolmenu.add_command(label="Get GUI Diagnostic Trace", command=self.__GetTrace, state=Tkinter.DISABLED)
#        toolmenu.add_command(label="Send GUI Trace", command=self.__SendTrace, state=Tkinter.DISABLED)
        toolmenu.add_command(label="Get GUI Diagnostic Trace", command=self.GetTrace)
        toolmenu.add_command(label="Send GUI Trace", command=self.__SendTrace)
        toolmenu.add_command(label="Get Engine Diagnostic Trace (Current, Primary, & Secondary)", command=self.GetEngineTrace)
        toolmenu.add_command(label="Get Engine Diagnostic Trace (Current & Primary)", command=self.GetEngineTrace_NS)
        toolmenu.add_command(label="Send Engine Trace", command=self.__SendEngineTrace)
        toolmenu.add_command(label="Update Engine Microcode", command=self.DownLoadCode)
#        toolmenu.add_command(label="Email Notification", command=self.__UnderConstruction, state=Tkinter.DISABLED)
        toolmenu.add_command(label="Configure Email Notification", command=self.SetEmailNotification)
        toolmenu.add_command(label="Switch Diagnostic Utility", command=self.GetSwitchTrace)
        toolmenu.add_command(label="Backup HA-AP Configuration", command=self.SaveBackupFile)
        toolmenu.add_command(label="Restore HA-AP Configuration", command=self.RestoreConfiguration)
        toolmenu.add_command(label="Engine Trace Analysis", command=self.AnalyzeEngineTrace)
        toolmenu.add_separator()
        toolmenu.add_command(label="Exit", command=root.quit)
        menubar.add_cascade(label="Diagnostic Tools", menu=toolmenu)

        # create IOG pulldown menus
        """
        iogmenu = Tkinter.Menu(menubar, tearoff=0)
        iogmenu.add_command(label="Start           ", command=self.__UnderConstruction)
        iogmenu.add_command(label="Stop            ", command=self.__UnderConstruction)
        menubar.add_cascade(label="IO Generator", menu=iogmenu)
        """

        # create Development Tools menus
        if DEVELOPMENT == 1:
            iogmenu = Tkinter.Menu(menubar, tearoff=0)
            iogmenu.add_command(label="TCP Server (for test)", command=self.__TCPserver)
            iogmenu.add_command(label="API Command Tester", command=self.__APItester)
            iogmenu.add_command(label="Lapresse test", command=self.__LapresseTest)
            iogmenu.add_command(label="JSON Tester", command=self.__JSONtester)
            iogmenu.add_command(label="Exit            ", command=root.quit)
            menubar.add_cascade(label="Development Utility", menu=iogmenu)

        # create Help pulldown menus
        helpmenu = Tkinter.Menu(menubar, tearoff=0)
        helpmenu.add_command(label="About", command=self.__About)
        menubar.add_cascade(label="Help", menu=helpmenu)

        # display the menu
        root.config(menu=menubar)
        
    def __UnderConstruction(self):
        thread.start_new_thread( tkMessageBox.showinfo, ("Menu Bar", "This option is currently under construction."))

#
    def __TCPserver(self):
        if self.TCPwindow_started == 1:
            dbg.printDBG2(file_name, "TCP test window already start, just bring to front")
            self.tcpw_ptr.lift()
            return
        
        self.TCPwindow_started = 1
        self.tcpw_ptr = Tkinter.Toplevel()
        #mainframe_width = (self.tcpw_ptr.winfo_screenwidth() / 2 - 300)
        #mainframe_heigth = (self.tcpw_ptr.winfo_screenheight() / 2 - 250)
        self.tcpw_ptr.geometry("+%d+%d" % (LLINE, 152))
        self.tcpw_ptr.protocol("WM_DELETE_WINDOW", self.__tcpCloseHandler)
        self.tcpw_ptr.title('--- TCP Server Window ---')

        p = ttk.Panedwindow(self.tcpw_ptr, orient=Tkinter.VERTICAL)
        # first pane, which would get widgets gridded into it:
        f1 = ttk.Labelframe(p, text="TCP Server Configuration", width=300, height=200 )
        f2 = ttk.Labelframe(p, text="Execution", width=300, height=200);
        p.add(f1)
        p.add(f2)
        p.pack()
#
# TCP Server Configuration
        l1 = Tkinter.Label(f1, text="Server IP", width=20, height=1, bg = 'light gray')
        l2 = Tkinter.Label(f1, text="Port", width=20, height=1, bg = 'light gray')
        self.server = Tkinter.Entry(f1, bd = 2, bg = 'light gray', width = 30)
        self.port = Tkinter.Entry(f1, bd = 2, bg = 'light gray', width = 30)
        l1.grid(row=0, column=0)
        l2.grid(row=1, column=0)
        self.server.grid(row=0, column=1)
        self.port.grid(row=1, column=1)
#
# Action Buttons
        b1 = ttk.Button(f2, text="Save Configuration", width = 16, command=self.__SaveTCP)
        b2 = ttk.Button(f2, text="Start TCP Server", width = 16, command=self.__tcpServerOn)
        b3 = ttk.Button(f2, text="Exit", width = 16, command=self.__tcpCloseHandler)
        b1.grid(row=0, column=0)
        b2.grid(row=0, column=1)
        b3.grid(row=0, column=2)
# Get Saved Data
        self.menu_enter = "YES"
        self.GetTCPInfo()
#
    def __tcpServerOn(self):
        dbg.printDBG1(file_name, "start the TCP Server")

        ans = tkMessageBox.askokcancel("TCP Server", "Start the TCP Server, OK?")        
        if ans != True:
            thread.start_new_thread( tkMessageBox.showinfo, ("TCP Server", "Action has been cancelled."))
            return False

        self.p = ControlTCP.xTCP()
        thread.start_new_thread( self.p.startTCPserver, ()) # should kill the thread... when exit!!!!
#
    def __tcpCloseHandler(self):
        tcp_server_stop = 1
        self.TCPwindow_started = 0
        self.tcpw_ptr.destroy()
    
    def __SendEngineTrace(self):
        dbg.printDBG1(file_name, "start send trace process")

        ans = tkMessageBox.askokcancel("Send Engine Trace", "It will take a few seconds to send Engines' trace, OK?")        
        if ans != True:
            thread.start_new_thread( tkMessageBox.showinfo, ("Send Trace", "Action has been cancelled."))
            return False

        du = ControlDiag.xDiagUtility()
        du.SendTrace("HA")  # HA is Engine trace

#
    def __APItester(self):
        if self.APIwindow_started == 1:
            dbg.printDBG2(file_name, "API tester already start, just bring to front")
            self.apiw_ptr.lift()
            return
        
        self.APIwindow_started = 1
        self.apiw_ptr = Tkinter.Toplevel()
        mainframe_width = (self.apiw_ptr.winfo_screenwidth() / 2 - 300)
        mainframe_heigth = (self.apiw_ptr.winfo_screenheight() / 2 - 250)
        self.apiw_ptr.geometry("+%d+%d" % (LLINE, 152))
        self.apiw_ptr.protocol("WM_DELETE_WINDOW", self.__apiCloseHandler)
        self.apiw_ptr.title('--- API Tester ---')

        p = ttk.Panedwindow(self.apiw_ptr, orient=Tkinter.VERTICAL)
        # first pane, which would get widgets gridded into it:
        f1 = ttk.Labelframe(p, text="TCP Client Configuration", width=300, height=200 )
        f2 = ttk.Labelframe(p, text="API Command #1", width=300, height=200 )
        f3 = ttk.Labelframe(p, text="API Command #2", width=300, height=200);
        f4 = ttk.Labelframe(p, text="API Command #3", width=300, height=200);
        f5 = ttk.Labelframe(p, text="Execution", width=300, height=200);
        p.add(f1)
        p.add(f2)
        p.add(f3)
        p.add(f4)
        p.add(f5)
        p.pack()
#
# TCP Server Configuration
        l1 = Tkinter.Label(f1, text="Server IP", width=20, height=1, bg = 'light gray')
        l2 = Tkinter.Label(f1, text="Port", width=20, height=1, bg = 'light gray')
        self.server = Tkinter.Entry(f1, bd = 2, bg = 'light gray', width = 30)
        self.port = Tkinter.Entry(f1, bd = 2, bg = 'light gray', width = 30)
        l1.grid(row=0, column=0)
        l2.grid(row=1, column=0)
        self.server.grid(row=0, column=1)
        self.port.grid(row=1, column=1)
#
# API 1
        l1 = Tkinter.Label(f2, text="Request Code (4 bytes hex)", width=28, height=1, bg = 'light gray')
        l2 = Tkinter.Label(f2, text="First Parameter (4 bytes hex)", width=28, height=1, bg = 'light gray')
        l3 = Tkinter.Label(f2, text="Second Parameter (4 bytes hex)", width=28, height=1, bg = 'light gray')
        l4 = Tkinter.Label(f2, text="Sequence Number (2 bytes hex)", width=28, height=1, bg = 'light gray')
        l5 = Tkinter.Label(f2, text="Payload Byte Count (2 bytes hex)", width=28, height=1, bg = 'light gray')
        l6 = Tkinter.Label(f2, text="Payload Data (8 bytes hex)", width=28, height=1, bg = 'light gray')
        self.slot1_1 = Tkinter.Entry(f2, bd = 2, bg = 'light gray', width = 30)
        self.slot1_2 = Tkinter.Entry(f2, bd = 2, bg = 'light gray', width = 30)
        self.slot1_3 = Tkinter.Entry(f2, bd = 2, bg = 'light gray', width = 30)
        self.slot1_4 = Tkinter.Entry(f2, bd = 2, bg = 'light gray', width = 30)
        self.slot1_5 = Tkinter.Entry(f2, bd = 2, bg = 'light gray', width = 30)
        self.slot1_6 = Tkinter.Entry(f2, bd = 2, bg = 'light gray', width = 30)
        l1.grid(row=0, column=0)
        l2.grid(row=1, column=0)
        l3.grid(row=2, column=0)
        l4.grid(row=3, column=0)
        l5.grid(row=4, column=0)
        l6.grid(row=5, column=0)
        self.slot1_1.grid(row=0, column=1)
        self.slot1_2.grid(row=1, column=1)
        self.slot1_3.grid(row=2, column=1)
        self.slot1_4.grid(row=3, column=1)
        self.slot1_5.grid(row=4, column=1)
        self.slot1_6.grid(row=5, column=1)
#
# API 2
        #
        l1 = Tkinter.Label(f3, text="Request Code (4 bytes hex)", width=28, height=1, bg = 'light gray')
        l2 = Tkinter.Label(f3, text="First Parameter (4 bytes hex)", width=28, height=1, bg = 'light gray')
        l3 = Tkinter.Label(f3, text="Second Parameter (4 bytes hex)", width=28, height=1, bg = 'light gray')
        l4 = Tkinter.Label(f3, text="Sequence Number (2 bytes hex)", width=28, height=1, bg = 'light gray')
        l5 = Tkinter.Label(f3, text="Payload Byte Count (2 bytes hex)", width=28, height=1, bg = 'light gray')
        l6 = Tkinter.Label(f3, text="Payload Data (8 bytes hex)", width=28, height=1, bg = 'light gray')
        self.slot2_1 = Tkinter.Entry(f3, bd = 2, bg = 'light gray', width = 30)
        self.slot2_2 = Tkinter.Entry(f3, bd = 2, bg = 'light gray', width = 30)
        self.slot2_3 = Tkinter.Entry(f3, bd = 2, bg = 'light gray', width = 30)
        self.slot2_4 = Tkinter.Entry(f3, bd = 2, bg = 'light gray', width = 30)
        self.slot2_5 = Tkinter.Entry(f3, bd = 2, bg = 'light gray', width = 30)
        self.slot2_6 = Tkinter.Entry(f3, bd = 2, bg = 'light gray', width = 30)
        l1.grid(row=0, column=0)
        l2.grid(row=1, column=0)
        l3.grid(row=2, column=0)
        l4.grid(row=3, column=0)
        l5.grid(row=4, column=0)
        l6.grid(row=5, column=0)
        self.slot2_1.grid(row=0, column=1)
        self.slot2_2.grid(row=1, column=1)
        self.slot2_3.grid(row=2, column=1)
        self.slot2_4.grid(row=3, column=1)
        self.slot2_5.grid(row=4, column=1)
        self.slot2_6.grid(row=5, column=1)
#
# API 3
        #
        l1 = Tkinter.Label(f4, text="Request Code (4 bytes hex)", width=28, height=1, bg = 'light gray')
        l2 = Tkinter.Label(f4, text="First Parameter (4 bytes hex)", width=28, height=1, bg = 'light gray')
        l3 = Tkinter.Label(f4, text="Second Parameter (4 bytes hex)", width=28, height=1, bg = 'light gray')
        l4 = Tkinter.Label(f4, text="Sequence Number (2 bytes hex)", width=28, height=1, bg = 'light gray')
        l5 = Tkinter.Label(f4, text="Payload Byte Count (2 bytes hex)", width=28, height=1, bg = 'light gray')
        l6 = Tkinter.Label(f4, text="Payload Data (8 bytes hex)", width=28, height=1, bg = 'light gray')
        self.slot3_1 = Tkinter.Entry(f4, bd = 2, bg = 'light gray', width = 30)
        self.slot3_2 = Tkinter.Entry(f4, bd = 2, bg = 'light gray', width = 30)
        self.slot3_3 = Tkinter.Entry(f4, bd = 2, bg = 'light gray', width = 30)
        self.slot3_4 = Tkinter.Entry(f4, bd = 2, bg = 'light gray', width = 30)
        self.slot3_5 = Tkinter.Entry(f4, bd = 2, bg = 'light gray', width = 30)
        self.slot3_6 = Tkinter.Entry(f4, bd = 2, bg = 'light gray', width = 30)
        l1.grid(row=0, column=0)
        l2.grid(row=1, column=0)
        l3.grid(row=2, column=0)
        l4.grid(row=3, column=0)
        l5.grid(row=4, column=0)
        l6.grid(row=5, column=0)
        self.slot3_1.grid(row=0, column=1)
        self.slot3_2.grid(row=1, column=1)
        self.slot3_3.grid(row=2, column=1)
        self.slot3_4.grid(row=3, column=1)
        self.slot3_5.grid(row=4, column=1)
        self.slot3_6.grid(row=5, column=1)
#
# Action Buttons
        b1 = ttk.Button(f5, text="Save Configuration", width = 20, command=self.__SaveAPI)
        b2 = ttk.Button(f5, text="Send API Commands", width = 20, command=self.__SendAPI)        
        b3 = ttk.Button(f5, text="Exit", width = 20, command=self.__apiCloseHandler)
        b1.grid(row=0, column=0)
        b2.grid(row=0, column=1)
        b3.grid(row=0, column=2)
#
# Get Saved Data
        self.menu_enter = "YES"
        self.GetAPIInfo()
#
    def __LapresseTest(self):
        if self.LPSwindow_started == 1:
            dbg.printDBG2(file_name, "LPS test already start, just bring to front")
            self.lpsw_ptr.lift()
            return
        
        self.LPSwindow_started = 1
        self.lpsw_ptr = Tkinter.Toplevel()
        mainframe_width = (self.lpsw_ptr.winfo_screenwidth() / 2 - 300)
        mainframe_heigth = (self.lpsw_ptr.winfo_screenheight() / 2 - 250)
        self.lpsw_ptr.geometry("+%d+%d" % (LLINE, 152))
        self.lpsw_ptr.protocol("WM_DELETE_WINDOW", self.__lpsCloseHandler)
        self.lpsw_ptr.title('--- Lapresse Test ---')

        p = ttk.Panedwindow(self.lpsw_ptr, orient=Tkinter.VERTICAL)
        # first pane, which would get widgets gridded into it:
        f1 = ttk.Labelframe(p, text="TCP Client Configuration", width=300, height=200 )
        f5 = ttk.Labelframe(p, text="Execution", width=300, height=200);
        p.add(f1)
        p.add(f5)
        p.pack()
#
# TCP Server Configuration
        l1 = Tkinter.Label(f1, text="Server IP", width=20, height=1, bg = 'light gray')
        l2 = Tkinter.Label(f1, text="Port", width=20, height=1, bg = 'light gray')
        self.server = Tkinter.Entry(f1, bd = 2, bg = 'light gray', width = 30)
        self.port = Tkinter.Entry(f1, bd = 2, bg = 'light gray', width = 30)
        l1.grid(row=0, column=0)
        l2.grid(row=1, column=0)
        self.server.grid(row=0, column=1)
        self.port.grid(row=1, column=1)
#
#
# Action Buttons
        b1 = ttk.Button(f5, text="Save Configuration", width = 20, command=self.__SaveLPS)
        b2 = ttk.Button(f5, text="Send LPS Commands", width = 20, command=self.__SendLPS)        
        b3 = ttk.Button(f5, text="Exit", width = 20, command=self.__lpsCloseHandler)
        b1.grid(row=0, column=0)
        b2.grid(row=0, column=1)
        b3.grid(row=0, column=2)
#
# Get Saved Data
        self.menu_enter = "YES"
        self.GetLPSInfo()
#
    def __JSONtester(self):
        if self.JSONwindow_started == 1:
            dbg.printDBG2(file_name, "JSON tester already start, just bring to front")
            self.jsonw_ptr.lift()
            return
        
        self.JSONwindow_started = 1
        self.jsonw_ptr = Tkinter.Toplevel()
        mainframe_width = (self.jsonw_ptr.winfo_screenwidth() / 2 - 300)
        mainframe_heigth = (self.jsonw_ptr.winfo_screenheight() / 2 - 250)
        self.jsonw_ptr.geometry("+%d+%d" % (LLINE, 152))
        self.jsonw_ptr.protocol("WM_DELETE_WINDOW", self.__jsonCloseHandler)
        self.jsonw_ptr.title('--- JSON Tester ---')

        p = ttk.Panedwindow(self.jsonw_ptr, orient=Tkinter.VERTICAL)
        # first pane, which would get widgets gridded into it:
        f1 = ttk.Labelframe(p, text="Python to JSON Structure", width=300, height=200 )
        f2 = ttk.Labelframe(p, text="Execution", width=300, height=200);
        p.add(f1)
        p.add(f2)
        p.pack()
#
# Python to JSON conversion 
        l1 = Tkinter.Label(f1, text="Python Directory 0", width=20, height=1, bg = 'light gray')
        l2 = Tkinter.Label(f1, text="Python Directory 1", width=20, height=1, bg = 'light gray')
        self.dir0 = Tkinter.Entry(f1, bd = 2, bg = 'light gray', width = 30)
        self.dir1 = Tkinter.Entry(f1, bd = 2, bg = 'light gray', width = 30)
        l1.grid(row=0, column=0)
        l2.grid(row=1, column=0)
        self.dir0.grid(row=0, column=1)
        self.dir1.grid(row=1, column=1)
#
# Action Buttons
        b1 = ttk.Button(f2, text="Save Configuration", width = 20, command=self.__SaveJSON)
        b2 = ttk.Button(f2, text="Convert to JSON", width = 20, command=self.__SendJSON)        
        b3 = ttk.Button(f2, text="Exit", width = 20, command=self.__jsonCloseHandler)
        b1.grid(row=0, column=0)
        b2.grid(row=0, column=1)
        b3.grid(row=0, column=2)
#
# Get Saved Data
        self.menu_enter = "YES"
        self.GetJSONinfo()
#
    def __SendAPI(self):
        ans = tkMessageBox.askokcancel("Send API", 
            "Have you saved your change of API Info Table, and want to send the API?")
        
        if ans != True:
            thread.start_new_thread( tkMessageBox.showinfo, ("Send API", "Action has been cancelled."))
            return False

        t = ControlTCP.xTCP()
        t.sendAPI()
#
    def __SendLPS(self):
        ans = tkMessageBox.askokcancel("Send LPS", 
            "Have you saved your change of LPS Info Table, and want to send the cmd?")
        
        if ans != True:
            thread.start_new_thread( tkMessageBox.showinfo, ("Send LPS", "Action has been cancelled."))
            return False

        t = ControlTCP.xTCP()
        t.sendLPS()
#
    def __SendJSON(self):
        ans = tkMessageBox.askokcancel("Send JSON", 
            "Have you saved your change of JSON Info Table, and want to convert the Python directory to JSON?")
        
        if ans != True:
            thread.start_new_thread( tkMessageBox.showinfo, ("Send JSON", "Action has been cancelled."))
            return False
            
        t = ControlJSON.xJSON()
        if JSON_info["dir0"] != "": t.ConvertToJSON(JSON_info["dir0"])
        print "----------"
        if JSON_info["dir1"] != "": t.ConvertToJSON(JSON_info["dir1"])
#
    def __About(self):
        thread.start_new_thread( tkMessageBox.showinfo, ("Help", "HA-AP GUI Version 1.0"))

    def __SendTrace(self):
        dbg.printDBG1(file_name, "start send trace process")
        ans = tkMessageBox.askokcancel("Send Trace", "It will take a few seconds to send GUI trace, OK?")        
        if ans != True:
            thread.start_new_thread( tkMessageBox.showinfo, ("Send Trace", "Action has been cancelled."))
            return False
        du = ControlDiag.xDiagUtility()
        du.SendTrace("LX")  # LX is GUI trace
#
    def __SendEngineTrace(self):
        dbg.printDBG1(file_name, "start send trace process")

        ans = tkMessageBox.askokcancel("Send Engine Trace", "It will take a few seconds to send Engines' trace, OK?")        
        if ans != True:
            thread.start_new_thread( tkMessageBox.showinfo, ("Send Trace", "Action has been cancelled."))
            return False

        du = ControlDiag.xDiagUtility()
        du.SendTrace("HA")  # HA is Engine trace

    def GetTrace(self):
        dbg.printDBG1(file_name, "start get trace process")

        ans = tkMessageBox.askokcancel("Get Trace", "It will take a couple of seconds to prepare GUI trace, OK?")        
        if ans != True:
            thread.start_new_thread( tkMessageBox.showinfo, ("Get Trace", "Action has been cancelled."))
            return False

        du = ControlDiag.xDiagUtility()
        du.GetTrace()
#        thread.start_new_thread( du.GetTrace, ())
#
    def SaveBackupFile(self):
        dbg.printDBG1(file_name, "Save backup file for all available engines")

        ans = tkMessageBox.askokcancel("Save Backup File", "It will take a few seconds to save all engine's configuration files, OK?")        
        if ans != True:
            thread.start_new_thread( tkMessageBox.showinfo, ("Save Backup File", "Action has been cancelled."))
            return False

        relevant_path = './data/'
#        if os.path.exists(relevant_path): shutil.rmtree (relevant_path)
#
        t = ControlEngine.xEngine()

        for i in range(engine_number):
            if current_engine[i][0] == 'off': continue
            
            result = t.BackupConfiguration( i)
            if result == False:
                tkMessageBox.showinfo("Save Backup File", "Engine%s backup configuration failed" % i)
                return False
            tkMessageBox.showinfo("Save Backup File", "Engine%s's backup configuration file created successfully!" % i)
#
    def GetEngineTrace(self):
        dbg.printDBG1(file_name, "start get engine trace process")

        ans = tkMessageBox.askokcancel("Get Engine Trace", "It will take a few seconds to get engines' trace, OK?")        
        if ans != True:
            thread.start_new_thread( tkMessageBox.showinfo, ("Get Engine Trace", "Action has been cancelled."))
            return False

        relevant_path = './trace/'
#        if os.path.exists(relevant_path): shutil.rmtree (relevant_path)
#
        t = ControlEngine.xEngine()

        for i in range(engine_number):
            if current_engine[i][0] == 'off': continue
            
            if t.SetPrepTrace( i, "trace") == True:
                t.saveTrace( i, "trace")
#               tkMessageBox.showinfo("Get Engine Trace", "Got coredump trace.")

            if t.SetPrepTrace( i, "coredump primary all") == True:
                t.saveTrace( i, "primary")
#               tkMessageBox.showinfo("Get Engine Trace", "Got primary.")

            if t.SetPrepTrace( i, "coredump secondary all") == True:
                t.saveTrace( i, "secondary")
#               tkMessageBox.showinfo("Get Engine Trace", "Got secondary.")
        
        zippath = './zip/'
        included_extenstions = ['txt'];
        if not os.path.exists(zippath): os.makedirs(zippath)
        zip_file_name = zippath + datetime.datetime.now().strftime('HA%Y%m%d%H%M%S.zip')
        zip_trace = zipfile.ZipFile(zip_file_name, 'w')
        
        file_names = [fn for fn in os.listdir(relevant_path) if any([fn.endswith(ext) for ext in included_extenstions])];
        
        for fn in file_names:
            shutil.move ("%s/%s" % (relevant_path, fn), "./%s" % fn)
            zip_trace.write(fn)
            os.remove (fn)            
        
#        shutil.rmtree (relevant_path)
        tkMessageBox.showinfo("Get Engine Trace", "Get Engine Trace completed with zip file %s created!" % zip_file_name)
#
    def GetEngineTrace_NS(self):
        dbg.printDBG1(file_name, "start get engine trace process (no secondary)")

        ans = tkMessageBox.askokcancel("Get Engine Trace (Current & Primary)", "It will take a few seconds to get engines' trace, OK?")        
        if ans != True:
            thread.start_new_thread( tkMessageBox.showinfo, ("Get Engine Trace (Current & Primary)", "Action has been cancelled."))
            return False

        relevant_path = './trace/'
#        if os.path.exists(relevant_path): shutil.rmtree (relevant_path)
#
        t = ControlEngine.xEngine()

        for i in range(engine_number):
            if current_engine[i][0] == 'off': continue
            
            if t.SetPrepTrace( i, "trace") == True:
                t.saveTrace( i, "trace")
#               tkMessageBox.showinfo("Get Engine Trace", "Got coredump trace.")

            if t.SetPrepTrace( i, "coredump primary all") == True:
                t.saveTrace( i, "primary")
#               tkMessageBox.showinfo("Get Engine Trace", "Got primary.")

        zippath = './zip/'
        included_extenstions = ['txt'];
        if not os.path.exists(zippath): os.makedirs(zippath)
        zip_file_name = zippath + datetime.datetime.now().strftime('HA%Y%m%d%H%M%S_NS.zip')
        zip_trace = zipfile.ZipFile(zip_file_name, 'w')
        
        file_names = [fn for fn in os.listdir(relevant_path) if any([fn.endswith(ext) for ext in included_extenstions])];
        
        for fn in file_names:
            shutil.move ("%s/%s" % (relevant_path, fn), "./%s" % fn)
            zip_trace.write(fn)
            os.remove (fn)            
        
#        shutil.rmtree (relevant_path)
        tkMessageBox.showinfo("Get Engine Trace (Current & Primary)", "Get Engine Trace completed with zip file %s created!" % zip_file_name)
#
#
    def __rscCloseHandler(self):
        self.RSCwindow_started = 0
        self.rscw_ptr.destroy()

    def __dlcCloseHandler(self):
        self.DLCwindow_started = 0
        self.dlcw_ptr.destroy()
        
    def __senCloseHandler(self):
        self.SENwindow_started = 0
        self.senw_ptr.destroy()
    #        
    def __sitCloseHandler(self):
        self.SITwindow_started = 0
        self.sitw_ptr.destroy()

    def __apiCloseHandler(self):
        self.APIwindow_started = 0
        self.apiw_ptr.destroy()
#
    def __lpsCloseHandler(self):
        self.LPSwindow_started = 0
        self.lpsw_ptr.destroy()
#
    def __jsonCloseHandler(self):
        self.JSONwindow_started = 0
        self.jsonw_ptr.destroy()
#
    def __aetCloseHandler(self):
        self.AETwindow_started = 0
        self.aetw_ptr.destroy()
#
#   self.dlcw_ptr
#                       p
#       f1                              f2     
#           f1_1                            f2_1
#               c1      c2                      c1
#       p_1                             P_2
#           f1_2                            f2_2
#               pb                                b1  b2
#
    def DownLoadCode(self):
        if self.DLCwindow_started == 1:
            dbg.printDBG2(file_name, "DLC window already start, just bring to front")
            self.dlcw_ptr.lift()
            return
        
        self.DLCwindow_started = 1
        self.dlcw_ptr = Tkinter.Toplevel()
        mainframe_width = (self.dlcw_ptr.winfo_screenwidth() / 2 - 300)
        mainframe_heigth = (self.dlcw_ptr.winfo_screenheight() / 2 - 250)
        self.dlcw_ptr.geometry("+%d+%d" % (LLINE, 152))
        self.dlcw_ptr.protocol("WM_DELETE_WINDOW", self.__dlcCloseHandler)
        self.dlcw_ptr.title('--- Download Microcode ---')

        p = ttk.Panedwindow(self.dlcw_ptr, orient=Tkinter.HORIZONTAL)
        # first pane, which would get widgets gridded into it:
        f1 = ttk.Labelframe(p, width=120, height=200 )
        f2 = ttk.Labelframe(p, width=300, height=200); # second pane
        p.add(f1)
        p.add(f2)
        p.pack()
        p_1 = ttk.Panedwindow(f1, orient=Tkinter.VERTICAL)
        f1_1 = ttk.Labelframe(p_1, text='Engine Selection', width = 300, height=200 )
        f1_2 = ttk.Labelframe(p_1, text='Progress Bar', width=300, height=200); # second pane
        p_1.add(f1_1)
        p_1.add(f1_2)
        p_1.pack()
        p_2 = ttk.Panedwindow(f2, orient=Tkinter.VERTICAL)
        f2_1 = ttk.Labelframe(p_2, text='Microcode Selection', width = 300, height=200 )
        f2_2 = ttk.Labelframe(p_2, text='Action', width=300, height=200); # second pane
        p_2.add(f2_1)
        p_2.add(f2_2)
        p_2.pack()
#
# Engine Selection
        self.selected_engine = [0 for x in range(engine_number)]
        for i in range (0, engine_number): self.selected_engine[i] = Tkinter.IntVar()
        for i in range (0, engine_number/2):
            c1 = Tkinter.Checkbutton(f1_1, text = "E"+str(i*2)+": "+cfg["Engine"+str(i*2)]['IP'], variable = self.selected_engine[i*2], \
                         onvalue = 1, offvalue = 0, height=2, width = 20, bg = 'light gray', justify=Tkinter.LEFT)
            c2 = Tkinter.Checkbutton(f1_1, text = "E"+str(i*2+1)+": "+cfg["Engine"+str(i*2+1)]['IP'], variable = self.selected_engine[i*2+1], \
                         onvalue = 1, offvalue = 0, height=2, width = 20, bg = 'light gray', justify=Tkinter.LEFT)
            c1.grid(row=i, column=0)
            c2.grid(row=i, column=1)
# Progress Bar
        self.pb = ttk.Progressbar(f1_2, orient='horizontal', mode='determinate')
        self.pb.pack(expand=True, fill=Tkinter.BOTH, side=Tkinter.TOP)
       
# Microcode Selection
        self.MODES =[]
        #
        for dirpath, dirs, files in os.walk('./mcode/'):
            i = 0
            for filename in files:
                if filename[-3:] != "bin": continue
                self.MODES.append((filename, "%s" % i))
                i += 1
        self.v = Tkinter.StringVar()
        self.v.set("0") # initialize

        for text, mode in self.MODES:
            r = Tkinter.Radiobutton(f2_1, text=text, variable=self.v, value=mode, bg = 'light gray')
            r.pack(anchor=Tkinter.W)
                
# Action Buttons
        b1 = ttk.Button(f2_2, text="Cancel", width = 20, command=self.__dlcCloseHandler)
        b2 = ttk.Button(f2_2, text="Confirm", width = 20, command=self.__ConfirmDownload)
        b1.grid(row=0, column=0)
        b2.grid(row=0, column=1)
        
    def __ConfirmDownload(self):        
        self.has_download = 0
        
        for text, mode in self.MODES:
            if mode == self.v.get(): break

        result = tkMessageBox.askokcancel("Download Microcode",
            "Starting to download microcode \"%s\", OK?" % text)
        if result != True: return
            
        t = ControlEngine.xEngine()
        for i in range (0, engine_number):
            if self.selected_engine[i].get() == 1:
                if t.downloadCode(i, text) == GOOD:
                    self.has_download = 1
                else:
                    thread.start_new_thread( tkMessageBox.showerror, ("Download Microcode", 
                        "FAILED to download microcode on engine %s" % cfg['Engine'+str(i)]['IP']))
            
        if self.has_download == 1:
            self.pb.start(600)
            self.pb.after(60000, self.__StopPB)   
            thread.start_new_thread( tkMessageBox.showinfo, ("Download Microcode", 
                "Microcode is updating....WARNING: DO NOT TURN OFF THE ENGINE POWER!"))
        #
        else:
            thread.start_new_thread( tkMessageBox.showinfo, ("Download Microcode", 
                "No Engine has been downloaded with new microcode!"))
#
#
    def RestoreConfiguration(self):
        if self.RSCwindow_started == 1:
            dbg.printDBG2(file_name, "RSC window already start, just bring to front")
            self.rscw_ptr.lift()
            return
        
        self.RSCwindow_started = 1
        self.rscw_ptr = Tkinter.Toplevel()
        mainframe_width = (self.rscw_ptr.winfo_screenwidth() / 2 - 300)
        mainframe_heigth = (self.rscw_ptr.winfo_screenheight() / 2 - 250)
        self.rscw_ptr.geometry("+%d+%d" % (LLINE, 152))
        self.rscw_ptr.protocol("WM_DELETE_WINDOW", self.__rscCloseHandler)
        self.rscw_ptr.title('--- Restore Configuration ---')

        p = ttk.Panedwindow(self.rscw_ptr, orient=Tkinter.HORIZONTAL)
        # first pane, which would get widgets gridded into it:
        f1 = ttk.Labelframe(p, width=300, height=200 )
        f2 = ttk.Labelframe(p, width=300, height=200); # second pane
        p.add(f1)
        p.add(f2)
        p.pack()
        p_1 = ttk.Panedwindow(f1, orient=Tkinter.VERTICAL)
        f1_1 = ttk.Labelframe(p_1, text='Engine Selection', width = 300, height=200 )
        f1_2 = ttk.Labelframe(p_1, text='Progress Bar', width=300, height=200); # second pane
        p_1.add(f1_1)
        p_1.add(f1_2)
        p_1.pack()
        p_2 = ttk.Panedwindow(f2, orient=Tkinter.VERTICAL)
        f2_1 = ttk.Labelframe(p_2, text='Saved Configuration File', width = 300, height=200 )
        f2_2 = ttk.Labelframe(p_2, text='Action', width=300, height=200); # second pane
        p_2.add(f2_1)
        p_2.add(f2_2)
        p_2.pack()
#
# Engine Selection
#
        self.selected_engine = Tkinter.IntVar()
        for i in range (0, engine_number):
            s = "E"+str(i)+": IP = %s; SN = %s ; " % (cfg["Engine"+str(i)]['IP'], engine_info[i]['SerialNumber'])
            r = Tkinter.Radiobutton(f1_1, text=s, variable=self.selected_engine, value=i, bg = 'light gray', \
                width = 40, justify = Tkinter.LEFT)
            r.pack(anchor=Tkinter.W)
#
# Progress Bar
#
        self.rcpb = ttk.Progressbar(f1_2, orient='horizontal', mode='determinate')
        self.rcpb.pack(expand=True, fill=Tkinter.BOTH, side=Tkinter.TOP)
       
# Configuration File Selection
        self.MODES =[]
        #
        for dirpath, dirs, files in os.walk('./data/'):
            i = 0
            for filename in files:
                if filename[-3:] != "zip": continue
                vv = filename.find('V')
                tt = filename.find('T')
                sn = filename[1:vv]
                fw = filename[vv+1:tt]
                tm = filename[tt+1:-4]
                tm = tm[:4]+'-'+tm[4:6]+'-'+tm[6:8]+'-'+tm[8:10]+'-'+tm[10:12]+'-'+tm[12:14]
                self.MODES.append((filename, sn, fw, tm, "%s" % i))
                i += 1
        self.var_cfg_file = Tkinter.StringVar()
#        self.var_cfg_file.set("0") # initialize

        for file, sn, fw, tm, index in self.MODES:
            s = "SN:%s; V%s; Time:%s" % (sn, fw, tm)
            r = Tkinter.Radiobutton(f2_1, text=s, variable=self.var_cfg_file, value=index, bg = 'light gray')
            r.pack(anchor=Tkinter.W)
                
# Action Buttons
        b1 = ttk.Button(f2_2, text="Cancel", width = 24, command=self.__rscCloseHandler)
        b2 = ttk.Button(f2_2, text="Confirm", width = 24, command=self.__ConfirmRecoverCfg)
        b1.grid(row=0, column=0)
        b2.grid(row=0, column=1)
        
    def __ConfirmRecoverCfg(self):        
        self.has_download = 0
        
        for file, sn, fw, tm, index in self.MODES:
            if index == self.var_cfg_file.get(): break
        engine_num = self.selected_engine.get()
#
# if serial number not match, refuse to continue        
#
        if current_engine[engine_num][0] != 'on':
            tkMessageBox.showinfo("Restore Configuration", "Selected Engine%s is offline!" % engine_num)
            return
        
        if engine_info[engine_num]['SerialNumber'] != sn:
            tkMessageBox.showinfo("Restore Configuration", "Selected Engine%s's Serial Number is wrong!" % engine_num)
            return
#
# if Engine revision is lower than backup configuration file's revision, refuse to continue
#
        efw = engine_info[engine_num]['Firmware'][1:-6].split('.')
        ffw = fw.split('.')
        
        if efw[0] < ffw[0]:
            tkMessageBox.showinfo("Restore Configuration", "Selected Engine%s's FW Rev is lower than backup file's!" % engine_num)
            return
        elif efw[0] == ffw[0] and efw[1] < ffw[1]:
            tkMessageBox.showinfo("Restore Configuration", "Selected Engine%s's FW Rev is lower than backup file's!" % engine_num)
            return
        elif efw[0] == ffw[0] and efw[1] == ffw[1] and efw[2] < ffw[2]:
            tkMessageBox.showinfo("Restore Configuration", "Selected Engine%s's FW Rev is lower than backup file's!" % engine_num)
            return
#       
        result = tkMessageBox.askokcancel("Restore Configuration", \
            "Starting to restore configuration file:\n%s,\ninto Engine%s serial number:%s, with\nfile created time:%s,\n\nIs these OK?" \
            % (file, engine_num, sn, tm))
        if result != True: return
#
# unzip, download, delete, and reboot
#
        t = ControlEngine.xEngine()
        if t.RestoreConfiguration(engine_num, file) == False:
            thread.start_new_thread( tkMessageBox.showerror, ("Restore Configuration", 
                "FAILED to restore configuration on engine%s, IP=%s" % (engine_num, cfg['Engine'+str(engine_num)]['IP'])))
            return
        result = tkMessageBox.askokcancel("Restore Configuration", \
            "Restore completed, will reboot the Engine%s now.\n\nIs this OK?" % engine_num)
        if result != True:
            tkMessageBox.showinfo("Restore Configuration", "Exit without Engine%s reboot!" % engine_num)
            return
        else:
            self.rcpb.start(136)
            self.rcpb.after(18000, self.__StopRC)   
            thread.start_new_thread( tkMessageBox.showinfo, ("Restore Configuration", 
                "Reboot is in process....WARNING: DO NOT TURN OFF THE ENGINE POWER!"))
            t.RebootEngine(engine_num)

        return
#
    def __StopRC(self):
        self.rcpb.stop()
        thread.start_new_thread( tkMessageBox.showinfo, ("Restore Configuration", "Restore configuration completed!"))
        self.__rscCloseHandler()

    def __StopPB(self):
        self.pb.stop()
        tkMessageBox.showinfo("Download Microcode", "Microcode update completed!")
        self.__dlcCloseHandler()
#        
#        
    def SetEmailNotification(self):
        if self.SENwindow_started == 1:
            dbg.printDBG2(file_name, "SEN window already start, just bring to front")
            self.senw_ptr.lift()
            return
        
        self.SENwindow_started = 1
        self.senw_ptr = Tkinter.Toplevel()
        mainframe_width = (self.senw_ptr.winfo_screenwidth() / 2 - 300)
        mainframe_heigth = (self.senw_ptr.winfo_screenheight() / 2 - 250)
        self.senw_ptr.geometry("+%d+%d" % (LLINE, 152))
        self.senw_ptr.protocol("WM_DELETE_WINDOW", self.__senCloseHandler)
        self.senw_ptr.title('--- Email Notification Table ---')

        p = ttk.Panedwindow(self.senw_ptr, orient=Tkinter.VERTICAL)
        # first pane, which would get widgets gridded into it:
        f1 = ttk.Labelframe(p, text="Email Send To", width=300, height=200 )
        f2 = ttk.Labelframe(p, text="SMTP Information", width=300, height=200); # second pane
        f3 = ttk.Labelframe(p, text="Email Content", width=300, height=200); # second pane
        f4 = ttk.Labelframe(p, text="Action", width=300, height=200); # second pane
        p.add(f1)
        p.add(f2)
        p.add(f3)
        p.add(f4)
        p.pack()

# Send To
        l1 = Tkinter.Label(f1, text="recipient 1)", width=20, height=1, bg = 'light gray')
        l2 = Tkinter.Label(f1, text="recipient 2)", width=20, height=1, bg = 'light gray')
        l3 = Tkinter.Label(f1, text="recipient 3)", width=20, height=1, bg = 'light gray')
        l4 = Tkinter.Label(f1, text="recipient 4)", width=20, height=1, bg = 'light gray')
        l5 = Tkinter.Label(f1, text="recipient 5)", width=20, height=1, bg = 'light gray')
        self.recipient1 = Tkinter.Entry(f1, bd = 2, bg = 'light gray', width = 30)
        self.recipient2 = Tkinter.Entry(f1, bd = 2, bg = 'light gray', width = 30)
        self.recipient3 = Tkinter.Entry(f1, bd = 2, bg = 'light gray', width = 30)
        self.recipient4 = Tkinter.Entry(f1, bd = 2, bg = 'light gray', width = 30)
        self.recipient5 = Tkinter.Entry(f1, bd = 2, bg = 'light gray', width = 30)
        l1.grid(row=0, column=0)
        l2.grid(row=1, column=0)
        l3.grid(row=2, column=0)
        l4.grid(row=3, column=0)
        l5.grid(row=4, column=0)
        self.recipient1.grid(row=0, column=1)
        self.recipient2.grid(row=1, column=1)
        self.recipient3.grid(row=2, column=1)
        self.recipient4.grid(row=3, column=1)
        self.recipient5.grid(row=4, column=1)
#
# SMTP In
        l1 = Tkinter.Label(f2, text="Server", width=20, height=1, bg = 'light gray')
        l2 = Tkinter.Label(f2, text="Port", width=20, height=1, bg = 'light gray')
        l3 = Tkinter.Label(f2, text="User Name", width=20, height=1, bg = 'light gray')
        l4 = Tkinter.Label(f2, text="Password", width=20, height=1, bg = 'light gray')
        self.server = Tkinter.Entry(f2, bd = 2, bg = 'light gray', width = 30)
        self.port = Tkinter.Entry(f2, bd = 2, bg = 'light gray', width = 30)
        self.uu = Tkinter.Entry(f2, bd = 2, bg = 'light gray', width = 30)
        self.ww = Tkinter.Entry(f2, bd = 2, bg = 'light gray', width = 30)
        l1.grid(row=0, column=0)
        l2.grid(row=1, column=0)
        l3.grid(row=2, column=0)
        l4.grid(row=3, column=0)
        self.server.grid(row=0, column=1)
        self.port.grid(row=1, column=1)
        self.uu.grid(row=2, column=1)
        self.ww.grid(row=3, column=1)
#
# Contents
        l1 = Tkinter.Label(f3, text="Subject", width=20, height=1, bg = 'light gray')
        l2 = Tkinter.Label(f3, text="Message", width=20, height=1, bg = 'light gray')
        self.subject = Tkinter.Entry(f3, bd = 2, bg = 'light gray', width = 30)
        self.message = Tkinter.Entry(f3, bd = 2, bg = 'light gray', width = 30)
        l1.grid(row=0, column=0)
        l2.grid(row=1, column=0)
        self.subject.grid(row=0, column=1)
        self.message.grid(row=1, column=1)
#
# Action Buttons
        b1 = ttk.Button(f4, text="Cancel", width = 15, command=self.__senCloseHandler)
        b2 = ttk.Button(f4, text="Test", width = 15, command=self.__SendTestEmail)
        b3 = ttk.Button(f4, text="Save", width = 15, command=self.__SaveENT)
        b4 = ttk.Button(f4, text="Reset", width = 15, command=self.__ResetENT)
        b1.grid(row=0, column=0)
        b2.grid(row=0, column=1)
        b3.grid(row=0, column=2)
        b4.grid(row=0, column=3)
#
# Get Default Data
        self.menu_enter = "YES"
        self.GetEmailInfo()
#        
    def GetSwitchTrace(self):
        if self.SITwindow_started == 1:
            dbg.printDBG2(file_name, "SIT window already start, just bring to front")
            self.sitw_ptr.lift()
            return
        
        self.SITwindow_started = 1
        self.sitw_ptr = Tkinter.Toplevel()
        mainframe_width = (self.sitw_ptr.winfo_screenwidth() / 2 - 300)
        mainframe_heigth = (self.sitw_ptr.winfo_screenheight() / 2 - 250)
        self.sitw_ptr.geometry("+%d+%d" % (LLINE, 152))
        self.sitw_ptr.protocol("WM_DELETE_WINDOW", self.__sitCloseHandler)
        self.sitw_ptr.title('--- Switch Diag Information ---')

        p = ttk.Panedwindow(self.sitw_ptr, orient=Tkinter.VERTICAL)
        # first pane, which would get widgets gridded into it:
        f1 = ttk.Labelframe(p, text="Switch Login", width=300, height=200 )
        f2 = ttk.Labelframe(p, text="Switch IP", width=300, height=200); # second pane
        f3 = ttk.Labelframe(p, text="Action", width=300, height=200); # second pane
        p.add(f1)
        p.add(f2)
        p.add(f3)
        p.pack()
#
# Switch Vendor
        option_list = ["Brocade","QLogic","Cisco", "Test"]

        self.switch_type = Tkinter.StringVar(f1)

        self.switch_type.set("")
        om = Tkinter.OptionMenu(f1, self.switch_type, *option_list)

        om.config(font=('Courier',(14)), bg="light gray", width=30)
        om['menu'].config(font=('Courier',(12)))
        om.grid(row=0, column=1)

        l1 = Tkinter.Label(f1, text="Switch Vendor", width=20, height=1, bg = 'light gray')
        l2 = Tkinter.Label(f1, text="User Name", width=20, height=1, bg = 'light gray')
        l3 = Tkinter.Label(f1, text="Password", width=20, height=1, bg = 'light gray')
        l4 = Tkinter.Label(f1, text="Prompt 1", width=20, height=1, bg = 'light gray')
        l5 = Tkinter.Label(f1, text="Prompt 2", width=20, height=1, bg = 'light gray')
#        self.server = Tkinter.Entry(f1, bd = 2, bg = 'light gray', width = 30)
        self.suu = Tkinter.Entry(f1, bd = 2, bg = 'light gray', width = 30)
        self.sww = Tkinter.Entry(f1, bd = 2, bg = 'light gray', width = 30)
        self.prompt1 = Tkinter.Entry(f1, bd = 2, bg = 'light gray', width = 30)
        self.prompt2 = Tkinter.Entry(f1, bd = 2, bg = 'light gray', width = 30)
        l1.grid(row=0, column=0)
        l2.grid(row=1, column=0)
        l3.grid(row=2, column=0)
        l4.grid(row=3, column=0)
        l5.grid(row=4, column=0)
#        self.server.grid(row=0, column=1)
        self.suu.grid(row=1, column=1)
        self.sww.grid(row=2, column=1)
        self.prompt1.grid(row=3, column=1)
        self.prompt2.grid(row=4, column=1)
#
# Switch IP
        l1 = Tkinter.Label(f2, text="IP of Switch 0)", width=20, height=1, bg = 'light gray')
        l2 = Tkinter.Label(f2, text="IP of Switch 1)", width=20, height=1, bg = 'light gray')
        l3 = Tkinter.Label(f2, text="IP of Switch 2)", width=20, height=1, bg = 'light gray')
        l4 = Tkinter.Label(f2, text="IP of Switch 3)", width=20, height=1, bg = 'light gray')
        l5 = Tkinter.Label(f2, text="IP of Switch 4)", width=20, height=1, bg = 'light gray')
        self.sip0 = Tkinter.Entry(f2, bd = 2, bg = 'light gray', width = 30)
        self.sip1 = Tkinter.Entry(f2, bd = 2, bg = 'light gray', width = 30)
        self.sip2 = Tkinter.Entry(f2, bd = 2, bg = 'light gray', width = 30)
        self.sip3 = Tkinter.Entry(f2, bd = 2, bg = 'light gray', width = 30)
        self.sip4 = Tkinter.Entry(f2, bd = 2, bg = 'light gray', width = 30)
        l1.grid(row=0, column=0)
        l2.grid(row=1, column=0)
        l3.grid(row=2, column=0)
        l4.grid(row=3, column=0)
        l5.grid(row=4, column=0)
        self.sip0.grid(row=0, column=1)
        self.sip1.grid(row=1, column=1)
        self.sip2.grid(row=2, column=1)
        self.sip3.grid(row=3, column=1)
        self.sip4.grid(row=4, column=1)
#
# Action Buttons
        b1 = ttk.Button(f3, text="Save Login Setting", width = 14, command=self.__SaveSIT)
        b2 = ttk.Button(f3, text=" Get Switch Logs  ", width = 14, command=self.__GetSwitchTrace)
        b3 = ttk.Button(f3, text=" Show Port Errors ", width = 14, command=self.__ShowPortError)
        b4 = ttk.Button(f3, text=" Clear Port Errors", width = 14, command=self.__ClearPortError)
#        b5 = ttk.Button(f3, text="Cancel", width = 6, command=self.__sitCloseHandler)
        b1.grid(row=0, column=0)
        b2.grid(row=0, column=1)
        b3.grid(row=0, column=2)
        b4.grid(row=0, column=3)
#        b5.grid(row=0, column=4)
#
# Get Default Data
        self.menu_enter = "YES"
        self.GetSwitchInfo()
#
#
#   self.aetw_ptr
#                       p
#       f1                              f2     
#           f1_1                            f2_1
#               c1      c2                      c1
#       p_1                             P_2
#           f1_2                            f2_2
#               pb                                b1  b2
#
    def AnalyzeEngineTrace(self):
        if self.AETwindow_started == 1:
            dbg.printDBG2(file_name, "AET window already started, just bring it to front")
            self.aetw_ptr.lift()
            return
        
        self.AETwindow_started = 1
        self.aetw_ptr = Tkinter.Toplevel()
        mainframe_width = (self.aetw_ptr.winfo_screenwidth() / 2 - 300)
        mainframe_heigth = (self.aetw_ptr.winfo_screenheight() / 2 - 250)
        self.aetw_ptr.geometry("+%d+%d" % (LLINE, 152))
        self.aetw_ptr.protocol("WM_DELETE_WINDOW", self.__aetCloseHandler)
        self.aetw_ptr.title('--- Engine Trace Analysis ---')

        p = ttk.Panedwindow(self.aetw_ptr, orient=Tkinter.HORIZONTAL)
        f1 = ttk.Labelframe(p, width=300, height=200 )
        f2 = ttk.Labelframe(p, width=300, height=200); # second pane
        p.add(f1)
        p.add(f2)
        p.pack()
        p_2 = ttk.Panedwindow(f1, orient=Tkinter.VERTICAL)
        f2_1 = ttk.Labelframe(p_2, text='Zipped Trace File Selection', width = 300, height=200 )
        f2_2 = ttk.Labelframe(p_2, text='Action', width=300, height=200); # second pane
        p_2.add(f2_1)
        p_2.add(f2_2)
        p_2.pack()
        p_1 = ttk.Panedwindow(f2, orient=Tkinter.VERTICAL)
        f1_1 = ttk.Labelframe(p_1, text='Search Filter Selection', width = 300, height=200 )
        p_1.add(f1_1)
        p_1.pack()
#
# Filter Selection
#
        self.filter_list = [
            "Alert Halt",
            "Link Error",
            "Queue Full",
            "ABTS",
            "Reboot",
            "RSCN",
            "Drive is blocked"          # potential CAW Lockup issue
        ]
        self.selected_filter = [0 for x in range(len(self.filter_list))]
        for i in range (len(self.filter_list)):
            self.selected_filter[i] = Tkinter.IntVar()
            self.selected_filter[i].set(1)
            c1 = Tkinter.Checkbutton(f1_1, text = self.filter_list[i], variable = self.selected_filter[i], \
                         onvalue = 1, offvalue = 0, height=1, width = 25, bg = 'light gray', justify=Tkinter.LEFT)
            c1.grid(row=i, column=0)

        size = 2
        self.keyword_filter = [0 for x in range(size)]
        for i in range (size):
            self.keyword_filter[i] = Tkinter.StringVar()
            e1 = Tkinter.Entry(f1_1, width=20, textvariable=self.keyword_filter[i])
            e1.grid(row=len(self.filter_list)+i, column=0)
       
# Zip Package Selection
        self.ZIPS =[]
        #
        for dirpath, dirs, files in os.walk('./z_analyze/'):
            i = 0
            for filename in files:
                if filename[-3:] != "zip": continue
                self.ZIPS.append((filename, "%s" % i))
                i += 1
        self.v = Tkinter.StringVar()
        self.v.set("0") # initialize

        for text, mode in self.ZIPS:
            r = Tkinter.Radiobutton(f2_1, text=text, variable=self.v, value=mode, bg = 'light gray')
            r.pack(anchor=Tkinter.W)
                
# Action Buttons
        b1 = ttk.Button(f2_2, text="Cancel", width = 20, command=self.__aetCloseHandler)
        b2 = ttk.Button(f2_2, text="Confirm", width = 20, command=self.__FilterZipSelection)
        b1.grid(row=0, column=0)
        b2.grid(row=0, column=1)
#
    def __FilterZipSelection(self):
        for zip_file, key in self.ZIPS:
            if key == self.v.get(): break   # got zip file name
        
        SEARCHS = []
        
        for i in range (len(self.filter_list)):
            if self.selected_filter[i].get() == 1: SEARCHS.append(self.filter_list[i])
            
        for i in range (len(self.keyword_filter)):
            if self.keyword_filter[i].get() != '': SEARCHS.append(self.keyword_filter[i].get())

        result = tkMessageBox.askokcancel("Trace Analysis", "Starting to analyze trace \"%s\", \n\nOK?" % zip_file)
        if result != True: return

# unzip the file
        FPATH = "./z_analyze/"    
        unzip_dir = zip_file.split('.')[0]
        zippath = FPATH + unzip_dir
        
        p = ZipUtility.ZipUtil()
        p.UnzipFile(FPATH+zip_file, zippath)

# find files

        txt_files = []
        for dirpath, dirs, files in os.walk(zippath):
            if files != []:
                for f in files:
                    txt_files.append((dirpath+"/"+f, f))

# display the filtered result
        
        self.trace_ptr = Tkinter.Toplevel()
        mainframe_width = (self.trace_ptr.winfo_screenwidth() / 2 - 300)
        mainframe_heigth = (self.trace_ptr.winfo_screenheight() / 2 - 250)
        if engine_number == 2:
            self.trace_ptr.geometry("+%d+%d" % (LLINE, 115))
        else:
            self.trace_ptr.geometry("+%d+%d" % (LLINE, 152))
        self.trace_ptr.protocol("WM_DELETE_WINDOW", self.__CloseHandler)
        self.trace_ptr.title('--- Trace File Analysis ---')


        for path_f, only_f in txt_files:
            if only_f[:2] == '._': continue

            txtfile = open(path_f, 'r')
            txtlines = txtfile.readlines()
            txtlength = len(txtlines)
#
        p = ttk.Panedwindow(self.trace_ptr, orient=Tkinter.HORIZONTAL)

        engine_info[0]['Analysis'] = {}        

        for path_f, only_f in txt_files:
            if only_f[:2] == '._': continue

            txtfile = open(path_f, 'r')
            txtlines = txtfile.readlines()
            txtlength = len(txtlines)
#
# use PCB Number to identify files
            for i in range (txtlength):
                if txtlines[i].find('PCB Number') != -1:
                    info = txtlines[i].split()
                    if info[3] not in engine_info[0]['Analysis']:
                        engine_info[0]['Analysis'][info[3]] = {}
                        engine_info[0]['Analysis'][info[3]]['File'] = [(path_f, only_f)]
                    else:
                        engine_info[0]['Analysis'][info[3]]['File'].append((path_f, only_f))
                    break
            txtfile.close()
#
# no PCB Number, use telnet IP to identify files
#       Connected to 10.100.5.56.
#
        if engine_info[0]['Analysis'] == {}:

            for path_f, only_f in txt_files:
                if only_f[:2] == '._': continue

                txtfile = open(path_f, 'r')
                txtlines = txtfile.readlines()
                txtlength = len(txtlines)

                for i in range (txtlength):
                    if not txtlines[i].startswith('Connected to'): continue
                    info = txtlines[i].split()
                    if info[2] not in engine_info[0]['Analysis']:
                        engine_info[0]['Analysis'][info[2]] = {}
                        engine_info[0]['Analysis'][info[2]]['File'] = [(path_f, only_f)]
                    else:
                        engine_info[0]['Analysis'][info[2]]['File'].append((path_f, only_f))
                    break
                txtfile.close()
    
        for item in engine_info[0]['Analysis']:
            engine_info[0]['Analysis'][item]['Pointer'] = ttk.LabelFrame(p, text=item, width=300, height=500 )
#            p.add(vpd_frame[self.FRAMES.index(item)])
            p.add(engine_info[0]['Analysis'][item]['Pointer'])
            p.pack()
#       
# Action Buttons (Diagnostic Tools)
#
            VY = Tkinter.Scrollbar(engine_info[0]['Analysis'][item]['Pointer'])
            VPD = Tkinter.Text(engine_info[0]['Analysis'][item]['Pointer'], wrap=Tkinter.NONE, height=15, width=50, bg="light gray",
                yscrollcommand=VY.set)
            VY.config(command=VPD.yview)
            SX = Tkinter.Scrollbar(engine_info[0]['Analysis'][item]['Pointer'], orient=Tkinter.HORIZONTAL)
            SY = Tkinter.Scrollbar(engine_info[0]['Analysis'][item]['Pointer'])
            TXT = Tkinter.Text(engine_info[0]['Analysis'][item]['Pointer'], wrap=Tkinter.NONE, height=25, width=50, bg="light gray",
                xscrollcommand=SX.set, yscrollcommand=SY.set)
            SX.config(command=TXT.xview)
            SY.config(command=TXT.yview)
            VPD.grid(row=0, column=0)
            VY.grid(row=0, column=1, sticky=Tkinter.N+Tkinter.S+Tkinter.E+Tkinter.W)
            TXT.grid(row=1, column=0)
            SY.grid(row=1, column=1, sticky=Tkinter.N+Tkinter.S+Tkinter.E+Tkinter.W)
            SX.grid(row=2, column=0, sticky=Tkinter.N+Tkinter.S+Tkinter.E+Tkinter.W)
#
# Find VPD
#
# Firmware V15.9.7.5      RSS6000T Official Release
# Revision Data : UDsafe(release), Mar  1 2017 19:24:05
# Uptime             : 00:50:05
#
            for path_f, only_f in engine_info[0]['Analysis'][item]['File']:
#
                txtfile = open(path_f, 'r')
                txtlines = txtfile.readlines()
                txtlength = len(txtlines)

                VPD.insert(Tkinter.END, '%s:\n' % only_f)
                fw = rd = ip = ut = -1 
                for i in range (txtlength):
                    if txtlines[i].startswith('Firmware'): fw = i
                    if txtlines[i].startswith('Revision Data'): rd = i
                    if txtlines[i].startswith('IP addresses'): ip = i
                    if txtlines[i].startswith('Uptime'): ut = i
                
                if fw != -1: VPD.insert(Tkinter.END, txtlines[fw])
                if rd != -1: VPD.insert(Tkinter.END, txtlines[rd])
                if ip != -1: VPD.insert(Tkinter.END, txtlines[ip])
                if ut != -1: VPD.insert(Tkinter.END, txtlines[ut])
#
# Search for lines
#
#!!!!
#              RE:   Drive is blocked at level 0
#13:38.639_433 RE: RE-IOCB 1191, address = 0x00f60874, next = 764
#              RE:   target_number 0x8203, fifo_level = 0, function = 61 !!!!compare write
#!!!!
#              RE:   ext_type = IOCB_EXT_SCSI
#              RE:   upstream = CM: 542, downstream = RE: 65535
#              RE:   flags = 0x14001885   !!!! bit 2 =1 , abort has received, 0101
#
                for k in SEARCHS:
                    TXT.insert(Tkinter.END, '%s\n%s:\n' % (only_f, k))
                    search_count = 0
                    for i in range (txtlength):
                        if txtlines[i].lower().find(k.lower()) != -1:
#
# line that no need to be counted
                            if k.lower() == 'queue full' and txtlines[i].find("Queue full count = 0") != -1: continue
                            if k.lower() == 'link error' and txtlines[i].find("Link error log:") != -1: continue
#
# line that needs to count
                            if k in self.filter_list: TXT.insert(Tkinter.END, txtlines[i])
#
# line that needs to treat specially
                            if txtlines[i].find("ABTS") != -1:
                                TXT.insert(Tkinter.END, txtlines[i+1])
                            if txtlines[i].find("Drive is blocked") != -1:
                                TXT.insert(Tkinter.END, txtlines[i+1])
                                TXT.insert(Tkinter.END, txtlines[i+2])
                            if txtlines[i].find("Alert Halt(") != -1:
                                TXT.insert(Tkinter.END, txtlines[i+1])
                            if k not in self.filter_list:       # display more lines when string input by hand
                                TXT.insert(Tkinter.END, txtlines[i-2])                                
                                TXT.insert(Tkinter.END, txtlines[i-1])
                                TXT.insert(Tkinter.END, txtlines[i])                                
                                TXT.insert(Tkinter.END, txtlines[i+1])
                                TXT.insert(Tkinter.END, txtlines[i+2])                                

                            search_count += 1

                    VPD.insert(Tkinter.END, '%s = %s\n' % (k, search_count))                        
                    TXT.insert(Tkinter.END, '\n')

                txtfile.close()
                VPD.insert(Tkinter.END, '\n')
                TXT.insert(Tkinter.END, '\n')
                
# remove unzipped files
        shutil.rmtree(zippath)
        
#
    def __SaveSIT(self):
        self.__SaveData("Switch.dat")
        tkMessageBox.showinfo("Switch Information Table", "Switch Information saved!")
#
    def __SaveENT(self):
        self.__SaveData("email.dat")
        tkMessageBox.showinfo("Email Notification", "Email Notification Table saved!")
#
    def __SaveTCP(self):
        self.__SaveData("TCP.dat")
        tkMessageBox.showinfo("TCP Server Window", "TCP Server Table saved!")
#
    def __SaveAPI(self):
        self.__SaveData("API.dat")
        tkMessageBox.showinfo("API Test Window", "API Test Table saved!")
#
    def __SaveLPS(self):
        self.__SaveData("LPS.dat")
        tkMessageBox.showinfo("Lapresse Test Window", "Lapresse Test Table saved!")
#
    def __SaveJSON(self):
        self.__SaveData("JSON.dat")
        tkMessageBox.showinfo("JSON Test Window", "JSON Test Table saved!")
#
    def __ResetENT(self):
        ans = tkMessageBox.askokcancel("Send Email", 
            "Are you sure you want to reset the email info back to default?")
        
        if ans != True:
            thread.start_new_thread( tkMessageBox.showinfo, ("Send Email", "Action has been cancelled."))
            return False
            
        self.__ReadSaved("default.dat")
#
    def __GetSwitchTrace(self):
        ans = tkMessageBox.askokcancel("Switch Diag Information", 
            "Have you saved your change of Switch Login settings, and want to get the switch logs?")
        
        if ans != True:
            tkMessageBox.showinfo("Switch Diag Information", "Action has been cancelled.")
            return False
            
        t = ControlSwitch.xSwitch()
        if t.getInfoFromSwitch() == True:
            tkMessageBox.showinfo("Switch Information Table", "Switch logs gathered successfully.")
        else:
            tkMessageBox.showinfo("Switch Information Table", "Failed to gather switch logs.")
#
    def __ShowPortError(self):
        ans = tkMessageBox.askokcancel("Display Switch Port Error", 
            "Have you saved your change of Switch Login settings, and want to check if any port error reported in log?")
        
        if ans != True:
            tkMessageBox.showinfo("Display Switch Port Error", "Action has been cancelled.")
            return False
            
        t = ControlSwitch.xSwitch()
        if t.checkSwitchError() == True:
#            tkMessageBox.showinfo("Switch Information Table", "Switch information com")
            pass
        else:
            tkMessageBox.showinfo("Display Switch Port Error", "Failed to access switch diag logs.")
#
    def __ClearPortError(self):
        ans = tkMessageBox.askokcancel("Switch Diag Information", 
            "Have you saved your change of Switch Login settings, and want to clear the switch diag counters?")
        
        if ans != True:
            thread.start_new_thread( tkMessageBox.showinfo, ("Switch Diag Information", "Action has been cancelled."))
            return False
            
        t = ControlSwitch.xSwitch()
        if t.getInfoFromSwitch(clear_count = True) == True:
            tkMessageBox.showinfo("Switch Diag Information", "Switch port diag counters cleared successfully.")
        else:
            tkMessageBox.showinfo("Switch Diag Information", "Failed to clear switch port diag counters.")
#
    def __SendTestEmail(self):
        ans = tkMessageBox.askokcancel("Send Email", 
            "Have you saved your change of Email Info Table, and want to send the test mail?")
        
        if ans != True:
            thread.start_new_thread( tkMessageBox.showinfo, ("Send Email", "Action has been cancelled."))
            return False
            
        t = ControlEmail.xEmail()
        if t.send_message(email_info) == True:
            tkMessageBox.showinfo("Email Notification", "Email Notification sent successfully.")
        else:
            tkMessageBox.showinfo("Email Notification", "Failed to send Email!")
#
    def GetEmailInfo(self):
        datapath = './data/'
        data_file_name = datapath + "default.dat"
        if not os.path.isfile(data_file_name):
            tkMessageBox.showerror("Email Notification", "Default file does not found!")            
            return False
        elif self.__CheckHash("default.dat") == False:
            tkMessageBox.showerror("Email Notification", "Default file is corrupted!")            
            return False
            
        data_file_name = datapath + "email.dat"
        if os.path.isfile(data_file_name):
            if self.__CheckHash("email.dat") == False:
                self.__ReadSaved("default.dat")
                tkMessageBox.showerror("Email Notification", "Email config file is corrupted! Roll back to default setting")            
                return False
            else:
                self.__ReadSaved("email.dat")                
        else:
            self.__ReadSaved("default.dat")

#
    def GetSwitchInfo(self):
        datapath = './data/'
        data_file_name = datapath + "Switch.dat"
        if os.path.isfile(data_file_name):
            if self.__CheckHash("Switch.dat") == True:
                self.__ReadSaved("Switch.dat")
                return True
        return False
#
    def GetAPIInfo(self):
        datapath = './data/'
        data_file_name = datapath + "API.dat"
        if os.path.isfile(data_file_name):
            if self.__CheckHash("API.dat") == True:
                self.__ReadSaved("API.dat")
                return True
        return False
#
    def GetLPSInfo(self):
        datapath = './data/'
        data_file_name = datapath + "LPS.dat"
        if os.path.isfile(data_file_name):
            if self.__CheckHash("LPS.dat") == True:
                self.__ReadSaved("LPS.dat")
                return True
        return False
#
    def GetJSONinfo(self):
        datapath = './data/'
        data_file_name = datapath + "JSON.dat"
        if os.path.isfile(data_file_name):
            if self.__CheckHash("JSON.dat") == True:
                self.__ReadSaved("JSON.dat")
                return True
        return False
#
    def GetTCPInfo(self):
        datapath = './data/'
        data_file_name = datapath + "TCP.dat"
        if os.path.isfile(data_file_name):
            if self.__CheckHash("TCP.dat") == True:
                self.__ReadSaved("TCP.dat")
                return True
        return False
#
    def __ReadSaved(self, file_name):
        global email_info
        global API_info
        global switch_info
        global TCP_info
        global LPS_info
        global JSON_info
        datapath = './data/'
        f = open(datapath+file_name, 'r')
        lines = f.readlines()
        f.close()

        #
        if file_name == "TCP.dat":
            for i in range (0, len(lines)-1, 2):
                TCP_info[base64.b64decode(lines[i])] = base64.b64decode(lines[i+1])

            if self.menu_enter == "NO": return
 
            for k, d in TCP_info.iteritems():
                eval("self."+ k).delete(0, 'end')
                eval("self."+ k).insert(0, d)

        if file_name == "LPS.dat":
            for i in range (0, len(lines)-1, 2):
                LPS_info[base64.b64decode(lines[i])] = base64.b64decode(lines[i+1])

            if self.menu_enter == "NO": return
 
            for k, d in LPS_info.iteritems():
                eval("self."+ k).delete(0, 'end')
                eval("self."+ k).insert(0, d)

        elif file_name == "API.dat":
            for i in range (0, len(lines)-1, 2):
                API_info[base64.b64decode(lines[i])] = base64.b64decode(lines[i+1])

            if self.menu_enter == "NO": return
 
            for k, d in API_info.iteritems():
                eval("self."+ k).delete(0, 'end')
                eval("self."+ k).insert(0, d)
        #
        elif file_name == "JSON.dat":
            for i in range (0, len(lines)-1, 2):
                JSON_info[base64.b64decode(lines[i])] = base64.b64decode(lines[i+1])

            if self.menu_enter == "NO": return
 
            for k, d in JSON_info.iteritems():
                eval("self."+ k).delete(0, 'end')
                eval("self."+ k).insert(0, d)
        #
        elif file_name == "Switch.dat":
            for i in range (0, len(lines)-1, 2):
                switch_info[base64.b64decode(lines[i])] = base64.b64decode(lines[i+1])

            if self.menu_enter == "NO": return
 
            for k, d in switch_info.iteritems():
                if (k == "switch_type"):
                    self.switch_type.set(d)
                    continue

                eval("self."+ k).delete(0, 'end')
                eval("self."+ k).insert(0, d)
                if k == "sww":
                    eval("self."+ k).delete(0, "end")
                    eval("self."+ k).insert(0, "*"*8)
        
        elif file_name == "email.dat" or file_name == "default.dat":
            for i in range (0, len(lines)-1, 2):
                email_info[base64.b64decode(lines[i])] = base64.b64decode(lines[i+1])

            if self.menu_enter == "NO": return
 
            for k, d in email_info.iteritems():
                if k == "runmode": continue
                eval("self."+ k).delete(0, 'end')
                eval("self."+ k).insert(0, d)
                if k == "ww":
                    eval("self."+ k).delete(0, "end")
                    eval("self."+ k).insert(0, "*"*8)
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
# update the email_info
        self.__ReadSaved(file_name)
#
    def __SaveData(self, file_name):
        if file_name == "email.dat":
            KEYS = ["server",
                "port",
                "recipient1",
                "recipient2",
                "recipient3",
                "recipient4",
                "recipient5",
                "uu",
                "ww",
                "subject",
                "message",
            ]
        #
        elif file_name == "API.dat":
            KEYS = [
                "server",
                "port",
                "slot1_1",
                "slot1_2",
                "slot1_3",
                "slot1_4",
                "slot1_5",
                "slot1_6",
                "slot2_1",
                "slot2_2",
                "slot2_3",
                "slot2_4",
                "slot2_5",
                "slot2_6",
                "slot3_1",
                "slot3_2",
                "slot3_3",
                "slot3_4",
                "slot3_5",
                "slot3_6",
            ]
        #
        elif file_name == "JSON.dat":
            KEYS = [
                "dir0",
                "dir1",
            ]
        #
        elif file_name == "TCP.dat":
            KEYS = ["server",
                "port",
            ]
        #
        elif file_name == "LPS.dat":
            KEYS = ["server",
                "port",
            ]
        #
        elif file_name == "Switch.dat":
            KEYS = [
                "switch_type",
                "suu",
                "sww",
                "prompt1",
                "prompt2",
                "sip0",
                "sip1",
                "sip2",
                "sip3",
                "sip4",
            ]
 
        datapath = './data/'
        if not os.path.exists(datapath): os.makedirs(datapath)
        data_file_name = datapath + file_name
        f = open(data_file_name, 'w')
        
        for k in KEYS:
            f.write( base64.b64encode(k) + "\n")
            if ((k == "ww" or k == "sww") and eval("self."+k).get() == "*"*8):
                if k == "ww": f.write( base64.b64encode(email_info["ww"]) + "\n")   # no change                
                elif k == "sww": f.write( base64.b64encode(switch_info["sww"]) + "\n")   # no change                
            else:
                f.write( base64.b64encode(eval("self."+k).get()) + "\n")    # update to new
        f.close()
#
# Add hash number to end of the file
        h = hashlib.md5()
        f = open(data_file_name, 'rb')
        h.update(f.read())
        f = open(data_file_name, 'a')
        f.write(h.hexdigest())
        f.close()
#
# update the email_info
        self.__ReadSaved(file_name)
#
#
    def __CloseHandler(self):
#        diag_global_ptr[STATUS] = STOPPED
        self.trace_ptr.destroy()

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
    def __AnalyzeEngineTrace(self):
        d = DisplayMenubar.DisplayMenubar()
        d.AnalyzeEngineTrace()
#        
    def __SetEmailNotification(self):
        d = DisplayMenubar.DisplayMenubar()
        d.SetEmailNotification()    
