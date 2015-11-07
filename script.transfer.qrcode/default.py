import sys
import xbmc, xbmcgui, xbmcaddon
import logging
import urllib
import json
import random
import os

# code header
__author__       = "jyc"
__scriptid__     = "script.session.transfer"
__addon__        = xbmcaddon.Addon(id=__scriptid__)
__addonid__      = __addon__.getAddonInfo('id')
__addonversion__ = __addon__.getAddonInfo('version')
__cwd__          = __addon__.getAddonInfo('path')
__language__     = __addon__.getLocalizedString

# skin parameters, details can be found on skin package
CANCEL_DIALOG  = ( 9, 10, 92, 216, 247, 257, 275, 61467, 61448, )

# global parameters
portalURL = '155.69.146.83'
QR_CODE = 4310

#text chat GUI
class QRContainerGUI( xbmcgui.WindowXMLDialog ):
    def __init__( self, *args, **kwargs):       
	pass
	
    def onInit( self ):  
	tmpFile = open(fullJID)
	jid = tmpFile.readline()
	urllib.urlretrieve('http://' + portalURL + ':' + str(port) + '/stv/session_key/?id='+ jid + '&rand='+str(random.random()), filePath)	
	self.getControl( QR_CODE ).setImage(filePath)	

    def onClick( self, controlId ):
        self.close()

    def onFocus( self, controlId ):
        self.controlId = controlId

    def onAction( self, action ):
        if ( action.getId() in CANCEL_DIALOG):
	    self.close()       
		
if ( __name__ == "__main__" ):
    # get login information from the command line arguments.
    xmppURL = sys.argv[1] 
    demoID = sys.argv[2]
    demoPwd = sys.argv[3] 
    
    # login to get cookies    
    r = requests.post(str(xmppURL)+'/users/login/',data=dict(LoginID=demoID, Password=demoPwd))
    cookies = r.cookies

    # Read User Name
    ui = QRContainerGUI("script-qrcode-container.xml" , "special://home/addons/skin.ace", "Default")
    ui.doModal()
    del ui
    
