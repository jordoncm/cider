#!/usr/bin/env python

import views

def index(req):
    req.content_type = 'text/html'
    v = views.Home(None, None, req=req)
    return v.render()
