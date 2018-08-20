#!/usr/bin/python
"""
Display Configuration Panel

Created by Susan Cheng on 2015-06-18.
Copyright (c) 2015-2017 __Loxoll__. All rights reserved.
"""

import ttk, Tkinter
import tkMessageBox

import time, datetime, os
import ControlEngine, ParseEngineVPD, ControlName
import functools
import threading, thread
import copy

file_name = os.path.basename(__file__)

LF_WIDTH=291
LF_HEIGHT=425
B_WIDTH = 16
EXP_WRAP = 260

class DisplayConfigPanel():

    def __init__(self):
        dbg.printDBG1(file_name, "initiate DisplayConfigPanel")

        for i in range (engine_number):
            engine_info[i]["Selected"]["Mirror"] = ""
            engine_info[i]["Selected"]["Primary"] = ""
            engine_info[i]["Selected"]["Secondary"] = ""

    def startDisplayConfigPanel(self, c, p):
        self.cfgw_ptr = Tkinter.Toplevel()
        mainframe_width = (self.cfgw_ptr.winfo_screenwidth() / 2 - 300)
        mainframe_heigth = (self.cfgw_ptr.winfo_screenheight() / 2 - 250)
        if engine_number == 2:
            self.cfgw_ptr.geometry("+%d+%d" % (LLINE, 115))
        else:
            self.cfgw_ptr.geometry("+%d+%d" % (LLINE, 152))
        self.cfgw_ptr.protocol("WM_DELETE_WINDOW", self.__CloseHandler)
        self.cfgw_ptr.title('--- %s Configuration ---' % p)
        n = ttk.Notebook(self.cfgw_ptr)
        n.pack(fill='both', expand='yes')
        #
        frame_1 = ttk.Frame(self.cfgw_ptr)
        frame_2 = ttk.Frame(self.cfgw_ptr)
        frame_3 = ttk.Frame(self.cfgw_ptr)
        frame_4 = ttk.Frame(self.cfgw_ptr)
        frame_5 = ttk.Frame(self.cfgw_ptr)
        frame_6 = ttk.Frame(self.cfgw_ptr)
        frame_7 = ttk.Frame(self.cfgw_ptr)
        frame_8 = ttk.Frame(self.cfgw_ptr)
        frame_9 = ttk.Frame(self.cfgw_ptr)
        frame_1.pack()
        frame_2.pack()
        frame_3.pack()
        frame_4.pack()
        frame_5.pack()
        frame_6.pack()
        frame_7.pack()
        frame_8.pack()
        frame_9.pack()
        # create the pages
        n.add(frame_1, text='  FC Port Explorer ')
        n.add(frame_2, text='  Auto Registraton ')
        n.add(frame_7, text=' Manual Registraton')
        n.add(frame_3, text=' Create Mirror LUN ')
        n.add(frame_8, text=' Rebuild Management')
        n.add(frame_6, text='  Name Management  ')
        n.add(frame_4, text=' Host-Map Grouping ')
        n.add(frame_9, text=' Host-LUN Mapping  ')
        n.add(frame_5, text='  License & Mode   ')
        
        total_pane_width = 1200
        self.PORTS = ['A1', 'A2', 'B1', 'B2']
        port_frame = [0 for x in range(len(self.PORTS))]
        self.var = [[0 for x in self.PORTS] for x in range(engine_number)]
#
# frame 1 (FC Port Explorer)
#
#       np1
#           np1_p[engines]
#               +-----------------------------------------------------------+
#               |  Explore A1  |  Explore A2  |  Explore B1  |  Explore B2  |
#           f1  |              |              |              |              |
#               |              |              |              |              |
#               |-----------------------------------------------------------|
#           f2  |   [Rescan]   |   [Rescan]   |   [Rescan]   |   [Rescan]   |
#               |-----------------------------------------------------------|
#
#       np1
#           np1_p[engines]
#               p1
#                   port_frame[FRAMES]    
#                       p2
#                           self.f1_1[FRAMES] (treeview)
#                           f1_2
#
#
# 1) define ptr of parent ttk (with grand parent) 
# 2) define ptr of child ttk (from parent) 
# 3) add child ptr ttk into parent ptr
# 4) pack parent
#
        np1 = ttk.Notebook(frame_1)
        np1.pack(fill='both', expand='yes')

        np1_p = [0 for x in range(engine_number)]
        self.exp_tv = [[0 for x in self.PORTS] for x in range(engine_number)]
        self.exp_tv_var = [[0 for x in self.PORTS] for x in range(engine_number)]
             
        for i in range (engine_number):
            np1_p[i] = ttk.Frame(frame_1)
            np1_p[i].pack()
            np1.add(np1_p[i], text='   Engine %s   ' % i)
#
            p1 = ttk.Panedwindow(np1_p[i], orient=Tkinter.HORIZONTAL)
            
            if current_engine[i][0] != 'on':
                tf = Tkinter.Label(p1, text="\n"*10 + "This Engine is offline.", justify = Tkinter.CENTER, bg = "#d8d8d8")
                p1.add(tf)
                p1.pack()
                continue
                            
            for pt in self.PORTS:
                port_frame[self.PORTS.index(pt)] = ttk.Labelframe(p1, text="Explore %s" % pt)         
                p1.add(port_frame[self.PORTS.index(pt)])
                p1.pack()

                p2 = ttk.Panedwindow(port_frame[self.PORTS.index(pt)])
                f1_2 = ttk.Frame(p2)             
                p2.add(f1_2)

                self.exp_tv[i][self.PORTS.index(pt)] = ttk.Treeview(port_frame[self.PORTS.index(pt)],
                    height=24, padding = (0,2,0,2))
                self.exp_tv[i][self.PORTS.index(pt)]["columns"]=('#1', '#2')

                self.exp_tv[i][self.PORTS.index(pt)].column("#0", width=65, anchor=Tkinter.E)
                self.exp_tv[i][self.PORTS.index(pt)].column("#1", width=70, anchor=Tkinter.E)
                self.exp_tv[i][self.PORTS.index(pt)].column("#2", width=150, anchor=Tkinter.E)
                self.exp_tv[i][self.PORTS.index(pt)].heading("#0", text="Type/LUN#")
                self.exp_tv[i][self.PORTS.index(pt)].heading("#1", text="Capacity")
                self.exp_tv[i][self.PORTS.index(pt)].heading("#2", text="WWPN/LUN Serial Number")
                
                self.exp_tv[i][self.PORTS.index(pt)].bind("<Double-Button-1>", self.__EngineInfoOnMotion)
                self.exp_tv[i][self.PORTS.index(pt)].pack(expand=YES, fill=Tkinter.BOTH)
#
# Action Buttons
                RescanButtonClick_with_arg = functools.partial (self.RescanButtonClick, i, pt)
                b2 = ttk.Button(f1_2, text="Rescan", command=RescanButtonClick_with_arg)

                b2.grid(row=0, column=0)
                p2.pack()
#
# get last explore info from exp file
#
                self.exp_tv_var[i][self.PORTS.index(pt)] = Tkinter.StringVar()
                self.exp_tv_var[i][self.PORTS.index(pt)].set("N/A")
#
            if current_engine[i][0] == 'on':
                p = ControlEngine.xEngine()
                for port in self.PORTS: p.UpdateInfo(i, 'exp', port)
                    
            self.DB2Panel_EXT(i)
#
# frame 2 (Auto Registraton)
#
#       np2
#           np2_p[engines]
#               +--------------------------------------------------------------+
#               | Registered Engines| Registered Drives | Registered Initiators|
#           f1  |                   |                   |                      |
#               |                   |                   |                      |
#               |--------------------------------------------------------------|
#           f2  |   [Update][Erase][AutoConfig Engines][AutoConfig Drives][AutoConfig Initiators]        |
#               |--------------------------------------------------------------|
#
#       np2
#           np2_p[engines]
#               p1
#                   port_frame[FRAMES]    
#                       p2
#                           self.f1_1[FRAMES] (treeview)
#                           f1_2
#
#
        np2 = ttk.Notebook(frame_2)
        np2.pack(fill='both', expand='yes')

        np2_p = [0 for x in range(engine_number)]
        self.FRAMES = ['Initiator', 'Drive', 'Engine']
        self.f1_1 = [[0 for x in self.FRAMES] for x in range(engine_number)]

        self.acb0 = [0 for x in range(engine_number)]
        self.acb1 = [0 for x in range(engine_number)]
        self.acb2 = [0 for x in range(engine_number)]
        self.acb3 = [0 for x in range(engine_number)]
        self.acb4 = [0 for x in range(engine_number)]
        self.acb5 = [0 for x in range(engine_number)]
             
        for i in range (engine_number):
            np2_p[i] = ttk.Frame(frame_2)
            np2_p[i].pack()
            np2.add(np2_p[i], text='   Engine %s   ' % i)
#
            p = ttk.Panedwindow(np2_p[i], orient=Tkinter.VERTICAL)
            f1 = ttk.Frame(p)
            f2 = ttk.Frame(p)
            p.add(f1)
            p.add(f2)
            p.pack()
#
            p = ttk.Panedwindow(f1, orient=Tkinter.HORIZONTAL)
            
            if current_engine[i][0] != 'on':
                tf = Tkinter.Label(p, text="\n"*10 + "This Engine is offline.", justify = Tkinter.CENTER,
                     bg = "#d8d8d8")
                p.add(tf)
                p.pack()
                continue
#         
            for pt in self.FRAMES:                
                engine_info[i]['Registered'][pt] = {}

                port_frame[self.FRAMES.index(pt)] = ttk.Labelframe(p, text="Registered %s" % pt)
                p.add(port_frame[self.FRAMES.index(pt)])
                p.pack()
#               
                self.f1_1[i][self.FRAMES.index(pt)] = ttk.Treeview(port_frame[self.FRAMES.index(pt)],
                    height=22, padding = (0,2,0,2))
                self.f1_1[i][self.FRAMES.index(pt)]["columns"]=('#1', '#2', '#3', '#4')
                if pt == 'Initiator':
                    self.f1_1[i][self.FRAMES.index(pt)].column("#0", width=70, anchor=Tkinter.CENTER)
                    self.f1_1[i][self.FRAMES.index(pt)].column("#1", width=50, anchor=Tkinter.CENTER)
                    self.f1_1[i][self.FRAMES.index(pt)].column("#2", width=50, anchor=Tkinter.CENTER)
                    self.f1_1[i][self.FRAMES.index(pt)].column("#3", width=160, anchor=Tkinter.CENTER)
                    self.f1_1[i][self.FRAMES.index(pt)].column("#4", width=50, anchor=Tkinter.CENTER)
                    self.f1_1[i][self.FRAMES.index(pt)].heading("#0", text="Inum")
                    self.f1_1[i][self.FRAMES.index(pt)].heading("#1", text="Type")
                    self.f1_1[i][self.FRAMES.index(pt)].heading("#2", text="Port")
                    self.f1_1[i][self.FRAMES.index(pt)].heading("#3", text="WWPN")
                    self.f1_1[i][self.FRAMES.index(pt)].heading("#4", text="Status")
                elif pt == 'Engine':
                    self.f1_1[i][self.FRAMES.index(pt)].column("#0", width=70, anchor=Tkinter.CENTER)
                    self.f1_1[i][self.FRAMES.index(pt)].column("#1", width=50, anchor=Tkinter.CENTER)
                    self.f1_1[i][self.FRAMES.index(pt)].column("#2", width=160, anchor=Tkinter.CENTER)
                    self.f1_1[i][self.FRAMES.index(pt)].column("#3", width=50, anchor=Tkinter.CENTER)
                    self.f1_1[i][self.FRAMES.index(pt)].column("#4", width=50, anchor=Tkinter.CENTER)
                    self.f1_1[i][self.FRAMES.index(pt)].heading("#0", text="Enum")
                    self.f1_1[i][self.FRAMES.index(pt)].heading("#1", text="Port")
                    self.f1_1[i][self.FRAMES.index(pt)].heading("#2", text="WWPN")
                    self.f1_1[i][self.FRAMES.index(pt)].heading("#3", text="Master")
                    self.f1_1[i][self.FRAMES.index(pt)].heading("#4", text="Status")                
                else:
                    self.f1_1[i][self.FRAMES.index(pt)].column("#0", width=70, anchor=Tkinter.CENTER)
                    self.f1_1[i][self.FRAMES.index(pt)].column("#1", width=50, anchor=Tkinter.CENTER)
                    self.f1_1[i][self.FRAMES.index(pt)].column("#2", width=160, anchor=Tkinter.CENTER)
                    self.f1_1[i][self.FRAMES.index(pt)].column("#3", width=50, anchor=Tkinter.CENTER)
                    self.f1_1[i][self.FRAMES.index(pt)].column("#4", width=50, anchor=Tkinter.CENTER)
                    self.f1_1[i][self.FRAMES.index(pt)].heading("#0", text="Tnum")
                    self.f1_1[i][self.FRAMES.index(pt)].heading("#1", text="Port")
                    self.f1_1[i][self.FRAMES.index(pt)].heading("#2", text="WWPN")
                    self.f1_1[i][self.FRAMES.index(pt)].heading("#3", text="LUN")
                    self.f1_1[i][self.FRAMES.index(pt)].heading("#4", text="Status")
                
                self.f1_1[i][self.FRAMES.index(pt)].bind("<Double-Button-1>", self.__EngineInfoOnMotion)
                self.f1_1[i][self.FRAMES.index(pt)].pack(expand=YES, fill=Tkinter.BOTH)
#
# Action Buttons
#
            p = ttk.Frame(f2)
            
            GetConfigCmg_with_arg = functools.partial (self.__GetConfigCmg, i)
            EraseConfigCmg_with_arg = functools.partial (self.__EraseConfigCmg, i)
            ConfigDriveCmg_with_arg = functools.partial (self.__ConfigDriveCmg, i)
            ConfigEngineCmg_with_arg = functools.partial (self.__ConfigEngineCmg, i)
            BootEngineCmg_with_arg = functools.partial (self.__BootEngineCmg, i)
            ConfigInitiatorCmg_with_arg = functools.partial (self.__ConfigInitiatorCmg, i)

            self.acb0[i] = ttk.Button(p, text="Retrieve Config Info ", command=GetConfigCmg_with_arg)
            self.acb1[i] = ttk.Button(p, text="1)  Clear Config     ", command=EraseConfigCmg_with_arg)
            self.acb2[i] = ttk.Button(p, text="2)  Config Drive     ", command=ConfigDriveCmg_with_arg)
            self.acb3[i] = ttk.Button(p, text="3)  Config Engine    ", command=ConfigEngineCmg_with_arg)
            self.acb4[i] = ttk.Button(p, text="4)  Reboot Engine    ", command=BootEngineCmg_with_arg)
            self.acb5[i] = ttk.Button(p, text="5)  Config Initiator ", command=ConfigInitiatorCmg_with_arg)

            self.acb2[i].config(state="disabled")
            self.acb3[i].config(state="disabled")
            self.acb4[i].config(state="disabled")
            self.acb5[i].config(state="disabled")
            
            self.acb0[i].grid(row=0, column=0)
            self.acb1[i].grid(row=0, column=1)
            self.acb2[i].grid(row=0, column=2)
            self.acb3[i].grid(row=0, column=3)
            self.acb4[i].grid(row=0, column=4)
            self.acb5[i].grid(row=0, column=5)
            p.pack()
#
# get up to date Engine info, and display to Auto Register panel
#      
            p = ControlEngine.xEngine()
            p.UpdateInfo(i, 'cmg')
            self.DB2Panel_ART(i)
#
#
# frame 3 (Initial Mirror Set)
#
#       np3
#           np3_p[engines]
#               +---------------------------------------------------------------+
#               |   Mirror Structure    |   Primary WWPN    |   Secondary WWPN  |
#               |                       |       <   >       |       <   >       |
#               |                       |-------------------|-------------------|
#           f1  |                       |   selectable t#   |   selectable t#   |
#               |                       |                   |                   |
#               |                       |                   |                   |
#               |---------------------------------------------------------------|
#           f2  |      Mirrored LUN     |   primary LUN     |   secondary LUN   |
#               |---------------------------------------------------------------|
#           f3  |               [Enter][Submit][Erase][Cancel]                  |
#               |---------------------------------------------------------------|
#
# frame 3 (Mirror Manager)
        np3 = ttk.Notebook(frame_3)
        np3.pack(fill='both', expand='yes')
        
        np3_p = [0 for x in range(engine_number)]
        self.p_variable_ps = [0 for x in range(engine_number)]
        self.p_variable_ss = [0 for x in range(engine_number)]

        self.mmtv_ms = [0 for x in range(engine_number)]    # Mirror Manager Tree View for Mirror Structure
        self.mmtv_ps = [0 for x in range(engine_number)]    # Mirror Manager Tree View for Primary Storage
        self.mmtv_ss = [0 for x in range(engine_number)]    # Mirror Manager Tree View for Secondary Storage
        self.mmtv_spl = [0 for x in range(engine_number)]   # Mirror Manager Tree View for Selected Primary LUN
        self.mmtv_ssl = [0 for x in range(engine_number)]   # Mirror Manager Tree View for Selected Secondary LUN
        self.mmtv_sml = [0 for x in range(engine_number)]   # Mirror Manager Tree View for Selected Mirror LUN

        for i in range (engine_number):
            
            np3_p[i] = ttk.Frame(frame_3)
            np3_p[i].pack()
            np3.add(np3_p[i], text='   Engine %s   ' % i)
#
            p = ttk.Panedwindow(np3_p[i], orient=Tkinter.VERTICAL)
            f1 = ttk.Frame(p)
            f2 = ttk.Frame(p)
            f3 = ttk.Frame(p)
            p.add(f1)
            p.add(f2)
            p.add(f3)
            p.pack()
#
            p = ttk.Panedwindow(f1, orient=Tkinter.HORIZONTAL)

            if current_engine[i][0] != 'on':
                tf = Tkinter.Label(p, text="\n"*10 + "This Engine is offline.", justify = Tkinter.CENTER,
                     bg = "#d8d8d8")
                p.add(tf)
                p.pack()
                continue

            if engine_info[i]['Master'] != "M":
                tf = Tkinter.Label(p, text="\n"*10 + "This is not a Master Engine"+
                        "\n(Mirror Manager must run on Master Engine)", justify = Tkinter.CENTER,
                        bg = "#d8d8d8")
                p.add(tf)
                p.pack()
                continue
                
            f1_1 = ttk.Labelframe(p, text="Mirror Member")
            f1_2 = ttk.Labelframe(p, text="Mirror Structure")
            p.add(f1_2)
            p.add(f1_1)
            p.pack()
            
            self.mmtv_ms[i] = ttk.Treeview(f1_2, height=20, padding = (0,2,0,2))
            self.mmtv_ms[i]["columns"]=('#1', '#2', '#3', '#4', '#5', '#6')
            self.mmtv_ms[i].column("#0", width=60, anchor=Tkinter.E)
            self.mmtv_ms[i].column("#1", width=40, anchor=Tkinter.CENTER)
            self.mmtv_ms[i].column("#2", width=150, anchor=Tkinter.E)
            self.mmtv_ms[i].column("#3", width=40, anchor=Tkinter.CENTER)
            self.mmtv_ms[i].column("#4", width=40, anchor=Tkinter.CENTER)
            self.mmtv_ms[i].column("#5", width=40, anchor=Tkinter.CENTER)
            self.mmtv_ms[i].column("#6", width=40, anchor=Tkinter.CENTER)
            self.mmtv_ms[i].heading("#0", text="Tnum")
            self.mmtv_ms[i].heading("#1", text="map")
            self.mmtv_ms[i].heading("#2", text="Capacity")
            self.mmtv_ms[i].heading("#3", text="Pri T#")
            self.mmtv_ms[i].heading("#4", text="Pri St")
            self.mmtv_ms[i].heading("#5", text="Sec T#")
            self.mmtv_ms[i].heading("#6", text="Sec St")
            self.mmtv_ms[i].insert("", 0, text="-", values=("-", "-      ", "-", "-", "-", "-"))

            self.MSTonDoubleClick_with_arg = functools.partial (self.__MSTonDoubleClick, i)
            self.mmtv_ms[i].bind("<Double-Button-1>", self.MSTonDoubleClick_with_arg)
            ttk.Style().configure("Treeview", background="light gray", fieldbackground="light gray")
            self.mmtv_ms[i].pack(expand=YES, fill=Tkinter.BOTH)

            self.__DB2Panel_MST(i)

            p = ttk.Panedwindow(f1_1, orient=Tkinter.HORIZONTAL)
            f1_1_1 = ttk.Labelframe(p, text="")
            f1_1_2 = ttk.Labelframe(p, text="")
            p.add(f1_1_1)
            p.add(f1_1_2)
            p.pack()
