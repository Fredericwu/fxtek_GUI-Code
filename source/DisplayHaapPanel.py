#!/usr/bin/python
"""
DisplayHaapPanel.py

Created by Susan Cheng on 2014-07-11.
Copyright (c) 2014-2016 __Loxoll__. All rights reserved.
"""

import ttk, Tkinter
import time, datetime, os

file_name = os.path.basename(__file__)

if __name__ == '__main__':
#
# Define Global Variables Here
#
#    from ParseINIfile import ParseINIfile
#    cfg = ParseUtil('Config.ini')
#    engine_number = int(cfg['General']['HAAP_NO'])*2
    pass

class DisplayHaapPanel():

    def __init__(self):
        dbg.printDBG1(file_name, "initiate DisplayHaapPanel")

    def startDisplayHaapPanel(self, c, p):
        self.haapw_ptr = Tkinter.Toplevel()
        mainframe_width = (self.haapw_ptr.winfo_screenwidth() / 2 - 300)
        mainframe_heigth = (self.haapw_ptr.winfo_screenheight() / 2 - 250)
        if engine_number == 2:
            self.haapw_ptr.geometry("+%d+%d" % (LLINE, 115))
        else:
            self.haapw_ptr.geometry("+%d+%d" % (LLINE, 152))
        self.haapw_ptr.protocol("WM_DELETE_WINDOW", self.__CloseHandler)
        self.haapw_ptr.title('--- %s Monitor ---' % p)
        n = ttk.Notebook(self.haapw_ptr)
        n.pack(fill='both', expand='yes')
#
#        style = Style()
#        style.configure("1.TFrame", background="red")
#        style.configure("2.TFrame", background="blue")
#        style.configure("3.TFrame", background="green")
#
        frame_1 = ttk.Frame(self.haapw_ptr, style="1.TFrame")
        frame_2 = ttk.Frame(self.haapw_ptr, style="2.TFrame")
        frame_3 = ttk.Frame(self.haapw_ptr, style="3.TFrame")
        frame_4 = ttk.Frame(self.haapw_ptr, style="1.TFrame")
        frame_5 = ttk.Frame(self.haapw_ptr, style="1.TFrame")
        frame_1.pack()
        frame_2.pack()
        frame_3.pack()
        frame_4.pack()
        frame_5.pack()
        # create the pages
        n.add(frame_1, text='    Mirror View   ')
        n.add(frame_2, text='Registered Devices')
        n.add(frame_3, text='   Storage View   ')
        n.add(frame_4, text='    Engine View   ')
        n.add(frame_5, text='     Host View    ')

        ttk.Style().configure("Treeview", background="light gray", fieldbackground="light gray")

