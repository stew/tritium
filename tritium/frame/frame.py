# frame.py -- a container for clients
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

from plwm import wmevents
from tritium.cycle import Cycle
import tritium.workspace 

class Frame( object ):
    """
    a container for [fullscreen] windows

    inv:
        self.tritium_parent != self

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
        if not isinstance( self.tritium_parent, Frame ):
            return self.tritium_parent
        else:
            return self.tritium_parent.workspace()

    def find_frame( self, x, y ):
        if ( self.x <= x ) and \
           ( self.y <= y ) and \
           ((self.x+self.width) >= x ) and \
           ((self.y+self.height) >= y):
            return self
    
    def append( self, window ):
        self.place_window( window  )
        if self.visible():
            self.deactivate()

        window.dispatch.add_handler( wmevents.RemoveClient, self.remove_client_event )
        self.windows.insert_after_current( window )

	if self.visible():
            self.activate()

        window.frame = self

    def remove_client_event( self, event ):
        self.remove( event.client )

    def remove( self, window ):
        cur = self.windows.current()

        try:
            self.windows.remove( window )
        except ValueError:
            log.warning( "window wasn't in list" )

        if cur == window:
            self.deactivate()
            if self.wm.current_frame() == self:
                self.windows.prev()
                self.activate()

    def visible( self ):
        return self.tritium_parent.visible()

    def next( self ):
        "Move to the next window in this pane."
        self.deactivate()
        self.windows.next()
        self.activate()

    def prev( self ):
        "Move to the prev window in this pane."
        self.deactivate()
        self.windows.prev()
        self.activate()

    def set_current( self, index ):
        "set the current window to index."
        self.deactivate()
        self.windows.index = index
        self.activate()

    def set_current_window( self, window ):
        self.windows.set_current( window )

    def show( self ):
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
        if self.windows.current() and not self.windows.current().withdrawn:
            #self.windows.current().panes_pointer_pos = self.windows.current().pointer_position()
            if self.wm.current_frame() == self:
                self.wm.set_current_client( None )

    def activate(self):
        "Dummy function, reset to _activate after all windows are opened."

    def _activate(self):
        "Activate whatever is currently self.windows.current()."
        self.wm.current_screen = self.screen
        self.wm.set_current_frame( self )

        if self.windows.current() and not self.windows.current().withdrawn:
            # Will raise window and give focus
            self.windows.current().activate()
            #pos = self.windows.current().panes_pointer_pos
            #if pos:
                #self.windows.current().warppointer(pos[0], pos[1])

    def next_frame( self ):
        if self.tritium_parent:
            return self.tritium_parent.next_sibling_frame( self )
        else:
            return self


    def first_child_frame( self ):
        return self


    def identity( self ):
        return self

    def __str__( self ):
        return "Frame: (%d,%d,%d,%d) <" %(self.x,self.y,self.width,self.height) + " parent: " + str( self.tritium_parent )
        
    topmost_child = bottommost_child = leftmost_child = rightmost_child = identity


def _test():
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    _test()
    print "DONE"
