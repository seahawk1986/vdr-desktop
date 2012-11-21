#!/usr/bin/python2
# vim: set fileencoding=utf-8 :
# Alexander Grothe 2012

import codecs
import datetime
import dbus
import dbus.service
import fcntl
import gobject
import gtk
import logging
import neo_cgi
import neo_util
import os
import psutil
import re
import socket
import string
import subprocess
import sys
import syslog
import time
import wnck

from optparse import OptionParser
from dbus.mainloop.glib import DBusGMainLoop

# Import own Modules
from optionparser import Options
from hdftool import HDF
#from vdrSetup import dbusVDRSetup
from vdrDBusCommands import vdrDBusCommands
from settings import Settings
from lircsocket import lircConnection
from graphtft import GraphTFT
from wnckController import wnckController

DBusGMainLoop(set_as_default=True)

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
            systembus = dbus.SystemBus()
            logging.info(u'Connected to SystemBus')
        except:
            logging.exception(u"could not connect to SystemBus")
            sys.exit(1)
        try:
            sessionbus = dbus.SessionBus()
            logging.info(u'Connected to SessionBus')
        except:
            logging.exception(u"could not connect to SessionBus")
            sys.exit(1)
        
        # load hdf
        self.hdf = HDF(options.hdf_file)
        # dbus2vdr /Setup fuctions
        self.vdrCommands = vdrDBusCommands(systembus)
        # check if graphtft is running
        self.graphtft = GraphTFT(systembus,self.hdf,self.vdrCommands.vdrSetup)
        self.settings = Settings(systembus,self.hdf,self.options,self.vdrCommands)
        self.lircConnection = lircConnection(self.vdrCommands)
     
        
if __name__ == '__main__':
    options = Options()
    main = Main(options.get_options())
    
    while gtk.events_pending():
        gtk.main_iteration()
    gtk.main()
