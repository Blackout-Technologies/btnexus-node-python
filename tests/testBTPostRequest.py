### THIS IS NO LONGER NECCESSARY BECAUSE IT IS USED BY THE NODE!!!






# '''Tests for the BTPostRequest'''
# # System imports
# from __future__ import print_function
# import unittest
# from threading import Lock
# import time
# import os
# import json, base64


# # 3rd Party imports
# from btPostRequest import BTPostRequest
# import timeout_decorator

# # local imports
# from reconnectUtils import ShakyInternet

# # end file header
# __author__      = 'Adrian Lubitz'
# __copyright__   = 'Copyright (c)2017, Blackout Technologies'

# class TestBTPostRequest(unittest.TestCase):
#     '''Tests for the BTPostRequest'''
        
#     def setUp(self):
#         self.lock = Lock()
#         self.looping = True
#         self.errorMsg = False
#         self.exception = None
#         connectHash = os.environ["CONNECT_HASH"]
#         self.config = json.loads(base64.b64decode(connectHash))

#         self.token = self.config['token']
#         self.axon = self.config['host']
#         self.applicationId = self.config['id']
#         self.applicationType = 'integration'
#         self.params =  {
#         'applicationId': self.applicationId,
#         'applicationType': self.applicationType
#         }

#     def callback(self, response):
#         """
#         callback for the request
#         """
#         if response['success']:
#             self.errorMsg = False 
#             print('RESPONSE: {}'.format(response))
#         else:
#             self.errorMsg = response['error']
#         self.lock.release()

#     def errBack(self, exception):
#         """
#         errBack for the request
#         """
#         self.exception = exception
#         self.lock.release()

#     # @timeout_decorator.timeout(60, use_signals=False)
#     def test_threadedSendSessionAccessRequest(self):
#         '''
#         test to send and btPostrequest and receive a response in a threaded fashion.
#         '''
#         print('TESTING THE threadedSendSessionAccessRequest')
        

#         self.lock.acquire()
#         BTPostRequest('applicationAccessRequest', self.params, accessToken=self.token, url=self.axon, callback=self.callback, errBack=self.errBack).send()
#         self.lock.acquire()
#         if self.errorMsg:
#             raise Exception(self.errorMsg)
#         if self.exception:
#             raise self.exception

#     # @timeout_decorator.timeout(60, use_signals=False)
#     def test_blockingSendSessionAccessRequest(self):
#         '''
#         test to send and btPostrequest and receive a response in a blocking fashion.
#         '''
#         print('TESTING THE blockingSendSessionAccessRequest')
#         BTPostRequest('applicationAccessRequest', self.params, accessToken=self.token, url=self.axon, callback=print).send(blocking=True, timeout=2)

# if __name__ == "__main__":
#     unittest.main()