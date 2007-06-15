# frame.py -- a container for clients
#
# Copyright 2007 Mike O'Connor <stew@vireo.org>
#
# Portions of code plagarized from plwm's panes.py which is
#    Copyright (C) 2001  Mike Meyer <mwm@mired.org>
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

"""
A frame is a container for multiple clients or sub-frames, it might be
floating, it might be fullscreen.
"""
from Xlib import X, Xutil, Xatom
from plwm import wmanager, wmevents, modewindow, cfilter
from cycle import Cycle
from tabs import Tabs
from title import Tab
import logging
log = logging.getLogger()

class FrameClient:
    """
    mixin for client windows that are contained in frames
    """
    def __client_init__( self ):
        self.frame_dragging = False
        frame = self.wm.current_frame()

        if frame.screen != self.screen:
            frame = self.wm.current_frame()
            while frame and frame.screen != self.screen:
                frame = frame.next_frame()

        self.add_to_frame( frame )

        self.dispatch.add_handler(X.MapNotify, self.frame_map)
        self.dispatch.add_handler(X.UnmapNotify, self.frame_unmap)
        self.dispatch.add_handler(X.DestroyNotify, self.frame_unmap)
        self.dispatch.add_handler(wmevents.RemoveClient, self.frame_unmap)
        self.dispatch.add_handler(wmevents.ClientFocusIn, self.frame_get_focus)

        if isinstance( frame, FloatingFrame ):
            self.dispatch.add_system_handler( X.ButtonPress, self.frame_client_mouse_down )
            self.dispatch.add_handler( X.ButtonRelease, self.frame_client_mouse_up ) 
            self.dispatch.add_handler( X.MotionNotify, self.frame_client_drag )

    def frame_map( self, event ):
        self.dispatch.add_system_handler( X.ButtonPress, self.frame_client_mouse_down )
        
    def frame_unmap( self, event ):
        log.debug( "STUSTUSTU: unmap: %s" %event )
        self.frame.remove( self )
        self.frame = None

    def frame_get_focus( self, event ):
        self.wm.workspaces.current().current_frame = self.frame

    def add_to_frame( self, frame ):
        self.frame = frame
        frame.append( self )

    def frame_client_mouse_down( self, event ):
        log.debug( "frame_client_mouse_down: %s" %event )
        if (event.detail == 1) and (event.state & X.Mod1Mask):
            log.debug( "my event: %s" % event )
            self.frame_dragging = True
            (x, y, width, height, borderwidth) = self.geometry()
            self.frame_drag_start_x = event.root_x - x
            self.frame_drag_start_y = event.root_y - y
        else:
            log.debug( "not my event: %s" % event )

    def frame_client_mouse_up( self, event ):
        log.debug( "frame_client_mouse_up: %s" %event )
        if event.detail == 1:
            self.frame_dragging = False

    def frame_client_drag( self, event ):
        if self.frame_dragging:
            log.debug( "frame_client_drag: event: %s" % (event) )
            self.move( event.root_x - self.frame_drag_start_x ,
                       event.root_y - self.frame_drag_start_y )


    # these functions are all hacky
    def move_left( self ):
        new_frame = self.frame.parent_frame.find_frame_left( self.frame )
        if new_frame and self.frame != new_frame:
            self.frame.remove( self )
            if( self.tab ):
                self.frame.remove_tab( self.tab )
            self.frame = new_frame
            self.frame.append( self )
           
    def move_right( self ):
        new_frame = self.frame.parent_frame.find_frame_right( self.frame )
        if new_frame and self.frame != new_frame:
            self.frame.remove( self )
            if( self.tab ):
                self.frame.remove_tab( self.tab )
            self.frame = new_frame
            self.frame.append( self )
            
    def move_up( self ):
        new_frame = self.frame.parent_frame.find_frame_above( self.frame )
        if new_frame and self.frame != new_frame:
            self.frame.remove( self )
            if( self.tab ):
                self.frame.remove_tab( self.tab )
            self.frame = new_frame
            self.frame.append( self )

    def move_down( self):
        new_frame = self.frame.parent_frame.find_frame_below( self.frame )
        if new_frame and self.frame != new_frame:
            self.frame.remove( self )
            if( self.tab ):
                self.frame.remove_tab( self.tab )
            self.frame = new_frame
            self.frame.append( self )

