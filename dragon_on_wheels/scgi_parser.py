# coding: utf-8

# Copyright (c) 2014-2016, Alexey V Michurin <a.michurin@gmail.com>.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification, are
# permitted provided that the following conditions are met:
#
#    1. Redistributions of source code must retain the above copyright notice, this list of
#       conditions and the following disclaimer.
#
#    2. Redistributions in binary form must reproduce the above copyright notice, this list
#       of conditions and the following disclaimer in the documentation and/or other materials
#       provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY Alexey V Michurin ''AS IS'' AND ANY EXPRESS OR IMPLIED
# WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND
# FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL Alexey V Michurin OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
# ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
# ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# The views and conclusions contained in the software and documentation are those of the
# authors and should not be interpreted as representing official policies, either expressed
# or implied, of Alexey V Michurin.


import StringIO
import logging


logger = logging.getLogger(__name__)


class SCGIInputParser:

    def __init__(self):
        self.raw = ''
        self.process = self.get_netstring_size
        self.is_complete = False

    def append(self, data):
        self.raw += data
        self.process()

    def get_netstring_size(self):
        if len(self.raw) > 10:
            x = self.raw.index(':')
            self.netstring_len = int(self.raw[:x])
            self.headers_shift = x + 1
            self.headers_len = self.netstring_len + x + 2
            self.process = self.get_headers
            self.process()

    def get_headers(self):
        if len(self.raw) >= self.headers_len:
            a = self.raw[self.headers_shift:self.headers_len - 2].split('\x00')
            self.headers = dict(zip(a[0::2], a[1::2]))
            self.request_len = self.headers_len + int(self.headers['CONTENT_LENGTH'])
            self.process = self.get_body
            self.process()

    def get_body(self):
        if len(self.raw) >= self.request_len:
            self.body = self.raw[self.headers_len:]
            self.wsgi_variables = self.headers.copy()
            self.wsgi_variables['wsgi.version'] = (1, 0)
            self.wsgi_variables['wsgi.url_scheme'] = {
                True: 'https',
                False: 'http'
            }['HTTPS' in self.headers]
            self.wsgi_variables['wsgi.input'] = StringIO.StringIO(self.body)
            self.wsgi_variables['wsgi.errors'] = StringIO.StringIO()
            self.wsgi_variables['wsgi.multithread'] = True
            self.wsgi_variables['wsgi.multiprocess'] = False
            self.wsgi_variables['wsgi.run_once'] = False
            logger.debug(
                'REQ: ' +
                ' '.join('='.join(x) for x in self.headers.items()) +
                ' BODY=' + repr(self.body)
            )
            self.is_complete = True
            self.process = None
