'''Tests for the Node'''
# System imports
import unittest
import time
from threading import Thread, Timer
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

class Ping(Node):
    """
    Pings and waits until it get 10 pongs back
    """
    def onConnected(self):
        self.pongs = 0
        self.subscribe(group='test', topic='test', callback=self.pong)
        self.sendPing()

    def sendPing(self):
        print('send ping')
        try:
            self.publish(group='test', topic='test', funcName='ping', params={})
        except Exception as e: # Can happen, that one message is still beeing send although already disconnected
            print(e)
        if self.pongs < 10:
            Timer(0.2, self.sendPing).start()

    def pong(self):
        self.pongs += 1
        print('Pongs: {}'.format(self.pongs))
        if self.pongs >= 10:
            self.disconnect()

class Pong(Node):
    """
    Answers with Pong on Ping
    """
    def onConnected(self):
        self.subscribe(group='test', topic='test', callback=self.ping)

    def ping(self):
        print('sending pong')
        self.publish(group='test', topic='test', funcName='pong', params={})


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

    # TODO: Make a real message_exchange test out of this Ping/Pong - it needs to fail if after n seconds not all pongs are collected.
    # def test_message_exchange(self):
    #     pong = Pong()
    #     pong.connect(blocking=False)
    #     for x in range(55):
    #         ping = Ping()
    #         ping.connect()
    #     pong.disconnect()

if __name__ == "__main__":
    unittest.main()        