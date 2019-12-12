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
    pass

class TestHook(unittest.TestCase):
    '''Tests for the Hook'''

    def test_init(self):
        '''
        test to initialize a Hook
        '''
        # h = ExampleHook()
        pass # TODO: For this a pong / testing instance (which is always available) is needed + .btnexusrc

