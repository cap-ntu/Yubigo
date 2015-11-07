import sys
import xbmc, xbmcgui, xbmcaddon
import logging
import urllib
import getpass
from optparse import OptionParser
import sleekxmpp
import json
import os
import requests
import base64
from datetime import datetime, date, time
from calendar import timegm

# code header
__author__       = "jyc"
__scriptid__     = "script.xmpp.client"
__addon__        = xbmcaddon.Addon(id=__scriptid__)
__addonid__      = __addon__.getAddonInfo('id')
__addonversion__ = __addon__.getAddonInfo('version')
__cwd__          = __addon__.getAddonInfo('path')
__language__     = __addon__.getLocalizedString

# skin parameters, details can be found on skin package
CANCEL_DIALOG  = ( 9, 10, 92, 216, 247, 257, 275, 61467, 61448, )

# global parameters
#xbmcgui.Dialog().ok(file_id, user_name + str(msg['body']))
global isVideoTransfer
global isCommentTransfer
global isNewsTransfer
global xmppIP
global serverIP
global delta_time
delta_time = 0
global userID
global userPwd
comment_content_path = xbmc.translatePath("special://home/")

# ROI parameter
factor = 0.5
comment_height = 940 * factor
comment_width = 400 * factor
comment_x = 1520 * factor
comment_y = 0
video_height = 940 * factor
video_width = 1510 * factor
video_x = 0
video_y = 0
news_height = 130 * factor
news_width = 1520 * factor
news_x = 0
news_y = 950 * factor

def readnews():
    global serverIP
    news_content = urllib.urlopen(serverIP + '/get_news/').read()
    news_list = json.loads(news_content).get('data')
    news_content = ""
    news_index = 1
    for news in news_list:
        news_content += str(news_index) + ". " + news.get('content') + " (" + news.get('time') + ")    "
        news_index += 1
    return news_content

def update_playlist():
    global serverIP
    global userID
    global userPwd
    r = requests.post(str(serverIP)+'/users/login/',data=dict(LoginID=userID, Password=userPwd))
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
            thumbnail_url = video.get('thumbnail')
            video_url = video.get('url') 
            video_url = video_url.replace('raw_video','content/files')       
            listitem=xbmcgui.ListItem(label=video_title, iconImage=thumbnail_url, thumbnailImage=thumbnail_url)
            playlist.add(url=video_url, listitem=listitem)
        # end of 'for'

        # loop the content on the list
        xbmc.Player().play(playlist)
        xbmc.executebuiltin("PlayerControl(RepeatAll)")

# start session transfer once mobile device sends request
def start_session_transfer():
    global serverIP
    # encode sycn image, and organize response xmpp message to mobile phone   
    video_url = str(xbmc.Player().getPlayingFile())
    video_id = video_url.split('/')[len(video_url.split('/'))-1]
    video_id = video_id[: video_id.find('.')]
    comment_content = ""
    news_content = readnews()
    news_length = len(news_content) if len(news_content) < 102 else 102
    news_content = news_content[0:news_length]
    if os.path.exists(comment_content_path + video_id):
        with open(comment_content_path + video_id,'r') as f: 
            comment_content = f.read()
        if len(comment_content.split('\n')) > 20:
            displayed_comment = ""
            for i in range(0,20): 
                displayed_comment += comment_content.split('\n')[i] + '\n'
            comment_content = displayed_comment
    image_URL = serverIP + "/migration/preview_tv/?width=960&height=540&uuid=" + str(video_id) + "&time=" + str(float(xbmc.Player().getTime())) + "&comment=" + comment_content + "&news=" + news_content
    encoded = base64.b64encode(urllib.urlopen(image_URL.encode('utf-8')).read())
    encoded = 'data:image/jpg;base64,' + encoded
    
    payLoad = '{"type":"pagesize","bg":"' + encoded + '","list":[{"x":'+str(video_x)+',"y":'+str(video_y)+',"width":'+str(video_width)+',"height":'+str(video_height)+'},{"x":'+str(comment_x)+',"y":'+str(comment_y)+',"width":'+str(comment_width)+',"height":'+str(comment_height)+'},{"x":'+str(news_x)+',"y":'+str(news_y)+',"width":'+str(news_width)+',"height":'+str(news_height)+'}]}'
    return payLoad


# deal with the ROI indication
def handle_query_pos(x, y):
    height = video_height
    width = video_width
    left = video_x
    top = video_y
    category = 'video'
    if (x > comment_x) and (x < comment_x + comment_width) and (y < comment_y + comment_height) and (y > comment_y):
        height = comment_height
        width = comment_width
        left = comment_x
        top = comment_y
        category = 'comment'
    elif (x > news_x) and (x < news_x + news_width) and (y < news_y + news_height) and (y > news_y):
        height = news_height
        width = news_width
        left = news_x
        top = news_y
        category = 'news'
    res = '{"id":"1","type":"rect","category":"' + category + '","bound":{"x":"' + str(left) + '","y":"' + str(top) + '","height":"' + str(height) + '","width":"' + str(width) + '"}}'
    global isVideoTransfer
    global isCommentTransfer
    global isNewsTransfer
    isNewsTransfer = False
    isCommentTransfer = False
    isVideoTransfer = False
    if cmp(category, 'video') == 0:
        isVideoTransfer = True
    elif cmp(category, 'comment') == 0:
        isCommentTransfer = True
    elif cmp(category, 'news') == 0:
        isNewsTransfer = True
    return res

