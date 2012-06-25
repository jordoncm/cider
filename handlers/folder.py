import tornado.web
import os
import json

import handlers.auth.dropbox
import log
import util

BASE_PATH_ADJUSTMENT = util.getBasePathAdjustment()

class DropboxCreateFolderHandler(handlers.auth.dropbox.BaseAuthHandler, handlers.auth.dropbox.Mixin):
    @tornado.web.authenticated
    @tornado.web.asynchronous
    def get(self):
        path = self.get_argument('path', '').replace('..', '').strip('/')
        self.dropbox_request(
            '/fileops/create_folder',
            access_token = self.current_user['access_token'],
            callback = self.async_callback(self.getCallback),
            post_args = {'root' : 'dropbox', 'path' : path}
        )
    def getCallback(self, response):
        if not response:
            self.authorize_redirect('/auth/dropbox/')
            return
        
        self.finish(json.dumps({
            'success' : True
        }))

class FileSystemCreateFolderHandler(tornado.web.RequestHandler):
    def get(self):
        self.set_header('Content-Type', 'application/json')
        try:
            path = self.get_argument('path', '').replace('..', '').strip('/')
            
            os.mkdir(os.path.join(
                os.path.dirname(__file__),
                BASE_PATH_ADJUSTMENT,
                path
            ))
            
            self.write(json.dumps({
                'success' : True
            }))
        except:
            self.write(json.dumps({
                'success' : False
            }))