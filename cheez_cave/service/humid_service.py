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


import time
import datetime
import logging
import logging.config
import ConfigParser

import cheez_cave.iface.power_relay as power_relay
import cheez_cave.service.display_service
import cheez_cave.service.data_service as data_service

class HumidService:

    APP_SECTION = 'AppOptions'
    OFF = False
    ON = True

    def __init__(self, config, display):
        self.logger = logging.getLogger('HumidService')
        self.config = config
        self.display = display
        self.dao = data_service.DataService(config)

        pin = int(self.config.get(HumidService.APP_SECTION, 'humidifier_pin'))
        self.humidifier = power_relay.PowerRelay('humidifier', pin)

        # The humidifier should not turn on and off rapidly.
        # Load the delay time from the config.
        # The delay represents the _minimum_ time the humidifier
        # will remain in its current state.
        delay_type = config.get(HumidService.APP_SECTION, 'humid_delay_type')
        delay_length = config.get(HumidService.APP_SECTION, 'humid_delay_length')
        self.delay = datetime.timedelta(**{delay_type: int(delay_length)})
        self.logger.info('Using {}={} as humidifier delay'.format(delay_type, delay_length))

        # rh_low is the set point to turn the humidifier on.
        self.rh_low = float(config.get(HumidService.APP_SECTION, 'rh_low'))
        self.logger.info('Using {} as humidity low setpoint.'.format(self.rh_low))

        # rh_high is the set point to turn the humidifier off.
        self.rh_high = float(config.get(HumidService.APP_SECTION, 'rh_high'))
        self.logger.info('Using {} as humidity high setpoint.'.format(self.rh_high))

        # The last time the humifier changed state
        self.toggle_time = datetime.datetime.fromtimestamp(time.time())

        # Keep track of the current state
        self.state = False
        self.turn_off()

        # Set toggle time back by delay amount to allow humidifier to initially 
        # turn on without waiting for the delay to elapse.
        self.toggle_time -= self.delay

    def update_humidifier(self, rh):
        ''' If enough time has passed since the last power state change,
            update_humidifier _may_ toggle the humidifier power.
            On: when state is OFF and rh is below rh_low setpoint.
            Off: when state is ON and rh is above rh_high setpoint.
        '''
        self.logger.debug('Update received: rh: {}%'.format(rh))
        if self.delay_check():
            if not self.state and float(rh) < float(self.rh_low):
                self.turn_on()
            if self.state and float(rh) > float(self.rh_high):
                self.turn_off()

        mode = 'OFF'
        if(self.state):
            mode = 'ON'

        self.dao.insert_humid_mode(mode)

    def turn_on(self):
        ''' Turn the humidifier power relay on. '''
        self.logger.info('Turning humidifier ON')
        self.toggle(self.humidifier.turn_on, True)
    
    def turn_off(self):
        ''' Turn the humidifier power relay off. '''
        self.logger.info('Turning humidifier OFF')
        self.toggle(self.humidifier.turn_off, False)
    
    def toggle(self, func, state):
        ''' Toggles the humidifier power relay and updates the 
            toggle time.

            Use turn_on and turn_off rather than invoking this directly.

            func: a lambda to perform 
        '''
        func()
        self.toggle_time = datetime.datetime.fromtimestamp(time.time())
        self.logger.debug('toggle operation complete, toggle_time: {}'.format(self.toggle_time))
        self.state = state
        self.display.set_rh_indicator(state)
      
    def delay_check(self):
        ''' Check to see if the last time the humidifier state
            changed was more than the configured delay ago.
        '''
        time_diff = datetime.datetime.fromtimestamp(time.time()) - self.toggle_time
        self.logger.debug('time_diff: {}, self.delay: {}, Result: {}'
                .format(time_diff, self.delay, time_diff > self.delay))
        return time_diff > self.delay
