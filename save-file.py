#!/usr/bin/env python

import cgi
import os
import sys
sys.path.append(os.path.dirname(__file__))

def application(environ, start_response):
    start_response('200 OK', [('Content-type', 'text/html')])
    form = cgi.FieldStorage(fp = environ['wsgi.input'], environ = environ)
    f = open(os.path.dirname(__file__) + '/' + form.getvalue('file'), 'w')
    f.write(form.getvalue('text'))
    f.close()
    return ['OK']
