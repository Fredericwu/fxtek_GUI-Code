#!/usr/bin/python
# coding: utf8
"""
DisplayDashboard

Created by Susan Cheng on 2014-07-11.
Copyright (c) 2014-2017 __Loxoll__. All rights reserved.
"""

import ttk, Tkinter
import tkMessageBox

import os
#from functools import partial
#import ParseEngineVPD
from ControlLED import LEDset, Color, LED
import ControlEngine
import DisplayMenubar
import threading, thread
from DisplayHaapPanel import DisplayHaapPanel
from DisplayConfigPanel import DisplayConfigPanel
from DisplayDiagPanel import DisplayDiagPanel
import ControlDiag
import ControlEmail
import ControlName

file_name = os.path.basename(__file__)

COMPANY = "Loxoll"
PRODUCT = "HA-AP"

#COMPANY = u'联创信安'.encode('utf-8')
#PRODUCT = "RSS6000T"
#print COMPANY,PRODUCT
cs = cfg['General']['COMPANY']
ps = cfg['General']['PRODUCT']
#s = u'联创信安'.encode('utf-8')

if cs[1:-1] != "":
    COMPANY = cs[1:-1]
    COMPANY = COMPANY.encode('utf-8')
    if not COMPANY[0].isalnum():
        CHINESE = 1
    dbg.printDBG1(file_name, "Company name: %s" % COMPANY)
if ps[1:-1] != "":
    PRODUCT = ps[1:-1]
    PRODUCT = PRODUCT.encode('utf-8')
    print PRODUCT
    dbg.printDBG1(file_name, "Product name: %s" % PRODUCT)

class DisplayDashboard(Tkinter.Frame):

    counter = 0
    FrameforLED = [[0 for x in range(LED.LED_NO)] for x in range(engine_number/2)]

    def __init__(self, parent):
        dbg.printDBG1(file_name, "initiate DisplayDashboard")
        Tkinter.Frame.__init__(self, parent)
        self.parent = parent

        s = " --- %s %s GUI REV 2.0 (Alpha Release) --- " % (COMPANY, PRODUCT)

        self.parent.title(s)
        style = ttk.Style()
        style.theme_use(Color.THEME)      # ('aqua', 'clam', 'alt', 'default', 'classic')
#        style.configure('.', font=('Arial', 16))   # set font for all widgets
#        style.configure('.', font=('Helvetica', 12))   # set font for all widgets

        style.configure("PANEL.TFrame", padding=2, relief="flat", background = Color.PANEL)
        style.configure("PANEL.TButton", padding=2, relief="sunken", foreground="white",
            background = Color.PANEL, width=18, anchor=Tkinter.W)
        style.map('PANEL.TButton',
                    foreground=[('disabled', 'gray'),
                                ('pressed', 'black'),
                                ('active', 'black')],
                    background=[('disabled', Color.PANEL),
                                ('pressed', '!focus', 'cyan'),
                                ('active', 'white')],
                    highlightcolor=[('focus', 'black'),
                                    ('!focus', Color.PANEL)],
                    relief=[('pressed', 'groove'),
                            ('!pressed', 'ridge')])
#        style.configure("P.TButton", padding=2, relief="raised", borderwidth=4,
        style.configure("P.TButton", padding=2, relief="sunken", borderwidth=4,
            background = Color.PANEL, foreground="white", width=6,
                highlightcolor= Color.PANEL)
        style.map('P.TButton',
                    foreground=[('disabled', 'gray'),
                                ('pressed', 'black'),
                                ('active', 'black')],
                    background=[('disabled', Color.PANEL),
                                ('pressed', '!focus', 'cyan'),
                                ('active', 'white')],
                    highlightcolor=[('focus', 'black'),
                                    ('!focus', Color.PANEL)],
                    relief=[('pressed', 'groove'),
                            ('!pressed', 'raised')])

        style.configure("LED.TCanvas", padding=6, relief="flat", width=15, height=10)

        basesize = 10
        d = center = int(basesize/2)
        r = int((basesize-2)/2)
        f = [0 for x in range(engine_number/2)]

        tf = ttk.Frame(self.parent, height=40, width=740, style='PANEL.TFrame')
        tf.grid(row=0, column=0)
