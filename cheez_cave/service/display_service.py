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

import Adafruit_CharLCD as LCD


class DisplayService:
    def __init__(self):
#        logging.config.fileConfig('../../cheez_cave.conf')
        self.logger = logging.getLogger('DisplayService')

        # Raspberry Pi pin configuration:
        self.lcd_rs        = 27 
        self.lcd_en        = 22
        self.lcd_d4        = 25
        self.lcd_d5        = 24
        self.lcd_d6        = 23
        self.lcd_d7        = 18
        self.lcd_backlight = 4

        # Alternatively specify a 20x4 LCD.
        self.lcd_columns = 20
        self.lcd_rows    = 4
    
        # Initialize the LCD using the pins above.
        self.lcd = LCD.Adafruit_CharLCD(self.lcd_rs, self.lcd_en, self.lcd_d4, self.lcd_d5, 
                            self.lcd_d6, self.lcd_d7, self.lcd_columns, self.lcd_rows, 
                            self.lcd_backlight, initial_backlight=0.0)

        # create custom degree character in position 0
        degree = [0xe, 0xa, 0xe, 0x0, 0x0, 0x0, 0x0, 0x0]
        self.lcd.create_char(0, degree)
        self.lcd.clear()

        self.temp = 0
        self.rh = 0
        self.time = str(datetime.datetime.now())[:19]
        self.message = 'Cheese Cave\nCurrent Temp: {}\0F  \nCurrent rH: {}%   \n{}'
        self.lcd.set_backlight(1)
    
    def show(self):
        ''' Displays current message string '''
        self.logger.debug('Setting display to ' + 
                             self.message.format(self.temp, self.rh, self.time)
                         )
        self.lcd.set_cursor(0, 0)
        self.lcd.message(self.message.format(self.temp, self.rh, self.time))

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

    def off(self):
        ''' clear the display and turn off the backlight '''
        self.logger.debug('turning off display')
        self.lcd.clear()
        self.lcd.set_backlight(0)

