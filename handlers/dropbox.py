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
import time
import tornado.template
import tornado.web

import collaborate
import handlers.auth.dropbox
import log
import util


class CreateFolderHandler(handlers.auth.dropbox.BaseAuthHandler, handlers.auth.dropbox.Mixin):
    """Handles the request to create a new folder."""
    
    @tornado.web.authenticated
    @tornado.web.asynchronous
    def get(self):
        """
        GET request; takes an argument path as the full path to the folder to 
        be created.
        """
        path = self.get_argument('path', '').replace('..', '').strip('/')
        self.dropbox_request(
            '/fileops/create_folder',
            access_token=self.current_user['access_token'],
            callback=self.async_callback(self.get_callback),
            post_args={'root': 'dropbox', 'path': path}
        )
    
    def get_callback(self, response):
        """
        Handles the callback from Dropbox. If auth does not fail to Dropbox, 
        this request currently assumes folder creation success.
        """
        if not response:
            self.authorize_redirect('/auth/dropbox/')
            return
        
        self.finish(json.dumps({
            'success': True
        }))


class DownloadHandler(handlers.auth.dropbox.BaseAuthHandler, handlers.auth.dropbox.Mixin):
    """Handles file download requests."""
    
    @tornado.web.authenticated
    @tornado.web.asynchronous
    def get(self):
        """
        GET request; takes an argument file as the full path of the file to 
        download.
        """
        file = self.get_argument('file', '').replace('..', '').strip('/')
        self.dropbox_request(
            '/files/dropbox/' + file,
            access_token=self.current_user['access_token'],
            callback=self.async_callback(self.get_callback)
        )
    
    def get_callback(self, response):
        """
        Handles the callback response from Dropbox. Outputs the content of the 
        download.
        """
        if not response:
            self.authorize_redirect('/auth/dropbox/')
            return
        file = self.get_argument('file', '').replace('..', '').strip('/')
        
        if file.find('/') != -1:
            file_name = file[(file.rfind('/') + 1):]
            path = file[:file.rfind('/')]
        else:
            file_name = file
            path = ''
        
        self.set_header('Content-Type', 'application/force-download')
        self.set_header(
            'Content-Disposition', 'attachment; filename="' + file_name + '"'
        )
        self.finish(response)


class EditorHandler(handlers.auth.dropbox.BaseAuthHandler, handlers.auth.dropbox.Mixin):
    """Handles editor requests."""
    
    @tornado.web.authenticated
    @tornado.web.asynchronous
    def get(self):
        """
        GET request; takes an argument file as the full path of the file to 
        load into the editor.
        """
        file = self.get_argument('file', '').replace('..', '').strip('/')
        self.dropbox_request(
            '/files/dropbox/' + file,
            access_token=self.current_user['access_token'],
            callback=self.async_callback(self.get_callback)
        )
    
    def get_callback(self, response):
        """Handles the callback from Dropbox and loads the editor."""
        # Need logic around auth issues verus new file.
        '''
        if not response:
            self.authorize_redirect('/auth/dropbox/')
            return
        '''
        file = self.get_argument('file', '').replace('..', '').strip('/')
        
        if file.find('/') != -1:
            file_name = file[(file.rfind('/') + 1):]
            path = file[:file.rfind('/')]
            title = '[' + file_name + '] ' + path + ' - Cider'
        else:
            file_name = file
            path = ''
            title = '[' + file_name + '] - Cider'
        
        if not response:
            text = ''
            save_text = 'Save'
        else:
            text = response
            save_text = 'Saved'
        
        ext = file[(file.rfind('.') + 1):]
        mode = util.get_mode(ext)
        tab_width = util.get_tab_width(ext)
        markup = util.is_markup(ext)
        
        self.set_header('Content-Type', 'text/html')
        loader = tornado.template.Loader('templates')
        self.finish(loader.load('editor.html').generate(
            file_name=file_name,
            path=path,
            title=title,
            file=file,
            text=text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;'),
            mode=mode,
            tab_width=tab_width,
            markup=markup,
            save_text=save_text,
            extra=''
        ))


class FileManagerHandler(handlers.auth.dropbox.BaseAuthHandler, handlers.auth.dropbox.Mixin):
    """Handles the file manager requests."""
    
    @tornado.web.authenticated
    @tornado.web.asynchronous
    def get(self):
        """GET request; takes path as an argument."""
        path = self.get_argument('path', '').replace('..', '').strip('/')
        self.dropbox_request(
            '/metadata/dropbox/' + path,
            access_token=self.current_user['access_token'],
            callback=self.async_callback(self.get_callback)
        )
    
    def get_callback(self, response):
        """Handles the callback from Dropbox and displays the file list."""
        if not response:
            self.authorize_redirect('/auth/dropbox/')
            return
        path = self.get_argument('path', '').replace('..', '').strip('/')
        title = path + ' - Cider'
        base = ''
        
        files = []
        for file in response['contents']:
            files.append({
                'name': os.path.basename(file['path']),
                'is_file': not file['is_dir'],
                'confirm': ''
            })
        files = sorted(files, key=lambda x: x['name'].encode().lower())
        files = sorted(files, key=itemgetter('is_file'))
        
        if path != '' and path.rfind('/') > -1:
            up = path[:path.rfind('/')]
        else:
            up = ''
        
        self.set_header('Content-Type', 'text/html')
        loader = tornado.template.Loader('templates')
        self.finish(loader.load('file-manager.html').generate(
            title=title,
            base=base,
            path=path,
            files_list=files,
            up=up,
            folder=self.get_argument('folder', ''),
            extra=''
        ))


class SaveFileHandler(handlers.auth.dropbox.BaseAuthHandler, handlers.auth.dropbox.Mixin):
    """Handles file saving requests."""
    
    @tornado.web.authenticated
    @tornado.web.asynchronous
    def get(self):
        """
        GET request; takes arguments file and text for the path of the file to 
        save and the content to put in it.
        """
        file = self.get_argument('file', '').replace('..', '').strip('/')
        self.dropbox_put(
            '/files_put/dropbox/' + file,
            access_token=self.current_user['access_token'],
            callback=self.async_callback(self.get_callback),
            put_args=self.get_argument('text')
        )
    
    def get_callback(self, response):
        """Handles the callback from Dropbox."""
        if not response:
            self.authorize_redirect('/auth/dropbox/')
            return
        file = self.get_argument('file', '').replace('..', '').strip('/')
        try:
            id = hashlib.sha224(file).hexdigest()
            collaborate.FileDiffManager().remove_diff(id)
            collaborate.FileDiffManager().create_diff(id)
            collaborate.FileSessionManager().broadcast(file, {'t': 's'})
        except:
            pass
        self.finish(self.write(json.dumps({
            'success': True,
            'notification': 'last saved: ' + time.strftime('%Y-%m-%d %H:%M:%S')
        })))
    
    def post(self):
        """Post request; same logic as the GET request."""
        self.get()