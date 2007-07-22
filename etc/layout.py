import re
import logging
log = logging.getLogger()

class TritiumLayout:

    def screen_0( self, screen ):
        screen.wm.new_workspace( screen, False, "shell" )
        screen.wm.new_workspace( screen, False, "comm" )
        screen.wm.new_workspace( screen, False, "emacs" )
        screen.wm.new_workspace( screen, False, "web" )
        screen.wm.set_current_workspace( 0 )

    xterm_re = re.compile( 'xterm',re.IGNORECASE )
    firefox_re = re.compile( 'firefox',re.IGNORECASE )
    emacs_re = re.compile( 'emacs',re.IGNORECASE )

    def which_frame( self, client ):
        (appname, appclass) = client.window.get_wm_class()

        if( self.firefox_re.match( appclass ) ):
            ws = client.wm.get_workspace_by_name( "web" )
            if ws:
                return ws.current_frame

        elif( self.emacs_re.match( appclass ) ):
            ws = client.wm.get_workspace_by_name( "emacs" )
            if ws:
                return ws.current_frame

        else:
            log.debug( "TritiumLayout.which_frame: %s did not match any re" % appclass )
