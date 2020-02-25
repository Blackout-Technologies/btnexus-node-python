'''A Node which accepts audio streams and forwards them to the speech to text service of your choice and publishes the transcript on the transcript topic'''

# System imports
from threading import Thread
import time
import os
# 3rd Party imports
from btNode import Node
from twisted.internet import ssl
from btPostRequest import BTPostRequest

# local imports
from nexus.protocols.audioStreamFactory import AudioStreamFactory
# end file header
__author__      = 'Adrian Lubitz'
__copyright__   = 'Copyright (c)2017, Blackout Technologies'


class StreamingNode(Node):

    def __init__(self, **kwargs):
        super(StreamingNode, self).__init__(**kwargs) 
        # self.personalityId = personalityId
        # self.integrationId = integrationId
        # self.language = language
        # self.sessionId = sessionId
        # print('after STREAMINGINIT')

    def connect(self, **kwargs):
        from twisted.internet import reactor
        super(StreamingNode, self).connect(blocking=False, **kwargs)
        reactor.run()

    def _setUp(self):
        self.transport = None
        if 'language' in self.initKwargs:
            self.language = self.initKwargs['language']
        else:
            self.language = 'en-US'
        if 'personalityId' in self.initKwargs:
            self.personalityId = self.initKwargs['personalityId']
        else:
            self.personalityId = os.environ["PERSONALITYID"] 
        # self.msKey = os.environ["MSKEY"]
        if 'integrationId' in self.initKwargs:
            self.integrationId = self.initKwargs['integrationId']
        else:
            self.integrationId = os.environ['INTEGRATIONID'] #"f0458d18-3108-11e9-b210-d663bd873d93" - This is the robot integrationId - this needs to be set correctly using env
        params = {
            'integrationId': self.integrationId,
            'personalityId': self.personalityId
        }
        if 'sessionId' in self.initKwargs:
            self.sessionId = self.initKwargs['sessionId']
        else:
            try:
                print("reusing sessionId: {}".format(self.sessionId))
            except AttributeError:
                try:
                    print("URL: {}".format(self.axonURL))
                    BTPostRequest('sessionAccessRequest', params, accessToken=self.token, url=self.axonURL, callback=self.setSessionId).send(True) #This is called as a blocking call - if there is never a response coming this might be a problem...
                except Exception as e:
                    try:
                        self.publishError('Unable to get the sessionId: {}'.format(e))
                    except:
                        print('Unable to get the sessionId: {}'.format(e)) # if not connected just prints
                    time.sleep(2) # sleep
                    self._setUp()  # and retry
        super(StreamingNode, self)._setUp()

    def setSessionId(self, response):
        # print('response: {}'.format(response))
        if response['success']:
            self.sessionId = response['sessionToken']
            print('[{}]set sessionId to {}'.format(self.nodeName, self.sessionId))
        else:
            pass # TODO: what should I do here? - retry

    def _onDisconnected(self): 
        # kill the connection here
        if self.transport:
            self.transport.loseConnection()
            # self.transport.connectionLost(reason=None) - this is a callback not a function to call ^^
            print('Killing the Streaming')
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
        # TODO: also subscribe to persId.sessId, speechToText, streamTo
        self.subscribe(group='{}.{}'.format(self.personalityId, self.sessionId), topic='speechToText', callback=self.streamTo)
        self.publish(group=self.personalityId, topic='speechToText', funcName='initStream', params=[self.sessionId, self.language])
        super(StreamingNode, self)._onConnected()

    def streamTo(self, host, port):
        if not self.transport:
            self.host = host
            self.port = int(port)
            print('Want to connect to {}:{}'.format(host, port))
            factory = AudioStreamFactory(self)
            from twisted.internet import reactor
            reactor.callFromThread(reactor.connectSSL, self.host, self.port, factory, ssl.ClientContextFactory())
            print('Starting the AudioStreamer on {}:{}'.format(self.host, self.port))
        else:
            print('Im already connected  - just ignoring this.')

    def _startStreaming(self, transport):
        self.transport = transport
        Thread(target=self.onStreamReady).start()

    def onStreamReady(self):
        '''
        Stream as long as you want but use reactor.callFromThread and after finishing self.transport.loseConnection and self.transport = None
        '''
        pass

    def getSessionId(self):
        '''
        return the sessionId this needs to be implemented for a service node
        '''
        return self.sessionId

if __name__ == '__main__':
    asn = StreamingNode()
    asn.connect()
    