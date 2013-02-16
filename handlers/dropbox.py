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

import tornado.web

import handlers.auth.dropbox
import handlers.mixins
import log
import util

class CreateFolderHandler(
    handlers.auth.dropbox.BaseAuthHandler,
    handlers.auth.dropbox.Mixin,
    handlers.mixins.CreateFolder
):
    """Handles the request to create a new folder."""
    @tornado.web.authenticated
    @tornado.web.asynchronous
    def get(self):
        """GET request; takes an argument path as the full path to the folder
        to be created.
        """
        self.dropbox_request(
            '/fileops/create_folder',
            access_token = self.current_user['access_token'],
            callback = self.async_callback(self.get_callback),
            post_args = {'root': 'dropbox', 'path': self.get_path()}
        )

    def get_callback(self, response):
        """Handles the callback from Dropbox. If auth does not fail to Dropbox,
        this request currently assumes folder creation success.
        """
        if not response:
            self.authorize_redirect('/auth/dropbox/')
            return
        self.do_success()

class DownloadHandler(
    handlers.auth.dropbox.BaseAuthHandler,
    handlers.auth.dropbox.Mixin,
    handlers.mixins.Download
):
    """Handles file download requests."""
    @tornado.web.authenticated
    @tornado.web.asynchronous
    def get(self):
        """GET request; takes an argument file as the full path of the file to
        download.
        """
        self.dropbox_request(
            '/files/dropbox/' + self.get_file(),
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
        filename = self.get_file()
        basename = util.find_base(filename)
        self.do_headers(basename)
        self.finish(response)

class EditorHandler(
    handlers.auth.dropbox.BaseAuthHandler,
    handlers.auth.dropbox.Mixin,
    handlers.mixins.Editor
):
    """Handles editor requests."""
    @tornado.web.authenticated
    @tornado.web.asynchronous
    def get(self):
        """GET request; takes an argument file as the full path of the file to
        load into the editor.
        """
        self.dropbox_request(
            '/files/dropbox/' + self.get_file(),
            access_token = self.current_user['access_token'],
            callback = self.async_callback(self.get_callback)
        )

    def get_callback(self, response):
        """Handles the callback from Dropbox and loads the editor."""
        # TODO: Need logic around auth issues verus new file.
        '''
        if not response:
            self.authorize_redirect('/auth/dropbox/')
            return
        '''
        text = ''
        if response:
            text = response
        self.do_output(text, 'dropbox://', self.current_user['uid'])

class FileManagerHandler(
    handlers.auth.dropbox.BaseAuthHandler,
    handlers.auth.dropbox.Mixin,
    handlers.mixins.FileManager
):
    """Handles the file manager requests."""
    @tornado.web.authenticated
    @tornado.web.asynchronous
    def get(self):
        """GET request; takes path as an argument."""
        self.dropbox_request(
            '/metadata/dropbox/' + self.get_path(),
            access_token = self.current_user['access_token'],
            callback = self.async_callback(self.get_callback)
        )

    def get_callback(self, response):
        """Handles the callback from Dropbox and displays the file list."""
        if not response:
            self.authorize_redirect('/auth/dropbox/')
            return
        files = []
        for i in response['contents']:
            files.append({
                'name': util.find_base(i['path']),
                'is_file': not i['is_dir'],
                'confirm': ''
            })

        self.do_output(files, prefix = 'dropbox://')

class SaveFileHandler(
    handlers.auth.dropbox.BaseAuthHandler,
    handlers.auth.dropbox.Mixin,
    handlers.mixins.SaveFile
):
    """Handles file saving requests."""
    @tornado.web.authenticated
    @tornado.web.asynchronous
    def get(self):
        """GET request; takes arguments file and text for the path of the file
        to save and the content to put in it.
        """
        self.dropbox_put(
            '/files_put/dropbox/' + self.get_file(),
            access_token = self.current_user['access_token'],
            callback = self.async_callback(self.get_callback),
            put_args = self.get_text()
        )

    def get_callback(self, response):
        """Handles the callback from Dropbox."""
        if not response:
            self.authorize_redirect('/auth/dropbox/')
            return
        self.broadcast_save(self.get_file(), self.current_user['uid'])
        self.do_success()

    def post(self):
        """Post request; same logic as the GET request."""
        self.get()
