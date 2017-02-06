import logging
import logging.config

import RPi.GPIO as GPIO


class PowerRelay():

    def __init__(self, name, gpio_pin, default=GPIO.LOW):
        ''' Assigns given pin as output and ensures Normally Open (NO)
            side of relay is open by default.
    
            The NC side of the relay may be used by setting default
            to GPIO.HIGH.
        '''
        self.logger = logging.getLogger('PowerRelay')

        self.name = name
        self.gpio_pin = gpio_pin

        if(GPIO.getmode() is None):
                GPIO.setmode(GPIO.BCM)

        self.logger.debug('Setting {} power relay pin to: {}'.format(self.name, self.gpio_pin))

        GPIO.setup(self.gpio_pin, GPIO.OUT)

        self.logger.debug('Setting initial {} power relay mode to: {}'.format(self.name, default))

        GPIO.output(self.gpio_pin, default)

    def turn_on(self):
        self.logger.debug('Closing NO side')
        self.toggle()

    def turn_off(self):
        self.logger.debug('Opening NO side')
        self.toggle()

    def toggle(self):
        self.logger.debug('Current state: {}, setting to {}'
                    .format(GPIO.input(self.gpio_pin), not GPIO.input(self.gpio_pin)))

        GPIO.output(self.gpio_pin, not GPIO.input(self.gpio_pin))
