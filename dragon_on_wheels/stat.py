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


import threading
import time
import logging
import os


import metrics
import dragon_on_wheels


logger = logging.getLogger(__name__)


__all__ = 'info',


def sec_to_str(d):
    s = ''
    for w, f in (
            (60, '%02ds'),
            (60, '%02dm '),
            (24, '%02dh '),
            (10000, '%dd ')
        ):
        if d == 0:
            break
        u = d % w
        s = (f % u) + s
        d -= u
        d /= w
    return s


class Monitor:

    def __init__(self, stat):
        self.stat = stat
        self.start = time.time()

    def __enter__(self):
        self.stat.enter()

    def __exit__(self, type, value, tb):
        self.stat.exit(time.time() - self.start)


class Stat:

    def __init__(self, name):
        self.metric = metrics.CumulativeMovingStandardDeviation()
        self.cnt_online = 0
        self.lock = threading.Lock()
        self.name = name
        with self.lock:
            GSTAT['threads'][name] = self # это навесегда!

    def enter(self):
        with self.lock:
            self.cnt_online += 1

    def exit(self, dt):
        logger.debug('%s: dt=%f' % (self.name, dt))
        with self.lock:
            self.metric.update(dt)
            self.cnt_online -= 1

    def __call__(self):
        return Monitor(self)

    def online(self):
        with self.lock:
            return self.cnt_online

    def info(self):
        with self.lock:
            return {
                'requests': self.metric.count,
                'online_time': self.metric.sum,
                'online_time_str': sec_to_str(self.metric.sum),
                'online_time_longest': self.metric.max,
                'online_time_shortest': self.metric.min,
                'online_time_average': self.metric.average,
                'online_time_stddev': self.metric.corrected_std_deviation,
                'online': self.cnt_online
            }


GSTAT = {
    'start_time': time.time(),
    'threads': {}
}


def info():
    st = GSTAT['start_time']
    uptime = int(time.time() - st)
    h = {
        'pid': os.getpid(),
        'start_time': st,
        'start_at_asctime': time.asctime(time.localtime(st)),
        'uptime': uptime,
        'uptime_str': sec_to_str(uptime),
    }
    rr = 0
    oo = 0
    for n, t in GSTAT['threads'].items():
        try:
            inf = t.info()
            rr += inf['requests']
            oo += inf['online']
            for p, q in inf.items():
                h[n + '_' + p] = q
        except metrics.NotEnoughData:
            h[n + '_error'] = 'Not enough data'
    h['requests'] = rr
    h['online'] = oo
    h['version'] = dragon_on_wheels.__version__
    return h
