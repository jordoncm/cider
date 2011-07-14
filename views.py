#!/usr/bin/env python

import pystache
import os

class Home(pystache.View):
    template_path = os.path.dirname(__file__) + '/templates'

    def title(self):
        return 'Cider - Dashboard'
    
    def terminalLink(self):
        req = self.get('req', None)
        return 'https://' + req.hostname + ':4200'