#
            p = ttk.Panedwindow(f1_1_1, orient=Tkinter.VERTICAL)
            f1_1_1_1 = ttk.Labelframe(p, text="Primary Storage")
            f1_1_1_1.pack()
            f1_1_1_2 = ttk.Labelframe(p, text="Available LUNs")
            f1_1_1_2.pack()
            p.add(f1_1_1_1)
            p.add(f1_1_1_2)
            p.pack()
            
            option_list_ps = []
            for wwpn in engine_info[i]['Registered']['Drive'].keys():
                option_list_ps.append(wwpn)           
            
            self.p_variable_ps[i] = Tkinter.StringVar(f1_1_1_1)
            if option_list_ps != []:
                self.p_variable_ps[i].set(option_list_ps[0])
                om = Tkinter.OptionMenu(f1_1_1_1, self.p_variable_ps[i], *option_list_ps)
            else: 
                self.p_variable_ps[i].set("")
                om = Tkinter.OptionMenu(f1_1_1_1, self.p_variable_ps[i], "")
            om.config(font=('Courier',(14)), bg="light gray", width=30)
            om['menu'].config(font=('Courier',(12)))
            om.grid(row=0, column=0)

            self.OptionList_ps_ok_with_arg = functools.partial (self.__OptionList_ps_ok, i)
            b = ttk.Button(f1_1_1_1, text="OK", command = self.OptionList_ps_ok_with_arg)
            b.grid(row=0, column=1)
#
            self.mmtv_ps[i] = ttk.Treeview(f1_1_1_2, height=15, padding = (0,2,0,2))
            self.mmtv_ps[i]["columns"]=('#1', '#2', '#3', '#4')
            self.mmtv_ps[i].column("#0", width=70, anchor=Tkinter.W)
            self.mmtv_ps[i].column("#1", width=40, anchor=Tkinter.CENTER)
            self.mmtv_ps[i].column("#2", width=50, anchor=Tkinter.CENTER)
            self.mmtv_ps[i].column("#3", width=160, anchor=Tkinter.E)
            self.mmtv_ps[i].column("#4", width=40, anchor=Tkinter.CENTER)
            self.mmtv_ps[i].heading("#0", text="Tnum")
            self.mmtv_ps[i].heading("#1", text="Port")
            self.mmtv_ps[i].heading("#2", text="LUN")
            self.mmtv_ps[i].heading("#3", text="Capacity")
            self.mmtv_ps[i].heading("#4", text="Status")
            self.mmtv_ps[i].insert("", 0, text="-", values=("-", "-", "-", "-"))

            self.PSTonDoubleClick_with_arg = functools.partial (self.__PSTonDoubleClick, i)
            self.mmtv_ps[i].bind("<Double-Button-1>", self.PSTonDoubleClick_with_arg)
            ttk.Style().configure("Treeview", background="light gray", fieldbackground="light gray")
            self.mmtv_ps[i].pack(expand=YES, fill=Tkinter.BOTH)

            p = ttk.Panedwindow(f1_1_2, orient=Tkinter.VERTICAL)
            f1_1_2_1 = ttk.Labelframe(p, text="Secondary Storage")
            f1_1_2_1.pack()
            f1_1_2_2 = ttk.Labelframe(p, text="Available LUNs")
            f1_1_2_2.pack()
            p.add(f1_1_2_1)
            p.add(f1_1_2_2)
            p.pack()
            
            option_list_ss = []
            
            for wwpn in engine_info[i]['Registered']['Drive'].keys():
                option_list_ss.append(wwpn)           
            
            self.p_variable_ss[i] = Tkinter.StringVar(f1_1_2_1)
            if option_list_ss != []:
                self.p_variable_ss[i].set(option_list_ss[len(option_list_ss)-1])
                om = Tkinter.OptionMenu(f1_1_2_1, self.p_variable_ss[i], *option_list_ss)
            else: 
                self.p_variable_ss[i].set("")
                om = Tkinter.OptionMenu(f1_1_2_1, self.p_variable_ss[i], "")
            om.config(font=('Courier',(14)), bg="light gray", width=30)
            om['menu'].config(font=('Courier',(12)))
            om.grid(row=0, column=0)
            
            self.OptionList_ss_ok_with_arg = functools.partial (self.__OptionList_ss_ok, i)
            b = ttk.Button(f1_1_2_1, text="OK", command = self.OptionList_ss_ok_with_arg)
            b.grid(row=0, column=1)
            
            self.mmtv_ss[i] = ttk.Treeview(f1_1_2_2, height=15, padding = (0,2,0,2))
            self.mmtv_ss[i]["columns"]=('#1', '#2', '#3', '#4')
            self.mmtv_ss[i].column("#0", width=70, anchor=Tkinter.CENTER)
            self.mmtv_ss[i].column("#1", width=40, anchor=Tkinter.CENTER)
            self.mmtv_ss[i].column("#2", width=50, anchor=Tkinter.CENTER)
            self.mmtv_ss[i].column("#3", width=160, anchor=Tkinter.E)
            self.mmtv_ss[i].column("#4", width=40, anchor=Tkinter.CENTER)
            self.mmtv_ss[i].heading("#0", text="Tnum")
            self.mmtv_ss[i].heading("#1", text="Port")
            self.mmtv_ss[i].heading("#2", text="LUN")
            self.mmtv_ss[i].heading("#3", text="Capacity")
            self.mmtv_ss[i].heading("#4", text="Status")
            self.mmtv_ss[i].insert("", 0, text="-", values=("-", "-", "-", "-"))

            self.SSTonDoubleClick_with_arg = functools.partial (self.__SSTonDoubleClick, i)
            self.mmtv_ss[i].bind("<Double-Button-1>", self.SSTonDoubleClick_with_arg)
            ttk.Style().configure("Treeview", background="light gray", fieldbackground="light gray")
            self.mmtv_ss[i].pack(expand=YES, fill=Tkinter.BOTH)
#
            p = ttk.Panedwindow(f2, orient=Tkinter.HORIZONTAL)
            f2_1 = ttk.Labelframe(p, text="Selected Primary LUN")
            f2_2 = ttk.Labelframe(p, text="Selected Secondary LUN")
            f2_3 = ttk.Labelframe(p, text="Selected Mirror LUN")
            p.add(f2_3)
            p.add(f2_1)
            p.add(f2_2)
            p.pack()
#
            self.mmtv_spl[i] = ttk.Treeview(f2_1, height=1, padding = (0,2,0,2))
            self.mmtv_spl[i]["columns"]=('#1', '#2', '#3', '#4')
            self.mmtv_spl[i].column("#0", width=70, anchor=Tkinter.CENTER)
            self.mmtv_spl[i].column("#1", width=40, anchor=Tkinter.CENTER)
            self.mmtv_spl[i].column("#2", width=55, anchor=Tkinter.CENTER)
            self.mmtv_spl[i].column("#3", width=160, anchor=Tkinter.E)
            self.mmtv_spl[i].column("#4", width=40, anchor=Tkinter.CENTER)
            self.mmtv_spl[i].heading("#0", text="Tnum")
            self.mmtv_spl[i].heading("#1", text="Port")
            self.mmtv_spl[i].heading("#2", text="LUN")
            self.mmtv_spl[i].heading("#3", text="Capacity")
            self.mmtv_spl[i].heading("#4", text="Status")

#            self.mmtv_spl[i].bind("<Double-Button-1>", self.__EngineInfoOnMotion)
#            ttk.Style().configure("Treeview", background="light gray", fieldbackground="light gray")
            self.mmtv_spl[i].pack(expand=YES, fill=Tkinter.BOTH)
#
            self.mmtv_ssl[i] = ttk.Treeview(f2_2, height=1, padding = (0,2,0,2))
            self.mmtv_ssl[i]["columns"]=('#1', '#2', '#3', '#4')
            self.mmtv_ssl[i].column("#0", width=70, anchor=Tkinter.CENTER)
            self.mmtv_ssl[i].column("#1", width=40, anchor=Tkinter.CENTER)
            self.mmtv_ssl[i].column("#2", width=55, anchor=Tkinter.CENTER)
            self.mmtv_ssl[i].column("#3", width=160, anchor=Tkinter.E)
            self.mmtv_ssl[i].column("#4", width=40, anchor=Tkinter.CENTER)
            self.mmtv_ssl[i].heading("#0", text="Tnum")
            self.mmtv_ssl[i].heading("#1", text="Port")
            self.mmtv_ssl[i].heading("#2", text="LUN")
            self.mmtv_ssl[i].heading("#3", text="Capacity")
            self.mmtv_ssl[i].heading("#4", text="Status")

#            self.mmtv_ssl[i].bind("<Double-Button-1>", self.__EngineInfoOnMotion)
#            ttk.Style().configure("Treeview", background="light gray", fieldbackground="light gray")
            self.mmtv_ssl[i].pack(expand=YES, fill=Tkinter.BOTH)
#
            self.mmtv_sml[i] = ttk.Treeview(f2_3, height=1, padding = (0,2,0,2))
            self.mmtv_sml[i]["columns"]=('#1', '#2', '#3', '#4')
            self.mmtv_sml[i].column("#0", width=70, anchor=Tkinter.CENTER)
            self.mmtv_sml[i].column("#1", width=60, anchor=Tkinter.CENTER)
            self.mmtv_sml[i].column("#2", width=60, anchor=Tkinter.CENTER)
            self.mmtv_sml[i].column("#3", width=170, anchor=Tkinter.E)
            self.mmtv_sml[i].column("#4", width=50, anchor=Tkinter.CENTER)
            self.mmtv_sml[i].heading("#0", text="Tnum")
            self.mmtv_sml[i].heading("#1", text="Pri T#")
            self.mmtv_sml[i].heading("#2", text="Sec T#")
            self.mmtv_sml[i].heading("#3", text="Capacity")
            self.mmtv_sml[i].heading("#4", text="Status")

#            self.mmtv_sml[i].bind("<Double-Button-1>", self.__EngineInfoOnMotion)
#            ttk.Style().configure("Treeview", background="light gray", fieldbackground="light gray")
            self.mmtv_sml[i].pack(expand=YES, fill=Tkinter.BOTH)
#
            p = ttk.Frame(f3)

            ClearSelection_with_arg = functools.partial (self.__ClearSelection, i)
            CreateMirror_with_arg = functools.partial (self.__CreateMirror, i)
            CreateMirrorNR_with_arg = functools.partial (self.__CreateMirrorNR, i)
            AddMirror_with_arg = functools.partial (self.__AddMirror, i)
            BreakMirror_with_arg = functools.partial (self.__BreakMirror, i)
            CloseConfiguration_with_arg = functools.partial (self.__CloseConfiguration, i)

            b1 = ttk.Button(p, text="Clear Selection", width = 20, command=ClearSelection_with_arg)
            b2 = ttk.Button(p, text="Create Mirror (normal)", width = 22, command=CreateMirror_with_arg)
            b3 = ttk.Button(p, text="Create Mirror w/out Rebuild", width = 22, command=CreateMirrorNR_with_arg)
            b4 = ttk.Button(p, text="Add Mirror", width = 20, command=AddMirror_with_arg)
            b5 = ttk.Button(p, text="Break Mirror", width = 20, command=BreakMirror_with_arg)
            b6 = ttk.Button(p, text="Close Configuration", width = 20, command=CloseConfiguration_with_arg)

            b1.grid(row=0, column=0)
            b2.grid(row=0, column=1)
            b3.grid(row=0, column=2)
            b4.grid(row=0, column=3)
            b5.grid(row=0, column=4)
            b6.grid(row=0, column=5)
            
            p.pack()        
#
# update Registered Drives
#
            self.__OptionList_ps_ok(i)
            self.__OptionList_ss_ok(i)
#
#
# frame 4 (Host-Map Grouping)
#
#       np4
#           np4_p[engines]
#               +---------------------------------------------------------------+
#               |      LUN Map Group       |            Host Group              |
#               |--------------------------|------------------------------------|
#           f1  |                          |                                    |
#               |        f1_1              |             f1_2                   |
#               |                          |                                    |
#               |--------------------------|------------------------------------|
#           f2  | Available HBA | Available|Group |Available LUN | Available ID | f2_1_1, f2_2_1, f2_3_1, f2_4_1
#               |--------------------------+------------------------------------|
#           f3  |                    [Submit][Erase][Cancel]                    |
#               |---------------------------------------------------------------|
#
# frame 4 (Host-Map Grouping)
        np4 = ttk.Notebook(frame_4)
        np4.pack(fill='both', expand='yes')
        
        np4_p = [0 for x in range(engine_number)]
        self.pvar_init_group = [0 for x in range(engine_number)]
        self.pvar_lun = [0 for x in range(engine_number)]
        self.pvar_hba = [0 for x in range(engine_number)]
        self.pvar_hbag = [0 for x in range(engine_number)]
        self.pvar_mcmd = [0 for x in range(engine_number)]
        self.pvar_hcmd = [0 for x in range(engine_number)]
        self.pvar_amap = [0 for x in range(engine_number)]
        self.pvar_maps = [0 for x in range(engine_number)]
        self.bb2 = [0 for x in range(engine_number)]
        self.bb3 = [0 for x in range(engine_number)]

        self.hltv_hg = [0 for x in range(engine_number)]    # Host LUN Tree View for Host Group table
        self.hltv_lm = [0 for x in range(engine_number)]    # Host LUN Tree View for LUN Map table
#
        for i in range (engine_number):
            
            np4_p[i] = ttk.Frame(frame_4)
            np4_p[i].pack()
            np4.add(np4_p[i], text='   Engine %s   ' % i)
#
            p = ttk.Panedwindow(np4_p[i], orient=Tkinter.VERTICAL)
            f1 = ttk.Frame(p) #, text="Display Panel")
            f2 = ttk.Frame(p) #, text="Execution Panel")
            p.add(f1)
            p.add(f2)
            p.pack()
#
            p = ttk.Panedwindow(f1, orient=Tkinter.HORIZONTAL)

            if current_engine[i][0] != 'on':
                tf = Tkinter.Label(p, text="\n"*10 + "This Engine is offline.", justify = Tkinter.CENTER,
                     bg = "#d8d8d8")
                p.add(tf)
                p.pack()
                continue
#
            if engine_info[i]['Master'] != "M":
                tf = Tkinter.Label(p, text="\n"*10 + "This is not a Master Engine"+
                        "\n(Mirror Manager must run on Master Engine)", justify = Tkinter.CENTER,
                        bg = "#d8d8d8")
                p.add(tf)
                p.pack()
                continue
#
            f1_1 = ttk.Labelframe(p, text="LUN-Map Structure")
            f1_2 = ttk.Labelframe(p, text="Initiator HBA Group")
            p.add(f1_1)
            p.add(f1_2)
            p.pack()
#
# Setup LUN-Map
# 
            p = ttk.Panedwindow(f1_1, orient=Tkinter.VERTICAL)
            f1_1_1 = ttk.Frame(p) #, text="Program Panel")
            f1_1_2 = ttk.Frame(p) #, text="Execution Panel")
            p.add(f1_1_1)
            p.add(f1_1_2)
            p.pack()            
#
            self.hltv_lm[i] = ttk.Treeview(f1_1_1, height=20, padding = (0,2,0,2))
            self.hltv_lm[i]["columns"]=('#1', '#2', '#3', '#4', '#5', '#6')
            self.hltv_lm[i].column("#0", width=10, anchor=Tkinter.CENTER)
            self.hltv_lm[i].column("#1", width=10, anchor=Tkinter.CENTER)
            self.hltv_lm[i].column("#2", width=80, anchor=Tkinter.CENTER)
            self.hltv_lm[i].column("#3", width=10, anchor=Tkinter.CENTER)
            self.hltv_lm[i].column("#4", width=80, anchor=Tkinter.CENTER)
            self.hltv_lm[i].column("#5", width=80, anchor=Tkinter.E)
            self.hltv_lm[i].column("#6", width=10, anchor=Tkinter.CENTER)
            self.hltv_lm[i].heading("#0", text="LUN ID")            
            self.hltv_lm[i].heading("#1", text="Map #")
            self.hltv_lm[i].heading("#2", text="Map Structure Name")
            self.hltv_lm[i].heading("#3", text="Mirror #")
            self.hltv_lm[i].heading("#4", text="Mirror LUN Name")
            self.hltv_lm[i].heading("#5", text="Capacity")
            self.hltv_lm[i].heading("#6", text="Status")
            self.hltv_lm[i].insert("", 0, text="-", values=("-", "-", "-", "-"))

            self.HGTonDoubleClick_with_arg = functools.partial (self.__HGTonDoubleClick, i)
            self.hltv_lm[i].bind("<Double-Button-1>", self.HGTonDoubleClick_with_arg)
            self.hltv_lm[i].pack(expand=YES, fill=Tkinter.BOTH)
#
            self.__UpdateLMT(i)
#
            b1 = ttk.Labelframe(f1_1_2, text= "Map Structure")
            b2 = ttk.Labelframe(f1_1_2, text= "Selected LUN")
            self.b3 = ttk.Labelframe(f1_1_2, text= "Selected HBA Group")
            b4 = ttk.Labelframe(f1_1_2, text= "Command")
            b5 = ttk.Labelframe(f1_1_2, text= "")
            b1.grid(row=0, column=0)
            b2.grid(row=0, column=1)
            self.b3.grid(row=0, column=2)
            b4.grid(row=0, column=3)
            b5.grid(row=0, column=4)
            
            self.pvar_maps[i] = Tkinter.StringVar()
            bb1 = Tkinter.Entry(b1, width=12, textvariable=self.pvar_maps[i])
#
            list_of_lun = ["--NULL--"]     # Available LUNs
            
            for mirror_id in engine_info[i]['Mirror']:
                mirror_name = self.__GetName(i, mirror_id)
                if mirror_name == '': list_of_lun.append(mirror_id)
                else: list_of_lun.append(mirror_id+' : '+mirror_name)

            self.pvar_lun[i] = Tkinter.StringVar()
            self.pvar_lun[i].set(list_of_lun[0])
            self.bb2[i] = Tkinter.OptionMenu(b2, self.pvar_lun[i], *list_of_lun)
            self.bb2[i].config(font=('Courier',(14)), bg="light gray", width=20)
            self.bb2[i]['menu'].config(font=('Courier',(12)))
#
            list_of_hbag = ["--NULL--"]      # Available HBA Group

            for hba_group in engine_info[i]['Group']['HBA']:
                list_of_hbag.append('HBA group #%s' % hba_group)
            
            self.pvar_hbag[i] = Tkinter.StringVar()
            self.pvar_hbag[i].set(list_of_hbag[0])
            self.bb3[i] = Tkinter.OptionMenu(self.b3, self.pvar_hbag[i], *list_of_hbag)
            self.bb3[i].config(font=('Courier',(14)), bg="light gray", width=16)
            self.bb3[i]['menu'].config(font=('Courier',(12)))
#
            list_of_cmd = ["Add", "Delete", "Skip"]   
            self.pvar_mcmd[i] = Tkinter.StringVar()
            self.pvar_mcmd[i].set(list_of_cmd[0])
            bb4 = Tkinter.OptionMenu(b4, self.pvar_mcmd[i], *list_of_cmd)
            bb4.config(font=('Courier',(14)), bg="light gray", width=10)
            bb4['menu'].config(font=('Courier',(12)))

            ConfirmHName_with_arg = functools.partial (self.__ConfirmMMap, i)
            bb5 = ttk.Button(b5, text="OK", width=4, command=ConfirmHName_with_arg)
            bb1.pack(side = Tkinter.LEFT)
            self.bb2[i].pack(side = Tkinter.LEFT)
            self.bb3[i].pack(side = Tkinter.LEFT)
            bb4.pack(side = Tkinter.LEFT)
            bb5.pack()