# frame 1 (Mirror View)
        p = ttk.Panedwindow(frame_1, orient=Tkinter.VERTICAL)
        # first pane, which would get widgets gridded into it:
        f1 = ttk.Labelframe(p, text='Engine Display', width = 1200, height=200)
        f2 = ttk.Labelframe(p, text='Mirror Information', width=1200, height=200) # second pane
        p.add(f1)
        p.add(f2)
        p.pack()

        self.tree_mv0 = ttk.Treeview(f1, height = 4, padding = (0,2,0,2))
        column_group = ('c1', 'c2', 'c3', 'c4', 'c5', 'c6', 'c7')
        self.tree_mv0["columns"]=column_group
        for cfg_column in column_group:
            self.tree_mv0.column("%s" % cfg_column , width=100, anchor=Tkinter.CENTER)
        self.tree_mv0.heading("#0", text="Engine : IP")
        self.tree_mv0.column("c1", width=150, anchor=Tkinter.CENTER)
        self.tree_mv0.heading("c1", text="Unique ID")
        self.tree_mv0.column("c2", width=120, anchor=Tkinter.CENTER)
        self.tree_mv0.heading("c2", text="Up Time")
        self.tree_mv0.column("c3", width=80, anchor=Tkinter.CENTER)
        self.tree_mv0.heading("c3", text="Alert Halt")
        self.tree_mv0.column("c4", width=150, anchor=Tkinter.CENTER)
        self.tree_mv0.heading("c4", text="Firmware Rev")
        self.tree_mv0.column("c5", width=80, anchor=Tkinter.CENTER)
        self.tree_mv0.heading("c5", text="Statue")
        self.tree_mv0.column("c6", width=60, anchor=Tkinter.CENTER)
        self.tree_mv0.heading("c6", text="Master")
        self.tree_mv0.column("c7", width=200, anchor=Tkinter.CENTER)
        self.tree_mv0.heading("c7", text="Time Updated")

        self.tree_mv0.bind("<Double-1>", self.__mv0OnMotion)
        self.tree_mv0.pack()
        self.tree_mv0.tag_configure('offline', background='gray')
        
        self.__mv0Update()
        
        self.tree_mv = ttk.Treeview(f2, height = 20, padding = (0,2,0,2))
        column_group = ('c1', 'c2', 'c3', 'c4', 'c5', 'c6', 'c7', 'c8', 'c9', 'c10', 'c11')
        self.tree_mv["columns"]=column_group
        for cfg_column in column_group:
            self.tree_mv.column("%s" % cfg_column , width=60, anchor=Tkinter.CENTER)
        self.tree_mv.heading("#0", text="Engine : IP")
        self.tree_mv.column("c1", width=120, anchor=Tkinter.CENTER)
        self.tree_mv.heading("c1", text="Mirror ID")
        self.tree_mv.column("c2", width=90, anchor=Tkinter.CENTER)
        self.tree_mv.heading("c2", text="Mapped ID")
        self.tree_mv.column("c3", width=140, anchor=Tkinter.E)
        self.tree_mv.heading("c3", text="Size")
        self.tree_mv.heading("c4", text="Member 1")
        self.tree_mv.heading("c5", text="M1 Status")
        self.tree_mv.heading("c6", text="Member 2")
        self.tree_mv.heading("c7", text="M2 Status")
        self.tree_mv.heading("c8", text="Member 3")
        self.tree_mv.heading("c9", text="M3 Status")
        self.tree_mv.heading("c10", text="Member 4")
        self.tree_mv.heading("c11", text="M4 Status")

        self.tree_mv.bind("<Double-1>", self.__mvOnMotion)
        self.tree_mv.pack()
        self.tree_mv.tag_configure('offline', background='gray')

        self.__SortList("Mirror", "mv")
        self.__mvUpdate()
        
# frame 2 (Registered Devices)
        p = ttk.Panedwindow(frame_2, orient=Tkinter.VERTICAL)
        f1 = ttk.Labelframe(p, text='Registered Devices', width = 1200, height=400 )
        p.add(f1)
        p.pack()

        self.tree_rv = ttk.Treeview(f1, height = 26, padding = (0,2,0,2))
        column_group = ('c1', 'c2', 'c3', 'c4', 'c5', 'c6', 'c7', 'c8', 'c9')
        self.tree_rv["columns"]=column_group
        for cfg_column in column_group:
            self.tree_rv.column("%s" % cfg_column , width=60, anchor=Tkinter.CENTER)
        self.tree_rv.heading("#0", text="Engine : IP")
        self.tree_rv.column("c1", width=60, anchor=Tkinter.CENTER)
        self.tree_rv.heading("c1", text="Drive ID")
        self.tree_rv.column("c2", width=60, anchor=Tkinter.CENTER)
        self.tree_rv.heading("c2", text="Path #")
        self.tree_rv.column("c3", width=80, anchor=Tkinter.CENTER)
        self.tree_rv.heading("c3", text="Engine Port")
        self.tree_rv.column("c4", width=200, anchor=Tkinter.CENTER)
        self.tree_rv.heading("c4", text="WWPN")
        self.tree_rv.column("c5", width=80, anchor=Tkinter.CENTER)
        self.tree_rv.heading("c5", text="Type")
        self.tree_rv.column("c6", width=80, anchor=Tkinter.CENTER)
        self.tree_rv.heading("c6", text="LUN")
        self.tree_rv.column("c7", width=150, anchor=Tkinter.E)
        self.tree_rv.heading("c7", text="Size")
        self.tree_rv.column("c8", width=60, anchor=Tkinter.CENTER)
        self.tree_rv.heading("c8", text="Status")
        self.tree_rv.column("c9", width=60, anchor=Tkinter.CENTER)
        self.tree_rv.heading("c9", text="Status (RE)")

        self.tree_rv.bind("<Double-1>", self.__rvOnMotion)
        self.tree_rv.pack()
        self.tree_rv.tag_configure('offline', background='gray')

        self.__SortList('Drive', "rv")
        self.__rvUpdate()