#
        DBW = 16+6  # (Construction button removed)
#
# <Monitor> Button
        if CHINESE == 1:
            s = u'监 控'.encode('utf-8')
        else:
            s = "Monitor"    
        cbtn = ttk.Button(tf, text=s, width = DBW, style= 'P.TButton', command=self.__DisplayHaapPanel)
        cbtn.grid(row=0, column=0)
#
# <Configuration> Button
        if CHINESE == 1:
            s = u'配 置'.encode('utf-8')
        else:
            s = "Configuration"    
        cbtn = ttk.Button(tf, text=s, width = DBW, style= 'P.TButton', command= self.__ConfigurationPanel)
        cbtn.grid(row=0, column=1)
#
# <Construction> Button
        #
        """
        if CHINESE == 1:
            s = u'架 构'.encode('utf-8')
        else:
            s = "Construction"    
        cbtn = ttk.Button(tf, text=s, width = DBW, style= 'P.TButton', command= self.__ConstructionPanel)
        cbtn.grid(row=0, column=2)
        """
#
# <Diagnosis> Button
        #
        if CHINESE == 1:
            s = u'诊 断'.encode('utf-8')
        else:
            s = "Diagnosis"    
        cbtn = ttk.Button(tf, text=s, width = DBW, style= 'P.TButton', command= self.__DiagnosisPanel)
        cbtn.grid(row=0, column=3)

        for i in range (0, engine_number/2):
# Lay the framework for LED/Engine/Cluster
            f[i] = ttk.Frame(self.parent, height=40, width=740,
                style='PANEL.TFrame')
            f[i].grid(row=i+1, column=0)
# LED 0
            self.FrameforLED[i][0] = ttk.Frame(f[i], style= 'PANEL.TFrame')
            self.FrameforLED[i][0].grid(row=0, column=0)
            led_ptr[i][0] = LEDset (self.FrameforLED[i][0], status=LED.OFF, blink=LED.OFF)
            led_ptr[i][0].frame.pack(expand=YES, padx=9, pady=9)
# Engine A
            if single_engine == "Yes" and cfg['CG0']['MEMBER'][1:-1] == "1":
                cbtn = ttk.Label(f[i], text= 10*" "+"--empty--", style= 'PANEL.TButton')
            else:
                cbtn = ttk.Label(f[i], text="E%s: " % (i*2) +cfg["Engine"+str(i*2)]['IP'], style= 'PANEL.TButton')
            cbtn.grid(row=0, column=1)
# LED 1
            self.FrameforLED[i][1] = ttk.Frame(f[i], style= 'PANEL.TFrame')
            self.FrameforLED[i][1].grid(row=0, column=2)
            led_ptr[i][1] = LEDset (self.FrameforLED[i][1], status=LED.OFF, blink=LED.OFF)
            led_ptr[i][1].frame.pack(expand=YES, padx=9, pady=9)
# Engine B
            if single_engine == "Yes" and cfg['CG0']['MEMBER'][1:-1] == "0":
                cbtn = ttk.Label(f[i], text= 10*" "+"--empty--", style= 'PANEL.TButton')
            else:
                cbtn = ttk.Label(f[i], text="E%s: " % (i*2+1) +cfg["Engine"+str(i*2+1)]['IP'], style= 'PANEL.TButton')
            cbtn.grid(row=0, column=3)
# LED 2
            self.FrameforLED[i][2] = ttk.Frame(f[i], style= 'PANEL.TFrame')
            self.FrameforLED[i][2].grid(row=0, column=4)
            led_ptr[i][2] = LEDset (self.FrameforLED[i][2], status=LED.OFF, blink=LED.OFF)
            led_ptr[i][2].frame.pack(expand=YES, padx=9, pady=9)
