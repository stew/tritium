# title.py -- floating windows
#
# Copyright 2007 Mike O'Connor <stew@vireo.org>
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

from Xlib import X,Xatom
from plwm import wmevents

import frame

class TitleScreen:

    def __screen_client_init__(self):

#         self.tab_on_fg = self.get_color_res('.tabs.on.foreground',
#                                             '.Tabs.On.Foreground',
#                                             '#ffff00')

#         self.tab_on_bg = self.get_color_res('.tabls.on.background',
# 				'.Tabs.On.Background',
# 				'#ff0000')

#         self.tab_off_fg = self.get_color_res('.tabs.off.foreground',
# 				'.Tabs.Off.Foreground',
# 				'#ffffff')

#         self.tab_off_bg = self.get_color_res('.tabs.off.background',
# 				'.Tabs.Off.Background',
# 				'#999999')

        self.tab_on_fg = self.get_color( "#000000" )
        self.tab_on_bg = self.get_color( "#999999" )
        self.tab_off_fg = self.get_color( "#ffffff" )
        self.tab_off_bg = self.get_color( "#333333" )
        self.tab_border_color = self.get_color( "#ffffff" )

        self.tab_font = self.wm.get_font_res('.tabs.font',
                                             '.Tabs.Font',
                                             'fixed' )

	fq = self.tab_font.query()
	font_center = (fq.font_ascent + fq.font_descent) / 2 - fq.font_descent
	self.tab_height = fq.font_ascent + fq.font_descent + 6
	self.tab_base = self.tab_height / 2 + font_center

class TabScreen:
    def __screen_client_init__(self):

#         self.tab_on_fg = self.get_color_res('.tabs.on.foreground',
#                                             '.Tabs.On.Foreground',
#                                             '#ffff00')

#         self.tab_on_bg = self.get_color_res('.tabls.on.background',
# 				'.Tabs.On.Background',
# 				'#ff0000')

#         self.tab_off_fg = self.get_color_res('.tabs.off.foreground',
# 				'.Tabs.Off.Foreground',
# 				'#ffffff')

#         self.tab_off_bg = self.get_color_res('.tabs.off.background',
# 				'.Tabs.Off.Background',
# 				'#999999')

        self.tab_on_fg = self.get_color( "#000000" )
        self.tab_on_bg = self.get_color( "#999999" )
        self.tab_off_fg = self.get_color( "#ffffff" )
        self.tab_off_bg = self.get_color( "#333333" )
        self.tab_border_color = self.get_color( "#ffffff" )

        self.tab_font = self.wm.get_font_res('.tabs.font',
                                             '.Tabs.Font',
                                             'fixed' )

	fq = self.tab_font.query()
	font_center = (fq.font_ascent + fq.font_descent) / 2 - fq.font_descent
	self.tab_height = fq.font_ascent + fq.font_descent + 6
	self.tab_base = self.tab_height / 2 + font_center


# Client mixin
class TitleClient:
    def __client_init__(self):
	self.dispatch.add_handler(X.PropertyNotify, self.modefocusedtitle_property_notify)
        self.dispatch.add_handler(wmevents.ClientFocusIn, self.tab_get_focus)
        self.dispatch.add_handler(wmevents.ClientFocusOut, self.tab_lose_focus)
        self.dispatch.add_handler(wmevents.RemoveClient, self.tab_remove)
        self.dispatch.add_handler(X.UnmapNotify, self.tab_remove)
        self.dispatch.add_handler(X.DestroyNotify, self.tab_remove)

    def modefocusedtitle_property_notify(self, event):
	if self.current and event.atom == Xatom.WM_NAME:
            try:
                self.tab.set_text( self.get_title())
            except:
                # should probably figure this one out
                pass

    def tab_get_focus(self, event):
        if isinstance( self.wm.current_frame(), frame.TabbedFrame ):
            self.tab.tab_activate()

    def tab_lose_focus(self, event):
        if isinstance( self.wm.current_frame(), frame.TabbedFrame ):
            self.tab.tab_deactivate()

    def tab_remove(self, event):
        if isinstance( self.wm.current_frame(), frame.TabbedFrame ):
            self.tab.tab_remove()

