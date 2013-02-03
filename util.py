# This work is copyright 2012 - 2013 Jordon Mears. All rights reserved.
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

"""
Support functions for Cider.
"""

import getpass
import json
import string
import sys


def get_configuration_value(key, default=None):
    """Fetches a configuration value from the configuration file."""
    try:
        return json.loads(open('configuration.json').read())[key]
    except:
        return default


def is_text_file(file):
    """Tests a file by looking at the beginning of the file for irregular
    characters.
    """
    sample = open(file).read(512)
    if not sample:
        return True
    if '\0' in sample:
        return False
    text = sample.translate(
        string.maketrans('', ''),
        ''.join(map(chr, range(32, 127)) + list('\n\r\t\b'))
    )
    if len(text) / len(sample) > 0.30:
        return False
    return True


def get_base_path_adjustment():
    """Generates a base path for reading files.

    Looks for a configuration value first and then defaults the home directory
    of the user running the Cider process.
    """
    base_path_adjustment = get_configuration_value('basePathAdjustment')
    if base_path_adjustment is None:
        base_path_adjustment = '..'
    elif base_path_adjustment == '~':
        if 'darwin' in sys.platform:
            base_path_adjustment = '/Users/' + getpass.getuser()
        elif 'win' in sys.platform:
            base_path_adjustment = 'C:\\Users\\' + getpass.getuser()
        else:
            base_path_adjustment = '/home/' + getpass.getuser()
    return base_path_adjustment


def get_mode(ext):
    """Returns the suggested highlight mode."""
    mode, tab_width, markup = get_mode_tab_width_markup(ext)
    return mode


def get_mode_tab_width_markup(ext):
    """Looks at the extension and returns recommended highlight mode, tab width
    and markup.
    """
    tab_width = 4
    markup = False

    if ext == 'c' or ext == 'cpp' or ext == 'h' or ext == 'hpp':
        mode = 'c_cpp'
    elif ext == 'clj':
        mode = 'clojure'
    elif ext == 'coffee':
        mode = 'coffee'
    elif ext == 'cfc' or ext == 'cfm':
        mode = 'coldfusion'
    elif ext == 'cs':
        mode = 'csharp'
    elif ext == 'css':
        mode = 'css'
    elif ext == 'go':
        mode = 'go'
    elif ext == 'groovy':
        mode = 'groovy'
    elif ext == 'hx':
        mode = 'haxe'
    elif ext == 'htm' or ext == 'html' or ext == 'mustache' or ext == 'tpl' or ext == 'shtml':
        mode = 'html'
        tab_width = 2
        markup = True
    elif ext == 'java':
        mode = 'java'
    elif ext == 'js':
        mode = 'javascript'
    elif ext == 'json':
        mode = 'json'
    elif ext == 'tex':
        mode = 'latex'
    elif ext == 'less':
        mode = 'less'
    elif ext == 'liquid':
        mode = 'liquid'
    elif ext == 'lua':
        mode = 'lua'
    elif ext == 'markdown' or ext == 'mdown' or ext == 'mdown' or ext == 'md' or ext == 'mkd' or ext == 'mkdn':
        mode = 'markdown'
    elif ext == 'ocaml' or ext == 'ml' or ext == 'mli':
        mode = 'ocaml'
    elif ext == 'pl' or ext == 'pm' or ext == 't':
        mode = 'perl'
    elif ext == 'pgsql':
        mode = 'pgsql'
    elif ext == 'php' or ext == 'inc' or ext == 'phtml' or ext == 'phps':
        mode = 'php'
    elif ext == 'ps1':
        mode = 'powershell'
    elif ext == 'py' or ext == 'pyw':
        mode = 'python'
    elif ext == 'rb' or ext == 'rbw':
        mode = 'ruby'
    elif ext == 'scad':
        mode = 'scad'
    elif ext == 'scala':
        mode = 'scala'
    elif ext == 'scss':
        mode = 'scss'
    elif ext == 'sh':
        mode = 'sh'
    elif ext == 'sql':
        mode = 'sql'
    elif ext == 'svg':
        mode = 'svg'
        tab_width = 2
        markup = True
    elif ext == 'textile':
        mode = 'textile'
    elif ext == 'xml' or ext == 'kml':
        mode = 'xml'
        tab_width = 2
        markup = True
    elif ext == 'xq' or ext == 'xqy' or ext == 'xquery':
        mode = 'xquery'
    else:
        mode = 'text'

    return mode, tab_width, markup


def get_tab_width(ext):
    """Returns recommended tab width."""
    mode, tab_width, markup = get_mode_tab_width_markup(ext)
    return tab_width


def is_markup(ext):
    """Returns True if the extension is a markup file, False otherwise."""
    mode, tab_width, markup = get_mode_tab_width_markup(ext)
    return markup
