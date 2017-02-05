## Synopsis

Cheez_cave is a temperature and humidity monitor intended for use on a Raspberry Pi.

## Motivation

I recently got into making cheese and thought "I could probably make better cheese if I knew what was going 
on inside my cheese cave and could automate the control of the environment in there".

## Requirements

    - A Raspberry Pi. I'm using a B, but any model should work with a little effort.
    - A DHT22 temperature and humidity sensor. (I went with the AM2302 from adafruit, which is a DHT22, but wired and in a nice enclosure.)
    - A 20 X 4 or 16 X 2 LCD, if onboard display is wanted.
    - *Optional for upcoming feature: A 120V power relay to control power to the humidifier. (Something like the Adafruit Power Relay FeatherWing.)
    - Potentially to be added at a future date: temperature control. This would require another power relay controlled outlet.
    - At this point, time and patience. This project is pre-alpha and my first python based project beyond simple scripts.
    
## Installation

At some point, I imagine the setup.py will do this after cheez_cave has been downloaded, but right now all it 
does is install the project code in the local python code library. As it is today, cheez_cave uses: 
Adafruit_Python_LCD, Adafruit_Python_DHT, flask, sqlite, pygal, apscheduler and supervisor to kick it all 
off.

## Contributors

<a href='https://github.com/rstojonic'>Ray Stojonic</a>

## License

MIT
