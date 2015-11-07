import sys
import xbmc, xbmcgui, xbmcaddon
import logging
import urllib
import json
import random
import os
import requests
import threading
from datetime import datetime

# code header
__author__       = "jyc"
__scriptid__     = "script.auto.shutdown"
__addon__        = xbmcaddon.Addon(id=__scriptid__)
__addonid__      = __addon__.getAddonInfo('id')
__addonversion__ = __addon__.getAddonInfo('version')
__cwd__          = __addon__.getAddonInfo('path')
__language__     = __addon__.getLocalizedString

# skin parameters, details can be found on skin package
CANCEL_DIALOG  = ( 9, 10, 92, 216, 247, 257, 275, 61467, 61448, )

# global parameters
global shutdownTime

def hms_to_seconds(t):
    h, m, s = [int(i) for i in t.split(':')]
    result = 3600*h + 60*m + s
    if (result > 3600*24):
        result = result - 3600*24
    return result

#timer class
class TimerClass(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.event = threading.Event()
        self.first = True
	        
    def run(self):
        while not self.event.is_set():            
	    # periodically refresh news content containe
	    if self.first:
                self.first = False
                # get time from google
                r = requests.get('http://www.google.com')
                currentTime = r.headers.get('date')[-12:-4]
                currentTime = str(int(currentTime[:2])+8) + currentTime[2:]
                			
		# calculate sleep time till auto shutdown
                global shutdownTime
                sleepTime = hms_to_seconds(shutdownTime) - hms_to_seconds(currentTime)
                if sleepTime < 0:
                    sleepTime = 10

                # set timer period
		self.event.wait( sleepTime )
            else:
                xbmc.executebuiltin('Quit')

    def stop(self):
        self.event.set()


if ( __name__ == "__main__" ):
    # get login information from the command line arguments.
    
    global shutdownTime
    shutdownTime = sys.argv[1]

    # start timer
    tmr = TimerClass()		
    tmr.start()

    
