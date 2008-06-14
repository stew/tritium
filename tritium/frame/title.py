# title.py -- floating windows with titlebars
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

from Xlib import X,Xatom
from plwm import wmevents

import frame

class TitleScreen:

    def __screen_client_init__(self):

# I have these resource based methods turned off for now becuase I
# don't like the fact that they pickup the generic '*foreground' and
# '*background' making your tabs come up with the same colors as other
# windows by default.

#         self.title_on_fg = self.get_color_res('.tabs.on.foreground',
#                                             '.Tabs.On.Foreground',
#                                             '#ffff00')

#         self.title_on_bg = self.get_color_res('.tabls.on.background',
# 				'.Tabs.On.Background',
# 				'#ff0000')

#         self.title_off_fg = self.get_color_res('.tabs.off.foreground',
# 				'.Tabs.Off.Foreground',
# 				'#ffffff')

#         self.title_off_bg = self.get_color_res('.tabs.off.background',
# 				'.Tabs.Off.Background',
# 				'#999999')

        self.title_on_fg = self.get_color( "#000000" )
        self.title_on_bg = self.get_color( "#999999" )
        self.title_off_fg = self.get_color( "#ffffff" )
        self.title_off_bg = self.get_color( "#333333" )
        self.title_border_color = self.get_color( "#ffffff" )

        self.title_font = self.wm.get_font_res('.tabs.font',
                                             '.Tabs.Font',
                                             'fixed' )

	fq = self.title_font.query()
	font_center = (fq.font_ascent + fq.font_descent) / 2 - fq.font_descent
	self.title_height = fq.font_ascent + fq.font_descent + 6
	self.title_base = self.title_height / 2 + font_center

# Client mixin
class TitleClient:
    """
    This class is a client mixing for floating windows which have a titlebar.
    It will create a new top level window to contain both the client
    window and a titlebar window

    """
    
    def __client_init__(self):
        log.debug( "TitleClient.__client_init__" )

        self.titlebar_moving = False
        self.titlebar_resizing = False

    def title_manage(self):
        """
        reparent a window into a frame with a titlebar decoration
        """
        log.debug( "title_manage" )
        (x, y, width, height, borderwidth) = self.geometry()
        
        # the decoration window is the parent of both the client window and the titlebar
        decoration_window = self.wm.current_frame().screen.root.create_window(
            max( 30, x-borderwidth), max(30, y - borderwidth - self.wm.current_frame().screen.title_height),
            width+(2*borderwidth), self.wm.current_frame().screen.title_height + height + (2*borderwidth), 0,
            X.CopyFromParent, X.InputOutput, X.CopyFromParent,
            background_pixmap = X.ParentRelative,
            event_mask = X.ButtonPressMask | X.ButtonReleaseMask | X.PointerMotionMask | X.ExposureMask
            )
        decoration_window.map()

        # the title_window is the titlebar
        title_window = decoration_window.create_window(
            borderwidth, borderwidth,
            width, self.wm.current_frame().screen.title_height, 1,
            X.CopyFromParent, X.InputOutput, X.CopyFromParent,
            background_pixel = self.wm.current_frame().screen.title_on_bg,
            event_mask = X.ExposureMask
            )

        self._title_create_gcs( title_window )
        self.decoration_window = self.wm.current_frame().screen.add_internal_window( decoration_window )

        decoration_window.change_attributes( border_pixel = self.wm.current_frame().screen.title_border_color)
        decoration_window.configure( border_width = 1 )

        title_window = decoration_window.create_window(
            borderwidth, borderwidth, width, self.wm.current_frame().screen.title_height, 0,
            X.CopyFromParent, X.InputOutput, X.CopyFromParent,
            background_pixel = self.frame.screen.title_on_bg,
            event_mask = X.ExposureMask
            )

        self.window.reparent( decoration_window, borderwidth, self.wm.current_frame().screen.title_height+(2*borderwidth) )
        title_window.reparent( decoration_window, borderwidth, borderwidth );
        self.title_window = self.frame.screen.add_internal_window(title_window)
        self.active = False
        self.title_window.map()
        self.title_text=self.get_title()
        self.title_window.raisewindow()

        self.title_window.dispatch.add_handler( X.ButtonPress, self.titlebar_mouse_down )
        self.title_window.dispatch.add_handler( X.MotionNotify, self.titlebar_drag )
        self.title_window.dispatch.add_handler( X.ButtonRelease, self.titlebar_mouse_up )

	self.dispatch.add_handler( X.PropertyNotify, self.title_property_notify )

        self.title_window.dispatch.add_handler( X.Expose, self.title_redraw )
        self.decoration_window.dispatch.add_handler( wmevents.ClientFocusIn, self.title_get_focus )
        self.decoration_window.dispatch.add_handler( wmevents.ClientFocusOut, self.title_lose_focus )

