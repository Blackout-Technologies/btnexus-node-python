'''Tests for the Node'''
# System imports
import unittest
import time
from threading import Thread, Timer
import os
import subprocess
from random import randint
# 3rd Party imports

# local imports
# end file header
__author__      = 'Adrian Lubitz'
__copyright__   = 'Copyright (c)2017, Blackout Technologies'

class ShakyInternet(object):
    def __init__(self, period=None):
        self.period = period
        # self.pastTime = 0
        self.startTime = None
        self.timer = None
        self.state = True # True: connected, False: disconnected

    def start(self):
        self.startTime = time.time()
        self.shakyInternet()


    def stop(self):
        self.timer.cancel()
        self.timer.join()
        self.connectInternet()


    def disconnectInternet(self, wait=True):
        print('disconnecting from the Internet')
        old_proc_args = ['nmcli', 'nm', 'enable', 'false']
        proc_args = ['nmcli', 'networking', 'off']
        p1 = subprocess.Popen(proc_args)
        p2 = subprocess.Popen(old_proc_args)
        if wait:
            p1.wait()
            p2.wait()
        self.state = 0


    def connectInternet(self, wait=True):
        print('connecting to the Internet')
        old_proc_args = ['nmcli', 'nm', 'enable', 'true']
        proc_args = ['nmcli', 'networking', 'on']
        p1 = subprocess.Popen(proc_args)
        p2 = subprocess.Popen(old_proc_args)
        if wait:
            p1.wait()
            p2.wait()
        self.state = 1

    def shakyInternet(self):
        """
        creates a shaky Internet connection for testing random reconnects.

        :param period: Approximate Period of seconds for how long the Internet connection should be shaky
        :type period: int
        """
        #Do the thing
        if self.state:
            self.disconnectInternet()
        else: 
            self.connectInternet()

        #if still time left start yourself again with max(left_time)
        if self.period:
            now = time.time()
            pastTime = now - self.startTime
            restTime = self.period - pastTime
            if pastTime < self.period:
                t = randint(min(5, int(restTime)), min(int(restTime), 60))
                self.timer = Timer(t, self.shakyInternet)
                self.timer.start()
        else:
            t = randint(5, 60)
            self.timer = Timer(t, self.shakyInternet)
            self.timer.start()

if __name__ == '__main__':
    s = ShakyInternet()
    s.start()
    print('living in a world with shaky internet')
    time.sleep(100)
    print('trying to stop the Thread')
    s.stop()
