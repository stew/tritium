class TritiumLayout:
    def screen_0( screen ):
        screen.wm.new_workspace( screen, False, "0" )
        screen.wm.new_workspace( screen, False, "1" )
        screen.wm.set_current_workspace( 0 )

    staticmethod( screen_0 )
