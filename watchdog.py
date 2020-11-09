#!/usr/bin/python3
import logging
import sys
import time
import serial
import argparse
import threading
from datetime import timedelta


class UsbWatchDog(object):

    def __init__(self, port, heartbeat=10, baud=9600, daemon=True):
        self.heartbeat = heartbeat if 10 < heartbeat <= 360 else 10
        self.port = port
        self.watchdog = serial.Serial(self.port, baud)
        if daemon:
            run = threading.Thread(target=self.run)
            run.daemon = False
            run.start()
            
    def _read(self, byte):
        try:
            self._write(byte)
            a = self.read()
            print(a)
        except Exception as e:
            systemd.daemon.notify('STOPPING=1')
            raise Exception('Error while reading: {}'.format(e))

    def _write(self, byte):
        try:
            self.watchdog.write(bytes([byte]))
            self.watchdog.flush()
        except Exception as e:
            raise Exception('Error while writing: {}'.format(e))

    def get_info(self):
        ''' TODO: get current system info
        '''
        with open('/proc/uptime', 'r') as f:
            uptime = float(f.readline().split()[0])
            last_boot = str(timedelta(seconds = uptime))

        scheduled_restart = 0
        info = {
            'last_boot':last_boot,
            'scheduled_restart': 0,
            'timeout':self.heartbeat
        }
        return info
        
    def run(self):
        ''' Interval ( in seconds ) = n/10,
        This number will always be rounded to the closest integer.
        If daemon variable is set, run this as a thread in background
        '''
        try:
            interval = int(self.heartbeat/10)
        except Exception as e:
            logging.warn("Interval seems invalids. Error {}".format(e))

        logging.debug ("Heartbeat configured for {} second(s) intervals"
                       .format(interval*10))
        systemd.daemon.notify('READY=1')
        while True:
            logging.debug ("Heartbeat {}".format(interval*10))
            self._write(interval)
            time.sleep(5)

    def reset(self):
        ''' Restart Now
        '''
        logging.debug('Restart Now')
        try:
            self._write(255)
        except Exception as e:
            print('Error {}'.format(e))
            logging.warning('Error {}'.format(e))

    def change_timeout_seconds(self, timeout):
        ''' Change Heartbeat timeout
        '''
        logging.debug('Changing heart beat from {} to {}'
                      .format(self.heartbeat, timeout))
        try:
            self.heartbeat = int(timeout) if 10 < int(timeout) <= 360 else 10
        except ValueError as e:
            logging.warning('Invalid type, integer is required. Error {}'.format(e))
            raise TypeError

    def check_internet(self):
        ''' Test internet connection
        '''
        import urllib2
        try:
            urllib2.urlopen('http://google.com', timeout=5)
            return True
        except urllib2.URLError as e: 
            return False


if __name__ == '__main__':
    import systemd.daemon
    logging.basicConfig(level=logging.DEBUG)
    
    parser = argparse.ArgumentParser(
        description='Python Script to allow you to control a usb watchdog')
    parser.add_argument('port', type=str, 
                        help='Serial port to use (e.g /dev/cu.wchussetila420)')
    parser.add_argument('--hb', nargs='?', const=10, type=int, 
                        help='Maximum amount of time without a hearbeat '
                        '(e.g. 180 seconds). 10 second increments only. '
                        'Default: 10 seconds, Max: 360')
    args = parser.parse_args()
    hb = 10 if not args.hb else args.hb
    try:
        device = UsbWatchDog(args.port, hb, daemon=False)
        logging.debug('Device Information {}'.format(device.get_info()))
        device.run()

    except (KeyboardInterrupt, SystemExit):
        logging.warning("Keyboard interrupt")
        systemd.daemon.notify('STOPPING=1')
        sys.exit()

