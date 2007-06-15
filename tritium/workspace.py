# workspace.py -- manage multiple 'desktops' or 'workspaces'
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

from cycle import Cycle
from frame import FloatingFrame, TabbedFrame
import logging
log = logging.getLogger()

class WorkspaceClient:
    def __client_init__( self ):
	(x, y, width, height, borderwidth) = self.geometry()
        self.hide_x = x
        self.hide_y = y
        self.workspace = self.wm.workspaces.current()

    def hide( self ):
	(x, y, width, height, borderwidth) = self.geometry()
        log.debug( "hiding %s" % self )
        self.hide_x = x
        self.hide_y = y
        self.move( -(2*self.workspace.screen.root_width), -(2*self.workspace.screen.root_height) )
        
    def show( self ):
        # [0] is wrong here
        self.move( self.hide_x,self.hide_y )
        
class WorkspaceScreen:
    def __screen_init__( self ):
        pass

class Workspace:
    def __init__( self, screen ):
        self.screen = screen
        self.current_frame = self.frame = TabbedFrame( self.screen, 0, 0, screen.root_width, screen.root_height )
        self.current_frame.parent_frame = self

    def next_frame( self ):
        self.current_frame.deactivate()
        self.current_frame = self.current_frame.next_frame()
        self.current_frame.activate()

    def find_frame( self, x, y ):
        return self.frame.find_frame( x, y )
    
    def activate( self ):
        self.frame.show()
        self.frame.activate()

    def deactivate( self ):
        self.frame.deactivate()
        self.frame.hide()

    def replace_me( self, me, with ):
        assert( self.frame == me )
        self.frame = with
        self.frame.parent_frame = self
        self.current_frame = self.frame.first_child_frame()

    def __str__( self ):
        return "Workspace: " + str( self.frame )
            
    def find_frame_right( self, frame ):
        self.screen.wm.set_current_workspace( self.screen.wm.workspaces.index + 1 )
        return self.screen.wm.current_frame();

    def find_frame_left( self, frame ):
        self.screen.wm.set_current_workspace( self.screen.wm.workspaces.index - 1 )
        return self.screen.wm.current_frame();

    find_frame_above = find_frame_left
    find_frame_below = find_frame_right

