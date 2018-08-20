#!/usr/bin/python
"""
Loxoll GUI rev 2.0
Copyright (c) 2014-2017, Loxoll Inc. All rights reserved.
"""
#
# Define Global Variables Here
#
import sys, os
import datetime
import pdb
#pdb.set_trace()
sys.path.append("./source")

import __builtin__
__builtin__.STOP    = 0
__builtin__.GO      = 1

__builtin__.ON      = 1
__builtin__.OFF     = 0

__builtin__.YES     = 0
__builtin__.NO      = 1

__builtin__.GOOD    = 0
__builtin__.TIMEOUT = 1
__builtin__.FAILED  = 1

__builtin__.JUST_START  = 3
__builtin__.STARTED     = 2
__builtin__.CONTINUE    = 1
__builtin__.STOPPED     = 0

__builtin__.ONE_SECOND  = 1
__builtin__.TWO_SECOND  = 2
__builtin__.FIVE_SECOND = 5

__builtin__.DEVELOPMENT = 1
__builtin__.SIMMOD = 1
__builtin__.MONITOR = 0
__builtin__.CHINESE = 0
__builtin__.BG_TIMER = 2
__builtin__.CLI_CUT = 1

from ParseINIfile import ParseINIfile
__builtin__.cfg = ParseINIfile('Config.ini')

__builtin__.debug_level = int(cfg['General']['DEBUG_LEVEL'])

__builtin__.engine_number = int(cfg['General']['HAAP_NO'])*2
__builtin__.reverse_sort = {}
__builtin__.sort_key = {}
__builtin__.smtp_ssl = cfg['General']['SMTP_SSL'][1:-1]

monitor_page = ('mv', 'rv', 'sv', 'ev', 'hv')
for p in monitor_page:
    reverse_sort[p] = 0    # first click will be "reverse" 
    sort_key[p] = 0        # first will be sort by "id"


print 'debug_level =', debug_level, ';',
print 'Simulation =', SIMMOD, ';',
print 'Development =', DEVELOPMENT, ';',
print 'monitor_only =', MONITOR, ';'

from ControlDiag import xDBG
__builtin__.dbg = xDBG()

file_name = os.path.basename(__file__)
print "Program start"
dbg.printDBG0(file_name, 'Start Program!!!!')

__builtin__.program_stop = False
__builtin__.telnet_avaiable = True

import Tkinter
from DisplayDashboard import DisplayDashboard

try:
    if not cfg['General']['HAAP_NO']: pass
except:
    dbg.printDBG0(file_name, "Fault Exit -- HA-AP not defined")
    print "-- STOP -- HA-AP not defined"
    sys.exit()
if engine_number == 0:
    dbg.printDBG0(file_name, "Fault Exit -- zero HA-AP defined")
    print "-- STOP -- zero HA-AP defined"
    sys.exit()
if engine_number > 40:
    dbg.printDBG0(file_name, "Fault Exit -- too many HA-AP defined")
    print "-- STOP -- Too many HA-AP defined"
    sys.exit()
try:
#    pdb.set_trace()
    for i in range(engine_number):
        if not cfg['Engine'+str(i)]['IP']: pass
except:
    dbg.printDBG0(file_name, "Fault Exit -- IP does not set correctly")
    print "-- STOP -- IP does not set correctly"
    sys.exit()

try:
    __builtin__.single_engine = "No"
    if cfg['General']['SINGLE_MODE'][1:-1] == "Yes": __builtin__.single_engine = "Yes"
except:
    pass

if single_engine is "Yes":
    if cfg['General']['HAAP_NO'] != "1":
        dbg.printDBG0(file_name, "Fault Exit -- Single Engine mode, HAAP # is not 1")
        print "-- STOP -- Single Engine mode, HAAP # must be 1"
        sys.exit()
    
    if cfg['CG0']['MEMBER'][1:-1] not in ("0", "1"):
        dbg.printDBG0(file_name, "Fault Exit -- Single Engine mode, Cluster Group # is not right")
        print "-- STOP -- Single Engine mode, Cluster Group # is not right"
        sys.exit()

