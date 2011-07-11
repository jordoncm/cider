#!/usr/bin/env python

import views

def index(req):
    req.content_type = 'text/html'
    """
    output = []
    output.append('<!DOCTYPE HTML>')
    output.append('<html>')
    output.append('<head>')
    output.append('<title>Cider - Home</title>')
    output.append('</head>')
    output.append('<body>')
    output.append('</body>')
    output.append('</html>')
    
    return '\n'.join(output)
    """
    v = views.Base(None, None, req=req)
    return v.render()