class Frame:
    """
    a container for [fullscreen] windows
    """
    def __init__( self, screen, x, y, width, height ):
        self.screen = screen
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.wm = screen.wm
        self.shown = True
        self.parent_frame = None
        self.windows = Cycle()

    def find_frame( self, x, y ):
        if ( self.x <= x ) and \
           ( self.y <= y ) and \
           ((self.x+self.width) >= x ) and \
           ((self.y+self.height) >= y):
            return self
    
    def append( self, window ):
        self.place_window( window  )
        self.deactivate()
        self.windows.insert_after_current( window )
        self.activate()

    def remove( self, window ):
        log.debug( "removing window: %s from frame %s" % (window,self))
        cur = self.windows.current()
        self.windows.remove( window )
        if cur == window:
            self.deactivate()
            if self.wm.current_frame() == self:
                self.windows.prev()
                self.activate()

    def next( self ):
        "Move to the next window in this pane."
        #clients = self.screen.query_clients(panefilter(self), 1)
        self.deactivate()
        self.windows.next()
        self.activate()

    def prev( self ):
        "Move to the next window in this pane."
        #clients = self.screen.query_clients(panefilter(self), 1)
        self.deactivate()
        self.windows.prev()
        self.activate()

    def set_current( self, index ):
        "Move to the next window in this pane."
        #clients = self.screen.query_clients(panefilter(self), 1)
        self.deactivate()
        self.windows.index = index
        self.activate()

    def deactivate(self):
        if self.windows.current() and not self.windows.current().withdrawn:
            #self.windows.current().panes_pointer_pos = self.windows.current().pointer_position()
            if self.wm.current_frame() == self:
                self.wm.set_current_client( None )

    def activate(self):
        "Dummy function, reset to _activate after all windows are opened."

    def _activate(self):
        "Activate whatever is currently self.windows.current()."
        self.wm.current_screen = self.screen
        if self.windows.current() and not self.windows.current().withdrawn:
            # Will raise window and give focus
            self.windows.current().activate()
            #pos = self.windows.current().panes_pointer_pos
            #if pos:
                #self.windows.current().warppointer(pos[0], pos[1])

    def show( self ):
        if not self.shown:
            for window in self.windows:
                window.show()

            self.shown = True

    def hide( self ):
        if self.shown:
            for window in self.windows:
                window.hide()
            self.shown = False

    # dummy here.  will be overridden by TabbedFrame
    def remove_tab( self, tab ):
        pass

    def next_frame( self ):
        if self.parent_frame:
            return self.parent_frame.next_sibling_frame( self )
        else:
            return self

    def first_child_frame( self ):
        return self

