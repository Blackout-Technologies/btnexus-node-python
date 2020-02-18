'''A Node which accepts audio streams and forwards them to the speech to text service of your choice and publishes the transcript on the transcript topic'''

# System imports
from threading import Thread
import time
import os
# 3rd Party imports
from btNode import Node
from btStreamingNode import StreamingNode
# local imports
# end file header
__author__      = 'Adrian Lubitz'
__copyright__   = 'Copyright (c)2017, Blackout Technologies'


# FORMAT = pyaudio.paInt16 
# CHANNELS = 2
# RATE = 16000  # This was 44100
# INPUT_BLOCK_TIME = 0.05 #Size of a block in s
# INPUT_FRAMES_PER_BLOCK = int(RATE*INPUT_BLOCK_TIME) #Size of a block in bytes
# SECONDS_TO_RECORD = 5


class AudioFileStreamingNode(StreamingNode):

    # def setUp(self):
    #     super().setUp()
    def setUp(self):
        print("MEIN SETUP!")
        

    def onConnected(self):
        # `group: personalityId`, `topic: sessionId`, `funcName:transcript`.
        # super().onConnected()
        self.subscribe(group=self.personalityId, topic=self.sessionId, callback=self.transcript)
        self.subscribe(group=self.personalityId, topic=self.sessionId, callback=self.intermediateTranscript)

    def transcript(self, transcript):
        print('[TRANSCRIPT]: {}'.format(transcript))

    def intermediateTranscript(self, transcript):
        print('[INTERMEDIATE]: {}'.format(transcript))

    def onStreamReady(self):
        '''
        Stream as long as you want but use reactor.callFromThread and after finishing self.transport.loseConnection and self.transport = None
        '''
        print('starting to send audio')
        from twisted.internet import reactor
        # audio = open('/home/al/repos/python-docs-samples/speech/cloud-client/resources/audio.raw', 'rb')
        # TODO: This should be given as a parameter(env var)
        audio = open('/home/al/repos/streaming-axon/BB.wav', 'rb')  # This has some more silence in the end - so the API can recognize the end of thr utterance
        byte = audio.read(64)
        while byte:
            reactor.callFromThread(self.transport.write, byte)
            byte = audio.read(64)
        # TODO: resend after a break of 15s
        time.sleep(15) # If no sleep is used it is not working - why? 3s works fine! 15s causes a timeout.
        self.onStreamReady()


if __name__ == '__main__':
    asn = AudioFileStreamingNode()
    asn.connect()
    