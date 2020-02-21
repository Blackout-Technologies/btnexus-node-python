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

    def __init__(self, token=None,  axonURL=None, debug=None, logger=None, personalityId=None, integrationId=None, language='en-US', sessionId=None):
        super(StreamingNode, self).__init__(token=token,  axonURL=axonURL, debug=debug, logger=logger)
        self.personalityId = personalityId
        self.integrationId = integrationId
        self.language = language
        self.sessionId = sessionId

    def connect(self):
        from twisted.internet import reactor
        super(StreamingNode, self).connect(blocking=False)
        reactor.run()

    def _setUp(self):
        super(StreamingNode, self)._setUp()
        self.transport = None
        if not self.personalityId:
            self.personalityId = os.environ["PERSONALITYID"] 
        # self.msKey = os.environ["MSKEY"]
        if not self.integrationId:
            self.integrationId = os.environ['INTEGRATIONID'] #"f0458d18-3108-11e9-b210-d663bd873d93" - This is the robot integrationId - this needs to be set correctly using env
        params = {
            'integrationId': self.integrationId,
            'personalityId': self.personalityId
        }
        if not self.sessionId:
            try:
                print("URL: {}".format(self.axonURL))
                BTPostRequest('sessionAccessRequest', params, accessToken=self.token, url=self.axonURL, callback=self.setSessionId).send(True) #This is called as a blocking call - if there is never a response coming this might be a problem...
            except Exception as e:
                try:
                    self.publishError('Unable to get sessionId: {}'.format(e))
                except:
                    pass # if not connected it will only print here
                time.sleep(2) # sleep
                self._setUp()  # and retry
            
        

    def setSessionId(self, response):
        # print('response: {}'.format(response))
        if response['success']:
            self.sessionId = response['sessionToken']
            print('[{}]set sessionId to {}'.format(self.nodeName, self.sessionId))
        else:
            pass # TODO: what should I do here? - retry

    def _onDisconnected(self): 
        # kill the connection here
        super(StreamingNode, self)._onDisconnected()
        if self.transport:
            self.transport.loseConnection()
            self.transport.connectionLost(reason=None)
            print('Killing the AudioStreamer')

    def _onConnected(self): 
        """
        This will be executed after a the Node is succesfully connected to the btNexus
        Here you need to subscribe and set everything else up.

        :returns: None
        """
        super(StreamingNode, self)._onConnected()
        # start the streaming in a thread
        # start a sending client here
        self.subscribe(group=self.personalityId, topic='audio', callback=self.initStream_response)
        self.publish(group=self.personalityId, topic='audio', funcName='initStream', params=[self.sessionId, self.language])


    def initStream_response(self, **kwargs):
        if not self.transport:
            serverAddress = kwargs['returnValue']
            print('Want to connect to {}'.format(serverAddress))
            self.host, self.port = serverAddress.split(':')
            self.port = int(self.port)
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
    