# return requested sessions to mobile device after ROIs are indicated
def handle_transfer_request():
    global isVideoTransfer
    global isCommentTransfer
    global isNewsTransfer
    global delta_time
    packs = ''
    transfer_type = 'back'
    if isVideoTransfer:  
        video_url = str(xbmc.Player().getPlayingFile())
        video_id = video_url.split('/')
        video_id = video_id[len(video_id)-1]
        video_id = video_id[: video_id.find('.')]
        packs = '"{\\"category\\":\\"video\\",\\"video_url\\":\\"' + video_url + '\\",\\"video_id\\":\\"' + video_id + '\\",\\"isPlaying\\":true,\\"timestamp\\":' + str(int(build_time(datetime.utcnow()) + delta_time)) + ',\\"position\\":' + str(int(xbmc.Player().getTime() * 1000)) + '}"'
        packs = '[' + packs + ']'
    elif isCommentTransfer:
        transfer_type = 'transfer-data'
        head = '"{\\"category\\":\\"comment\\",\\"msg\\":'
        video_id = str(xbmc.Player().getPlayingFile()).split('/')
        video_id = video_id[len(video_id)-1]
        video_id = video_id[: video_id.find('.')]
        if os.path.exists(comment_content_path + video_id):
            with open(comment_content_path + video_id,'r') as f:
                comment_list = f.readlines()
        else:
            packs = ']}"'
            comment_list = ""
        commenter_name = ""
        comments = ""
        for i in range(0, len(comment_list)):
            if i%3 == 0: 
                commenter_name = comment_list[i].replace('\n','')
            elif i%3 == 1:
                comments = comment_list[i].replace('\n','')
            else:
                packs = packs + '{\\"from\\":\\"'+commenter_name+'\\",\\"self\\":true,\\"content\\":\\"'+comments+'\\"}'
                if i != len(comment_list) - 1:
                    packs = packs + ','
                else:
	            packs = packs + ']}"'
        packs = '[' + head + '[' + packs + ']'
    elif isNewsTransfer:
        transfer_type = 'transfer-data'
        head = '"{\\"category\\":\\"news\\",\\"msg\\":'
        packs = '[' + head + '[]}"]'
    res = '{"type":"' + transfer_type + '","ok":true,"payload":' + packs + '}'
    return res

