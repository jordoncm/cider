#!/usr/bin/env python

import cgi
import json
import os
import sys
import time
sys.path.append(os.path.dirname(__file__))

def application(environ, start_response):
    start_response('200 OK', [('Content-type', 'application/json')])
    form = cgi.FieldStorage(fp = environ['wsgi.input'], environ = environ)
    f = open(os.path.dirname(__file__) + '/' + form.getvalue('file'), 'w')
    f.write(form.getvalue('text'))
    f.close()
    return json.dumps({
        'success' : True,
        'notification' : 'last saved: ' + time.strftime('%Y-%m-%d %H:%I:%S')
    })
