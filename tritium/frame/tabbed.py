# tabbed.py -- a container for maximized clients with tabs across the top
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

from frame import Frame
from split import SplitFrame
from tab import Tabs, Tab
from Xlib import X
from plwm.frame import FrameProxy

class TabbedFrame( Frame ):
    def __init__( self, screen, x, y, width, height ):
        log.debug( "TabbedFrame.__init__" )
        Frame.__init__( self, screen, x, y, width, height )
        self.tabs = Tabs( self )

    def append( self, window ):
        Frame.append( self, window )
        tab = Tab( self, window )
        window.tab = tab
        self.tabs.append( tab )
        if not self.visible():
            tab.hide()
        tab.set_text( window.get_title() )
        # shouldn't some of the stuff above be moved into tab_manage?
        window.tab_manage()

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
        if not self.shown:
            for window in self.windows:
                window.show()

            self.shown = True

    def hide( self ):
        Frame.hide( self )
        self.tabs.hide()
        if self.shown:
            for window in self.windows:
                window.hide()
            self.shown = False

    def __str__( self ):
        return "TabbedFrame: " + Frame.__str__( self )

    def place_window( self, window = None ):
        """
        Figure out where the window should be put.
        """
        if not window: window = self.windows.current()

        if( window.transient ):
#            width, height = window.follow_size_hints(self.width - 2, self.height - 2)
            width, height = window.width, window.height

            if not window.gravity:
                window.gravity = X.SouthGravity

            width = min( width, self.width-self.screen.title_height - 2 )
            height = min( height, self.height-2 )

            if window.gravity in ( X.NorthEastGravity, 
                                   X.EastGravity,
                                   X.SouthEastGravity):
                x = self.x
            elif window.gravity in ( X.NorthGravity, 
                                     X.CenterGravity,
                                     X.SouthGravity ):
                x = self.x + ( self.width - width - 2 ) / 2
            else:
                x = self.x + self.width - width - 1

            if window.gravity in ( X.NorthEastGravity, 
                                   X.NorthGravity,
                                   X.NorthWestGravity):
                y = self.y + self.screen.title_height + 2

            elif window.gravity in ( X.EastGravity, 
                                     X.CenterGravity,
                                     X.WestGravity ):
                y = self.y + self.screen.title_height + ( self.height - height - 2 ) / 2
            else:
                y = self.y + self.screen.title_height + self.height - height - 1

            window.moveresize( x, y, width, height )
#            window.frameProxy = FrameProxy( self.screen, window )
        else:
            window.moveresize( self.x, self.y + self.screen.title_height, self.width-2, self.height-self.screen.title_height-2)


        window.hidden = False # ugh, i don't like having to set it here, but this seems to be before __client_init__ is called
        if not self.visible():
            window.hide()

    def split_vertically( self ):
        SplitFrame( self.screen, self.x, self.y, self.width, self.height, True, self )

    def split_horizontally( self ):
        SplitFrame( self.screen, self.x, self.y, self.width, self.height, False, self )

    def remove_split( self ):
        if self.tritium_parent:
            self.tritium_parent.remove_me( self )
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
