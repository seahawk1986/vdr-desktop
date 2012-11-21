#!/usr/bin/python2
# vim: set fileencoding=utf-8 :
# Alexander Grothe 2012

import dbus
import dbus.service
from dbus.mainloop.glib import DBusGMainLoop
DBusGMainLoop(set_as_default=True)

import logging
import gtk

from vdrPIP import vdrPIP

class dbusService(dbus.service.Object):
    def __init__(self,main_instance):
        self.main_instance = main_instance
        bus_name = dbus.service.BusName('de.yavdr.frontend', bus=main_instance.systembus)
        dbus.service.Object.__init__(self, bus_name, '/frontend')

    @dbus.service.method('de.yavdr.frontend',in_signature='i',out_signature='b')
    def deta(self,active=0):
        self.main_instance.frontend.detach()
        if active == 1:
            self.main_instance.settings.frontend_active = 1
            self.main_instance.settings.external_prog = 1
        self.main_instance.graphtft.graphtft_switch()
        return True

    @dbus.service.method('de.yavdr.frontend',out_signature='b')
    def atta(self):
        self.main_instance.frontend.resume(frontend.status())
        self.main_instance.settings.external_prog = 0
        return True

    @dbus.service.method('de.yavdr.frontend',out_signature='b')
    def start(self):
        self.main_instance.startup()
        return True

    @dbus.service.method('de.yavdr.frontend',out_signature='b')
    def toggle(self):
        if self.main_instance.settings.frontend_active == 0 and self.main_instance.settings.external_prog == 0:
            status = self.main_instance.frontend.status()
            if status == "SUSPENDED":
                self.main_instance.frontend.resume()
            elif status == "SUSPEND_DETACHED":
                self.main_instance.frontend.attach()
            self.main_instance.graphtft.graphtft_switch()
            self.main_instance.settings.external_prog = 0
            self.main_instance.settings.frontend_active = 1
        else:
            self.main_instance.frontend.detach()
            self.main_instance.settings.external_prog = 0
            self.main_instance.settings.frontend_active = 0
        return True

    @dbus.service.method('de.yavdr.frontend',out_signature='b')
    def start_xbmc(self):
        if not settings.external_prog == 1:
            self.main_instance.settings.external_prog = 1
            cmd = ['/usr/lib/xbmc/xbmc.bin','--standalone','--lircdev','/var/run/lirc/lircd']
            start_app(cmd)#
            return True

    @dbus.service.method('de.yavdr.frontend',in_signature='si',out_signature='b')
    def start_application(self,cmd,standalone=0):
        self.main_instance.settings.external_prog = 1
        start_app(cmd)#
        return True

    @dbus.service.method('de.yavdr.frontend',out_signature='b')
    def fullscreen(self):
        window = self.main_instance.wnckC.windows['softhddevice_main']
        if window:
            gdkwindow = gtk.gdk.window_foreign_new(window.get_xid())
            gdkwindow.set_decorations(0)
            window.set_fullscreen(0)
            window.unmake_above()
            window.maximize()
            window.activate(int(time.strftime("%s",time.gmtime())))
        return True

    @dbus.service.method('de.yavdr.frontend',in_signature='sii',out_signature='b')
    def resize(self,s,above,decoration):
        w,h,x,y = self.main_instance.settings.tsplit(s,('x','+'))
        print(x,y,w,h)
        window = self.main_instance.wnckC.windows['softhddevice_main']
        logging.debug(u'got window %s',window)
        if window:
            gdkwindow = gtk.gdk.window_foreign_new(window.get_xid())
            self.main_instance.wnckC.resize(window,int(x),int(y),int(w),int(h),above,decoration)
            return True
        else:
            return False

    @dbus.service.method('de.yavdr.frontend',in_signature='isii',out_signature='b')
    def resizexid(self,xid,s,above,decoration):
        w,h,x,y = settings.tsplit(s,('x','+'))
        print(x,y,w,h)
        if window:
            gdkwindow = gtk.gdk.window_foreign_new(xid)
            self.main_instance.wnckC.resize(window,int(x),int(y),int(w),int(h),above,decoration)
            return True
        else:
            return False

    @dbus.service.method('de.yavdr.frontend',out_signature='b')
    def shutdown(self):
        self.main_instance.vdrControl.vdrRemote.enable()
        self.main_instance.vdrControl.vdrRemote.sendkey("POWER")
        if settings.frontend_active == 0:
            self.main_instance.vdrControl.vdrRemote.disable()
        self.main_instance.settings.timer = gobject.timeout_add(15000,soft_detach)
        return True

    @dbus.service.method('de.yavdr.frontend',out_signature='b')
    def check_shutdown(self):
        self.send_shutdown(user=True)
        return True
        
    @dbus.service.method('de.yavdr.frontend',out_signature='b')
    def send_shutdown(self,user=False):
        if self.main_instance.vdrControl.vdrShutdown.confirmShutdown(user):
            self.main_instance.vdrControl.vdrRemote.enable()
            self.main_instance.sendkey("POWER")
            self.main_instance.vdrControl.vdrRemote.disable()
        return True

    @dbus.service.method('de.yavdr.frontend',in_signature='s',out_signature='b')
    def setBackground(self,path):
        if os.path.isfile(path):
            subprocess.call(["/usr/bin/feh","--bg-fill",path], env=settings.env)
            syslog.syslog("setting Background to %s"%(path))
            return True
        else:
            return False

    @dbus.service.method('de.yavdr.frontend',out_signature='s')
    def vdr_stop(self):
        print "stopping vdr"

        self.main_instance.frontend.detach()
        try:
            self.main_instance.pip.vdr.stopvdr()
        except: pass
        vdr_pid = 1
        while vdr_pid:
            vdr_pid = [p.pid for p in psutil.process_iter() if "vdr" in str(p.name)]
            if vdr_pid:
                print "waiting for VDR exit"
                time.sleep(1)
            else:
                print("vdr terminated")
        main()
        return True
        
