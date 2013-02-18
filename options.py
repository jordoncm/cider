# This work is copyright 2011 - 2013 Jordon Mears. All rights reserved.
#
# This file is part of Cider.
#
# Cider is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# Cider is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# Cider. If not, see <http://www.gnu.org/licenses/>.
"""Module containing and processing command line options."""

import optparse

PARSER = optparse.OptionParser(prog = 'cider')
PARSER.add_option('-c', '--config', help ='Path to configuration file.')
PARSER.add_option('-p', '--port', help ='The port to listen on.')
PARSER.add_option(
    '-s',
    '--suppress',
    action = 'store_true',
    help = 'If set, will suppress the attempt to open a browser on launch.'
)
OPTIONS = PARSER.parse_args()[0]

def get(key, default = None):
    """Retrieve an options by its key."""
    if getattr(OPTIONS, key):
        return getattr(OPTIONS, key)
    return default
