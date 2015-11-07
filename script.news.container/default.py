import sys
import xbmc, xbmcgui, xbmcaddon
import logging
import urllib
import json
import random
import os

# code header
__author__       = "jyc"
__scriptid__     = "script.news.container"
__addon__        = xbmcaddon.Addon(id=__scriptid__)
__addonid__      = __addon__.getAddonInfo('id')
__addonversion__ = __addon__.getAddonInfo('version')
__cwd__          = __addon__.getAddonInfo('path')
__language__     = __addon__.getLocalizedString

# skin parameters, details can be found on skin package
CANCEL_DIALOG  = ( 9, 10, 92, 216, 247, 257, 275, 61467, 61448, )
NEWS_LABEL = 4121
global serverIP
# news_URL = "http://155.69.146.82:9999/get_news/"

# global parameters

def readnews():
    global serverIP    
    news_content = urllib.urlopen(serverIP+'/get_news/').read()
    news_list = json.loads(news_content).get('data')
    news_content = ""
    news_index = 1
    for news in news_list:
        news_content += str(news_index) + ". " + news.get('content') + " (" + news.get('time') + ")    "
        news_index += 1
    return news_content

# qrcode container GUI
class NewsContainerGUI( xbmcgui.WindowXMLDialog ):
    def __init__( self, *args, **kwargs):       
	pass
	
    def onInit( self ):        
        self.getControl( NEWS_LABEL ).setLabel(readnews())

    def onClick( self, controlId ):
	if controlId == 9921:
	    # update news here
            self.getControl( NEWS_LABEL ).setLabel(readnews())
	             
    def onFocus( self, controlId ):
        self.controlId = controlId

    def onAction( self, action ):
        if ( action.getId() in CANCEL_DIALOG):
	    self.close()       
		
if ( __name__ == "__main__" ):
    global serverIP
    serverIP = sys.argv[1] 

    # load qrcode container
    ui = NewsContainerGUI("script-news-container.xml" , "special://home/addons/skin.maximinimalism", "Default")
    ui.doModal()
    del ui


    