#
# Setup HBA Group
#
            p = ttk.Panedwindow(f1_2, orient=Tkinter.VERTICAL)
            f1_2_1 = ttk.Frame(p) #, text="Program Panel")
            f1_2_2 = ttk.Frame(p) #, text="Execution Panel")
            p.add(f1_2_1)
            p.add(f1_2_2)
            p.pack()            
#
            self.hltv_hg[i] = ttk.Treeview(f1_2_1, height=20, padding = (0,2,0,2))
            self.hltv_hg[i]["columns"]=('#1', '#2', '#3', '#4', '#5', '#6')
            self.hltv_hg[i].column("#0", width=10, anchor=Tkinter.CENTER)
            self.hltv_hg[i].column("#1", width=50, anchor=Tkinter.CENTER)
            self.hltv_hg[i].column("#2", width=120, anchor=Tkinter.W)
            self.hltv_hg[i].column("#3", width=50, anchor=Tkinter.CENTER)
            self.hltv_hg[i].column("#4", width=10, anchor=Tkinter.CENTER)
            self.hltv_hg[i].column("#5", width=50, anchor=Tkinter.CENTER)
            self.hltv_hg[i].column("#6", width=10, anchor=Tkinter.CENTER)
            self.hltv_hg[i].heading("#0", text="Group #")
            self.hltv_hg[i].heading("#1", text="Group Name")
            self.hltv_hg[i].heading("#2", text="WWPN")
            self.hltv_hg[i].heading("#3", text="Initiator Name")
            self.hltv_hg[i].heading("#4", text="Map #")
            self.hltv_hg[i].heading("#5", text="Map Structure Name")
            self.hltv_hg[i].heading("#6", text="Status")
            self.hltv_hg[i].insert("", 0, text="-", values=("-", "-", "-", "-", "-"))

            self.LMTonDoubleClick_with_arg = functools.partial (self.__LMTonDoubleClick, i)
            self.hltv_hg[i].bind("<Double-Button-1>", self.LMTonDoubleClick_with_arg)
            self.hltv_hg[i].pack(expand=YES, fill=Tkinter.BOTH)
#
            self.__UpdateHGT(i)
#
            b1 = ttk.Labelframe(f1_2_2, text= "HBA Group")
            b2 = ttk.Labelframe(f1_2_2, text= "Selected HBA")
            b3 = ttk.Labelframe(f1_2_2, text= "Command")
            b4 = ttk.Labelframe(f1_2_2, text= "")
            b1.grid(row=0, column=0)
            b2.grid(row=0, column=1)
            b3.grid(row=0, column=2)
            b4.grid(row=0, column=3)
            
            self.pvar_init_group[i] = Tkinter.StringVar()
            bb1 = Tkinter.Entry(b1, width=12, textvariable=self.pvar_init_group[i])
#
            list_of_hba = ["--NULL--"]      # Available HBAs

            for wwpn in engine_info[i]['Registered']['Initiator']:
                init_name = self.__GetName(i, wwpn)
                if init_name == '': list_of_hba.append(wwpn)
                else: list_of_hba.append(wwpn+' : '+init_name)
            
            self.pvar_hba[i] = Tkinter.StringVar()
            self.pvar_hba[i].set(list_of_hba[0])
            bb2 = Tkinter.OptionMenu(b2, self.pvar_hba[i], *list_of_hba)
            bb2.config(font=('Courier',(14)), bg="light gray", width=30)
            bb2['menu'].config(font=('Courier',(12)))
#
            list_of_cmd = ["Add", "Delete"]   
            self.pvar_hcmd[i] = Tkinter.StringVar()
            self.pvar_hcmd[i].set(list_of_cmd[0])
            bb3 = Tkinter.OptionMenu(b3, self.pvar_hcmd[i], *list_of_cmd)
            bb3.config(font=('Courier',(14)), bg="light gray", width=10)
            bb3['menu'].config(font=('Courier',(12)))
#
            ConfirmHGroup_with_arg = functools.partial (self.__ConfirmHGroup, i)
            bb4 = ttk.Button(b4, text="OK", width=4, command=ConfirmHGroup_with_arg)
            bb1.pack(side = Tkinter.LEFT)
            bb2.pack(side = Tkinter.LEFT)
            bb3.pack(side = Tkinter.LEFT)
            bb4.pack()
#
# Setup Execution Buttons
#
            p = ttk.Panedwindow(f2, orient=Tkinter.HORIZONTAL)
            f2_1 = ttk.Frame(p)
            f2_2 = ttk.Frame(p)
            p.add(f2_1)
            p.add(f2_2)
            p.pack()
            
            ClearSelection_with_arg = functools.partial (self.__ClearSelection, i)
            CloseConfiguration_with_arg = functools.partial (self.__CloseConfiguration, i)

            b1 = ttk.Button(f2_1, text="Clear Selection", width = 24, command=ClearSelection_with_arg)
            b2 = ttk.Button(f2_1, text="Close Configuration", width = 24, command=CloseConfiguration_with_arg)

            b1.grid(row=0, column=0)
            b2.grid(row=0, column=1)
#
            s1 = ttk.Frame(f2_2)
#
            self.pls_amap = ["Auto Map: Enable", "Auto Map: Disable"]
            self.pvar_amap[i] = Tkinter.StringVar()

            if engine_info[i]['AutoMap'] == 'Enabled':
                self.pvar_amap[i].set(self.pls_amap[0])
            elif engine_info[i]['AutoMap'] == 'Disabled':
                self.pvar_amap[i].set(self.pls_amap[1])
            else:
                self.pvar_amap[i].set('')
                
            s1 = Tkinter.OptionMenu(f2_2, self.pvar_amap[i], *self.pls_amap)
            s1.config(font=('Courier',(14)), bg="light gray", width=20)
            s1['menu'].config(font=('Courier',(12)))
#
            ConfirmAMAP_with_arg = functools.partial (self.__ConfirmAMAP, i)
            s2 = ttk.Button(f2_2, text="OK", width=4, command=ConfirmAMAP_with_arg)
#
            s1.grid(row=0, column=0)
            s2.grid(row=0, column=1)
#
# get last info from file            
#
#            self.GetLastCmgInfo(i)
#            self.__OptionList_ps_ok(i)
#            self.__OptionList_ss_ok(i)
#
# frame 5 (Licenses & Mode)
#
#       np5
#           np5_p[engines]
#                          f1                               f2
#                                            f2_1_1         f2_1_2       f2_1_3
#               +-----------------------|---------------------------------------+
#               |  licensed installed   | Mode Status | Mode Selection | Action |  f2_1
#               |                       |---------------------------------------|
#       f1_1    |                       |                                       |  f2_2
#               |                       |---------------------------------------|
#               |                       |                                       |  f2_3
#               |-----------------------|---------------------------------------|
#       f1_2    |   <add new license>   |                                       |
#               |-----------------------|---------------------------------------|
#       f1_3    |   [Cancel][Submit]    |                                       |
#               |-----------------------|---------------------------------------|
#
# frame 5 (Licenses & Mode)
#
        np5 = ttk.Notebook(frame_5)
        np5.pack(fill='both', expand='yes')
        
        np5_p = [0 for x in range(engine_number)]
        self.license_key = [0 for x in range(engine_number)]
        self.feature_no = [0 for x in range(engine_number)]
        self.license_var = [0 for x in range(engine_number)]

        MSLOT = 8
        self.rbvar = [[0 for x in range(MSLOT)] for x in range(engine_number)]
        self.status_var = [[0 for x in range(MSLOT)] for x in range(engine_number)]

        for i in range (engine_number):
            np5_p[i] = ttk.Frame(frame_5)
            np5_p[i].pack()
            np5.add(np5_p[i], text='   Engine %s   ' % i)
#
            p = ttk.Panedwindow(np5_p[i], orient=Tkinter.HORIZONTAL)
            
            if current_engine[i][0] != 'on':
                tf = Tkinter.Label(p, text="\n"*10 + "This Engine is offline.", justify = Tkinter.CENTER,
                     bg = "#d8d8d8")
                p.add(tf)
                p.pack()
                continue
                
            f1 = ttk.Labelframe(p, text=" Licenses Installed")
            f2 = ttk.Labelframe(p, text=" Special Modes Setting")
            p.add(f1)
            p.add(f2)
            p.pack()
#
# set up F1
            p = ttk.Panedwindow(f1, orient=Tkinter.VERTICAL)
            f1_1 = ttk.Frame(p, width=LF_WIDTH-16, height=LF_HEIGHT-30)
            f1_1.pack_propagate(0)
            f1_2 = ttk.Labelframe(p, text="Add New License")
            f1_3 = ttk.Frame(p)
            p.add(f1_1)
            p.add(f1_2)
            p.add(f1_3)
            p.pack()
#
# New License to add
            p0 = ttk.Label(f1_2, text="PCB #" + engine_info[i]['PCBnumber'])
            p0.grid(row=0, column=3)
            p1 = ttk.Label(f1_2, text="  #")
            self.feature_no[i] = Tkinter.Entry(f1_2, bd = 2, bg = '#d8d8d8', width = 4)
            p2 = ttk.Label(f1_2, text="  KEY")
            self.license_key[i] = Tkinter.Entry(f1_2, bd = 2, bg = '#d8d8d8', width = 20)
            p1.grid(row=1, column=0)
            self.feature_no[i].grid(row=1, column=1)
            p2.grid(row=1, column=2)
            self.license_key[i].grid(row=1, column=3)
#
# Action Buttons
            SubmitNewLicense_with_arg = functools.partial (self.__SubmitNewLicense, i)
            b1 = ttk.Button(f1_3, text="Cancel", width = B_WIDTH, command=self.__CloseHandler)
            b2 = ttk.Button(f1_3, text="Submit", width = B_WIDTH, command=SubmitNewLicense_with_arg)
            b1.grid(row=0, column=0)
            b2.grid(row=0, column=1)
#
# Update .cmg file to get all the up to date Special Mode info
#
#            p = ControlEngine.xEngine()
#            if p.UpdateInfo(i, 'cmg') == False:
#                thread.start_new_thread( tkMessageBox.showinfo, ("Special Mode", "Failed to update .cmg file."))    
#
# get current license info from database
#
            self.license_var[i] = Tkinter.StringVar()
            ll = Tkinter.Label(f1_1, textvariable=self.license_var[i], bg = '#d8d8d8')
            ll.pack()

            text = ""
            for j in range (len(engine_info[i]['License'])):
                text = text + engine_info[i]['License'][j] + "\n"
            self.license_var[i].set(text[:-1])
#
# Initialize the Special Mode Panel - F2
#
            f2_ = [0 for x in range(MSLOT)]
            
            p = ttk.Panedwindow(f2, orient=Tkinter.VERTICAL)            
            for j in range (MSLOT):
                f2_[j] = ttk.Frame(p)
                p.add(f2_[j])
            p.pack()
#
            j = 0
            for item in engine_info[i]['Application']:
                pd = ttk.Frame(f2_[j], width=20)
                pd.grid(row=0, column=0)
        
                SubmitNewMode_with_arg = functools.partial (self.__SubmitNewMode, i, j, item)
                b = ttk.Button(f2_[j], text="Change", width = 10, command=SubmitNewMode_with_arg)
                b.grid(row=0, column=1)

                pd = ttk.Frame(f2_[j], width=20)
                pd.grid(row=0, column=2)

                f2_1_1 = ttk.Label(f2_[j], text=item, width=20)
                f2_1_1.grid(row=0, column=3)
            
                self.status_var[i][j] = Tkinter.StringVar()
                f2_1_1 = ttk.Label(f2_[j], textvariable=self.status_var[i][j], width=15)
                self.status_var[i][j].set(engine_info[i]['Application'][item])
                f2_1_1.grid(row=0, column=4)

                self.MODES = [('ON', '0'), ('OFF', '1')]
                self.rbvar[i][j] = Tkinter.IntVar()
            
                k = 1
                for text, mode in self.MODES:
                    r = Tkinter.Radiobutton(f2_[j], text=text, variable=self.rbvar[i][j], value=mode, bg = '#d8d8d8')
                    r.grid(row=0, column=k+4)
                    r.deselect()
                    k += 1
                j += 1
#
# frame 6 (Name Manager)
#
#       np6
#           np6_p[engines]
#               +-----------------------+------------------+---------------------+
#               |      HBA Name         |    Group Name    |      LUN Name       |
#               |-----------------------|------------------|---------------------|
#               |                       |                  |                     |
#               |        f1_1_1         |       f1_2_1     |        f1_3_1       |
#               |                       |                  |                     |
#           f1  |-----------------------|------------------|---------------------|
#               | Prog HBA name f1_1_2  | Prog Group Name  | Prog LUN Name       | f2_1_1, f2_2_1, f2_3_1, f2_4_1
#               |-----------------------+------------------+---------------------|
#           f2  |                    [Submit][Erase][Cancel]                     |
#               |----------------------------------------------------------------|
#
# frame 6 (Name Manager)
        np6 = ttk.Notebook(frame_6)
        np6.pack(fill='both', expand='yes')
        
        np6_p = [0 for x in range(engine_number)]
        self.p_variable_hi = [0 for x in range(engine_number)]  # HBA ID
        self.p_variable_hn = [0 for x in range(engine_number)]  # HBA Name
 
        self.p_variable_gi = [0 for x in range(engine_number)]  # Group ID
        self.p_variable_gn = [0 for x in range(engine_number)]  # Group Name

        self.p_variable_li = [0 for x in range(engine_number)]  # LUN ID
        self.p_variable_ln = [0 for x in range(engine_number)]  # LUN Name

        self.nmtv_hn = [0 for x in range(engine_number)]    # HBA Name Tree View for Host Group table
        self.nmtv_gn = [0 for x in range(engine_number)]    # Group Name Tree View for LUN Map table
        self.nmtv_ln = [0 for x in range(engine_number)]    # LUN Name Tree View for LUN Map table
#
        for i in range (engine_number):
            
            np6_p[i] = ttk.Frame(frame_6)
            np6_p[i].pack()
            np6.add(np6_p[i], text='   Engine %s   ' % i)
#
            p = ttk.Panedwindow(np6_p[i], orient=Tkinter.VERTICAL)
            f1 = ttk.Frame(p) #, text="Program Panel")
            f2 = ttk.Frame(p) #, text="Execution Panel")
            p.add(f1)
            p.add(f2)
            p.pack()
#
            p = ttk.Panedwindow(f1, orient=Tkinter.HORIZONTAL)

            if current_engine[i][0] != 'on':
                tf = Tkinter.Label(p, text="\n"*10 + "This Engine is offline.", justify = Tkinter.CENTER,
                     bg = "#d8d8d8")
                p.add(tf)
                p.pack()
                continue
#
            if engine_info[i]['Master'] != "M":
                tf = Tkinter.Label(p, text="\n"*10 + "This is not a Master Engine"+
                        "\n(Name Manager must run on Master Engine)", justify = Tkinter.CENTER,
                        bg = "#d8d8d8")
                p.add(tf)
                p.pack()
                continue
#
            f1_1 = ttk.Labelframe(p, text="Host Name")
            f1_2 = ttk.Labelframe(p, text="Group Name")
            f1_3 = ttk.Labelframe(p, text="LUN Name")
            p.add(f1_1)
            p.add(f1_2)
            p.add(f1_3)
            p.pack()
#
# HBA Name
#
            p = ttk.Panedwindow(f1_1, orient=Tkinter.VERTICAL)
            f1_1_1 = ttk.Frame(p) #, text="Program Panel")
            f1_1_2 = ttk.Frame(p) #, text="Execution Panel")
            p.add(f1_1_1)
            p.add(f1_1_2)
            p.pack()            

            self.nmtv_hn[i] = ttk.Treeview(f1_1_1, height=20, padding = (0,2,0,2))
            self.nmtv_hn[i]["columns"]=('#1', '#2')
            self.nmtv_hn[i].column("#0", width=8, anchor=Tkinter.CENTER)
            self.nmtv_hn[i].column("#1", width=80, anchor=Tkinter.W)
            self.nmtv_hn[i].column("#2", width=100, anchor=Tkinter.CENTER)
            self.nmtv_hn[i].heading("#0", text="Initiator #")
            self.nmtv_hn[i].heading("#1", text="HBA ID")
            self.nmtv_hn[i].heading("#2", text="HBA Name")
            self.nmtv_hn[i].insert("", 0, text="-", values=("-", "-"))
            self.HNTonDoubleClick_with_arg = functools.partial (self.__HNTonDoubleClick, i)
            self.nmtv_hn[i].bind("<Double-Button-1>", self.HNTonDoubleClick_with_arg)
#            ttk.Style().configure("Treeview", background="light gray", fieldbackground="light gray")
            self.nmtv_hn[i].pack(expand=YES, fill=Tkinter.BOTH)

            self.__UpdateHNT(i)

            b1 = ttk.Labelframe(f1_1_2, text= "HBA")
            b2 = ttk.Labelframe(f1_1_2, text= "Name")
            b3 = ttk.Labelframe(f1_1_2, text= "")
            b1.grid(row=0, column=0)
            b2.grid(row=0, column=1)
            b3.grid(row=0, column=2)
            
            self.p_variable_hi[i] = Tkinter.StringVar()
            bb1 = Tkinter.Entry(b1, width=14, textvariable=self.p_variable_hi[i])
            self.p_variable_hn[i] = Tkinter.StringVar()
            bb2 = Tkinter.Entry(b2, width=20, textvariable=self.p_variable_hn[i])
#            bb2 = Tkinter.Entry(b2, width=24, textvariable=self.p_variable_hn[i])
            ConfirmHName_with_arg = functools.partial (self.__ConfirmHName, i)
            bb3 = ttk.Button(b3, text="OK", width=4, command=ConfirmHName_with_arg)
            bb1.pack(side = Tkinter.LEFT)
            bb2.pack(side = Tkinter.LEFT)
            bb3.pack()
            
            self.p_variable_hi[i].set("--host ID--")
            self.p_variable_hn[i].set("--host name--")
#
# Group Name
#
            p = ttk.Panedwindow(f1_2, orient=Tkinter.VERTICAL)
            f1_2_1 = ttk.Frame(p) #, text="Program Panel")
            f1_2_2 = ttk.Frame(p) #, text="Execution Panel")
            p.add(f1_2_1)
            p.add(f1_2_2)
            p.pack()            

            self.nmtv_gn[i] = ttk.Treeview(f1_2_1, height=20, padding = (0,2,0,2))
            self.nmtv_gn[i]["columns"]=('#1', '#2')
            self.nmtv_gn[i].column("#0", width=50, anchor=Tkinter.W)
            self.nmtv_gn[i].column("#1", width=5, anchor=Tkinter.CENTER)
            self.nmtv_gn[i].column("#2", width=100, anchor=Tkinter.CENTER)
            self.nmtv_gn[i].heading("#0", text="Group Type")
            self.nmtv_gn[i].heading("#1", text="")
            self.nmtv_gn[i].heading("#2", text="Group Name")
            self.nmtv_gn[i].insert("", 0, text="-", values=("-", "-"))
            self.GNTonDoubleClick_with_arg = functools.partial (self.__GNTonDoubleClick, i)
            self.nmtv_gn[i].bind("<Double-Button-1>", self.GNTonDoubleClick_with_arg)
            self.nmtv_gn[i].pack(expand=YES, fill=Tkinter.BOTH)
            self.__UpdateGNT(i)

            b1 = ttk.Labelframe(f1_2_2, text= "Group")
            b2 = ttk.Labelframe(f1_2_2, text= "Name")
            b3 = ttk.Labelframe(f1_2_2, text= "")
            b1.grid(row=0, column=0)
            b2.grid(row=0, column=1)
            b3.grid(row=0, column=2)

            self.p_variable_gi[i] = Tkinter.StringVar()
            bb1 = Tkinter.Entry(b1, width=14, textvariable=self.p_variable_gi[i])
            self.p_variable_gn[i] = Tkinter.StringVar()
            bb2 = Tkinter.Entry(b2, width=20, textvariable=self.p_variable_gn[i])
#            bb2 = Tkinter.Entry(b2, width=24, textvariable=self.p_variable_gn[i])
            ConfirmGName_with_arg = functools.partial (self.__ConfirmGName, i)
            bb3 = ttk.Button(b3, text="OK", width=4, command=ConfirmGName_with_arg)
            bb1.pack(side = Tkinter.LEFT)
            bb2.pack(side = Tkinter.LEFT)
            bb3.pack()
            
            self.p_variable_gi[i].set("--group ID--")
            self.p_variable_gn[i].set("--group name--")
