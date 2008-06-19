# -*-python-*-

import sys
from Xlib import XK
from plwm import keys
from tritium.submap import SubMap
import logging
log = logging.getLogger()
from tritium.identify import IdentifyWindow
from tritium.workspace import Workspace

#from tritium.frame import SplitFrame
from tritium.frame.split import SplitFrame

            
"""
 This class MUST be named "TritiumKeys" it will define the keybindings for tritium.

 Binding a key is done by declaring a function with the name of the
 keysym you are binding. A function named 'k' will be called when a
 key event is received for the 'k' key.  Modifier keys can preceed the
 keysym, separated by underscores (_).

 s means shift
 c means control
 m means meta (modifier 1)
 m1,m2,m3,m4,m5 mean Mod1,Mod2,Mod3,Mod4

 The case and order of the modifiers is not important

 Return
 C_Right
 C_M_F1

"""

def find_split( frame, vertical ):
    """
    find a vertical or horizontal split that can be resized
    if none are found, return None
    """

    if isinstance( frame, Workspace):
        return None
    if isinstance( frame, SplitFrame) and frame.vertical == vertical:
        return frame
    else: 
        return find_split( frame.tritium_parent, vertical )

class TritiumKeys(keys.KeyHandler):
    def __init__( self, a ):
        keys.KeyHandler.__init__( self, a )
        self.wii = None

    class ResizeMap( SubMap ):
        """
        use the home row keys to resize a SplitFrame
        """

        def __init__( self, wm, time, vertical ):
            SubMap.__init__( self, wm, time )
            self.vertical = vertical

        pct_map = { XK.XK_a : .1,
                    XK.XK_s : .2,
                    XK.XK_d : .3,
                    XK.XK_f : .4,
                    XK.XK_g : .5,
                    XK.XK_h : .6,
                    XK.XK_j : .7,
                    XK.XK_k : .8,
                    XK.XK_l : .9,
                    }
        
        def Any_a( self, event ):
            f = find_split( self.wm.current_frame(), self.vertical )
            if f:
                f.resize_fraction( self.pct_map[ self.wm.display.keycode_to_keysym(event.detail, 0) ] )

        Any_s = Any_d = Any_f = Any_g = Any_h = Any_j = Any_k = Any_l = Any_a


    class CtrlJ( SubMap ):
        def Any_c( self, event ):
            self.wm.current_frame().screen.system( "x-terminal-emulator &")

        def Any_n( self, event ):
            self.wm.current_frame().next()

        def Any_p( self, event ):
            self.wm.current_frame().prev()

	def Any_c( self, event ):
            self.wm.current_frame().windows.current().delete()

	def Any_k( self, event ):
            self.wm.current_frame().windows.current().destroy()

        def Any_x( self, event ):
            self.wm.current_frame().remove_split()

        def _1( self, event ):
            self.wm.current_frame().set_current( self.wm.display.keycode_to_keysym(event.detail, 0) - XK.XK_1 )

        Any_1 = Any_2 = Any_3 = Any_4 = Any_5 = Any_6 = Any_7 = Any_9 = _1 

    class NoKeys( keys.KeyGrabKeyboard ):
        """
        Ungrab all keys except one so that the window manager 'gets
        out of your way'.
        """
        F11 = keys.KeyGrabKeyboard._timeout

    def F1( self, event ):
        self.wm.runMan.query( self.wm.current_frame() )
    
    def F2( self, event ):
        self.wm.current_frame().screen.system( "x-terminal-emulator &")

    def F3( self, event ):
        self.wm.runCommand.query( self.wm.current_frame() )

    def C_F3( self, event ):
        self.wm.runPython.query( self.wm.current_frame() )

    def S_F3( self, event ):
        self.wm.runCommandInXterm.query( self.wm.current_frame() )

    def F4( self, event ):
        self.wm.runSSH.query( self.wm.current_frame() )

    def F9( self, event ):
        self.wm.new_workspace( self.wm.current_frame().screen )

    def S_F9( self, event ):
        self.wm.new_workspace( self.wm.current_frame().screen, True )

    def M4_F1( self, event ):
        self.wm.set_current_workspace( self.wm.display.keycode_to_keysym(event.detail, 0) - XK.XK_F1 )

    M4_F2 = M4_F3 = M4_F4 = M4_F5 = M4_F6 = M4_F7 = M4_F8 = M4_F9 = M4_F1

    def M4_w( self, event ):
        self.wm.current_frame().windows.current().delete()

    def M4_n( self, event ):
        self.wm.current_frame().next()

    def M4_p( self, event ):
        self.wm.current_frame().prev()

    def M4_s( self, event ):
        self.wm.current_frame().split_vertically()

    def M4_S_s( self, event ):
        self.wm.current_frame().split_horizontally()

    def M4_h( self, event ):
        self.wm.current_frame().prev()

    def M4_l( self, event ):
        self.wm.current_frame().next()

    def C_j( self, event ):
        self.CtrlJ( self.wm, event.time )

    def M4_r( self, event ):
        self.ResizeMap( self.wm, event.time, True )

    def M4_e( self, event ):
        self.ResizeMap( self.wm, event.time, False )

    def M4_Right( self, event ):
        f = find_split( self.wm.current_frame(), False )
        if( f ):
            f.resize_incr( 5 )

    def M4_Left( self, event ):
        f = find_split( self.wm.current_frame(), False )
        if( f ):
            f.resize_incr( -5 )

    def M4_Down( self, event ):
        f = find_split( self.wm.current_frame(), True )
        if( f ):
            f.resize_incr( 5 )

    def M4_Up( self, event ):
        f = find_split( self.wm.current_frame(), True )
        if( f ):
            f.resize_incr( -5 )

    def M4_k( self, event ):
        old = self.wm.current_frame()
        new = old.tritium_parent.find_frame_above( old )
        old.deactivate()
        new.activate();

    def M4_j( self, event ):
        old = self.wm.current_frame()
        new = old.tritium_parent.find_frame_below( old )
        old.deactivate()
        new.activate();         

    def M4_semicolon( self, event ):
        old = self.wm.current_frame()
        new = old.tritium_parent.find_frame_right( old )
        old.deactivate()
        new.activate();

    def M4_g( self, event ):
        old = self.wm.current_frame()
        new = old.tritium_parent.find_frame_left( old )
        old.deactivate()
        new.activate();

    def S_M4_h( self, event ):
        cw = self.wm.current_frame().windows.current()
        f = cw.frame.tritium_parent.find_frame_left( cw.frame )
        if f:
            cw.move_to_frame( cw.frame.tritium_parent.find_frame_left( cw.frame ) )

    def S_M4_l( self, event ):
        cw = self.wm.current_frame().windows.current()
        f = cw.frame.tritium_parent.find_frame_right( cw.frame )
        if f:
            cw.move_to_frame( f )

    def S_M4_j( self, event ):
        cw = self.wm.current_frame().windows.current()
        f = cw.frame.tritium_parent.find_frame_below( cw.frame )
        if f:
            cw.move_to_frame( f )

    def S_M4_k( self, event ):
        cw = self.wm.current_frame().windows.current()
        f = cw.frame.tritium_parent.find_frame_above( cw.frame )
        if f:
            cw.move_to_frame( f )

    def M4_Tab( self, event ):
        self.wm.workspaces.current().next_frame()

    def M4_i( self, event ):
        IdentifyWindow( self.wm.current_frame().windows.current(), event.time )

    def F11(self, evt):
	wmanager.debug('keys', 'dropping keygrabs temporarily')

	# First release all our grabs.  They will be reinstalled
	# when BypassHandler exits
	
	self._ungrab()
	BypassHandler(self)

    def F12( self, event ):
        self.wm.Debian_menu()
    
    def F13( self, event ):
        self.wm.set_current_workspace( self.wm.workspaces.index - 1 )

    def F14( self, event ):
        self.wm.set_current_workspace( self.wm.workspaces.index + 1 )
    
