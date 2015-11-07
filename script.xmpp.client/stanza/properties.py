import logging

from sleekxmpp.xmlstream import ElementBase, ET
from sleekxmpp.thirdparty import OrderedDict

# <properties xmlns="http://www.jivesoftware.com/xmlns/xmpp/properties">
#     <property>
#         <name>type</name>
#         <value type="string">state_update</value>
#     </property>
# </properties>

class Properties(ElementBase):
    #: The `name` field refers to the basic XML tag name of the
    #: stanza. Here, the tag name will be 'action'.
    name = 'properties'
    #: The namespace of the main XML tag.
    namespace = 'http://www.jivesoftware.com/xmlns/xmpp/properties'
    #: The `plugin_attrib` value is the name that can be used
    #: with a parent stanza to access this stanza. For example
    #: from a Message stanza object, accessing:
    #:
    #:     msg['properties']
    #:
    #: would reference an Properties object, and will even create
    #: a Properties object and append it to the Message stanza if
    #: one doesn't already exist.
    plugin_attrib = 'properties'
    interfaces = set()

    def add_property(self, name, value):
        property = Property(parent=self)
        property['name'] = name
        property['value'] = value
        return property

    def get_properties(self):
        properties = OrderedDict()
        propertiesXML = self.xml.findall('{%s}property' % self.namespace)
        for propertyXML in propertiesXML:
            property = Property(xml=propertyXML)
            properties[property['name']] = property['value']
        return properties

class Property(ElementBase):
    name = 'property'
    namespace = 'http://www.jivesoftware.com/xmlns/xmpp/properties'
    plugin_attrib = 'property'
    interfaces = set(['name', 'value'])
    #: By default, values in the `interfaces` set are mapped to
    #: attribute values. This can be changed such that an interface
    #: maps to a subelement's text value by adding interfaces to
    #: the sub_interfaces set.
    sub_interfaces = set(['name'])

    def getValue(self):
        return self._get_sub_text('value')

    def setValue(self, value):
        self._set_sub_text('value', text=value)
        node = self.xml.find('{%s}value' % self.namespace)
        node.attrib['type'] = 'string'
        return self


