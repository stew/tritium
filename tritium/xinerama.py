from Xlib.protocol import request, rq

XineramaScreenInfo = rq.Struct(
    rq.Int16('x_org'),
    rq.Int16('y_org'),
    rq.Card16('width'),
    rq.Card16('height') )

class XineramaQueryScreenInfo(rq.ReplyRequest):
    _request = rq.Struct( rq.Card8( 'opcode' ), 
                          rq.Opcode( 5 ), 
                          rq.RequestLength() )

    _reply = rq.Struct( rq.Int8( 'type' ),
                        rq.Pad( 1 ),
                        rq.Card16( 'sequence_number' ),
                        rq.Card32( 'length' ),
                        rq.LengthOf( 'screen_info', 4 ), 
                        rq.Pad( 20 ),
                        rq.List( 'screen_info', XineramaScreenInfo ) )

class Xinerama(object):
    def __init__( self, display ):
        self.extension = display.query_extension( "XINERAMA" )
    
    def get_screen_info( self ):
        if self.extension:
            infos = XineramaQueryScreenInfo( opcode = self.extension.major_opcode )
            if infos:
                return infos.screen_info

