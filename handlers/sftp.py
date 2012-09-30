#
# This work is copyright 2012 Jordon Mears. All rights reserved.
#
# This file is part of Cider.
#
# Cider is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Cider is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Cider.  If not, see <http://www.gnu.org/licenses/>.
#

from operator import itemgetter

import hashlib
import json
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

    def setup_connection(self):
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

        id = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(8))
        self.set_secure_cookie('sftp-' + id, json.dumps(details), expires_days=None)
        return id


class CreateFolderHandler(BaseHandler):
    """Handles the request to create a new folder."""

    def get(self):
        """
        GET request; takes an argument path as the full path to the folder to
        be created.
        """
        if self.get_argument('connection', None) is not None:
            id = self.get_argument('connection')
            id = id.upper()
            details = json.loads(self.get_secure_cookie('sftp-' + id))
            try:
                server = pysftp.Connection(
                    host=details['host'],
                    username=details['user'],
                    password=details['password']
                )
            except:
                log.error('Connection to server over SSH failed.')
                self.write(json.dumps({
                    'success': False
                }))

            self.set_header('Content-Type', 'application/json')
            try:
                path = self.get_argument('path', '').replace('..', '').strip('/')
                base = details['path']

                server.execute(
                    'mkdir ' + os.path.join(base, path).replace(' ', '\ ')
                )

                self.write(json.dumps({
                    'success': True
                }))
            except:
                self.write(json.dumps({
                    'success': False
                }))
            server.close()
        else:
            id = self.setup_connection()
            self.redirect('?connection=' + id)


class DownloadHandler(BaseHandler):
    """Handles file download requests."""

    def get(self):
        """
        GET request; takes an argument file as the full path of the file to
        download.
        """
        if self.get_argument('connection', None) is not None:
            id = self.get_argument('connection')
            id = id.upper()
            details = json.loads(self.get_secure_cookie('sftp-' + id))
            try:
                server = pysftp.Connection(
                    host=details['host'],
                    username=details['user'],
                    password=details['password']
                )
            except:
                log.error('Connection to server over SSH failed.')
                data = None
                length = 0

            file = self.get_argument('file', '').replace('..', '').strip('/')
            base = details['path']

            if file.find('/') != -1:
                file_name = file[(file.rfind('/') + 1):]
                path = file[:file.rfind('/')]
            else:
                file_name = file
                path = ''

            try:
                tmp_path = tempfile.mkstemp()
                tmp_path = tmp_path[1]
                server.get(os.path.join(base, file), tmp_path)
                f = open(tmp_path, 'rb')
                data = f.read()
                f.close()
                length = os.path.getsize(tmp_path)
                os.remove(tmp_path)
            except Exception as e:
                log.error(e)
                data = None
                length = 0

            self.set_header('Content-Type', 'application/force-download')
            self.set_header(
                'Content-Disposition', 'attachment; filename="' + file_name + '"'
            )
            self.set_header('Content-Length', length)
            self.write(data)
            server.close()
        else:
            id = self.setup_connection()
            self.redirect('?connection=' + id)


class EditorHandler(BaseHandler):
    """Handles editor requests."""

    def get(self):
        """
        GET request; takes an argument file as the full path of the file to
        load into the editor.
        """
        if self.get_argument('connection', None) is not None:
            id = self.get_argument('connection')
            id = id.upper()
            details = json.loads(self.get_secure_cookie('sftp-' + id))
            try:
                server = pysftp.Connection(
                    host=details['host'],
                    username=details['user'],
                    password=details['password']
                )
            except:
                log.error('Connection to server over SSH failed.')
                loader = tornado.template.Loader('templates')
                self.write(loader.load('error.html').generate(
                    title='Error - Cider',
                    config=json.dumps({
                        'message': 'Authentication to the server failed. Please go back and try the connection again.'
                    })
                ))
                return

            file = self.get_argument('file', '').replace('..', '').strip('/')
            base = details['path']

            if file.find('/') != -1:
                file_name = file[(file.rfind('/') + 1):]
                path = file[:file.rfind('/')]
                title = '[' + file_name + '] ' + path + ' - Cider'
            else:
                file_name = file
                path = ''
                title = '[' + file_name + '] - Cider'

            try:
                tmp_path = tempfile.mkstemp()
                tmp_path = tmp_path[1]
                server.get(os.path.join(base, file), tmp_path)
                f = open(tmp_path, 'r')
                text = f.read().replace('{', '~' + 'lb').replace('}', '~' + 'rb')
                f.close()
                os.remove(tmp_path)

                save_text = 'Saved'
            except Exception as e:
                log.warn(e)
                text = ''
                save_text = 'Save'

            ext = file[(file.rfind('.') + 1):]
            mode = util.get_mode(ext)
            tab_width = util.get_tab_width(ext)
            markup = util.is_markup(ext)

            self.set_header('Content-Type', 'text/html')
            loader = tornado.template.Loader('templates')
            self.write(loader.load('editor.html').generate(
                config=json.dumps({
                    'file_name': file_name,
                    'path': path,
                    'title': title,
                    'file': file,
                    'text': text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;'),
                    'mode': mode,
                    'tab_width': tab_width,
                    'markup': markup,
                    'save_text': save_text,
                    'extra': '&connection=' + id,
                    'prefix': 'sftp://' + details['user'] + '@' + details['host'] + details['path'],
                    'salt': id
                }),
                title=title
            ))
        else:
            id = self.setup_connection()
            self.redirect('?connection=' + id)


