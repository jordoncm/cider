#!/usr/bin/env python

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

class FileManager(Base):
    def fileList(self):
        return []