# Appliance
            cluster_group = cfg['CG'+str(i)]['MEMBER'][1:-1].split(',')
            if cluster_group == ['']: cluster_group = []            
            cluster_string = "-"
            
            for cluster_member in cluster_group:
#                s = cfg["Engine"+cluster_member]['IP']
#                cluster_string = cluster_string + s[s.find('.' ,s.find('.', s.find('.')+1)+1)+1:] + "-"
                s = "E"+cluster_member
                cluster_string = cluster_string + s + "-"
            cbtn = ttk.Label(f[i], text="CG"+str(i)+": "+cluster_string+ " ", width=18, style= 'PANEL.TButton')
            cbtn.grid(row=0, column=5)

#
# Initialize Monitor Window
        haapw_global_ptr[POINTER] = DisplayHaapPanel()
        haapw_global_ptr[STATUS] = STOPPED
#
# Initialize Config Window
        cfgw_global_ptr[POINTER] = DisplayConfigPanel()
        cfgw_global_ptr[STATUS] = STOPPED
#
# Initialize Diag Window
        diag_global_ptr[POINTER] = DisplayDiagPanel()
        diag_global_ptr[STATUS] = STOPPED

    def __DisplayHaapPanel(self):
        dbg.printDBG1(file_name, "start Monitor window")

        if haapw_global_ptr[STATUS] == STOPPED:
            dbg.printDBG2(file_name, "new start")
            haapw_global_ptr[STATUS] = JUST_START
            haapw_global_ptr[POINTER].startDisplayHaapPanel(COMPANY, PRODUCT)
        else:
            dbg.printDBG2(file_name, "already start, just bring to front")
            haapw_global_ptr[POINTER].liftDisplayHaapPanel()

    def __ConfigurationPanel(self):
        dbg.printDBG1(file_name, "start Configuration window")
        if MONITOR == 1: return
#        if DEVELOPMENT == 0:
#            thread.start_new_thread( tkMessageBox.showinfo, 
#                ("Configuration Panel", "Configuration will be available for future release."))
#            return

        if cfgw_global_ptr[STATUS] == STOPPED:
            dbg.printDBG2(file_name, "new start")
            cfgw_global_ptr[STATUS] = JUST_START
            cfgw_global_ptr[POINTER].startDisplayConfigPanel(COMPANY, PRODUCT)
        else:
            dbg.printDBG2(file_name, "already start, just bring to front")
            cfgw_global_ptr[POINTER].liftDisplayConfigPanel()
#
    def __ConstructionPanel(self):
        dbg.printDBG1(file_name, "start Construction window")
        thread.start_new_thread( tkMessageBox.showinfo, 
                ("Structure Panel", "Construction will be available for future release."))
#
    def __DiagnosisPanel(self):
        dbg.printDBG1(file_name, "start Diagnosis window")
        if MONITOR == 1: return
#        if DEVELOPMENT == 0:
#            thread.start_new_thread( tkMessageBox.showinfo, 
#                ("Configuration Panel", "Diagnosis will be available for future release."))
#            return

        if diag_global_ptr[STATUS] == STOPPED:
            dbg.printDBG2(file_name, "new start")
            diag_global_ptr[STATUS] = JUST_START
            diag_global_ptr[POINTER].startDisplayDiagPanel(COMPANY, PRODUCT)
        else:
            dbg.printDBG2(file_name, "already start, just bring to front")
            diag_global_ptr[POINTER].liftDisplayDiagPanel()
#
    def __SendTrace(self):
        dbg.printDBG1(file_name, "start send trace process")
        du = ControlDiag.xDiagUtility()
        du.SendTrace()
