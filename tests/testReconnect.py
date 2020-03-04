'''Tests for the Node'''
# System imports
import unittest
import time
from threading import Thread, Timer
import os
import subprocess

# 3rd Party imports
from btNode import Node
import timeout_decorator

# local imports
import _socket_toggle
# end file header
__author__      = 'Adrian Lubitz'
__copyright__   = 'Copyright (c)2017, Blackout Technologies'


class TestNode(Node):

    def __init__(self,**kwargs):
        super(TestNode, self).__init__(**kwargs)
        self.connects = 0
    def onConnected(self):
        self.connects += 1
        if self.connects > 3:
            self.disconnect()    



class NodeTests(unittest.TestCase):
    '''Tests for the reconnecting the Node''' 


    @timeout_decorator.timeout(600, use_signals=False)
    def test_reconnection(self):
        re = TestNode()
        re.connect(blocking=False)
        for x in range(3):
            time.sleep(40)
            disconnectInternet()
            time.sleep(40)
            connectInternet()


if __name__ == "__main__":
    unittest.main()        