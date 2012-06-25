import tornado.web
import os

import handlers.auth.dropbox
import log
import util

BASE_PATH_ADJUSTMENT = util.getBasePathAdjustment()

class DropboxHandler(handlers.auth.dropbox.BaseAuthHandler, handlers.auth.dropbox.Mixin):
    @tornado.web.authenticated
    @tornado.web.asynchronous
    def get(self):
        file = self.get_argument('file', '').replace('..', '').strip('/')
        self.dropbox_request(
            '/files/dropbox/' + file,
            access_token = self.current_user['access_token'],
            callback = self.async_callback(self.getCallback)
        )
    def getCallback(self, response):
        if not response:
            self.authorize_redirect('/auth/dropbox/')
            return
        file = self.get_argument('file', '').replace('..', '').strip('/')
        
        if file.find('/') != -1:
            fileName = file[(file.rfind('/') + 1):]
            path = file[:file.rfind('/')]
        else:
            fileName = file
            path = ''
        
        self.set_header('Content-Type', 'application/force-download');
        self.set_header('Content-Disposition', 'attachment; filename="' + fileName + '"');
        
        self.finish(response)

class FileSystemHandler(tornado.web.RequestHandler):
    def get(self):
        file = self.get_argument('file', '').replace('..', '').strip('/')
        
        if file.find('/') != -1:
            fileName = file[(file.rfind('/') + 1):]
            path = file[:file.rfind('/')]
        else:
            fileName = file
            path = ''
        
        try:
            f = open(
                os.path.join(
                    os.path.dirname(__file__),
                    BASE_PATH_ADJUSTMENT,
                    file
                ),
                'rb'
            )
            data = f.read()
            length = os.path.getsize(os.path.join(
                os.path.dirname(__file__),
                BASE_PATH_ADJUSTMENT,
                file
            ))
        except Exception as e:
            log.error(e)
            data = None
            length = 0
        
        self.set_header('Content-Type', 'application/force-download');
        self.set_header('Content-Disposition', 'attachment; filename="' + fileName + '"');
        self.set_header('Content-Length', length);
        
        self.write(data)