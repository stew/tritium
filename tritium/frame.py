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
from tab import Tabs, Tab
import workspace

import logging
log = logging.getLogger()

class FrameWindowManager:
    def find_me_a_home( self, client ):
        frame = client.screen.layout.which_frame( client )
        if frame:
            return frame
        return self.current_frame()
    

class FrameClient( object ):
    """
    mixin for client windows that are contained in frames

    inv:
        self._check_frame_state()
       
    """
    def __client_init__( self ):
        log.debug( "FrameClient.__client_init__" )
        self.frame_dragging = False
        frame = self.wm.find_me_a_home( self )
        self.add_to_frame( frame )
        self.dispatch.add_handler(wmevents.ClientFocusIn, self.frame_get_focus)

    # moved this into its own function so I can allow for frame not
    # yet being assigned
    def _check_frame_state( self ):
        try:
            return self.__getattribute__( 'frame' ) != None
        except:
            return True
        
    def frame_unmap( self, event ):
        log.debug( "frame_unmap" )
        self.frame.remove( self )

    def frame_get_focus( self, event ):
        log.debug( "frame_get_focus" )
        log.debug( "setting current frame to %s" % self.frame )
        self.wm.workspaces.current().current_frame = self.frame
        self.frame.set_current_window( self )

    def add_to_frame( self, frame ):
        log.debug( "FrameClient.add_to_frame" )
        log.debug( "adding to frame: %s" % frame )
        self.frame = frame
        frame.append( self )

    def move_to_frame( self, new_frame ):
        log.debug( "FrameClient.move_to_frame" )
        if new_frame and self.frame != new_frame:
            old_workspace = self.frame.workspace()
            new_workspace = new_frame.workspace()
            if new_workspace != old_workspace:
                old_workspace.deactivate()
                new_workspace.activate()
            log.debug( "moving from frame %s to frame %s" % ( self.frame, new_frame ) )
            self.tab_remove()
            self.frame.remove( self )
            self.add_to_frame( new_frame )

class Frame:
    """
    a container for [fullscreen] windows
    """
    def __init__( self, screen, x, y, width, height ):
        log.debug( "Frame.__init__" )
        self.screen = screen
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.wm = screen.wm
        self.shown = True
        self.tritium_parent = None
        self.windows = Cycle()

    def workspace( self ):
        "return the workspace this frame is part of"
        if isinstance( self.tritium_parent, workspace.Workspace ):
            return self.tritium_parent
        else:
            return self.tritium_parent.workspace()

    def find_frame( self, x, y ):
        log.debug( "find_frame" )
        if ( self.x <= x ) and \
           ( self.y <= y ) and \
           ((self.x+self.width) >= x ) and \
           ((self.y+self.height) >= y):
            return self
    
    def append( self, window ):
        log.debug( "Frame.append" )
        self.place_window( window  )
        if self.visible():
            self.deactivate()

        self.windows.insert_after_current( window )

	if self.visible():
            self.activate()

        window.frame = self

    def remove( self, window ):
        log.debug( "Frame.remove" )
        log.debug( "removing window: %s from frame %s with windows: %s" % (window,self,self.windows))
        cur = self.windows.current()
        self.windows.remove( window )
        if cur == window:
            self.deactivate()
            if self.wm.current_frame() == self:
                self.windows.prev()
                self.activate()

    def visible( self ):
        return self.tritium_parent.visible()

    def next( self ):
        "Move to the next window in this pane."
        #clients = self.screen.query_clients(panefilter(self), 1)
        log.debug( "Frame.next" )
        self.deactivate()
        self.windows.next()
        self.activate()

    def prev( self ):
        "Move to the prev window in this pane."
        #clients = self.screen.query_clients(panefilter(self), 1)
        log.debug( "Frame.prev" )
        self.deactivate()
        self.windows.prev()
        self.activate()

    def set_current( self, index ):
        "set the current window to index."
        #clients = self.screen.query_clients(panefilter(self), 1)
        log.debug( "Frame.set_current" )
        self.deactivate()
        self.windows.index = index
        self.activate()

    def set_current_window( self, window ):
        self.windows.set_current( window )

    def show( self ):
        log.debug( "Frame.show" )
        if not self.shown:
            for window in self.windows:
                window.show()

            self.shown = True

    def hide( self ):
        log.debug( "Frame.hide" )
