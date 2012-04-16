#!/usr/bin/env python

# 
# This work is copyright 2011 Jordon Mears. All rights reserved.
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

import json
import os
import sys
import thread
import time
import tornado.ioloop
import tornado.template
import tornado.web
import webbrowser

try:
    __file__
except NameError:
    if hasattr(sys, 'frozen') and sys.frozen in ('windows_exe', 'console_exe'):
        __file__ = os.path.dirname(os.path.abspath(sys.executable))

def getConfigurationValue(key):
    try:
        return json.loads(open(os.path.join(
            os.path.dirname(__file__),
            'configuration.json'
        )).read())[key]
    except:
        return None

BASE_PATH_ADJUSTMENT = getConfigurationValue('basePathAdjustment')
if BASE_PATH_ADJUSTMENT == None:
    BASE_PATH_ADJUSTMENT = '..'

class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        terminalLink = getConfigurationValue('terminalLink')
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

class EditorHandler(tornado.web.RequestHandler):
    def get(self):
        file = self.get_argument('file', '').replace('..', '').strip('/')
        
        if file.find('/') != -1:
            fileName = file[(file.rfind('/') + 1):]
            path = file[:file.rfind('/')]
            title = '[' + fileName + '] ' + path + ' - Cider'
        else:
            fileName = file
            path = ''
            title = '[' + fileName + '] - Cider'
        
        try:
            f = open(
                os.path.join(
                    os.path.dirname(__file__),
                    BASE_PATH_ADJUSTMENT,
                    file
                ),
                'r'
            )
            text = f.read().replace('{', '~' + 'lb').replace('}', '~' + 'rb')
            
            saveText = 'Saved'
        except Exception:
            text = ''
            saveText = 'Save'
        
        tabWidth = 4
        
        ext = file[(file.rfind('.') + 1):]

        if ext == 'c' or ext == 'cpp':
            mode = 'c_cpp'
        elif ext == 'cs':
            mode = 'csharp'
        elif ext == 'css':
            mode = 'css'
        elif ext == 'groovy':
            mode = 'groovy'
        elif ext == 'html' or ext == 'mustache' or ext == 'tpl':
            mode = 'html'
            tabWidth = 2
        elif ext == 'java':
            mode = 'java'
        elif ext == 'js':
            mode = 'javascript'
        elif ext == 'json':
            mode = 'json'
        elif ext == 'php' or ext == 'inc':
            mode = 'php'
        elif ext == 'py':
            mode = 'python'
        elif ext == 'rb':
            mode = 'ruby'
        elif ext == 'sql':
            mode = 'sql'    
        elif ext == 'svg':
            mode = 'svg'
            tabWidth = 2
        elif ext == 'xml' or ext == 'kml':
            mode = 'xml'
            tabWidth = 2
        else:
            mode = 'text'
        
        self.set_header('Content-Type', 'text/html')
        loader = tornado.template.Loader('templates')
        self.write(loader.load('editor.html').generate(
            fileName = fileName,
            path = path,
            title = title,
            file = file,
            text = text,
            mode = mode,
            tabWidth = tabWidth,
            saveText = saveText
        ))

class SaveFileHandler(tornado.web.RequestHandler):
    def get(self):
        self.set_header('Content-Type', 'application/json')
        try:
            f = open(
                os.path.join(
                    os.path.dirname(__file__),
                    BASE_PATH_ADJUSTMENT,
                    self.get_argument('file', '').replace('..', '').strip('/')
                ),
                'w'
            )
            f.write(self.get_argument('text'))
            f.close()
            
            success = True
            notification = 'last saved: ' + time.strftime('%Y-%m-%d %H:%M:%S')
        except:
            success = False
            notification = 'save failed'
        
        self.write(json.dumps({
            'success' : success,
            'notification' : notification
        }))
    def post(self):
        self.get()

class FileManagerHandler(tornado.web.RequestHandler):
    def get(self):
        path = self.get_argument('path', '').replace('..', '').strip('/')
        
        title = path + ' - Cider'
        
        base = os.path.join(os.path.dirname(__file__), BASE_PATH_ADJUSTMENT)
        
        files = []
        files = os.listdir(os.path.join(base, path))
        files.sort(key = lambda x: x.encode().lower())
        
        for i in range(len(files)):
            files[i] = {
                'name' : files[i],
                'isFile' : os.path.isfile(
                    os.path.join(base, path, files[i])
                )
            }
        
        files = sorted(files, key = itemgetter('isFile'))
        
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

class DownloadHandler(tornado.web.RequestHandler):
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
        except Exception:
            data = None
            length = 0
        
        self.set_header('Content-Type', 'application/force-download');
        self.set_header('Content-Disposition', 'attachment; filename="' + fileName + '"');
        self.set_header('Content-Length', length);
        
        self.write(data)
        

class CreateFolderHandler(tornado.web.RequestHandler):
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

class DeleteFileHandler(tornado.web.RequestHandler):
    pass

class DeleteFolderHandler(tornado.web.RequestHandler):
    pass

settings = {
    'static_path' : os.path.join(os.path.dirname(__file__), 'static')
}

application = tornado.web.Application([
    (r'/', IndexHandler),
    (r'/editor/?', EditorHandler),
    (r'/save-file/?', SaveFileHandler),
    (r'/file-manager/?', FileManagerHandler),
    (r'/download/?', DownloadHandler),
    (r'/create-folder/?', CreateFolderHandler)
], **settings)

def start():
    application.listen(3333)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == '__main__':
    try:
        thread.start_new_thread(start, ())
        webbrowser.open_new_tab('http://localhost:3333')
        
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