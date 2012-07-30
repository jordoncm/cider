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

class DropboxSaveFileHandler(handlers.auth.dropbox.BaseAuthHandler, handlers.auth.dropbox.Mixin):
    @tornado.web.authenticated
    @tornado.web.asynchronous
    def get(self):
        file = self.get_argument('file', '').replace('..', '').strip('/')
        self.dropbox_put(
            '/files_put/dropbox/' + file,
            access_token = self.current_user['access_token'],
            callback = self.async_callback(self.getCallback),
            put_args = self.get_argument('text')
        )
    def getCallback(self, response):
        if not response:
            self.authorize_redirect('/auth/dropbox/')
            return
        file = self.get_argument('file', '').replace('..', '').strip('/')
        try:
            id = hashlib.sha224(file).hexdigest()
            collaborate.FileDiffManager().removeDiff(id)
            collaborate.FileDiffManager().createDiff(id)
            collaborate.FileSessionManager().broadcast(file, {'t' : 's'})
        except:
            pass
        self.finish(self.write(json.dumps({
            'success' : True,
            'notification' : 'last saved: ' + time.strftime('%Y-%m-%d %H:%M:%S')
        })))
    def post(self):
        self.get()

class FileSystemSaveFileHandler(tornado.web.RequestHandler):
    def get(self):
        self.set_header('Content-Type', 'application/json')
        try:
            file = self.get_argument('file', '').replace('..', '').strip('/')
            f = open(
                os.path.join(
                    os.path.dirname(__file__),
                    util.getBasePathAdjustment(),
                    file
                ),
                'w'
            )
            f.write(self.get_argument('text'))
            f.close()
            
            try:
                id = hashlib.sha224(file).hexdigest()
                collaborate.FileDiffManager().removeDiff(id)
                collaborate.FileDiffManager().createDiff(id)
                collaborate.FileSessionManager().broadcast(file, {'t' : 's'})
            except:
                pass
            
            success = True
            notification = 'last saved: ' + time.strftime('%Y-%m-%d %H:%M:%S')
        except Exception as e:
            log.error(e)
            success = False
            notification = 'save failed'
        
        self.write(json.dumps({
            'success' : success,
            'notification' : notification
        }))
    def post(self):
        self.get()