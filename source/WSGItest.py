#!/usr/bin/python
"""
WSGI Applicaton Module

Created by Susan Cheng on 2017-02-05.
Copyright (c) 2014-2017 __Loxoll__. All rights reserved.
"""
#
# To test:
# ./source> python WSGIapplication.py
# http://localhost:8051
#
import os, sys, time, glob
from wsgiref.simple_server import make_server   # Python's bundled WSGI server
from cgi import parse_qs, escape

file_name = os.path.basename(__file__)

import cgi

form = b'''
<html>
    <head>
        <title>Hello User!</title>
    </head>
    <body>
        <form method="post">
            <label>Hello</label>
            <input type="text" name="name">
            <input type="submit" value="Go">
        </form>
    </body>
</html>
'''

def app(environ, start_response):
    html = form

    if environ['REQUEST_METHOD'] == 'POST':
        post_env = environ.copy()
        post_env['QUERY_STRING'] = ''
        post = cgi.FieldStorage(
            fp=environ['wsgi.input'],
            environ=post_env,
            keep_blank_values=True
        )
        html = b'Hello, ' + post['name'].value + '!'

    start_response('200 OK', [('Content-Type', 'text/html')])
    return [html]

if __name__ == '__main__':
    try:
        from wsgiref.simple_server import make_server
        httpd = make_server('', 8080, app)
        print('Serving on port 8080...')
        httpd.serve_forever()
    except KeyboardInterrupt:
        print('\nGoodbye.')

