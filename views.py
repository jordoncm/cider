#!/usr/bin/env python

import cgi
import os
import pystache

class Base(pystache.View):
    template_path = os.path.dirname(__file__) + '/templates'

class Home(Base):
    def title(self):
        return 'Cider - Dashboard'
    
    def terminalLink(self):
        environ = self.get('environ', None)
        return 'https://' + environ['SERVER_NAME'] + ':4200'

class Editor(Base):
    def title(self):
        return 'Cider - ' + self.file()
    
    def file(self):
        environ = self.get('environ', None)
        form = cgi.FieldStorage(fp = environ['wsgi.input'], environ = environ)
        return form.getvalue('file')

    def text(self):
        try:
            f = open(os.path.dirname(__file__) + os.sep + self.file(), 'r')
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
    def fileList(self):
        return []
