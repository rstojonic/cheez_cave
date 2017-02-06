#!/usr/bin/python

# Copyright (c) 2017
# Author: Ray Stojonic
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import logging
import logging.config

from cheez_cave import readings_dao


class ReadingsService():

    def __init__(self, config):
        self.logger = logging.getLogger('ReadingsService')
        self.dao = readings_dao.ReadingsDAO()

    def select_range(self, begin, end):
        '''Return an array of readings bound by provided datetimes

        Keyword Arguments:
        begin: A datetime or string demarking the beginning of the desired range.
        end  : A datetime or string demarking the end of the desired range.
        '''

        self.logger.debug('selecting range: {} to {}'.format(begin, end))

        if not isinstance(begin, basestring):
            begin = str(begin)

        if not isinstance(end, basestring):
            end = str(end)

        data = self.dao.select_range(begin, end)

        result = []
        for row in data:
            result.append((row[0][:16], round(row[1], 1), round(row[2], 1)))

        self.logger.debug('Range contained {} items'.format(len(result)))

        return result

    def insert_reading(self, humidity, temperature):
        '''Insert a new reading.'''

        self.logger.debug('inserting new record: temp {}, rh: {}'.format(temperature, humidity))
        return self.dao.insert_reading(humidity, temperature)

