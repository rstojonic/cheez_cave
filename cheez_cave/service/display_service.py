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
import time
import datetime
import logging
import logging.config

import Adafruit_CharLCD as LCD


DISPLAY_SECTION = 'DisplayOptions'
LOGGER_NAME = 'DisplayService'

class DisplayService:
    def __init__(self, config):
        self.logger = logging.getLogger(LOGGER_NAME)
        self.config = config

        # Raspberry Pi pin configuration:
        self.lcd_rs = int(config.get(DISPLAY_SECTION, 'lcd_rs')) 
        self.lcd_en = int(config.get(DISPLAY_SECTION, 'lcd_en'))
        self.lcd_d4 = int(config.get(DISPLAY_SECTION, 'lcd_d4'))
        self.lcd_d5 = int(config.get(DISPLAY_SECTION, 'lcd_d5'))
        self.lcd_d6 = int(config.get(DISPLAY_SECTION, 'lcd_d6'))
        self.lcd_d7 = int(config.get(DISPLAY_SECTION, 'lcd_d7'))
        self.lcd_backlight = int(config.get(DISPLAY_SECTION, 'lcd_backlight'))

        # Alternatively specify a 20x4 LCD.
        self.lcd_columns = int(config.get(DISPLAY_SECTION, 'lcd_columns'))
        self.lcd_rows = int(config.get(DISPLAY_SECTION, 'lcd_rows'))
    
        # Initialize the LCD using the pins above.
        self.lcd = LCD.Adafruit_CharLCD(self.lcd_rs, self.lcd_en, self.lcd_d4, self.lcd_d5, 
                            self.lcd_d6, self.lcd_d7, self.lcd_columns, self.lcd_rows, 
                            self.lcd_backlight, initial_backlight=0.0)

        # create custom characters
        # custom character position zero seems to have some issues, use 1+
        # Degree symbol
        degree = [0xe, 0xa, 0xe, 0x0, 0x0, 0x0, 0x0, 0x0]
        self.lcd.create_char(1, degree)
        # rH on (rH +)
        rh_on = [0x18,0x15,0x17,0x05,0x00,0x04,0x0E,0x04]
        self.lcd.create_char(2, rh_on)
        # rH off (rH -)
        rh_off = [0x18,0x15,0x17,0x05,0x00,0x00,0x0E,0x00]
        self.lcd.create_char(3, rh_off)
        self.lcd.clear()

        self.temp = 0
        self.rh = 0
        self.time = str(datetime.datetime.now())[:19]
        self.message = self.config_message()
        self.lcd.set_backlight(1)

        # Set initial rh power indicator
        self.rh_ind = '\3'
    
    def show(self):
        ''' Displays current message string '''
        self.logger.debug('Setting display to ' + 
                             self.message.format(self.rh_ind,  self.temp, '\1', self.rh, self.time)
                         )
        self.lcd.set_cursor(0, 0)
        self.lcd.message(self.message.format(self.rh_ind, self.temp, '\1', self.rh, self.time))

    def set_temp(self, temp):
        self.temp = temp

    def set_rh(self, rh):
        self.rh = rh

    def update(self, rh, temp):
        ''' Update temperature and rh '''
        self.logger.debug('Setting internal temp: {} and rh: {}'.format(temp, rh))
        self.set_temp(temp)
        self.set_rh(rh)

    def update_time(self):
        ''' Causes this class to update the time and reflect the 
            change on the display.
        '''
        self.logger.debug('updating time')
        self.time = str(datetime.datetime.now())[:19]
        self.show()    

    def set_rh_indicator(self, on):
        if(on):
            self.rh_ind = '\2'
        else:
            self.rh_ind = '\3'

    def off(self):
        ''' clear the display and turn off the backlight '''
        self.logger.debug('turning off display')
        self.lcd.clear()
        self.lcd.set_backlight(0)

    def config_message(self):
        lines = []
        for i in range(1, 5):
            lines.append(self.config.get(DISPLAY_SECTION, 'line_' + str(i)))
        return '\n'.join(lines)