# frame 3 (Storage View)
        p = ttk.Panedwindow(frame_3, orient=Tkinter.VERTICAL)
        # first pane, which would get widgets gridded into it:
        f1 = ttk.Labelframe(p, text='Engine Display', width = 1200, height=200 )
        f2 = ttk.Labelframe(p, text='Drive Information', width=1200, height=200); # second pane
        p.add(f1)
        p.add(f2)
        p.pack()

        self.tree_sv0 = ttk.Treeview(f1, height = 4, padding = (0,2,0,2))
        column_group = ('c1', 'c2', 'c3', 'c4', 'c5', 'c6', 'c7')
        self.tree_sv0["columns"]=column_group
        for cfg_column in column_group:
            self.tree_sv0.column("%s" % cfg_column , width=100, anchor=Tkinter.CENTER)
        self.tree_sv0.heading("#0", text="Engine : IP")
        self.tree_sv0.column("c1", width=150, anchor=Tkinter.CENTER)
        self.tree_sv0.heading("c1", text="Unique ID")
        self.tree_sv0.column("c2", width=120, anchor=Tkinter.CENTER)
        self.tree_sv0.heading("c2", text="Up Time")
        self.tree_sv0.column("c3", width=80, anchor=Tkinter.CENTER)
        self.tree_sv0.heading("c3", text="Alert Halt")
        self.tree_sv0.column("c4", width=150, anchor=Tkinter.CENTER)
        self.tree_sv0.heading("c4", text="Firmware Rev")
        self.tree_sv0.column("c5", width=80, anchor=Tkinter.CENTER)
        self.tree_sv0.heading("c5", text="Statue")
        self.tree_sv0.column("c6", width=60, anchor=Tkinter.CENTER)
        self.tree_sv0.heading("c6", text="Master")
        self.tree_sv0.column("c7", width=200, anchor=Tkinter.CENTER)
        self.tree_sv0.heading("c7", text="Time Updated")

        self.tree_sv0.bind("<Double-1>", self.__sv0OnMotion)
        self.tree_sv0.pack()
        self.tree_sv0.tag_configure('offline', background='gray')

        self.__sv0Update()

        self.tree_sv = ttk.Treeview(f2, height = 20, padding = (0,2,0,2))
        column_group = ('c1', 'c2', 'c3', 'c4', 'c5', 'c6', 'c7', 'c8')
        self.tree_sv["columns"]=column_group
        for cfg_column in column_group:
            self.tree_sv.column("%s" % cfg_column , width=80, anchor=Tkinter.CENTER)
        self.tree_sv.heading("#0", text="Engine : IP")
        self.tree_sv.column("c1", width=80, anchor=Tkinter.CENTER)
        self.tree_sv.heading("c1", text="Drive ID")
        self.tree_sv.column("c2", width=80, anchor=Tkinter.CENTER)
        self.tree_sv.heading("c2", text="Path #")
        self.tree_sv.column("c3", width=80, anchor=Tkinter.CENTER)
        self.tree_sv.heading("c3", text="Engine Port")
        self.tree_sv.column("c4", width=200, anchor=Tkinter.CENTER)
        self.tree_sv.heading("c4", text="WWPN")
        self.tree_sv.column("c5", width=80, anchor=Tkinter.CENTER)
        self.tree_sv.heading("c5", text="LUN")
        self.tree_sv.column("c6", width=150, anchor=Tkinter.E)
        self.tree_sv.heading("c6", text="Size")
        self.tree_sv.column("c7", width=80, anchor=Tkinter.CENTER)
        self.tree_sv.heading("c7", text="Status")
        self.tree_sv.column("c8", width=80, anchor=Tkinter.CENTER)
        self.tree_sv.heading("c8", text="Status (RE)")
#        self.tree_sv.column("c9", width=40, anchor=Tkinter.CENTER)
#        self.tree_sv.heading("c9", text="")

        self.tree_sv.bind("<Double-1>", self.__svOnMotion)
        self.tree_sv.pack()
        self.tree_sv.tag_configure('offline', background='gray')

        self.__SortList('Drive', "sv")
        self.__svUpdate()

