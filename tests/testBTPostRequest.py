'''Tests for the BTPostRequest'''
# System imports
from __future__ import print_function
import unittest
from threading import Lock
import time
import os


# 3rd Party imports
from btPostRequest import BTPostRequest
# local imports
# end file header
__author__      = 'Adrian Lubitz'
__copyright__   = 'Copyright (c)2017, Blackout Technologies'

class TestBTPostRequest(unittest.TestCase):
    '''Tests for the BTPostRequest'''
    def setUp(self):
        self.lock = Lock()
        self.looping = True
        self.errorMsg = False
        self.exception = None
        self.token = os.environ["TOKEN"]
        self.axon = os.environ["AXON_HOST"]
        self.personalityId = os.environ["PERSONALITYID"]
        self.integrationId = os.environ["INTEGRATIONID"]
        print('Token: {}'.format(self.token))
        print('url: {}'.format('https://' + self.axon))


    def callback(self, response):
        """
        callback for the request
        """
        if response['success']:
            self.errorMsg = False 
            print('RESPONSE: {}'.format(response))
        else:
            self.errorMsg = response['error']
        self.lock.release()

    def errBack(self, exception):
        """
        errBack for the request
        """
        self.exception = exception
        self.lock.release()


    def test_threadedSendSessionAccessRequest(self):
        '''
        test to send and btPostrequest and receive a response in a threaded fashion.
        '''
        print('TESTING THE threadedSendSessionAccessRequest')
        params = {
        'integrationId': self.integrationId,
        'personalityId': self.personalityId
        }

        self.lock.acquire()
        BTPostRequest('sessionAccessRequest', params, accessToken=self.token, url='https://' + self.axon, callback=self.callback, errBack=self.errBack).send()
        self.lock.acquire()
        if self.errorMsg:
            raise Exception(self.errorMsg)
        if self.exception:
            raise self.exception

    def test_blockingSendSessionAccessRequest(self):
        '''
        test to send and btPostrequest and receive a response in a blocking fashion.
        '''
        print('TESTING THE blockingSendSessionAccessRequest')
        params = {
        'integrationId': self.integrationId,
        'personalityId': self.personalityId
        }
        BTPostRequest('sessionAccessRequest', params, accessToken=self.token, url='https://' + self.axon, callback=print).send(blocking=True, timeout=2)

if __name__ == "__main__":
    unittest.main()