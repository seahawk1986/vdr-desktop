#!/usr/bin/python
# vim: set fileencoding=utf-8 :
# Alexander Grothe 2012

# dbus
import dbus
import dbus.service
from dbus.mainloop.glib import DBusGMainLoop
DBusGMainLoop(set_as_default=True)

import codecs
import datetime
import fcntl
import gobject
import gtk
import logging
import os
import re
import string
import sys
import time
import wnck

from optionparser import Options
from hdftool import HDF

# Import own Modules
from vdrDBusCommands import vdrDBusCommands
from settings import Settings
from lircsocket import lircConnection
from graphtft import GraphTFT
import dbusService
from wnckController import wnckController
from adeskbar import adeskbarDBus

class Main():
    def __init__(self,options):
        # command line arguments
        self.options = options
        # Logging
        logging.basicConfig(
            filename=self.options.logfile,
            level=getattr(logging,self.options.loglevel),
            format='%(asctime)-15s %(levelname)-6s %(message)s'            
            )
        logging.info(u"Started yavdr-frontend")
        # dbus SystemBus and SessionBus
        try:
            self.systembus = dbus.SystemBus()
            logging.info(u'Connected to SystemBus')
        except:
            logging.exception(u"could not connect to SystemBus")
            sys.exit(1)
        try:
            self.sessionbus = dbus.SessionBus()
            logging.info(u'Connected to SessionBus')
        except:
            logging.exception(u"could not connect to SessionBus")
            sys.exit(1)      
        # init hdf
        self.hdf = HDF(options.hdf_file)
        # dbus2vdr fuctions
        self.vdrCommands = vdrDBusCommands(self)
        # Settings for frontend process
        self.settings = Settings(self)
        self.graphtft = GraphTFT(self)
        # connect to (event)lircd-Socket
        self.lircConnection = lircConnection(self,self.vdrCommands)
        # wnck Window Controller
        self.wnckC = wnckController(self)
        # dbus Control for yavdr-frontend
        self.dbusService = dbusService.dbusService(self)
        # PIP Class
        self.dbusPIP = dbusService.dbusPIP(self)
        # Adeskbar control
        self.adeskbar = adeskbarDBus(self.systembus)
        
        if self.hdf.readKey('vdr.frontend') == 'softhddevice' and self.vdrCommands.vdrSofthddevice:
            logging.info(u'Configured softhddevide as primary frontend')
            self.frontend = self.vdrCommands.vdrSofthddevice
        self.frontend.attach()
        
    def start_app(self,cmd,detachf=True):
        if self.settings.frontend_active == 1 and detachf == True:
            self.dbusService.detach()
            self.wnckC.windows['softhddevice_main'] = None
            self.settings.reattach = 1
        else:
            self.settings.reattach = 0
        print(settings.conf['user'])
        proc = subprocess.Popen(cmd) # Spawn process
        gobject.child_watch_add(proc.pid,self.on_exit,proc) # Add callback on exit

    def on_exit(self,pid, condition,data):
        print "called function with pid=%s, condition=%s, data=%s"%(pid, condition,data)
        if condition == 0:
            logging.info(u"normal exit")
            gobject.timeout_add(500,reset_external_prog)
        elif condition < 16384:
            logging.warn(u"abnormal exit: %s",condition)
            gobject.timeout_add(500,reset_external_prog)
        elif condition == 16384:
            logging.info(u"XBMC shutdown")
            self.dbusService.send_shutdown(user=True)
        elif condition == 16896:
            logging.info(u"XBMC wants a reboot")
        return False
        
     
        
if __name__ == '__main__':
    options = Options()
    main = Main(options.get_options())
    
    while gtk.events_pending():
        gtk.main_iteration()
    gtk.main()
