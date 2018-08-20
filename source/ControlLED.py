#!/usr/bin/python
"""
Control LED Module

Created by Susan Cheng on 2014-07-11.
Copyright (c) 2014-2016 __Loxoll__. All rights reserved.
"""
#

from Tkinter import *
from ttk import *
import time, datetime, os
file_name = os.path.basename(__file__)

class Color():
    THEME	= 'default'			# ('aqua', 'clam', 'alt', 'default', 'classic')
    PANEL	= '#545454'
    OFF		= '#656565'
    ON		= '#00FF33'
    WARN	= '#ffcc00'
    ALARM	= '#ff4422'

class LED():
    INIT  = 'off'					# INIT = OFF
    OFF   = 'off'
    ON    = 'on'
    WARN  = 'warn'
    ALARM = 'alarm'
    LED_NO = 3

class LEDset(object):

    def __init__(self, master, status=LED.OFF, blink=LED.OFF):
        dbg.printDBG2(file_name, "initiate LEDset, status=%s, blink=%s" % (status, blink))

        width=20
        hight=20
        appearance=FLAT
        bd=1
        bg=None
        outline=""
        blinkrate=1
        takefocus=0

        # preserve attributes
        self.master       = master
        self.onColor      = Color.ON
        self.offColor     = Color.OFF
        self.alarmColor   = Color.ALARM
        self.warningColor = Color.WARN
        self.status       = status
        self.blink        = blink
        self.blinkrate    = int(blinkrate)
        self.on           = LED.OFF
        self.saveStatus   = LED.OFF

        bg = Color.PANEL

        # Base frame to contain light
        style = Style()
        style.theme_use(Color.THEME)
        style.configure("LED.TFrame", padding=3, relief="sunken")        
        self.frame=Frame(master, relief=appearance, takefocus=takefocus, style='LED.TFrame')

        basesize = width
        d = center = int(basesize/2)

        r = int((basesize-2)/2)
        self.canvas=Canvas(self.frame, width=width, height=width,
                highlightthickness=0, bg=bg, bd=0)
        if bd > 0:
            self.border=self.canvas.create_oval(center-r, center-r,
                center+r, center+r)
            r = r - bd
        
        self.light=self.canvas.create_oval(center-r-1, center-r-1, 
                               center+r, center+r, fill=Color.ON,
                               outline=outline)

        self.canvas.grid()                  # display the LED
        self.update()                       # make the change
    
    def changeLED(self, status, blink):
#        dbg.printDBG3(file_name, "changeLED, status = %s, blink = %s" % (status, blink))
        self.status  = status
        if self.blink == LED.ON:    # already blinking
            if blink == LED.ON:     # blinking more
                self.saveStatus = self.status   # update color
                self.update()       # take this line out if the blink control timer is in "update()"
            else:                   # no blinking
                self.blink = blink
                self.update()
        else:
            if blink == LED.ON:     # start blinking
                self.saveStatus = self.status   # update color
                self.blink = blink
                self.update()                
            else:                   # no blinking
                self.blink = blink
                self.update()
    #
    def ChangeEngineLED(self, engine_idx):
#        dbg.printDBG3(file_name, "ChangeEngineLED, engine current status = " + str(current_engine[engine_idx]))
        
        if current_engine[engine_idx][2] == "green": status = LED.ON
        elif current_engine[engine_idx][2] == "yellow": status = LED.WARN
        elif current_engine[engine_idx][2] == "red": status = LED.ALARM
        elif current_engine[engine_idx][2] == "dark": status = LED.OFF       
        else:
            dbg.printDBG3(file_name, "Failed changeLED, engine current status = " + str(current_engine[engine_idx]))
            return False
        if current_engine[engine_idx][3] == "solid": blink = LED.OFF
        elif current_engine[engine_idx][3] == "blinking": blink = LED.ON
        else:
            dbg.printDBG3(file_name, "Failed changeLED, engine current status = " + str(current_engine[engine_idx]))
            return False
        
#        print engine_idx, status, blink, self.blink
        self.changeLED( status, blink)

#
    def ChangeClusterLED(self, idx):
        if current_cluster[idx][2] == "green": status = LED.ON
        elif current_cluster[idx][2] == "yellow": status = LED.WARN
        elif current_cluster[idx][2] == "red": status = LED.ALARM
        elif current_cluster[idx][2] == "dark": status = LED.OFF       
        else:
            dbg.printDBG3(file_name, "Failed changeLED, cluster current status = " + str(current_cluster[idx]))
            return False
        if current_cluster[idx][3] == "solid": blink = LED.OFF
        elif current_cluster[idx][3] == "blinking": blink = LED.ON
        else:
            dbg.printDBG3(file_name, "Failed changeLED, cluster current status = " + str(current_cluster[idx]))
            return False
        
#        print idx, status, blink, self.blink
        self.changeLED( status, blink)
                    


                    
    def update(self):
#        dbg.printDBG4(file_name, "update, status = %s, blink = %s" % (self.status, self.blink))        
        # First do the blink, if set to blink

        if self.blink == LED.ON:
#            dbg.printDBG4(file_name, "blink is on, status = %s" % self.status)        
            if self.on == LED.ON:   # time to turn off the LED
#                dbg.printDBG4(file_name, "LED is on, status = %s" % self.status)        
                self.status  = LED.OFF
                self.on      = LED.OFF                            
            else:                   # time to turn on the LED
#                dbg.printDBG4(file_name, "LED is off, status = %s" % self.status)        
                self.status = self.saveStatus    # Current ON color
                self.on = LED.ON

        if self.status == LED.ON:
            if program_stop == False: self.canvas.itemconfig(self.light, fill=self.onColor)
        elif self.status == LED.OFF:
            if program_stop == False: self.canvas.itemconfig(self.light, fill=self.offColor)
        elif self.status == LED.WARN:
            if program_stop == False: self.canvas.itemconfig(self.light, fill=self.warningColor)
        elif self.status == LED.ALARM:    
            if program_stop == False: self.canvas.itemconfig(self.light, fill=self.alarmColor)
        else:
            raw_input("AH9")

        if program_stop == False: self.canvas.update_idletasks()

#        if self.blink == LED.ON:
#            dbg.printDBG4(file_name, "prepare for next blink, status = %s, blink = %s" % (self.status, self.blink))
#            if not program_stop: self.frame.after(self.blinkrate * 100, self.update)

