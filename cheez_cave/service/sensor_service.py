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

# Adapted from Adafruit_Python_DHT


import ConfigParser

import Adafruit_DHT


class SensorService():

    APP_SECTION = 'AppOptions'

    def __init__(self, config):
        self.sensor = Adafruit_DHT.AM2302
      
        self.config = config
  
        self.pin = self.config.get(SensorService.APP_SECTION, 'sensor_pin')

        # number of decimal digits in response
        self.ndigits = 1
        
    # Try to grab a sensor reading.  Use the read_retry method which will 
    # retry up to 15 times to get a sensor reading (waiting 2 seconds 
    # between each retry).
    def read(self):
        return Adafruit_DHT.read_retry(self.sensor, self.pin)
    
    # Read the sensor and return rounded output.
    def read_rounded(self):
        humidity, temperature = Adafruit_DHT.read_retry(self.sensor, self.pin)
        return round(humidity, self.ndigits), round(temperature, self.ndigits)

    # Return humidity and temperature in Celcius.
    def read_c(self):
        return self.read_rounded()

    # Return humidity and temperature in Fahrenheit.
    def read_f(self):
        humidity, temperature = self.read_rounded()
        return humidity, round(temperature * 1.8 + 32, self.ndigits)

    # Set the number of decimal digits in the reply.
    # Defaults to 1.
    def set_ndigits(self, ndigits):
        self.ndigits = ndigits

    def get_ndigits(self):
        return self.ndigits


