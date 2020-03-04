'''Tests for the Node'''
# System imports
import unittest
import time
from threading import Thread, Timer
import os

# 3rd Party imports
from btNode import Node
import timeout_decorator

# local imports
from reconnectUtils import ShakyInternet
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
        # print('send ping')
        try:
            self.publish(group='test', topic='test', funcName='ping', params={})
        except Exception as e: # Can happen, that one message is still beeing send although already disconnected
            print(e)
        if self.pongs < 10:
            Timer(0.1, self.sendPing).start()
        # 10 pings will be send in approx 1 second

    def pong(self):
        self.pongs += 1
        # print('Pongs: {}'.format(self.pongs))
        if self.pongs >= 10:
            self.disconnect()

class Pong(Node):
    """
    Answers with Pong on Ping
    """
    def onConnected(self):
        self.subscribe(group='test', topic='test', callback=self.ping)

    def ping(self):
        # print('sending pong')
        self.publish(group='test', topic='test', funcName='pong', params={})


class NodeTests(unittest.TestCase):
    '''Tests for the Node''' 
    shakyInternet = ShakyInternet()

    def setUp(self):
        self.shakyInternet.start()

    def tearDown(self):
        self.shakyInternet.stop()

    def test_connect(self):
        '''
        Test the connect process of the Node
        '''
        # read token from gitlab variables! and axonURL
        print('TESTING THE NODE')
        node = TestNode()
        node.connect()

    # def test_connect_rt_bt(self):
    #     '''
    #     Test the connect process of the Node
    #     '''
    #     # read token from gitlab variables! and axonURL
    #     print('TESTING THE NODE')
    #     node = TestNode()
    #     node.connect(reconnection=True, blocking=True)
    #     time.sleep(1)
    #     assert not node.nexusConnector.isConnected, 'disconnect is not completed [isConnected]'
    #     assert not node.nexusConnector.isRegistered, 'disconnect is not completed [isRegistered]'

    # def test_connect_rf_bf(self):
    #     '''
    #     Test the connect process of the Node
    #     '''
    #     # read token from gitlab variables! and axonURL
    #     print('TESTING THE NODE')
    #     node = TestNode()
    #     node.connect(reconnection=False, blocking=False)
    #     time.sleep(1)
    #     assert not node.nexusConnector.isConnected, 'disconnect is not completed [isConnected]'
    #     assert not node.nexusConnector.isRegistered, 'disconnect is not completed [isRegistered]'
    
    # def test_connect_rf_bt(self):
    #     '''
    #     Test the connect process of the Node
    #     '''
    #     # read token from gitlab variables! and axonURL
    #     print('TESTING THE NODE')
    #     node = TestNode()
    #     node.connect(reconnection=False, blocking=True)
    #     time.sleep(1)
    #     assert not node.nexusConnector.isConnected, 'disconnect is not completed [isConnected]'
    #     assert not node.nexusConnector.isRegistered, 'disconnect is not completed [isRegistered]'

    # Making a real message_exchange test out of Ping/Pong - it fails if after n seconds not all pongs are collected.
    @timeout_decorator.timeout(600, use_signals=False)
    def test_message_exchange(self):
        pong = Pong()
        pong.connect(blocking=False)
        for x in range(20):
            ping = Ping()
            ping.connect(blocking=not bool(x % 5)) # every 5th Node is blocking
            print('Ping/Pong {} done'.format(x))
        pong.disconnect()

    # @timeout_decorator.timeout(200, use_signals=False)
    # def test_message_exchange_with_reconnection(self):
    #     reconnectUtils.shakyInternet(120)
    #     pong = Pong()
    #     pong.connect(blocking=False)
    #     for x in range(60):
    #         ping = Ping()
    #         ping.connect(blocking=True)#not bool(x % 5)) # every 5th Node is blocking
    #         print('Ping/Pong {} done'.format(x))
    #     pong.disconnect()
    

if __name__ == "__main__":
    unittest.main()        