#        thread.start_new_thread( du.SendTrace, ())
		
    def WindowStart(self, i):
        self.counter += 1
        t = Toplevel(self)
        t.title("%s Window #%s" % (PRODUCT, self.counter))
        l = Label(t, text="%s GUI Window from #%s" % (PRODUCT,i))
        l.pack(side="top", fill="both", expand=True, padx=200, pady=100)

import ControlTCP

class TimerThread (threading.Thread):
    global current_engine

    def __init__(self, event):
        dbg.printDBG1(file_name, "initiate TimerThread")

        threading.Thread.__init__(self)
        self.stopped = event

        for i in range(0, engine_number):
            current_engine[i] = ('off','off','dark','solid')

        for i in range(0, engine_number/2):
            cluster_group[i] = cfg['CG'+str(i)]['MEMBER'][1:-1].split(',')
            if cluster_group[i] == ['']: cluster_group[i] = []
            if cluster_group[i] == []:
                current_cluster[i] = ('off','off','dark','solid')
            else:
                current_cluster[i] = ('off','off','dark','solid')

        self.es = ControlEngine.xEngine()

    def run(self):
        while not self.stopped.wait(BG_TIMER):
            dbg.printDBG2 (file_name, "%s second background loop --" % BG_TIMER)
#
# Update Current Engine LED
#            
            for engine_idx in range (0, engine_number):
                if program_stop == True: break
                
                if single_engine == "Yes":
                    if cfg['CG0']['MEMBER'][1:-1] == "0":
                        if engine_idx == 1: continue
                    if cfg['CG0']['MEMBER'][1:-1] == "1":
                        if engine_idx == 0: continue                
                
                dbg.printDBG2 (file_name, "Engine%s in state %s" % (engine_idx, current_engine[engine_idx]))
#
# Engine on2on
                if current_engine[engine_idx] == ('on', 'on', 'green', 'solid'):
                    if self.es.UpdateInfo(engine_idx) == True:
                        dbg.printDBG1 (file_name, "engine%s %s -- VPD updated" % (engine_idx, current_engine[engine_idx]))
                        if engine_info[engine_idx]['Alert'] == 'None':
                            current_engine[engine_idx] = ('on','on','green','solid')
                        else:
                            current_engine[engine_idx] = ('on','off','yellow','solid')
                            dbg.printDBG1 (file_name, "engine%s %s -- in Alert Halt %s" % \
                                (engine_idx, current_engine[engine_idx], engine_info[engine_idx]['Alert']))                          
                    else:
                        current_engine[engine_idx] = ('on','off','yellow','solid')                    
                        dbg.printDBG1 (file_name, "engine%s %s -- not able to update VPD" % (engine_idx, current_engine[engine_idx]))
#
# Engine off2on
                elif current_engine[engine_idx] == ('off','on','green','blinking'):
                    if self.es.UpdateInfo(engine_idx) == True:
                        dbg.printDBG1 (file_name, "engine%s %s -- VPD collected" % (engine_idx, current_engine[engine_idx]))
                        p = ControlName.xName()         
                        p.ReadSavedName(engine_idx)     # get the saved names from file
                        if engine_info[engine_idx]['Alert'] == 'None':
                            current_engine[engine_idx] = ('on','on','green','solid')
                            dbg.printDBG1 (file_name, "engine%s %s -- normal state" % (engine_idx, current_engine[engine_idx]))                          
                        else:
                            current_engine[engine_idx] = ('on','off','yellow','solid')
                            dbg.printDBG1 (file_name, "engine%s %s -- in Alert Halt %s" % \
                                (engine_idx, current_engine[engine_idx], engine_info[engine_idx]['Alert']))                          
                    else:
                        current_engine[engine_idx] = ('on','off','yellow','solid')
                        dbg.printDBG1 (file_name, "engine%s %s -- not able to collect VPD" % (engine_idx, current_engine[engine_idx]))
