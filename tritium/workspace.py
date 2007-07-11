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

class WorkspaceWindowManager:
    """
    window manager mixin for a wm with workspaces
    """
    def __wm_screen_init__( self ):
        log.debug( "WorkspaceWindowManager.__wm_screen_init__" )
        self.workspaces = Cycle()
        self.workspaceDict = {}

    def __wm_init__( self ):
        log.debug( "WorkspaceWindowManager.__wm_init__" )
        workspace = self.workspaces.current()
        if workspace:
            workspace.activate()


    def current_frame( self ):
        log.debug( "WorkspaceWindowManager.current_frame" )
        ws = self.workspaces.current()
        if ws:
            return ws.current_frame

    def set_current_frame( self, frame ):
        log.debug( "tritiumWindowManager.set_current_frame" )
        if frame:
            self.workspaces.current().current_frame = frame
        else:
            log.error( "wtf, set_current_frame got a null frame" )

    def set_current_workspace( self, index ):
        log.debug( "tritiumWindowManager.set_current_workspace: %d" % index )
        
        if( index != self.workspaces.index and index >= 0 and index < len( self.workspaces ) ):
            log.debug( "setting current workspace to %d" %index )
            self.workspaces.current().deactivate()
            self.workspaces.index = index
            self.workspaces.current().activate()

    def new_workspace( self, screen, floating=False, name="" ):
        log.debug( "tritiumWindowManager.new_workspace" )
        try:
            (ws,index) = self.workspaceDict[ name ]
        except KeyError:
            ws = Workspace( screen, floating, name )
            self.workspaceDict[ name ] = ws
            self.workspaces.append( ws )
            index = len( self.workspaces ) - 1

        self.set_current_workspace( index )
        return ws

class WorkspaceClient:
    def __client_init__( self ):
        log.debug( "WorkspaceClient.__client_init__" )
	(x, y, width, height, borderwidth) = self.geometry()
        self.hide_x = x
        self.hide_y = y
        self.workspace = self.wm.workspaces.current()

    def hide( self ):
        log.debug( "WorkspaceClient.hide" )
	(x, y, width, height, borderwidth) = self.geometry()
        log.debug( "hiding %s" % self )
        self.hide_x = x
        self.hide_y = y
        self.move( -(2*self.workspace.screen.root_width), -(2*self.workspace.screen.root_height) )
        
    def show( self ):
        log.debug( "WorkspaceClient.show" )
        self.move( self.hide_x,self.hide_y )
        
class WorkspaceScreen:
    def __screen_init__( self ):
        pass

class Workspace:
    def __init__( self, screen, floating=False, name="" ):
        log.debug( "Workspace.__init__" )
        self.name = name
        self.screen = screen
        if floating:
            self.current_frame = self.frame = FloatingFrame( self.screen, 0, 0, screen.root_width, screen.root_height )
        else:
            self.current_frame = self.frame = TabbedFrame( self.screen, 0, 0, screen.root_width, screen.root_height )

        self.current_frame.parent_frame = self

    def next_frame( self ):
        log.debug( "Workspace.next_frame" )
        self.current_frame.deactivate()
        self.current_frame = self.current_frame.next_frame()
        self.current_frame.activate()

    def find_frame( self, x, y ):
        log.debug( "Workspace.find_frame" )
        return self.frame.find_frame( x, y )
    
    def activate( self ):
        log.debug( "Workspace.activate" )
        self.frame.show()
        # TODO this should really be the last current window's frame
        self.frame.topmost_child().activate()

    def deactivate( self ):
        log.debug( "Workspace.deactivate" )
        self.frame.deactivate()
        self.frame.hide()

    def replace_me( self, me, with ):
        log.debug( "Workspace.replace_me" )
        assert( self.frame == me )
        self.frame = with
        self.frame.parent_frame = self
        self.current_frame = self.frame.first_child_frame()

    def __str__( self ):
        return "Workspace: " + str( self.frame )
            
    def find_frame_right( self, frame ):
        log.debug( "Workspace.find_frame_right" )
        self.screen.wm.set_current_workspace( self.screen.wm.workspaces.index + 1 )
        return self.screen.wm.current_frame();

    def find_frame_left( self, frame ):
        log.debug( "Workspace.find_frame_left" )
        self.screen.wm.set_current_workspace( self.screen.wm.workspaces.index - 1 )
        return self.screen.wm.current_frame();

    find_frame_above = find_frame_left
    find_frame_below = find_frame_right

