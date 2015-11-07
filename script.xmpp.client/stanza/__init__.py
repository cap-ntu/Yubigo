from sleekxmpp.xmlstream import register_stanza_plugin
from properties import Properties
from sleekxmpp.stanza import Message

def register_stanza_plugins():
    register_stanza_plugin(Message, Properties)
