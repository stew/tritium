# xinerama.py -- a frame split into multiple frames, one the size and
# location of each monitor in a multi-monitor desktop
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

class XineramaFrame( Frame ):
    """
    a special case of a split frame which is split so that each sub
    frame is one display in a xinerama enabled display.
    """
    """
    A frame that contains two frames split either vertically or
    horizontally. 
    """
    def __init__( self, screen, infos ):
        log.debug( "XineramaFrame.__init__" )
        
        min_x = min_y = sys.maxint
        max_x = max_y = -sys.maxint

        for info in infos:
            min_x = min( min_x, info.x_org )
            min_y = min( min_y, info.y_org )
            max_x = max( max_x, info.x_org + info.width )
            max_y = max( max_y, info.y_org + info.height )


        Frame.__init__( self, screen, min_x, min_y, max_x-min_x, max_y-min_y )


        self.frames = []
        for info in infos:
            frame = TabbedFrame( self.screen, 
                                 info.x_org, 
                                 info.y_org, 
                                 info.width, 
                                 info.height )
            frame.tritium_parent = self
            self.frames.append( frame )


    def find_frame_right( self, frame ):
        seen = False
        for child_frome in self.frames:
            if seen:
                return child_frame
            if frame == child_frame:
                seen = True

        return self.tritium_parent.find_frame_right( self )

    def find_frame_left( self, frame ):
        last = None
        for child_frome in self.frames:
            if frame == child_frame:
                if last:
                    return last
                else:
                    return self.tritium_parent.find_frame_left( self )
            else:
	    	last = child_frame

        return self.tritium_parent.find_frame_left( self )

    def find_frame_above( self, frame ):
        last = None
        for child_frome in self.frames:
            if frame == child_frame:
                if last:
                    return last
                else:
                    return self.tritium_parent.find_frame_above( self )
            else:
                last = child_frame

        return self.tritium_parent.find_frame_above( self )

    def find_frame_below( self, frame ):
        seen = False
        for child_frome in self.frames:
            if seen:
                return child_frame
            if frame == child_frame:
                seen = True

        return self.tritium_parent.find_frame_below( self )

    # these four below could probably be made smarter at some point,
    # like topmost could be topmost containing a certain x
    def topmost_child( self ):
        return self.frames[0]

    def bottommost_child( self ):
        return self.frames[-1]

    leftmost_child = topmost_child
    rightmost_child = bottommost_child

    def hide( self ):
        Frame.hide( self )
        for frame in self.frames:
            frame.hide()

    def show( self ):
        Frame.hide( self )
        for frame in self.frames:
            frame.show()

    def find_frame( self, x, y ):
        log.debug( "SplitFrame.find_frame" )
        for frame in self.frames:
            if ( frame.x <= x ) and \
                    ( frame.y <= y ) and \
                    ((frame.x+frame.width) >= x ) and \
                    ((frame.y+frame.height) >= y):
                return frame

        return self.frames[0]

    def next_sibling_frame( self, frame ):
        log.debug( "SplitFrame.next_sibling_frame" )
        if frame == self.frame1:
            return self.frame2.first_child_frame()
        else:
            return self.next_frame()

    def first_child_frame( self ):
        log.debug( "SplitFrame.first_child_frame" )
        return self.frame1.first_child_frame()


    def remove_me( self, me ):
        """you can't remove one of my child frames, so this does nothing"""
        return

    def replace_me( self, me, replacewith ):
        log.debug( "SplitFrame.replace_me" )
        for i in range( len( self.frames ) ):
            if self.frames[i] == me:
                self.frame[i] = replacewith
                break

        replacewith.tritium_parent = self

    def __str__( self ):
        log.debug( "XineramaFrame.__str__" )
        return "XineramaFrame(%d,%d,%d,%d): <" %(self.x,self.y,self.width,self.height) + ">"


def _test():
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    _test()
    print "DONE"
