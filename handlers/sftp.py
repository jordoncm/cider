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
"""Handlers to manage SFTP requests."""

import hashlib
import json
from operator import itemgetter
import os
import pysftp
import random
import string
import tempfile
import time
import tornado.template
import tornado.web

import collaborate
import log
import util

class BaseHandler(tornado.web.RequestHandler):
    """Base handler of methods to manage SFTP connection."""
    def setup_connection(self):
        """Sets up the connection details as a secure cookie with the client.

        Connection details are kept as a secure cookie so the client is in
        control of the data and no access details are kept with the server.
        """
        user = self.get_argument('sftp_user', 'root')
        if user == '':
            user = 'root'
        path = self.get_argument('sftp_path', '/')
        if path == '':
            path = '/'

        details = {
            'host': self.get_argument('sftp_host', ''),
            'user': user,
            'password': self.get_argument('sftp_password', ''),
            'path': path
        }
        connection_id = ''.join(
            random.choice(string.ascii_uppercase + string.digits)
            for x in range(8)
        )

        self.set_secure_cookie(
            'sftp-' + connection_id,
            json.dumps(details),
            expires_days = None
        )
        return connection_id

    def get_connection_id(self):
        """Returns the connection id based on the request parameter."""
        return str(self.get_argument('connection', '')).upper()

    def get_connection_details(self):
        """Fetches connection details from the cookie."""
        connection_id = self.get_connection_id()
        return json.loads(self.get_secure_cookie('sftp-' + connection_id))

    def get_connection(self):
        """Open the SSH connection."""
        connection_id = self.get_connection_id()
        if connection_id:
            details = self.get_connection_details()
            try:
                server = pysftp.Connection(
                    host = details['host'],
                    username = details['user'],
                    password = details['password']
                )
                return server
            except:  # pylint: disable=W0702
                log.error('Connection to server over SSH failed.')
                self.send_error(200)
                return None
        else:
            connection_id = self.setup_connection()
            # TODO: This should properly parse the URL in order to maintain
            # existing parameters.
            self.redirect('?connection=' + connection_id)
            self.finish()
            return None

    def write_error(self, status_code, **kwargs):
        """A default error response."""
        loader = tornado.template.Loader('templates')
        self.write(loader.load('error.html').generate(
            title = 'Error - Cider',
            config = json.dumps({
                'message': ' '.join([
                    'Authentication to the server failed.',
                    'Please go back and try the connection again.'
                ])
            })
        ))

class CreateFolderHandler(BaseHandler):
    """Handles the request to create a new folder."""
    def get(self):
        """GET request; takes an argument path as the full path to the folder
        to be created.
        """
        server = self.get_connection()
        if server:
            details = self.get_connection_details()
            path = self.get_argument('path', '')
            path = path.replace('..', '').strip('/')  # pylint: disable=E1103
            base = details['path']
            try:
                server.execute(
                    'mkdir ' + os.path.join(base, path).replace(' ', '\ ')
                )
                self.set_header('Content-Type', 'application/json')
                self.write(json.dumps({'success': True}))
            except:  # pylint: disable=W0702
                self.send_error(200)
            server.close()

    def write_error(self, status_code, **kwargs):
        """Outputs failure JSON."""
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps({'success': False}))

class DownloadHandler(BaseHandler):
    """Handles file download requests."""
    def get(self):
        """GET request; takes an argument file as the full path of the file to
        download.
        """
        server = self.get_connection()
        if server:
            details = self.get_connection_details()
            the_file = self.get_argument('file', '')
            the_file = the_file.replace('..', '').strip('/')  # pylint: disable=E1103
            base = details['path']
            file_name = self.calculate_file_name()

            try:
                tmp_path = tempfile.mkstemp()
                tmp_path = tmp_path[1]
                server.get(os.path.join(base, the_file), tmp_path)
                file_handler = open(tmp_path, 'rb')
                data = file_handler.read()
                file_handler.close()
                length = os.path.getsize(tmp_path)
                os.remove(tmp_path)
                self.output_file(file_name, length, data)
            except Exception as error:  # pylint: disable=W0703
                log.error(error)
                self.send_error(200)
            server.close()

    def write_error(self, status_code, **kwargs):
        """Write out error."""
        self.output_file(self.calculate_file_name(), 0, None)

    def calculate_file_name(self):
        """Figures out file name based on URL parameter."""
        the_file = self.get_argument('file', '')
        the_file = the_file.replace('..', '').strip('/')  # pylint: disable=E1103
        file_name = the_file
        if the_file.find('/') != -1:
            file_name = the_file[(the_file.rfind('/') + 1):]
        return file_name

    def output_file(self, file_name, length, data):
        """Sets up the headers and outputs the file."""
        self.set_header('Content-Type', 'application/force-download')
        self.set_header(
            'Content-Disposition',
            'attachment; filename="' + file_name + '"'
        )
        self.set_header('Content-Length', length)
        self.write(data)

