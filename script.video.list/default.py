import sys
import xbmc, xbmcgui, xbmcaddon
import logging
import urllib
import json
import threading
import string
import os

__author__       = "jyc"
__scriptid__     = "script.text.chat"
__addon__        = xbmcaddon.Addon(id=__scriptid__)
__addonid__      = __addon__.getAddonInfo('id')
__addonversion__ = __addon__.getAddonInfo('version')
__cwd__          = __addon__.getAddonInfo('path')
__language__     = __addon__.getLocalizedString

CANCEL_DIALOG  = ( 9, 10, 92, 216, 247, 257, 275, 61467, 61448, )

portalURL = '155.69.146.83'
port = 80
isChatActive = xbmc.translatePath("special://home/") + 'isChat'
chatContent = xbmc.translatePath("special://home/") + 'chatContent'

STATUS_LABEL   = 4100
USER_ICON      = 4110
CHAT_CONTENT   = 4120
FRIEND_LIST    = 4220

#text chat GUI
class TextChatGUI( xbmcgui.WindowXMLDialog ):
    def __init__( self, *args, **kwargs):      
	self.chatuser = kwargs.get( "chatuser" )
	self.itemCount = 0
        pass
	
    def onInit( self ):  
	listitem = xbmcgui.ListItem(label = self.chatuser, iconImage = 'http://' + portalURL + ':' + str(port) + '/static/new_ui/picture/' + self.chatuser + '.jpg') 
	self.getControl( FRIEND_LIST ).addItem(listitem)
	self.itemCount = self.itemCount + 1
	self.setFocus( self.getControl( FRIEND_LIST ) )
        self.getControl( FRIEND_LIST ).selectItem( 0 )


    def onClick( self, controlId ):
	if controlId == 9911:
	    tmpFile = open(isChatActive)
	    self.chatuser = tmpFile.readline()
	    tmpFile.close()
	    self.setFocus( self.getControl( FRIEND_LIST ) )
	    if not (cmp(self.chatuser, self.getControl(FRIEND_LIST).getSelectedItem().getLabel()) == 0):
	        itemPosition = -1
	        for i in range(0, self.itemCount):
	            if cmp(self.getControl(FRIEND_LIST).getListItem(i).getLabel(), self.chatuser) == 0:
	                itemPosition = i
		        break
	        #xbmc.executebuiltin('Notification(%s, %s)'%(self.chatuser, ""))  
	        if itemPosition == -1:
		    listitem = xbmcgui.ListItem(label = self.chatuser, iconImage = 'http://' + portalURL + ':' + str(port) + '/static/new_ui/picture/' + self.chatuser + '.jpg') 
	            self.getControl( FRIEND_LIST ).addItem(listitem)	        
		    self.setFocus( self.getControl( FRIEND_LIST ) )
		    self.getControl( FRIEND_LIST ).selectItem( self.itemCount )
		    self.itemCount = self.itemCount + 1
	        else:
		    self.getControl( FRIEND_LIST ).selectItem(itemPosition)
	elif controlId == 9912:
	    if os.path.exists(isChatActive):
		os.remove(isChatActive)
	    self.close()


    def onFocus( self, controlId ):
	self.setFocus( self.getControl( FRIEND_LIST ) )
	self.content = ""
	self.focusedUser = self.getControl(FRIEND_LIST).getSelectedItem().getLabel()
	tmpFile = open(chatContent)
	data = tmpFile.readline()
	while data:
	    lineMsg = json.loads(data)
	    if cmp(lineMsg['user'], self.focusedUser) == 0:
		#self.content = lineMsg['user'] + " (" + lineMsg['time'] + ")\n" + lineMsg['content'] + "\n" + self.content 
		self.content = lineMsg['from'] + ":\n" + lineMsg['content'] + "\n" + self.content 
	    data = tmpFile.readline()
	self.getControl( CHAT_CONTENT ).setLabel(self.content)
	tmpFile.close()
	

    def onAction( self, action ):
        if ( action.getId() in CANCEL_DIALOG):
	    if os.path.exists(isChatActive):
		os.remove(isChatActive)
            self.close()       


if ( __name__ == "__main__" ):
    chatUI = TextChatGUI( "script-textchat-box.xml" , "special://home/addons/skin.ace", chatuser=sys.argv[1])
    chatUI.doModal()
    del chatUI

    
    
