# dock.py -- floating windows with titlebars
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

from Xlib import X,Xatom,Xutil

BOTTOM = 'bottom'
TOP = 'top'
LEFT = 'left'
RIGHT = 'right'

class DockScreen(object):
    def __screen_client_init__( self ):
        self.dock_windows = []
        self.dock_size = 0

    def set_dock_area( self, where=BOTTOM, size=64, gravity=X.SouthGravity ):
        self.dock_where = where
        self.dock_x, self.dock_y, self.dock_width, self.dock_height = self.alloc_border( where, size )

    def add_dock_window( self, client ):
        self.dock_windows.append( client )

# Client mixin
class DockClient(object):
    """
    This class is a client mixin for window that provides an IconWindow

    """
    
    def __client_init__(self):
        log.debug( "DockClient.__client_init__" )
#         if( self.screen.dock_where ):
#             # is this client a dockapp?
#             wmh = self.window.get_wm_hints()
#             if wmh and wmh.flags & Xutil.IconWindowHint:
#                 self.dock_manage()
    
    def dock_manage( self ):
        self.on_top = True
        self.dockapp = True
        self.screen.add_dock_window( self )

        self.dispatch.add_handler( X.ConfigureRequest, self.dock_configure ) 

        log.debug( "moving dock window to (%d,%d)" % ( self.screen.dock_x, self.screen.dock_y ) )
        self.move( self.screen.dock_x, self.screen.dock_y )

    def dock_configure( self, event ):
        log.debug( "moving dock window to (%d,%d) becuase of ConfigureRequest" % ( self.screen.dock_x, self.screen.dock_y ) )
        self.move( self.screen.dock_x, self.screen.dock_y )
        
