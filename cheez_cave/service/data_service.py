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

import cheez_cave.dao.readings_dao as readings_dao
import cheez_cave.dao.humidifier_dao as humidifier_dao


class DataService():

    def __init__(self, config):
        self.logger = logging.getLogger('DataService')
        self.readings_dao = readings_dao.ReadingsDAO(config)
        self.humid_dao = humidifier_dao.HumidifierDAO(config)

    def select_range(self, begin, end):
        '''Return arrays of readings and humidifier states within provided datetimes.

            Keyword Arguments:
            begin: A datetime or string demarking the beginning of the desired range.
            end: A datetime or string demarking the end of the desired range.
        '''

        self.logger.debug('selecting range: {} to {}'.format(begin, end))

        if not isinstance(begin, basestring):
            begin = str(begin)

        if not isinstance(end, basestring):
            end = str(end)

        readings_data = self.readings_dao.select_range(begin, end)

        readings_result = []
        for row in readings_data:
            readings_result.append((row[0][:16], round(row[1], 1), round(row[2], 1), round(row[3], 1)))

        self.logger.debug('Readings result contained {} items'.format(len(readings_result)))

        humid_data = self.humid_dao.select_range(begin, end)

        prev = None
        humid_result = []
        for row in humid_data:
            # Taking advantage of plotly's line 'gaps' for missing data.
            # I'm using a static number, to position the line on the chart
            # vertically (some place easy to see) and using 'None' for all OFF values
            # *after* the first OFF following one or more ONs.
            # This way, we get a graphical representation of when the humidifier
            # was on and off.
            mode = 85.0
            if(row[1] == 'OFF' and prev != 'ON'):
                mode = None
            humid_result.append((row[0][:16], mode))
            prev = row[1]

        self.logger.debug('Humidifier result contained {} items'.format(len(humid_result)))

        return readings_result, humid_result

    def insert_reading(self, humidity, temperature):
        '''Insert a new reading.'''

        self.logger.debug('inserting new temp and rh record: temp {}, rh: {}'.format(temperature, humidity))
        return self.readings_dao.insert_reading(humidity, temperature)

    def insert_humid_mode(self, mode):
        '''Insert a new humidifier mode record.'''

        self.logger.debug('inserting new humidifier record: mode: {}'.format(mode))
        return self.humid_dao.insert_humid_mode(mode)


