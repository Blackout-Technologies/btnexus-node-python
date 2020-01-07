'''Tests for the Node'''
# System imports
import unittest
import time
from threading import Thread
import os

# 3rd Party imports
from btNode import Node
# local imports
# end file header
__author__      = 'Adrian Lubitz'
__copyright__   = 'Copyright (c)2017, Blackout Technologies'


class TestNode(Node):
    def onConnected(self):
        self.disconnect() #connecting was successfull - disconnect


class NodeTests(unittest.TestCase):
    '''Tests for the Node''' 

    def test_connect(self):
        '''
        Test the connect process of the Node
        '''
        # read token from gitlab variables! and axonURL
        print('TESTING THE NODE')
        node = TestNode()
        node.connect(reconnection=False)
        assert not node.nexusConnector.isConnected, 'disconnect is not completed [isConnected]'
        assert not node.nexusConnector.isRegistered, 'disconnect is not completed [isRegistered]'

if __name__ == "__main__":
    unittest.main()        