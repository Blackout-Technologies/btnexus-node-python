'''A Node which accepts audio streams and forwards them to the speech to text service of your choice and publishes the transcript on the transcript topic'''

# System imports
from threading import Thread, Timer
import time
import os
import warnings

# 3rd Party imports
from btNode import Node
from twisted.internet import ssl
from btPostRequest import BTPostRequest

# local imports
from nexus.protocols.audioStreamFactory import AudioStreamFactory
from nexus.nexusExceptions import NexusNotConnectedException
# end file header
__author__      = 'Adrian Lubitz'
__copyright__   = 'Copyright (c)2017, Blackout Technologies'


class StreamingNode(Node):

    def __init__(self, language=None, personalityId=None, sessionId=None, **kwargs):
        super(StreamingNode, self).__init__(**kwargs)
        self.sessionId = sessionId
        self.language = language
        if not self.language:
            if 'LANGUAGE' in os.environ:
                self.language = os.environ['LANGUAGE']
            else:
                self.language = self.package['language']
        self.personalityId = personalityId
        if not self.personalityId:
            if 'PERSONALITYID' in os.environ:
                self.personalityId = os.environ['PERSONALITYID']
            else:
                self.personalityId = self.package['personalityId']  

    def connect(self, **kwargs):
        """
        connect the Axon and start the reactor for twisted. 
        This will always block because of the reactor pattern
        """
        if 'blocking' in kwargs:
            warnings.warn("StreamingNodes cant be connected non-blocking. The call to connect will always blcok because of the reactor pattern.", Warning) #Apperently DeprecationWarnings are ignored for some reason
            del kwargs['blocking']
        from twisted.internet import reactor
        super(StreamingNode, self).connect(blocking=False, **kwargs)
        reactor.run()

    def _setUp(self):
        """
        Setting up
        """
        self.transport = None
        params = {
            'integrationId': self.config['id'],
            'personalityId': self.personalityId
        }
        if self.sessionId:
            self.logger.log(self.NEXUSINFO, "[{}]: reusing sessionId: {}".format(self.nodeName, self.sessionId))            
        else:
            try:
                BTPostRequest('sessionAccessRequest', params, accessToken=self.config['token'], url=self.config['host'], callback=self.setSessionId).send(True) #This is called as a blocking call - if there is never a response coming this might be a problem...
            except Exception as e:
                try:
                    self.publishError('Unable to get the sessionId: {}'.format(e))
                except NexusNotConnectedException:
                    # print('Unable to get the sessionId: {}'.format(e)) # if not connected just prints
                    pass
                time.sleep(2) # sleep
                self._setUp()  # and retry

        super(StreamingNode, self)._setUp()

    def setSessionId(self, response):
        """
        callback for the sessionAccessRequest
        """
        # print('response: {}'.format(response))
        if response['success']:
            self.sessionId = response['sessionToken']
            self.logger.log(self.NEXUSINFO, '[{}]set sessionId to {}'.format(self.nodeName, self.sessionId))            
        else:
            pass # TODO: what should I do here? - retry
            time.sleep(2)
            self._setUp()

    def _onDisconnected(self): 
        """
        Kill the twisted connection and if the diosconnect was initialized by myself stop the whole thing, because there will be no more reconnect.
        """
        # kill the connection here
        if self.transport:
            self.transport.loseConnection()
            # self.transport.connectionLost(reason=None) - this is a callback not a function to call - apperently some say it should be called
            self.logger.log(self.NEXUSINFO, '[{}] Killing the Streaming'.format(self.nodeName))            
        if self.disconnecting: # Disconnect was initialized by myself
            from twisted.internet import reactor
            reactor.stop()

        super(StreamingNode, self)._onDisconnected()

    def _onConnected(self): 
        """
        This will be executed after a the Node is succesfully connected to the btNexus
        Here you need to subscribe and set everything else up.

        :returns: None
        """
        # start the streaming in a thread
        # start a sending client here
        # self.subscribe(group=self.personalityId, topic='speechToText', callback=self.initStream_response)
        self.ready = False  # ready when the handshake is done
        self.subscribe(group='{}.{}'.format(self.personalityId, self.sessionId), topic='speechToText', callback=self.streamTo)
        self.handshake()
        super(StreamingNode, self)._onConnected()

    def streamTo(self, host, port):
        """
        This reacts to the message from the Service telling where to connect to with twisted.
        """
        self.ready = True
        if not self.transport:
            self.host = host
            self.port = int(port)
            self.logger.log(self.NEXUSINFO, "[{}]: Want to connect to {}:{}".format(self.nodeName, host, port))
            factory = AudioStreamFactory(self)
            from twisted.internet import reactor
            reactor.callFromThread(reactor.connectSSL, self.host, self.port, factory, ssl.ClientContextFactory())
            self.logger.log(self.NEXUSINFO, "[{}]: Starting the AudioStreamer on {}:{}".format(self.nodeName, self.host, self.port))
        else:
            self.logger.log(self.NEXUSINFO,'[{}] Im already connected  - just ignoring this.'.format(self.nodeName))

    def _startStreaming(self, transport):
        self.transport = transport
        Thread(target=self.onStreamReady).start()

    def onStreamReady(self):
        '''
        Start your stream with self.stream(stream) - this will stream data from the given stream to the SpeechService.
        '''
        pass

    def getSessionId(self):
        '''
        return the sessionId this needs to be implemented for a service node
        '''
        return self.sessionId

    def stream(self, stream):
        """
        This takes a stream and streams it to the Service
        """
        # TODO: maybe put this in a Thread...Then it is not blocking
        from twisted.internet import reactor
        byte = stream.read(64)
        while byte:
            reactor.callFromThread(self.transport.write, byte)
            byte = stream.read(64)

    def handshake(self):
        """
        Do the Handshake with the Service and retry until it works.
        """
        if not self.ready:
            Timer(3, self.handshake).start()
            self.logger.log(self.NEXUSINFO, "[{}]: Handshake not performed yet - retry".format(self.nodeName))            
            try:
                self.publish(group=self.personalityId, topic='speechToText', funcName='initStream', params=[self.sessionId, self.language])
            except Exception as e:
                self.logger.error(str(e))

if __name__ == '__main__':
    asn = StreamingNode(packagePath='./tests/packageIntegration.json', rcPath='../streaming-axon/speechIntegration/.btnexusrc')
    asn.connect()
    