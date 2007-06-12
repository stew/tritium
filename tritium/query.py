# query.py -- promt the user for input
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
from plwm import input, message

log = logging.getLogger()

class MyEditHandler(input.InputKeyHandler):
    Any_Escape = C_g = input.InputKeyHandler._abort
    Any_Return = input.InputKeyHandler._done
    Any_Enter = input.InputKeyHandler._done
    Any_BackSpace = C_h = input.InputKeyHandler._delback
    C_d = input.InputKeyHandler._delforw
    C_b = input.InputKeyHandler._back
    C_f = input.InputKeyHandler._forw
    C_k = input.InputKeyHandler._deltoend
    C_a = input.InputKeyHandler._begin
    C_e = input.InputKeyHandler._end
    C_y = input.InputKeyHandler._paste
    C_p = input.InputKeyHandler._history_up
    C_n = input.InputKeyHandler._history_down
    Up = input.InputKeyHandler._history_up
    Down = input.InputKeyHandler._history_down
    Left = input.InputKeyHandler._back
    Right = input.InputKeyHandler._forw

class query:
    "base class for queries"
    def __init__( self, prompt ):
        self.history = []
        self.prompt = prompt
        
    def query( self, frame ):
        self.system = frame.screen.system
        window = input.inputWindow( self.prompt, frame.screen, length = 64)
        window.read( self, MyEditHandler, self.history, frame.x, frame.y )

    def __call__( self, string ):
        self.history.append( string )

class runCommand( query ):
    "Read a string from the user, and run it as a command."

    def __init__( self ):
        query.__init__( self, "Run: " )

    def __call__(self, string):
        query.__call__( self, string )
        self.system(string + " &")

class runCommandInXterm( query ):
    "Read a string from the user, and run it as a command."

    def __init__( self ):
        query.__init__( self, "Run in terminal emulator: " )

    def __call__( self, string):
        query.__call__( self, string )
        self.system( "x-terminal-emulator -e \"" + string + "\" &")

class runSSH( query ):
    "Read a hostname from from the user, and ssh to it in a terminal."
    def __init__( self ):
        query.__init__( self, "ssh: " )

    def __call__( self, string):
        query.__call__( self, string )
        self.system("x-terminal-emulator -e ssh " + string + " &")

class runPython( query ):
    "Read a hostname from from the user, and ssh to it in a terminal."
    def __init__( self ):
        query.__init__( self, ">>> " )

    def query( self, frame ):
        query.query( self, frame )
	self.wm = frame.wm
        

    def __call__( self, string):
        query.__call__( self, string )
        exec string in {'wm': self.wm}

class runMan( query ):
    """
    Read manpage from the user, and display the manpage in a terminal emulator.
    """
    def __init__( self ):
        query.__init__( self, "man: " )

    def __call__( self, string):
        query.__call__( self, string )
        self.system("x-terminal-emulator -e man " + string + " &")

