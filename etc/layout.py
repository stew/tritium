import re
import logging
from tritium import workspace,dock
from Xlib import X

log = logging.getLogger()

class TritiumLayout(object):

    def screen_0( self, screen ):
        """ 
        screen_0 is called when the screen is first initialized.
        (screen_1, screen_2, etc will be called for subsequent screens).
        This gives us a chance to setup workspaces / frames 
        """

        wm = screen.wm


        # the following allocates a 25 pixel area at the bottom of the
        # screen where clients marked with "dockapp=True" will be placed.
        # I use this to run a gnome-panel
        screen.set_dock_area( dock.BOTTOM, 25 )

        wm.new_workspace( screen, workspace.TABBED, "shell" )
        wm.new_workspace( screen, workspace.TABBED, "client" )
        wm.new_workspace( screen, workspace.TABBED, "emacs" )
        wm.new_workspace( screen, workspace.TABBED, "web" )

        screen.wm.set_current_workspace( 0 )
        wm.current_frame().split_horizontally()

    gnome_panel_re = re.compile( 'Gnome-panel',re.IGNORECASE )

    def which_frame( self, client ):
        """
        which_frame is called for each new client that is created.  It
        gives us a chance to decide where the new client should be placed
        """
        (appname, appclass) = client.window.get_wm_class()

        if( "Conky" == appclass or self.gnome_panel_re.match( appclass ) ):
            client.dockapp = True
            return None

        # By default, we return None, which causes the window to show
        # up in the current frame
        return None
    

# Here is the which_frame implementation I use, which shows how you
# can map new clients to particular workspaces or frames
#  
#     xterm_re = re.compile( 'xterm',re.IGNORECASE )
#     firefox_re = re.compile( 'firefox',re.IGNORECASE )
#     emacs_re = re.compile( 'emacs',re.IGNORECASE )
#     music_re = re.compile( 'music',re.IGNORECASE )
#     def which_frame( self, client ):
#         """
#         which_frame is called for each new client that is created.  It
#         gives us a chance to decide where the new client should be placed
#         """
#         (appname, appclass) = client.window.get_wm_class()

#         if( self.gnome_panel_re.match( appclass ) ):
#             client.dockapp = True

#         if( self.firefox_re.match( appclass ) ):
#             ws = client.wm.get_workspace_by_name( "web" )
#             if ws:
#                 return ws.current_frame

#         elif( self.emacs_re.match( appclass ) ):
#             ws = client.wm.get_workspace_by_name( "emacs" )
#             if ws:
#                 return ws.current_frame

#         elif( self.music_re.match( appname ) ):
#             ws = client.wm.get_workspace_by_name( "client" )
#             if ws:
#                 return ws.current_frame
