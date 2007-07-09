# -*-python-*-

from Xlib import XK
from plwm import keys
from tritium.submap import SubMap
import logging
log = logging.getLogger()

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

class TritiumKeys(keys.KeyHandler):
    class CtrlJ( SubMap ):
        def Any_c( self, event ):
            self.wm.current_frame().screen.system( "x-terminal-emulator &")

        def Any_n( self, event ):
            self.wm.current_frame().next()

        def Any_p( self, event ):
            self.wm.current_frame().prev()

	def k( self, event ):
            self.wm.current_frame().windows.current().close()

	def C_k( self, event ):
            self.wm.current_frame().windows.current().close()

	def S_k( self, event ):
            self.wm.current_frame().windows.current().kill()

        def Any_x( self, event ):
            log.debug( "remove_split????" )
            self.wm.current_frame().remove_split()
            log.debug( "after unsplit command: " + str( self.wm.workspaces.current() ) )

        def _1( self, event ):
            self.wm.current_frame().set_current( self.wm.display.keycode_to_keysym(event.detail, 0) - XK.XK_1 )

        Any_1 = Any_2 = Any_3 = Any_4 = Any_5 = Any_6 = Any_7 = Any_9 = _1 

    class NoKeys( keys.KeyGrabKeyboard ):
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
        self.wm.new_workspace( self.wm.current_frame().screen, False, "0" )

    def S_F9( self, event ):
        self.wm.new_workspace( self.wm.current_frame().screen, True, "0" )

    def M4_F1( self, event ):
        self.wm.set_current_workspace( self.wm.display.keycode_to_keysym(event.detail, 0) - XK.XK_F1 )

    M4_F2 = M4_F3 = M4_F4 = M4_F5 = M4_F6 = M4_F7 = M4_F8 = M4_F9 = M4_F1

    def M4_n( self, event ):
        self.wm.current_frame().next()

    def M4_p( self, event ):
        self.wm.current_frame().prev()

    def M4_s( self, event ):
        self.wm.current_frame().split_vertically()
        log.debug( "after split command: " + str( self.wm.workspaces.current() ) )

    def M4_S_s( self, event ):
        self.wm.current_frame().split_horizontally()
        log.debug( "after split command: " + str( self.wm.workspaces.current() ) )

    def M4_h( self, event ):
        self.wm.current_frame().prev()

    def M4_l( self, event ):
        self.wm.current_frame().next()

    def C_j( self, event ):
        log.debug( "ctr-j" )
        self.CtrlJ( self.wm, event.time )

    def S_M4_h( self, event ):
        cw = self.wm.current_frame().windows.current()
        cw.move_to_frame( cw.frame.parent_frame.find_frame_left( cw.frame ) )

    def S_M4_l( self, event ):
        cw = self.wm.current_frame().windows.current()
        cw.move_to_frame( cw.frame.parent_frame.find_frame_right( cw.frame ) )

    def S_M4_j( self, event ):
        cw = self.wm.current_frame().windows.current()
        cw.move_to_frame( cw.frame.parent_frame.find_frame_below( cw.frame ) )

    def S_M4_k( self, event ):
        cw = self.wm.current_frame().windows.current()
        cw.move_to_frame( cw.frame.parent_frame.find_frame_above( cw.frame ) )

    def M4_Tab( self, event ):
        self.wm.workspaces.current().next_frame()
        
    def F11( self, event ):
        self.NoKeys( self.wm, event.time )

    def F12( self, event ):
        self.wm.Debian_menu()
        
