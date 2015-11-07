import sys
import xbmc, xbmcgui, xbmcaddon
import logging
import urllib
import json
import random
import os
import threading
from datetime import datetime

# code header
__author__       = "jyc"
__scriptid__     = "script.comments.update"
__addon__        = xbmcaddon.Addon(id=__scriptid__)
__addonid__      = __addon__.getAddonInfo('id')
__addonversion__ = __addon__.getAddonInfo('version')
__cwd__          = __addon__.getAddonInfo('path')
__language__     = __addon__.getLocalizedString

# skin parameters, details can be found on skin package
CANCEL_DIALOG  = ( 9, 10, 92, 216, 247, 257, 275, 61467, 61448, )

# global parameters

#timer class
class TimerClass(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.event = threading.Event()
	        
    def run(self):
        while not self.event.is_set():
	    # periodically refresh news content container, as defined in script-qrcode-container.xml under skin folder
	    if xbmc.Player().isPlayingVideo():
			file_length = xbmc.Player().getTotalTime() - xbmc.Player().getTime()
			
			# refresh comments for the new video
			xbmc.executebuiltin('SendClick(4300,9930)')
			
			# set timer period
			self.event.wait( int(file_length) + 1)

    def stop(self):
        self.event.set()


if ( __name__ == "__main__" ):
    # get login information from the command line arguments.
    
    # load qrcode container
    xbmc.executebuiltin('RunScript(script.comments.container)')

    # start timer
    tmr = TimerClass()		
    tmr.start()

    
