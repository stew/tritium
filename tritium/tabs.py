# tabs.py -- a container for windows
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

"""
A set of tabs to display a list of windows contained in a frame.
"""
import logging
log = logging.getLogger()

from Xlib import X, Xatom
from plwm import wmevents
from cycle import Cycle
import frame

class Tabs:
    def __init__( self, frame ):
        self.tabs = []
        self.frame = frame

    def _current_index( self ):
        for index in range( len( self.tabs ) ):
            if self.tabs[index].active:
                return index

        return len( self.tabs ) -1
        
    def append( self, tab ):
        self.tabs.insert( self._current_index()+1, tab )
        self.resize_tabs()

    def remove( self, tab ):
        self.tabs.remove( tab )
        self.resize_tabs()
        
    def remove_all( self ):
        for tab in self.tabs:
            tab.destroy()
        self.tabs = []
        
    def redraw( self ):
        for tab in self.tabs:
            tab.draw()

    def show( self ):
        for tab in self.tabs:
            tab.show()

        self.resize_tabs()

    def hide( self ):
        for tab in self.tabs:
            tab.hide()

    def _tab_width( self ):
        if len( self.tabs ):
            return (self.frame.width-( (len( self.tabs ) -1) * 2 ))/ len( self.tabs )
        else:
            return 0

    def resize_tabs( self ):
        width = self._tab_width()
        x = self.frame.x
        for tab in self.tabs:
            tab.resize_tab( x, width )
            x += width+2

