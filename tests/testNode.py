'''Tests for the Node'''
# System imports
import unittest

# 3rd Party imports
from btNode import Node
# local imports
# end file header
__author__      = 'Adrian Lubitz'
__copyright__   = 'Copyright (c)2017, Blackout Technologies'

class TestNode(unittest.TestCase):
    '''Tests for the Node'''

    def test_init(self):
        '''
        Test init of the Node
        The params make no sense - the test is only checking if the init of a Node is possible
        '''
        node = Node(token='token', axonURL='axon', debug='debug')

    def test_connect(self):
        '''
        Test the connect process of the Node
        '''
        pass # TODO: For this a pong / testing instance (which is always available) is needed
        # node = Node(token='token', axonURL='axon', debug='debug')
        # node.connect()

if __name__ == '__main__':
    unittest.main()
            