# frame 4 (Engine View)
        p = ttk.Panedwindow(frame_4, orient=Tkinter.VERTICAL)
        # first pane, which would get widgets gridded into it:
        f1 = ttk.Labelframe(p, text='Engine Display', width = 1200, height=200 )
        f2 = ttk.Labelframe(p, text='Engine Details', width=1200, height=200); # second pane
        p.add(f1)
        p.add(f2)
        p.pack()

        self.tree_ev0 = ttk.Treeview(f1, height = 4, padding = (0,2,0,2))
        column_group = ('c1', 'c2', 'c3', 'c4', 'c5', 'c6', 'c7')
        self.tree_ev0["columns"]=column_group
        for cfg_column in column_group:
            self.tree_ev0.column("%s" % cfg_column , width=100, anchor=Tkinter.CENTER)
        self.tree_ev0.heading("#0", text="Engine : IP")
        self.tree_ev0.column("c1", width=150, anchor=Tkinter.CENTER)
        self.tree_ev0.heading("c1", text="Unique ID")
        self.tree_ev0.column("c2", width=120, anchor=Tkinter.CENTER)
        self.tree_ev0.heading("c2", text="Up Time")
        self.tree_ev0.column("c3", width=80, anchor=Tkinter.CENTER)
        self.tree_ev0.heading("c3", text="Alert Halt")
        self.tree_ev0.column("c4", width=150, anchor=Tkinter.CENTER)
        self.tree_ev0.heading("c4", text="Firmware Rev")
        self.tree_ev0.column("c5", width=80, anchor=Tkinter.CENTER)
        self.tree_ev0.heading("c5", text="Statue")
        self.tree_ev0.column("c6", width=60, anchor=Tkinter.CENTER)
        self.tree_ev0.heading("c6", text="Master")
        self.tree_ev0.column("c7", width=200, anchor=Tkinter.CENTER)
        self.tree_ev0.heading("c7", text="Time Updated")

        self.tree_ev0.bind("<Double-1>", self.__ev0OnMotion)
        self.tree_ev0.pack()
        self.tree_ev0.tag_configure('offline', background='gray')

        self.__ev0Update()

        self.tree_ev = ttk.Treeview(f2, height = 20, padding = (0,2,0,2))
        column_group = ('c1', 'c2', 'c3', 'c4', 'c5', 'c6')
        self.tree_ev["columns"]=column_group
        for cfg_column in column_group:
            self.tree_ev.column("%s" % cfg_column , width=100, anchor=Tkinter.CENTER)
        self.tree_ev.heading("#0", text="Engine : IP")
        self.tree_ev.column("c1", width=60, anchor=Tkinter.CENTER)
        self.tree_ev.heading("c1", text="Port")
        self.tree_ev.column("c2", width=320, anchor=Tkinter.CENTER)
        self.tree_ev.heading("c2", text="WWNN:WWPN")
        self.tree_ev.column("c3", width=80, anchor=Tkinter.CENTER)
        self.tree_ev.heading("c3", text="Status")
        self.tree_ev.column("c4", width=60, anchor=Tkinter.CENTER)
        self.tree_ev.heading("c4", text="Speed")
        self.tree_ev.column("c5", width=120, anchor=Tkinter.CENTER)
        self.tree_ev.heading("c5", text="Error Rate")
        self.tree_ev.column("c6", width=200, anchor=Tkinter.CENTER)
        self.tree_ev.heading("c6", text="Time Updated")

        self.tree_ev.bind("<Double-1>", self.__evOnMotion)
        self.tree_ev.pack()
        self.tree_ev.tag_configure('offline', background='gray')

        self.__evUpdate()

# frame 5 (Host View)
        p = ttk.Panedwindow(frame_5, orient=Tkinter.VERTICAL)
        # first pane, which would get widgets gridded into it:
        f1 = ttk.Labelframe(p, text='Engine Display', width = 1200, height=200 )
        f2 = ttk.Labelframe(p, text='HBA Information', width=1200, height=200); # second pane
        p.add(f1)
        p.add(f2)
        p.pack()

        self.tree_hv0 = ttk.Treeview(f1, height = 4, padding = (0,2,0,2))
        column_group = ('c1', 'c2', 'c3', 'c4', 'c5', 'c6', 'c7')
        self.tree_hv0["columns"]=column_group
        for cfg_column in column_group:
            self.tree_hv0.column("%s" % cfg_column , width=100, anchor=Tkinter.CENTER)
        self.tree_hv0.heading("#0", text="Engine : IP")
        self.tree_hv0.column("c1", width=150, anchor=Tkinter.CENTER)
        self.tree_hv0.heading("c1", text="Unique ID")
        self.tree_hv0.column("c2", width=120, anchor=Tkinter.CENTER)
        self.tree_hv0.heading("c2", text="Up Time")
        self.tree_hv0.column("c3", width=80, anchor=Tkinter.CENTER)
        self.tree_hv0.heading("c3", text="Alert Halt")
        self.tree_hv0.column("c4", width=150, anchor=Tkinter.CENTER)
        self.tree_hv0.heading("c4", text="Firmware Rev")
        self.tree_hv0.column("c5", width=80, anchor=Tkinter.CENTER)
        self.tree_hv0.heading("c5", text="Statue")
        self.tree_hv0.column("c6", width=60, anchor=Tkinter.CENTER)
        self.tree_hv0.heading("c6", text="Master")
        self.tree_hv0.column("c7", width=200, anchor=Tkinter.CENTER)
        self.tree_hv0.heading("c7", text="Time Updated")

        self.tree_hv0.bind("<Double-1>", self.__hv0OnMotion)
        self.tree_hv0.pack()
        self.tree_hv0.tag_configure('offline', background='gray')

        self.__hv0Update()

        self.tree_hv = ttk.Treeview(f2, height = 20, padding = (0,2,0,2))
