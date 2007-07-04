# tab.py -- floating windows
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

from Xlib import X, Xatom
from plwm import wmevents
from cycle import Cycle
import frame

class Tabs:
    def __init__( self, frame ):
        log.debug( "Tabs.__init__" )
        self.tabs = []
        self.frame = frame

    def _current_index( self ):
        log.debug( "tabs._current_index" )
        for index in range( len( self.tabs ) ):
            if self.tabs[index].active:
                return index

        return len( self.tabs ) -1
        

    # stew: you know better then to have both of these functions
    # looking so similar, please refactor, thanks -stew
    def next( self ):
        log.debug( "Tabs.next" )
        if len( self.tabs ):
            i = self._current_index()
            current_tab = self.tabs[ i ]
            i = (i + 1) % len( self.tabs )
            self.tabs[ i ].activate_client()
        
    def prev( self ):
        log.debug( "Tabs.prev" )
        if len( self.tabs ):
            i = self._current_index()
            current_tab = self.tabs[ i ]
            i = (i - 1) % len( self.tabs )
            self.tabs[ i ].activate_client()
        
    def append( self, tab ):
        log.debug( "Tabs.append" )
        self.tabs.insert( self._current_index()+1, tab )
        self.resize_tabs()

    def remove( self, tab ):
        log.debug( "Tabs.remove" )
        self.tabs.remove( tab )
        self.resize_tabs()
        
    def remove_all( self ):
        log.debug( "Tabs.remove_all" )
        for tab in self.tabs:
            tab.destroy()
        self.tabs = []
        
    def tab_redraw( self ):
        log.debug( "Tabs.tab_redraw" )
        for tab in self.tabs:
            tab.tab_draw()

    def show( self ):
        log.debug( "Tabs.show" )
        for tab in self.tabs:
            tab.show()

        self.resize_tabs()

    def hide( self ):
        log.debug( "Tabs.hide" )
        for tab in self.tabs:
            tab.hide()

    def _tab_width( self ):
        log.debug( "Tabs._tab_width" )
        if len( self.tabs ):
            return (self.frame.width-( (len( self.tabs ) -1) * 2 ))/ len( self.tabs )
        else:
            return 0

    def resize_tabs( self ):
        log.debug( "Tabs.resize_tabs" )
        width = self._tab_width()
        x = self.frame.x
        for tab in self.tabs:
            tab.resize_tab( x, width )
            x += width+2

# Client mixin
class TabClient:
    def __client_init__(self):
        log.debug( "TabClient.__client_init__" )
        pass

    def tab_manage( self ):
        log.debug( "tab_manage" )
	self.dispatch.add_handler(X.PropertyNotify, self.modefocusedtitle_property_notify)
        self.dispatch.add_handler(wmevents.ClientFocusIn, self.tab_get_focus)
        self.dispatch.add_handler(wmevents.ClientFocusOut, self.tab_lose_focus)
        self.dispatch.add_handler(wmevents.RemoveClient, self.tab_remove)
        self.dispatch.add_handler(X.UnmapNotify, self.tab_remove)
        self.dispatch.add_handler(X.DestroyNotify, self.tab_remove)
        self.dispatch.add_handler(wmevents.RemoveClient, self.tab_remove)


    def tab_unmanage( self ):
        log.debug( "tab_unmanage" )

	self.dispatch.remove_handler( self.modefocusedtitle_property_notify)
        self.dispatch.remove_handler( self.tab_get_focus)
        self.dispatch.remove_handler( self.tab_lose_focus)
        self.dispatch.remove_handler( self.tab_remove)


    def modefocusedtitle_property_notify(self, event):
        log.debug( "TabClient.modefocusedtitle_property_notify" )

	if self.current and event.atom == Xatom.WM_NAME:
            try:
                self.tab.set_text( self.get_title())
            except:
                # should probably figure this one out
                pass

    def tab_get_focus(self, event):
        log.debug( "TabClient.tab_get_focus" )
        if isinstance( self.wm.current_frame(), frame.TabbedFrame ):
            self.tab.tab_activate()

    def tab_lose_focus(self, event):
        log.debug( "TabClient.tab_lose_focus" )
        if isinstance( self.wm.current_frame(), frame.TabbedFrame ):
            self.tab.tab_deactivate()

    def tab_remove(self, event):
        log.debug( "TabClient.tab_remove" )
        self.tab_unmanage()
        if self.tab:
            self.tab.tab_remove()