class SplitFrame( Frame ):
    """
    A frame that contains two frames split either vertically or
    horizontally. 
    """
    def __init__( self, screen, x, y, width, height, vertical, frame1 ):
        Frame.__init__( self, screen, x, y, width, height )
        self.split_dragging = False
        self.vertical = vertical

        if vertical:
            self.split = height
        else:
            self.split = width
        self.split = self.split >> 1

        self.frame1 = frame1

        if vertical:
            self.frame1.moveresize( x, y, self.width, self.height - self.split )
            self.frame2 = TabbedFrame( self.screen, self.x, self.split+4,
                                       self.width, self.height-self.split-4)
        else:
            self.frame1.moveresize( x, y, self.width - self.split, self.height )
            self.frame2 = TabbedFrame( self.screen, self.split+4, self.y,
                                       self.width-self.split-4, self.height)


        frame1.parent_frame.replace_me( frame1, self )

        self.frame1.parent_frame = self.frame2.parent_frame = self
        self.frame2.activate()

        self.create_split_window()

    def moveresize( self, x, y, width, height ):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        if self.vertical:
            self.split = height >> 1
            self.window.moveresize( self.x, self.split, self.width, 4 )
            self.frame1.moveresize( self.x, self.y, self.width, self.split )
            self.frame2.moveresize( self.x, self.split+4, self.width, self.height - self.split - 4 )
        else:
            self.split = width >> 1
            self.window.moveresize( self.split, self.y, 4, self.height )
            self.frame1.moveresize( self.x, self.y, self.split, self.height )
            self.frame2.moveresize( self.split+4, self.y, self.width - self.split - 4, self.height )

        self.redraw( self )

    def find_frame_right( self, frame ):
        if not self.vertical and self.frame1 == frame:
            return self.frame2
        else:
            return self.parent_frame.find_frame_to_right( self )

    def find_frame_left( self, frame ):
        if not self.vertical and self.frame2 == frame:
            return self.frame1
        else:
            return self.parent_frame.find_frame_left( self )

    def find_frame_above( self, frame ):
        if self.vertical and self.frame2 == frame:
            return self.frame1
        else:
            return self.parent_frame.find_frame_above( self )

    def find_frame_below( self, frame ):
        if self.vertical and self.frame1 == frame:
            return self.frame2
        else:
            return self.parent_frame.find_frame_below( self )

    def find_frame( self, x, y ):
        if ( self.x <= x ) and \
           ( self.y <= y ) and \
           ((self.x+self.width) >= x ) and \
           ((self.y+self.height) >= y):

            r = self.frame1.find_frame( x, y )
            if not r:
                r = self.frame2.find_frame( x, y )
                if not r:
                    r = self

            return r

    def next_sibling_frame( self, frame ):
        if frame == self.frame1:
            return self.frame2.first_child_frame()
        else:
            return self.next_frame()

    def first_child_frame( self ):
        return self.frame1.first_child_frame()

    def create_split_window( self ):
        
        if self.vertical:
            window = self.screen.root.create_window(
                self.x, self.split, self.width, 4, 0,
                X.CopyFromParent, X.InputOutput, X.CopyFromParent,
                event_mask = X.ExposureMask
                )
        else:
            window = self.screen.root.create_window(
                self.split, self.y, 4, self.height, 0,
                X.CopyFromParent, X.InputOutput, X.CopyFromParent,
                event_mask = X.ExposureMask
                )
            
        self.window = self.screen.add_internal_window(window)

        self.window.dispatch.add_handler( X.Expose, self.redraw )
        self.window.dispatch.add_handler( X.ButtonRelease, self.splitbar_mouse_up ) 
        self.window.dispatch.add_handler( X.ButtonPress, self.splitbar_mouse_down )
        self.window.dispatch.add_handler( X.MotionNotify, self.splitbar_drag )        
        window.map()
        self._create_gcs( window )

    def _create_gcs( self, window ):
        self.split_gc1 = window.create_gc( foreground =
                                           self.screen.get_color( "#ffffff" ))

        self.split_gc2 = window.create_gc( foreground =
                                           self.screen.get_color( "#cccccc" ))

        self.split_gc3 = window.create_gc( foreground =
                                           self.screen.get_color( "#999999" ))
        
        self.split_gc4 = window.create_gc( foreground =
                                           self.screen.get_color( "#666666" ))


    def redraw( self, event = None ):
        if self.vertical:
            self.window.fill_rectangle( self.split_gc1, self.x, 0, self.width, 1 )
            self.window.fill_rectangle( self.split_gc2, self.x, 1, self.width, 1 )
            self.window.fill_rectangle( self.split_gc3, self.x, 2, self.width, 1 )
            self.window.fill_rectangle( self.split_gc4, self.x, 3, self.width, 1 )
        else:
            self.window.fill_rectangle( self.split_gc1, 0, self.y, 1, self.height )
            self.window.fill_rectangle( self.split_gc2, 1, self.y, 1, self.height )
            self.window.fill_rectangle( self.split_gc3, 2, self.y, 1, self.height )
            self.window.fill_rectangle( self.split_gc4, 3, self.y, 1, self.height )

    def splitbar_mouse_down( self, event ):
        self.split_dragging = True
        if self.vertical:
            self.splitbar_drag_start = event.root_y - self.split
        else:
            self.splitbar_drag_start = event.root_x - self.split

    def splitbar_mouse_up( self, event ):
        self.split_dragging = False
        
    def splitbar_drag( self, event ):
        if self.split_dragging:
            if self.vertical:
                self.split = event.root_y - self.splitbar_drag_start
                self.window.move( self.x, self.split )
                self.frame1.moveresize( self.x, self.y, self.width, self.split )
                self.frame2.moveresize( self.x, self.split+4, self.width, self.height - self.split - 4 )
            else:
                self.split = event.root_x - self.splitbar_drag_start
                self.window.move( self.split, self.y  )
                self.frame1.moveresize( self.x, self.y, self.split, self.height )
                self.frame2.moveresize( self.split+4, self.y, self.width - self.split - 4, self.height )

    def remove_me( self, me ):
        if self.frame1 == me:
            with = self.frame2
        else:
            with = self.frame1

        for client in me.windows:
            client.add_to_frame( with )

        self.window.destroy()
        self.parent_frame.replace_me( self, with )
        with.moveresize( self.x, self.y, self.width, self.height )

    def replace_me( self, me, with ):
        if self.frame1 == me:
            self.frame1 = with
        elif self.frame2 == me:
            self.frame2 = with

        with.parent_frame = self

    def __str__( self ):
        if self.vertical:
            return "SplitFrame(%d,%d,%d,%d): top: <" %(self.x,self.y,self.width,self.height) + str( self.frame1 ) + "> bottom: <" + str( self.frame2 ) + ">"
        else:
            return "SplitFrame(%d,%d,%d,%d): left: <" %(self.x,self.y,self.width,self.height) + str( self.frame1 ) + "> right: <" + str( self.frame2 ) + ">"
        
