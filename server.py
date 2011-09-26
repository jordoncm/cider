#!/usr/bin/env python

import json
import os
import time
import tornado.ioloop
import tornado.web

import views

BASE_PATH_ADJUSTMENT = '..'

class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        self.set_header('Content-Type', 'text/html')
        v = views.Index(None, None, host = self.request.host)
        self.write(v.render())

class EditorHandler(tornado.web.RequestHandler):
    def get(self):
        self.set_header('Content-Type', 'text/html')
        v = views.Editor(None, None, file = self.get_argument('file', ''))
        self.write(v.render())

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
    application.listen(3333)
    tornado.ioloop.IOLoop.instance().start()