#         if self.shown:
#             for window in self.windows:
#                 window.hide()
#             self.shown = False

    def deactivate(self):
        log.debug( "deactivate" )
        if self.windows.current() and not self.windows.current().withdrawn:
            #self.windows.current().panes_pointer_pos = self.windows.current().pointer_position()
            if self.wm.current_frame() == self:
                self.wm.set_current_client( None )

    def activate(self):
        "Dummy function, reset to _activate after all windows are opened."

    def _activate(self):
        log.debug( "Frame._activate" )
        "Activate whatever is currently self.windows.current()."
        self.wm.current_screen = self.screen
        self.wm.set_current_frame( self )
        log.debug( "Frame._activate: setting current frame to %s in %s" % ( self, self.wm ) )

        if self.windows.current() and not self.windows.current().withdrawn:
            # Will raise window and give focus
            self.windows.current().activate()
            #pos = self.windows.current().panes_pointer_pos
            #if pos:
                #self.windows.current().warppointer(pos[0], pos[1])

    def next_frame( self ):
        log.debug( "Frame.next_frame" )
        if self.tritium_parent:
            return self.tritium_parent.next_sibling_frame( self )
        else:
            return self


    def first_child_frame( self ):
        log.debug( "first_child_frame" )
        return self


    def identity( self ):
        return self

    topmost_child = bottommost_child = leftmost_child = rightmost_child = identity

class SplitFrame( Frame ):
    """
    A frame that contains two frames split either vertically or
    horizontally. 
    """
    def __init__( self, screen, x, y, width, height, vertical, frame1 ):
        log.debug( "SplitFrame.__init__" )
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

        frame1.tritium_parent.replace_me( frame1, self )

        self.frame1.tritium_parent = self.frame2.tritium_parent = self
        self.frame1.activate()

        self.create_split_window()

    def moveresize( self, x, y, width, height ):
        log.debug( "SplitFrame.moveresize" )
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
        log.debug( "SplitFrame.find_frame_right" )
        if not self.vertical and self.frame1 == frame:
            return self.frame2.leftmost_child()
        else:
            return self.tritium_parent.find_frame_right( self )

    def find_frame_left( self, frame ):
        log.debug( "SplitFrame.find_frame_left" )
        if not self.vertical and self.frame2 == frame:
            return self.frame1.rightmost_child()
        else:
            return self.tritium_parent.find_frame_left( self )

    def find_frame_above( self, frame ):
        log.debug( "SplitFrame.find_frame_above" )
        if self.vertical and self.frame2 == frame:
            return self.frame1.bottommost_child()
        else:
            return self.tritium_parent.find_frame_above( self )

    def find_frame_below( self, frame ):
        log.debug( "SplitFrame.find_frame_below" )
        if self.vertical and self.frame1 == frame:
            return self.frame2.topmost_child()
        else:
            return self.tritium_parent.find_frame_below( self )

    # these four below could probably be made smarter at some point,
    # like topmost could be topmost containing a certain x
    def topmost_child( self ):
        return self.frame1

    def bottommost_child( self ):
        return self.frame2

    leftmost_child = topmost_child
    rightmost_child = bottommost_child


    def find_frame( self, x, y ):
        log.debug( "SplitFrame.find_frame" )
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
        log.debug( "SplitFrame.next_sibling_frame" )
        if frame == self.frame1:
            return self.frame2.first_child_frame()
        else:
            return self.next_frame()

    def first_child_frame( self ):
        log.debug( "SplitFrame.first_child_frame" )
        return self.frame1.first_child_frame()

    def create_split_window( self ):
        log.debug( "SplitFrame.create_split_window" )
        
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
        log.debug( "SplitFrame._create_gcs" )
        self.split_gc1 = window.create_gc( foreground =
                                           self.screen.get_color( "#ffffff" ))

        self.split_gc2 = window.create_gc( foreground =
                                           self.screen.get_color( "#cccccc" ))

        self.split_gc3 = window.create_gc( foreground =
                                           self.screen.get_color( "#999999" ))
        
        self.split_gc4 = window.create_gc( foreground =
                                           self.screen.get_color( "#666666" ))


    def redraw( self, event = None ):
        log.debug( "SplitFrame.redraw" )
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
        log.debug( "SplitFrame.splitbar_mouse_down" )
        self.split_dragging = True
        if self.vertical:
            self.splitbar_drag_start = event.root_y - self.split
        else:
            self.splitbar_drag_start = event.root_x - self.split

    def splitbar_mouse_up( self, event ):
        log.debug( "SplitFrame.splitbar_mouse_up" )
        self.split_dragging = False
        
    def splitbar_drag( self, event ):
        log.debug( "SplitFrame.splitbar_drag" )
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
        log.debug( "SplitFrame.remove_me" )
        if self.frame1 == me:
            with = self.frame2
        else:
            with = self.frame1

        for client in me.windows:
            client.add_to_frame( with )

        self.window.destroy()
        self.tritium_parent.replace_me( self, with )
        with.moveresize( self.x, self.y, self.width, self.height )

    def replace_me( self, me, with ):
        log.debug( "SplitFrame.replace_me" )
        if self.frame1 == me:
            self.frame1 = with
        elif self.frame2 == me:
            self.frame2 = with

        with.tritium_parent = self

    def __str__( self ):
        log.debug( "SplitFrame.__str__" )
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
        log.debug( "FloatingFrame.place_window" )
        pass

    def append( self, window ):
        log.debug( "FloatingFrame.append" )
        window.title_manage()
        Frame.append( self, window )

    def remove( self, window ):
        log.debug( "FloatingFrame.remove" )
        log.debug( "NOT removing window: %s from frame %s" % (window,self))
        # this is doing nothing becuase during reparenting, we get an
        # unmap event when we are being unmapped from the root window.
        # probably here we should be doing SOMETHING when we get
        # ummapped from the decorator window though.  (but that
        # belongs in title.py, not here, i'm writing it here, becuase
        # this is where I am right now, and it should be written down
        
    def show( self ):
        log.debug( "Frame.show" )
        if not self.shown:
            for window in self.windows:
                window.title_show()

            self.shown = True

    def hide( self ):
        log.debug( "Frame.hide" )
        if self.shown:
            for window in self.windows:
                window.title_hide()
            self.shown = False

    def __str__( self ):
         return "FloatingFrame(%d,%d,%d,%d):" %(self.x,self.y,self.width,self.height)

