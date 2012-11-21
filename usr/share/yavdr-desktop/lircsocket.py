#!/usr/bin/python2
# vim: set fileencoding=utf-8 :
# Alexander Grothe 2012

import gobject
import logging
import socket

class lircConnection():
    def __init__(self,vdrCommands,socket_path="/var/run/lirc/lircd"):
        self.socket_path = socket_path
        self.vdrCommands = vdrCommands
        self.try_connection()
        
    def connect_eventlircd(self):
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.connect(self.socket_path)
        gobject.io_add_watch(sock, gobject.IO_IN, self.handler)

    def try_connection(self):
        try:
            self.connect_eventlircd()
            logging.info(u"conntected to Lirc-Socket on %s"%(self.socket_path))
            return False
        except:
            gobject.timeout_add(1000, self.try_connection)
            logging.error("Error: vdr-frontend could not connect to eventlircd socket")
            return True
            
    def handler(self, sock, *args):
        '''callback function for activity on eventlircd socket'''
        try:
            buf = sock.recv(1024)
            if not buf:
                sock.close()
                logging.error("Error reading from lircd socket")
                try_connection()
                return True
        except:
            sock.close()
            try_connection()
            return True
        lines = string.split(buf, "    n")
        for line in lines[:-1]:
          if settings.external_prog == 1: pass
          else:
            try: gobject.source_remove(settings.timer)
            except: pass
            try:  code,count,cmd,device = string.split(line, " ")[:4]
            except: return True
            if cmd == settings.conf['key_detach']:
                if frontend.status() == "NOT_SUSPENDED":
                    detach()
                    settings.frontend_active = 0
                else:
                    resume(frontend.status())
            elif cmd == settings.conf['key_xbmc'] and settings.external_prog == 0:
                    settings.external_prog = 1
                    #gobject.timeout_add(50, start_xbmc)
                    cmd = ['/usr/lib/xbmc/xbmc.bin','--standalone','--lircdev','/var/run/lirc/lircd']
                    gobject.timeout_add(50, start_app,cmd)
                    return True

            elif cmd == settings.conf['key_power']:
                if frontend.status() == "NOT_SUSPENDED":
                    settings.timer = gobject.timeout_add(15000,soft_detach)
                    settings.frontend_active = 0
                else:
                    send_shutdown()
            else:
                if settings.frontend_active == 0 and settings.external_prog == 0:
                    resume(frontend.status())
                    settings.frontend_active = 1
                else:
                    pass
        return True
