# split.py -- a frame split either vertically or horizontalliy
# that contains two other frames
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

from Xlib import X, Xutil, Xatom

from frame import Frame

import logging
log = logging.getLogger()

class SplitFrame( Frame ):
    """
    A frame that contains two frames split either vertically or
    horizontally. 
    """
    def __init__( self, screen, x, y, width, height, vertical, frame1 ):
        log.debug( "SplitFrame.__init__" )
        Frame.__init__( self, screen, x, y, width, height )
        self.split_dragging = False
        self.vertical = vertical

        if vertical:
            self.split = height
        else:
            self.split = width
        self.split = self.split >> 1

        self.frame1 = frame1

        if vertical:
            self.frame1.moveresize( x, y, self.width, self.height - self.split )
            # this is a horrible hack to get around circular importing
            self.frame2 = self.frame1.topmost_child().__class__( self.screen, self.x, self.y + self.split+4,
                                                 self.width, self.height-self.split-4)
        else:
            self.frame1.moveresize( x, y, self.width - self.split, self.height )
            self.frame2 = self.frame1.topmost_child().__class__( self.screen, self.x + self.split+4, self.y,
                                                 self.width-self.split-4, self.height)

        frame1.tritium_parent.replace_me( frame1, self )

        self.frame1.tritium_parent = self.frame2.tritium_parent = self
        self.frame1.activate()

        self.create_split_window()

    def _activate(self):
        Frame._activate( self )
        self.window.raisewindow()
    activate=_activate

    def moveresize( self, x, y, width, height ):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        if self.vertical:
#            self.split = height >> 1
            self.window.moveresize( self.x, self.y + self.split, self.width, 4 )
            self.frame1.moveresize( self.x, self.y, self.width, self.split )
            self.frame2.moveresize( self.x, self.split+4, self.width, self.height - self.split - 4 )
        else:
