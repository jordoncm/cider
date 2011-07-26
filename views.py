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
        return 'views.py'
        environ = self.get('environ', None)
        form = cgi.FieldStorage(fp = environ['wsgi.input'], environ = environ)
        return form.getvalue('file')

    def text(self):
        f = open(os.path.dirname(__file__) + '/' + self.file(), 'r')
        return f.read()

    def mode(self):
        file = self.file()
        ext = file[(file.rfind('.') + 1):]

        if ext == 'py':
            return 'python'
        else:
            return 'javascript'

class FileManager(Base):
    def fileList(self):
        return []
