'''Helper Object for google speech service'''
# System imports
import threading
from threading import Thread
# 3rd Party imports
from google.cloud import speech
from six.moves import queue
# local imports
# end file header
__author__      = 'Adrian Lubitz'
__copyright__   = 'Copyright (c)2017, Blackout Technologies'

class GoogleHelper():
    def __init__(self, languageCode, transcriptCallback, intermediateTranscriptCallback, sessionId): # TODO: The mapping to the sessionId is somehow still needed here!
        self.sessionId = sessionId # TODO: this is not 100% clean...because the helper shouldnt know about the session? Is probably okay
        self.transcriptCallback = transcriptCallback # needs to take to arguments (sessionId, transcript)
        self.intermediateTranscriptCallback = intermediateTranscriptCallback # needs to take to arguments (sessionId, transcript)
        self._buff = queue.Queue()
        self.closed = True
        self.sampleRate = 16000
        self.languageCode = languageCode
        self.collectLoop = None #Thread(target=self._start)

    def feedData(self, data):
        self._buff.put(data)
    def generator(self):
        while not self.closed:
            # Use a blocking get() to ensure there's at least one chunk of
            # data, and stop iteration if the chunk is None, indicating the
            # end of the audio stream.
            chunk = self._buff.get()
            if chunk is None:
                return
            data = [chunk]

            # Now consume whatever other data's still buffered.
            while True:
                try:
                    chunk = self._buff.get(block=False)
                    if chunk is None:
                        return
                    data.append(chunk)
                except queue.Empty:
                    break
            yield b''.join(data)
    
    def stop(self):
        self.closed = True
        self.collectLoop = None
        # self.collectLoop.join() # TODO: test!
        # TODO: empty buffer and (close connection to google) - for restarting later

    def start(self):
        """
        This starts a Thread calling the API
        """
        if self.closed:
            self.closed = False
            self.collectLoop = Thread(target=self._start)
            self.collectLoop.start()
    
    def restart(self):
        self.stop()
        self._start()

    def _start(self):
        # print('[START SERVICE]: {}'.format(threading.currentThread().getName()))
        client = speech.SpeechClient() # TODO: write credentials to file and create the client with speech.SpeechClient.from_service_account_file
        config = speech.types.RecognitionConfig(
        encoding=speech.enums.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=self.sampleRate,
        language_code=self.languageCode,
        max_alternatives=1,
        enable_word_time_offsets=True)

        streaming_config = speech.types.StreamingRecognitionConfig(
        config=config,
        interim_results=True)

        audio_generator = self.generator()

        requests = (speech.types.StreamingRecognizeRequest(
                audio_content=content)
                for content in audio_generator)
            
        # responses itself is a generator because it uses a generator and therefore every response is directly used in listen_print_loop
        responses = client.streaming_recognize(streaming_config,
                                                   requests)
        try:
            for response in responses:
                # print('got response: {}'.format(response))
                self._handleResponse(response)
            # print('I shouldnt be here')
        except Exception as e:
            print('[EXCEPTION]: {}'.format(e)) 
            self.restart() 
        # print('[END SERVICE]: {}'.format(threading.currentThread().getName()))

    def _handleError(self, error):
        # print('[ERRORTYPE]: {}'.format(type(error))) # google.rpc.status_pb2.Status
        print('[ERROR]: {}'.format(error)) # TODO: make some sense here and maybe somewhere else needs to be a try...
        # self.stop()

    def _handleResponse(self, response):
        print("Handeling resonse") #TODO:remove!
        if response.error.code:
            self._handleError(response.error)
        if response.results:
            if response.results[0].is_final:
                self.transcriptCallback(self.sessionId, response.results[0].alternatives[0].transcript) # Only 1 alternative is used for final results
            else:
                self.intermediateTranscriptCallback(self.sessionId, response.results[0].alternatives[0].transcript) # Taking only the first(most-likely) alternative
                # for i, result in enumerate(response.results):
                #     self.intermediateTranscriptCallback(result.alternatives[0].transcript + ': {}'.format(i)) # Taking only the first(most-likely) alternative

if __name__ == '__main__':
    def finalPrint(sessionId, transcript):
        print('[FINAL]: {}'.format(transcript))

    def interPrint(sessionId, transcript):
        print('[INTERMEDIATE]: {}'.format(transcript))

    g = GoogleHelper('en-US', finalPrint, interPrint, 'testId')
    audio = open('/home/al/repos/python-docs-samples/speech/cloud-client/resources/audio.raw', 'rb')
    g.start() # Times out after ~10 secs without audio
    byte = audio.read(1)
    while byte:
        g.feedData(byte)
        byte = audio.read(1)

