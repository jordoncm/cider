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

import json
import os
import pysftp
import random
import string
import tempfile
import tornado.template
import tornado.web

import handlers.mixins
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

    def generate_prefix(self, details):
        """Returns the prefix based on given connection details."""
        return ''.join([
            'sftp://',
            details['user'],
            '@',
            details['host'],
            details['path']
        ])

class CreateFolderHandler(BaseHandler, handlers.mixins.CreateFolder):
    """Handles the request to create a new folder."""
    def get(self):
        """GET request; takes an argument path as the full path to the folder
        to be created.
        """
        server = self.get_connection()
        if server:
            details = self.get_connection_details()
            path = self.get_path()
            base = details['path']
            try:
                server.execute(
                    'mkdir ' + os.path.join(base, path).replace(' ', '\ ')
                )
                self.do_success()
            except:  # pylint: disable=W0702
                self.send_error(200)
            server.close()

    def write_error(self, status_code, **kwargs):
        """Outputs failure JSON."""
        self.do_failure()

class DownloadHandler(BaseHandler, handlers.mixins.Download):
    """Handles file download requests."""
    def get(self):
        """GET request; takes an argument file as the full path of the file to
        download.
        """
        server = self.get_connection()
        if server:
            details = self.get_connection_details()
            filename = self.get_file()
            basename = util.find_base(filename)

            try:
                tmp_path = tempfile.mkstemp()
                tmp_path = tmp_path[1]
                server.get(os.path.join(details['path'], filename), tmp_path)
                file_handler = open(tmp_path, 'rb')
                data = file_handler.read()
                file_handler.close()
                length = os.path.getsize(tmp_path)
                os.remove(tmp_path)
                self.output_file(basename, length, data)
            except Exception as error:  # pylint: disable=W0703
                log.error(error)
                self.send_error(200)
            server.close()

    def write_error(self, status_code, **kwargs):
        """Write out error."""
        basename = util.find_base(self.get_file())
        self.output_file(basename, 0, None)

    def output_file(self, basename, length, data):
        """Sets up the headers and outputs the file."""
        self.do_headers(basename, length)
        self.finish(data)

class EditorHandler(BaseHandler, handlers.mixins.Editor):
    """Handles editor requests."""
    def get(self):
        """GET request; takes an argument file as the full path of the file to
        load into the editor.
        """
        server = self.get_connection()
        if server:
            details = self.get_connection_details()
            filename = self.get_file()
            text = ''
            saved = False

            try:
                tmp_path = tempfile.mkstemp()
                tmp_path = tmp_path[1]
                server.get(os.path.join(details['path'], filename), tmp_path)
                file_handler = open(tmp_path, 'r')
                text = file_handler.read()
                file_handler.close()
                os.remove(tmp_path)
                saved = True
            except Exception as error:  # pylint: disable=W0703
                log.warn(error)

            self.do_output(
                text,
                self.generate_prefix(details),
                self.get_connection_id(),
                '&connection=' + self.get_connection_id(),
                saved
            )
            server.close()

class FileManagerHandler(BaseHandler, handlers.mixins.FileManager):
    """Handles the file manager requests."""
    def get(self):
        """GET request; takes path as an argument."""
        server = self.get_connection()
        if server:
            details = self.get_connection_details()
            path = self.get_path()
            base = details['path']

            files = []
            try:
                file_list = server.listdir(os.path.join(base, path))
                for i in file_list:
                    try:
                        filename = os.path.join(base, path, i)
                        is_file = True
                        command = ''.join([
                            'if test -d ',
                            filename.replace(' ', '\ '),
                            '; then echo -n 1; fi'
                        ])
                        if len(server.execute(command)):
                            is_file = False
                        confirm = ''
                        files.append({
                            'name': i,
                            'is_file': is_file,
                            'confirm': confirm
                        })
                    except Exception as error:  # pylint: disable=W0703
                        log.warn(error)
            except Exception as error:  # pylint: disable=W0703
                log.warn(error)

            self.do_output(
                files,
                base,
                self.generate_prefix(details),
                '&connection=' + self.get_connection_id()
            )
            server.close()

    def post(self):
        """Post request; same logic as the GET request."""
        self.get()

class SaveFileHandler(BaseHandler, handlers.mixins.SaveFile):
    """Handles file saving requests."""
    def get(self):
        """GET request; takes arguments file and text for the path of the file
        to save and the content to put in it.
        """
        server = self.get_connection()
        if server:
            details = self.get_connection_details()
            filename = self.get_file()

            try:
                tmp_path = tempfile.mkstemp()
                tmp_path = tmp_path[1]
                file_handler = open(tmp_path, 'w')
                file_handler.write(self.get_text())
                file_handler.close()
                server.put(tmp_path, os.path.join(details['path'], filename))
                os.remove(tmp_path)

                self.broadcast_save(filename, self.get_connection_id())
                self.do_success()
            except Exception as error:  # pylint: disable=W0703
                log.error(error)
                self.send_error(200)

    def post(self):
        """Post request; same logic as the GET request."""
        self.get()

    def write_error(self, status_code, **kwargs):
        """Outputs failure JSON."""
        self.do_failure()
