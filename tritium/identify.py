# identify.py -- show the user info about the current window
#
# Copyright 2007,2008 Mike O'Connor <stew@vireo.org>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

import logging
log = logging.getLogger()

from Xlib import X, Xatom
from Xlib.keysymdef import latin1
from plwm import wmanager, event, keys
from submap import SubMap
import threading

class IdentifyWindow:
    """
    A window to display properties about a client
    """
    fontname= "9x15"
    foreground = "black"
    background = "white"
    borderwidth = 3
    bordercolor = "black"

    def __init__( self, client, time ):
        screen = client.screen
        appname,appclass = client.window.get_wm_class()
        self.strings = [ "Title: %s" % client.get_title(),
                         "Application Name: %s" % appname,
                         "Class: %s" % appclass ]

        fg = screen.get_color( self.foreground )
        bg = screen.get_color( self.background )
        bc = screen.get_color( self.bordercolor )
        font = screen.wm.get_font( self.fontname, 'fixed' )
        self.size = font.query()
        self.height = (self.size.font_ascent + self.size.font_descent + 1) * len( self.strings )
        self.width = 0
        for string in self.strings:
            self.width = max( self.width, font.query_text_extents( string ).overall_width )

        window = screen.root.create_window(0, 0, self.width, self.height,
                                           self.borderwidth,
                                           X.CopyFromParent, X.InputOutput,
                                           X.CopyFromParent,
                                           background_pixel = bg,
                                           border_pixel = bc,
                                           event_mask = (X.VisibilityChangeMask |
                                                         X.ExposureMask))

        self.gc = window.create_gc(font = font, function = X.GXinvert,
                                   foreground = fg, background = bg)

        self.font = font
        self.window = screen.add_internal_window(window)
        self.window.dispatch.add_handler(X.VisibilityNotify, self.raisewindow)
        self.window.dispatch.add_handler(X.Expose, self.redraw)

        (x,y,width,height,borderwidth) = client.geometry()

        x, y, width, height = self.window.keep_on_screen( x, y, self.width, self.height )
        self.window.configure( x = x, y = y, width = self.width, height = self.height )
        self.window.map()

        threading.Timer( 5, self.done ).start()

    def raisewindow( self, event ):
        self.window.raisewindow()

    def redraw( self, event = None ):
        self.window.clear_area( width = self.width, height = self.height )

        baseline = self.size.font_ascent + 1
        for string in self.strings:
            self.window.image_text( self.gc, 0, baseline, string )
            baseline += self.size.font_ascent + 1 + self.size.font_descent
            
    def done( self ):
        log.debug( "Identify.done" )
        self.window.destroy()
