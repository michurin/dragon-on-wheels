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


import logging
import time

from dragon_on_wheels.server import Server
from dragon_on_wheels.processors import WSGI, shell_stat
from dragon_on_wheels import __doc__ as welcome_message, __version__ as version


logger = logging.getLogger(__name__)


def testrun():
    lgr = logging.getLogger('dragon_on_wheels')
    lgr.setLevel(logging.DEBUG)
    fh = logging.StreamHandler()
    fh.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s %(process)d:%(thread)d [%(levelname)s] %(message)s')
    fh.setFormatter(formatter)
    lgr.addHandler(fh)
    lgr.info('Run demo server')
    def simple_app(environ, start_response):
        start_response('200 OK', [('Content-type', 'text/plain; charset=utf-8')])
        return ['%s\nVersion = %s\n\nEnviron:\n\n%s\n\ntime.asctime() = %s\n' % (
            welcome_message,
            version,
            '\n'.join(map(lambda x: '%s = %s' % (
                x,
                repr(environ[x])
            ), sorted(environ.keys()))),
            time.asctime()
        )]
    Server((
        (('127.0.0.1', 9002), WSGI(simple_app, 'Server_on_port_9002', 10)),
        (('127.0.0.1', 9003), WSGI(simple_app, 'Server_on_port_9003', 2)),
        (('127.0.0.1', 9004), shell_stat),
    )).serve_forever()


if __name__ == '__main__':
    testrun()
