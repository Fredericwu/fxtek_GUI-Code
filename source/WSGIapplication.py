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

html = """
<html>
<body>
   <form method="post" action="">
        <p>
           Age: <input type="text" name="age" value="%(age)s">
        </p>
        <p>
            Hobbies:
            <input
                name="hobbies" type="checkbox" value="software"
                %(checked-software)s
            > Software
            <input
                name="hobbies" type="checkbox" value="tunning"
                %(checked-tunning)s
            > Auto Tunning
        </p>
        <p>
            <input type="submit" value="Submit">
        </p>
    </form>
    <p>
        Age: %(age)s<br>
        Hobbies: %(hobbies)s
    </p>
</body>
</html>
"""

def application(environ, start_response):

    # the environment variable CONTENT_LENGTH may be empty or missing
    try:
        request_body_size = int(environ.get('CONTENT_LENGTH', 0))
        print '1'
    except (ValueError):
        request_body_size = 0
        print '2'

    # When the method is POST the variable will be sent
    # in the HTTP request body which is passed by the WSGI server
    # in the file like wsgi.input environment variable.
    request_body = environ['wsgi.input'].read(request_body_size)
    print '3', request_body

    d = parse_qs(request_body)
    print '4', d

    age = d.get('age', [''])[0] # Returns the first age value.
    hobbies = d.get('hobbies', []) # Returns a list of hobbies.

    # Always escape user input to avoid script injection
    age = escape(age)
    hobbies = [escape(hobby) for hobby in hobbies]

    response_body = html % { # Fill the above html template in
        'checked-software': ('', 'checked')['software' in hobbies],
        'checked-tunning': ('', 'checked')['tunning' in hobbies],
        'age': age or 'Empty',
        'hobbies': ', '.join(hobbies or ['No Hobbies?'])
    }

    status = '200 OK'
    response_headers = [('Content-Type', 'text/html'), ('Content-Length', str(len(response_body)))]

    start_response(status, response_headers)
    return [response_body]

try:
    httpd = make_server('localhost', 8051, application)
    print('Serving on port 8051...')
    httpd.serve_forever()
except KeyboardInterrupt:
    print('\nGoodbye.')

