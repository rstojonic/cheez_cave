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
import logging
import logging.config

from apscheduler.schedulers.blocking import BlockingScheduler

import cheez_cave.service.chart_service as chart_service
import cheez_cave.service.display_service as display_service
import cheez_cave.service.humid_service as humid_service
import cheez_cave.service.data_service as data_service
import cheez_cave.service.sensor_service as sensor_service


class Monitor():
    def __init__(self):
        self.config = ConfigParser.ConfigParser()
        config_file = '/home/pi/cheez_cave/cheez_cave.conf'
        self.config.read(config_file)

        logging.config.fileConfig(self.config.get('AppOptions', 'logging_conf'))
        self.logger = logging.getLogger('Monitor')
        
        self.chart = chart_service.ChartService(self.config)
        self.display = display_service.DisplayService(self.config)
        self.humidifier = humid_service.HumidService(self.config, self.display)
        self.dao = data_service.DataService(self.config)
        self.sensor = sensor_service.SensorService(self.config)
        
    def persist_reading(self):
        ''' Get the current sensor reading and persist in database. '''
        humidity, temperature = self.read_sensor()
        result = self.dao.insert_reading(humidity, temperature)
        self.logger.debug('Reading insert attempt: temp : {}, rh : {}, result: {}'
                            .format(temperature, humidity, result)
                         )
        self.display.update(humidity, temperature)
        self.chart.generate_default_chart()

    def update_humidifier(self):
        ''' Get the current humidity and update humidifier control. '''
        humidity = self.read_sensor()[0]
        self.logger.debug('Updating humidifer, current rh: {}%'.format(humidity))
        self.humidifier.update_humidifier(humidity)

    def read_sensor(self):
        return self.sensor.read_f()
    
    def tick(self):
        self.display.update_time()
    
    def main(self):

        # Initialize the display with the current sensor reading.
        humidity, temperature = self.read_sensor()
        self.display.update(humidity, temperature)
    
        # Schedule the jobs.
        sched = BlockingScheduler()

        # Schedule persist_reading for every 5 minutes.
        sched.add_job(self.persist_reading, trigger='cron', minute='*/5')
        self.logger.info('Monitor persist_reading job added to schedule')

        # Schedule humidifier for every minute, at 30 seconds.
        # Initially had at every minute, 0 seconds, but the extra load
        # caused the tick job to miss its scheduled time, resulting in a 
        # blank display.
        sched.add_job(self.update_humidifier, trigger='cron', minute='*/1', second=30)
        self.logger.info('Monitor update_humidifier job added to schedule')

        # Schedule tick for every second.
        sched.add_job(self.tick, trigger='cron', second='*')
        self.logger.info('Monitor tick job added to schedule')
        
        try:
            self.logger.info('Starting jobs')
            sched.start()
        finally:
            self.display.off()
    
if __name__ == '__main__':
    Monitor().main()    
