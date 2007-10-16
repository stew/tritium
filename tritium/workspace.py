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
from frame.floating import FloatingFrame
from frame.tabbed import TabbedFrame
import logging

log = logging.getLogger()

FLOATING, TABBED = range( 2 )

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

    def get_workspace_by_name( self, name ):
        (ws,index) = self.workspaceDict[ name ]
        return ws


    def new_workspace( self, screen, type=TABBED, name="" ):
        log.debug( "tritiumWindowManager.new_workspace" )
        try:
            (ws,index) = self.workspaceDict[ name ]
        except KeyError:
            ws = Workspace( screen, type, name )
            index = len(self.workspaces)
            self.workspaceDict[ name ] = (ws,index)
            self.workspaces.append( ws )

        self.set_current_workspace( index )
        return ws

class OnTopFilter:
    def __call__( self, client ):
        try:
            return client.__getattribute__( 'on_top' )
        except:
            return False
        

class WorkspaceClient:
    def __client_init__( self ):
        log.debug( "WorkspaceClient.__client_init__: %s" % self )
        if not self.dockapp:
            self.workspace = self.wm.workspaces.current()

    def hide( self ):
        log.debug( "WorkspaceClient.hide: %s" % self )
        if not self.hidden:
            (x, y, width, height, borderwidth) = self.geometry()
            log.debug( "hiding %s" % self )
            self.hide_x = x
            self.hide_y = y
            new_x = self.screen.root_width+1
            new_y = self.screen.root_height+1
            log.debug( "moving %s from (%d, %d) to (%d, %d)" % (self.get_title(),x,y,new_x,new_y) )
            self.move( new_x, new_y )
            self.hidden = True
        
    def show( self ):
        log.debug( "WorkspaceClient.show" )
        if self.hidden:
            log.debug( "moving %s back to (%d, %d)" % (self.get_title(), self.hide_x, self.hide_y) )
            self.move( self.hide_x,self.hide_y )
            self.hidden = False
        
class WorkspaceScreen:
    def __screen_init__( self ):
        pass

class Workspace:
    def __init__( self, screen, type=TABBED, name="" ):
        log.debug( "Workspace.__init__" )
        self.name = name
        self.screen = screen
        self.active = False
        if type == FLOATING:
            self.current_frame = self.frame = FloatingFrame( self.screen, 0, 0, screen.root_width, screen.root_height )
        else:
            self.current_frame = self.frame = TabbedFrame( self.screen, 0, 0, screen.root_width, screen.root_height )

        self.current_frame.tritium_parent = self

    def raisewindows( self ):
        """ 
        way to notify the workspace that a window was raised, and
        therefore all "on top" windows need to be raised as
        well. perhaps if python-xlib supported XRestackWindows, this
        would be better
        """
        for client in self.screen.query_clients( OnTopFilter() ):
            client.raisewindow()
        pass


    def next_frame( self ):
        log.debug( "Workspace.next_frame" )
        self.current_frame.deactivate()
        self.current_frame = self.current_frame.next_frame()
        self.current_frame.activate()

    def next_sibling_frame( self, frame ):
        """
        this function ends up getting called when the last frame in a
        workspace calls "next_sibling_frame" so here we will return
        the first frame so that the frames will cycle
        """
        return self.frame.first_child_frame()

    def find_frame( self, x, y ):
        log.debug( "Workspace.find_frame" )
        return self.frame.find_frame( x, y )
    
    def visible( self ):
        log.debug( "Workspace.visible: %s? %d" %(self.name, self.active))
        return self.active

    def activate( self ):
        log.debug( "Workspace.activate" )
        self.active = True
        self.frame.show()
        # TODO this should really be the last current window's frame
        self.frame.topmost_child().activate()

    def deactivate( self ):
        log.debug( "Workspace.deactivate" )
        self.active = False
        self.frame.deactivate()
        self.frame.hide()

    def replace_me( self, me, replacewith ):
        log.debug( "Workspace.replace_me" )
        assert( self.frame == me )
        self.frame = replacewith
        self.frame.tritium_parent = self
        self.current_frame = self.frame.first_child_frame()

    def __str__( self ):
        return "Workspace: " + str( self.name )
            
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

