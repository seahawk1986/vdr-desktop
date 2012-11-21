#!/usr/bin/python2
# vim: set fileencoding=utf-8 :
# Alexander Grothe 2012
import dbus
import logging

class vdrDBusCommands():
    def __init__(self,bus):
        self.vdrSetup = dbusVDRSetup(bus)
        self.vdrShutdown = dbusShutdown(bus)


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

class dbusShutdown():
    '''wrapper for shutdown interface provided by the dbus2vdr plugin'''
    def __init__(self,bus):
        self.dbusshutdown = bus.get_object("de.tvdr.vdr","/Shutdown")
        self.interface = 'de.tvdr.vdr.shutdown'

    def manualstart(self):
        return self.dbusshutdown.ManualStart(dbus_interface=self.interface)

    def confirmShutdown(self,user=False):
        code, message, shutdownhooks, message = self.dbusshutdown.ConfirmShutdown(dbus.Boolean(user),dbus_interface=self.interface)
        if code in [250,990]: return True
        else:
            logging.info(u"vdr not ready for shutdown: %s: %s"%(code,message))
            return False
