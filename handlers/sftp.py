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
import time
import tornado.template
import tornado.web

import collaborate
import log
import util


class CreateFolderHandler(tornado.web.RequestHandler):
    """Handles the request to create a new folder."""
    pass


class DownloadHandler(tornado.web.RequestHandler):
    """Handles file download requests."""
    pass


class EditorHandler(tornado.web.RequestHandler):
    """Handles editor requests."""
    pass


class FileManagerHandler(tornado.web.RequestHandler):
    """Handles the file manager requests."""
    
    def get(self):
        if self.get_argument('connection', None) is not None:
            id = self.get_argument('connection')
            details = json.loads(self.get_secure_cookie('sftp-' + id))
            server = pysftp.Connection(
                host=details['host'],
                username=details['user'],
                password=details['password']
            )
            
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
                        if len(server.execute('if test -d ' + file.replace(' ', '\ ') + '; then echo -n 1; fi')):
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
                base=base,
                path=path,
                files_list=files,
                up=up,
                folder=self.get_argument('folder', ''),
                extra='&connection=' + id
            ))
            
            server.close()
        else:
            id = self.setup_connection()
            self.redirect('?connection=' + id)
    
    def post(self):
        self.get()
    
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
        self.set_secure_cookie('sftp-' + id, json.dumps(details))
        return id


class SaveFileHandler(tornado.web.RequestHandler):
    """Handles file saving requests."""
    pass