# -*- coding: utf-8 -*-
import xbmcplugin, xbmcgui
import xbmc, xbmcaddon
import urllib
import json
import string
import requests
import sys
import threading

# global parameters
serverIP = 'http://155.69.146.44' #
xmppIP =  'http://155.69.146.44' # 
demoID = 'dmalstb@ntu.edu.sg' # 'wkwstb1@ntu.edu.sg' 
demoPwd =  '558ec6e03f95358bc9333d3fed51b3ba17474553' 
xmppResource = 'stbdemo999'
shutdowntime = '20:58:00'

# skin parameters, details can be found on skin 
STATUS_LABEL   = 4100
USER_ICON      = 4110
CHAT_CONTENT   = 4120
FRIEND_LIST    = 4220


if ( __name__ == "__main__" ):
    # login system with demo account, and get cookies
    r = requests.post(str(serverIP)+'/users/login/',data=dict(LoginID=demoID, Password=demoPwd))
    cookies = r.cookies

    # get content list
    contentList = requests.post(str(serverIP)+'/content/list/',cookies=cookies,data=json.dumps({"type":"playlist","range":{"startIndex":0,"maxCount":20}}))
    return_type = contentList.json()['type']
    if cmp(return_type,'error') == 0:
        xbmcgui.Dialog().ok(" Error", " There is something wrong with your account ")
    else:
        contentList = contentList.json()['result']

        # clear and create playlist
        playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
        playlist.clear()

        # setup content to UI
        for video in contentList:
            video_title = video.get('title') 
            video_uuid = video.get('uuid')
            thumbnail_url = video.get('thumbnail')
            description = ' ' # 'Catagory: ' + str(video.get('category').get('name')) + '  Length: ' + str(video.get('length')) + 's Score: ' + str(video.get('score'))

            #video_url = requests.post(str(serverIP)+'/content/list/',cookies=cookies,data=json.dumps({"type":"request","request":"video-info","uuid":str(video_uuid)}))
            #video_url = video_url.json()['result']['url']
            video_url = video.get('url')
            video_url = video_url.replace('raw_video','content/files')    
            #open("d://abc.txt",'a').write(video_url+'\n')

            listitem=xbmcgui.ListItem(label=video_title, iconImage=thumbnail_url, thumbnailImage=thumbnail_url)
            listitem.setInfo('video', { 'plot': description })

            playlist.add(url=video_url, listitem=listitem)
        # end of 'for'

        # loop the content on the list
        #player = XBMCPlayer()
        xbmc.Player().play(playlist)
        xbmc.executebuiltin("PlayerControl(RepeatAll)")

        # adjust player location and size
        #command='{"jsonrpc": "2.0", "method": "Player.GetActivePlayers", "params": {}, "id": 1}'
        #result = xbmc.executeJSONRPC( command )

        # login xmpp service
        xbmc.executebuiltin('RunScript(script.xmpp.client, ' + serverIP + ', ' + xmppIP + ', '+ demoID + ', ' + demoPwd + ', ' + xmppResource + ')')
        
        # show news on the buttom
        xbmc.executebuiltin('RunScript(script.news.container, ' + serverIP + ')')
        
        # show video comments the right column
        xbmc.executebuiltin('RunScript(script.comments.update)')

        # start auto shutdown service
        xbmc.executebuiltin('RunScript(script.auto.shutdown, ' + shutdowntime + ')')

        xbmc.sleep(3000)
        # show qrcode
        xbmc.executebuiltin('RunScript(script.qrcode.update, '+ serverIP + ', '+ demoID + ', ' + demoPwd + ', ' + xmppResource + ')')