#        column_group = ('c1', 'c2', 'c3', 'c4', 'c5', 'c6')
        column_group = ('c1', 'c2', 'c3', 'c5', 'c6')
        self.tree_hv["columns"]=column_group
        for cfg_column in column_group:
            self.tree_hv.column("%s" % cfg_column , width=60, anchor=Tkinter.CENTER)

        self.tree_hv.heading("#0", text="Engine : IP")
        self.tree_hv.column("c1", width=80, anchor=Tkinter.CENTER)
        self.tree_hv.heading("c1", text="Host ID")
        self.tree_hv.column("c2", width=160, anchor=Tkinter.CENTER)
        self.tree_hv.heading("c2", text="WWPN")
        self.tree_hv.column("c3", width=80, anchor=Tkinter.CENTER)
        self.tree_hv.heading("c3", text="Engine Port")
#        self.tree_hv.column("c4", width=60, anchor=Tkinter.CENTER)
#        self.tree_hv.heading("c4", text="Speed")
        self.tree_hv.column("c5", width=120, anchor=Tkinter.CENTER)
        self.tree_hv.heading("c5", text="Status")
#        self.tree_hv.column("c6", width=340, anchor=Tkinter.CENTER)
        self.tree_hv.column("c6", width=400, anchor=Tkinter.CENTER)
        self.tree_hv.heading("c6", text="")

        self.tree_hv.bind("<Double-1>", self.__hvOnMotion)
        self.tree_hv.pack()
        self.tree_hv.tag_configure('offline', background='gray')

        self.__SortList('Initiator', "hv")
        self.__hvUpdate()
    #
    def __mv0OnMotion(self, event):
        row_id = self.tree_mv0.identify_row(event.y)
        column_id = self.tree_mv0.identify_column(event.x)
#        print "mv0 row = %s, colume = %s" % (row_id, column_id)

    #
    def __mvOnMotion(self, event):
        column_id = self.tree_mv.identify_column(event.x)
        
        def __f(x):
            return {
                '#1': 'Mirror ID',
                '#2': 'Mapped ID'
#                '#3': 2, # Size
#                '#4': 3, # Member 1
#                '#5': 4, # M1 Status
#                '#6': 5, # Member 2
#                '#7': 6, # M2 Status
            }.get(x, 'Mirror ID')     # default if x not found

        reverse_sort['mv'] ^= 1        
        self.__SortList("Mirror", __f(column_id), 'mv')
        self.__mvUpdate()
#
    def __rvOnMotion(self, event):
        column_id = self.tree_rv.identify_column(event.x)

        def __f(x):
            return {
                '#1': 'Drive ID',
#                '#2': 1, # Path
                '#3': 'Engine Port',
                '#4': 'WWN',
                '#6': 'LUN',
                '#8': 'Status'
            }.get(x, 'Drive ID')     # default if x not found
        
        reverse_sort["rv"] ^= 1
        self.__SortList('Drive', __f(column_id), 'rv')
        self.__rvUpdate()
    
#
    def __sv0OnMotion(self, event):
        row_id = self.tree_sv0.identify_row(event.y)
        column_id = self.tree_sv0.identify_column(event.x)
#        print "sv0 row = %s, colume = %s" % (row_id, column_id)
#
#   {'Drive': { "T0000": { "5002-2c1001-33d003": (A1, 0001, A, "")}}}
#
    def __svOnMotion(self, event):
        global reverse_sort, sort_key
        column_id = self.tree_rv.identify_column(event.x)
#
        def __f(x):
            return {
                '#1': 'Drive ID',
                '#3': 'Port',
                '#4': 'WWN',
                '#5': 'LUN',
                '#7': 'Status'
            }.get(x, 'Drive ID')     # default if x not found

        reverse_sort['sv'] ^= 1
        self.__SortList('Drive', __f(column_id), 'sv')
        self.__svUpdate()
#
    def __ev0OnMotion(self, event):
        row_id = self.tree_ev0.identify_row(event.y)
        column_id = self.tree_ev0.identify_column(event.x)
