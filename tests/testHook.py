'''Tests for the Hook'''
# System imports
import unittest
import time

# 3rd Party imports
from btHook import Hook
# local imports
from reconnectUtils import ShakyInternet

# end file header
__author__      = 'Adrian Lubitz'
__copyright__   = 'Copyright (c)2017, Blackout Technologies'

class ExampleHook(Hook):
    '''
    Hook for testing
    '''
    def onConnected(self):
        self.disconnect() # disconnects after successfully connecting

class TestHook(unittest.TestCase):
    '''Tests for the Hook'''
    shakyInternet = ShakyInternet()

    def setUp(self):
        self.shakyInternet.start()

    def tearDown(self):
        self.shakyInternet.stop()
        time.sleep(2)

    def test_init(self):
        '''
        test to initialize a Hook
        '''
        print('TESTING THE HOOK')
        h = ExampleHook(packagePath='packageHook.json')
        # h.connect(reconnection=False)
        # TODO: nothing here until I have a hook for testing in dev5
        
if __name__ == "__main__":
    unittest.main()