class EditorHandler(BaseHandler):
    """Handles editor requests."""
    def get(self):
        """GET request; takes an argument file as the full path of the file to
        load into the editor.
        """
        server = self.get_connection()
        if server:
            details = self.get_connection_details()
            the_file = self.get_argument('file', '')
            the_file = the_file.replace('..', '').strip('/')  # pylint: disable=E1103
            base = details['path']
            file_name = the_file
            path = ''
            title = '[' + file_name + '] - Cider'
            if the_file.find('/') != -1:
                file_name = the_file[(the_file.rfind('/') + 1):]
                path = the_file[:the_file.rfind('/')]
                title = '[' + file_name + '] ' + path + ' - Cider'
            ext = the_file[(the_file.rfind('.') + 1):]
            mode = util.get_mode(ext)
            tab_width = util.get_tab_width(ext)
            markup = util.is_markup(ext)

            try:
                tmp_path = tempfile.mkstemp()
                tmp_path = tmp_path[1]
                server.get(os.path.join(base, the_file), tmp_path)
                file_handler = open(tmp_path, 'r')
                text = file_handler.read()
                text = text.replace('{', '~' + 'lb').replace('}', '~' + 'rb')
                file_handler.close()
                os.remove(tmp_path)
                save_text = 'Saved'
            except Exception as error:  # pylint: disable=W0703
                log.warn(error)
                text = ''
                save_text = 'Save'

            self.set_header('Content-Type', 'text/html')
            loader = tornado.template.Loader('templates')
            self.write(loader.load('editor.html').generate(
                config = json.dumps({
                    'file_name': file_name,
                    'path': path,
                    'title': title,
                    'file': the_file,
                    'text': text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;'),
                    'mode': mode,
                    'tab_width': tab_width,
                    'markup': markup,
                    'save_text': save_text,
                    'extra': '&connection=' + self.get_connection_id(),
                    'prefix': 'sftp://' + details['user'] + '@' + details['host'] + details['path'],
                    'salt': self.get_connection_id(),
                    'modes': util.MODES
                }),
                title = title,
                modes = util.MODES
            ))
            server.close()

class FileManagerHandler(BaseHandler):
    """Handles the file manager requests."""
    def get(self):
        """GET request; takes path as an argument."""
        server = self.get_connection()
        if server:
            details = self.get_connection_details()
            path = self.get_argument('path', '')
            path = path.replace('..', '').strip('/')  # pylint: disable=E1103
            title = path + ' - Cider'
            base = details['path']

            files = []
            try:
                file_list = server.listdir(os.path.join(base, path))
                file_list.sort(key=lambda x: x.encode().lower())

                for i in range(len(file_list)):
                    try:
                        the_file = os.path.join(base, path, file_list[i])
                        is_file = True
                        command = 'if test -d ' + the_file.replace(' ', '\ ') + '; then echo -n 1; fi'
                        if len(server.execute(command)):
                            is_file = False
                        confirm = ''
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
                title = title,
                config = json.dumps({
                    'base': base,
                    'path': path,
                    'files_list': files,
                    'up': up,
                    'folder': self.get_argument('folder', ''),
                    'extra': '&connection=' + self.get_connection_id(),
                    'prefix': 'sftp://' + details['user'] + '@' + details['host'] + details['path']
                })
            ))
            server.close()

    def post(self):
        """Post request; same logic as the GET request."""
        self.get()

class SaveFileHandler(BaseHandler):
    """Handles file saving requests."""
    def get(self):
        """GET request; takes arguments file and text for the path of the file
        to save and the content to put in it.
        """
        server = self.get_connection()
        if server:
            details = self.get_connection_details()
            the_file = self.get_argument('file', '')
            the_file = the_file.replace('..', '').strip('/')  # pylint: disable=E1103
            base = details['path']

            try:
                tmp_path = tempfile.mkstemp()
                tmp_path = tmp_path[1]
                file_handler = open(tmp_path, 'w')
                text = self.get_argument('text', strip = False)
                text = text.encode('ascii', 'replace')  # pylint: disable=E1103
                file_handler.write(text)
                file_handler.close()
                server.put(tmp_path, os.path.join(base, the_file))
                os.remove(tmp_path)

                try:
                    salt = self.get_argument('salt', '')
                    diff_id = hashlib.sha224(salt + the_file).hexdigest()
                    collaborate.FileDiffManager().remove_diff(diff_id)
                    collaborate.FileDiffManager().create_diff(diff_id)
                    collaborate.FileSessionManager().broadcast(
                        the_file,
                        salt,
                        {'t': 's'}
                    )
                except:  # pylint: disable=W0702
                    pass

                self.set_header('Content-Type', 'application/json')
                self.write(json.dumps({
                    'success': True,
                    'notification': 'last saved: ' + time.strftime('%Y-%m-%d %H:%M:%S')
                }))
            except Exception as error:  # pylint: disable=W0703
                log.error(error)
                self.send_error(200)

    def post(self):
        """Post request; same logic as the GET request."""
        self.get()

    def write_error(self, status_code, **kwargs):
        """Outputs failure JSON."""
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps({
            'success': False,
            'notification': 'save failed'
        }))
