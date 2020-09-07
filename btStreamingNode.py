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
    def __init__(self, **kwargs):
        super(StreamingNode, self).__init__(**kwargs)
        self.streams = {} # mapping between group/topic/funcName and the StreamingNodeHelper which sends the stream - can only be one
        self.subscribers = {} # mapping between group/topic/funcName and the StreamingNodeHelper which handles the stream - could also be multiple(does not make too much sense though) - first attempt should be only one!

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
        # new publishing StreamHelperNode - maybe also check if the Helper is still alive
        if not '{}.{}.{}'.format(group, topic, funcName) in self.streams:
            self.streams['{}.{}.{}'.format(group, topic, funcName)] = StreamingHelperNode(group=group, topic=topic, funcName=funcName, stream=stream, packagePath=self.packagePath, connectHash=self.connectHash, debug=self.debug, logger=self.logger, **kwargs)
            self.streams['{}.{}.{}'.format(group, topic, funcName)].connect(blocking=False, binary=True, **kwargs)    
        else:
            self.unpublishStream(group=group, topic=topic, funcName=funcName, **kwargs)
            self.publishStream(group=group, topic=topic, funcName=funcName, stream=stream, **kwargs)
            

    def unpublishStream(self, group, topic, funcName, **kwargs):
        # kill correct StreamHelperNode
        if '{}.{}.{}'.format(group, topic, funcName) in self.streams:
            # disconnect
            self.streams['{}.{}.{}'.format(group, topic, funcName)].disconnect()
            del self.streams['{}.{}.{}'.format(group, topic, funcName)]
        else:
            pass #TODO: exception?
            print('You cannot unpublish from a topic you never published on')

    def subscribeStream(self, group, topic, callback, funcName=None, **kwargs):
        """
        Subscribe to a stream on group & topic with a callback

        :param group: Name of the group
        :type group: String
        :param topic: Name of the topic
        :type topic: String
        :param callback: function pointer to the callback which expects one parameter as the incoming chunks of the stream
        :type callback: function pointer
        :param funcName: Name of the function. If not set this is the name of the function in the implementation(needed if you want to link a function to a different name)
        :type funcName: String
        """
        if not funcName:
            funcName = callback.__name__
        # new subscring StreamHelperNode - maybe also check if the Helper is still alive
        if not '{}.{}.{}'.format(group, topic, funcName) in self.subscribers:
            self.subscribers['{}.{}.{}'.format(group, topic, funcName)] = StreamingHelperNode(group=group, topic=topic, funcName=funcName, callback=callback, packagePath=self.packagePath, connectHash=self.connectHash, debug=self.debug, logger=self.logger, **kwargs)
            self.subscribers['{}.{}.{}'.format(group, topic, funcName)].connect(blocking=False, binary=True, **kwargs)    
        else:
            pass # kill the old and start the new one
            self.unsubscribeStream(group, topic, funcName, **kwargs)
            self.subscribeStream(group, topic, callback, funcName, **kwargs)

    def unsubscribeStream(self, group, topic, funcName, **kwargs):
        # kill correct StreamHelperNode
        if '{}.{}.{}'.format(group, topic, funcName) in self.subscribers:
            # disconnect
            self.subscribers['{}.{}.{}'.format(group, topic, funcName)].disconnect()
            del self.subscribers['{}.{}.{}'.format(group, topic, funcName)]
        else:
            pass #TODO: exception?
            print('You cannot unsubscribe from a topic you never subscribed on')

    
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
        self.callback(data)

    def onConnected(self):
        self.nexusConnector.join("{}.{}.{}".format(self.group, self.topic, self.funcName))
        if self.sending:     
            #TODO maybe start a Thread here to leave the onConnected method gracefully
            # StreamHelperNode sends chunks
            byte = self.stream.read(1024) 
            while byte and self.isConnected:
                self.nexusConnector.sio.emit('btnexus-stream', byte, namespace="/{}".format(self.nexusConnector.hostId))
                byte = self.stream.read(1024) 
            #TODO: after I sent everything or after someone forced me to - stop sending and disconnect? Or end of stream callback?
            time.sleep(10) # TODO: here the underlying socket buffer may not be completely empty by now which means I would kill of some bytes if I dont sleep - maybe there is a better option like waiting for the buffer and then disconnect...
            self.disconnect()
        else:
            self.nexusConnector.sio.on('stream', self.onStreamData, namespace="/{}".format(self.nexusConnector.hostId)) #TODO: probably change btnexus-stream to stream later
if __name__ == "__main__":
    pass # See examples
    
    