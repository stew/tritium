""" Setup script for tritium

Just run "python setup.py install" to install tritium
Iron setup script

Copyright (C) 2007,2008 Mike O'Connor <stew@vireo.org>
 
This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You can find the full GNU General Public Licence at
  http://www.gnu.org/licenses/gpl.html
or included with your favourite Linux Distribution.
"""

#from setuptools import setup
from distutils.core import setup
import tritium


# Call the setup() routine which does most of the work
setup( name             = tritium.__distname__,
       version          = tritium.__version__,
       description      = tritium.__description__,
       long_description = tritium.__long_description__,
       author           = tritium.__author__,
       author_email     = tritium.__email__,
       url              = tritium.__url__,
       license          = tritium.__license__,
       packages         = ['tritium', 'tritium.frame'],
       scripts          = ['bin/tritium'],
       data_files       = [ ('/etc/X11/tritium/', ['etc/keys.py', 'etc/layout.py']),
                            ('share/applications', ['extras/tritium.desktop']),
                            ],

# why, oh why, can't i make this work
#        entry_points="""
#             [distutils.commands]
#             install_config = tritium.install_config:install_config
#         """,
#        entry_points = {
#         "distutils.commands": [
#             "install_config = install_config:install_config",
#             ],
#         "distutils.setup_keywords": [
#             "config_files = install_config:install_config",
            

#             ],
#         },
)