#            self.split = width >> 1
            self.window.moveresize( self.x + self.split, self.y, 4, self.height )
            self.frame1.moveresize( self.x, self.y, self.split, self.height )
            self.frame2.moveresize( self.x + self.split+4, self.y, self.width - self.split - 4, self.height )

        self.redraw( self )

    def find_frame_right( self, frame ):
        if not self.vertical and self.frame1 == frame:
            return self.frame2.leftmost_child()
        else:
            return self.tritium_parent.find_frame_right( self )

    def find_frame_left( self, frame ):
        if not self.vertical and self.frame2 == frame:
            return self.frame1.rightmost_child()
        else:
            return self.tritium_parent.find_frame_left( self )

    def find_frame_above( self, frame ):
        if self.vertical and self.frame2 == frame:
            return self.frame1.bottommost_child()
        else:
            return self.tritium_parent.find_frame_above( self )

    def find_frame_below( self, frame ):
        if self.vertical and self.frame1 == frame:
            return self.frame2.topmost_child()
        else:
            return self.tritium_parent.find_frame_below( self )

    # these four below could probably be made smarter at some point,
    # like topmost could be topmost containing a certain x
    def topmost_child( self ):
        return self.frame1.topmost_child()

    def bottommost_child( self ):
        return self.frame2.bottommost_child()

    leftmost_child = topmost_child
    rightmost_child = bottommost_child

    def hide( self ):
        Frame.hide( self )
        self.frame1.hide()
        self.frame2.hide()
        self.window.unmap()

    def show( self ):
        Frame.show( self )
        self.frame1.show()
        self.frame2.show()
        self.window.map()

    def find_frame( self, x, y ):
        if ( self.x <= x ) and \
           ( self.y <= y ) and \
           ((self.x+self.width) >= x ) and \
           ((self.y+self.height) >= y):

            r = self.frame1.find_frame( x, y )
            if not r:
                r = self.frame2.find_frame( x, y )
                if not r:
                    r = self

            return r

    def next_sibling_frame( self, frame ):
        if frame == self.frame1:
            return self.frame2.first_child_frame()
        else:
            return self.next_frame()

    def first_child_frame( self ):
        return self.frame1.first_child_frame()

    def create_split_window( self ):
        if self.vertical:
            window = self.screen.root.create_window(
                self.x, self.y + self.split, self.width, 8, 0,
                X.CopyFromParent, X.InputOutput, X.CopyFromParent,
                event_mask = X.ExposureMask
                )
        else:
            window = self.screen.root.create_window(
                self.x + self.split, self.y, 8, self.height, 0,
                X.CopyFromParent, X.InputOutput, X.CopyFromParent,
                event_mask = X.ExposureMask
                )
            
        self.window = self.screen.add_internal_window(window)

        self.window.dispatch.add_handler( X.Expose, self.redraw )
        self.window.dispatch.add_handler( X.ButtonRelease, self.splitbar_mouse_up ) 
        self.window.dispatch.add_handler( X.ButtonPress, self.splitbar_mouse_down )
        self.window.dispatch.add_handler( X.MotionNotify, self.splitbar_drag )        
        window.map()
        self.window.raisewindow()
        self._create_gcs( window )

    def _create_gcs( self, window ):
        self.split_gc1 = window.create_gc( foreground =
                                           self.screen.get_color( "#ffffff" ))

        self.split_gc2 = window.create_gc( foreground =
                                           self.screen.get_color( "#cccccc" ))

        self.split_gc3 = window.create_gc( foreground =
                                           self.screen.get_color( "#999999" ))
        
        self.split_gc4 = window.create_gc( foreground =
                                           self.screen.get_color( "#666666" ))


    def redraw( self, event = None ):
        if self.vertical:
            self.window.fill_rectangle( self.split_gc1, 0, 0, self.width, 2 )
            self.window.fill_rectangle( self.split_gc2, 0, 2, self.width, 2 )
            self.window.fill_rectangle( self.split_gc3, 0, 4, self.width, 2 )
            self.window.fill_rectangle( self.split_gc4, 0, 6, self.width, 2 )
        else:
            self.window.fill_rectangle( self.split_gc1, 0, 0, 2, self.height )
            self.window.fill_rectangle( self.split_gc2, 2, 0, 2, self.height )
            self.window.fill_rectangle( self.split_gc3, 4, 0, 2, self.height )
            self.window.fill_rectangle( self.split_gc4, 6, 0, 2, self.height )

    def splitbar_mouse_down( self, event ):
        self.split_dragging = True
        if self.vertical:
            self.splitbar_drag_start = event.root_y - self.split
        else:
            self.splitbar_drag_start = event.root_x - self.split

    def splitbar_mouse_up( self, event ):
        self.split_dragging = False
        
    def splitbar_drag( self, event ):
        if self.split_dragging:
            self.resize_point( event.root_x - self.splitbar_drag_start, event.root_y - self.splitbar_drag_start )

    def resize_point( self, x, y ):
        if self.vertical:
            if self.split + self.y != y:
                self.split = y - self.y
                self.window.move( self.x, self.y + self.split )
                self.frame1.moveresize( self.x, self.y, self.width, self.split + self.y )
                self.frame2.moveresize( self.x, self.y + self.split+8, self.width, self.height - self.split - 8 )
        else:
            if self.split != x:
                self.split = x
                self.window.move( self.x + self.split, self.y  )
                self.frame1.moveresize( self.x, self.y, self.split, self.height )
                self.frame2.moveresize( self.x + self.split+8, self.y, self.width - self.split - 8, self.height )

    def resize_fraction( self, fraction ):
        """
        move the split bar to (frame_size * fraction) pixels

        pre:
            (fraction >= 0) and (fraction <= 1.0)
        """
        if self.vertical:
            self.resize_point( 0, int(fraction * self.height) )
        else:
            self.resize_point( int(fraction * self.width), 0 )
    

    def resize_incr( self, incr ):
        """
        move the split bar to (frame_size * fraction) pixels

        pre:
            (fraction >= 0) and (fraction <= 1.0)
        """
        if self.vertical:
            self.resize_point( 0, self.split + incr )
        else:
            self.resize_point( self.split + incr, 0 )
    

    def remove_me( self, me ):
        if self.frame1 == me:
            replacewith = self.frame2
        else:
            replacewith = self.frame1

        for client in me.windows:
            client.add_to_frame( replacewith )

        self.window.destroy()
        self.tritium_parent.replace_me( self, replacewith )
        replacewith.moveresize( self.x, self.y, self.width, self.height )

    def replace_me( self, me, replacewith ):
        if self.frame1 == me:
            self.frame1 = replacewith
        elif self.frame2 == me:
            self.frame2 = replacewith

        replacewith.tritium_parent = self

def _test():
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    _test()
    print "DONE"