#        print "ev0 row = %s, colume = %s" % (row_id, column_id)
    #
    def __evOnMotion(self, event):
        row_id = self.tree_ev.identify_row(event.y)
        column_id = self.tree_ev.identify_column(event.x)
#        print "ev row = %s, colume = %s" % (row_id, column_id)
    #
    def __hv0OnMotion(self, event):
        row_id = self.tree_hv0.identify_row(event.y)
        column_id = self.tree_hv0.identify_column(event.x)
#        print "hv0 row = %s, colume = %s" % (row_id, column_id)
    #
    def __hvOnMotion(self, event):
        global reverse_sort, sort_key
        column_id = self.tree_rv.identify_column(event.x)

        def __f(x):
            return {
                '#1': 'Host ID'
#                '#2': 2, # 5000-612024-534000 (WWN)
#                '#3': 1, # Engine Port
#                '#4': 3, # A, N (Status)
            }.get(x, 'Host ID')     # default if x not found
        
        reverse_sort['hv'] ^= 1
        self.__SortList('Initiator', __f(column_id), 'hv')
        self.__hvUpdate()
    #

#
    def __SortList(self, dictionary, sort_key, page = 'rv'):
#
# Sort the list by dictionary (Drive, Mirror, Initiator, Engine) 
#   on page rv (register view), mv (mirror view), hv (host view), sv (storage view)
#
#   {"Mirror": {"33281": ["Operational", "-", "1073741824", "T2045", "OK", "T2046", "OK", "-", "-", "-", "-"]}}
#   {'Drive': { "T0000": { "5002-2c1001-33d003": (A1, 0001, A, "")}}}
#   {"Initiator": {"I0001": ["2", "A2", "2100-0024ff-5d272b", "A"]}}
#   {"Engine": {"E01": {"2300-006022-ad0b60": ["B1", "A"]}}} 
#
        self.sort_list = [0 for x in range(engine_number)]
        
        for i in range(engine_number):
            self.sort_list[i] = []
            if engine_info[i][dictionary] == {}: continue

            for item_id in sorted( engine_info[i][dictionary], reverse=Tkinter.TRUE):
                sort_idx = 0
                if self.sort_list[i] == []:
                    self.sort_list[i].append(item_id)
                    continue

                for sort_id in self.sort_list[i]:
                    if reverse_sort[page] == 1:
#
                        if dictionary == 'Mirror':          # 'Mirror ID', 'Mapped ID'
                            if sort_key == 'Mirror ID':
                                if int(sort_id) < int(item_id): break
                            else:
                                if int(sort_id) < int(item_id): break
#
                        if dictionary == 'Drive':           # 'Drive ID', 'Engine Port', 'WWN', 'LUN', 'Status'
                            if sort_key == 'Drive ID':
                                if sort_id < item_id: break
                            elif sort_key == 'WWN':
                                if sort_id < item_id: break
                            else:
                                if sort_id < item_id: break
#
                        if dictionary == 'Initiator':       # 'Host ID'
                            if sort_key == 'Host ID':
                                if sort_id < item_id: break
                            else:
                                if sort_id < item_id: break
#
                        if dictionary == 'Engine':          # 'Engine ID', 'Mapped ID'
                            if sort_key == 'Engine ID':
                                if sort_id < item_id: break
                            else:
                                if sort_id < item_id: break
#
                    else:
#
                        if dictionary == 'Mirror':          # 'Mirror ID', 'Mapped ID'
                            if sort_key == 'Mirror ID':
                                if int(sort_id) >= int(item_id): break
                            else:
                                if int(sort_id) >= int(item_id): break
#
                        if dictionary == 'Drive':           # 'Drive ID', 'Engine Port', 'WWN', 'LUN', 'Status'
                            if sort_key == 'Drive ID':
                                if sort_id >= item_id: break
                            elif sort_key == 'WWN':
                                if sort_id >= item_id: break
                            else:
                                if sort_id >= item_id: break
#
                        if dictionary == 'Initiator':       # 'Host ID'
                            if sort_key == 'Host ID':
                                if sort_id >= item_id: break
                            else:
                                if sort_id >= item_id: break
#
                        if dictionary == 'Engine':          # 'Engine ID', 'Mapped ID'
                            if sort_key == 'Engine ID':
                                if sort_id >= item_id: break
                            else:
                                if sort_id >= item_id: break
#
                    sort_idx += 1
                self.sort_list[i].insert(sort_idx, item_id)