#
# LUN Name
#
            p = ttk.Panedwindow(f1_3, orient=Tkinter.VERTICAL)
            f1_3_1 = ttk.Frame(p) #, text="Program Panel")
            f1_3_2 = ttk.Frame(p) #, text="Execution Panel")
            p.add(f1_3_1)
            p.add(f1_3_2)
            p.pack()            
      
            self.nmtv_ln[i] = ttk.Treeview(f1_3_1, height=20, padding = (0,2,0,2))
            self.nmtv_ln[i]["columns"]=('#1', '#2', '#3')
            self.nmtv_ln[i].column("#0", width=20, anchor=Tkinter.CENTER)
            self.nmtv_ln[i].column("#1", width=10, anchor=Tkinter.CENTER)
            self.nmtv_ln[i].column("#2", width=80, anchor=Tkinter.E)
            self.nmtv_ln[i].column("#3", width=80, anchor=Tkinter.CENTER)
            self.nmtv_ln[i].heading("#0", text="Target #")
            self.nmtv_ln[i].heading("#1", text="LUN #")
            self.nmtv_ln[i].heading("#2", text="Capacity")
            self.nmtv_ln[i].heading("#3", text="LUN Name")
            self.nmtv_ln[i].insert("", 0, text="-", values=("-", "-"))
            self.LNTonDoubleClick_with_arg = functools.partial (self.__LNTonDoubleClick, i)
            self.nmtv_ln[i].bind("<Double-Button-1>", self.LNTonDoubleClick_with_arg)
            self.nmtv_ln[i].pack(expand=YES, fill=Tkinter.BOTH)
            self.__UpdateLNT(i)

            b1 = ttk.Labelframe(f1_3_2, text= "LUN")
            b2 = ttk.Labelframe(f1_3_2, text= "Name")
            b3 = ttk.Labelframe(f1_3_2, text= "")
            b1.grid(row=0, column=0)
            b2.grid(row=0, column=1)
            b3.grid(row=0, column=2)

            self.p_variable_li[i] = Tkinter.StringVar()
            bb1 = Tkinter.Entry(b1, width=14, textvariable=self.p_variable_li[i])
            self.p_variable_ln[i] = Tkinter.StringVar()
            bb2 = Tkinter.Entry(b2, width=20, textvariable=self.p_variable_ln[i])
#            bb2 = Tkinter.Entry(b2, width=24, textvariable=self.p_variable_ln[i])
            ConfirmLName_with_arg = functools.partial (self.__ConfirmLName, i)
            bb3 = ttk.Button(b3, text="OK", width=4, command=ConfirmLName_with_arg)
            bb1.pack(side = Tkinter.LEFT)
            bb2.pack(side = Tkinter.LEFT)
            bb3.pack()
            
            self.p_variable_li[i].set("--LUN ID--")
            self.p_variable_ln[i].set("--LUN name--")
#            
# Setup Execution Buttons
#
            p = ttk.Panedwindow(f2, orient=Tkinter.HORIZONTAL)
            f2_1 = ttk.Frame(p)
            p.add(f2_1)
            p.pack()
            
            ClearSelection_with_arg = functools.partial (self.__ClearSelection, i)
            SaveCurrentName_with_arg = functools.partial (self.__SaveCurrentName, i)
            CloseConfiguration_with_arg = functools.partial (self.__CloseConfiguration, i)

            b1 = ttk.Button(f2_1, text="Clear Selections", width = 24, command=ClearSelection_with_arg)
            b2 = ttk.Button(f2_1, text="Save to Clustered Engines", width = 24, command=SaveCurrentName_with_arg)
            b3 = ttk.Button(f2_1, text="Close Configuration", width = 24, command=CloseConfiguration_with_arg)
            b1.grid(row=0, column=0)
            b2.grid(row=0, column=1)
            b3.grid(row=0, column=2)
#
# get last info from file            
#
#            self.GetLastCmgInfo(i)
#            self.__OptionList_ps_ok(i)
#            self.__OptionList_ss_ok(i)
#

#
# frame 7 (Manual Registraton)
#
#       np7
#           np7_p[engines]
#               +---------------------------------------------------------------+
#               |      Host Group       |               LUN Map                 |
#               |-----------------------|---------------------------------------|
#           f1  |                       |                                       |
#               |        f1_1           |                 f1_2                  |
#               |                       |                                       |
#               |---------------------------------------------------------------|
#           f2  | Available HBA | Available Group |Available LUN | Available ID | f2_1_1, f2_2_1, f2_3_1, f2_4_1
#               |---------------------------------------------------------------|
#           f3  |                    [Submit][Erase][Cancel]                    |
#               |---------------------------------------------------------------|
#
# frame 7 (Manual Registration)
#
        np7 = ttk.Notebook(frame_7)
        np7.pack(fill='both', expand='yes')
        
        np7_p = [0 for x in range(engine_number)]

        self.revar_tnum = [0 for x in range(engine_number)]
        self.revar_port = [0 for x in range(engine_number)]
        self.revar_wwpn = [0 for x in range(engine_number)]
        self.revar_lun_no = [0 for x in range(engine_number)]
        self.revar_device = [0 for x in range(engine_number)]
        self.revar_mmd = [0 for x in range(engine_number)]
        self.revar_engnum = [0 for x in range(engine_number)]

        self.revar_unreg_id = [0 for x in range(engine_number)]
        self.revar_unreg_wwpn = [0 for x in range(engine_number)]
        self.revar_wwpn_name = [0 for x in range(engine_number)]
        
        self.retv_ur = [0 for x in range(engine_number)]    # Manual Registration Tree View for UN-Register table
        self.retv_re = [0 for x in range(engine_number)]    # Manual Registration Tree View for REgistered table
#
        for i in range (engine_number):
            
            np7_p[i] = ttk.Frame(frame_7)
            np7_p[i].pack()
            np7.add(np7_p[i], text='   Engine %s   ' % i)
#
            p = ttk.Panedwindow(np7_p[i], orient=Tkinter.VERTICAL)
            f1 = ttk.Frame(p) #, text="Display Panel")
            f2 = ttk.Frame(p) #, text="Execution Panel")
            p.add(f1)
            p.add(f2)
            p.pack()
#
            p = ttk.Panedwindow(f1, orient=Tkinter.HORIZONTAL)

            if current_engine[i][0] != 'on':
                tf = Tkinter.Label(p, text="\n"*10 + "This Engine is offline.", justify = Tkinter.CENTER,
                     bg = "#d8d8d8")
                p.add(tf)
                p.pack()
                continue
#
            f1_1 = ttk.Labelframe(p, text="UN-Registered Device")
            f1_2 = ttk.Labelframe(p, text="Registered Device")
            p.add(f1_1)
            p.add(f1_2)
            p.pack()
#
# Setup UN-Register
# 
            p = ttk.Panedwindow(f1_1, orient=Tkinter.VERTICAL)
            f1_1_1 = ttk.Frame(p) #, text="Program Panel")
            f1_1_2 = ttk.Frame(p) #, text="Execution Panel")
            p.add(f1_1_1)
            p.add(f1_1_2)
            p.pack()            
#
            self.retv_ur[i] = ttk.Treeview(f1_1_1, height=20, padding = (0,2,0,2))
            self.retv_ur[i]["columns"]=('#1', '#2', '#3', '#4', '#5')
            self.retv_ur[i].column("#0", width=15, anchor=Tkinter.CENTER)
            self.retv_ur[i].column("#1", width=5, anchor=Tkinter.CENTER)
            self.retv_ur[i].column("#2", width=100, anchor=Tkinter.E)
            self.retv_ur[i].column("#3", width=5, anchor=Tkinter.CENTER)
            self.retv_ur[i].column("#4", width=70, anchor=Tkinter.E)
            self.retv_ur[i].column("#5", width=25, anchor=Tkinter.E)
            self.retv_ur[i].heading("#0", text="Type")            
            self.retv_ur[i].heading("#1", text="Port")
            self.retv_ur[i].heading("#2", text="WWPN")
            self.retv_ur[i].heading("#3", text="LUN #")
            self.retv_ur[i].heading("#4", text="Serial Number")
            self.retv_ur[i].heading("#5", text="Capacity")
            self.retv_ur[i].insert("", 0, text="-", values=("-", "-", "-", "-"))

            self.URTonDoubleClick_with_arg = functools.partial (self.__URTonDoubleClick, i)
            self.retv_ur[i].bind("<Double-Button-1>", self.URTonDoubleClick_with_arg)
            self.retv_ur[i].pack(expand=YES, fill=Tkinter.BOTH)
#
            self.DB2Panel_URT(i)
#
            b1 = ttk.Labelframe(f1_1_2, text= "Type")
            b2 = ttk.Labelframe(f1_1_2, text= "port")
            b3 = ttk.Labelframe(f1_1_2, text= "WWPN to Register")
            b4 = ttk.Labelframe(f1_1_2, text= "LUN #")
            b5 = ttk.Labelframe(f1_1_2, text= "tnum")
            b6 = ttk.Labelframe(f1_1_2, text= "")
            b1.grid(row=0, column=0)
            b2.grid(row=0, column=1)
            b3.grid(row=0, column=2)
            b4.grid(row=0, column=3)
            b5.grid(row=0, column=4)
            b6.grid(row=0, column=5)
#
            self.rels_device = ["LUN-AA", "LUN-AP","LUN-S", "HBA", "Engine" ]
#            self.rels_device = ["LUN-AA", "HBA", "Engine" ]
            self.revar_device[i] = Tkinter.StringVar()
            self.revar_device[i].set('')
            bb1 = Tkinter.OptionMenu(b1, self.revar_device[i], *self.rels_device)
            bb1.config(font=('Courier',(14)), bg="light gray", width=10)
            bb1['menu'].config(font=('Courier',(12)))
#
            rels_port = ["A1", "A2","B1", "B2"]
            self.revar_port[i] = Tkinter.StringVar()
            self.revar_port[i].set('')
            bb2 = Tkinter.OptionMenu(b2, self.revar_port[i], *rels_port)
            bb2.config(font=('Courier',(14)), bg="light gray", width=6)
            bb2['menu'].config(font=('Courier',(12)))
#
            self.revar_wwpn[i] = Tkinter.StringVar()
            bb3 = Tkinter.Entry(b3, width=20, textvariable=self.revar_wwpn[i])
            self.revar_lun_no[i] = Tkinter.StringVar()
            bb4 = Tkinter.Entry(b4, width=8, textvariable=self.revar_lun_no[i])

            self.revar_tnum[i] = Tkinter.StringVar()
            bb5 = Tkinter.Entry(b5, width=6, textvariable=self.revar_tnum[i])

            ConfirmREUR_with_arg = functools.partial (self.__ConfirmREUR, i)
            bb6 = ttk.Button(b6, text="OK", width=4, command=ConfirmREUR_with_arg)
#
            bb1.pack(side = Tkinter.LEFT)
            bb2.pack(side = Tkinter.LEFT)
            bb3.pack(side = Tkinter.LEFT)
            bb4.pack(side = Tkinter.LEFT)
            bb5.pack(side = Tkinter.LEFT)
            bb6.pack()
#
# Setup Registered Device
#
            p = ttk.Panedwindow(f1_2, orient=Tkinter.VERTICAL)
            f1_2_1 = ttk.Frame(p) #, text="Program Panel")
            f1_2_2 = ttk.Frame(p) #, text="Execution Panel")
            p.add(f1_2_1)
            p.add(f1_2_2)
            p.pack()            
#
            self.retv_re[i] = ttk.Treeview(f1_2_1, height=20, padding = (0,2,0,2))
            self.retv_re[i]["columns"]=('#1', '#2', '#3', '#4', '#5')
            self.retv_re[i].column("#0", width=10, anchor=Tkinter.CENTER)
            self.retv_re[i].column("#1", width=10, anchor=Tkinter.CENTER)
            self.retv_re[i].column("#2", width=100, anchor=Tkinter.E)
            self.retv_re[i].column("#3", width=10, anchor=Tkinter.CENTER)
            self.retv_re[i].column("#4", width=80, anchor=Tkinter.E)
            self.retv_re[i].column("#5", width=10, anchor=Tkinter.CENTER)
            self.retv_re[i].heading("#0", text="ID")
            self.retv_re[i].heading("#1", text="Port")
            self.retv_re[i].heading("#2", text="WWPN/LUN Serial Number")
            self.retv_re[i].heading("#3", text="LUN #")
            self.retv_re[i].heading("#4", text="Capacity/Name/Note")
            self.retv_re[i].heading("#5", text="Status")
            self.retv_re[i].insert("", 0, text="-", values=("-", "-", "-", "-", "-"))

            self.RETonDoubleClick_with_arg = functools.partial (self.__RETonDoubleClick, i)
            self.retv_re[i].bind("<Double-Button-1>", self.RETonDoubleClick_with_arg)
            self.retv_re[i].pack(expand=YES, fill=Tkinter.BOTH)
#
            self.DB2Panel_RET(i)
#
            b1 = ttk.Labelframe(f1_2_2, text= "ID to UN-Register")
            b2 = ttk.Labelframe(f1_2_2, text= "WWPN to UN-Register")
            b3 = ttk.Labelframe(f1_2_2, text= "Name")
            b4 = ttk.Labelframe(f1_2_2, text= "")
            b1.grid(row=0, column=0)
            b2.grid(row=0, column=1)
            b3.grid(row=0, column=2)
            b4.grid(row=0, column=3)
#
            self.revar_unreg_id[i] = Tkinter.StringVar()
            bb1 = Tkinter.Label(b1, width=10, textvariable=self.revar_unreg_id[i], bg = '#d8d8d8')
            self.revar_unreg_wwpn[i] = Tkinter.StringVar()
            bb2 = Tkinter.Label(b2, width=20, textvariable=self.revar_unreg_wwpn[i], bg = '#d8d8d8')
            self.revar_wwpn_name[i] = Tkinter.StringVar()
            bb3 = Tkinter.Label(b3, width=20, textvariable=self.revar_wwpn_name[i], bg = '#d8d8d8')
#
            ConfirmRERE_with_arg = functools.partial (self.__ConfirmRERE, i)
            bb4 = ttk.Button(b4, text="OK", width=4, command=ConfirmRERE_with_arg)
            bb1.pack(side = Tkinter.LEFT)
            bb2.pack(side = Tkinter.LEFT)
            bb3.pack(side = Tkinter.LEFT)
            bb4.pack()
#
# Setup Execution Buttons
#
            p = ttk.Panedwindow(f2, orient=Tkinter.HORIZONTAL)
            f2_1 = ttk.Frame(p)
            f2_2 = ttk.Frame(p)
            f2_3 = ttk.Frame(p)
            p.add(f2_1)
            p.add(f2_2)
            p.add(f2_3)
            p.pack()            
#
            ClearRESelection_with_arg = functools.partial (self.__ClearRESelection, i)
            CloseConfiguration_with_arg = functools.partial (self.__CloseConfiguration, i)
            b1 = ttk.Button(f2_1, text="Clear Selection", width = 24, command=ClearRESelection_with_arg)
            b2 = ttk.Button(f2_1, text="Close Configuration", width = 24, command=CloseConfiguration_with_arg)

            b1.grid(row=0, column=0)
            b2.grid(row=0, column=1)
#
            s1 = ttk.Frame(f2_2)
#
            self.rels_mmd = ["conmgr mode: pg83", "conmgr mode: wwnn"]
            self.revar_mmd[i] = Tkinter.StringVar()
            if engine_info[i]['Special']['pg83 MPIO'] == 'ON':
                self.revar_mmd[i].set(self.rels_mmd[0])
            else:
                self.revar_mmd[i].set(self.rels_mmd[1])
                
            s1 = Tkinter.OptionMenu(f2_2, self.revar_mmd[i], *self.rels_mmd)
            s1.config(font=('Courier',(14)), bg="light gray", width=20)
            s1['menu'].config(font=('Courier',(12)))
#
            ConfirmREMD_with_arg = functools.partial (self.__ConfirmREMD, i)
            s2 = ttk.Button(f2_2, text="OK", width=4, command=ConfirmREMD_with_arg)
#
            s1.grid(row=0, column=0)
            s2.grid(row=0, column=1)
#
            self.rels_engnum = ["# of this Engine: 1 (M)", "# of this Engine: 2", "# of this Engine: 3",
                                "# of this Engine: 4", "# of this Engine: 5", "# of this Engine: 6"]
            self.revar_engnum[i] = Tkinter.StringVar()
            if engine_info[i]['This Engine'] == 'U':
                self.revar_engnum[i].set("Undefined")
            else:
                self.revar_engnum[i].set(self.rels_engnum[ int(engine_info[i]['This Engine'])-1 ])
                
            s1 = Tkinter.OptionMenu(f2_3, self.revar_engnum[i], *self.rels_engnum)
            s1.config(font=('Courier',(14)), bg="light gray", width=25)
            s1['menu'].config(font=('Courier',(12)))
#
            ConfirmREEN_with_arg = functools.partial (self.__ConfirmREEN, i)
            s2 = ttk.Button(f2_3, text="OK", width=4, command=ConfirmREEN_with_arg)
#
            s1.grid(row=0, column=0)
            s2.grid(row=0, column=1)
#
#
# frame 8 (Rebuild Management)
#
#       np8
#           np8_p[engines]
#               +---------------------------------------------------------------+
#               |                        Rebuild Information                    |
#               |---------------------------------------------------------------|
#           f1  |                                                               |
#               |                                                               |
#               |                                                               |
#               |---------------------------------------------------------------|
#           f2  |                    [Submit][Erase][Cancel]                    |
#               |---------------------------------------------------------------|
#
#
        np8 = ttk.Notebook(frame_8)
        np8.pack(fill='both', expand='yes')
        
        np8_p = [0 for x in range(engine_number)]
        self.rbvar_init_group = [0 for x in range(engine_number)]
        self.rbvar_lun = [0 for x in range(engine_number)]
        self.rbvar_hba = [0 for x in range(engine_number)]
        self.rbvar_hbag = [0 for x in range(engine_number)]
        self.rbvar_mcmd = [0 for x in range(engine_number)]
        self.rbvar_hcmd = [0 for x in range(engine_number)]
        self.rbvar_amap = [0 for x in range(engine_number)]
        self.rbvar_maps = [0 for x in range(engine_number)]
        self.rbvar_value = [0 for x in range(engine_number)]
        self.bb1 = [0 for x in range(engine_number)]
        self.rbvar_dcmd = [0 for x in range(engine_number)]
        self.rbvar_dvalue = [0 for x in range(engine_number)]

        self.rbtv_ml = [0 for x in range(engine_number)]    # Host LUN Tree View for LUN Map table
#
        for i in range (engine_number):
            
            np8_p[i] = ttk.Frame(frame_8)
            np8_p[i].pack()
            np8.add(np8_p[i], text='   Engine %s   ' % i)
#
            p = ttk.Panedwindow(np8_p[i], orient=Tkinter.VERTICAL)
            f1 = ttk.Frame(p) #, text="Display Panel")
            f2 = ttk.Frame(p) #, text="Execution Panel")
            p.add(f1)
            p.add(f2)
            p.pack()
#
            p = ttk.Panedwindow(f1, orient=Tkinter.HORIZONTAL)

            if current_engine[i][0] != 'on':
                tf = Tkinter.Label(p, text="\n"*10 + "This Engine is offline.", justify = Tkinter.CENTER,
                     bg = "#d8d8d8")
                p.add(tf)
                p.pack()
                continue
#
            f1_1 = ttk.Labelframe(p, text="Rebuild Information")
            p.add(f1_1)
            p.pack()
#
# Setup LUN-Map
# 
            p = ttk.Panedwindow(f1_1, orient=Tkinter.VERTICAL)
            f1_1_1 = ttk.Frame(p) #, text="Program Panel")
            f1_1_2 = ttk.Frame(p) #, text="Execution Panel")
            p.add(f1_1_1)
            p.add(f1_1_2)
            p.pack()            
