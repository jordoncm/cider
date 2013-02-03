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
"""Support functions for Cider."""

import getpass
import json
import string
import sys

DEFAULT_MODE = 'text'
DEFAULT_IS_MARKUP = False
DEFAULT_TAB_WIDTH = 4

# A mapping of file extensions to suggested editor modes and tab width.
MODES = [
    (['abap'], {'display_name': 'ABAP', 'mode': 'abap'}),
    ([''], {'display_name': 'AsciiDoc', 'mode': 'asciidoc'}),
    (['c', 'cpp', 'h', 'hpp'], {'display_name': 'C/C++', 'mode': 'c_cpp'}),
    (['clj'], {'display_name': 'Clojure', 'mode': 'clojure'}),
    (['coffee'], {'display_name': 'CoffeeScript', 'mode': 'coffee'}),
    (['cfc', 'cfm'], {'display_name': 'ColdFusion', 'mode': 'coldfusion'}),
    (['cs'], {'display_name': 'C#', 'mode': 'csharp'}),
    (['css', 'gss'], {'display_name': 'CSS', 'mode': 'css'}),
    (['dart'], {'display_name': 'Dart', 'mode': 'dart'}),
    (['diff'], {'display_name': 'diff', 'mode': 'diff'}),
    (['dot'], {'display_name': 'Dot', 'mode': 'dot'}),
    (
        ['glsl', 'frag', 'glslf', 'glslv', 'shader', 'vert'],
        {'display_name': 'OpenGL Shading', 'mode': 'glsl'}
    ),
    (['go'], {'display_name': 'Go', 'mode': 'golang'}),
    (['groovy'], {'display_name': 'Groovy', 'mode': 'groovy'}),
    (['haml'], {'display_name': 'Haml', 'mode': 'haml'}),
    (['hx'], {'display_name': 'Haxe', 'mode': 'haxe'}),
    (
        ['htm', 'html', 'mustache', 'tpl', 'shtml'],
        {'display_name': 'HTML', 'markup': True, 'mode': 'html', 'tab_width': 2}
    ),
    (['jade'], {'display_name': 'Jade', 'mode': 'jade'}),
    (['java'], {'display_name': 'Java', 'mode': 'java'}),
    (['js'], {'display_name': 'JavaScript', 'mode': 'javascript'}),
    (['json'], {'display_name': 'JSON', 'mode': 'json'}),
    (['jsp'], {'display_name': 'JavaServer Pages', 'mode': 'jsp'}),
    (['jsx'], {'display_name': 'JSX', 'mode': 'jsx'}),
    (['tex'], {'display_name': 'LaTeX', 'mode': 'latex'}),
    (['less'], {'display_name': 'LESS', 'mode': 'less'}),
    (['liquid'], {'display_name': 'Liquid', 'mode': 'liquid'}),
    (['lisp', 'lsp'], {'display_name': 'Lisp', 'mode': 'lisp'}),
    (['lua'], {'display_name': 'Lua', 'mode': 'lua'}),
    (['lp'], {'display_name': 'Lua Pages', 'mode': 'luapage'}),
    (
        [
            'cfs',
            'fnm',
            'fdx',
            'fdt',
            'tis',
            'tii',
            'frq',
            'prx',
            'nrm',
            'tvx',
            'tvd',
            'tvf',
            'del'
        ],
        {'display_name': 'Lucene', 'mode': 'lucene'}
    ),
    ([''], {'display_name': 'Makefile', 'mode': 'makefile'}),
    (
        ['markdown', 'mdown', 'md', 'mkd', 'mkdn'],
        {'display_name': 'Markdown', 'mode': 'markdown'}
    ),
    (['h', 'm', 'mm'], {'display_name': 'Objective-C', 'mode': 'objectivec'}),
    (['ocaml', 'ml', 'mli'], {'display_name': 'OCaml', 'mode': 'ocaml'}),
    (['pl', 'pm', 't'], {'display_name': 'Perl', 'mode': 'perl'}),
    (['pgsql'], {'display_name': 'pgSQL', 'mode': 'pgsql'}),
    (['php', 'inc', 'phtml', 'phps'], {'display_name': 'PHP', 'mode': 'php'}),
    (['ps1'], {'display_name': 'PowerShell', 'mode': 'powershell'}),
    (['py', 'pyw'], {'display_name': 'Python', 'mode': 'python'}),
    (['r'], {'display_name': 'R', 'mode': 'r'}),
    (['rdoc'], {'display_name': 'RDoc', 'mode': 'rdoc'}),
    (['erb', 'rhtml'], {'display_name': 'eRuby', 'mode': 'rhtml'}),
    (['rb', 'rbw'], {'display_name': 'Ruby', 'mode': 'ruby'}),
    (['scad'], {'display_name': 'OpenSCAD', 'mode': 'scad'}),
    (['scala'], {'display_name': 'Scala', 'mode': 'scala'}),
    (['scss'], {'display_name': 'Sass', 'mode': 'scss'}),
    (['sh'], {'display_name': 'Shell/Bash', 'mode': 'sh'}),
    (['sql'], {'display_name': 'SQL', 'mode': 'sql'}),
    (['styl'], {'display_name': 'Stylus', 'mode': 'stylus'}),
    (
        ['svg'],
        {'display_name': 'SVG', 'markup': True, 'mode': 'svg', 'tab_width': 2}
    ),
    (['tcl'], {'display_name': 'Tcl', 'mode': 'tcl'}),
    (['textile'], {'display_name': 'Textile', 'mode': 'textile'}),
    (['ts'], {'display_name': 'TypeScript', 'mode': 'typescript'}),
    (
        ['vbs', 'vbe', 'wsf', 'wsc', 'hta', 'asp'],
        {'display_name': 'VBScript', 'mode': 'vbscript'}
    ),
    (
        ['xml', 'kml'],
        {'display_name': 'XML', 'markup': True, 'mode': 'xml', 'tab_width': 2}
    ),
    (['xq', 'xqy', 'xquery'], {'display_name': 'XQuery', 'mode': 'xquery'}),
    (['yaml'], {'display_name': 'YAML', 'mode': 'yaml'})
]

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

def find_mode_dict(ext):
    """Looks at the extension and returns recommended mode dictionary."""
    if ext:
        for i in MODES:
            if ext.lower() in i[0]:
                return i[1]
    return {}

def get_mode(ext):
    """Returns the suggested highlight mode."""
    return find_mode_dict(ext).get('mode', DEFAULT_MODE)

def get_tab_width(ext):
    """Returns recommended tab width."""
    return find_mode_dict(ext).get('tab_width', DEFAULT_TAB_WIDTH)

def is_markup(ext):
    """Returns True if the extension is a markup file, False otherwise."""
    return find_mode_dict(ext).get('markup', DEFAULT_IS_MARKUP)
