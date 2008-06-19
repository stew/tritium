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

from Xlib import X
from plwm import wmevents
from plwm.frame import FrameProxy
import traceback

class FrameWindowManager( object ):
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
    #TODO: find me a home:
    default_gravity = X.SouthGravity

    def __init__(self, screen, window, maprequest):
	try:
	    transient = window.get_wm_transient_for()
            if transient:
                self.transient = True
	except:
            traceback.print_exc()
	    pass

        self.gravity = self.default_gravity

    def __client_init__( self ):
        log.debug( "FrameClient.__client_init__" )
        frame = self.wm.find_me_a_home( self )
        if self.dockapp:
            self.frame = None
            self.dock_manage()
        else:
            self.frame_dragging = False
            self.add_to_frame( frame )
            self.dispatch.add_handler(wmevents.ClientFocusIn, self.frame_get_focus)

    # moved this into its own function so I can allow for frame not
    # yet being assigned
    def _check_frame_state( self ):
        try:
            return self.dockapp or (self.__getattribute__( 'frame' ) != None)
        except:
            return True
        
    def frame_unmap( self, event ):
        self.frame.remove( self )

    def frame_get_focus( self, event ):
        self.wm.workspaces.current().current_frame = self.frame
        self.frame.set_current_window( self )

    def add_to_frame( self, frame ):
       	self.frame = frame
        frame.append( self )

    def move_to_frame( self, new_frame ):
        if new_frame and self.frame != new_frame:
            old_workspace = self.frame.workspace()
            new_workspace = new_frame.workspace()
            if new_workspace != old_workspace:
                old_workspace.deactivate()
                new_workspace.activate()
            self.tab_remove()
            self.frame.remove( self )
            self.add_to_frame( new_frame )

        
def _test():
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    _test()
    print "DONE"
