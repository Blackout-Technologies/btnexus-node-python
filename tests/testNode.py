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
        pass


class NodeTests(unittest.TestCase):
    '''Tests for the Node''' 

    def test_connect_rt_bf(self):
        '''
        Test the connect process of the Node
        '''
        # read token from gitlab variables! and axonURL
        print('TESTING THE NODE')
        node = TestNode()
        node.connect(reconnection=True, blocking=False)
        time.sleep(1)
        assert not node.nexusConnector.isConnected, 'disconnect is not completed [isConnected]'
        assert not node.nexusConnector.isRegistered, 'disconnect is not completed [isRegistered]'

    def test_connect_rt_bt(self):
        '''
        Test the connect process of the Node
        '''
        # read token from gitlab variables! and axonURL
        print('TESTING THE NODE')
        node = TestNode()
        node.connect(reconnection=True, blocking=True)
        time.sleep(1)
        assert not node.nexusConnector.isConnected, 'disconnect is not completed [isConnected]'
        assert not node.nexusConnector.isRegistered, 'disconnect is not completed [isRegistered]'

    def test_connect_rf_bf(self):
        '''
        Test the connect process of the Node
        '''
        # read token from gitlab variables! and axonURL
        print('TESTING THE NODE')
        node = TestNode()
        node.connect(reconnection=False, blocking=False)
        time.sleep(1)
        assert not node.nexusConnector.isConnected, 'disconnect is not completed [isConnected]'
        assert not node.nexusConnector.isRegistered, 'disconnect is not completed [isRegistered]'
    
    def test_connect_rf_bt(self):
        '''
        Test the connect process of the Node
        '''
        # read token from gitlab variables! and axonURL
        print('TESTING THE NODE')
        node = TestNode()
        node.connect(reconnection=False, blocking=True)
        time.sleep(1)
        assert not node.nexusConnector.isConnected, 'disconnect is not completed [isConnected]'
        assert not node.nexusConnector.isRegistered, 'disconnect is not completed [isRegistered]'

if __name__ == "__main__":
    unittest.main()        