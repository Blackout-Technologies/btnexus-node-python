# '''Tests for the Hook'''
# # System imports
# import unittest
# import time, os
# import logging
# import inspect
# import json
# import base64
# from multiprocessing.pool import ThreadPool as Pool


# # 3rd Party imports
# import timeout_decorator
# from btPostRequest import BTPostRequest

# # local imports
# from reconnectUtils import ShakyInternet

# # end file header
# __author__      = 'Adrian Lubitz'
# __copyright__   = 'Copyright (c)2017, Blackout Technologies'

# # moduleName = 'TESTS'
# # logger = logging.getLogger(moduleName)
# # logger.setLevel(Hook.NEXUSINFO)
# # # create file handler which logs even debug messages
# # fh = logging.StreamHandler()
# # fh.setLevel(Hook.NEXUSINFO)
# # formatter = logging.Formatter('%(asctime)s - [%(levelname)s]: %(message)s') 
# # fh.setFormatter(formatter)
# # logger.addHandler(fh)


# class TestChatIntegration(unittest.TestCase):
#     '''Tests for a simple chat integration'''
#     # shakyInternet = ShakyInternet()
#     # timeout = (5, 5)
#     local_rc = os.path.join(os.path.dirname(os.path.realpath(os.path.abspath(__file__))), '.btnexusrc_integration')
#     print("Class: {}".format(local_rc))
#     if os.path.isfile(local_rc):
#         print("using local btnexusrc file")
#         rc_path = local_rc
#     elif "HOOKRC" in os.environ:
#         print("using env var HOOKRC")
#         rc_path = os.environ['HOOKRC']
#     else:
#         raise Exception("No valid btnexusrc")

#     with open(rc_path) as rcFile:
#         connectHash = rcFile.read()
#     config = json.loads(base64.b64decode(connectHash))
#     applicationId = config['id']
#     applicationType = 'integration'
#     personalityId = '382279b1-6620-3f73-1772-67859e0305f9' # TODO: this is Captain Hook - needs to be changed to Auto Tests later
#     params = {
#     'integrationId': applicationId,
#     'personalityId': personalityId
#     }

    
#     def onFirstChat(self, response):
#         if response['success']:
#             # There can still be an error in response['response'] - if so publishDebug the error
#             if 'error' in response['response']:
#                 raise Exception("Error in chat response: {}".format(response['response']['error']))
#             answer = response['response']['answer']
#             print("ANSWER: {}".format(answer))
#             assert answer == "Hello, you! How are you?"
#         else:
#             raise Exception('error getting the chat response: {}'.format(response['error']))


#     def onSecondChat(self, response):
#         if response['success']:
#             # There can still be an error in response['response'] - if so publishDebug the error
#             if 'error' in response['response']:
#                 raise Exception("Error in chat response: {}".format(response['response']['error']))
#             answer = response['response']['answer']
#             print("ANSWER: {}".format(answer))
#             assert answer == "Hello world from my new btNexus Hook!"
#         else:
#             raise Exception('error getting the chat response: {}'.format(response['error']))


#     def onThirdChat(self, response):
#         if response['success']:
#             # There can still be an error in response['response'] - if so publishDebug the error
#             if 'error' in response['response']:
#                 raise Exception("Error in chat response: {}".format(response['response']['error']))
#             answer = response['response']['answer']
#             print("ANSWER: {}".format(answer))
#             assert answer == "Hello world from my second btNexus Hook!"
#         else:
#             raise Exception('error getting the chat response: {}'.format(response['error']))


#     def onSessionId(self, response):
#         if response['success']:
#             sessionToken = response['sessionToken']
#             print('SessionId: {}'.format(sessionToken))
#             # call first chat blocking
#             params = {
#                 'text': 'hi',
#                 'language': 'en-US',
#                 'sessionToken': sessionToken
#             }
#             BTPostRequest('chat', params, accessToken=self.config['token'], url=self.config['host'], callback=self.onFirstChat).send(blocking=True)

#             # call second chat blocking
#             params = {
#                 'text': 'what do you know about hooks?',
#                 'language': 'en-US',
#                 'sessionToken': sessionToken
#             }
#             BTPostRequest('chat', params, accessToken=self.config['token'], url=self.config['host'], callback=self.onSecondChat).send(blocking=True)
            
#             # call third chat blocking
#             params = {
#                 'text': 'what is the second greeting?',
#                 'language': 'en-US',
#                 'sessionToken': sessionToken
#             }
#             BTPostRequest('chat', params, accessToken=self.config['token'], url=self.config['host'], callback=self.onThirdChat).send(blocking=True)
#         else:
#             raise Exception('error getting the chatSessionId: {}'.format(response['error']))

        


#     @timeout_decorator.timeout(120, use_signals=False)
#     def test_chat(self, a=None):
#         '''
#         test to make chain of chat requests in one session
#         '''
#         # get sessionId blocking - and starting the chain
#         BTPostRequest('sessionAccessRequest', self.params, accessToken=self.config['token'], url=self.config['host'], callback=self.onSessionId).send(blocking=True) 
    
#     @timeout_decorator.timeout(120)
#     def test_chat_parallel(self):
#         '''
#         test to make chain of chat requests in multiple sessions in parallel
#         '''
#         p = Pool(20)
#         p.map(self.test_chat, range(100))

# if __name__ == "__main__":
#     unittest.main()