#
# Engine on2off                        
                elif current_engine[engine_idx] == ('on','off','yellow','solid'):
                    if self.es.DetectEngine(engine_idx) == True:
                        current_engine[engine_idx] = ('off','on','green','blinking')
                        dbg.printDBG1 (file_name, "engine%s %s -- engine detected" % (engine_idx, current_engine[engine_idx]))
                    else:
                        current_engine[engine_idx] = ('off','off','red','solid')
                        dbg.printDBG1 (file_name, "engine%s %s -- not able to detect engine" % (engine_idx, current_engine[engine_idx]))
#
# Engine off2off
                elif current_engine[engine_idx][0:2] == ('off','off'):
                    if self.es.DetectEngine(engine_idx) == True:
                        current_engine[engine_idx] = ('off','on','green','blinking')
                        dbg.printDBG1 (file_name, "engine%s %s -- engine detected" % (engine_idx, current_engine[engine_idx]))
                else:
                    dbg.printDBG0 (file_name, "engine%s %s -- not supported engine, Alart Halt!!!" % (engine_idx, current_engine[engine_idx]))
                    raw_input("AH8") 
#
# Update Current Cluster LED
#
            for cluster_idx in range (0, engine_number/2):
                if program_stop == True: break
                if cluster_group[cluster_idx] == []: continue
                
                dbg.printDBG2 (file_name, "Cluster%s in state %s" % (cluster_idx, current_cluster[cluster_idx]))
#
# Cluster on2on
                if current_cluster[cluster_idx] == ('on', 'on', 'green', 'solid'):
                    if self.__MirrorAllGood(cluster_idx) != True:
                        current_cluster[cluster_idx] = ('on', 'exp', 'yellow', 'blinking')
                        dbg.printDBG1 (file_name, "Cluster%s %s -- Mirror exposed" % (cluster_idx, current_cluster[cluster_idx]))
                    elif self.__ClusterAllGood(cluster_idx) != True:
                        current_cluster[cluster_idx] = ('on','exp','yellow','blinking')
                        dbg.printDBG1 (file_name, "Cluster%s %s -- CG engine missing" % (cluster_idx, current_cluster[cluster_idx]))
                    elif self.__PortAllGood(cluster_idx) != True:
                        current_cluster[cluster_idx] = ('on','exp','yellow','blinking')
                        dbg.printDBG1 (file_name, "Cluster%s %s -- engine BPT issue" % (cluster_idx, current_cluster[cluster_idx]))
#
# Cluster on2exp                     
                elif current_cluster[cluster_idx][0:2] == ('on','exp'):
                    if self.__MirrorFailed(cluster_idx) == True:
                        current_cluster[cluster_idx] = ('exp', 'off', 'red', 'solid')
                        self.__SendEmailNotification('Mirror Failed')
                        dbg.printDBG1 (file_name, "Cluster%s %s -- Mirror Failed" % (cluster_idx, current_cluster[cluster_idx]))
                    elif self.__ClusterAllDown(cluster_idx) == True:
                        current_cluster[cluster_idx] = ('exp', 'chk', 'red', 'solid')
#                        self.__SendEmailNotification('Cluster Failed')      # don't report immediately, it maybe just temp ethernet problem
                        dbg.printDBG1 (file_name, "Cluster%s %s -- Cluster All Down" % (cluster_idx, current_cluster[cluster_idx]))
                    elif self.__MirrorAllGood(cluster_idx) != True:
                        current_cluster[cluster_idx] = ('exp', 'exp', 'yellow', 'solid')
                        self.__SendEmailNotification('Check Mirror')
                        dbg.printDBG1 (file_name, "Cluster%s %s -- Mirror NOT All Good" % (cluster_idx, current_cluster[cluster_idx]))
                    elif self.__ClusterAllGood(cluster_idx) != True:
                        current_cluster[cluster_idx] = ('exp','chk','yellow','solid')
