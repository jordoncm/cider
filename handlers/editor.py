import os
import tornado.template
import tornado.web

import handlers.auth.dropbox
import log
import util

def getMode(ext):
    mode, tabWidth, markup = getModeTabWidthMarkup(ext)
    return mode

def getModeTabWidthMarkup(ext):
    tabWidth = 4
    markup = False
    
    if ext == 'c' or ext == 'cpp' or ext == 'h' or ext == 'hpp':
        mode = 'c_cpp'
    elif ext == 'clj':
        mode = 'clojure'
    elif ext == 'coffee':
        mode = 'coffee'
    elif ext == 'cfc' or ext == 'cfm':
        mode = 'coldfusion'
    elif ext == 'cs':
        mode = 'csharp'
    elif ext == 'css':
        mode = 'css'
    elif ext == 'go':
        mode = 'go'
    elif ext == 'groovy':
        mode = 'groovy'
    elif ext == 'hx':
        mode = 'haxe'
    elif ext == 'htm' or ext == 'html' or ext == 'mustache' or ext == 'tpl' or ext == 'shtml':
        mode = 'html'
        tabWidth = 2
        markup = True
    elif ext == 'java':
        mode = 'java'
    elif ext == 'js':
        mode = 'javascript'
    elif ext == 'json':
        mode = 'json'
    elif ext == 'tex':
        mode = 'latex'
    elif ext == 'less':
        mode = 'less'
    elif ext == 'liquid':
        mode = 'liquid'
    elif ext == 'lua':
        mode = 'lua'
    elif ext == 'markdown' or ext == 'mdown' or ext == 'mdown' or ext == 'md' or ext == 'mkd' or ext == 'mkdn':
        mode = 'markdown'
    elif ext == 'ocaml' or ext == 'ml' or ext == 'mli':
        mode = 'ocaml'
    elif ext == 'pl' or ext == 'pm' or ext == 't':
        mode = 'perl'
    elif ext == 'pgsql':
        mode = 'pgsql'
    elif ext == 'php' or ext == 'inc' or ext == 'phtml' or ext == 'phps':
        mode = 'php'
    elif ext == 'ps1':
        mode = 'powershell'
    elif ext == 'py' or ext == 'pyw':
        mode = 'python'
    elif ext == 'rb' or ext == 'rbw':
        mode = 'ruby'
    elif ext == 'scad':
        mode = 'scad'
    elif ext == 'scala':
        mode = 'scala'
    elif ext == 'scss':
        mode = 'scss'
    elif ext == 'sh':
        mode = 'sh'
    elif ext == 'sql':
        mode = 'sql'
    elif ext == 'svg':
        mode = 'svg'
        tabWidth = 2
        markup = True
    elif ext == 'textile':
        mode = 'textile'
    elif ext == 'xml' or ext == 'kml':
        mode = 'xml'
        tabWidth = 2
        markup = True
    elif ext == 'xq' or ext == 'xqy' or ext == 'xquery':
        mode = 'xquery'
    else:
        mode = 'text'
    
    return mode, tabWidth, markup

def getTabWidth(ext):
    mode, tabWidth, markup = getModeTabWidthMarkup(ext)
    return tabWidth

def isMarkup(ext):
    mode, tabWidth, markup = getModeTabWidthMarkup(ext)
    return markup

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
        # Need logic around auth issues verus new file.
        '''
        if not response:
            self.authorize_redirect('/auth/dropbox/')
            return
        '''
        file = self.get_argument('file', '').replace('..', '').strip('/')
        
        if file.find('/') != -1:
            fileName = file[(file.rfind('/') + 1):]
            path = file[:file.rfind('/')]
            title = '[' + fileName + '] ' + path + ' - Cider'
        else:
            fileName = file
            path = ''
            title = '[' + fileName + '] - Cider'
        
        if not response:
            text = ''
            saveText = 'Save'
        else:
            text = response
            saveText = 'Saved'
        
        ext = file[(file.rfind('.') + 1):]
        mode = getMode(ext)
        tabWidth = getTabWidth(ext)
        markup = isMarkup(ext)
        
        self.set_header('Content-Type', 'text/html')
        loader = tornado.template.Loader('templates')
        self.finish(loader.load('editor.html').generate(
            fileName = fileName,
            path = path,
            title = title,
            file = file,
            text = text,
            mode = mode,
            tabWidth = tabWidth,
            markup = markup,
            saveText = saveText
        ))

class FileSystemHandler(tornado.web.RequestHandler):
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
                    util.getBasePathAdjustment(),
                    file
                ),
                'r'
            )
            text = f.read().replace('{', '~' + 'lb').replace('}', '~' + 'rb')
            
            saveText = 'Saved'
        except Exception as e:
            log.warn(e)
            text = ''
            saveText = 'Save'
        
        ext = file[(file.rfind('.') + 1):]
        mode = getMode(ext)
        tabWidth = getTabWidth(ext)
        markup = isMarkup(ext)
        
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
            markup = markup,
            saveText = saveText
        ))