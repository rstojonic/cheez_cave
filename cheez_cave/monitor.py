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

from apscheduler.schedulers.blocking import BlockingScheduler

from cheez_cave import chart_service
from cheez_cave import display_service
from cheez_cave import readings_service
from cheez_cave import sensor_service

class Monitor():
    def __init__(self):
        logging.config.fileConfig('/home/pi/cheez_cave/cheez_cave.conf')
        self.logger = logging.getLogger('Monitor')
        self.sensor = sensor_service.SensorService()
        self.dao = readings_service.ReadingsService()
        self.display = display_service.DisplayService()
        self.chart = chart_service.ChartService()
        
    def persist_reading(self):
        ''' Get the current sensor reading and persist in database '''
        humidity, temperature = self.sensor.read_f()
        result = self.dao.insert_reading(humidity, temperature)
        self.logger.debug('Reading insert attempt: temp : {}, rh : {}, result: {}'
                            .format(temperature, humidity, result)
                         )
        self.display.update(humidity, temperature)
        self.chart.default_chart()
        
    
    def tick(self):
        self.display.update_time()
    
    def main(self):

        # initialize the display with the current sensor reading
        humidity, temperature = self.sensor.read_f()
        self.display.update(humidity, temperature)
    
        # schedule the jobs
        sched = BlockingScheduler()
        sched.add_job(self.persist_reading, trigger='cron', minute='*/5')
        self.logger.info('Monitor persist_reading job added to schedule')
        sched.add_job(self.tick, trigger='cron', second='*')
        self.logger.info('Monitor tick job added to schedule')
        
        try:
            self.logger.info('Starting jobs')
            sched.start()
        finally:
            self.display.off()
    
if __name__ == '__main__':
    Monitor().main()    
