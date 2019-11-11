"""A post request following the BTProtocol"""
# System imports

import json
import threading
import requests

# 3rd Party imports

# local imports
from nexus.postRequest import PostRequest

# end file header
__author__      = "Adrian Lubitz"
__copyright__   = "Copyright (c)2017, Blackout Technologies"

class BTPostRequest(PostRequest):
    """A post request following the BTProtocol"""
    def __init__(self, intent, params, accessToken, url, callback=None):
        """
        setting up the request with the btProtocol.

        :param intent: intent for the BTPostRequest
        :type intent: String
        :param params: the parameters for the BTPostRequest
        :type params: dict
        :param accessToken: the accessToken
        :type accessToken: String
        :param url: the url of the instance to send the request to
        :type url: String
        :param callback: the callback which handles the response
        :type callback: function pointer
        """

        # check if slash in the end
        if not url.endswith("/"):
            url += "/"
        url += "api"
        
        params['api'] = {'version':'5.0', 'intent':intent}
        headers = {'content-type': 'application/json', 'blackout-token': accessToken}
        super(BTPostRequest, self).__init__(url, params, callback, headers = headers)

if __name__ == '__main__':
    import os
    def printResponse(response):
        print('Response: {}'.format(response))
    token = os.environ["TOKEN"]
    axon = os.environ["AXON_HOST"]
    # print ("URL: {}".format(axon))
    # print ("Token: {}".format(token))
    personalityId = os.environ["PERSONALITYID"]
    integrationId = "f0458d18-3108-11e9-b210-d663bd873d93" # TODO: This is the robot integrationId - this needs to be set correctly
    params = {
        'integrationId': integrationId,
        'personalityId': personalityId
    }
    print('params: {}'.format(params))
    print('Token: {}'.format(token))
    print('url: {}'.format('https://' + axon))

    BTPostRequest('sessionAccessRequest', params, accessToken=token, url='https://' + axon, callback=printResponse).send()

