#!/usr/bin/env python

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

gui = False
try:
    from Tkinter import *
    gui = True
except ImportError:
    gui = False

import getpass
import hashlib
import json
import logging
import os
import pickledb
import string
import sys
import thread
import time
import tornado.auth
import tornado.ioloop
import tornado.template
import tornado.web
import tornado.websocket
import webbrowser

import collaborate
import handlers.auth.dropbox
import handlers.download
import handlers.editor
import handlers.file
import handlers.filemanager
import handlers.folder
import log
import util

try:
    __file__
except NameError:
    if hasattr(sys, 'frozen') and sys.frozen in ('windows_exe', 'console_exe'):
        __file__ = os.path.dirname(os.path.abspath(sys.executable))

BASE_PATH_ADJUSTMENT = util.getBasePathAdjustment()

class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        terminalLink = util.getConfigurationValue('terminalLink')
        if terminalLink != None:
            host = self.request.host
            host = host[:host.find(':')]
            terminalLink = terminalLink.replace('[host]', host)
        
        self.set_header('Content-Type', 'text/html')
        loader = tornado.template.Loader('templates')
        self.write(loader.load('index.html').generate(
            title = 'Dashboard - Cider',
            terminalLink = terminalLink
        ))

class EditorWebSocketHandler(tornado.websocket.WebSocketHandler):
    def open(self):
        self.file = None
        self.name = None
        collaborate.FileSessionManager().registerSession(self)
    def on_message(self, message):
        messageObject = json.loads(message)
        if messageObject['t'] == 'f':
            self.file = messageObject['f']
            self.name = messageObject['n']
            sessions = collaborate.FileSessionManager().getSessions(self.file)
            names = []
            for i in sessions:
                names.append(i.name)
            collaborate.FileSessionManager().broadcast(
                self.file,
                {
                    't' : 'n',
                    'n' : names
                }
            )
        elif messageObject['t'] == 'd' and self.file != None:
            collaborate.FileSessionManager().notify(self, messageObject)
        elif messageObject['t'] == 'i' and self.file != None:
            collaborate.FileSessionManager().notify(self, messageObject)
        
        db = pickledb.load(
            os.path.join(
                os.path.dirname(__file__),
                'patch',
                hashlib.sha224(self.file).hexdigest()
            ),
            True
        )
        if messageObject['t'] == 'f':
            if db.get('diffs') == None:
                db.lcreate('diffs')
            else:
                self.write_message(json.dumps(db.lgetall('diffs')))
        else:
            db.ladd('diffs', messageObject)
    def on_close(self):
        file = self.file
        collaborate.FileSessionManager().unregisterSession(self)
        sessions = collaborate.FileSessionManager().getSessions(file)
        names = []
        for i in sessions:
            names.append(i.name)
        collaborate.FileSessionManager().broadcast(
            self.file,
            {
                't' : 'n',
                'n' : names
            }
        )
        if collaborate.FileSessionManager().hasSessions(file) == False:
            db = pickledb.load(
                os.path.join(
                    os.path.dirname(__file__),
                    'patch',
                    hashlib.sha224(file).hexdigest()
                ),
                True
            )
            db.deldb()

settings = {
    'autoescape' : None,
    'cookie_secret' : '12oETzKXQAGaYdkL5gEmGeJJFuYh7EQnp2XdTP1o/Vo=',
    'dropbox_consumer_key' : 'rvs2rp86wlxbssd',
    'dropbox_consumer_secret' : 't4dzxao7h6w4vhk',
    'login_url' : '/',
    'static_path' : os.path.join(os.path.dirname(__file__), 'static'),
}

application = tornado.web.Application([
    (r'/', IndexHandler),
    (r'/ws/?', EditorWebSocketHandler),
    (r'/auth/dropbox/', handlers.auth.dropbox),
    (r'/dropbox/create-folder/?', handlers.folder.DropboxCreateFolderHandler),
    (r'/dropbox/download/?', handlers.download.DropboxHandler),
    (r'/dropbox/editor/?', handlers.editor.DropboxHandler),
    (r'/dropbox/file-manager/?', handlers.filemanager.DropboxHandler),
    (r'/dropbox/save-file/?', handlers.file.DropboxSaveFileHandler),
    (r'/file/create-folder/?', handlers.folder.FileSystemCreateFolderHandler),
    (r'/file/download/?', handlers.download.FileSystemHandler),
    (r'/file/editor/?', handlers.editor.FileSystemHandler),
    (r'/file/file-manager/?', handlers.filemanager.FileSystemHandler),
    (r'/file/save-file/?', handlers.file.FileSystemSaveFileHandler)
], **settings)

def start():
    log.msg('Starting server...')
    port = util.getConfigurationValue('port', 3333)
    log.msg('Listening on port ' + str(port) + '.')
    application.listen(port)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == '__main__':
    try:
        thread.start_new_thread(start, ())
        if util.getConfigurationValue('suppressBrowser', False) == False:
            webbrowser.open_new_tab(
                'http://localhost:' + str(util.getConfigurationValue('port', 3333))
            )
        
        if gui == True:
            root = Tk()
            root.withdraw()
            menu = Menu(root)
            root.config(menu = menu)
            root.mainloop()
        else:
            while(True):
                time.sleep(10)
    except KeyboardInterrupt:
        sys.exit(0)