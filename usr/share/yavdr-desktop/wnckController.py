#!/usr/bin/python2
# vim: set fileencoding=utf-8 :
# Alexander Grothe 2012

import dbus
from dbus.mainloop.glib import DBusGMainLoop
DBusGMainLoop(set_as_default=True)
import wnck

class wnckController():
    def __init__(self,settings):
        self.settings = settings
        self.windows = {
        'softhddevice_main':None,
        'softhddevice_pip':None,
        'xbmc':None
        }
        self.windownames = ['softhddevice','Geany','XBMC Media Center']
        self.screen = wnck.screen_get_default()
        self.screen.connect("window-opened", self.on_window_opened)
        self.screen.connect('window-closed', self.on_window_closed)

        self.screen_height = self.screen.get_height()
        self.screen_width = self.screen.get_width()

    def on_window_opened(self,screen,window):
        gtk.main_iteration()
        wname = window.get_name()
        window.connect('name-changed', self.window_name_changed)
        self.window_name_changed(window)


    def window_name_changed(self, window):
        wname = window.get_name()
        if wname in self.windownames:
            if wname == 'softhddevice':
                if self.windows['softhddevice_main'] == None:
                    print("assigning new main window")
                    self.windows['softhddevice_main'] = window
                    self.maximize_and_undecorate(window)
                    #window.connect('geometry-changed', self.on_window_geochanged)
                elif self.windows['softhddevice_pip'] == None and self.windows['softhddevice_main'].get_xid() != window.get_xid():
                    print("softhddevice_pip")
                    self.windows['softhddevice_pip'] = window
                    self.resize(window,1200,795,720,405,1,0)
                elif window.get_xid() == self.windows['softhddevice_main'].get_xid():
                    print("main window already defined")
                else:
                    print("too many softhddevice windows!")
            elif wname == 'XBMC Media Center':
                print("Detected XBMC Media Center")
                gdkwindow = gtk.gdk.window_foreign_new(window.get_xid())
                gdkwindow.set_icon_list([gtk.gdk.pixbuf_new_from_file('/usr/share/icons/hicolor/48x48/apps/xbmc.png')])
                if not window.is_fullscreen():
                    print "no fullscreen - maximizing and undecorating"
                    window.set_fullscreen(0)
                    window.maximize()
                    #window.make_below()
                    window.unmake_above()

    def maximize_and_undecorate(self,window):
        print("Window recognized: %s"%window.get_name())
        print("Window is fullscreen: %s"%window.is_fullscreen())
        print("Window is maximized: %s"%window.is_maximized())
        gdkwindow = gtk.gdk.window_foreign_new(window.get_xid())
        gdkwindow.set_decorations(0)
        if window.is_fullscreen():
            print("set to maximized view")
            window.set_fullscreen(0)
            window.maximize()
        if not window.is_maximized():
            window.maximize()
        window.activate(int(time.strftime("%s",time.gmtime())))

        gdkwindow.set_icon_list([gtk.gdk.pixbuf_new_from_file('/usr/share/icons/xineliboutput-sxfe.svg')])

    def resize(self,window,x=0,y=0,w=1280,h=720,above=0,d=0):
        print("run resize")
        if window != None:
            if window.is_fullscreen():
                window.set_fullscreen(0)
            if window.is_maximized():
                window.unmaximize()
            if above == 1:
                window.make_above()
            else:
                window.unmake_above()
            window.set_geometry(0,255,x,y,w,h)
            gdkwindow = gtk.gdk.window_foreign_new(window.get_xid())
            gdkwindow.set_decorations(d)
        adeskbar.hide()

    def on_window_geochanged(self,window):
        print("Window Geometry changed")
        print(window.get_name())
        gdkwindow = gtk.gdk.window_foreign_new(window.get_xid())
        if window.is_fullscreen():
            print("window is fullscreen")
            window.set_fullscreen(0)
            window.maximize()
            gdkwindow.set_decorations(0)
        elif window.is_maximized():
            print("window maximized")
            gdkwindow.set_decorations(0)
            #window.set_fullscreen(1)
        elif not window.is_maximized():
            print("window not maximized")
            #gdkwindow.set_decorations(1)

    def on_window_closed(self,screen,window):
        print("Closed Window %s:"%(window.get_name()))
        if window in self.windows.itervalues():
            WindowKey = [key for key, value in self.windows.iteritems() if value == window][0]
            print WindowKey
            self.windows[WindowKey] = None
