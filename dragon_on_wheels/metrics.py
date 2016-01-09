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


import math


class NotEnoughData(ValueError): pass


class Average:

    def __init__(self):
        self._min = None
        self._max = None
        self._sum = 0
        self._count = 0

    def update(self, v):
        if self._count == 0:
            self._min = v
            self._max = v
        self._count += 1
        self._sum += v
        self._min = min(self._min, v)
        self._max = max(self._max, v)

    @property
    def average(self):
        if self._count == 0:
            raise NotEnoughData('No data')
        return float(self._sum) / self._count

    @property
    def sum(self):
        return self._sum

    @property
    def count(self):
        return self._count

    @property
    def min(self):
        return self._min

    @property
    def max(self):
        return self._max


class CumulativeMovingStandardDeviation:

    '''
    X — set of data
    E[X] = μ — average or expected value
    σ² = E[(X-μ)²] = E[X²]-2μE[X]+μ² = E[X²]-μ²
    Uncorrected sample standard deviation = √(σ²)
    Corrected sample standard deviation = √((N/(N-1))σ²) = √(N/(N-1) √(σ²)
    '''

    def __init__(self):
        self.a = Average()
        self.a2 = Average() # mean of squares

    def update(self, v):
        self.a.update(v)
        self.a2.update(v * v)

    @property
    def average(self):
        return self.a.average

    @property
    def sum(self):
        return self.a._sum

    @property
    def count(self):
        return self.a.count

    @property
    def min(self):
        return self.a.min

    @property
    def max(self):
        return self.a.max

    @property
    def std_deviation_square(self):
        m = self.average
        return self.a2.average - m * m

    @property
    def std_deviation(self):
        return math.sqrt(self.std_deviation_square)

    @property
    def corrected_std_deviation(self):
        n = self.count
        if n < 2:
            raise NotEnoughData('Not enough data')
        return self.std_deviation * math.sqrt(float(n)/(n - 1))


def test():
    a = CumulativeMovingStandardDeviation()
    for x in range(0, 5):
        a.update(x)
    for x in range(4, -1, -1):
        a.update(x)
    print a.average # 2.0
    print a.std_deviation # 1.41421356237 (√2)
    print a.corrected_std_deviation # 1.490711985 (√(20/9))
    print a.min
    print a.max
    print a.count
    print a.sum


if __name__ == '__main__':
    test()
