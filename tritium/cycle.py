# clientlist.py -- a container for clients
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

"""
A list with a rotating iterator
"""

class Cycle:
    """
    >>> f=Cycle()
    >>> f.append(1)
    >>> f.append(2)
    >>> f.append(3)
    >>> for a in f: print a
    1
    2
    3
    >>> f[1]
    2
    """
    def __init__( self ):
        self.items = []
        self.index = 0

    def __str__( self ):
        return "Cycle: %s" % self.items

    def append( self, item ):
        self.items.append( item )

    def insert_after_current( self, item ):
        self.items.insert( self.index+1, item )
        self.index += 1

    def contains( self, item ):
        try:
            self.items.index( item )
            return True
        except:
            return False

    def current( self ):
        self._adjust()
        if len( self.items ):
            return self.items[ self.index ]

    def set_current( self, obj ):
        for self.index in range( len( self ) ):
            if( self.current() == obj ):
                return

    def remove( self, client ):
        self.items.remove( client )
        
    def __getitem__( self, i ):
        return self.items.__getitem__( i )

    def __iter__( self ):
        return self.items.__iter__()

    def __len__( self ):
        return self.items.__len__()

    def next( self ):
        """
        # test the cycling
        >>> f=Cycle()
        >>> f.append( 1 )
        >>> f.append( 2 )
        >>> f.append( 3 )
        >>> f.items
        [1, 2, 3]
        >>> f.next()
        2
        >>> f.next()
        3
        >>> f.next()
        1

        """
        self.index += 1
        return self.current()

    def prev( self ):
        """
        # test the cycling
        >>> f=Cycle()
        >>> f.append( 1 )
        >>> f.append( 2 )
        >>> f.append( 3 )
        >>> f.items
        [1, 2, 3]
        >>> f.prev()
        3
        >>> f.prev()
        2
        >>> f.prev()
        1
        >>> f.prev()
        3

        """
        self.index -= 1
        return self.current()

    def _adjust( self ):
        """
        Make sure our index is sane:
        >>> f = Cycle()
        >>> f.index
        0
        >>> f._adjust()
        >>> f.index
        0
        >>> f.index = 10
        >>> f._adjust()
        >>> f.index
        0
        >>> f.append( 1 )
        >>> f.index
        0
        >>> f._adjust()
        >>> f.index
        0
        >>> f.index = 10
        >>> f._adjust()
        >>> f.index
        0
        >>> f.index = 1
        >>> f._adjust()
        >>> f.index
        0
        >>> f.append( 1 )
        >>> f.append( 2 )
        >>> f.index = 2
        >>> f._adjust()
        >>> f.index
        2
        >>> f.index = 3
        >>> f._adjust()
        >>> f.index
        0
        >>> f.index = -1
        >>> f._adjust()
        >>> f.index
        2
        """
        if self.index >= len( self.items ):
            self.index = 0
        if self.index < 0:
            self.index = len( self.items ) -1

def _test():
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    _test()
    print "DONE"