class Tab:
    def __init__( self, frame, client ):
        log.debug( "Tab.__init__" )
        self.frame = frame
        self.text = ""
        self.width = 0
        self.active = False
        self.window = None
        self.client = client
        self.tab_dragging = False
        self.hide_x = 0
        self.hide_y = 0

    def create_tab_window( self, x ):
        log.debug( "create_tab_window" )
        
        if self.width:
            window = self.frame.screen.root.create_window(
                x, self.frame.y, self.width, self.frame.screen.title_height, 0,
                X.CopyFromParent, X.InputOutput, X.CopyFromParent,
                background_pixel = self.frame.screen.title_on_bg,
                event_mask = X.ExposureMask
                )

            self.window = self.frame.screen.add_internal_window(window)
	    window.change_attributes( border_pixel = self.frame.screen.title_border_color)
            self.window.configure(border_width = 1)

            self.window.dispatch.add_handler( X.Expose, self.tab_redraw )
            self.window.dispatch.add_handler( X.ButtonPress, self.tab_mouse_down )
            window.map()
            self._tab_create_gcs( window )
        
    def hide( self ):
        log.debug( "hide" )
	(x, y, width, height, borderwidth) = self.window.geometry()
        self.hide_x = x
        self.hide_y = y
        self.window.move( -(2*self.client.workspace.screen.root_width), -(2*self.client.workspace.screen.root_height) )

    def show( self ):
        log.debug( "show" )
        # [0] is wrong here
        self.window.move( self.hide_x,self.hide_y )

    def _tab_create_gcs( self, window ):
        log.debug( "_tab_create_gcs" )
        self.on_fg_gc = window.create_gc(foreground =
                                         self.frame.screen.title_on_fg,
                                         background =
                                         self.frame.screen.title_on_bg,
                                         font =
                                         self.frame.screen.title_font)

        self.off_fg_gc = window.create_gc(foreground =
                                          self.frame.screen.title_off_fg,
                                          background =
                                          self.frame.screen.title_off_bg,
                                          font =
                                          self.frame.screen.title_font)

        self.on_bg_gc = window.create_gc( foreground =
                                          self.frame.screen.title_on_bg )
        
        self.off_bg_gc = window.create_gc(foreground =
                                          self.frame.screen.title_off_bg )


    def activate_client( self ):
        log.debug( "activate_client" )
	self.client.raisewindow()
	self.window.raisewindow()
        self.frame.wm.set_current_client( self.client )

    def tab_mouse_down( self, event ):
        log.debug( "tab_mouse_down" )
        self.tab_dragging = True
        self.window.dispatch.add_handler( X.ButtonRelease, self.tab_mouse_up ) 
        self.window.dispatch.add_handler( X.MotionNotify, self.tab_drag )        
        event.window.grab_pointer( False,
                                   X.ButtonPressMask | X.ButtonReleaseMask | X.PointerMotionMask,
                                   X.GrabModeAsync, X.GrabModeAsync, 0, 0, X.CurrentTime )
        self.activate_client()
	(x, y, width, height, borderwidth) = self.window.geometry()
        self.tab_drag_start_x = event.root_x - x
        self.tab_drag_start_y = event.root_y - y
        

    def destroy( self ):
        log.debug( "Tab.destroy" )
        self.window.destroy()

    def tab_mouse_up( self, event ):
        log.debug( "tab_mouse_up" )
        self.tab_dragging = False
        self.frame.wm.display.ungrab_pointer( X.CurrentTime )
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
        log.debug( "tab_drag" )
        if self.tab_dragging:
            self.window.move( event.root_x - self.tab_drag_start_x ,
                              event.root_y - self.tab_drag_start_y )

    def tab_remove( self ):
        log.debug( "tab_remove" )
        if self.window:
            self.window.destroy()
        self.frame.remove_tab( self )

    def tab_activate( self ):
        log.debug( "tab_activate" )
        if not self.active:
            self.active = True
            self.tab_draw()

    def tab_deactivate( self ):
        log.debug( "tab_deactivate" )
        if self.active:
            self.active = False
            self.tab_draw()

    def resize_tab( self, x, width ):
        log.debug( "resize_tab" )
        self.width = width
        if not self.window:
            self.create_tab_window( x )
        else:
            self.window.moveresize( x, self.frame.y,
                                    width, self.frame.screen.title_height)
    def set_text(self, text):
        log.debug( "set_text" )
	if text == self.text:
	    return

	self.text = text
        self.tab_undraw()
        self.tab_draw()

    def tab_draw( self ):
        log.debug( "tab_draw" )
	if not self.text:
	    return

        if self.active:
            fg_gc = self.on_fg_gc
            bg_gc = self.on_bg_gc
        else:
            fg_gc = self.off_fg_gc
            bg_gc = self.off_bg_gc
            
        self.window.fill_rectangle( bg_gc, 0, 0, self.width, self.frame.screen.title_height )
        
        # Get width
        f = fg_gc.query_text_extents(self.text)
        width = f.overall_width + 4

        width = min( width, self.width - 4 )
        x = ( self.width - width ) / 2

	self.window.draw_text( fg_gc, x, self.frame.screen.title_base, self.text )

    def tab_redraw(self, event):
        log.debug( "tab_redraw" )
        self.tab_draw()

    def tab_undraw(self):
        log.debug( "tab_undraw" )
        self.window.clear_area( width = self.width )
