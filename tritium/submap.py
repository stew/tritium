# submap.py -- a keyboard "submap" for creating prefix keybindings
#
# Copyright 2007 Mike O'Connor <stew@vireo.org>
#
# Portions of code plagarized from plwm's panes.py which is
#    Copyright (C) 2001  Mike Meyer <mwm@mired.org>
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
import time
from plwm import wmanager, event, keys
from Xlib import X
log = logging.getLogger()


class SubMap(keys.KeyGrabKeyboard):
    def _keyevent(self, event):
	# Store key press time (approximate to the current time
	# as the X event.time isn't synced with that)
	self.last_key_time = time.time()

        log.debug('keys: %s %d %d, keyhandler %s' % (event.__class__.__name__, event.detail, event.state, self))

	if event.type != X.KeyPress:
            return
	
	# First check for an exact modifier match
	match = keys.hash_keycode(event.detail, event.state)
        log.debug( "haskey?" )
	if self.bindings.has_key(match):
            log.debug( "haskey" )
	    self.bindings[match](event)

	# else, check for an AnyModifier key
	else:
	    match = keys.hash_keycode(event.detail, X.AnyModifier)
	    if self.bindings.has_key(match):
		self.bindings[match](event)

        self._cleanup()


