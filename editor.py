#!/usr/env/bin python

import os
import sys
sys.path.append(os.path.dirname(__file__))

import views

def application(environ, start_response):
    start_response('200 OK', [('Content-type', 'text/html')])
    v = views.Editor(None, None, environ=environ)
    return [v.render('ascii')]