class FileManagerHandler(BaseHandler):
    """Handles the file manager requests."""

    def get(self):
        """GET request; takes path as an argument."""
        if self.get_argument('connection', None) is not None:
            id = self.get_argument('connection')
            id = id.upper()
            details = json.loads(self.get_secure_cookie('sftp-' + id))
            try:
                server = pysftp.Connection(
                    host=details['host'],
                    username=details['user'],
                    password=details['password']
                )
            except:
                log.error('Connection to server over SSH failed.')
                loader = tornado.template.Loader('templates')
                self.write(loader.load('error.html').generate(
                    title='Error - Cider',
                    config=json.dumps({
                        'message': 'Authentication to the server failed. Please go back and try the connection again.'
                    })
                ))
                return

            path = self.get_argument('path', '').replace('..', '').strip('/')
            title = path + ' - Cider'
            base = details['path']

            files = []
            try:
                file_list = server.listdir(os.path.join(base, path))
                file_list.sort(key=lambda x: x.encode().lower())

                for i in range(len(file_list)):
                    try:
                        file = os.path.join(base, path, file_list[i])
                        is_file = True
                        command = 'if test -d ' + file.replace(' ', '\ ') + '; then echo -n 1; fi'
                        if len(server.execute(command)):
                            is_file = False
                        confirm = ''
                        files.append({
                            'name': file_list[i],
                            'is_file': is_file,
                            'confirm': confirm
                        })
                    except IOError as e:
                        log.warn(e)

                files = sorted(files, key=itemgetter('is_file'))
            except Exception as e:
                log.warn(e)

            if path != '' and path.rfind('/') > -1:
                up = path[:path.rfind('/')]
            else:
                up = ''

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
                    'extra': '&connection=' + id,
                    'prefix': 'sftp://' + details['user'] + '@' + details['host'] + details['path']
                })
            ))

            server.close()
        else:
            id = self.setup_connection()
            self.redirect('?connection=' + id)

    def post(self):
        self.get()


class SaveFileHandler(BaseHandler):
    """Handles file saving requests."""

    def get(self):
        """
        GET request; takes arguments file and text for the path of the file to
        save and the content to put in it.
        """
        if self.get_argument('connection', None) is not None:
            id = self.get_argument('connection')
            id = id.upper()
            details = json.loads(self.get_secure_cookie('sftp-' + id))
            try:
                server = pysftp.Connection(
                    host=details['host'],
                    username=details['user'],
                    password=details['password']
                )
            except:
                log.error('Connection to server over SSH failed.')
                success = False
                notification = 'save failed'

            self.set_header('Content-Type', 'application/json')
            try:
                file = self.get_argument('file', '').replace('..', '').strip('/')
                base = details['path']

                tmp_path = tempfile.mkstemp()
                tmp_path = tmp_path[1]
                f = open(tmp_path, 'w')
                f.write(
                    self.get_argument('text', strip=False).encode('ascii', 'replace')
                )
                f.close()
                server.put(tmp_path, os.path.join(base, file))
                os.remove(tmp_path)

                try:
                    salt = self.get_argument('salt', '')
                    id = hashlib.sha224(salt + file).hexdigest()
                    collaborate.FileDiffManager().remove_diff(id)
                    collaborate.FileDiffManager().create_diff(id)
                    collaborate.FileSessionManager().broadcast(file, salt, {'t': 's'})
                except:
                    pass

                success = True
                notification = 'last saved: ' + time.strftime('%Y-%m-%d %H:%M:%S')
            except Exception as e:
                log.error(e)
                success = False
                notification = 'save failed'

            self.write(json.dumps({
                'success': success,
                'notification': notification
            }))
        else:
            id = self.setup_connection()
            self.redirect('?connection=' + id)

    def post(self):
        """Post request; same logic as the GET request."""
        self.get()
