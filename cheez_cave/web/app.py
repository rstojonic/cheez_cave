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

import ConfigParser
import datetime
import json
import logging
import logging.config
import sys
from urllib2 import urlopen

from flask import Flask, render_template, redirect
from flask.views import View

reload(sys)
sys.setdefaultencoding("utf-8")

app = Flask(__name__)
logger = logging.getLogger('CheezCaveWebApp')

# get file name from config
config = ConfigParser.ConfigParser()
config.read('/home/pi/cheez_cave/cheez_cave.conf')
SVG_FILENAME = config.get('AppOptions', 'svg_filename')

@app.after_request
def add_header(response):
    response.cache_control.max_age = 0
    return response

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/cave')
def get_cave_data(begin=None, end=None):
    ''' Return chart with readings from requested range.
        Defaults to last 24 hours.
    '''
    global logger
    global SVG_FILENAME
    filename = SVG_FILENAME

    # TODO handle custom  date ranges
#    if end is None:
#        end = datetime.datetime.now()

#    if begin is None:
#        begin = end - datetime.timedelta(days=1)
    
#    logger.debug('selecting readings range from {} to {}'.format(begin, end))

    return render_template('monitor.html', 
                           title=config.get('AppOptions', 'title'),
                           svg_file=filename, 
                           date=str(datetime.datetime.now())
    )

def main():
    # Threaded or not threaded? It's up to you.
    app.run(debug=True, host='0.0.0.0', threaded=True)
    # app.run(debug=True, host='0.0.0.0')


if __name__ == '__main__':
    main()

