'''Tests for the Node'''
# System imports
import unittest
import time
from threading import Thread, Timer
import os
import logging
import inspect



# 3rd Party imports
from btNode import Node
import timeout_decorator

# local imports
from reconnectUtils import ShakyInternet
# end file header
__author__      = 'Adrian Lubitz'
__copyright__   = 'Copyright (c)2017, Blackout Technologies'

moduleName = 'TESTS'
logger = logging.getLogger(moduleName)
logger.setLevel(Node.NEXUSINFO)
# create file handler which logs even debug messages
fh = logging.StreamHandler()
fh.setLevel(Node.NEXUSINFO)
formatter = logging.Formatter('%(asctime)s - [%(levelname)s]: %(message)s') 
fh.setFormatter(formatter)
logger.addHandler(fh)


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

class ReconnectingNode(Node):
    """
    This Nodes tests the reconnect() method
    """
    def __init__(self, **kwargs):
        super(ReconnectingNode, self).__init__(**kwargs)
        self.reconnects = 0
    def onConnected(self):
        """ reconnect 5 times and then disconnect """
        if self.reconnects < 5:
            self.reconnect()
            self.reconnects += 1
        else:
            self.disconnect()

class NodeTests(unittest.TestCase):
    '''Tests for the Node''' 
    shakyInternet = ShakyInternet()
    local_rc = os.path.join(os.path.dirname(os.path.realpath(os.path.abspath(__file__))), '.btnexusrc_integration')
    if os.path.isfile(local_rc):
        print("using local btnexusrc file")
        rc_path = local_rc
    elif "INTEGRATIONRC" in os.environ:
        print("using env var INTEGRATIONRC")
        rc_path = os.environ['INTEGRATIONRC']
    else:
        raise Exception("No valid btnexusrc")


    def setUp(self):
        self.shakyInternet.start()
        

    def tearDown(self):
        self.shakyInternet.stop()
        time.sleep(2)
    
    @timeout_decorator.timeout(120, use_signals=False)
    def test_connect(self):
        '''
        Test the connect process of the Node
        '''
        # read token from gitlab variables! and axonURL
        print('TESTING THE NODE')
        node = TestNode(packagePath='packageIntegration.json', rcPath=self.rc_path, logger=logger)
        node.connect()

    # Making a real message_exchange test out of Ping/Pong - it fails if after n seconds not all pongs are collected.
    @timeout_decorator.timeout(600, use_signals=False)
    def test_message_exchange(self):
        pong = Pong(packagePath='packageIntegration.json', rcPath=self.rc_path, logger=logger)
        pong.connect(blocking=False)
        for x in range(20):
            ping = Ping(packagePath='packageIntegration.json', rcPath=self.rc_path, logger=logger)
            ping.connect(blocking=not bool(x % 5)) # every 5th Node is blocking
            print('Ping/Pong {} done'.format(x))
        pong.disconnect()

    def test_reconnect(self):
        print('TESTING THE RECONNECTNODE')
        node = ReconnectingNode(packagePath='packageIntegration.json', rcPath=self.rc_path, logger=logger)
        node.connect()
    

if __name__ == "__main__":
    unittest.main()        