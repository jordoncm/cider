from operator import itemgetter

import os
import tornado.template
import tornado.web

import handlers.auth.dropbox
import log
import util

class DropboxHandler(handlers.auth.dropbox.BaseAuthHandler, handlers.auth.dropbox.Mixin):
    @tornado.web.authenticated
    @tornado.web.asynchronous
    def get(self):
        path = self.get_argument('path', '').replace('..', '').strip('/')
        self.dropbox_request(
            '/metadata/dropbox/' + path,
            access_token = self.current_user['access_token'],
            callback = self.async_callback(self.getCallback)
        )
    def getCallback(self, response):
        if not response:
            self.authorize_redirect('/auth/dropbox/')
            return
        path = self.get_argument('path', '').replace('..', '').strip('/')
        title = path + ' - Cider'
        base = ''
        
        files = []
        for file in response['contents']:
            files.append({
                'name' : os.path.basename(file['path']),
                'isFile' : not file['is_dir'],
                'confirm' : ''
            })
        files = sorted(files, key = lambda x: x['name'].encode().lower())
        files = sorted(files, key = itemgetter('isFile'))
        
        if path != '' and path.rfind('/') > -1:
            up = path[:path.rfind('/')]
        else:
            up = ''
        
        self.set_header('Content-Type', 'text/html')
        loader = tornado.template.Loader('templates')
        self.finish(loader.load('file-manager.html').generate(
            title = title,
            base = base,
            path = path,
            filesList = files,
            up = up
        ))

class FileSystemHandler(tornado.web.RequestHandler):
    def get(self):
        path = self.get_argument('path', '').replace('..', '').strip('/')
        title = path + ' - Cider'
        base = os.path.join(os.path.dirname(__file__), util.getBasePathAdjustment())
        
        files = []
        try:
            fileList = os.listdir(os.path.join(base, path))
            fileList.sort(key = lambda x: x.encode().lower())
            
            for i in range(len(fileList)):
                try:
                    file = os.path.join(base, path, fileList[i])
                    isFile = os.path.isfile(file)
                    confirm = ''
                    if isFile and os.path.getsize(file) > 10485760:
                        confirm = 'large'
                    if isFile and not util.isTextFile(file):
                        confirm = 'binary'
                    files.append({
                        'name' : fileList[i],
                        'isFile' : isFile,
                        'confirm' : confirm
                    })
                except IOError as e:
                    log.warn(e)
            
            files = sorted(files, key = itemgetter('isFile'))
        except Exception as e:
            log.warn(e)
        
        if path != '' and path.rfind('/') > -1:
            up = path[:path.rfind('/')]
        else:
            up = ''
        
        self.set_header('Content-Type', 'text/html')
        loader = tornado.template.Loader('templates')
        self.write(loader.load('file-manager.html').generate(
            title = title,
            base = base,
            path = path,
            filesList = files,
            up = up
        ))