#                        self.__SendEmailNotification('Check Engine')       # don't report immediately, it maybe just temp ethernet problem
                        dbg.printDBG1 (file_name, "Cluster%s %s -- Cluster NOT All Good" % (cluster_idx, current_cluster[cluster_idx]))
                    elif self.__PortAllGood(cluster_idx) != True:
                        current_cluster[cluster_idx] = ('exp','exp','yellow','solid')
                        self.__SendEmailNotification('Check Engine Port')                        
                        dbg.printDBG1 (file_name, "Cluster%s %s -- BPT NOT Clear" % (cluster_idx, current_cluster[cluster_idx]))
                    else:
                        current_cluster[cluster_idx] = ('exp','on','green','solid')
                        dbg.printDBG1 (file_name, "Cluster%s %s -- Cluster and Mirror All Good" % (cluster_idx, current_cluster[cluster_idx]))
#
# Cluster exp2on                     
                elif current_cluster[cluster_idx][0:2] == ('exp','on'):
                    if (self.__ClusterAllGood(cluster_idx) == True) & (self.__MirrorAllGood(cluster_idx) == True) & \
                       (self.__PortAllGood(cluster_idx) == True):
                        current_cluster[cluster_idx] = ('on','on','green','solid')
                    else: 
                        current_cluster[cluster_idx] = ('on','exp','yellow','blinking')
#
# Cluster exp2chk
                elif current_cluster[cluster_idx][0:2] == ('exp','chk'):
                    if self.__MirrorFailed(cluster_idx) == True:
                        current_cluster[cluster_idx] = ('exp', 'off', 'red', 'solid')
                        dbg.printDBG1 (file_name, "Cluster%s %s -- Mirror failed" % (cluster_idx, current_cluster[cluster_idx]))
                    elif self.__ClusterAllDown(cluster_idx) == True:
                        current_cluster[cluster_idx] = ('exp','off','red','solid')
                        self.__SendEmailNotification('Cluster Failed')  # don't report immediately, it maybe just temp ethernet problem
                        dbg.printDBG1 (file_name, "Cluster%s %s -- CG engine all down" % (cluster_idx, current_cluster[cluster_idx]))
                    elif self.__ClusterAllGood(cluster_idx) != True:
                        current_cluster[cluster_idx] = ('exp','exp','yellow','solid')
                        self.__SendEmailNotification('Check Engine')    # don't report immediately, it maybe just temp ethernet problem
                        dbg.printDBG1 (file_name, "Cluster%s %s -- CG engine down" % (cluster_idx, current_cluster[cluster_idx]))
                    elif (self.__ClusterAllGood(cluster_idx) == True) & (self.__MirrorAllGood(cluster_idx) == True) & \
                         (self.__PortAllGood(cluster_idx) == True):
                        current_cluster[cluster_idx] = ('exp','on','green','solid')
                        dbg.printDBG1 (file_name, "Cluster%s %s -- CG engine, mirror, and port all good" % (cluster_idx, current_cluster[cluster_idx]))
                    else:
                        current_cluster[cluster_idx] = ('exp','exp','yellow','solid')                        
#
# Cluster exp2exp
                elif current_cluster[cluster_idx][0:2] == ('exp','exp'):
                    if self.__MirrorFailed(cluster_idx) == True:
                        current_cluster[cluster_idx] = ('exp', 'off', 'red', 'solid')
                        dbg.printDBG1 (file_name, "Cluster%s %s -- Mirror failed" % (cluster_idx, current_cluster[cluster_idx]))
                    elif self.__ClusterAllDown(cluster_idx) == True:
                        current_cluster[cluster_idx] = ('exp','off','red','solid')
                        dbg.printDBG1 (file_name, "Cluster%s %s -- CG engine all down" % (cluster_idx, current_cluster[cluster_idx]))
                    elif (self.__ClusterAllGood(cluster_idx) == True) & (self.__MirrorAllGood(cluster_idx) == True) & \
                         (self.__PortAllGood(cluster_idx) == True):
                        current_cluster[cluster_idx] = ('exp','on','green','solid')
                        dbg.printDBG1 (file_name, "Cluster%s %s -- CG engine, mirror, and port all good" % (cluster_idx, current_cluster[cluster_idx]))
                    else:
                        current_cluster[cluster_idx] = ('exp','exp','yellow','solid')                        
