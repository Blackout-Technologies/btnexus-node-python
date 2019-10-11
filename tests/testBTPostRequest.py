'''Tests for the BTPostRequest'''
# System imports
import unittest

# 3rd Party imports
from btPostRequest import BTPostRequest
# local imports
# end file header
__author__      = 'Adrian Lubitz'
__copyright__   = 'Copyright (c)2017, Blackout Technologies'

class TestBTPostRequest(unittest.TestCase):
    '''Tests for the BTPostRequest'''

    def test_init(self):
        '''
        test to initialize a Hook
        '''
        r = BTPostRequest(intent='intent', params={}, accessToken='token', url='url')
    def test_send(self):
        '''
        test to initialize a Hook
        '''
        r = BTPostRequest(intent='intent', params={}, accessToken='token', url='url')
        # r.send() # TODO: For this a pong / testing instance (which is always available) is needed
        # can only return if the callback was executed

if __name__ == '__main__':
    unittest.main()