class Tab:
    def __init__( self, frame, client ):
        self.frame = frame
        self.text = ""
        self.width = 0
        self.active = False
        self.window = None
        self.client = client
        self.tab_dragging = False
        self.titlebar_dragging = False
        self.hide_x = 0
        self.hide_y = 0

    def create_tab_window( self, x ):
        
        if self.width:
            window = self.frame.screen.root.create_window(
                x, self.frame.y, self.width, self.frame.screen.tab_height, 0,
                X.CopyFromParent, X.InputOutput, X.CopyFromParent,
                background_pixel = self.frame.screen.tab_on_bg,
                event_mask = X.ExposureMask
                )

            self.window = self.frame.screen.add_internal_window(window)
	    window.change_attributes( border_pixel = self.frame.screen.tab_border_color)
            self.window.configure(border_width = 1)

            self.window.dispatch.add_handler( X.Expose, self.redraw )
            self.window.dispatch.add_handler( X.ButtonRelease, self.tab_mouse_up ) 
            self.window.dispatch.add_handler( X.ButtonPress, self.tab_mouse_down )
            self.window.dispatch.add_handler( X.MotionNotify, self.tab_drag )        
            window.map()
            self._create_gcs( window )
        
    def hide( self ):
	(x, y, width, height, borderwidth) = self.window.geometry()
        self.hide_x = x
        self.hide_y = y
        self.window.move( -(2*self.client.workspace.screen.root_width), -(2*self.client.workspace.screen.root_height) )

    def show( self ):
        # [0] is wrong here
        self.window.move( self.hide_x,self.hide_y )

    def create_title_window( self ):
        
	(x, y, width, height, borderwidth) = self.client.geometry()
        y -= (self.frame.screen.tab_height + 1)
        height = self.frame.screen.tab_height
        self.width = width

        if self.width:
            window = self.frame.screen.root.create_window(
                x, y, width, height, 0,
                X.CopyFromParent, X.InputOutput, X.CopyFromParent,
                background_pixel = self.frame.screen.tab_on_bg,
                event_mask = X.ExposureMask
                )

            self.window = self.frame.screen.add_internal_window(window)
	    window.change_attributes( border_pixel = self.frame.screen.tab_border_color)
            self.window.configure(border_width = 1)

            self.window.dispatch.add_handler( X.Expose, self.redraw )
            self.window.dispatch.add_handler( X.ButtonRelease, self.titlebar_mouse_up ) 
            self.window.dispatch.add_handler( X.ButtonPress, self.titlebar_mouse_down )
            self.window.dispatch.add_handler( X.MotionNotify, self.titlebar_drag )        
            window.map()
            self._create_gcs( window )

    def _create_gcs( self, window ):
        self.on_fg_gc = window.create_gc(foreground =
                                         self.frame.screen.tab_on_fg,
                                         background =
                                         self.frame.screen.tab_on_bg,
                                         font =
                                         self.frame.screen.tab_font)

        self.off_fg_gc = window.create_gc(foreground =
                                          self.frame.screen.tab_off_fg,
                                          background =
                                          self.frame.screen.tab_off_bg,
                                          font =
                                          self.frame.screen.tab_font)

        self.on_bg_gc = window.create_gc( foreground =
                                          self.frame.screen.tab_on_bg )
        
        self.off_bg_gc = window.create_gc(foreground =
                                          self.frame.screen.tab_off_bg )

    def tab_mouse_down( self, event ):
        self.tab_dragging = True
	self.client.raisewindow()
	self.window.raisewindow()
        self.frame.wm.set_current_client( self.client )
	(x, y, width, height, borderwidth) = self.window.geometry()
        self.tab_drag_start_x = event.root_x - x
        self.tab_drag_start_y = event.root_y - y

    def destroy( self ):
        self.window.destroy()

    def tab_mouse_up( self, event ):
        self.tab_dragging = False
        f = self.frame.wm.workspaces.current().find_frame( event.root_x, event.root_y )
        if f and (f != self.frame):
            if isinstance( f, frame.TabbedFrame ):
                self.frame.remove( self.client )
                self.frame.remove_tab( self )
                self.client.add_to_frame( f )
                self.window.destroy()
            else:
                f = self.frame

        if f:
            f.tabs.resize_tabs()
        else:
            self.frame.tabs.resize_tabs()
        
    def tab_drag( self, event ):
        if self.tab_dragging:
            self.window.move( event.root_x - self.tab_drag_start_x ,
                              event.root_y - self.tab_drag_start_y )


    def titlebar_mouse_down( self, event ):
        self.titlebar_dragging = True
	#self.client.raisewindow()
#	self.window.raisewindow()
        self.frame.wm.set_current_client( self.client )
	(x, y, width, height, borderwidth) = self.window.geometry()
        self.tab_drag_start_x = event.root_x - x
        self.tab_drag_start_y = event.root_y - y

    def titlebar_mouse_up( self, event ):
        self.titlebar_dragging = False

    def titlebar_drag( self, event ):
        if self.titlebar_dragging:
            self.window.move( event.root_x - self.tab_drag_start_x ,
                              event.root_y - self.tab_drag_start_y )

            self.client.move( event.root_x - self.tab_drag_start_x ,
                              event.root_y - self.tab_drag_start_y )

    def tab_remove( self ):
        if self.window:
            self.window.unmap()
        self.frame.remove_tab( self )

    def tab_activate( self ):
        if not self.active:
            self.active = True
            self.draw()

    def tab_deactivate( self ):
        if self.active:
            self.active = False
            self.draw()

    def resize_tab( self, x, width ):
        self.width = width
        if not self.window:
            self.create_tab_window( x )
        else:
            self.window.moveresize( x, self.frame.y,
                                    width, self.frame.screen.tab_height)

    def resize_title( self ):
        if not self.window:
            self.create_title_window( )
        else:
            (x, y, width, height, borderwidth) = self.client.geometry()
            y -= (self.frame.screen.tab_height + 1)
            height = self.frame.screen.tab_height
            self.width = width
            self.window.moveresize( x,y, width, height )

    def set_text(self, text):
	if text == self.text:
	    return

	self.text = text
        self.undraw()
        self.draw()

    def draw( self ):
	if not self.text:
	    return

        if self.active:
            fg_gc = self.on_fg_gc
            bg_gc = self.on_bg_gc
        else:
            fg_gc = self.off_fg_gc
            bg_gc = self.off_bg_gc
            
        self.window.fill_rectangle( bg_gc, 0, 0, self.width, self.frame.screen.tab_height )
        
        # Get width
        f = fg_gc.query_text_extents(self.text)
        width = f.overall_width + 4

        width = min( width, self.width - 4 )
        x = ( self.width - width ) / 2

	self.window.draw_text( fg_gc, x, self.frame.screen.tab_base, self.text )

    def redraw(self, event):
        self.draw()

    def undraw(self):
        self.window.clear_area( width = self.width )
