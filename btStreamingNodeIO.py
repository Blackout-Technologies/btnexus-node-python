"""
A Node which can stream binary data
"""
# System imports
from threading import Thread, Timer
import time
import os
import warnings

# 3rd Party imports
from btNode import Node

# local imports

# end file header
__author__      = 'Adrian Lubitz'
__copyright__   = 'Copyright (c)2017, Blackout Technologies'

class StreamingNode(Node):
    """
    A Node which can stream binary data
    """
    def publishStream(self, group, topic, funcName, stream, **kwargs):
        """
        starts a Stream with the payload(funcName and params) to a topic.

        :param group: Name of the group
        :type group: String
        :param topic: Name of the topic
        :type topic: String
        :param funcName: Name of the function.
        :type funcName: String
        :param stream: a stream Object that will be stream to the group/topic/funcName
        :type stream: stream
        """
        #TODO: new publishing StreamHelperNode
        pass

    def unpublishStream(self, group, topic, funcName, **kwargs):
        #TODO: kill correct StreamHelperNode
        pass

    def subscribeStream(self, group, topic, callback, funcName=None):
        """
        Subscribe to a stream on group & topic with a callback

        :param group: Name of the group
        :type group: String
        :param topic: Name of the topic
        :type topic: String
        :param callback: function pointer to the callback
        :type callback: function pointer
        :param funcName: Name of the function. If not set this is the name of the function in the implementation(needed if you want to link a function to a different name)
        :type funcName: String
        """
        #TODO: new subscring StreamHelperNode
        pass

    def unsubscribeStream(self, group, topic, funcName, **kwargs):
        #TODO: kill correct StreamHelperNode
        pass

    
class StreamingHelperNode(Node):
    """
    A Helper Node, which sends or receives streams
    """
    def __init__(self, group, topic, funcName, callback=None, stream=None, **kwargs):
        super(StreamingHelperNode, self).__init__(**kwargs)
        if (stream and callback) or (not stream and not callback):
            raise AttributeError("Either callback XOR stream to init StreamingHelperNode. Not both nor none.")
        elif stream:
            self.sending = True
            self.stream = stream
        elif callback:
            self.sending = False
            self.callback = callback
        
        self.group = group
        self.topic = topic
        self.funcName = funcName

    def onStreamData(self, data):
        Thread(target=self.callback, args=(data,)).start()

    def onConnected(self):
        self.nexusConnector.join("{}.{}.{}".format(self.group, self.topic, self.funcName))
        self.nexusConnector.join("btnexus-stream-out") #TODO remove!
        if self.sending:     
            #TODO maybe start a Thread here to leave the onConnected method gracefully
            print("[{}] Want to start sending".format(self.nodeName))   
            # self.nexusConnector.sio.emit('btnexus-stream', "here I want to send stuff", namespace="/{}".format(self.nexusConnector.hostId))    
            # time.sleep(8)
            # self.nexusConnector.sio.emit('btnexus-stream', "here I want to send stuff", namespace="/{}".format(self.nexusConnector.hostId))    
            # StreamHelperNode sends chunks
            byte = self.stream.read(64)
            print('read the first chunk')
            while byte and self.isConnected:
                # time.sleep(0.25)
                self.nexusConnector.sio.emit('btnexus-stream', byte, namespace="/{}".format(self.nexusConnector.hostId))
                #print('sent a chunk')
                byte = self.stream.read(64)
            #TODO: after I sent everything or after someone fiorced me to - stop sending and disconnect
            # self.disconnect()
        else:
            print('[{}] want to start listening'.format(self.nodeName))
            self.nexusConnector.sio.on('stream', self.onStreamData, namespace="/{}".format(self.nexusConnector.hostId)) #TODO: probably change btnexus-stream to stream later
            print('[{}] REALLY IMMA TRYING TO USE THE DATA'.format(self.nodeName))

if __name__ == "__main__":

    fileCopy = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'BBCOPY.wav'), 'wb')
    def callback(data):
        # print('received data')
        fileCopy.write(data)
        fileCopy.flush()

    class Receiver(StreamingHelperNode):
        pass
    class Sender(StreamingHelperNode):
        pass
    receiver = Receiver(group='testGroup', topic='testTopic', funcName='testFuncName', callback=callback, packagePath='tests/packageIntegration.json', debug=False).connect(blocking=False, binary=True, engineio_logger=False)

    import time
    time.sleep(2)


    stream = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'BB.wav'), 'rb')  
    sender = Sender(group='testGroup', topic='testTopic', funcName='testFuncName', stream=stream, packagePath='tests/packageIntegration.json', debug=False).connect( binary=True, engineio_logger=False)

    
    