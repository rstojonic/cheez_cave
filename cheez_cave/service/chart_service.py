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
import time

import pygal
from pygal.style import DarkSolarizedStyle
from pygal import Config

import cheez_cave.service.data_service as data_service

import sys
reload(sys)
sys.setdefaultencoding('utf8')

class ChartService:

    COL_DATE = 0
    COL_RH = 1
    COL_TEMP = 2
    COL_RH_AVG = 3
    COL_MODE = 1
    APP_SECTION = 'AppOptions'
    CHART_SECTION = 'ChartOptions'
    
    def __init__(self, config):
        self.logger = logging.getLogger('ChartService')
        self.config = config

        self.dao = data_service.DataService(self.config)

        # get chart config from config file
        chart_options = self.config._sections[ChartService.CHART_SECTION]

        # process chart config into pygal friendly Config.
        # The title is a string value and must be quoted for ast
        # to properly process it. I tried to do this in the conf file
        # but a quoted string there won't have refs (ie:%(var)s) replaced.
        # Pop it out now, and add it back after ast has had its way, using
        # the config to run the replacement.
        title = self.config.get(ChartService.CHART_SECTION, 'title')
        chart_options.pop('title')

        # __name__ will be a string, but it's not needed here, so
        # just pop it out.
        chart_options.pop('__name__')

        for key in chart_options.keys():
            chart_options[key] = ast.literal_eval(chart_options[key])
        chart_options['title'] = title

        self.logger.debug('chart options: ' + str(chart_options))

        self.pygal_config = Config(**chart_options)

    def get_data(self, begin=None, end=None):
        # Retrieve data from provided range from database.
        if end is None:
            end = datetime.datetime.now()
    
        if begin is None:
            begin = end - datetime.timedelta(days=1)
    
        self.logger.debug('selecting range from {} to {}'.format(begin, end))
    
        temp_rh, humid = self.dao.select_range(begin, end)

        return temp_rh, humid
    

    def render_chart(self, temp_rh, humid):
        # get a new chart and populate with data
        # set config using self.config

        chart = pygal.Line(self.pygal_config)
    
        chart.x_labels = [row[ChartService.COL_DATE] for row in temp_rh]
        chart.add('Temp', [row[ChartService.COL_TEMP] for row in temp_rh])
        chart.add('rH', [row[ChartService.COL_RH] for row in temp_rh])
        chart.add('rH avg', [row[ChartService.COL_RH_AVG] for row in temp_rh])

        return chart.render()
    
    def store(self, rendered_chart, fullpath):
        # store rendered chart (svg) to specified file.
        file = open(fullpath, 'w')

        self.logger.debug('Writing rendered chart to: {}'.format(fullpath))

        try:
            with file:
                file.write(rendered_chart)
        except IOError as e:
            self.logger.error(e)
    
    def generate_default_chart(self):
        # Generates the default chart (previous 24 hours) and
        # and writes to file specified by AppOptions.svg_fullpath
        # in cheez_cave.conf.
        # temp_rh, humid = self.get_data()
        # chart = self.render_chart(temp_rh, humid)

        # self.store(chart, self.config.get(ChartService.APP_SECTION, 'svg_fullpath'))
        self.generate_xy_chart(self.config.get(ChartService.APP_SECTION, 'svg_filename'))

    def generate_chart(self, filename):
        # Generates a one off chart (previous 24 hours) and
        # and writes to file specified.
        temp_rh, humid = self.get_data()
        chart = self.render_chart(temp_rh, humid)
        fullpath = self.config.get(ChartService.APP_SECTION, 'svg_path') + filename
        self.store(chart, fullpath)

    def generate_xy_chart(self, filename):
        temp_rh, humid = self.get_data()

        chart = pygal.DateTimeLine(
            x_label_rotation = -75,
            range = (40,100),
            stroke_style = {'width':8},            
            x_value_formatter=lambda dt: dt.strftime('%Y-%m-%d %H:%M')
        )
        chart.title = 'Cheez Cave v0.3'
        
        # format with degree symbol ('\xB0') and F
        degree = u'\xB0'
        chart.add(
            'Temp', 
            self.get_date_time_line_data(temp_rh, 
                                    ChartService.COL_DATE, 
                                    ChartService.COL_TEMP), 
            formatter=lambda x: "{}: {}{}F".format(
                time.strftime('%Y-%m-%d %H:%M', time.gmtime(x[0])), x[1], degree)
        )

        chart.add(
            'rH', 
            self.get_date_time_line_data(temp_rh, 
                                    ChartService.COL_DATE, 
                                    ChartService.COL_RH), 
            formatter=lambda x: '{}: {}%'.format(
                time.strftime('%Y-%m-%d %H:%M', time.gmtime(x[0])), x[1])
        )

        chart.add(
            'rH Avg', 
            self.get_date_time_line_data(temp_rh, 
                                    ChartService.COL_DATE, 
                                    ChartService.COL_RH_AVG), 
            formatter=lambda x: '{}: {}%'.format(
                time.strftime('%Y-%m-%d %H:%M', time.gmtime(x[0])), x[1])
        )

        chart.add(
            'Hum On', 
            self.get_date_time_line_data(humid, 
                                    ChartService.COL_DATE, 
                                    ChartService.COL_MODE), 
            allow_interruptions=True
        )

        fullpath = self.config.get(ChartService.APP_SECTION, 'svg_path') + filename
        self.store(chart.render(), fullpath)

    def get_date_time_line_data(self, data, col_x, col_y):
        return [(
            datetime.datetime.strptime(row[col_x], '%Y-%m-%d %H:%M'),
            row[col_y]
        ) for row in data]

    
if __name__ == '__main__':
    test = ChartService()
    test.default_chart()
