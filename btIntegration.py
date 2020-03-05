'''A Node for Integrations - is basically the Node class'''
# System imports
# 3rd Party imports
# local imports
from btNode import Node
# end file header
__author__      = 'Adrian Lubitz'
__copyright__   = 'Copyright (c)2017, Blackout Technologies'

class Integration(Node):
    def onConnected(self):
        self.logger.log(self.NEXUSINFO, 'Integration {} is connected'.format(self.nodeName))

if __name__ == '__main__':
    i = Integration()
    i.connect()