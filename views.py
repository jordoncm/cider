#!/usr/bin/env python

import cgi
import os
import pystache

class Base(pystache.View):
    template_path = os.path.dirname(__file__) + '/templates'

class Home(Base):
    def title(self):
        return 'Dashboard - Cider'
    
    def terminalLink(self):
        environ = self.get('environ', None)
        return 'https://' + environ['SERVER_NAME'] + ':4200'

class Editor(Base):
    def title(self):
        return self.file() + ' - Cider'
    
    def file(self):
        environ = self.get('environ', None)
        form = cgi.FieldStorage(fp = environ['wsgi.input'], environ = environ)
        return form.getvalue('file')

    def text(self):
        try:
            f = open(os.path.join(os.path.dirname(__file__), self.file()), 'r')
            return f.read().replace('{{', '~dlb').replace('}}', '~drb')
        except Exception:
            return ''

    def mode(self):
        file = self.file()
        ext = file[(file.rfind('.') + 1):]

        if ext == 'c' or ext == 'cpp':
            return 'c_cpp'
        elif ext == 'cs':
            return 'csharp'
        elif ext == 'css':
            return 'css'
        elif ext == 'html' or ext == 'mustache':
            return 'html'
        elif ext == 'java':
            return 'java'
        elif ext == 'json':
            return 'json'
        elif ext == 'php':
            return 'php'
        elif ext == 'py':
            return 'python'
        elif ext == 'rb':
            return 'ruby'
        elif ext == 'svg':
            return 'svg'
        elif ext == 'xml':
            return 'xml'
        else:
            return 'javascript'

class FileManager(Base):
    def title(self):
        return self.path() + ' - Cider'
        
    def base(self):
        return os.path.dirname(__file__)
    
    def fileList(self):
        base = self.base()
        path = self.path()
        
        files = []
        files = os.listdir(os.path.join(base, path))
        
        for i in range(len(files)):
            files[i] = {
                'name' : files[i],
                'isFile' : os.path.isfile(
                    os.path.join(base, path, files[i])
                ),
                'path' : path
            }
        
        return files
    
    def path(self):
        environ = self.get('environ', None)
        form = cgi.FieldStorage(fp = environ['wsgi.input'], environ = environ)
        if form.getvalue('path') != None:
            return form.getvalue('path')
        else:
            return ''
