'''Factory for the audioStreamProtocol'''
# System imports
# 3rd Party imports
from twisted.internet.protocol import ClientFactory
from nexus.message import Message

# local imports
from .audioStreamProtocol import AudioStreamProtocol
# end file header
__author__      = 'Adrian Lubitz'
__copyright__   = 'Copyright (c)2017, Blackout Technologies'


class AudioStreamFactory(ClientFactory):
    protocol = AudioStreamProtocol

    def __init__(self, service):
        self.service = service
    

if __name__ == '__main__':
    class Test():
        def getSessionId(self):
            return 'FakeSessionId'
    test = Test()
    factory = AudioStreamFactory(test)
    from twisted.internet import reactor
    server = reactor.connectTCP('localhost', 12345, factory)
    print('Starting the TestClient on {}'.format(server.getDestination()))
    reactor.run()