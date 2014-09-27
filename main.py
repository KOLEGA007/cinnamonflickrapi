#!/usr/bin/python

import sys
sys.path.append('/usr/lib/cinnamon-settings/bin')
from SettingsWidgets import *
import os
from flickrapi import FlickrApi
from subprocess import Popen
from os.path import expanduser
from gi.repository import Gio, Gtk, GObject, Gdk, Pango, GLib
import dbus
import imtools
import gettext
import subprocess
import tempfile
import commands

flickr = Gtk.Dialog()
flickr.set_title(_("Add Flickr Source"))
flickr.value = Gtk.Entry()
flickr.label = Gtk.Label(_("Author's url: "))
flickr.box = Gtk.HBox()
flickr.box.pack_start(flickr.label, False, 0, 5,)
flickr.box.pack_start(flickr.value, False, 0, 5,)
flickr.get_content_area().pack_start(flickr.box, False, 0 ,5)
flickr.show_all()
flickr.add_buttons(Gtk.STOCK_OK, Gtk.ResponseType.OK, Gtk.STOCK_CLOSE, Gtk.ResponseType.CLOSE)
res = flickr.run()
if res == Gtk.ResponseType.OK:
    user = FlickrApi.get_user_from_url(flickr.value.get_text())
    if user is not None:
        Popen(["./flickrapi.py", 'author', 'photos', user['user_id']])
        path = FlickrApi.path + FlickrApi.service + "/" + user['user_name']
    else:
        print("User not found!")
    flickr.hide()                
else:
    flickr.hide()         
    print ("ERROR")   