#
    def __mv0Update(self):
        for i in self.tree_mv0.get_children():
            self.tree_mv0.delete(i)

        row_idx = 0
        for i in range(engine_number):
            if engine_info[i]['Update'] == {}:
                time_string = ""
            else:
                time_string = engine_info[i]['Update']['date']+" "+engine_info[i]['Update']['time']

            self.tree_mv0.insert("", row_idx,
                    text="Engine%s : %s" % (i, cfg['Engine'+str(i)]['IP']),
                    values=(engine_info[i]['UniqueID'], engine_info[i]['Uptime'], engine_info[i]['Alert'], engine_info[i]['Firmware'],
                    engine_info[i]['Status'], engine_info[i]['Master'], time_string))
            row_idx += 1
    #
    def __mvUpdate(self):
        for i in self.tree_mv.get_children():
            self.tree_mv.delete(i)

        row_idx = 0
        for i in range(engine_number):
            if engine_info[i]['Mirror'] == {}: continue

            for mirror_id in self.sort_list[i]:
                op_status, mirror_map, mirror_size, mirror_m1, mirror_m1_status, mirror_m2, mirror_m2_status, \
                    mirror_m3, mirror_m3_status, mirror_m4, mirror_m4_status = \
                    engine_info[i]['Mirror'][mirror_id]

                self.tree_mv.insert("", row_idx,
                    text="Engine%s : %s" % (i, cfg['Engine'+str(i)]['IP']),
                    values=( mirror_id, mirror_map, '{:,}'.format(int(mirror_size)), mirror_m1, mirror_m1_status, \
                        mirror_m2, mirror_m2_status, mirror_m3, mirror_m3_status, mirror_m4, mirror_m4_status))
                row_idx += 1
    #
    def __rvUpdate(self):
        for i in self.tree_rv.get_children():
            self.tree_rv.delete(i)
            
        row_idx = 0
        for i in range(engine_number):
            if engine_info[i]['Drive'] == {}: continue

            for drive_id in self.sort_list[i]:
