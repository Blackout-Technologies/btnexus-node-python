'''
A Node which accepts audio streams and forwards them to the speech to text service of your choice and publishes the transcript on the transcript topic
This example needs to have the speech to text service up and running for your personality.
'''

# System imports
from threading import Timer
import time
import os
# 3rd Party imports
import pyaudio

# from btNode import Node
from btStreamingNode import StreamingNode

# local imports
from googleHelper import GoogleHelper
# end file header
__author__      = 'Adrian Lubitz'
__copyright__   = 'Copyright (c)2017, Blackout Technologies'



class MicStreamingNode(StreamingNode):

    def onConnected(self):
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 16000
        CHUNK = 1024
        audio = pyaudio.PyAudio()
        #### For Mac PYAudio recording works only from terminal not from vscode integrated terminal - issue with asking for permissions
        stream = audio.open(format=FORMAT, channels=CHANNELS,
                    rate=RATE, input=True,
                    frames_per_buffer=CHUNK)
        self.publishStream('group', 'topic', 'funcName', stream)

class STTNode(StreamingNode):
    def onConnected(self):
        self.g = GoogleHelper('en-US', self.finalPrint, self.interPrint, 'testId')
        self.g.start() # Times out after ~10 secs without audio
        self.subscribeStream('group', 'topic', callback=self.transcribe, funcName='funcName')

    def transcribe(self, soundData):
        self.g.feedData(soundData)

    def finalPrint(self, sessionId, transcript):
        print('[FINAL]: {}'.format(transcript))

    def interPrint(self, sessionId, transcript):
        print('[INTERMEDIATE]: {}'.format(transcript))
        
        
if __name__ == '__main__':
    # asn = AudioFileStreamingNode(language='en-US', personalityId='18b50f0b-d966-6e5a-1fa1-b3a31e4fc428' , integrationId='randomIntegration' ,sessionId='abc123')
    receiver = STTNode(packagePath='../tests/packageIntegration.json')
    receiver.connect(blocking=False)
    
    sender = MicStreamingNode(packagePath='../tests/packageIntegration.json')
    sender.connect(blocking=False)



    
    