#
# Cluster exp2off                     
                elif current_cluster[cluster_idx][0:2] == ('exp','off'):
                    if (self.__ClusterAllDown(cluster_idx) != True) & (self.__MirrorFailed(cluster_idx) != True):
                        current_cluster[cluster_idx] = ('off','exp','yellow','solid')
                    else:
                        current_cluster[cluster_idx] = ('off','off','red','solid')                        
#
# Cluster off2exp
                elif current_cluster[cluster_idx][0:2] == ('off','exp'):
                    if (self.__ClusterAllDown(cluster_idx) != True) & (self.__MirrorFailed(cluster_idx) != True):
                        current_cluster[cluster_idx] = ('exp','exp','yellow','blinking')
                        dbg.printDBG1 (file_name, "Cluster%s %s -- No Mirror Fail" % (cluster_idx, current_cluster[cluster_idx]))
                    else:
                        current_cluster[cluster_idx] = ('exp','off','red','solid')                        
#
# Cluster off2off                  
                elif current_cluster[cluster_idx][0:2] == ('off','off'):
                    if (self.__ClusterAllDown(cluster_idx) != True) & (self.__MirrorFailed(cluster_idx) != True):
                        current_cluster[cluster_idx] = ('off','exp','yellow','blinking')
                        dbg.printDBG1 (file_name, "Cluster%s %s -- No Mirror Fail" % (cluster_idx, current_cluster[cluster_idx]))
                    else:
                        current_cluster[cluster_idx] = ('off','off','red','solid')
#
# Cluster exception
                else:
                    dbg.printDBG1 (file_name, "Cluster%s %s -- Exception" % (cluster_idx, current_cluster[cluster_idx]))
                    print current_cluster[cluster_idx]
                    
#
#
    def __ClusterAllGood(self, i):
        for engine in cluster_group[i]:
            if current_engine[int(engine)][0:2] == ('on', 'on'): continue
            return False
        return True
#
#
    def __ClusterAllDown(self, i):
        for engine in cluster_group[i]:
            if current_engine[int(engine)][0:2] != ('on', 'on'): continue
            return False
        return True
#
#
    def __MirrorAllGood(self, i):
        for engine in cluster_group[i]:
            for mlun in engine_info[int(engine)]['Mirror'].keys():
                if ((engine_info[int(engine)]['Mirror'][mlun][4] in ("OK", "-")) & \
                    (engine_info[int(engine)]['Mirror'][mlun][6] in ("OK", "-")) & \
                    (engine_info[int(engine)]['Mirror'][mlun][8] in ("OK", "-")) & \
                    (engine_info[int(engine)]['Mirror'][mlun][10] in ("OK", "-"))): continue
                else:
                    return False
        return True
#
#
    def __MirrorFailed(self, i):
        for engine in cluster_group[i]:
            for mlun in engine_info[int(engine)]['Mirror'].keys():
                if (engine_info[int(engine)]['Mirror'][mlun][4] != "OK") & (engine_info[int(engine)]['Mirror'][mlun][6] != "OK"):
                    return True
        return False
#
#
    def __PortAllGood(self, i):
        for engine in cluster_group[i]:
            for pid in engine_info[int(engine)]['BPT'].keys():
                if (engine_info[int(engine)]['BPT'][pid][1] == "No Entries"):
                    continue
                else:
                    if DEVELOPMENT == 1: continue
#                    print engine_info[int(engine)]['BPT'][pid][1], "....Check Bad Port Table (\"bpt\")"
                    #
                    # Port A1 (0) link is down
                    # Port A2 (1) link is down
                    # Port B1 (2) link is down
                    # Port B2 (3) link is down
                    #
                    #    Bad Port Table protection mode is set to protect:
                    #       The last operational member of each mirror
                    #
                    return False
        return True
