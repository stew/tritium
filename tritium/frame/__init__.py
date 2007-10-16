# frame.py -- a container for clients
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

from plwm import wmevents

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
    def __client_init__( self ):
        log.debug( "FrameClient.__client_init__" )
        frame = self.wm.find_me_a_home( self )
        if self.dockapp:
            self.frame = None
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
        log.debug( "frame_unmap" )
        self.frame.remove( self )

    def frame_get_focus( self, event ):
        log.debug( "frame_get_focus" )
        log.debug( "setting current frame to %s" % self.frame )
        self.wm.workspaces.current().current_frame = self.frame
        self.frame.set_current_window( self )

    def add_to_frame( self, frame ):
        log.debug( "FrameClient.add_to_frame" )
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

        
def _test():
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    _test()
    print "DONE"
