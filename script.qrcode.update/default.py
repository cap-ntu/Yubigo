import sys
import xbmc, xbmcgui, xbmcaddon
import logging
import urllib
import json
import random
import os
import requests
import threading

# code header
__author__       = "jyc"
__scriptid__     = "script.qrcode.update"
__addon__        = xbmcaddon.Addon(id=__scriptid__)
__addonid__      = __addon__.getAddonInfo('id')
__addonversion__ = __addon__.getAddonInfo('version')
__cwd__          = __addon__.getAddonInfo('path')
__language__     = __addon__.getLocalizedString

# skin parameters, details can be found on skin package
CANCEL_DIALOG  = ( 9, 10, 92, 216, 247, 257, 275, 61467, 61448, )

# global parameters
global userID
global userPwd
global serverIP
global isRefreshed
global xmppResource
isRefreshed = True
qrcodePath1 = xbmc.translatePath("special://home/") + 'qrcode1.png'
qrcodePath2 = xbmc.translatePath("special://home/") + 'qrcode2.png'

#timer class
class TimerClass(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.event = threading.Event()
	        
    def run(self):
        while not self.event.is_set():
	    # get new qr code
	    global serverIP
            global userID
            global userPwd
            global xmppResource
            r = requests.post(str(serverIP)+'/users/login/',data=dict(LoginID=userID, Password=userPwd))
            cookies = r.cookies
	    r = requests.get(serverIP+'/users/session_key/?format=png&resource='+xmppResource, cookies=cookies)
            
	
	    # use two images to update qrcode in XBMC
	    global isRefreshed	    
	    if isRefreshed:
		qrcodeContainerComm = 9933
		isRefreshed = False
		qrcodePath = qrcodePath1
	    else:
		qrcodeContainerComm = 9934
		isRefreshed = True
		qrcodePath = qrcodePath2

	    # write obtained qrcode to local file
    	    if os.path.exists(qrcodePath):
		os.remove(qrcodePath)
    	    with open(qrcodePath, 'wb') as fd:
        	for chunk in r.iter_content(4096):
	    	   fd.write(chunk)

	    # refresh qr code container, as defined in script-qrcode-container.xml under skin folder
	    xbmc.executebuiltin('SendClick(4400,'+str(qrcodeContainerComm)+')')

	    # set timer period as 10 mins
	    self.event.wait( 600 )

    def stop(self):
        self.event.set()
    
		
if ( __name__ == "__main__" ):
    # get login information from the command line arguments.
    global serverIP
    global userID
    global userPwd
    global xmppResource
    serverIP = sys.argv[1] 
    userID = sys.argv[2]
    userPwd = sys.argv[3] 
    xmppResource = sys.argv[4]

    # load qrcode container
    xbmc.executebuiltin('RunScript(script.qrcode.container)')

    # start timer
    tmr = TimerClass()		
    tmr.start()


    