#
# {'5742-b0f000-4e4032': ('B1', '0001', 'A', 'A'),
#  '5742-b0f000-4e4022': ('B2', '0001', 'A', 'A'),
#  '5742-b0f000-4e4012': ('B1', '0001', 'A', 'A')}
#
                path_id = 0
                for drive_wwpn in sorted (engine_info[i]['Drive'][drive_id]):
                    engine_port = engine_info[i]['Drive'][drive_id][drive_wwpn][0]
                    drive_lun = engine_info[i]['Drive'][drive_id][drive_wwpn][1]
                    drive_status = engine_info[i]['Drive'][drive_id][drive_wwpn][2]
                    re_status = engine_info[i]['Drive'][drive_id][drive_wwpn][3]
                
                    drive_size = engine_info[i]['DrivesCap'][drive_id][1]
                    self.tree_rv.insert("", row_idx,
                        text="Engine%s : %s" % (i, cfg['Engine'+str(i)]['IP']),
                        values=( drive_id, path_id, engine_port, drive_wwpn.upper(), 'Drive', drive_lun, '{:,}'.format(int(drive_size)), drive_status, re_status))
                    path_id += 1
                    row_idx += 1
    #
    def __sv0Update(self):
        for i in self.tree_sv0.get_children():
            self.tree_sv0.delete(i)

        #
        row_idx = 0
        for i in range(engine_number):
            if engine_info[i]['Update'] == {}:
                time_string = ""
            else:
                time_string = engine_info[i]['Update']['date']+" "+engine_info[i]['Update']['time']

            self.tree_sv0.insert("", row_idx,
                    text="Engine%s : %s" % (i, cfg['Engine'+str(i)]['IP']),
                    values=(engine_info[i]['UniqueID'], engine_info[i]['Uptime'], engine_info[i]['Alert'], engine_info[i]['Firmware'],
                    engine_info[i]['Status'], engine_info[i]['Master'], time_string))
            row_idx += 1    
    #
    def __svUpdate(self):
        for i in self.tree_sv.get_children():
            self.tree_sv.delete(i)

        row_idx = 0
        for i in range(engine_number):
            if engine_info[i]['Drive'] == {}: continue

            path_id = 0
            for drive_id in self.sort_list[i]:
                path_id = 0
                for drive_wwpn in sorted (engine_info[i]['Drive'][drive_id]):
                    engine_port = engine_info[i]['Drive'][drive_id][drive_wwpn][0]
                    drive_lun = engine_info[i]['Drive'][drive_id][drive_wwpn][1]
                    drive_status = engine_info[i]['Drive'][drive_id][drive_wwpn][2]
                    re_status = engine_info[i]['Drive'][drive_id][drive_wwpn][3]
                
                    drive_size = '{:,}'.format(int(engine_info[i]['DrivesCap'][drive_id][1]))
                    
                    self.tree_sv.insert("", row_idx,
                        text="Engine%s : %s" % (i, cfg['Engine'+str(i)]['IP']),
                        values=( drive_id, path_id, engine_port, drive_wwpn.upper(), drive_lun, drive_size, drive_status, re_status))
                    path_id += 1
                    row_idx += 1
    #
    def __ev0Update(self):
        for i in self.tree_ev0.get_children():
            self.tree_ev0.delete(i)

        row_idx = 0
        for i in range(engine_number):
            if engine_info[i]['Update'] == {}:
                time_string = ""
            else:
                time_string = engine_info[i]['Update']['date']+" "+engine_info[i]['Update']['time']
                
            self.tree_ev0.insert("", row_idx,
                    text="Engine%s : %s" % (i, cfg['Engine'+str(i)]['IP']),
                    values=(engine_info[i]['UniqueID'], engine_info[i]['Uptime'], engine_info[i]['Alert'], engine_info[i]['Firmware'],
                    engine_info[i]['Status'], engine_info[i]['Master'], time_string))
            row_idx += 1    
    #
    def __evUpdate(self):
        for i in self.tree_ev.get_children():
            self.tree_ev.delete(i)

        port_set = ('A1', 'A2', 'B1', 'B2')

        row_idx = 0
        for i in range(engine_number):
            if engine_info[i]['Ports'] == {}: continue

            if engine_info[i]['Update'] == {}:
                time_string = ""
            else:
                time_string = engine_info[i]['Update']['date']+" "+engine_info[i]['Update']['time']

            for p in port_set:
                self.tree_ev.insert("", row_idx,
                    text="Engine%s : %s" % (i, cfg['Engine'+str(i)]['IP']),
                    values=(p, engine_info[i]['Ports'][p][0].upper()+" : "+engine_info[i]['Ports'][p][1].upper(), engine_info[i]['Ports'][p][3],
                    engine_info[i]['Ports'][p][4], '', time_string))
                row_idx += 1
    #
    def __hv0Update(self):
        for i in self.tree_hv0.get_children():
            self.tree_hv0.delete(i)

        row_idx = 0
        for i in range(engine_number):
            if engine_info[i]['Update'] == {}:
                time_string = ""
            else:
                time_string = engine_info[i]['Update']['date']+" "+engine_info[i]['Update']['time']
            self.tree_hv0.insert("", row_idx,
                    text="Engine%s : %s" % (i, cfg['Engine'+str(i)]['IP']),
                    values=(engine_info[i]['UniqueID'], engine_info[i]['Uptime'], engine_info[i]['Alert'], engine_info[i]['Firmware'],
                    engine_info[i]['Status'], engine_info[i]['Master'], time_string))
            row_idx += 1    
    #
    def __hvUpdate(self):

        for i in self.tree_hv.get_children():
            self.tree_hv.delete(i)

        row_idx = 0
        for i in range(engine_number):
            if engine_info[i]['Initiator'] == {}: continue

            for host_id in self.sort_list[i]:
                for wwpn in engine_info[i]['Initiator'][host_id]:
                    object_type, engine_port, dummy, LUN_status = \
                        engine_info[i]['Initiator'][host_id][wwpn]

                    self.tree_hv.insert("", row_idx,
                        text="Engine%s : %s" % (i, cfg['Engine'+str(i)]['IP']),
                        values=( host_id, wwpn.upper(), engine_port, LUN_status))
                    row_idx += 1    
    
        
    def __CloseHandler(self):
        haapw_global_ptr[STATUS] = STOPPED
        self.haapw_ptr.destroy()

    def UpdateAllHAAP(self):
        self.__mv0Update()
        self.__SortList("Mirror", "mv")
        self.__mvUpdate()
        self.__SortList('Drive', "rv")
        self.__rvUpdate()
        self.__sv0Update()
        self.__SortList('Drive', "sv")
        self.__svUpdate()
        self.__ev0Update()
        self.__evUpdate()
        self.__hv0Update()
        self.__SortList('Initiator', "hv")
        self.__hvUpdate()

    def liftDisplayHaapPanel(self):
        self.haapw_ptr.lift()
        self.UpdateAllHAAP()

    def refreshDisplayHaapPanel(self):
        self.UpdateAllHAAP()

if __name__ == '__main__':
#
# Define Global Variables Here
#
    gui_app= DisplayHaapPanel()
    gui_app.startDisplayHaapPanel()

