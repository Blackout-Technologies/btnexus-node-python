'''
A Node which accepts audio streams and forwards them to the speech to text service of your choice and publishes the transcript on the transcript topic
This example needs to have the speech to text service up and running for your personality.
'''

# System imports
from threading import Timer
import time
import os
# 3rd Party imports
# from btNode import Node
from btStreamingNode import StreamingNode

# local imports
# end file header
__author__      = 'Adrian Lubitz'
__copyright__   = 'Copyright (c)2017, Blackout Technologies'



class AudioFileStreamingNode(StreamingNode):

    def onConnected(self):
        pass # publish the file to a predefined group/topic/funcName.
        stream = open('BB.wav', 'rb')  
        self.publishStream('group', 'topic', 'funcName', stream)

class AudioFileReceivingNode(StreamingNode):
    def onConnected(self):
        pass # subscribe to a predefined group/topic/funcName where I publish the file. Subscribe with a callback that writes it on disk.
        self.fileCopy = open('BBCOPY.wav', 'wb')  
        self.numberOfChunks = 0
        self.subscribeStream('group', 'topic', callback=self.writeFile, funcName='funcName')

    def writeFile(self, incomingData):
        pass
        self.fileCopy.write(incomingData)
        self.numberOfChunks += 1
        
    def onDisconnected(self):
        #TODO: unsubscribe
        self.fileCopy.close()
        print("Saved {} chunks".format(self.numberOfChunks))
        
if __name__ == '__main__':
    # asn = AudioFileStreamingNode(language='en-US', personalityId='18b50f0b-d966-6e5a-1fa1-b3a31e4fc428' , integrationId='randomIntegration' ,sessionId='abc123')
    receiver = AudioFileReceivingNode(packagePath='../tests/packageIntegration.json')
    receiver.connect(blocking=False)

    time.sleep(5) # giving the receiver some time - normally you should implement some protocol which does some handshake to make sure both ends are ready to receive

    
    sender = AudioFileStreamingNode(packagePath='../tests/packageIntegration.json')
    sender.connect(blocking=False)

    time.sleep(10) # After 10 seconds stop the receiver assuming this is enough time to receive the whole file - normally you should implement some protocol which indicates when the sender is done if it is a finite stream(In general the streamingNode is designed for infinite raw streams)

    receiver.disconnect()

    
    