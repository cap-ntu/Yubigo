import sys
import xbmc, xbmcgui, xbmcaddon
import logging
import urllib
import json
import random
import os

# code header
__author__       = "jyc"
__scriptid__     = "script.comments.container"
__addon__        = xbmcaddon.Addon(id=__scriptid__)
__addonid__      = __addon__.getAddonInfo('id')
__addonversion__ = __addon__.getAddonInfo('version')
__cwd__          = __addon__.getAddonInfo('path')
__language__     = __addon__.getLocalizedString


# skin parameters, details can be found on skin package
CANCEL_DIALOG  = ( 9, 10, 92, 216, 247, 257, 275, 61467, 61448, )
COMMENTS_LABEL = 4031
comment_content_path = xbmc.translatePath("special://home/")
maxLength = 25

# refresh
def refreshComment():
    file_id = str(xbmc.Player().getPlayingFile()).split('/')
    file_id = file_id[len(file_id)-1]
    file_id = file_id[: file_id.find('.')]
    new_comments = ""   
    if os.path.exists(comment_content_path + file_id):
        with open(comment_content_path + file_id, 'r') as f:
            lines = f.readlines()
            for i in range(0, len(lines)):        
                eachline = lines[i]                
                if i%3 == 0:
                    new_comments += '[COLOR username]' + eachline + '[/COLOR]'
                elif i%3 == 1:
                    while len(eachline) > maxLength:
                        tempComment = eachline[:maxLength-1]
                        if eachline[maxLength-1] != " ":
                            tempComment += "- "
                        eachline = eachline[maxLength:]
                        new_comments += tempComment
                    new_comments += eachline
                else:
                    new_comments += eachline
    return new_comments


# news container GUI
class NewsContainerGUI( xbmcgui.WindowXMLDialog ):
    def __init__( self, *args, **kwargs):       
	pass
	
    def onInit( self ):         
        self.getControl( COMMENTS_LABEL ).setText(refreshComment() )

    def onClick( self, controlId ):
	self.getControl( COMMENTS_LABEL ).reset()
        if controlId == 9930: # update comments for different videos
            self.getControl( COMMENTS_LABEL ).setText(refreshComment() )
	             
    def onFocus( self, controlId ):
        self.controlId = controlId

    def onAction( self, action ):
        if ( action.getId() in CANCEL_DIALOG):
	    self.close()       
		
if ( __name__ == "__main__" ):
    # load news container
    ui = NewsContainerGUI("script-comments-container.xml" , "special://home/addons/skin.maximinimalism", "Default")
    ui.doModal()
    del ui


    
