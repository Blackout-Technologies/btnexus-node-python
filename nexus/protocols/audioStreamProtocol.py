'''The Protocol for the streaming of audio data'''
# System imports
import socket
# 3rd Party imports
from twisted.protocols.basic import LineReceiver 
from nexus.message import Message

# local imports
# end file header
__author__      = 'Adrian Lubitz'
__copyright__   = 'Copyright (c)2017, Blackout Technologies'

class AudioStreamProtocol(LineReceiver): 

    def connectionMade(self):
        LineReceiver.connectionMade(self)
        # print('connectionMade')
        self.intent = 'stream'
        message = Message(intent=self.intent)
        message['sessionId'] = self.factory.service.getSessionId()
        self.sendLine(message.getJsonContent().encode('utf-8'))


    def lineReceived(self, line):
        message = Message()
        message.loadFromJsonString(line)
        intent = message['api']['intent']
        if intent == self.intent + '_start':
            if message['success']:
                self.factory.service._startStreaming(self.transport)                
            else:
                self.factory.service.publishDebug('Closing connection because: {}'.format(message['error']))
        else:
            self.factory.service.publishDebug('Intent {} does not match the protocol. Expecting {}'.format(intent, self.intent + '_start'))
            self.transport.loseConnection()

    def connectionLost(self, reason):
        self.factory.service.publishDebug('Lost connection')
        
