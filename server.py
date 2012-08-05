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

gui = False
try:
    from Tkinter import *
    gui = True
except ImportError:
    gui = False

import hashlib
import json
import os
import sys
import thread
import time
import tornado.ioloop
import tornado.template
import tornado.web
import tornado.websocket
import webbrowser

import collaborate
import handlers.auth.dropbox
import handlers.dropbox
import handlers.file
import log
import util

try:
    __file__
except NameError:
    if hasattr(sys, 'frozen') and sys.frozen in ('windows_exe', 'console_exe'):
        __file__ = os.path.dirname(os.path.abspath(sys.executable))


class IndexHandler(tornado.web.RequestHandler):
    
    def get(self):
        terminal_link = util.get_configuration_value('terminalLink')
        if terminal_link != None:
            host = self.request.host
            host = host[:host.find(':')]
            terminal_link = terminal_link.replace('[host]', host)
        
        enable_dropbox = False
        if util.get_configuration_value('dropboxKey', '') != '' and util.get_configuration_value('dropboxSecret', '') != '':
            enable_dropbox = True
        
        self.set_header('Content-Type', 'text/html')
        loader = tornado.template.Loader('templates')
        self.write(loader.load('index.html').generate(
            title = 'Dashboard - Cider',
            terminal_link = terminal_link,
            enable_local_file_system = util.get_configuration_value(
                'enableLocalFileSystem',
                True
            ),
            enable_dropbox = enable_dropbox
        ))


class EditorWebSocketHandler(tornado.websocket.WebSocketHandler):
    
    def open(self):
        self.file = None
        self.name = None
        collaborate.FileSessionManager().register_session(self)
    
    def on_message(self, message):
        message_object = json.loads(message)
        if message_object['t'] == 'f':
            self.file = message_object['f']
            self.name = message_object['n']
            sessions = collaborate.FileSessionManager().get_sessions(self.file)
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
        elif message_object['t'] == 'd' and self.file != None:
            collaborate.FileSessionManager().notify(self, message_object)
        elif message_object['t'] == 'i' and self.file != None:
            collaborate.FileSessionManager().notify(self, message_object)
        
        id = hashlib.sha224(self.file).hexdigest()
        if message_object['t'] == 'f':
            if collaborate.FileDiffManager().has_diff(id) == False:
                collaborate.FileDiffManager().create_diff(id)
            else:
                self.write_message(
                    json.dumps(collaborate.FileDiffManager().get_all(id))
                )
        else:
            collaborate.FileDiffManager().add(id, message_object)
    
    def on_close(self):
        file = self.file
        collaborate.FileSessionManager().unregister_session(self)
        sessions = collaborate.FileSessionManager().get_sessions(file)
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
        if collaborate.FileSessionManager().has_sessions(file) == False:
            id = hashlib.sha224(self.file).hexdigest()
            collaborate.FileDiffManager().remove_diff(id)

settings = {
    'autoescape' : None,
    'cookie_secret' : util.get_configuration_value('cookieSecret', 'aW5zZWN1cmVTZWNyZXQ='),
    'dropbox_consumer_key' : util.get_configuration_value('dropboxKey', ''),
    'dropbox_consumer_secret' : util.get_configuration_value('dropboxSecret', ''),
    'login_url' : '/',
    'static_path' : os.path.join(os.path.dirname(__file__), 'static'),
}

urls = [
    (r'/', IndexHandler),
    (r'/ws/?', EditorWebSocketHandler)
]

if util.get_configuration_value('dropboxKey', '') != '' and util.get_configuration_value('dropboxSecret', '') != '':
    urls = urls + [
        (r'/auth/dropbox/?', handlers.auth.dropbox.DropboxHandler),
        (r'/dropbox/create-folder/?', handlers.dropbox.CreateFolderHandler),
        (r'/dropbox/download/?', handlers.dropbox.DownloadHandler),
        (r'/dropbox/editor/?', handlers.dropbox.EditorHandler),
        (r'/dropbox/file-manager/?', handlers.dropbox.FileManagerHandler),
        (r'/dropbox/save-file/?', handlers.dropbox.SaveFileHandler)
    ]

if util.get_configuration_value('enableLocalFileSystem', True):
    urls = urls + [
        (r'/file/create-folder/?', handlers.file.CreateFolderHandler),
        (r'/file/download/?', handlers.file.DownloadHandler),
        (r'/file/editor/?', handlers.file.EditorHandler),
        (r'/file/file-manager/?', handlers.file.FileManagerHandler),
        (r'/file/save-file/?', handlers.file.SaveFileHandler)
    ]

application = tornado.web.Application(urls, **settings)


def start():
    log.msg('Starting server...')
    port = util.get_configuration_value('port', 3333)
    log.msg('Listening on port ' + str(port) + '.')
    application.listen(port)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == '__main__':
    try:
        thread.start_new_thread(start, ())
        if util.get_configuration_value('suppressBrowser', False) == False:
            webbrowser.open_new_tab(
                'http://localhost:' + str(util.get_configuration_value('port', 3333))
            )
        
        if gui == True:
            try:
                root = Tk()
                root.withdraw()
                menu = Menu(root)
                root.config(menu = menu)
                root.mainloop()
            except KeyboardInterrupt:
                sys.exit()
            except Exception:
                log.msg('Graphical main loop failed, using time sleep instead.')
                while(True):
                    time.sleep(10)
        else:
            log.msg('Graphical libraries not present, using time sleep instead.')
            while(True):
                time.sleep(10)
    except KeyboardInterrupt:
        sys.exit()