# xmpp message handler
class EchoBot(sleekxmpp.ClientXMPP):
    def __init__(self, jid, password):
        sleekxmpp.ClientXMPP.__init__(self, jid, password)
        self.add_event_handler("session_start", self.start)
        # The message event is triggered whenever a message
        # stanza is received. Be aware that that includes
        # MUC messages and error messages.
        self.add_event_handler("message", self.message)

    def start(self, event):
        self.send_presence()
        self.get_roster()

    def message(self, msg):
        global delta_time
        global serverIP
        global userID
        global userPwd
        if cmp(str(msg['type']), 'chat') == 0:
            r = requests.post(serverIP+'/users/login/',data=dict(LoginID=userID, Password=userPwd))
            cookies = r.cookies   
            res = requests.post(serverIP+'/users/info/',cookies=cookies,data='{"type":"request","request":"retrieve-info","jids":["'+str(msg['from'])[:-9]+'"]}')
            user_name = 'unknown'
            try:
                user_name = str(json.loads(res.text).get('result')[0].get('name'))
                user_name = user_name.split(' ')[0]
            except:
                pass
            video_id = str(xbmc.Player().getPlayingFile()).split('/')
            video_id = video_id[len(video_id)-1]
            video_id = video_id[: video_id.find('.')]
            comment_content = ""
            if os.path.exists(comment_content_path + video_id):
                with open(comment_content_path + video_id,'r') as f: 
                    comment_content = f.read()
            with open(comment_content_path + video_id,'w') as f: 
                f.write(user_name + ' (' + str(datetime.now().strftime("%d/%m/%y %H:%M")) +'):' + '\n' + str(msg['body'])+'\n\n'+comment_content) 
            xbmc.executebuiltin('SendClick(4300,9930)')
        elif cmp(str(msg['properties'].get_properties()['type']), 'playlist_update') == 0:
            update_playlist()
        elif cmp(str(msg['properties'].get_properties()['type']), 'news_update') == 0:
            xbmc.executebuiltin('SendClick(4200,9921)')
        elif cmp(json.loads(msg['body']).get('type'), 'request') == 0:
            payLoad = start_session_transfer()
            msg = self.make_message(mto = msg['from'], mbody = payLoad, mtype='headline')
            add_properties(msg, {'type': 'migration'})
            msg.send()

            msg = self.make_message(mto = 'session_controller@socialtv', mbody = '{"send_time":'+str(build_time(datetime.utcnow()))+'}', mtype='headline')
            add_properties(msg, {'type': 'time_sync_request'})  
            msg.send()
        elif cmp(json.loads(msg['body']).get('type'), 'query_pos') == 0:
            x = int(json.loads(msg['body']).get('x'))
            y = int(json.loads(msg['body']).get('y'))
            res = handle_query_pos(x,y)
            msg = self.make_message(mto = msg['from'], mbody = res, mtype='headline')
            add_properties(msg, {'type': 'migration'})  
            msg.send()
        elif cmp(json.loads(msg['body']).get('type'), 'transfer') == 0:
            res = handle_transfer_request()
            msg = self.make_message(mto = msg['from'], mbody = res, mtype='headline')
            add_properties(msg, {'type': 'migration'})  
            msg.send()
            
            res = {
                'data': res,
                'back': False,
                'target': str(msg['to'])}
            res = json.dumps(res)
            msg = self.make_message(mto = 'session_controller@socialtv', mbody = res, mtype='headline')
            add_properties(msg, {'type': 'migration'})
            msg.send()

        elif cmp(json.loads(msg['body']).get('type'), 'back') == 0:
            msg_from = msg['from']
            res = {
                'data': msg['body'],
                'back': True,
                'target': str(msg['from'])}
            res = json.dumps(res)
            msg = self.make_message(mto = 'session_controller@socialtv', mbody = res, mtype='headline')
            add_properties(msg, {'type': 'migration'})
            msg.send()

            msg = self.make_message(mto = msg_from, mbody = '{"type":"back_ack"}', mtype='headline')
            add_properties(msg, {'type': 'migration'})  
            msg.send()

        elif cmp(str(msg['properties'].get_properties()['type']), 'time_sync_response') == 0:
            client_recv = build_time(datetime.utcnow())
            client_send = int(json.loads(msg['body']).get('client_send_time'))
            server_recv = int(json.loads(msg['body']).get('server_recv_time'))
            server_send = int(json.loads(msg['body']).get('send_time'))
            delta_time = ((server_recv - client_send) + (server_send - client_recv)) / 2
            

def add_properties(msg, properties):
    props = msg['properties']
    for prop in properties:
        props.add_property(
            name = prop,
            value = properties[prop]
        )

def build_time(now):
    return int(timegm(now.utctimetuple()) * 1000
                + now.microsecond / 1000)


if ( __name__ == "__main__" ):
    # get login information from the command line arguments.
    global serverIP
    global xmppIP
    global userID
    global userPwd

    serverIP = sys.argv[1] 
    xmppIP = sys.argv[2]
    userID = sys.argv[3]
    userPwd = sys.argv[4] 
    xmppResource = sys.argv[5]
    

    # login to get cookies    
    r = requests.post(str(serverIP)+'/users/login/',data=dict(LoginID=userID, Password=userPwd))
    cookies = r.cookies
         
    optp = OptionParser()
    # Output verbosity options.
    optp.add_option('-q', '--quiet', help='set logging to ERROR', action='store_const', dest='loglevel',
                    const=logging.ERROR, default=logging.INFO)
    optp.add_option('-d', '--debug', help='set logging to DEBUG', action='store_const', dest='loglevel',
                    const=logging.DEBUG, default=logging.INFO)
    optp.add_option('-v', '--verbose', help='set logging to COMM', action='store_const', dest='loglevel',
                    const=5, default=logging.INFO)

    # JID and password options.
    optp.add_option("-j", "--jid", dest="jid", help="JID to use")
    optp.add_option("-p", "--password", dest="password", help="password to use")
    opts, args = optp.parse_args()

    # Setup logging.
    logging.basicConfig(level=opts.loglevel, format='%(levelname)-8s %(message)s')
    
    # get XMPP service information
    r = requests.get(serverIP+'/users/chatconfig/', cookies=cookies).text
    r = json.loads(r)

    # Config XMPP Message
    if opts.jid is None:
        opts.jid = r.get('username') + '@' + r.get('domain') + '/' + xmppResource
    if opts.password is None:
        opts.password = r.get('password')

    xmpp = EchoBot(opts.jid, opts.password)
    xmpp.register_plugin('xep_0030') # Service Discovery
    xmpp.register_plugin('xep_0004') # Data Forms
    xmpp.register_plugin('xep_0060') # PubSub
    xmpp.register_plugin('xep_0199') # XMPP Ping
    from stanza import register_stanza_plugins
    register_stanza_plugins()

    if xmpp.connect((r.get('server'), 5222)):
        xmpp.process(block=True)
        print("Done")
    else:
        print("Unable to connect.")
    
    
