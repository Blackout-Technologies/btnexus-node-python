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
        self.subscribers = {} # mapping between group/topic/funcName and the StreamingNodeHelper which handles the stream - could also be multiple(does not make too much sense though)

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
        # new publishing StreamHelperNode
        if not '{}.{}.{}'.format(group, topic, funcName) in self.streams:
            self.streams['{}.{}.{}'.format(group, topic, funcName)] = StreamingHelperNode(group=group, topic=topic, funcName=funcName, stream=stream, packagePath=self.packagePath, connectHash=self.connectHash, debug=self.debug, logger=self.logger, **kwargs)
            self.streams['{}.{}.{}'.format(group, topic, funcName)].connect(blocking=False, binary=True, **kwargs)    
        else:
            pass #TODO: kill the old and start the new one

    def unpublishStream(self, group, topic, funcName, **kwargs):
        #TODO: kill correct StreamHelperNode
        if '{}.{}.{}'.format(group, topic, funcName) in self.streams:
            # disconnect
            self.streams['{}.{}.{}'.format(group, topic, funcName)].disconnect()
        else:
            pass #TODO: exception?

    def subscribeStream(self, group, topic, callback, funcName=None, **kwargs):
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
        if not funcName:
            funcName = callback.__name__
        #TODO: new subscring StreamHelperNode
        if not '{}.{}.{}'.format(group, topic, funcName) in self.subscribers:
            self.subscribers['{}.{}.{}'.format(group, topic, funcName)] = StreamingHelperNode(group=group, topic=topic, funcName=funcName, callback=callback, packagePath=self.packagePath, connectHash=self.connectHash, debug=self.debug, logger=self.logger, **kwargs)
            self.subscribers['{}.{}.{}'.format(group, topic, funcName)].connect(blocking=False, binary=True, **kwargs)    
        else:
            pass #TODO: kill the old and start the new one

    def unsubscribeStream(self, group, topic, funcName, **kwargs):
        #TODO: kill correct StreamHelperNode
        if '{}.{}.{}'.format(group, topic, funcName) in self.streams:
            # disconnect
            self.subscribers['{}.{}.{}'.format(group, topic, funcName)].disconnect()
        else:
            pass #TODO: exception?

    
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
        # self.nexusConnector.join("btnexus-stream-out") #TODO remove!
        if self.sending:     
            #TODO maybe start a Thread here to leave the onConnected method gracefully
            print("[{}] Want to start sending".format(self.nodeName))   
            # self.nexusConnector.sio.emit('btnexus-stream', "here I want to send stuff", namespace="/{}".format(self.nexusConnector.hostId))    
            # time.sleep(8)
            # self.nexusConnector.sio.emit('btnexus-stream', "here I want to send stuff", namespace="/{}".format(self.nexusConnector.hostId))    
            
            fileCopy = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'BBCOPYbeforesending.wav'), 'wb')
            numberOfChunks = 0

            # StreamHelperNode sends chunks
            byte = self.stream.read(1024) 
            # testBytes = ["1", "2", "3", "4", "5"]
            # try:
            #     byte = testBytes.pop(0)
            # except:
            #     byte = None
            # print('read the first chunk')
            while byte and self.isConnected:

                fileCopy.write(byte)
                numberOfChunks += 1

                # time.sleep(0.25)
                self.nexusConnector.sio.emit('btnexus-stream', byte, namespace="/{}".format(self.nexusConnector.hostId))
                #print('sent a chunk')
                byte = self.stream.read(1024) 
                # try:
                #     byte = testBytes.pop(0)
                # except:
                #     byte = None
            #TODO: after I sent everything or after someone forced me to - stop sending and disconnect
            time.sleep(10) # TODO: here the underlying socket buffer may not be completely empty by now which means I would kill of some bytes if I dont sleep - maybe there is a better option like waiting for the buffer and then disconnect...
            
            fileCopy.close()
            print('[Sender]: NumberOfChunks: {}'.format(numberOfChunks))

            
            self.disconnect()
        else:
            self.nexusConnector.sio.on('stream', self.onStreamData, namespace="/{}".format(self.nexusConnector.hostId)) #TODO: probably change btnexus-stream to stream later
            print('[Receiver]: started listening')
if __name__ == "__main__":
    #import GoogleHelper for Testing
    from googleHelper import GoogleHelper

    def finalPrint(sessionId, transcript):
        print('[FINAL]: {}'.format(transcript))

    def interPrint(sessionId, transcript):
        print('[INTERMEDIATE]: {}'.format(transcript))

    g = GoogleHelper('en-US', finalPrint, interPrint, 'testId')
    # audio = open('/Users/adrianlubitz/repos/btnexus-node-python/BB.wav', 'rb') # original file works fine copy gives wrong results probably because it is somehow broken.
    g.start() # Times out after ~10 secs without audio
    # byte = audio.read(1)
    # while byte:
    #     g.feedData(byte)
    #     byte = audio.read(1)




    numberOfChunks = 0
    fileCopy = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'BBCOPY.wav'), 'wb')
    def callback(data):
        g.feedData(data)
        global numberOfChunks
        # print('received data: {}'.format(data))
        fileCopy.write(data)
        fileCopy.flush()
        numberOfChunks += 1
        

    class Receiver(StreamingHelperNode):
        pass
    class Sender(StreamingHelperNode):
        pass
    receiver = Receiver(group='testGroup', topic='testTopic', funcName='testFuncName', callback=callback, packagePath='tests/packageIntegration.json', debug=False).connect(blocking=False, binary=True, engineio_logger=False)

    import time
    time.sleep(2)


    stream = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'BB.wav'), 'rb')  
    sender = Sender(group='testGroup', topic='testTopic', funcName='testFuncName', stream=stream, packagePath='tests/packageIntegration.json', debug=False).connect(blocking=False, binary=True, engineio_logger=False)
    
    #TODO: MIC streaming
    
    time.sleep(19)
    print('[Receiver]: NumberOfChunks: {}'.format(numberOfChunks))
    
    