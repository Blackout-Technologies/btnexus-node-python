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
        super().onConnected()
        self.disconnect()

class TestHook(unittest.TestCase):
    '''Tests for the Hook'''

    def test_init(self):
        '''
        test to initialize a Hook
        '''
        h = ExampleHook(reconnection=False)
        pass # TODO: disconnect

