'''Tests for the Node'''
# System imports
import unittest
import time
from threading import Thread, Timer
import os
import inspect
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
        dockerDeactivatePath = os.path.join(os.path.dirname(os.path.realpath(os.path.abspath(inspect.getfile(self.__class__)))), 'dockerDeactivate.sh')
        # print('dockerDeactivatePath: {}'.format(dockerDeactivatePath))
        docker_proc_args = [dockerDeactivatePath]
        old_proc_args = ['nmcli', 'nm', 'enable', 'false']
        proc_args = ['nmcli', 'networking', 'off']

        p3 = subprocess.Popen(docker_proc_args) #This needs to be first otherwise it fails because of no internet
        if wait:
            p3.wait()
        p1 = subprocess.Popen(proc_args)
        if wait:
            p1.wait()
        p2 = subprocess.Popen(old_proc_args)
        if wait:
            p2.wait()

        # if wait:
        #     p1.wait()
        #     p2.wait()
        #     p3.wait()
        self.state = 0


    def connectInternet(self, wait=True):
        print('connecting to the Internet')
        dockerActivatePath = os.path.join(os.path.dirname(os.path.realpath(os.path.abspath(inspect.getfile(self.__class__)))), 'dockerActivate.sh')
        # print('dockerDeactivatePath: {}'.format(dockerActivatePath))
        docker_proc_args = [dockerActivatePath]
        old_proc_args = ['nmcli', 'nm', 'enable', 'true']
        proc_args = ['nmcli', 'networking', 'on']
        p3 = subprocess.Popen(docker_proc_args)
        p1 = subprocess.Popen(proc_args)
        p2 = subprocess.Popen(old_proc_args)

        p3 = subprocess.Popen(docker_proc_args) #This needs to be first otherwise it fails because of no internet
        if wait:
            p3.wait()
        p1 = subprocess.Popen(proc_args)
        if wait:
            p1.wait()
        p2 = subprocess.Popen(old_proc_args)
        if wait:
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
    time.sleep(10)
    print('trying to stop the Thread')
    s.stop()
