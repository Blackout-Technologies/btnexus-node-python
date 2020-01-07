'''Tests for the Hook'''
# System imports
import unittest

# 3rd Party imports
from btHook import Hook
# local imports
# end file header
__author__      = 'Adrian Lubitz'
__copyright__   = 'Copyright (c)2017, Blackout Technologies'

class ExampleHook(Hook):
    '''
    Hook for testing
    '''
    def onConnected(self):
        super(ExampleHook, self).onConnected()
        self.disconnect() # disconnects after successfully connecting

class TestHook(unittest.TestCase):
    '''Tests for the Hook'''

    def test_init(self):
        '''
        test to initialize a Hook
        '''
        print('TESTING THE HOOK')
        h = ExampleHook(reconnection=False)
        
if __name__ == "__main__":
    unittest.main()
