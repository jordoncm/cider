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
"""Handlers to manage local filesystem requests."""

import hashlib
import json
from operator import itemgetter
import os
import time
import tornado.template
import tornado.web

import collaborate
import log
import util

class CreateFolderHandler(tornado.web.RequestHandler):
    """Handles the request to create a new folder."""
    def get(self):
        """GET request; takes an argument path as the full path to the folder
        to be created.
        """
        self.set_header('Content-Type', 'application/json')
        try:
            path = self.get_argument('path', '')
            path = path.replace('..', '').strip('/')  # pylint: disable=E1103
            os.mkdir(os.path.join(
                os.path.dirname(__file__),
                util.get_base_path_adjustment(),
                path
            ))
            self.write(json.dumps({
                'success': True
            }))
        except:  # pylint: disable=W0702
            self.write(json.dumps({
                'success': False
            }))

class DownloadHandler(tornado.web.RequestHandler):
    """Handles file download requests."""
    def get(self):
        """GET request; takes an argument file as the full path of the file to
        download.
        """
        the_file = self.get_argument('file', '')
        the_file = the_file.replace('..', '').strip('/')  # pylint: disable=E1103

        if the_file.find('/') != -1:
            file_name = the_file[(the_file.rfind('/') + 1):]
        else:
            file_name = the_file

        try:
            file_handler = open(
                os.path.join(
                    os.path.dirname(__file__),
                    util.get_base_path_adjustment(),
                    the_file
                ),
                'rb'
            )
            data = file_handler.read()
            length = os.path.getsize(os.path.join(
                os.path.dirname(__file__),
                util.get_base_path_adjustment(),
                the_file
            ))
        except Exception as error:  # pylint: disable=W0703
            log.error(error)
            data = None
            length = 0

        self.set_header('Content-Type', 'application/force-download')
        self.set_header(
            'Content-Disposition', 'attachment; filename="' + file_name + '"'
        )
        self.set_header('Content-Length', length)
        self.write(data)

class EditorHandler(tornado.web.RequestHandler):
    """Handles editor requests."""
    def get(self):
        """GET request; takes an argument file as the full path of the file to
        load into the editor.
        """
        the_file = self.get_argument('file', '')
        the_file = the_file.replace('..', '').strip('/')  # pylint: disable=E1103

        if the_file.find('/') != -1:
            file_name = the_file[(the_file.rfind('/') + 1):]
            path = the_file[:the_file.rfind('/')]
            title = '[' + file_name + '] ' + path + ' - Cider'
        else:
            file_name = file
            path = ''
            title = '[' + file_name + '] - Cider'

        try:
            file_handler = open(
                os.path.join(
                    os.path.dirname(__file__),
                    util.get_base_path_adjustment(),
                    the_file
                ),
                'r'
            )
            text = file_handler.read()
            text = text.replace('{', '~' + 'lb').replace('}', '~' + 'rb')

            save_text = 'Saved'
        except Exception as error:  # pylint: disable=W0703
            log.warn(error)
            text = ''
            save_text = 'Save'

        ext = the_file[(the_file.rfind('.') + 1):]
        mode = util.get_mode(ext)
        tab_width = util.get_tab_width(ext)
        markup = util.is_markup(ext)
        text = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

        self.set_header('Content-Type', 'text/html')
        loader = tornado.template.Loader('templates')
        self.write(loader.load('editor.html').generate(
            config=json.dumps({
                'file_name': file_name,
                'path': path,
                'title': title,
                'file': the_file,
                'text': text,
                'mode': mode,
                'tab_width': tab_width,
                'markup': markup,
                'save_text': save_text,
                'extra': '',
                'prefix': '',
                'salt': '',
                'modes': util.MODES
            }),
            title=title,
            modes=util.MODES
        ))

class FileManagerHandler(tornado.web.RequestHandler):
    """Handles the file manager requests."""
    def get(self):
        """GET request; takes path as an argument."""
        path = self.get_argument('path', '')
        path = path.replace('..', '').strip('/')  # pylint: disable=E1103
        title = path + ' - Cider'
        base = util.get_base_path_adjustment()

        files = []
        try:
            file_list = os.listdir(os.path.join(base, path))
            file_list.sort(key=lambda x: x.encode().lower())

            for i in range(len(file_list)):
                try:
                    the_file = os.path.join(base, path, file_list[i])
                    is_file = os.path.isfile(the_file)
                    confirm = ''
                    if is_file and os.path.getsize(the_file) > 10485760:
                        confirm = 'large'
                    if is_file and not util.is_text_file(the_file):
                        confirm = 'binary'
                    files.append({
                        'name': file_list[i],
                        'is_file': is_file,
                        'confirm': confirm
                    })
                except IOError as error:
                    log.warn(error)

            files = sorted(files, key=itemgetter('is_file'))
        except Exception as error:  # pylint: disable=W0703
            log.warn(error)

        up = ''
        if path != '' and path.rfind('/') > -1:
            up = path[:path.rfind('/')]

        self.set_header('Content-Type', 'text/html')
        loader = tornado.template.Loader('templates')
        self.write(loader.load('file-manager.html').generate(
            title=title,
            config=json.dumps({
                'base': base,
                'path': path,
                'files_list': files,
                'up': up,
                'folder': self.get_argument('folder', ''),
                'extra': '',
                'prefix': ''
            })
        ))

class SaveFileHandler(tornado.web.RequestHandler):
    """Handles file saving requests."""
    def get(self):
        """GET request; takes arguments file and text for the path of the file
        to save and the content to put in it.
        """
        self.set_header('Content-Type', 'application/json')
        try:
            the_file = self.get_argument('file', '')
            the_file = the_file.replace('..', '').strip('/')  # pylint: disable=E1103
            text = self.get_argument('text', strip=False)
            text = text.encode('ascii', 'replace')  # pylint: disable=E1103
            file_handler = open(
                os.path.join(
                    os.path.dirname(__file__),
                    util.get_base_path_adjustment(),
                    the_file
                ),
                'w'
            )
            file_handler.write(text)
            file_handler.close()

            try:
                salt = self.get_argument('salt', '')
                diff_id = hashlib.sha224(salt + file).hexdigest()
                collaborate.FileDiffManager().remove_diff(diff_id)
                collaborate.FileDiffManager().create_diff(diff_id)
                collaborate.FileSessionManager().broadcast(
                    the_file,
                    salt,
                    {'t': 's'}
                )
            except:  # pylint: disable=W0702
                pass

            success = True
            notification = 'last saved: ' + time.strftime('%Y-%m-%d %H:%M:%S')
        except Exception as error:  # pylint: disable=W0703
            log.error(error)
            success = False
            notification = 'save failed'

        self.write(json.dumps({
            'success': success,
            'notification': notification
        }))

    def post(self):
        """Post request; same logic as the GET request."""
        self.get()
