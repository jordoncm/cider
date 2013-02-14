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
"""Handlers for talking to Dropbox."""

import hashlib
import json
from operator import itemgetter
import os
import time
import tornado.template
import tornado.web

import collaborate
import handlers.auth.dropbox
import util

class CreateFolderHandler(
    handlers.auth.dropbox.BaseAuthHandler,
    handlers.auth.dropbox.Mixin
):
    """Handles the request to create a new folder."""
    @tornado.web.authenticated
    @tornado.web.asynchronous
    def get(self):
        """GET request; takes an argument path as the full path to the folder
        to be created.
        """
        path = self.get_argument('path', '')
        path = path.replace('..', '').strip('/')  # pylint: disable=E1103
        self.dropbox_request(
            '/fileops/create_folder',
            access_token = self.current_user['access_token'],
            callback = self.async_callback(self.get_callback),
            post_args = {'root': 'dropbox', 'path': path}
        )

    def get_callback(self, response):
        """Handles the callback from Dropbox. If auth does not fail to Dropbox,
        this request currently assumes folder creation success.
        """
        if not response:
            self.authorize_redirect('/auth/dropbox/')
            return

        self.finish(json.dumps({
            'success': True
        }))

class DownloadHandler(
    handlers.auth.dropbox.BaseAuthHandler,
    handlers.auth.dropbox.Mixin
):
    """Handles file download requests."""
    @tornado.web.authenticated
    @tornado.web.asynchronous
    def get(self):
        """GET request; takes an argument file as the full path of the file to
        download.
        """
        the_file = self.get_argument('file', '')
        the_file = the_file.replace('..', '').strip('/')  # pylint: disable=E1103
        self.dropbox_request(
            '/files/dropbox/' + the_file,
            access_token = self.current_user['access_token'],
            callback = self.async_callback(self.get_callback)
        )

    def get_callback(self, response):
        """Handles the callback response from Dropbox. Outputs the content of
        the download.
        """
        if not response:
            self.authorize_redirect('/auth/dropbox/')
            return
        the_file = self.get_argument('file', '')
        the_file = the_file.replace('..', '').strip('/')  # pylint: disable=E1103

        file_name = the_file
        if the_file.find('/') != -1:
            file_name = the_file[(the_file.rfind('/') + 1):]

        self.set_header('Content-Type', 'application/force-download')
        self.set_header(
            'Content-Disposition',
            'attachment; filename="' + file_name + '"'
        )
        self.finish(response)

class EditorHandler(
    handlers.auth.dropbox.BaseAuthHandler,
    handlers.auth.dropbox.Mixin
):
    """Handles editor requests."""
    @tornado.web.authenticated
    @tornado.web.asynchronous
    def get(self):
        """GET request; takes an argument file as the full path of the file to
        load into the editor.
        """
        the_file = self.get_argument('file', '')
        the_file = the_file.replace('..', '').strip('/')  # pylint: disable=E1103
        self.dropbox_request(
            '/files/dropbox/' + the_file,
            access_token = self.current_user['access_token'],
            callback = self.async_callback(self.get_callback)
        )

    def get_callback(self, response):
        """Handles the callback from Dropbox and loads the editor."""
        # Need logic around auth issues verus new file.
        '''
        if not response:
            self.authorize_redirect('/auth/dropbox/')
            return
        '''
        the_file = self.get_argument('file', '')
        the_file = the_file.replace('..', '').strip('/')  # pylint: disable=E1103

        file_name = the_file
        path = ''
        title = '[' + file_name + '] - Cider'
        if the_file.find('/') != -1:
            file_name = the_file[(the_file.rfind('/') + 1):]
            path = the_file[:the_file.rfind('/')]
            title = '[' + file_name + '] ' + path + ' - Cider'

        if not response:
            text = ''
            save_text = 'Save'
        else:
            text = response
            save_text = 'Saved'

        ext = the_file[(the_file.rfind('.') + 1):]
        mode = util.get_mode(ext)
        tab_width = util.get_tab_width(ext)
        markup = util.is_markup(ext)

        self.set_header('Content-Type', 'text/html')
        loader = tornado.template.Loader('templates')
        self.finish(loader.load('editor.html').generate(
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
                'extra': '',
                'prefix': 'dropbox://',
                'salt': self.current_user['uid'],
                'modes': util.MODES
            }),
            title = title,
            modes = util.MODES
        ))

class FileManagerHandler(
    handlers.auth.dropbox.BaseAuthHandler,
    handlers.auth.dropbox.Mixin
):
    """Handles the file manager requests."""
    @tornado.web.authenticated
    @tornado.web.asynchronous
    def get(self):
        """GET request; takes path as an argument."""
        path = self.get_argument('path', '')
        path = path.replace('..', '').strip('/')  # pylint: disable=E1103
        self.dropbox_request(
            '/metadata/dropbox/' + path,
            access_token = self.current_user['access_token'],
            callback = self.async_callback(self.get_callback)
        )

    def get_callback(self, response):
        """Handles the callback from Dropbox and displays the file list."""
        if not response:
            self.authorize_redirect('/auth/dropbox/')
            return
        path = self.get_argument('path', '')
        path = path.replace('..', '').strip('/')  # pylint: disable=E1103
        title = path + ' - Cider'
        base = ''

        files = []
        for the_file in response['contents']:
            files.append({
                'name': os.path.basename(the_file['path']),
                'is_file': not the_file['is_dir'],
                'confirm': ''
            })
        files = sorted(files, key=lambda x: x['name'].encode().lower())
        files = sorted(files, key=itemgetter('is_file'))

        up = ''
        if path != '' and path.rfind('/') > -1:
            up = path[:path.rfind('/')]

        self.set_header('Content-Type', 'text/html')
        loader = tornado.template.Loader('templates')
        self.finish(loader.load('file-manager.html').generate(
            title = title,
            config = json.dumps({
                'base': base,
                'path': path,
                'files_list': files,
                'up': up,
                'folder': self.get_argument('folder', ''),
                'extra': '',
                'prefix': 'dropbox://'
            })
        ))

class SaveFileHandler(
    handlers.auth.dropbox.BaseAuthHandler,
    handlers.auth.dropbox.Mixin
):
    """Handles file saving requests."""
    @tornado.web.authenticated
    @tornado.web.asynchronous
    def get(self):
        """GET request; takes arguments file and text for the path of the file
        to save and the content to put in it.
        """
        the_file = self.get_argument('file', '')
        the_file = the_file.replace('..', '').strip('/')  # pylint: disable=E1103
        self.dropbox_put(
            '/files_put/dropbox/' + the_file,
            access_token = self.current_user['access_token'],
            callback = self.async_callback(self.get_callback),
            put_args = self.get_argument('text', strip = False).encode('ascii', 'replace')  # pylint: disable=E1103
        )

    def get_callback(self, response):
        """Handles the callback from Dropbox."""
        if not response:
            self.authorize_redirect('/auth/dropbox/')
            return
        the_file = self.get_argument('file', '')
        the_file = the_file.replace('..', '').strip('/')  # pylint: disable=E1103
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
        self.finish(json.dumps({
            'success': True,
            'notification': 'last saved: ' + time.strftime('%Y-%m-%d %H:%M:%S')
        }))

    def post(self):
        """Post request; same logic as the GET request."""
        self.get()
