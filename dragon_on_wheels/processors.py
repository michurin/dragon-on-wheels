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


from dragon_on_wheels.stat import info, Stat
from dragon_on_wheels.scgi_parser import SCGIInputParser

import socket
import errno
import logging


__all__ = 'WSGI', 'shell_stat'


logger = logging.getLogger(__name__)


DISCONNECTED = frozenset((
    errno.ECONNRESET,
    errno.ENOTCONN,
    errno.ESHUTDOWN,
    errno.ECONNABORTED,
    errno.EPIPE,
    errno.EBADF))


def delivery_message(sock, mess):
    try:
        while len(mess) > 0:
            n = sock.send(mess)
            if n == len(mess):
                break
            mess = mess[n:]
    except socket.error, why:
        en = why[0]
        if en in DISCONNECTED:
            logger.warning('DISCONNECTED on send')
        else:
            raise


def close_socket(sock):
    try:
        sock.shutdown(socket.SHUT_RDWR)
        sock.close()
    except socket.error, why:
        en = why[0]
        if en in DISCONNECTED:
            logger.warning('DISCONNECTED on close')
        else:
            raise


def shell_stat((sock, addr)):
    delivery_message(sock, ''.join(
        "SCGI_SERVER_%s='%s'\n" % (
            p, str(q).replace("'", "'\"'\"'")
        ) for p, q in info().items()
    ))
    close_socket(sock)


class StartResponseWriter:

    # PEP3333
    # New WSGI applications and frameworks should not use
    # the write() callable if it is possible

    def __init__(self, start_response):
        self.start_response = start_response

    def __call__(self, data):
        self.start_response.data += data


class StartResponse:

    def __call__(self, status, response_headers, exc_info=None):
        if not exc_info is None:
            raise exc_info[0], exc_info[1], exc_info[2]
        self.status = status
        self.response_headers = response_headers
        self.data = ''
        return StartResponseWriter(self)


class WSGI:

    def __init__(self, app, name, thread_limit):
        self.app = app
        self.stat = Stat(name)
        self.name = name
        self.thread_limit = thread_limit

    def __call__(self, (sock, addr)):
        online = self.stat.online()
        if online >= self.thread_limit:
            logger.warning(
                '%s: Threads limit reached! (limit=%d online=%d)' % (
                    self.name,
                    self.thread_limit,
                    online
            ))
            close_socket(sock)
            return
        with self.stat():
            data = SCGIInputParser()
            while not data.is_complete:
                try:
                    d = sock.recv(4096)
                except socket.error, why:
                    en = why[0]
                    if en in DISCONNECTED:
                        logger.warning(self.name + ': DISCONNECTED')
                        break
                    if en == errno.EWOULDBLOCK:
                        logger.warning(self.name + ': EWOULDBLOCK. HOW?!')
                        break
                if len(d) == 0:
                    logger.warning(self.name + ': EMPTY. HOW?!')
                    break
                data.append(d)
            if data.is_complete:
                # PEP3333
                # WSGI application cat submit data by two ways:
                # (i) return an iterator, or (ii) call start_response.
                # We are support both of them, but in fixed order.
                start_response = StartResponse()
                data.wsgi_variables['wsgi.x_thread_stat'] = self.stat # add statistics
                replay = self.app(data.wsgi_variables, start_response)
                message = (
                    'Status: ' + start_response.status + '\n' +
                    '\n'.join(': '.join(x) for x in start_response.response_headers) +
                    '\n\n' +
                    start_response.data + ''.join(replay)
                )
                delivery_message(sock, message)
            else:
                logger.error('REQUEST NOT COMPLETE: ' + repr(data.raw))
            close_socket(sock)