#
            self.rbtv_ml[i] = ttk.Treeview(f1_1_1, height=20, padding = (0,2,0,2))
            self.rbtv_ml[i]["columns"]=('#1', '#2', '#3', '#4', '#5', '#6', '#7', '#8', '#9', '#10', '#11', '#12', \
                                        '#13', '#14', '#14', '#15', '#16')
            self.rbtv_ml[i].column("#0", width=12, anchor=Tkinter.CENTER)
            self.rbtv_ml[i].column("#1", width=40, anchor=Tkinter.CENTER)
            self.rbtv_ml[i].column("#2", width=8, anchor=Tkinter.CENTER)
            self.rbtv_ml[i].column("#3", width=80, anchor=Tkinter.E)
            self.rbtv_ml[i].column("#4", width=8, anchor=Tkinter.CENTER)
            self.rbtv_ml[i].column("#5", width=8, anchor=Tkinter.CENTER)
            self.rbtv_ml[i].column("#6", width=8, anchor=Tkinter.CENTER)
            self.rbtv_ml[i].column("#7", width=8, anchor=Tkinter.CENTER)
            self.rbtv_ml[i].column("#8", width=8, anchor=Tkinter.CENTER)
            self.rbtv_ml[i].column("#9", width=8, anchor=Tkinter.CENTER)
            self.rbtv_ml[i].column("#10", width=8, anchor=Tkinter.CENTER)
            self.rbtv_ml[i].column("#11", width=8, anchor=Tkinter.CENTER)
            self.rbtv_ml[i].column("#12", width=8, anchor=Tkinter.CENTER)
            self.rbtv_ml[i].column("#13", width=8, anchor=Tkinter.CENTER)
            self.rbtv_ml[i].column("#14", width=8, anchor=Tkinter.CENTER)
            self.rbtv_ml[i].column("#15", width=40, anchor=Tkinter.CENTER)
            self.rbtv_ml[i].column("#16", width=10, anchor=Tkinter.CENTER)
            self.rbtv_ml[i].column("#17", width=35, anchor=Tkinter.CENTER)
            self.rbtv_ml[i].heading("#0", text="Mirror #")
            self.rbtv_ml[i].heading("#1", text="Name")
            self.rbtv_ml[i].heading("#2", text="M Member")
            self.rbtv_ml[i].heading("#3", text="Capacity")
            self.rbtv_ml[i].heading("#4", text="Member 1")
            self.rbtv_ml[i].heading("#5", text="M1 Status")
            self.rbtv_ml[i].heading("#6", text="Member 2")
            self.rbtv_ml[i].heading("#7", text="M2 Status")
            self.rbtv_ml[i].heading("#8", text="Member 3")
            self.rbtv_ml[i].heading("#9", text="M3 Status")
            self.rbtv_ml[i].heading("#10", text="Member 4")
            self.rbtv_ml[i].heading("#11", text="M4 Status")
            self.rbtv_ml[i].heading("#12", text="Max Speed")
            self.rbtv_ml[i].heading("#13", text="Max IOPS")
            self.rbtv_ml[i].heading("#14", text="Type")
            self.rbtv_ml[i].heading("#15", text="Progress Time")
            self.rbtv_ml[i].heading("#16", text="Completed")
            self.rbtv_ml[i].heading("#17", text="Remain")
            self.rbtv_ml[i].insert("", 0, text="-", values=("-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-"))

#            self.RBTonDoubleClick_with_arg = functools.partial (self.__RBTonDoubleClick, i)
#            self.rbtv_ml[i].bind("<Double-Button-1>", self.RBTonDoubleClick_with_arg)
            self.rbtv_ml[i].pack(expand=YES, fill=Tkinter.BOTH)
#
            self.__UpdateRBT(i)
#
            b1 = ttk.Labelframe(f1_1_2, text= "Selected Mirror #")
            b2 = ttk.Labelframe(f1_1_2, text= "")
            b3 = ttk.Labelframe(f1_1_2, text= "Value")
            b4 = ttk.Labelframe(f1_1_2, text= "Command")
            b5 = ttk.Labelframe(f1_1_2, text= "")
            b1.grid(row=0, column=0)
            b2.grid(row=0, column=1)
            b3.grid(row=0, column=2)
            b4.grid(row=0, column=3)
            b5.grid(row=0, column=4)
#
            list_of_lun = ["--NULL--"]     # Available LUNs
            
            for mirror_id in engine_info[i]['Rebuild']:
                list_of_lun.append(mirror_id+' : '+str(int(engine_info[i]['Rebuild'][mirror_id][2], 16)))

            self.rbvar_lun[i] = Tkinter.StringVar()
            self.rbvar_lun[i].set(list_of_lun[0])
            self.bb1[i] = Tkinter.OptionMenu(b1, self.rbvar_lun[i], *list_of_lun)
            self.bb1[i].config(font=('Courier',(14)), bg="light gray", width=25)
            self.bb1[i]['menu'].config(font=('Courier',(12)))

#            self.rbvar_maps[i] = Tkinter.StringVar()
            bb2 = Tkinter.Label(b2, width=68, bg = '#d8d8d8')
#            bb2 = Tkinter.Label(b2, width=76, bg = '#d8d8d8')
#
            self.rbvar_value[i] = Tkinter.StringVar()
            bb3 = Tkinter.Entry(b3, width=15, textvariable=self.rbvar_value[i])
#
            list_of_cmd = ["Speed", "Pause", "Resume", "Abort", "Permit", "IOPS"]   
            self.rbvar_mcmd[i] = Tkinter.StringVar()
            self.rbvar_mcmd[i].set(list_of_cmd[0])
            bb4 = Tkinter.OptionMenu(b4, self.rbvar_mcmd[i], *list_of_cmd)
            bb4.config(font=('Courier',(14)), bg="light gray", width=15)
            bb4['menu'].config(font=('Courier',(12)))

            ConfirmRebuild_with_arg = functools.partial (self.__ConfirmRebuild, i)
            bb5 = ttk.Button(b5, text="OK", width=4, command=ConfirmRebuild_with_arg)
            self.bb1[i].pack(side = Tkinter.LEFT)
            bb2.pack(side = Tkinter.LEFT)
            bb3.pack(side = Tkinter.LEFT)
            bb4.pack(side = Tkinter.LEFT)
            bb5.pack()
#
# Setup Execution Buttons
#
            p = ttk.Panedwindow(f2, orient=Tkinter.HORIZONTAL)
#            f2_1 = ttk.Frame(p)
            f2_1 = ttk.LabelFrame(p, text= "")
            f2_2 = ttk.Labelframe(p, text= "Default Setting")
            p.add(f2_1)
            p.add(f2_2)
            p.pack()
            
            ClearSelection_with_arg = functools.partial (self.__ClearSelection, i)
            CloseConfiguration_with_arg = functools.partial (self.__CloseConfiguration, i)

            b1 = ttk.Button(f2_1, text="Clear Selection", width = 24, command=ClearSelection_with_arg)
            b2 = ttk.Button(f2_1, text="Close Configuration", width = 24, command=CloseConfiguration_with_arg)

            b1.grid(row=0, column=0)
            b2.grid(row=0, column=1)
#
            list_of_cmd = ["Default Speed", "Default IOPS"]
            self.rbvar_dcmd[i] = Tkinter.StringVar()
            
            s1 = ttk.Frame(f2_2)            
            s1 = Tkinter.OptionMenu(f2_2, self.rbvar_dcmd[i], *list_of_cmd)
            s1.config(font=('Courier',(14)), bg="light gray", width=16)
            s1['menu'].config(font=('Courier',(12)))
#
            self.rbvar_dvalue[i] = Tkinter.StringVar()
            l1 = Tkinter.Entry(f2_2, width=5, textvariable=self.rbvar_dvalue[i])

            ConfirmDRB_with_arg = functools.partial (self.__ConfirmDRB, i)
            s2 = ttk.Button(f2_2, text="OK", width=4, command=ConfirmDRB_with_arg)
#
            s1.grid(row=0, column=0)
            l1.grid(row=0, column=1)
            s2.grid(row=0, column=2)
#
#
# get last info from file            
#
#            self.GetLastCmgInfo(i)
#            self.__OptionList_ps_ok(i)
#            self.__OptionList_ss_ok(i)
#
# frame 9 (Host-LUN Mapping)
#   Host mapping is the process of controlling which hosts have access to specific LUN within the system.
#
#       np9
#           np9_p[engines]
#                          f1                               f2
#                                            f2_1_1         f2_1_2       f2_1_3
#               +-----------------------|---------------------------------------+
#               |  licensed installed   | Mode Status | Mode Selection | Action |  f2_1
#               |                       |---------------------------------------|
#       f1_1    |                       |                                       |  f2_2
#               |                       |---------------------------------------|
#               |                       |                                       |  f2_3
#               |-----------------------|---------------------------------------|
#       f1_2    |   <add new license>   |                                       |
#               |-----------------------|---------------------------------------|
#       f1_3    |   [Cancel][Submit]    |                                       |
#               |-----------------------|---------------------------------------|
#
#   Host Group      id #0    #1    #2    #3    #4    #5
#   Host Group    
#
# frame 9 (Host-LUN Mapping)
#
        np9 = ttk.Notebook(frame_9)
        np9.pack(fill='both', expand='yes')
        
        np9_p = [0 for x in range(engine_number)]
#        self.license_key = [0 for x in range(engine_number)]
#        self.feature_no = [0 for x in range(engine_number)]
#        self.license_var = [0 for x in range(engine_number)]

        HGROUP = 8
        self.hg_var = [[0 for x in range(HGROUP)] for x in range(engine_number)]
        self.status_var = [[0 for x in range(HGROUP)] for x in range(engine_number)]

        for i in range (engine_number):
            np9_p[i] = ttk.Frame(frame_9)
            np9_p[i].pack()
            np9.add(np9_p[i], text='   Engine %s   ' % i)
#
            p = ttk.Panedwindow(np9_p[i], orient=Tkinter.HORIZONTAL)
            
            if current_engine[i][0] != 'on':
                tf = Tkinter.Label(p, text="\n"*10 + "This Engine is offline.", justify = Tkinter.CENTER,
                     bg = "#d8d8d8")
                p.add(tf)
                p.pack()
                continue
                
            f1 = ttk.Labelframe(p, text="Host Grouping ")
            f2 = ttk.Labelframe(p, text="LUN Mapping")
            p.add(f1)
            p.add(f2)
            p.pack()
#
# Update .cmg file to get all the up to date Special Mode info
#
#            p = ControlEngine.xEngine()
#            if p.UpdateInfo(i, 'cmg') == False:
#                thread.start_new_thread( tkMessageBox.showinfo, ("Special Mode", "Failed to update .cmg file."))    
#
# Initialize the Special Mode Panel - F1
#
            f1_ = [0 for x in range(HGROUP)]
            
            p = ttk.Panedwindow(f1, orient=Tkinter.VERTICAL)            
            for j in range (MSLOT):
                f1_[j] = ttk.Frame(p)
                p.add(f1_[j])
            p.pack()
#
            j = 0
            for item in engine_info[i]['Application']:
                pd = ttk.Frame(f1_[j], width=20)
                pd.grid(row=0, column=0)
        
                SubmitNewMode_with_arg = functools.partial (self.__SubmitNewMode, i, j, item)
                b = ttk.Button(f1_[j], text="Change", width = 10, command=SubmitNewMode_with_arg)
                b.grid(row=0, column=1)

                pd = ttk.Frame(f1_[j], width=20)
                pd.grid(row=0, column=2)

                f1_1_1 = ttk.Label(f1_[j], text=item, width=20)
                f1_1_1.grid(row=0, column=3)
            
                self.status_var[i][j] = Tkinter.StringVar()
                f1_1_1 = ttk.Label(f1_[j], textvariable=self.status_var[i][j], width=15)
                self.status_var[i][j].set(engine_info[i]['Application'][item])
                f1_1_1.grid(row=0, column=4)

                self.MODES = [('ON', '0'), ('OFF', '1')]
                self.rbvar[i][j] = Tkinter.IntVar()
            
                k = 1
                for text, mode in self.MODES:
                    r = Tkinter.Radiobutton(f1_[j], text=text, variable=self.rbvar[i][j], value=mode, bg = '#d8d8d8')
                    r.grid(row=0, column=k+4)
                    r.deselect()
                    k += 1
                j += 1
#
# Initialize the Special Mode Panel - F2
#
            f2_ = [0 for x in range(HGROUP)]
            
            p = ttk.Panedwindow(f2, orient=Tkinter.VERTICAL)            
            for j in range (MSLOT):
                f2_[j] = ttk.Frame(p)
                p.add(f2_[j])
            p.pack()
#
            j = 0
            for item in engine_info[i]['Application']:
                pd = ttk.Frame(f2_[j], width=20)
                pd.grid(row=0, column=0)
        
                SubmitNewMode_with_arg = functools.partial (self.__SubmitNewMode, i, j, item)
                b = ttk.Button(f2_[j], text="Change", width = 10, command=SubmitNewMode_with_arg)
                b.grid(row=0, column=1)

                pd = ttk.Frame(f2_[j], width=20)
                pd.grid(row=0, column=2)

                f2_1_1 = ttk.Label(f2_[j], text=item, width=20)
                f2_1_1.grid(row=0, column=3)
            
                self.status_var[i][j] = Tkinter.StringVar()
                f2_1_1 = ttk.Label(f2_[j], textvariable=self.status_var[i][j], width=15)
                self.status_var[i][j].set(engine_info[i]['Application'][item])
                f2_1_1.grid(row=0, column=4)

                self.MODES = [('ON', '0'), ('OFF', '1')]
                self.rbvar[i][j] = Tkinter.IntVar()
            
                k = 1
                for text, mode in self.MODES:
                    r = Tkinter.Radiobutton(f2_[j], text=text, variable=self.rbvar[i][j], value=mode, bg = '#d8d8d8')
                    r.grid(row=0, column=k+4)
                    r.deselect()
                    k += 1
                j += 1
#
    def __SubmitNewMode(self, i, j, item):
        change = self.rbvar[i][j].get()
        
        if change == 0: text = 'ON'
        else: text = 'OFF'
        
        if engine_info[i]['Application'][item] == text:
            tkMessageBox.showinfo("Change Mode", "Engine #%ss %s has already turned %s." % (i, item, text))        
            return
        
        ans = tkMessageBox.askokcancel("Change Mode", 
            "Request to turn %s the %s for Engine #%s \n\nIs this correct?" % (text, item, i))
        
        if ans != True:
            tkMessageBox.showinfo("Change Mode", "Action has been cancelled.")
            return False
        else:
            # change mode take action
            p = ControlEngine.xEngine()
            if p.SetNewMode(i, j, item, text) == False:
                tkMessageBox.showinfo("Change Mode", "Change Mode process failed, please verify the result!")
                return False
#
# update .cmg file
#          
            p = ControlEngine.xEngine()
            if p.Engine2File(i, 'cmg') == False:
                thread.start_new_thread( tkMessageBox.showinfo, ("Special Mode", "Failed to update .cmg file."))    
#
# update engine_info[engine_idx][Special], and engine_info[engine_idx][Application]
#       
            p = ControlEngine.xEngine()
            p.UpdateInfo(i, 'cmg')
#
# update the Special Mode panel
#
            self.status_var[i][j].set(text)
#
            tkMessageBox.showinfo("Add License", "License added successfully.")
#
#
    def __SubmitNewLicense(self, i):
        feature = self.feature_no[i].get()
        key = self.license_key[i].get()
        if feature == "" or key == "":
            tkMessageBox.showinfo("Add License", "Please enter proper Feature # and Key code.")
            return False
        
        ans = tkMessageBox.askokcancel("Add License", 
            "Do you want to add license with the: \nfeature =  %s\nkey = %s" % (feature, key))
        
        if ans != True:
            tkMessageBox.showinfo("Add License", "Action has been cancelled.")
            return False
        else:
            # add new license
            p = ControlEngine.xEngine()
            if p.SetNewLicense(i, feature, key) == False:
                tkMessageBox.showinfo("Add License",
                    "Add License process failed, please verify the result!")
                return False

            # update the license table
            text = ""
            for j in range (len(engine_info[i]['License'])):
                text = text + engine_info[i]['License'][j] + "\n"
            self.license_var[i].set(text[:-1])
            
            tkMessageBox.showinfo("Add License", "License added successfully.")
#
    def RescanButtonClick(self, i, port):
        if SIMMOD == 1:
            print port
            self.exp_tv_var[i][self.PORTS.index(port)].set("N/A")
            return

            p = ControlEngine.xEngine()
            p.ExecuteCommand(i, 'cmd_Explore', port)
            return
            
        if current_engine[i][0] != 'on':
            self.exp_tv_var[i][self.PORTS.index(port)].set("N/A")
            return
        else:
            p = ControlEngine.xEngine()
            if p.ExecuteCommand(i, 'cmd_Explore', port) == False:
                self.exp_tv_var[i][self.PORTS.index(port)].set("N/A")
                return False
            self.DB2Panel_EXT(i)
#
# Connection Manager Functions
#
    def __GetConfigCmg(self, i):
        
        if SIMMOD == 0:
            if current_engine[i][0] != 'on':
                thread.start_new_thread( tkMessageBox.showinfo, ("Connection Manager", "Engine is not ready."))    
                return
            else:
                ans = tkMessageBox.askokcancel("Connection Manager",
                        "This function will get the current registered Drive, Engine, and Initiator table, OK?")

                if ans != True:
                    thread.start_new_thread( tkMessageBox.showinfo, ("Connection Manager", "Action has been cancelled."))
                    return False
                
                p = ControlEngine.xEngine()
                if p.UpdateInfo(i, 'cmg') == False:
                    thread.start_new_thread( tkMessageBox.showinfo, ("Connection Manager", "Action failed."))    
                    return
        else:   # simulation mode
            pass
            
        self.DB2Panel_ART(i)
        thread.start_new_thread( tkMessageBox.showinfo, ("Connection Manager", "Action completed successfully."))
#
    def __EraseConfigCmg(self, i):
        if SIMMOD == 1:         # simulation mode
            self.DB2Panel_ART(i)
            return
            
        if current_engine[i][0] != 'on':
            thread.start_new_thread( tkMessageBox.showinfo, ("Connection Manager", "Engine is not ready."))    
            return
        else:
            ans = tkMessageBox.askokcancel("Connection Manager",
                    "This function will Erase the current registered Drive, Engine, and Initiator table, OK?")

            if ans != True:
                thread.start_new_thread( tkMessageBox.showinfo, ("Connection Manager", "Action has been cancelled."))
                return False
                
        p = ControlEngine.xEngine()
        if p.EraseCmgfromEngine(i) == False:
            thread.start_new_thread( tkMessageBox.showinfo, ("Connection Manager", "Erase failed."))    
            return False
                
        if current_engine[i][0] != 'on':
            time.sleep(3)

        self.acb1[i].config(state="disabled")
        self.acb2[i].config(state="normal")
#
#        p = ControlEngine.xEngine()
#        if p.UpdateInfo(i, 'cmg') == False:
#            thread.start_new_thread( tkMessageBox.showinfo, ("Connection Manager", "Update failed."))    
#            return False
#
        self.DB2Panel_ART(i)
        tkMessageBox.showinfo ("Connection Manager", "Action completed successfully.")
#
    def __BootEngineCmg(self, i):
        if SIMMOD == 0:
