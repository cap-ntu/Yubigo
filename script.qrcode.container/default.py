import sys
import xbmc, xbmcgui, xbmcaddon
import logging
import urllib
import json
import random
import os

# code header
__author__       = "jyc"
__scriptid__     = "script.qrcode.container"
__addon__        = xbmcaddon.Addon(id=__scriptid__)
__addonid__      = __addon__.getAddonInfo('id')
__addonversion__ = __addon__.getAddonInfo('version')
__cwd__          = __addon__.getAddonInfo('path')
__language__     = __addon__.getLocalizedString

# skin parameters, details can be found on skin package
CANCEL_DIALOG  = ( 9, 10, 92, 216, 247, 257, 275, 61467, 61448, )
QR_CODE = 4310

# global parameters
qrcodePath1 = xbmc.translatePath("special://home/") + 'qrcode1.png'
qrcodePath2 = xbmc.translatePath("special://home/") + 'qrcode2.png'

# qrcode container GUI
class QRContainerGUI( xbmcgui.WindowXMLDialog ):
    def __init__( self, *args, **kwargs):       
	pass
	
    def onInit( self ):  
	pass

    def onClick( self, controlId ):
	if controlId == 9933:
	    self.getControl(QR_CODE).setImage(qrcodePath1)
	elif controlId == 9934:
	    self.getControl(QR_CODE).setImage(qrcodePath2)
	             
    def onFocus( self, controlId ):
        self.controlId = controlId

    def onAction( self, action ):
        if ( action.getId() in CANCEL_DIALOG):
	    self.close()       
		
if ( __name__ == "__main__" ):
    # load qrcode container
    ui = QRContainerGUI("script-qrcode-container.xml" , "special://home/addons/skin.maximinimalism", "Default")
    ui.doModal()
    del ui


    