#        self.window.grab_button( 1, X.Mod1Mask, True, X.ButtonPressMask, X.GrabModeAsync, X.GrabModeAsync, 0, 0 )
#        self.window.grab_button( 3, X.Mod1Mask, True, X.ButtonPressMask, X.GrabModeAsync, X.GrabModeAsync, 0, 0 )

        # ugh, these two shouldn't be needed
        decoration_window.grab_button( 1, X.Mod1Mask, True, X.ButtonPressMask, X.GrabModeAsync, X.GrabModeAsync, 0, 0 )
        decoration_window.grab_button( 3, X.Mod1Mask, True, X.ButtonPressMask, X.GrabModeAsync, X.GrabModeAsync, 0, 0 )

        self.dispatch.add_handler(X.UnmapNotify, self.title_unmap)

        self.decoration_window.dispatch.add_handler( X.ButtonRelease, self.titlebar_mouse_up )
        self.decoration_window.dispatch.add_handler( X.ButtonPress, self.titlebar_mouse_down )
        self.decoration_window.dispatch.add_handler( X.MotionNotify, self.titlebar_drag )

        self.title_draw()

    def title_unmap( self, event ):
        self.title_unmanage()

    def title_unmanage(self):
        """
        reparent the managed client back to the root window, get rid
        of the decoration window
        """
        log.debug( "TitleClient.title_unmanage" )
        self.decoration_window.dispatch.remove_handler( self.titlebar_mouse_up )
        self.decoration_window.dispatch.remove_handler( self.titlebar_mouse_down )
        self.decoration_window.dispatch.remove_handler( self.titlebar_drag )

        self.dispatch.remove_handler( self.titlebar_mouse_up )
        self.dispatch.remove_handler( self.titlebar_mouse_down )
        self.dispatch.remove_handler( self.titlebar_drag )

	self.dispatch.remove_handler( self.title_property_notify )
        self.dispatch.remove_handler( self.title_remove )
        self.dispatch.remove_handler( self.title_remove )

        self.title_window.dispatch.remove_handler( self.title_redraw )
        self.decoration_window.dispatch.remove_handler( self.title_get_focus )
        self.decoration_window.dispatch.remove_handler( self.title_lose_focus )

	(x, y, width, height, borderwidth) = self.decoration_window.geometry()
        self.window.reparent( self.workspace.screen.root, x, y )

        self.title_window.unmap()
        self.title_window.destroy()
        self.title_window = None

        self.decoration_window.unmap()
        self.decoration_window.destroy()
        self.decoration_window = None
        

    def title_property_notify(self, event):
        log.debug( "TitleClient.modefocusedtitle_property_notify" )
	if self.current and event.atom == Xatom.WM_NAME:
            try:
                self.set_text( self.get_title())
            except:
                pass

    def title_get_focus(self, event):
        log.debug( "TitleClient.title_get_focus" )
        self.active = True
        self.title_draw()

    def title_lose_focus(self, event):
        log.debug( "TitleClient.title_lose_focus" )
        self.active = False
        self.title_draw()

    def title_remove(self, event):
        log.debug( "TitleClient.title_remove" )
        self.title_window.unmap()

    def title_hide( self ):
        log.debug( "TitleClient.title_hide" )
	(x, y, width, height, borderwidth) = self.decoration_window.geometry()
        self.hide_x = x
        self.hide_y = y
        self.decoration_window.move( -(2*self.workspace.screen.root_width), -(2*self.workspace.screen.root_height) )

    def title_show( self ):
        log.debug( "TitleClient.title_show" )
        self.decoration_window.move( self.hide_x,self.hide_y )


    def _title_create_gcs( self, window ):
        log.debug( "TitleClient._title_create_gcs" )
        self.title_on_fg_gc = window.create_gc(foreground =
                                         self.wm.current_frame().screen.title_on_fg,
                                         background =
                                         self.wm.current_frame().screen.title_on_bg,
                                         font =
                                         self.wm.current_frame().screen.title_font)

        self.title_off_fg_gc = window.create_gc(foreground =
                                          self.wm.current_frame().screen.title_off_fg,
                                          background =
                                          self.wm.current_frame().screen.title_off_bg,
                                          font =
                                          self.wm.current_frame().screen.title_font)

        self.title_on_bg_gc = window.create_gc( foreground =
                                          self.wm.current_frame().screen.title_on_bg )
        
        self.title_off_bg_gc = window.create_gc(foreground =
                                          self.wm.current_frame().screen.title_off_bg )


    def activate_client( self ):
        log.debug( "TitleClient.activate_client" )
	self.decoration_window.raisewindow()
        self.workspace.raisewindows() # raise the "alwaysontop" windows
        self.wm.current_frame().wm.set_current_client( self )
        
    def destroy( self ):
        log.debug( "TitleClient.destroy" )
        self.decoration_window.destroy()

    def titlebar_mouse_down( self, event ):
        log.debug( "TitleClient.titlebar_mouse_down" )
        ( x, y, width, height, borderwidth) = self.decoration_window.geometry();


        if event.root_y > ( y + self.screen.title_height + (2 * borderwidth) ):

            if ( event.detail == 1 ) and ( event.state & X.Mod1Mask ):
                self.start_move( event )

            elif ( event.detail == 3 ) and ( event.state & X.Mod1Mask ):
                self.start_resize( event )

        else:
            if ( event.detail == 3 ) and ( event.state & X.Mod1Mask ):
                self.start_resize( event )
            else:
                self.start_move( event )


    def start_move( self, event ):
        log.debug( "TitleClient.start_move" )
        event.window.grab_pointer( False,
                                   X.ButtonPressMask | X.ButtonReleaseMask | X.PointerMotionMask | X.LeaveWindowMask,
                                   X.GrabModeAsync, X.GrabModeAsync, 0, 0, X.CurrentTime )
        self.titlebar_moving = True
        self.titlebar_resizing = False
        self.workspace.raisewindows() # raise the "alwaysontop" windows
        self.wm.current_frame().wm.set_current_client( self )
        (x, y, width, height, borderwidth) = self.decoration_window.geometry()
        self.tab_drag_start_x = event.root_x - x
        self.tab_drag_start_y = event.root_y - y

    # need to make the resizing smarter so it knows which corner we
    # are nearest and anchor the opposite corner instead of always
    # anchoring the top-left
    def start_resize( self, event ):
        log.debug( "TitleClient.start_resize" )

        event.window.grab_pointer( False,
                                   X.ButtonPressMask | X.ButtonReleaseMask | X.PointerMotionMask | X.LeaveWindowMask,
                                   X.GrabModeAsync, X.GrabModeAsync, 0, 0, X.CurrentTime )
        self.titlebar_moving = False
        self.titlebar_resizing = True
        self.decoration_window.raisewindow()
        self.workspace.raisewindows() # raise the "alwaysontop" windows
        self.wm.current_frame().wm.set_current_client( self )
        (x, y, width, height, borderwidth) = self.decoration_window.geometry()
        self.tab_drag_start_x = x
        self.tab_drag_start_y = y
        self.title_resize_start_x = width - event.root_x
        self.title_resize_start_y = height - event.root_y

    def titlebar_mouse_up( self, event ):
        log.debug( "TitleClient.titlebar_mouse_up" )
        if self.titlebar_moving:
            self.titlebar_moving = False
            self.wm.display.ungrab_pointer( X.CurrentTime )
        elif self.titlebar_resizing:
            self.titlebar_resizing = False
            self.wm.display.ungrab_pointer( X.CurrentTime )