#            if current_engine[i][0] == 'off':
            if False:           # code v15.9.3.x and earlier don't support ping under AH
                thread.start_new_thread( tkMessageBox.showinfo, ("Connection Manager", "Engine is not ready."))    
                return
            else:
                ans = tkMessageBox.askyesno("Connection Manager",
                        "All engines in cluster configured properly and ready to reboot?")

                if ans != True:
                    thread.start_new_thread( tkMessageBox.showinfo, ("Connection Manager", "Action has been cancelled."))
                    return False
                
                p = ControlEngine.xEngine()
                if p.RebootEngine(i) == False:
                    thread.start_new_thread( tkMessageBox.showinfo, ("Connection Manager", "Action failed."))    
                    return
        else:   # simulation mode
            pass
                
        # get port explore info

        self.acb4[i].config(state="disabled")
        self.acb5[i].config(state="normal")

        thread.start_new_thread( tkMessageBox.showinfo, ("Connection Manager", "Action completed successfully."))    

    def __ConfigEngineCmg(self, i):
        if SIMMOD == 0:
            if current_engine[i][0] != 'on':
                thread.start_new_thread( tkMessageBox.showinfo, ("Connection Manager", "Engine is not ready."))    
                return
            else:
                ans = tkMessageBox.askokcancel("Connection Manager",
                        "About to auto register Engine table, will put engine to AH990 after the registration to wait for all engines in cluster are configured, OK?")

                if ans != True:
                    tkMessageBox.showinfo("Connection Manager", "Action has been cancelled.")
                    return False
                
                p = ControlEngine.xEngine()
                if p.AutoCmgfromEngine(i, 'Engine') == False:
                    tkMessageBox.showinfo("Connection Manager", "Action failed.")    
                    return
        else:   # simulation mode
            return
                
        # get port explore info

        self.acb3[i].config(state="disabled")
        self.acb4[i].config(state="normal")

        self.DB2Panel_ART(i)
        tkMessageBox.showinfo("Connection Manager", "Action completed successfully.")

    #
    def __ConfigDriveCmg(self, i):
        if SIMMOD == 0:
            if current_engine[i][0] != 'on':
                thread.start_new_thread( tkMessageBox.showinfo, ("Connection Manager", "Engine is not ready."))    
                return
            else:
                ans = tkMessageBox.askokcancel("Connection Manager",
                        "About to auto register Drive table, OK?")

                if ans != True:
                    tkMessageBox.showinfo("Connection Manager", "Action has been cancelled.")
                    return False
                
                p = ControlEngine.xEngine()
                if p.AutoCmgfromEngine(i, 'Drive') == False:
                    tkMessageBox.showinfo("Connection Manager", "Action failed.")
                    return
        else:   # simulation mode
            pass
                
        # get port explore info

        self.acb2[i].config(state="disabled")
        self.acb3[i].config(state="normal")

        self.DB2Panel_ART(i)
        tkMessageBox.showinfo("Connection Manager", "Action completed successfully.")

    #
    def __ConfigInitiatorCmg(self, i):
        if SIMMOD == 0:
            if current_engine[i][0:2] != ('on','on'):
                thread.start_new_thread( tkMessageBox.showinfo, ("Connection Manager", "Engine is not ready."))    
                return
            else:
                ans = tkMessageBox.askokcancel("Connection Manager",
                        "About to auto register Initiator table, OK?")

                if ans != True:
                    tkMessageBox.showinfo("Connection Manager", "Action has been cancelled.")
                    return False
                
                p = ControlEngine.xEngine()
                if p.AutoCmgfromEngine(i, 'Initiator') == False:
                    tkMessageBox.showinfo("Connection Manager", "Action failed.") 
                    return
        else:   # simulation mode
            return
                
        # get port explore info

        self.acb5[i].config(state="disabled")
        self.acb1[i].config(state="normal")

        self.DB2Panel_ART(i)
        tkMessageBox.showinfo("Connection Manager", "Action completed successfully.")

#
    def __ClearRESelection(self, i):
        self.__ClearRERESelection(i)
        self.__ClearREURSelection(i)

    def __ClearREURSelection(self, i):
        self.revar_device[i].set('')
        self.revar_port[i].set('')
        self.revar_wwpn[i].set('')
        self.revar_tnum[i].set('')
        self.revar_lun_no[i].set('')

    def __ClearRERESelection(self, i):
        self.revar_unreg_id[i].set('')
        self.revar_unreg_wwpn[i].set('')
        self.revar_wwpn_name[i].set('')

    def __ClearSelection(self, i):
        self.mmtv_sml[i].delete(*self.mmtv_sml[i].get_children())
        self.mmtv_spl[i].delete(*self.mmtv_spl[i].get_children())
        self.mmtv_ssl[i].delete(*self.mmtv_ssl[i].get_children())
        engine_info[i]["Selected"]["Mirror"] = ""
        engine_info[i]["Selected"]["Primary"] = ""
        engine_info[i]["Selected"]["Secondary"] = ""
        self.__DB2Panel_MST(i)
        self.__DB2Panel_PST(i)
        self.__DB2Panel_SST(i)
#   
    def __AddMirror(self, i):
        mid = engine_info[i]["Selected"]["Mirror"][:5]
        pid = engine_info[i]["Selected"]["Primary"]
        sid = engine_info[i]["Selected"]["Secondary"]
        
        if mid == "": 
            tkMessageBox.showinfo("Add Mirror", "Mirror LUN has not been selected!")
            return False

        if pid != "": 
            tkMessageBox.showinfo("Add Mirror", "Primary LUN should not be selected!")
            return False

        if sid == "": 
            tkMessageBox.showinfo("Add Mirror", "Secondary LUN has not been selected!")
            return False

        mcap = engine_info[i]['Mirror'][mid][2]
        scap = engine_info[i]['DrivesCap'][sid][1]

        if int(mcap) > int(scap):
            tkMessageBox.showinfo("Add Mirror", "Not enough capacity on Secondary LUN!")
            return False

        ans = tkMessageBox.askokcancel("Add Mirror", 
            "Request to: \nAdd mirror set %s with new member %s, and keep data intact. \n\nIs that correct?" % (mid, sid))

        if ans != True:
            tkMessageBox.showinfo("Add Mirror", "Action has been cancelled.")
            return False

        p = ControlEngine.xEngine()
        if p.SetAddMirror(i, mid, sid) == False:
            tkMessageBox.showinfo("Add Mirror",
                "Mirror split process failed, mirror may or may not be deleted, please check the result!")
            return False
        
        self.mmtv_sml[i].delete(*self.mmtv_sml[i].get_children())
        self.mmtv_spl[i].delete(*self.mmtv_spl[i].get_children())
        self.mmtv_ssl[i].delete(*self.mmtv_ssl[i].get_children())
        engine_info[i]["Selected"]["Mirror"] = ""
        engine_info[i]["Selected"]["Primary"] = ""
        engine_info[i]["Selected"]["Secondary"] = ""
        self.__DB2Panel_MST(i)
        self.__DB2Panel_PST(i)
        self.__DB2Panel_SST(i)
#        
    def __CreateMirror(self, i):
        self.mmtv_sml[i].delete(*self.mmtv_sml[i].get_children())
        engine_info[i]["Selected"]["Mirror"] = ""

        pid = engine_info[i]["Selected"]["Primary"]
        sid = engine_info[i]["Selected"]["Secondary"]
            
        if pid == "": 
            tkMessageBox.showinfo("Create Mirror", "Primary LUN has not selected!")
            return False

        pcap = engine_info[i]['DrivesCap'][pid][1]

        if sid == "": 
            self.mmtv_sml[i].insert("", 0, text="-----", 
                values=(pid, sid, '{:,}'.format(int(engine_info[i]['DrivesCap'][pid][1]))))

            ans = tkMessageBox.askokcancel("Create Mirror", 
                "Request to: \ncreate one way mirror with %s \n\nIs that correct?" % pid)

            if ans != True:
                tkMessageBox.showinfo("Create Mirror", "Action has been cancelled.")
                return False
            
        else:
            scap = engine_info[i]['DrivesCap'][sid][1]        
                              
            if int(pcap) > int(scap):
                tkMessageBox.showinfo("Connection Manager", "Not enough capacity on Secondary LUN!")
                return False

            self.mmtv_sml[i].insert("", 0, text="-----", 
                values=(pid, sid, '{:,}'.format(int(engine_info[i]['DrivesCap'][pid][1]))))
        
            ans = tkMessageBox.askokcancel("Create Mirror", 
                "Request to: \nmirror %s and %s, and rebuild from %s to %s. \n\nIs that correct?" % (pid, sid, pid, sid))

            if ans != True:
                tkMessageBox.showinfo("Create Mirror", "Action has been cancelled.")
                return False

        p = ControlEngine.xEngine()
        if p.SetCreateMirror(i, pid, sid) == False:
            tkMessageBox.showinfo("Create Mirror",
                "Mirror creation process failed, mirror may or may not be created, please double check the result!")
            return False                    
        
        self.mmtv_sml[i].delete(*self.mmtv_sml[i].get_children())
        self.mmtv_spl[i].delete(*self.mmtv_spl[i].get_children())
        self.mmtv_ssl[i].delete(*self.mmtv_ssl[i].get_children())
        engine_info[i]["Selected"]["Mirror"] = ""
        engine_info[i]["Selected"]["Primary"] = ""
        engine_info[i]["Selected"]["Secondary"] = ""
        self.__DB2Panel_MST(i)
        self.__DB2Panel_PST(i)
        self.__DB2Panel_SST(i)
#
    def __CreateMirrorNR(self, i):
        self.mmtv_sml[i].delete(*self.mmtv_sml[i].get_children())
        engine_info[i]["Selected"]["Mirror"] = ""

        pid = engine_info[i]["Selected"]["Primary"]
        sid = engine_info[i]["Selected"]["Secondary"]
            
        if pid == "": 
            tkMessageBox.showinfo("Create Mirror", "Primary LUN has not selected!")
            return False

        pcap = engine_info[i]['DrivesCap'][pid][1]

        if sid == "": 
            self.mmtv_sml[i].insert("", 0, text="-----", 
                values=(pid, sid, '{:,}'.format(int(engine_info[i]['DrivesCap'][pid][1]))))

            ans = tkMessageBox.askokcancel("Create Mirror", 
                "Request to: \ncreate one way mirror with %s \n\nIs that correct?" % pid)

            if ans != True:
                tkMessageBox.showinfo("Create Mirror", "Action has been cancelled.")
                return False
            
        else:
            scap = engine_info[i]['DrivesCap'][sid][1]        
                              
            if int(pcap) > int(scap):
                tkMessageBox.showinfo("Connection Manager", "Not enough capacity on Secondary LUN!")
                return False

            self.mmtv_sml[i].insert("", 0, text="-----", 
                values=(pid, sid, '{:,}'.format(int(engine_info[i]['DrivesCap'][pid][1]))))
        
            ans = tkMessageBox.askokcancel("Create Mirror", 
                "Request to: \nmirror %s and %s, and rebuild from %s to %s. \n\nIs that correct?" % (pid, sid, pid, sid))

            if ans != True:
                tkMessageBox.showinfo("Create Mirror", "Action has been cancelled.")
                return False

        p = ControlEngine.xEngine()
        if p.SetCreateMirror(i, pid, sid, "no_rebuild") == False:
            tkMessageBox.showinfo("Create Mirror",
                "Mirror creation process failed, mirror may or may not be created, please double check the result!")
            return False                    
        
        self.mmtv_sml[i].delete(*self.mmtv_sml[i].get_children())
        self.mmtv_spl[i].delete(*self.mmtv_spl[i].get_children())
        self.mmtv_ssl[i].delete(*self.mmtv_ssl[i].get_children())
        engine_info[i]["Selected"]["Mirror"] = ""
        engine_info[i]["Selected"]["Primary"] = ""
        engine_info[i]["Selected"]["Secondary"] = ""
        self.__DB2Panel_MST(i)
        self.__DB2Panel_PST(i)
        self.__DB2Panel_SST(i)
#        
    def __ConfirmMirrorLUN(self, i):
        self.mmtv_spl[i].delete(*self.mmtv_spl[i].get_children())
        self.mmtv_ssl[i].delete(*self.mmtv_ssl[i].get_children())
        engine_info[i]["Selected"]["Primary"] = ""
        engine_info[i]["Selected"]["Secondary"] = ""

        mid = engine_info[i]["Selected"]["Mirror"]            
        if mid == "":
            tkMessageBox.showinfo("Mirror Manager", "Mirror LUN has not selected.")
            return False
                                
        pid = engine_info[i]['Mirror'][mid][3]
        sid = engine_info[i]['Mirror'][mid][5]
        
        if pid not in engine_info[i]['Drive']:
            self.mmtv_spl[i].insert("", 0, text=pid, values=('-', '-', '-', '-'))
        else:
            for wwpn in engine_info[i]['Drive'][pid]:
                self.mmtv_spl[i].insert("", 0, text=pid, 
                    values=(engine_info[i]['Drive'][pid][wwpn][0], engine_info[i]['Drive'][pid][wwpn][1],
                        '{:,}'.format(int(engine_info[i]['DrivesCap'][pid][1])), engine_info[i]['Drive'][pid][wwpn][2]))
                break

        if sid == '-': return

        if sid not in engine_info[i]['Drive']:
            self.mmtv_ssl[i].insert("", 0, text=sid, values=('-', '-', '-', '-'))
        else:
            for wwpn in engine_info[i]['Drive'][sid]:
                self.mmtv_ssl[i].insert("", 0, text=sid, 
                    values=(engine_info[i]['Drive'][sid][wwpn][0], engine_info[i]['Drive'][sid][wwpn][1],
                        '{:,}'.format(int(engine_info[i]['DrivesCap'][sid][1])), engine_info[i]['Drive'][sid][wwpn][2]))
                break
                    
    def __BreakMirror(self, i):
        if self.__ConfirmMirrorLUN(i) == False: return False
        
        mid = engine_info[i]["Selected"]["Mirror"][:5]
        pid = engine_info[i]['Mirror'][mid][3]
        sid = engine_info[i]['Mirror'][mid][5]

        ans = tkMessageBox.askokcancel("Break Mirror", 
            "Request to: \nSplit mirror set %s, break into %s and %s, and keep both's data intact. \n\nIs that correct?" % (mid, pid, sid))

        if ans != True:
            tkMessageBox.showinfo("Break Mirror", "Action has been cancelled.")
            return False

        p = ControlEngine.xEngine()
        if p.SetBreakMirror(i, mid) == False:
            tkMessageBox.showinfo("Break Mirror",
                "Mirror split process failed, mirror may or may not be deleted, please check the result!")
            return False
        
        self.mmtv_sml[i].delete(*self.mmtv_sml[i].get_children())
        self.mmtv_spl[i].delete(*self.mmtv_spl[i].get_children())
        self.mmtv_ssl[i].delete(*self.mmtv_ssl[i].get_children())
        engine_info[i]["Selected"]["Mirror"] = ""
        engine_info[i]["Selected"]["Primary"] = ""
        engine_info[i]["Selected"]["Secondary"] = ""
        self.__DB2Panel_MST(i)
        self.__DB2Panel_PST(i)
        self.__DB2Panel_SST(i)
        
    def __CloseConfiguration(self, i):
        cfgw_global_ptr[STATUS] = STOPPED
        self.cfgw_ptr.destroy()

    def __SubmitSelection(self, i):
        #
        return

    def __NotAvailable(self):
        tkMessageBox.showinfo("Connection Manager", "This function is currently not available.")
#
    def __GetName(self, i, chk_string):
        for content in name_info[i]:
            if content == chk_string: return name_info[i][content]
        return ''
#
    def __ConfirmAMAP(self, i):
        selected_mode = self.pvar_amap[i].get()
#
        if selected_mode == self.pls_amap[0]:
            if engine_info[i]['AutoMap'] == 'Enabled':
                tkMessageBox.showinfo("Group & Map", "Auto Map already set to %s" % self.pls_amap[0])
                return True
        else:
            if engine_info[i]['AutoMap'] == 'Disabled':
                tkMessageBox.showinfo("Group & Map", "Auto Map already set to %s" % self.pls_amap[1])
                return True
#        
        ans = tkMessageBox.askokcancel("Group & Map", 
            "Request to: \nchange Auto Map mode to \'%s\'. \n\nIs that correct?" % selected_mode)

        if ans != True:
            tkMessageBox.showinfo("Group & Map", "Action has been cancelled.")
            return False

        p = ControlEngine.xEngine()
        if p.ChangeAutoMap(i, selected_mode) == False:
            tkMessageBox.showinfo("Group & Map",
                "Auto Map mode change failed, please check the result!")
            return False

        tkMessageBox.showinfo("Group & Map", "Auto Map mode changed successfully.")
        return True
#
#
    def __ConfirmRebuild(self, i):
        s = self.rbvar_lun[i].get().split()
        lun = s[0]
        member = s[2]
        value = self.rbvar_value[i].get()
        cmd = self.rbvar_mcmd[i].get()
#
        if cmd == '':
            tkMessageBox.showinfo("Rebuild Management", "Please select a command!")
            return True
#
        if (cmd == 'Speed' or cmd == 'IOPS') and value == '':
            tkMessageBox.showinfo("Rebuild Management", "Please input a value!")
            return True
        
        ans = tkMessageBox.askokcancel("Rebuild Management", 
            "Request to: \nchange %s to \'%s\'. \n\nIs that correct?" % (cmd, value))

        if ans != True:
            tkMessageBox.showinfo("Rebuild Management", "Action has been cancelled.")
            return False

        p = ControlEngine.xEngine()
        if p.ChangeRebuild(i, lun, cmd, value, member) == False:
            tkMessageBox.showinfo("Rebuild Management",
                "Rebuild default value change failed, please check the result!")
            return False

        tkMessageBox.showinfo("Rebuild Management", "Rebuild default value changed successfully.")
        return True
#
#
    def __ConfirmDRB(self, i):
        cmd = self.rbvar_dcmd[i].get()
        value = self.rbvar_dvalue[i].get()
#
        if cmd == '':
            tkMessageBox.showinfo("Rebuild Management", "Please select a command!")
            return True
#
        if value == '':
            tkMessageBox.showinfo("Rebuild Management", "Please input a value!")
            return True
        
        ans = tkMessageBox.askokcancel("Rebuild Management", 
            "Request to: \nchange %s to \'%s\'. \n\nIs that correct?" % (cmd, value))

        if ans != True:
            tkMessageBox.showinfo("Rebuild Management", "Action has been cancelled.")
            return False

        p = ControlEngine.xEngine()
        if p.ChangeDRB(i, cmd, value) == False:
            tkMessageBox.showinfo("Rebuild Management",
                "Rebuild default value change failed, please check the result!")
            return False

        tkMessageBox.showinfo("Rebuild Management", "Rebuild default value changed successfully.")
        return True
#
#
    def __ConfirmREMD(self, i):
        selected_mode = self.revar_mmd[i].get()
#
        if selected_mode == self.rels_mmd[0]:
            if engine_info[i]['Special']['pg83 MPIO'] == 'ON':
                tkMessageBox.showinfo("Connection Manager", "conmgr mode already set to %s" % self.rels_mmd[0])
                return True
        else:
            if engine_info[i]['Special']['pg83 MPIO'] == 'OFF':
                tkMessageBox.showinfo("Connection Manager", "conmgr mode already set to %s" % self.rels_mmd[1])
                return True
#        
        ans = tkMessageBox.askokcancel("Connection Manager", 
            "Request to: \nchange conmgr mode to \'%s\'. \n\nIs that correct?" % selected_mode)

        if ans != True:
            tkMessageBox.showinfo("Connection Manager", "Action has been cancelled.")
            return False

        p = ControlEngine.xEngine()
        if p.ChangeConmgrMode(i, selected_mode) == False:
            tkMessageBox.showinfo("Connection Manager",
                "Connection Manager change mode failed, please check the result!")
            return False

        tkMessageBox.showinfo("Connection Manager", "Connection Manager mode changed successfully.")
        return True
#
#
    def __ConfirmREEN(self, i):
        selected_num = self.revar_engnum[i].get()[18:19]
#
        if engine_info[i]['This Engine'] == selected_num:
            tkMessageBox.showinfo("Connection Manager", "This Engine already set to number %s" % selected_num)
            return True
#        
        ans = tkMessageBox.askokcancel("Connection Manager", 
            "Request to: \nchange engine number of this engine to %s. \n\nIs that correct?" % selected_num)

        if ans != True:
            tkMessageBox.showinfo("Connection Manager", "Action has been cancelled.")
            return False

        p = ControlEngine.xEngine()
        if p.ChangeEngineNumber(i, selected_num) == False:
            tkMessageBox.showinfo("Connection Manager",
                "Connection Manager change engine number failed, please check the result!")
            return False

        tkMessageBox.showinfo("Connection Manager", "Connection Manager change engine number successfully.")
        return True
#
    def __ConfirmREUR(self, i):
        device = self.revar_device[i].get()
        port = self.revar_port[i].get()
        wwpn = self.revar_wwpn[i].get()
        if wwpn[:2] == '0x' or wwpn[:2] == '0X':
            wwpn = wwpn[2:]
        tnum = self.revar_tnum[i].get()
        lun_no = self.revar_lun_no[i].get()

        if device == '' or wwpn == '':
            tkMessageBox.showinfo("Manual Registration", "Please input the selection.")
            return False
        if device[:3] == 'LUN':
            type = device[4:]
            device = 'LUN'
        else: type = device 
