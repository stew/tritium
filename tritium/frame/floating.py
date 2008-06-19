# floating.py -- a frame that is a container for free floating
# decorated windows
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

class FloatingFrame( Frame ):
    """
    a Frame that contains floating windows
    """
    def place_window(self, window = None):
        "Figure out where the window should be put."
        pass

    def append( self, window ):
        window.title_manage()
        Frame.append( self, window )

    def remove( self, window ):
        # this is doing nothing becuase during reparenting, we get an
        # unmap event when we are being unmapped from the root window.
        # probably here we should be doing SOMETHING when we get
        # ummapped from the decorator window though.  (but that
        # belongs in title.py, not here, i'm writing it here, becuase
        # this is where I am right now, and it should be written down
	pass
        
    def show( self ):
        if not self.shown:
            for window in self.windows:
                window.title_show()

            self.shown = True

    def hide( self ):
        if self.shown:
            for window in self.windows:
                window.title_hide()
            self.shown = False

    def __str__( self ):
         return "FloatingFrame(%d,%d,%d,%d):" %(self.x,self.y,self.width,self.height)

def _test():
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    _test()
    print "DONE"
