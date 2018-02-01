#!/usr/bin/python
import sys
import serial
import time


def run():
  '''
  Interval ( in seconds ) = n/10
  This number will always be rounded to the closest integer.
  '''
  interval = 1 
  
  try:
    user_interval = int(sys.argv[2])/10
    if 0 < user_interval < 360:
      interval = user_interval
  except Exception as e:
    # Interval seems invalid. Let's ignore it.
    pass
  print "Heartbeat configured for {} second(s) intervals".format((interval*10))
  while True:
    watchdog.write(chr(interval))
    watchdog.flush()
    time.sleep(1)

usage = '''{} <port> [ <heartbeat_interval> ]

                  port: Serial port to use ( e.g. /dev/cu.wchusbserial1420 )
    heartbeat_interval: maximum amount of time without a hearbeat ( e.g. 180 seconds. 10 second increments only )
'''.format(sys.argv[0])

def reset():
  watchdog.write(chr(255))
  watchdog.flush()
  time.sleep(1)

def checkInternet():
  import urllib2
  try:
    urllib2.urlopen('http://google.com', timeout=5)
    return True
  except urllib2.URLError as err: 
    return False

if len(sys.argv)> 1:
  watchdog = serial.Serial(sys.argv[1], 9600)
  time.sleep(1)
  run()
else:
  print usage


