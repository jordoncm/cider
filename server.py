#!/usr/bin/env python

import json
import os
import time
import tornado.ioloop
import tornado.template
import tornado.web

import views

BASE_PATH_ADJUSTMENT = '..'

class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        host = self.request.host
        host = host[:host.find(':')]
        host = 'https://' + host + ':4200'
        
        self.set_header('Content-Type', 'text/html')
        loader = tornado.template.Loader('templates')
        self.write(loader.load('index.html').generate(
            title = 'Dashboard - Cider',
            terminalLink = host
        ))

class EditorHandler(tornado.web.RequestHandler):
    def get(self):
        file = self.get_argument('file', '')
        
        # try:
        f = open(
            os.path.join(
                os.path.dirname(__file__),
                BASE_PATH_ADJUSTMENT,
                file
            ),
            'r'
        )
        text = f.read().replace('{', '~' + 'lb').replace('}', '~' + 'rb')
        # except Exception:
        #     text = ''
        
        ext = file[(file.rfind('.') + 1):]

        if ext == 'c' or ext == 'cpp':
            mode = 'c_cpp'
        elif ext == 'cs':
            mode = 'csharp'
        elif ext == 'css':
            mode = 'css'
        elif ext == 'html' or ext == 'mustache':
            mode = 'html'
        elif ext == 'java':
            mode = 'java'
        elif ext == 'js':
            mode = 'javascript'
        elif ext == 'json':
            mode = 'json'
        elif ext == 'php':
            mode = 'php'
        elif ext == 'py':
            mode = 'python'
        elif ext == 'rb':
            mode = 'ruby'
        elif ext == 'svg':
            mode = 'svg'
        elif ext == 'xml':
            mode = 'xml'
        else:
            mode = ''
        
        self.set_header('Content-Type', 'text/html')
        loader = tornado.template.Loader('templates')
        self.write(loader.load('editor.html').generate(
            title = file + ' - Cider',
            file = file,
            text = text,
            mode = mode
        ))
        '''
        v = views.Editor(None, None, file = self.get_argument('file', ''))
        self.write(v.render())
        '''

class SaveFileHandler(tornado.web.RequestHandler):
    def get(self):
        self.set_header('Content-Type', 'application/json')
        f = open(
            os.path.join(
                os.path.dirname(__file__),
                BASE_PATH_ADJUSTMENT,
                self.get_argument('file')
            ),
            'w'
        )
        f.write(self.get_argument('text'))
        f.close()
        self.write(json.dumps({
            'success' : True,
            'notification' : 'last saved: ' + time.strftime('%Y-%m-%d %H:%M:%S')
        }))
    def post(self):
        self.get()

class FileManagerHandler(tornado.web.RequestHandler):
    def get(self):
        self.set_header('Content-Type', 'text/html')
        v = views.FileManager(None, None, path = self.get_argument('path', ''))
        self.write(v.render())

application = tornado.web.Application([
    (r'/', IndexHandler),
    (r'/editor/?', EditorHandler),
    (r'/save-file/?', SaveFileHandler),
    (r'/file-manager/?', FileManagerHandler),
    (r'/ace/(.*)', tornado.web.StaticFileHandler, {'path' : './ace'}),
    (r'/images/(.*)', tornado.web.StaticFileHandler, {'path' : './images'}),
    (r'/javascript/(.*)', tornado.web.StaticFileHandler, {'path' : './javascript'}),
    (r'/(.*)', tornado.web.StaticFileHandler, {'path' : './css'})
])

if __name__ == '__main__':
    application.listen(4444)
    tornado.ioloop.IOLoop.instance().start()