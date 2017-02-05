#!/usr/bin/python

import time
import datetime


out = open('ts_convert.sql', 'w')
f = open('dump.sql', 'r')

change = 5
delta = datetime.timedelta(minutes=change)

with out:
    for line in f:
        s = line.split(',')
        t = datetime.datetime.fromtimestamp(float(s[1]))
        if int(s[0].split('(')[1]) > 535:
            t = t + delta
            change += 5
            delta = datetime.timedelta(minutes=change)
            
        s[1] = "'" + str(t) + "'"
        out.write(','.join(s))
    