class dbusPIP(dbus.service.Object):
    def __init__(self,main_instance):
        self.main_instance = main_instance
        bus_name = dbus.service.BusName('de.yavdr.frontend', bus=main_instance.systembus)
        dbus.service.Object.__init__(self, bus_name, '/pip')
        self.wnckctrl = main_instance.wnckC
        self.vdr = vdrPIP(main_instance)
        

    def activateWindow(self,window):
        pass
        window.activate(int(time.strftime("%s",time.gmtime())))

    @dbus.service.method('de.yavdr.frontend',out_signature='s')
    def win(self):
        return ", ".join(self.wnckctrl.windows)
    @dbus.service.method('de.yavdr.frontend',out_signature='b')
    def start(self):
        if self.vdr.proc == None:
            self.vdr.run_vdr()
        self.vdr.attach()
        return True

    @dbus.service.method('de.yavdr.frontend',out_signature='b')
    def stop(self):
        main_window = self.wnckctrl.windows['softhddevice_main']
        if main_window == None:
            frontend.attach()
            time.sleep(1)
        self.wnckctrl.maximize_and_undecorate(main_window)
        if self.vdr.proc != None:
            #self.vdr.proc.terminate()
            #self.vdr.proc = None
            self.vdr.detach()
            gobject.timeout_add(500,self.activateWindow,main_window)
            return True
        else:
            gobject.timeout_add(500,self.activateWindow,main_window)
            return False


    @dbus.service.method('de.yavdr.frontend',out_signature='b')
    def toggle(self):
        pip_window = self.wnckctrl.windows['softhddevice_pip']
        main_window = self.wnckctrl.windows['softhddevice_main']
        if pip_window == None:
            if self.vdr.proc == None:
                self.vdr.run_vdr()
            self.vdr.attach()
            gobject.timeout_add(500,self.activateWindow,main_window)
            return True
        else:
            self.vdr.detach()
            #self.vdr.proc.terminate()
            #self.vdr.proc = None
            main_window = self.wnckctrl.windows['softhddevice_main']
            if main_window != None:
                frontend.attach()
                time.sleep(1)
                self.wnckctrl.maximize_and_undecorate(main_window)
            gobject.timeout_add(500,self.activateWindow,main_window)
            return True

    @dbus.service.method('de.yavdr.frontend',out_signature='b')
    def sbs(self):
        main_window = self.wnckctrl.windows['softhddevice_main']
        pip_window = self.wnckctrl.windows['softhddevice_pip']
        if main_window == None:
            self.main_instance.frontend.attach()
            time.sleep(2)
        self.wnckctrl.resize(main_window,0,0,1600,900,0,0)
        if pip_window == None:
            if self.vdr.proc == None:
                self.vdr.run_vdr()
            self.vdr.attach()
            time.sleep(2)
        if pip_window != None:
            self.wnckctrl.resize(pip_window,1200,795,720,405,0,0)
            pip_window.make_above()
        if main_window != None:
            gobject.timeout_add(500,self.activateWindow,main_window)
        gobject.timeout_add(800,adeskbar.hide)
        return True


    @dbus.service.method('de.yavdr.frontend',in_signature='sii',out_signature='b')
    def resize(self,s,above,decoration):
        w,h,x,y = main_instance.settings.tsplit(s,('x','+'))
        print(x,y,w,h)
        window = self.wnckctrl.windows['softhddevice_pip']
        if window:
            self.wnckctrl.resize(window,int(x),int(y),int(w),int(h),above,decoration)
            return True
        else:
            return False