class TabbedFrame( Frame ):
    def __init__( self, screen, x, y, width, height ):
        log.debug( "TabbedFrame.__init__" )
        Frame.__init__( self, screen, x, y, width, height )
        self.tabs = Tabs( self )

    def append( self, window ):
        log.debug( "TabbedFrame.append" )
        tab = Tab( self, window )
        window.tab = tab
        self.tabs.append( tab )
        if not self.visible():
            tab.hide()
        tab.set_text( window.get_title() )
        # shouldn't some of the stuff above be moved into tab_manage?
        window.tab_manage()
        Frame.append( self, window )

    def moveresize( self, x, y, width, height ):
        log.debug( "TabbedFrame.moveresize" )
        self.x = x
        self.y = y
        self.height = height
        self.width = width
        map( self.place_window, self.windows )
        self.tabs.resize_tabs();
        
    def show( self ):
        log.debug( "TabbedFrame.show" )
        Frame.show( self )
        self.tabs.show()
        if not self.shown:
            for window in self.windows:
                window.show()

            self.shown = True

    def hide( self ):
        log.debug( "TabbedFrame.hide" )
        Frame.hide( self )
        self.tabs.hide()
        if self.shown:
            for window in self.windows:
                window.hide()
            self.shown = False

    def __str__( self ):
        return "TabbedFrame(%d,%d,%d,%d):" %(self.x,self.y,self.width,self.height)

    def place_window( self, window = None ):
        """
        Figure out where the window should be put.
        """
        log.debug( "TabbedFrame.place_window: %s " % window.get_title() )
        if not window: window = self.windows.current()
        window.moveresize( self.x, self.y + self.screen.title_height, self.width, self.height-self.screen.title_height)
        window.hidden = False # ugh, i don't like having to set it here, but this seems to be before __client_init__ is called
        if not self.visible():
            window.hide()

    def split_vertically( self ):
        log.debug( "TabbedFrame.split_vertically" )
        SplitFrame( self.screen, self.x, self.y, self.width, self.height, True, self )

    def split_horizontally( self ):
        log.debug( "TabbedFrame.split_horizontally" )
        SplitFrame( self.screen, self.x, self.y, self.width, self.height, False, self )

    def remove_split( self ):
        log.debug( "TabbedFrame.remove_split" )
        if self.tritium_parent:
            self.tritium_parent.remove_me( self )
            self.tabs.remove_all()


    def next( self ):
        "Move to the next window in this pane."
        #clients = self.screen.query_clients(panefilter(self), 1)
        log.debug( "TabbedFrame.next" )
        self.tabs.next()

    def prev( self ):
        "Move to the next window in this pane."
        #clients = self.screen.query_clients(panefilter(self), 1)
        log.debug( "TabbedFrame.prev" )
        self.tabs.prev()


def _test():
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    _test()
    print "DONE"
