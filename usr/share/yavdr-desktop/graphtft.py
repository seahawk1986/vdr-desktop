#!/usr/bin/python2
# vim: set fileencoding=utf-8 :
# Alexander Grothe 2012

import dbus
import logging

class GraphTFT():
    '''Handle GraphTFT if loaded'''
    hdfpath = 'yavdr.frontend.graphtft'
    viewnormal = 'yavdr.frontend.graphtft.view_normal'
    viewdetached = 'yavdr.frontend.graphtft.view_detached'
    def __init__(self,bus,hdf,settings):
        self.settings = settings
        self.bus = bus
        self.hdf = hdf
        self.check_graphtft(settings)
        self.loadsettings()
        
        
    def loadsettings(self):
        self.view = self.hdf.readKey(GraphTFT.viewdetached,"NonLiveTv")
        self.hdf.writeKey(GraphTFT.viewdetached,self.view)
        self.hdf.writeFile()
        
    def check_graphtft(self,settings):
        plugins = settings.get_dbusPlugins()
        if 'graphtft' in plugins:
            logging.info(u"GraphTFT-Plugin is active")
            self.graphtft = True
        else:
            self.graphtft = False
        
    def graphtft_switch(self):
        if self.graphtft:
            dbusgraph = self.bus.get_object("de.tvdr.vdr","/Plugins/graphtft")
            if settings.frontend_active == 0:
               dbusgraph.SVDRPCommand(dbus.String('TVIEW'),dbus.String(hdf.readKey(GraphTFT.viewdetached,"NonLiveTv")),dbus_interface='de.tvdr.vdr.plugin')
            elif settings.frontend_active == 1:
               dbusgraph.SVDRPCommand(dbus.String('RVIEW'),dbus.String(None),dbus_interface='de.tvdr.vdr.plugin')
