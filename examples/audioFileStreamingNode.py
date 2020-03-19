'''A Node which accepts audio streams and forwards them to the speech to text service of your choice and publishes the transcript on the transcript topic'''

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
        # `group: personalityId.sessionId`, `topic: speechToText`, `funcName:transcript`.
        self.subscribe(group='{}.{}'.format(self.personalityId, self.sessionId), topic='speechToText', callback=self.transcript)
        self.subscribe(group='{}.{}'.format(self.personalityId, self.sessionId), topic='speechToText', callback=self.intermediateTranscript)

    def transcript(self, transcript):
        print('[TRANSCRIPT]: {}'.format(transcript))
        # can't directly disconnect, because the response needs to be send back first.
        # Timer(5.0, self.onStreamReady).start()
        Timer(3.0, self.disconnect).start()


    def intermediateTranscript(self, transcript):
        print('[INTERMEDIATE]: {}'.format(transcript))

    def onStreamReady(self):
        '''
        Here the audio file is opened and the stream is given to self.stream()
        '''
        print('starting to send audio')
        audio = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'BB.wav'), 'rb')  
        self.stream(audio)



if __name__ == '__main__':
    # asn = AudioFileStreamingNode(language='en-US', personalityId='18b50f0b-d966-6e5a-1fa1-b3a31e4fc428' , integrationId='randomIntegration' ,sessionId='abc123')
    asn = AudioFileStreamingNode(sessionId = 'Test', packagePath='../tests/packageSpeechIntegration.json', rcPath='../../streaming-axon/speechIntegration/.btnexusrc')
    asn.connect()

    
    