#        else:
#            event.window.send_event( event );

    def titlebar_drag( self, event ):
        log.debug( "TitleClient.titlebar_drag" )
        if self.titlebar_moving:
            self.decoration_window.move( event.root_x - self.tab_drag_start_x ,
                                         event.root_y - self.tab_drag_start_y )
        elif self.titlebar_resizing:
            width = max( 0, event.root_x + self.title_resize_start_x )
            height = max( (self.screen.title_height + ( 2 ) ),
                          ( event.root_y + self.title_resize_start_y ) )

            self.decoration_window.moveresize( self.tab_drag_start_x, self.tab_drag_start_y,
                                               width, height )

            self.moveresize( 1, self.screen.title_height+2,
                             width-2, height-self.screen.title_height )

            self.title_window.moveresize( 1, 1,
                                          width-2, self.screen.title_height )

    def set_text(self, text):
        log.debug( "TitleClient.set_text" )
	if text == self.title_text:
	    return

        self.title_undraw()
	self.title_text = text
        self.title_draw()

    def title_draw( self ):
        log.debug( "TitleClient.title_draw" )
	(x, y, wwidth, height, borderwidth) = self.title_window.geometry()
	if not self.title_text:
	    return

        if self.active:
            fg_gc = self.title_on_fg_gc
            bg_gc = self.title_on_bg_gc
        else:
            fg_gc = self.title_off_fg_gc
            bg_gc = self.title_off_bg_gc
            
        self.title_window.fill_rectangle( bg_gc, 0, 0, wwidth, self.wm.current_frame().screen.title_height )
        
        # Get width
        f = fg_gc.query_text_extents(self.title_text)
        width = f.overall_width + 4

        width = min( width, wwidth - 4 )
        x = ( wwidth - width ) / 2

	self.title_window.draw_text( fg_gc, x, self.wm.current_frame().screen.title_base, self.title_text )

    def title_redraw(self, event):
        log.debug( "TitleClient.title_redraw" )
        self.title_draw()

    def title_undraw(self):
        log.debug( "TitleClient.title_undraw" )
	(x, y, width, height, borderwidth) = self.title_window.geometry()
        self.title_window.clear_area( width = width, height = height )


def _test():
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    _test()
    print "DONE"