#
#
#    def __PortFailed(self, i):
#        for engine in cluster_group[i]:
#            for pid in engine_info[int(engine)]['BPT'].keys():
#                if (engine_info[int(engine)]['BPT'][pid][1] != "No Entries"):
#                    return True
#        return False
#
#
    def __SendEmailNotification(self, status = 'Unknow'):
        dbg.printDBG1 (file_name, "Send Email Notification, status = %s" % status)
        
        if cfg['General']['EMAIL_NOTIFICATION'][1:-1] == "ENABLED":
            p = DisplayMenubar.DisplayMenubar()
            p.GetEmailInfo()
            t = ControlEmail.xEmail()
            t.auto_send_message(email_info, status)
#
"""
5 secodes timer loop:
############################################################################################################
for engine in range(0, engine_number): 
    off2off:
        ping every 5 seconds (if Diag Mode: check if the engine log file in Diag directory)
        current_engine = ('off','on')
    
    off2on:
        get engine log file (if Diag Mode: use the engine log file in Diag directory)
        turn on LED
        current_engine = ('on','on')
        update_count = 12

    on2on:
        ping every 5 seconds (if Diag Mode: check if the engine log file in Diag directory)
            if can not ping: current_engine = ('on', 'off')
            
            else if (update_count -= 1) == 0: #wait for 60 seconds
                update_count = 12
                update engine log file (if Diag Mode: use the engine log file in Diag directory)

    on2off:
        turn off LED
        state = ('off', 'off')

############################################################################################################
for cluster in range(0, engine_number/2): 
    off2off:
    check member every 5 seconds
        if any engine in cluster is 'on' and if all mirror is not (failed), current_cluster = ('off', 'exp')
#
    off2exp:
        LED = "yellow"
        check member is "on" every 5 seconds
            if any engine in cluster is 'off', current_cluster = ('on', 'exp')
        
        check mirror is (ok, ok) every 60 seconds
            if any mirror is not (ok, ok), current_cluster = ('on', 'exp')
#
    exp2on:
        LED = "green"
        get engine log file (if Diag Mode: use the engine log file in Diag directory)
        turn on LED
        current_engine = ('on','on')
        update_count = 12
#
    on2on:
        check member is "on" every 5 seconds
            if any engine in cluster is 'off', current_cluster = ('on', 'exp')
            
        check mirror is (ok, ok) every 60 seconds
            if any mirror is not (ok, ok), current_cluster = ('on', 'exp')
#
    on2exp:
        LED = "yellow"
        send email notification
        check member every 5 seconds
            if any engine in cluster is 'off', current_cluster = ('exp', 'exp')
            else if any mirror is not (ok, ok), current_cluster = ('exp', 'exp')
            else current_cluster = ('exp', 'on')
#
    exp2exp:
        check member every 5 seconds
            if any engine in cluster is all 'off', current_cluster = ('exp', 'off')            
            else if any mirror is (failed), current_cluster = ('exp', 'off')
            
            else if cluster is all "on", and mirror is all "good", current_cluster = ('exp', 'on')
#
    exp2on:
        LED = "green"
        check member every 5 seconds
            if cluster is all "on", and mirror is all "good", current_cluster = ('on', 'on')
#
    exp2off:
        LED = "red"
        check member every 5 seconds
            if any engine in cluster is 'on' and if all mirror is not (failed), current_cluster = ('off', 'exp')
            else current_cluster = ('off', 'off')
#
# create SQL database (no longer use SQL) ---------------------------------------------------------------------
#
#        sql_ptr = ControlSQL.xmCT()
#        for i in range(0, engine_number):
#            sql_ptr.createCT(table_name = "VPDengine%s" % i,
#                sql_column = ",Uptime,SerialNumber,Firmware,Alert,UniqueID,EngineTime,IPaddress,Revision")
#
"""
