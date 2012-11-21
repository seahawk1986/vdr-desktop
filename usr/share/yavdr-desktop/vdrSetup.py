#!/usr/bin/python2
# vim: set fileencoding=utf-8 :
# Alexander Grothe 2012

import dbus
import logging

class dbusVDRSetup():
    '''wrapper for setup interface provided by the dbus2vdr plugin'''
    def __init__(self,bus):
        self.bus = bus
        self.dbussetup = self.bus.get_object("de.tvdr.vdr","/Setup")
        self.interface = 'de.tvdr.vdr.setup'

    def vdrsetupget(self,option):
        value = self.dbussetup.Get(dbus.String(option),dbus_interface=self.interface)
        logging.debug(u"got value %s for setting %s"%(value,option))
        return value

    def get_dbusPlugins(self):
        '''wrapper for dbus plugin list'''
        logging.info(u"asking vdr for plugins")
        dbusplugins = self.bus.get_object("de.tvdr.vdr","/Plugins")
        raw = dbusplugins.List(dbus_interface="de.tvdr.vdr.plugin")
        plugins = {}
        for name, version in raw:
            logging.debug(u"found plugin %s %s"%(name,version))
            plugins[name]=version
        return plugins