#
        try:
            int(wwpn, 16)
        except ValueError:
            tkMessageBox.showinfo("Manual Registration", "Invalid WWPN!")
            return False
        if len(wwpn) > 16:
            tkMessageBox.showinfo("Manual Registration", "Invalid WWPN!")
            return False
            
        wwpn = wwpn.rjust(16, '0')
#
# prepare to register LUN
#
        if device == 'LUN':
            if tnum.isdigit() != True or len(tnum) > 4:
                tkMessageBox.showinfo("Manual Registration", "Please input up to 4 digits' number for LUN # and tnum.")
                return False
#
            if lun_no.isdigit() != True or len(lun_no) > 4:
                tkMessageBox.showinfo("Manual Registration", "Please input up to 4 digits' number for LUN # and tnum.")
                return False
#
            tnum = 'T%0.4d' % int(tnum)
            if tnum in engine_info[i]['Drive']:
                for reg_wwpn in engine_info[i]['Drive'][tnum]:
                    if reg_wwpn.replace('-', '').upper() == wwpn.upper():
                        tkMessageBox.showinfo("Manual Registration", "WWPN already defined!")
                        return False
                device = 'LUN Path'     # if the tnum exists, add the path, otherwise, add new drive
#
# prepare to register HBA
#   Note: same wwpn will be checked and rejected by engine
#
        elif device == 'HBA':
            if tnum.isdigit() != True or len(tnum) > 4:
                tkMessageBox.showinfo("Manual Registration", "Please input up to 4 digits' number for LUN # and tnum.")
                return False

            tnum = 'I%0.4d' % int(tnum)
            if tnum in engine_info[i]['Initiator']:
                tkMessageBox.showinfo("Manual Registration", "Initiator Number is used!")
                return False
#
# Prepare to register Engine
#      
        elif device == 'Engine':
            if tnum.isdigit() != True or len(tnum) > 4:
                tkMessageBox.showinfo("Manual Registration", "Please input up to 4 digits' number for LUN # and tnum.")
                return False

            tnum = 'E%0.4d' % int(tnum)
            if tnum in engine_info[i]['Engine']:
                for reg_wwpn in engine_info[i]['Engine'][tnum]:
                    if reg_wwpn.replace('-', '').upper() == wwpn.upper():
                        tkMessageBox.showinfo("Manual Registration", "WWPN already defined!")
                        return False
                device = 'Engine Path'     # if the tnum exists, add the path, otherwise, add new drive
#
# Confirm setting
#
        ans = tkMessageBox.askokcancel("Manual Registration",
            "Request to: \nRegister %s with the: \nport = %s \nwwpn = %s \nlun = %s  \nassign to = %s\n\nIs these correct?"  \
                % (device, port, wwpn, lun_no, tnum))

        if ans != True:
            tkMessageBox.showinfo("Manual Registration", "Action has been cancelled.")
            return False
#
# Issue commands
#
        p = ControlEngine.xEngine()
        if p.SetManualRegister(i, device, type, port, wwpn, lun_no, tnum) == False:
            tkMessageBox.showinfo("Manual Registration",
                "Registraton process failed, please check the result!")
            return False
#
        if p.return_string != '':
            tkMessageBox.showinfo("Manual Registration", "%s, please check the result!" % p.return_string)
#
# Update GUI
#
        p = ControlEngine.xEngine()
        p.UpdateInfo(i, 'cmg')
#
        self.DB2Panel_URT(i)
        self.DB2Panel_RET(i)
#       self.__ClearREURSelection(i)    # (keep the selection info)
#
    def __ConfirmRERE(self, i):
        unreg_id = self.revar_unreg_id[i].get()
        unreg_wwpn = self.revar_unreg_wwpn[i].get()
        wwpn_name = self.revar_wwpn_name[i].get()
#
        if unreg_id == '':
            tkMessageBox.showinfo("Manual Registration", "Please input the selection.")
            return False

        ans = tkMessageBox.askokcancel("Manual Registration",
            "Request to: \nUn-register %s with the: \nwwpn = %s \nname = %s \n\nIs that correct?" % (unreg_id, unreg_wwpn, wwpn_name))

        if ans != True:
            tkMessageBox.showinfo("Manual Registration", "Action has been cancelled.")
            return False

        p = ControlEngine.xEngine()
        if p.RemoveManualRegister(i, unreg_id) == False:
            tkMessageBox.showinfo("Manual Registration",
                "Un-registraton process failed, please check the result!")
            return False
#
        p = ControlEngine.xEngine()
        p.UpdateInfo(i, 'cmg')
#
        self.DB2Panel_URT(i)
        self.DB2Panel_RET(i)
        self.__ClearRERESelection(i)
#
    def __ConfirmHGroup(self, i):
        group_num = self.pvar_init_group[i].get()[11:]
        hba = self.pvar_hba[i].get().split()[0]
        cmd = self.pvar_hcmd[i].get()

        if group_num == '':
            tkMessageBox.showinfo("Host-LUN Mapping", "Please input the proper group number.")
            return False

        if cmd == 'Delete':
            hba = ''        # don't need hba info for delete
            if 'HBA' not in engine_info[i]['Group'] or \
                ('HBA' in engine_info[i]['Group'] and group_num not in engine_info[i]['Group']['HBA']):

                tkMessageBox.showinfo("Host-LUN Mapping", "Host group not found.")
                return False
                
        if cmd == 'Add':
            if 'HBA' in engine_info[i]['Group']:
                if group_num in engine_info[i]['Group']['HBA']:
                    if hba in engine_info[i]['Group']['HBA'][group_num]:
                        tkMessageBox.showinfo("Host-LUN Mapping", "Host group already has this wwpn.")
                        return False

        ans = tkMessageBox.askokcancel("Host-LUN Mapping",
            "Request to: \n%s host group %s with the: \nwwpn = %s\n\nIs that correct?" % (cmd, group_num, hba))

        if ans != True:
            tkMessageBox.showinfo("Host-LUN Mapping", "Action has been cancelled.")
            return False

        p = ControlEngine.xEngine()
        if p.ChangeHostGroup(i, cmd, group_num, hba) == False:
            tkMessageBox.showinfo("Host-LUN Mapping",
                "%s host group operation failed, please check the result!" % cmd)
            return False
#
        p = ControlEngine.xEngine()
        p.UpdateInfo(i, 'cmg')

        tkMessageBox.showinfo("Host-LUN Mapping", "%s host group successfully." % cmd)
        return True
#
#        self.DB2Panel_URT(i)
#        self.DB2Panel_RET(i)
#        self.__ClearRERESelection(i)
#
    def __ConfirmMMap(self, i):
        
        mg = self.pvar_maps[i].get()[11:]
        lun = self.pvar_lun[i].get().split()[0]
        if lun == "--NULL--": lun = ''
        hg = self.pvar_hbag[i].get()[11:]
        cmd = self.pvar_mcmd[i].get()
        
        if mg == '':
            tkMessageBox.showinfo("Host-LUN Mapping", "Please input the proper Mirror Structure.")
            return False
            
        if cmd == 'Add':
            if lun == '' and hg == '':
                tkMessageBox.showinfo("Host-LUN Mapping", "Please select the proper LUN# and/or HBA group.")
                return False
        
        ans = tkMessageBox.askokcancel("Host-LUN Mapping",
            "Request to: \n%s Map Structure %s with the: \nLUN = %s \nHBA Group = %s \n\nIs that correct?" % (cmd, mg, lun, hg))

        if ans != True:
            tkMessageBox.showinfo("Host-LUN Mapping", "Action has been cancelled.")
            return False

        p = ControlEngine.xEngine()
        if p.ChangeMapStructure(i, cmd, mg, lun, hg) == False:
            tkMessageBox.showinfo("Host-LUN Mapping",
                "%s Map Structure operation failed, please check the result!" % cmd)
            return False
#
        p = ControlEngine.xEngine()
        p.UpdateInfo(i, 'cmg')

        tkMessageBox.showinfo("Host-LUN Mapping", "%s Map Structure successfully." % cmd)
        return True
#
#        self.DB2Panel_URT(i)
#        self.DB2Panel_RET(i)
#        self.__ClearRERESelection(i)
#
    def __ConfirmHName(self, i):
        id = self.p_variable_hi[i].get()
        name = self.p_variable_hn[i].get()
        name_info[i][id] = name
        self.__UpdateHNT(i)
        self.__UpdateLMT(i) # also update LUN-Map table that use name
        self.__UpdateHGT(i) # also update Host Group table that use name
        self.__UpdateManuOption(i)
#
    def __ConfirmGName(self, i):
        id = self.p_variable_gi[i].get()
        name = self.p_variable_gn[i].get()
        name_info[i][id] = name
        self.__UpdateGNT(i)
        self.__UpdateLMT(i) # also update LUN-Map table that use name
        self.__UpdateHGT(i) # also update Host Group table that use name
        self.__UpdateManuOption(i)
#
    def __ConfirmLName(self, i):
        id = self.p_variable_li[i].get()
        name = self.p_variable_ln[i].get()
        name_info[i][id] = name
        self.__UpdateLNT(i)
        self.__UpdateLMT(i) # also update LUN-Map table that use name
        self.__UpdateHGT(i) # also update Host Group table that use name
        self.__UpdateManuOption(i)
#
    def __SaveCurrentName(self, i):
        p = ControlName.xName()
        p.SaveCurrentName(i)
#
    def __UpdateCurrentName(self, i):
        p = ControlName.xName()
        p.UpdateCurrentName(i)
#
    def __ReadSavedName(self, i):
        p = ControlName.xName()
        p.ReadSavedNameFile(i)
#
    def __DeleteSavedName(self, i):
        p = ControlName.xName()
        p.DeleteSavedName(i)
#
# Update Auto Registraton tables
#    DB2Panel_ART() ; GetLastCmgInfo()
#
    def DB2Panel_ART(self, engine_idx):
        
        if current_engine[engine_idx][0] == 'on':     # get last Connection Manager Drive info
            #
            # clear treeview
            self.f1_1[engine_idx][self.FRAMES.index('Drive')].delete(
                    *self.f1_1[engine_idx][self.FRAMES.index('Drive')].get_children())
            self.f1_1[engine_idx][self.FRAMES.index('Engine')].delete(
                    *self.f1_1[engine_idx][self.FRAMES.index('Engine')].get_children())
            self.f1_1[engine_idx][self.FRAMES.index('Initiator')].delete(
                    *self.f1_1[engine_idx][self.FRAMES.index('Initiator')].get_children())
            #
            # Update Drive panel
            #   {'Drive': { "T0000": { "5002-2c1001-33d003": (A1, 0001, A, "")}}}
            #
            if engine_info[engine_idx]['Drive'] == {}:
                self.f1_1[engine_idx][self.FRAMES.index('Drive')].insert("", 0, text="",
                    values=("", "empty", "", ""))

            else:
                for did in sorted (engine_info[engine_idx]['Drive'].keys(), reverse=True):
                    for wwpn in sorted (engine_info[engine_idx]['Drive'][did]):
                        self.f1_1[engine_idx][self.FRAMES.index('Drive')].insert("", 0, text=did,
                            values=(engine_info[engine_idx]['Drive'][did][wwpn][0],
                                    wwpn, engine_info[engine_idx]['Drive'][did][wwpn][1],
                                    engine_info[engine_idx]['Drive'][did][wwpn][2]))
            #
            # Update Engine panel
            #   {'Engine': { "E02": { "2300-006022-0929d6": (B1, A),
            #                        "2400-006022-0929d6": (B2, A)}}}
            #
            if engine_info[engine_idx]['Engine'] == {}:
                self.f1_1[engine_idx][self.FRAMES.index('Engine')].insert("", 0, text="",
                    values=("", "empty", "", ""))
            else:
                for eid in sorted (engine_info[engine_idx]['Engine'].keys(), reverse=True):
                    for wwpn in sorted (engine_info[engine_idx]['Engine'][eid]):
                        self.f1_1[engine_idx][self.FRAMES.index('Engine')].insert("", 0, text=eid,
                            values=(engine_info[engine_idx]['Engine'][eid][wwpn][0],
                                    wwpn, "", engine_info[engine_idx]['Engine'][eid][wwpn][1]))
            #
            # Update Initiator panel
            #   {'Initiator': { "I0000": ("0", "A2", "1000-0000c9-b81778", "A"),
            #                   "I0001": ("0", "A2", "1000-0000c9-b8168a", "A")}}
            #
            if engine_info[engine_idx]['Initiator'] == {}:
                self.f1_1[engine_idx][self.FRAMES.index('Initiator')].insert("", 0, text="",
                    values=("", "", "empty",""))
            else:
                for iid in sorted (engine_info[engine_idx]['Initiator'].keys(), reverse=True):
                    for wwpn in sorted (engine_info[engine_idx]['Initiator'][iid]):
                        self.f1_1[engine_idx][self.FRAMES.index('Initiator')].insert("", 0, text=iid,
                            values=(engine_info[engine_idx]['Initiator'][iid][wwpn][0],       # type
                                    engine_info[engine_idx]['Initiator'][iid][wwpn][1],       # port
                                    wwpn,                                                     # wwpn
                                    engine_info[engine_idx]['Initiator'][iid][wwpn][3]))      # status
#
# update engine_info[engine_idx] database
#
            p = ControlEngine.xEngine()
            p.UpdateInfo(engine_idx, 'cmg')
#
# Update Auto Registraton tables
#    DB2Panel_EXT()
#
    def DB2Panel_EXT(self, engine_idx):
        
        if current_engine[engine_idx][0] == 'on':     # get last Connection Manager Drive info
            #
            # clear treeview
            for item in self.PORTS:
                self.exp_tv[engine_idx][self.PORTS.index(item)].delete(
                    *self.exp_tv[engine_idx][self.PORTS.index(item)].get_children())
#
#   {'Explore': { "A1": { 'Drive': { "5002-2c1001-33d003": { '0001' ('2929.6GB', 'dg0ld0', '0x010825')}}
#                       { 'Initiator': { '5006-022300-ad0c2b': (0x020600)}}}}}
#
                if engine_info[engine_idx]['Explore'] == {}:
                    self.exp_tv[engine_idx][self.PORTS.index(item)].insert("", 0, text="",
                        values=("", "empty", "", ""))
            
            for port in sorted (engine_info[engine_idx]['Explore'].keys()):
                for type in sorted (engine_info[engine_idx]['Explore'][port]):
                    if type == 'Drive':
                        for wwpn in sorted (engine_info[engine_idx]['Explore'][port][type]):
                            self.exp_tv[engine_idx][self.PORTS.index(port)].insert("", 'end', text='Target', values=('', wwpn.upper()))
                            for luns in sorted (engine_info[engine_idx]['Explore'][port][type][wwpn]):
                                cap = engine_info[engine_idx]['Explore'][port][type][wwpn][luns][0]
                                sn = engine_info[engine_idx]['Explore'][port][type][wwpn][luns][1]
                                self.exp_tv[engine_idx][self.PORTS.index(port)].insert("", 'end', text=luns, values=(cap, sn))
                                   
                    if type == 'Initiator':
                        for wwpn in sorted (engine_info[engine_idx]['Explore'][port][type]):
                            self.exp_tv[engine_idx][self.PORTS.index(port)].insert("", 'end', text=type, values=('', wwpn.upper()))                            
            return
#
    def __RBTonDoubleClick(self, i, event):
        item = self.rbtv_ml[i].identify('row',event.x,event.y)
        type = self.rbtv_ml[i].item(item,"text")
        s = self.rbtv_ml[i].item(item, 'values')
        map_id = s[0]
        self.rbvar_maps[i].set(type)
#
    def __HGTonDoubleClick(self, i, event):
        item = self.hltv_lm[i].identify('row',event.x,event.y)
        type = self.hltv_lm[i].item(item,"text")
        s = self.hltv_lm[i].item(item, 'values')
        map_id = s[0]
        self.pvar_maps[i].set("MAP group #%s" % map_id)
#
    def __UpdateManuOption(self, i):
#
# Update Mirror LUN Option in Host-Map page
#
#
        list = ["--NULL--"]
        self.bb2[i]['menu'].delete(0, 'end')
        self.pvar_lun[i].set(list[0])
            
        for mirror_id in engine_info[i]['Mirror']:
            mirror_name = self.__GetName(i, mirror_id)
            if mirror_name == '': list.append(mirror_id)
            else: list.append(mirror_id+' : '+mirror_name)
        for entry in list:    
            self.bb2[i]['menu'].add_command(label=entry, command=Tkinter._setit(self.pvar_lun[i], entry))
#
# Update HBA Group Option in Host-Map page
#
        list = ["--NULL--"]
        self.bb3[i]['menu'].delete(0, 'end')
        self.pvar_hbag[i].set(list[0])
        for hba_group in engine_info[i]['Group']['HBA']:
            list.append('HBA group #%s' % hba_group)
        for entry in list:    
            self.bb3[i]['menu'].add_command(label=entry, command=Tkinter._setit(self.pvar_hbag[i], entry))
#
    def __LMTonDoubleClick(self, i, event):
        item = self.hltv_hg[i].identify('row',event.x,event.y)
        type = self.hltv_hg[i].item(item,"text")
        s = self.hltv_hg[i].item(item, 'values')
        self.pvar_init_group[i].set("HBA group #%s" % type)
#        for wwpn in engine_info[i]['Registered']['Initiator']: self.list_of_hba.append(wwpn)
        
    def __URTonDoubleClick(self, i, event):
        item = self.retv_ur[i].identify('row',event.x,event.y)
        type = self.retv_ur[i].item(item,"text")
        s = self.retv_ur[i].item(item, 'values')
        port = s[0]
        wwpn = s[1]
        lun = s[2]
        sn = s[3]
        cap = s[4]
        
        if type == 'Drive': self.revar_device[i].set(self.rels_device[0])
        elif type == 'Initiator': self.revar_device[i].set('HBA')
        self.revar_wwpn[i].set(wwpn)
        self.revar_lun_no[i].set(lun)
#        self.revar_lun_name[i].set(sn)
#
    def __RETonDoubleClick(self, i, event):
        item = self.retv_re[i].identify('row',event.x,event.y)
        id = self.retv_re[i].item(item,"text")
        s = self.retv_re[i].item(item, 'values')
        port = s[0]
        wwpn = s[1]
        cap = s[3]
        name = ''
        if id in name_info[i]: name = name_info[i][id]
        elif wwpn in name_info[i]: name = name_info[i][id]

        self.revar_unreg_id[i].set(id)
        self.revar_unreg_wwpn[i].set(wwpn)
        self.revar_wwpn_name[i].set(name)
#
    def __MSTonDoubleClick(self, i, event):
        item = self.mmtv_ms[i].identify('row',event.x,event.y)
        s = self.mmtv_ms[i].item(item,"text")

        for mid in engine_info[i]['Mirror']:
            if mid[:5] == s:
                engine_info[i]["Selected"]["Mirror"] = mid
                self.mmtv_sml[i].insert("", 0, text=mid[:5], 
                    values=(engine_info[i]['Mirror'][mid][3], engine_info[i]['Mirror'][mid][5],
                            '{:,}'.format(int(engine_info[i]['Mirror'][mid][2]))))

        self.mmtv_spl[i].delete(*self.mmtv_spl[i].get_children())
        self.mmtv_ssl[i].delete(*self.mmtv_ssl[i].get_children())
        engine_info[i]["Selected"]["Primary"] = ""
        engine_info[i]["Selected"]["Secondary"] = ""
        self.__DB2Panel_MST(i)
        self.__DB2Panel_PST(i)
        self.__DB2Panel_SST(i)
#
    def __PSTonDoubleClick(self, i, event):
        item = self.mmtv_ps[i].identify('row',event.x,event.y)
        s = self.mmtv_ps[i].item(item,"text")
        
        ps_wwpn = self.p_variable_ps[i].get()
        
        for tid in sorted (engine_info[i]['Registered']['Drive'][ps_wwpn]):
            if tid == s:
                engine_info[i]["Selected"]["Primary"] = tid
                self.mmtv_spl[i].insert("", 0, text=tid, 
                    values=(engine_info[i]['Drive'][tid][ps_wwpn][0], engine_info[i]['Drive'][tid][ps_wwpn][1],
                            '{:,}'.format(int(engine_info[i]['DrivesCap'][tid][1])), engine_info[i]['Drive'][tid][ps_wwpn][2]))
        # need to update PST and SST
        self.mmtv_sml[i].delete(*self.mmtv_sml[i].get_children())
        engine_info[i]["Selected"]["Mirror"] = ""
        if engine_info[i]["Selected"]["Secondary"] == "":
            self.mmtv_ssl[i].delete(*self.mmtv_ssl[i].get_children())                
        self.__DB2Panel_MST(i)
        self.__DB2Panel_PST(i)
        self.__DB2Panel_SST(i)
