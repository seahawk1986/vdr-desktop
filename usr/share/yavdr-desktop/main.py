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
import subprocess
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
        # wait for VDR running
        self.running = self.wait_for_vdrstart()
        try:
            logging.debug(u'connecting to upstart')
            self.upstart_vdr = self.systembus.get_object("org.freedesktop.DBus","/com/ubuntu/Upstart/jobs/vdr")
            self.upstart_vdr.connect_to_signal("VDR", self.signal_handler, dbus_interface="com.ubuntu.Upstart0_6.Instance")
            self.systembus.add_signal_receiver(self.signal_handler, interface_keyword='dbus_interface', member_keyword='member', sender_keyword='sender', path_keyword='path'
)
            logging.debug(u'connected to upstart')
        except dbus.DBusException:
            logging.debug(u'ran into exception')
            logging.exception(traceback.print_exc())
        # dbus2vdr fuctions
        self.vdrCommands = vdrDBusCommands(self)
        
        # dbus Control for yavdr-frontend
        self.dbusService = dbusService.dbusService(self)
        # Settings for frontend process
        self.settings = Settings(self)
        self.graphtft = GraphTFT(self)
        # wnck Window Controller
        self.wnckC = wnckController(self)
        
        # PIP Class
        self.dbusPIP = dbusService.dbusPIP(self)
        # Adeskbar control
        self.adeskbar = adeskbarDBus(self.systembus)
        # connect to (event)lircd-Socket
        self.lircConnection = lircConnection(self,self.vdrCommands)
        if self.hdf.readKey('vdr.frontend') == 'softhddevice' and self.vdrCommands.vdrSofthddevice:
            logging.info(u'Configured softhddevide as primary frontend')
            self.frontend = self.vdrCommands.vdrSofthddevice
        self.frontend.attach()
            
    def startup(self):
        # dbus2vdr fuctions
        self.vdrCommands = vdrDBusCommands(self)
        self.graphtft = GraphTFT(self)
        
        
        if self.hdf.readKey('vdr.frontend') == 'softhddevice' and self.vdrCommands.vdrSofthddevice:
            logging.info(u'Configured softhddevide as primary frontend')
            self.frontend = self.vdrCommands.vdrSofthddevice
        self.frontend.attach()
        
    def wait_for_vdrstart(self):
        upstart = self.systembus.get_object("com.ubuntu.Upstart", "/com/ubuntu/Upstart")
        status = None
        while not status == 'start/running':
            try:
                path = upstart.GetJobByName("vdr", dbus_interface="com.ubuntu.Upstart0_6")
                job = self.systembus.get_object("com.ubuntu.Upstart", path)
                path = job.GetInstance([], dbus_interface="com.ubuntu.Upstart0_6.Job")
                instance = self.systembus.get_object("com.ubuntu.Upstart", path)
                props = instance.GetAll("com.ubuntu.Upstart0_6.Instance", dbus_interface=dbus.PROPERTIES_IFACE)
                status = "%s/%s"%(props["goal"], props["state"])
            except: pass
            if not status: 
                logging.info('vdr upstart job not running, wait 1 s')
                time.sleep(1)
            else:
                logging.info('vdr upstart job running')
                return True
    
    def signal_handler(self,*args, **kwargs):
        if '/com/ubuntu/Upstart/jobs/vdr/_' == kwargs['path']:
            if kwargs['member'] == "StateChanged":
                logging.debug("StateChanged:")
                if not self.running and 'running' in args[0]:
                    self.startup()
                    self.running = True
                    logging.debug(u"vdr upstart job running")
                    #self.frontend.attach()
                if 'waiting' in args[0]:
                    self.running = False
                    logging.debug(u"vdr upstart job stopped/waiting")
            elif kwargs['member'] == "InstanceRemoved":
                logging.debug("killed job")
            elif kwargs['member'] == "InstanceAdded":
                logging.debug("added upstart-job")
            else:
                return
            if len(args):
                logging.info("VDR is %s", args[0])
                #logging.info(kwargs)
        
    def start_app(self,cmd,detachf=True):
        logging.info('starting %s',cmd)
        if self.settings.frontend_active == 1 and detachf == True:
            logging.info('detaching frontend')
            self.dbusService.deta()
            self.wnckC.windows['softhddevice_main'] = None
            self.settings.reattach = 1
        else:
            self.settings.reattach = 0
        logging.info('starting %s',cmd)
        proc = subprocess.Popen(cmd) # Spawn process
        gobject.child_watch_add(proc.pid,self.on_exit,proc) # Add callback on exit

    def on_exit(self,pid, condition,data):
        logging.debug("called function with pid=%s, condition=%s, data=%s",pid, condition,data)
        self.settings.external_prog = 0
        if condition == 0:
            logging.info(u"normal exit")
            gobject.timeout_add(500,self.reset_external_prog)
        elif condition < 16384:
            logging.warn(u"abnormal exit: %s",condition)
            gobject.timeout_add(500,reset_external_prog)
        elif condition == 16384:
            logging.info(u"XBMC shutdown")
            self.dbusService.send_shutdown(user=True)
        elif condition == 16896:
            logging.info(u"XBMC wants a reboot")
        
        return False
        
    def reset_external_prog(self):
        self.settings.external_prog = 0
        if self.settings.reattach == 1:
            logging.info("restart vdr-frontend")
            self.dbusService.toggle()
            self.settings.frontend_active = 1
        else:
            self.settings.frontend_active = 0
        return False
        
     
        
if __name__ == '__main__':
    options = Options()
    main = Main(options.get_options())
    
    while gtk.events_pending():
        gtk.main_iteration()
    gtk.main()