__builtin__.current_engine = [0 for x in range(engine_number)]   # engine current state
__builtin__.current_cluster = [0 for x in range(engine_number/2)]   # engine current state
__builtin__.cluster_group = [0 for x in range(engine_number/2)]   # engine current state

import ControlLED
__builtin__.led_ptr = [[0 for x in range(ControlLED.LED.LED_NO)] for x in range(engine_number/2)]

import ParseEngineVPD
__builtin__.engine_info = [0 for x in range(engine_number)] # all engine's information
__builtin__.name_info = [0 for x in range(engine_number)]   # HBA, LUN, and Group names' database

for i in range (engine_number):
    engine_info[i] = {}
    name_info[i] = {}
    p = ParseEngineVPD.ParseEngineVPD()
    p.initEngineInfo(i)

__builtin__.haapw_global_ptr = [0 for x in range(2)]
__builtin__.cfgw_global_ptr = [0 for x in range(2)]
__builtin__.diag_global_ptr = [0 for x in range(2)]
__builtin__.STATUS = 0
__builtin__.POINTER = 1
__builtin__.TAGS = 2

__builtin__.email_info = {}
__builtin__.TCP_info = {}
__builtin__.API_info = {}
__builtin__.LPS_info = {}
__builtin__.switch_info = {}
__builtin__.switch_err = {}
__builtin__.JSON_info = {}

root = Tkinter.Tk()
__builtin__.LLINE = 120
root.geometry("+%d+%d" % (LLINE,0))
root.wm_resizable(0,0)              # disable resizing

dbg.printDBG0(file_name, "start Dashboard")
gui_app= DisplayDashboard(root)
gui_app.lift()
#
# Starts the 5 sencond timer thread to get the HA-AP status and update LED
#
import threading
from DisplayDashboard import TimerThread

ROOT_TIME = 400
SEC4_TIME = 4000/ROOT_TIME
__builtin__.task_counter = SEC4_TIME

def task():
#
# update LED
    for engine_idx in range (0, engine_number):
        led_ptr[engine_idx/2][engine_idx%2].ChangeEngineLED(engine_idx)
    for cluster_idx in range (0, engine_number/2):
        led_ptr[cluster_idx][2].ChangeClusterLED(cluster_idx)
#
    def sec4_task():
        #sys.stdout.write('. ')
        #sys.stdout.flush()
        
        if haapw_global_ptr[STATUS] != STOPPED:
            dbg.printDBG1(file_name, "Refresh Monitor Window")
            haapw_global_ptr[POINTER].refreshDisplayHaapPanel()
        #
        if cfgw_global_ptr[STATUS] != STOPPED:
            dbg.printDBG1(file_name, "Refresh Configuration Window")
            cfgw_global_ptr[POINTER].refreshDisplayConfigPanel()
#
    global task_counter
    task_counter -= 1
    if task_counter == 0:
        sec4_task()
        task_counter = SEC4_TIME
#
    root.after(ROOT_TIME, task)  # reschedule event in .1 seconds


timer_stop = threading.Event()
thread_ptr = TimerThread(timer_stop)
dbg.printDBG0(file_name, "start %s second timer" % BG_TIMER)
thread_ptr.start()

import DisplayMenubar

p = DisplayMenubar.DisplayMenubar()
p.startDisplayMenubar(root)

try:
    root.after(100, task)      # This is to avoid pausing introducted by Tkinter functions (not sure why)
    dbg.printDBG0(file_name, "GUI mainloop enter")
    root.call('wm', 'attributes', '.', '-topmost', True)
    root.mainloop()

except:
    dbg.printDBG0(file_name, "mainloop exit")    

__builtin__.program_stop = True
timer_stop.set()

dbg.printDBG0(file_name, "Stopped %s second timer" % BG_TIMER)

print "Program exit"
dbg.printDBG0(file_name, "Program exit")
