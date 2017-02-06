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


import ast
import ConfigParser
import datetime
import logging
import logging.config

import pygal
from pygal.style import DarkSolarizedStyle
from pygal import Config

import cheez_cave.service.readings_service as readings_service


class ChartService:

    COL_DATE = 0
    COL_RH = 1
    COL_TEMP = 2
    APP_SECTION = 'AppOptions'
    CHART_SECTION = 'ChartOptions'
    
    def __init__(self, config):
        self.logger = logging.getLogger('ChartService')
        self.config = config

        self.dao = readings_service.ReadingsService(self.config)

        # get chart config from config file
        chart_options = self.config._sections[ChartService.CHART_SECTION]

        # process chart config into pygal friendly Config
        chart_options.pop('__name__')
        for key in chart_options.keys():
            chart_options[key] = ast.literal_eval(chart_options[key])
        self.logger.debug('chart options: ' + str(chart_options))
        self.pygal_config = Config(**chart_options)

    def get_data(self, begin=None, end=None):
        # Retrieve data from provided range from database
        if end is None:
            end = datetime.datetime.now()
    
        if begin is None:
            begin = end - datetime.timedelta(days=1)
    
        self.logger.debug('selecting range from {} to {}'.format(begin, end))
    
        data = self.dao.select_range(begin, end)

        return data
    

    def render_chart(self, data):
        # get a new chart and populate with data
        # set config using self.config

        chart = pygal.Line(self.pygal_config)
    
        chart.x_labels = [row[ChartService.COL_DATE] for row in data]
        chart.add('Temp', [row[ChartService.COL_TEMP] for row in data])
        chart.add('rH', [row[ChartService.COL_RH] for row in data])

        return chart.render()
    
    def store(self, chart, filename):
        # store rendered chart (svg) to specified file.
        file = open(filename, 'w')
        try:
            with file:
                file.write(chart)
        except Error as e:
            self.logger.error(e)
    
    def generate_default_chart(self):
        # Generates the default chart (previous 24 hours) and
        # and writes to file specified by AppOptions.svg_fullpath
        # in cheez_cave.conf.
        data = self.get_data()
        chart = self.render_chart(data)

        self.store(chart, self.config.get(ChartService.APP_SECTION, 'svg_fullpath'))


if __name__ == '__main__':
    test = ChartService()
    test.default_chart()