class FloatingFrame( Frame ):
    """
    a Frame that contains floating windows
    """
    def place_window(self, window = None):
        "Figure out where the window should be put."

        if not window: window = self.window
        width, height = window.follow_size_hints(self.width - 2 * window.border_width,
                                                 self.height - 2 * window.border_width)

        # If it doesn't fit, just force it.
        if width > self.width - 2 * window.border_width:
            width = self.width - 2 * window.border_width
        if height > self.height - ((4 * window.border_width) + self.screen.tab_height):
            height = self.height - ((4 * window.border_width) + self.screen.tab_height)

        x = self.x
        y = self.y + self.screen.tab_height + (2*window.border_width)

        x, y, width, height = window.keep_on_screen(x, y, width, height)

        window.moveresize(x, y, width, height)

    def append( self, window ):
        tab = Tab( self, window )
        window.tab = tab
        Frame.append( self, window )
        tab.resize_title()
        tab.set_text( window.get_title() )

    def __str__( self ):
        return "FloatingFrame(%d,%d,%d,%d):" %(self.x,self.y,self.width,self.height)

class TabbedFrame( Frame ):
    def __init__( self, screen, x, y, width, height ):
        Frame.__init__( self, screen, x, y, width, height )
        self.tabs = Tabs( self )

    def append( self, window ):
        tab = Tab( self, window )
        window.tab = tab
        self.tabs.append( tab )
        tab.set_text( window.get_title() )
        Frame.append( self, window )

    def moveresize( self, x, y, width, height ):
        self.x = x
        self.y = y
        self.height = height
        self.width = width
        map( self.place_window, self.windows )
        self.tabs.resize_tabs();
        
    def show( self ):
        Frame.show( self )
        self.tabs.show()

    def hide( self ):
        Frame.hide( self )
        self.tabs.hide()

    def remove_tab( self, tab ):
        self.tabs.remove( tab )

    def __str__( self ):
        return "TabbedFrame(%d,%d,%d,%d):" %(self.x,self.y,self.width,self.height)

    def place_window( self, window = None ):
        """
        Figure out where the window should be put.
        """
        if not window: window = self.windows.current()
        window.moveresize( self.x, self.y + self.screen.tab_height, self.width, self.height-self.screen.tab_height)

    def split_vertically( self ):
        SplitFrame( self.screen, self.x, self.y, self.width, self.height, True, self )

    def split_horizontally( self ):
        SplitFrame( self.screen, self.x, self.y, self.width, self.height, False, self )

    def remove_split( self ):
        if self.parent_frame:
            self.parent_frame.remove_me( self )
            self.tabs.remove_all()


    def next( self ):
        "Move to the next window in this pane."
        #clients = self.screen.query_clients(panefilter(self), 1)
        self.tabs.next()

    def prev( self ):
        "Move to the next window in this pane."
        #clients = self.screen.query_clients(panefilter(self), 1)
        self.tabs.prev()


def _test():
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    _test()
    print "DONE"
