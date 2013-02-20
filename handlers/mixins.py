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
"""Shared methods for handler connection types."""

import hashlib
import json
from operator import itemgetter
import time
import tornado.template

import collaborate
import log
import util

class BaseMixin(object):
    """Shared methods between handler actions."""
    def get_path(self):
        """Returns the path from the request argument."""
        path = self.get_argument('path', '')
        return path.replace('..', '').strip('/')  # pylint: disable=E1103

    def get_file(self):
        """Returns the file from the request argument."""
        the_file = self.get_argument('file', '')
        return the_file.replace('..', '').strip('/')  # pylint: disable=E1103

class CreateFolder(BaseMixin):
    """Shared methods for creating a folder."""
    # pylint: disable=E1101
    def do_success(self):
        """Execute the success response."""
        self.set_header('Content-Type', 'application/json')
        self.finish(json.dumps({'success': True}))

    def do_failure(self):
        """Execute the failure response."""
        self.set_header('Content-Type', 'application/json')
        self.finish(json.dumps({'success': False}))

class Download(BaseMixin):
    """Shared methods for downloading files."""
    # pylint: disable=E1101
    def do_headers(self, basename, length = None):
        """Outputs the force download headers and the content name."""
        self.set_header('Content-Type', 'application/force-download')
        self.set_header(
            'Content-Disposition',
            'attachment; filename="' + basename + '"'
        )
        if length is not None:
            self.set_header('Content-Length', length)

class Editor(BaseMixin):
    """Shared methods for editing files."""
    # pylint: disable=E1101
    def find_title(self, path, basename):
        """Returns page title based on the path and basename."""
        title = '[' + basename + '] - Cider'
        if path:
            title = '[' + basename + '] ' + path + ' - Cider'
        return title

    def do_output(self, text = '', prefix = '', salt = '', extra = '', saved = None, read_only = False):
        """Builds response, outputs headers, renders the template and outputs
        the response.
        """
        filename = self.get_file()
        path = util.find_path(filename)
        basename = util.find_base(filename)
        title = self.find_title(path, basename)

        save_text = 'Save'
        if saved is None:
            # Save status was not specified as an argument, perform test on
            # text.
            if text:
                save_text = 'Saved'
        elif saved:
            # The saved argument indicates the file is saved.
            save_text = 'Saved'

        text = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        ext = util.find_extension(filename)
        mode = util.get_mode(ext)
        tab_width = util.get_tab_width(ext)
        markup = util.is_markup(ext)

        self.set_header('Content-Type', 'text/html')
        loader = tornado.template.Loader('templates')
        self.finish(loader.load('editor.html').generate(
            config = json.dumps({
                'file_name': basename,
                'path': path,
                'title': title,
                'file': filename,
                'text': text,
                'mode': mode,
                'tab_width': tab_width,
                'markup': markup,
                'save_text': save_text,
                'extra': extra,
                'prefix': prefix,
                'salt': salt,
                'modes': util.MODES,
                'read_only': read_only
            }),
            title = title,
            modes = util.MODES
        ))

class FileManager(BaseMixin):
    """Shared methods for the file manager."""
    # pylint: disable=E1101
    def find_title(self, path):
        """Returns page title based on the path."""
        return path + ' - Cider'

    def do_output(self, files, base = '', prefix = '', extra = ''):
        """Renders the file manager template based on a given list of files."""
        files = sorted(files, key=lambda x: x['name'].encode().lower())
        files = sorted(files, key=itemgetter('is_file'))

        path = self.get_path()
        title = self.find_title(path)

        up = ''  # pylint: disable=C0103
        if path != '' and path.rfind('/') > -1:
            up = path[:path.rfind('/')]  # pylint: disable=C0103

        self.set_header('Content-Type', 'text/html')
        loader = tornado.template.Loader('templates')
        self.finish(loader.load('file-manager.html').generate(
            title=title,
            config=json.dumps({
                'base': base,
                'path': path,
                'files_list': files,
                'up': up,
                'folder': self.get_argument('folder', ''),
                'extra': extra,
                'prefix': prefix
            })
        ))

class SaveFile(BaseMixin):
    """Shared methods for saving files."""
    # pylint: disable=E1101
    def get_text(self):
        """"Returns the file from the request argument."""
        text = self.get_argument('text', strip = False)
        # TODO: Need to figure out proper unicode support.
        return text.encode('ascii', 'replace')  # pylint: disable=E1103

    def get_salt(self):
        """Returns the salt from the request argument."""
        return self.get_argument('salt', '')

    def broadcast_save(self, filename, salt = ''):
        """Broadcasts the file save to all collaborators."""
        try:
            diff_id = hashlib.sha224(str(salt) + filename).hexdigest()
            collaborate.FileDiffManager().remove_diff(diff_id)
            collaborate.FileDiffManager().create_diff(diff_id)
            collaborate.FileSessionManager().broadcast(
                filename,
                salt,
                {'t': 's'}
            )
        except:  # pylint: disable=W0702
            log.error('Broadcasting save error.')

    def do_success(self):
        """Execute the success response."""
        self.set_header('Content-Type', 'application/json')
        self.finish(json.dumps({
            'success': True,
            'notification': 'last saved: ' + time.strftime('%Y-%m-%d %H:%M:%S')
        }))

    def do_failure(self):
        """Execute the failure response."""
        self.set_header('Content-Type', 'application/json')
        self.finish(json.dumps({
            'success': False,
            'notification': 'save failed'
        }))