#
    def __SSTonDoubleClick(self, i, event):
        item = self.mmtv_ss[i].identify('row',event.x,event.y)
        s = self.mmtv_ss[i].item(item,"text")

        ss_wwpn = self.p_variable_ss[i].get()
        
        for tid in sorted (engine_info[i]['Registered']['Drive'][ss_wwpn]):
            if tid == s:
                engine_info[i]["Selected"]["Secondary"] = tid
                self.mmtv_ssl[i].insert("", 0, text=tid, 
                    values=(engine_info[i]['Drive'][tid][ss_wwpn][0], engine_info[i]['Drive'][tid][ss_wwpn][1],
                            '{:,}'.format(int(engine_info[i]['DrivesCap'][tid][1])), engine_info[i]['Drive'][tid][ss_wwpn][2]))
        # need to update PST and SST
#        self.mmtv_sml[i].delete(*self.mmtv_sml[i].get_children())
#        engine_info[i]["Selected"]["Mirror"] = ""
        
        if engine_info[i]["Selected"]["Primary"] == "":
            self.mmtv_spl[i].delete(*self.mmtv_spl[i].get_children())                
        self.__DB2Panel_MST(i)
        self.__DB2Panel_PST(i)
        self.__DB2Panel_SST(i)
#
#
    def __HNTonDoubleClick(self, i, event):
        item = self.nmtv_hn[i].identify('row',event.x,event.y)
        s = self.nmtv_hn[i].item(item,"text")
        iid = engine_info[i]['Initiator'][s].keys()[0]
        self.p_variable_hi[i].set(iid)
        self.p_variable_hn[i].set('')
        for nid in name_info[i]:
            if iid == nid: self.p_variable_hn[i].set(name_info[i][nid])
#
    def __GNTonDoubleClick(self, i, event):
        item = self.nmtv_gn[i].identify('row',event.x,event.y)
        s = self.nmtv_gn[i].item(item,"text")
        self.p_variable_gi[i].set(s)
        self.p_variable_gn[i].set('')
        for nid in name_info[i]:
            if s == nid: self.p_variable_gn[i].set(name_info[i][nid])

    def __LNTonDoubleClick(self, i, event):
        item = self.nmtv_ln[i].identify('row',event.x,event.y)
        tid = self.nmtv_ln[i].item(item,"text")
        self.p_variable_li[i].set(tid)
        self.p_variable_ln[i].set('')
        for nid in name_info[i]:
            if tid == nid: self.p_variable_ln[i].set(name_info[i][tid])
#
    def __EngineInfoOnMotion(self, event):
        row_id = self.mmtv_ps[0].identify_row(event.y)
        column_id = self.mmtv_ps[0].identify_column(event.x)
        item = self.mmtv_ps[0].identify('row',event.x,event.y)

    def __OptionList_ps_ok(self, i):
        self.mmtv_sml[i].delete(*self.mmtv_sml[i].get_children())
        self.mmtv_spl[i].delete(*self.mmtv_spl[i].get_children())
        engine_info[i]["Selected"]["Mirror"] = ""
        engine_info[i]["Selected"]["Primary"] = ""
        self.__DB2Panel_MST(i)
        self.__DB2Panel_PST(i)
        self.__DB2Panel_SST(i)
#   
    def __OptionList_ss_ok(self, i):
        self.mmtv_sml[i].delete(*self.mmtv_sml[i].get_children())
        self.mmtv_ssl[i].delete(*self.mmtv_ssl[i].get_children())
        engine_info[i]["Selected"]["Mirror"] = ""
        engine_info[i]["Selected"]["Secondary"] = ""
        self.__DB2Panel_MST(i)
        self.__DB2Panel_PST(i)
        self.__DB2Panel_SST(i)
#
    def __DB2Panel_MST(self, i):
        self.mmtv_ms[i].delete(*self.mmtv_ms[i].get_children())
        list = sorted(engine_info[i]["Mirror"])

        if engine_info[i]['Mirror'] == {}: return   
        for mid in list:
            self.mmtv_ms[i].insert("", "end", text=mid[:5], 
                values=(engine_info[i]['Mirror'][mid][1], '{:,}'.format(int(engine_info[i]['Mirror'][mid][2])),
                        engine_info[i]['Mirror'][mid][3][1:], engine_info[i]['Mirror'][mid][4],
                        engine_info[i]['Mirror'][mid][5][1:], engine_info[i]['Mirror'][mid][6]))
# 
    def __DB2Panel_PST(self, i):
        self.mmtv_ps[i].delete(*self.mmtv_ps[i].get_children())         # Clear treeview
        ps_select = self.p_variable_ps[i].get()
        if ps_select == "": return
        if engine_info[i]['Registered']['Drive'] == {}: return
        list = copy.deepcopy(engine_info[i]['Registered']['Drive'][ps_select])        
        list.sort()        
        #
        # reduce the mirrored LUN from list
        for mid in engine_info[i]['Mirror']:
            for j in range (len(list)):
                if list[j] == engine_info[i]['Mirror'][mid][3]:
                    del list[j]
                    break
            for j in range (len(list)):
                if list[j] == engine_info[i]['Mirror'][mid][5]:
                    del list[j]
                    break
        #
        # reduce the selected LUNs from list
        if engine_info[i]["Selected"]["Primary"] != "":
            for j in range (len(list)):
                if list[j] == engine_info[i]["Selected"]["Primary"]:
                    del list[j]
                    break
        if engine_info[i]["Selected"]["Secondary"] != "":
            for j in range (len(list)):
                if list[j] == engine_info[i]["Selected"]["Secondary"]:
                    del list[j]
                    break
        
        if engine_info[i]['Drive'] == {}: return                   
        for tid in list:
            self.mmtv_ps[i].insert("", "end", text=tid, 
                values=(engine_info[i]['Drive'][tid][ps_select][0], engine_info[i]['Drive'][tid][ps_select][1],
                        '{:,}'.format(int(engine_info[i]['DrivesCap'][tid][1])), engine_info[i]['Drive'][tid][ps_select][2]))    
        
    def __DB2Panel_SST(self, i):
        self.mmtv_ss[i].delete(*self.mmtv_ss[i].get_children())
        ss_select = self.p_variable_ss[i].get()
        if ss_select == "": return
        if engine_info[i]['Registered']['Drive'] == {}: return
        list = copy.deepcopy(engine_info[i]['Registered']['Drive'][ss_select])
        list.sort()
        #
        # reduce the mirrored LUN from list
        for mid in engine_info[i]['Mirror']:
            for j in range (len(list)):
                if list[j] == engine_info[i]['Mirror'][mid][3]:
                    del list[j]
                    break
            for j in range (len(list)):
                if list[j] == engine_info[i]['Mirror'][mid][5]:
                    del list[j]
                    break
        #
        # reduce the selected LUNs from list
        if engine_info[i]["Selected"]["Primary"] != "":
            for j in range (len(list)):
                if list[j] == engine_info[i]["Selected"]["Primary"]:
                    del list[j]
                    break
                
        if engine_info[i]["Selected"]["Secondary"] != "":
            for j in range (len(list)):
                if list[j] == engine_info[i]["Selected"]["Secondary"]:
                    del list[j]
                    break
        
        if engine_info[i]['Drive'] == {}: return   
        for tid in list:
            self.mmtv_ss[i].insert("", "end", text=tid, 
                values=(engine_info[i]['Drive'][tid][ss_select][0], engine_info[i]['Drive'][tid][ss_select][1],
                        '{:,}'.format(int(engine_info[i]['DrivesCap'][tid][1])), engine_info[i]['Drive'][tid][ss_select][2]))
#
    def __UpdateRBT(self, i):
        if current_engine[i][0] != 'on': return
        
        self.rbtv_ml[i].delete(*self.rbtv_ml[i].get_children())

#   {"Mirror": {"33281": ["Operational", "-", "1073741824", "T2045", "OK", "T2046", "OK", "-", "-", "-", "-"]}}
#
#   {"Rebuild": {"33281": ["0", "1", "0x0000", "3.4%", "10", "100", "quick", "0:01:32", "0:43:33"]}}

        for mid in sorted(engine_info[i]['Rebuild']):
            idx, engine, member, done, mbps, iops, rebuild_type, active_time, remain_time = engine_info[i]['Rebuild'][mid]
            member = str(int(member, 16))
            status, temp, cap, m1, s1, m2, s2, m3, s3, m4, s4 = engine_info[i]['Mirror'][mid]
            mirror_name = self.__GetName(i, mid)
            cap = '{:,}'.format(int(cap))

            self.rbtv_ml[i].insert("", "end", text=mid, 
                values=(mirror_name, member, cap, m1, s1, m2, s2, m3, s3, m4, s4, mbps+'MB/s', iops+'/s', rebuild_type, active_time,
                        done, remain_time))
#
    def __UpdateHGT(self, i):
        self.hltv_hg[i].delete(*self.hltv_hg[i].get_children())
        if engine_info[i]['Initiator'] == {}: return
#
        for init_id in sorted(engine_info[i]["Initiator"]):
# get wwpn of initiator
            init_name = ''
            wwpn = engine_info[i]["Initiator"][init_id].keys()[0]
# get initiator name
            for s in name_info[i]:
                if s == wwpn:
                    init_name = name_info[i][s]
                    break
# get initiator group number
            init_group_no = ''
            if 'HBA' in engine_info[i]['Group']:
                for n in engine_info[i]['Group']['HBA']:
                    if wwpn in engine_info[i]['Group']['HBA'][n]:
                        init_group_no = n
                        break
# get initiator group name
            init_group_name = self.__GetName(i, "HBA group #%s" % init_group_no)
# get Map number
            map_structure = ''
            if 'Map' in engine_info[i]['Group']:
                for map_no in engine_info[i]['Group']['Map']:
                    if init_id in engine_info[i]['Group']['Map'][map_no]['Used By']:
                        map_structure = map_no
                        break
# get Map Structure name
            map_structure_name = self.__GetName(i, "MAP group #%s" % init_group_no)
# get status
            status = engine_info[i]['Initiator'][init_id][wwpn][3]
#
            self.hltv_hg[i].insert("", "end", text=init_group_no, 
                values=(init_group_name, wwpn.upper(), init_name, map_structure, map_structure_name, status))
#
    def __UpdateLMT(self, i):            
        self.hltv_lm[i].delete(*self.hltv_lm[i].get_children())
        if engine_info[i]['Mirror'] == {}: return
#
        for mirror_id in sorted(engine_info[i]["Mirror"]):
# get LUN name
            phy_lun_name = ''
            for s in name_info[i]:
                if s == mirror_id:
                    phy_lun_name = name_info[i][mirror_id]
                    break
# get Map number
            map_structure = ''
            if 'Map' in engine_info[i]['Group']:
                for map_no in engine_info[i]['Group']['Map']:
                    if mirror_id in engine_info[i]['Group']['Map'][map_no]['Include']:
                        map_structure = map_no
                        break
# get Map Structure name
            map_structure_name = ''
            if map_structure != '':
                for s in name_info[i]:
                    if s == "MAP group #%s" % map_structure:
                        map_structure_name = name_info[i][s]
                        break
# get Capacity
            capacity = '{:,}'.format(int(engine_info[i]['Mirror'][mirror_id][2]))
# get status
            status = 'U'
            if engine_info[i]['Mirror'][mirror_id][0] == 'Operational':
                status = 'A'
            elif engine_info[i]['Mirror'][mirror_id][0] == 'has_undef':
                status = 'U'
            else:
                print "!! Unknown mirror status:", engine_info[i]['Mirror'][mirror_id][0]
#
            self.hltv_lm[i].insert("", "end", text=engine_info[i]['Mirror'][mirror_id][1], 
                values=(map_structure, map_structure_name, mirror_id, phy_lun_name, capacity, status))
#
    def __UpdateHNT(self, i):
        self.nmtv_hn[i].delete(*self.nmtv_hn[i].get_children())
        if engine_info[i]['Initiator'] == {}: return       
#
# get HBA group
#   
        for init_id in sorted(engine_info[i]['Initiator']):
            wwpn = engine_info[i]['Initiator'][init_id].keys()[0]
            HBA_name = ''
            for nid in name_info[i]:
                if wwpn == nid: HBA_name = name_info[i][nid]
            
            self.nmtv_hn[i].insert("", "end", text=init_id,
                values=(wwpn, HBA_name))
#
    def __UpdateGNT(self, i):
        self.nmtv_gn[i].delete(*self.nmtv_gn[i].get_children())

        if engine_info[i]["Group"] == {}: return
        
        if engine_info[i]["Group"]['Drive'] != {}:
            for gid in sorted(engine_info[i]["Group"]['Drive']):
                Group_name = ''
                for nid in name_info[i]:
                    if 'LUN group #%s' % gid == nid: Group_name = name_info[i][nid]
                self.nmtv_gn[i].insert("", "end", text='LUN group #%s' % gid, values=('-', Group_name))
        
        if engine_info[i]["Group"]['HBA'] != {}:
            for gid in sorted(engine_info[i]["Group"]['HBA']):
                Group_name = ''
                for nid in name_info[i]:
                    if 'HBA group #%s' % gid == nid: Group_name = name_info[i][nid]
                self.nmtv_gn[i].insert("", "end", text='HBA group #%s' % gid, values=('-', Group_name))
                    
        if engine_info[i]["Group"]['Map'] != {}:
            for gid in sorted(engine_info[i]["Group"]['Map']):
                Group_name = ''
                for nid in name_info[i]:
                    if 'MAP group #%s' % gid == nid: Group_name = name_info[i][nid]
                self.nmtv_gn[i].insert("", "end", text='MAP group #%s' % gid, values=('-', Group_name))

    def __UpdateLNT(self, i):
        self.nmtv_ln[i].delete(*self.nmtv_ln[i].get_children())
        if engine_info[i]['Drive'] == {} and engine_info[i]["Mirror"] == {} : return

        for mid in sorted( engine_info[i]["Mirror"]):
            MLUN_name = ''
            for nid in name_info[i]:
                if mid == nid: MLUN_name = name_info[i][nid]
            self.nmtv_ln[i].insert("", "end", text=mid,
                values=(engine_info[i]['Mirror'][mid][1], '{:,}'.format(int(engine_info[i]['Mirror'][mid][2])), MLUN_name))
        for tid in sorted( engine_info[i]['Drive']):
            LUN_name = ''
            for nid in name_info[i]:
                if tid == nid: LUN_name = name_info[i][nid]
            for wwpn in engine_info[i]['Drive'][tid]:
                self.nmtv_ln[i].insert("", "end", text=tid,
                    values=(int(engine_info[i]['Drive'][tid][wwpn][1]), '{:,}'.format(int(engine_info[i]['DrivesCap'][tid][1])), LUN_name))
                break
#
#   {"Mirror": {"33281": ["Operational", "-", "1073741824", "T2045", "OK", "T2046", "OK", "-", "-", "-", "-"]}}
#####   {"Initiator": {"I0001": ["2", "A2", "2100-0024ff-5d272b", "A"]}}
#   {"Initiator": {"I0001": {"2100-0024ff-5d272b": ["2", "A2", , "A"]}}}
#   {"Engine": {"E01": {"2300-006022-ad0b60": ["B1", "A"]}}} 
#
#   {'Drive': {"T0000": {"5002-2c1001-33d003": (A1, 0001, A, "")}}}
#   {"DrivesCap": {"T2044": ["", "1073741824", "0", "Operational"]}} 
#   {"DrivesSN": { "T2044": ["A-A", "serial number"]}} 
#
#   {'Explore': { "A1": { 'Drive': { "5002-2c1001-33d003": { '0001': ('2929.6GB', 'dg0ld0', '0x010825', 'T0001')}}
#                                                          { '0006': ('2929.6GB', 'dg0ld0', '0x010825', '')}}
#                       { 'Initiator': { '5006-022300-ad0c2b': ('0x020600', 'I0001')}}}}}
#
#   {"Group": {"Drive": {"0": ["33537", "33538"],
#                        "3": ["33538", "33539"]},
#              "HBA": {"21": ["5006-022100-ad0c2b"]},
#              "Map": {"2": {"Has": ["33537", "33538"],
#                            "Use": ["5006-022300-ad0c2b"]}, 
#                      "3": {"Has": ["33537", "33538"],
#                            "Use": ["5006-022100-ad0c2b"]}, 
#                     "99": {"Has": ["33025", "33026", "33537", "33538"], 
#                            "Use": []}}}}
#
#
    def DB2Panel_RET(self, i):
        self.retv_re[i].delete(*self.retv_re[i].get_children())
#
        for lun_id in sorted( engine_info[i]["Drive"]):
            ser_number = ''
            cap = '{:,}'.format(int(engine_info[i]['DrivesCap'][lun_id][1]))
            for wwpn in sorted( engine_info[i]["Drive"][lun_id]):
                port = engine_info[i]["Drive"][lun_id][wwpn][0]
                lun = engine_info[i]["Drive"][lun_id][wwpn][1]
                status = engine_info[i]["Drive"][lun_id][wwpn][2]
                if lun_id in engine_info[i]['DriveSN']:
                    ser_number = engine_info[i]['DriveSN'][lun_id][1]
                self.retv_re[i].insert("", "end", text=lun_id, values=(port, wwpn.upper(), lun, cap, status))
#
        for eng_id in sorted( engine_info[i]["Engine"]):
            cap = ''
            for wwpn in sorted( engine_info[i]["Engine"][eng_id]):
                port = engine_info[i]["Engine"][eng_id][wwpn][0]
                lun = ''
                status = engine_info[i]["Engine"][eng_id][wwpn][1]
                self.retv_re[i].insert("", "end", text=eng_id, values=(port, wwpn.upper(), lun, cap, status))
#
        for init_id in sorted( engine_info[i]["Initiator"]):
            cap = ''
            wwpn = engine_info[i]["Initiator"][init_id].keys()[0]
            port = engine_info[i]["Initiator"][init_id][wwpn][1]
            lun = ''
            status = engine_info[i]["Initiator"][init_id][wwpn][3]
            self.retv_re[i].insert("", "end", text=init_id, values=(port, wwpn.upper(), lun, cap, status))
#
    def DB2Panel_URT(self, i):
        self.retv_ur[i].delete(*self.retv_ur[i].get_children())
#
# Display the rest as un-registered
#
        for port in sorted( engine_info[i]['Explore']):
            if 'Drive' in engine_info[i]['Explore'][port]:
                for wwpn in engine_info[i]['Explore'][port]['Drive']:
                    for lun_number in sorted( engine_info[i]['Explore'][port]['Drive'][wwpn]):
                        if engine_info[i]['Explore'][port]['Drive'][wwpn][lun_number][3] == '':
                            ser_number = engine_info[i]['Explore'][port]['Drive'][wwpn][lun_number][1]
                            cap = engine_info[i]['Explore'][port]['Drive'][wwpn][lun_number][0]
                            self.retv_ur[i].insert("", "end", text='Drive', values=(port, wwpn.upper(), lun_number, ser_number, cap))
#
        for port in sorted( engine_info[i]['Explore']):
            if 'Initiator' in engine_info[i]['Explore'][port]:
                for wwpn in engine_info[i]['Explore'][port]['Initiator']:
                    self.retv_ur[i].insert("", "end", text='Initiator', values=(port, wwpn.upper(), '', '', ''))
#
    def UpdateAllConfigPanel(self):
        for i in range (engine_number): self.__UpdateRBT(i)

    def liftDisplayConfigPanel(self):
        self.cfgw_ptr.lift()
        self.UpdateAllConfigPanel()

    def refreshDisplayConfigPanel(self):
        self.UpdateAllConfigPanel()

    def __CloseHandler(self):
        cfgw_global_ptr[STATUS] = STOPPED
        self.cfgw_ptr.destroy()
#

if __name__ == '__main__':
#
# Define Global Variables Here
#
    gui_app= DisplayConfigPanel()
    gui_app.startDisplayConfigPanel()

