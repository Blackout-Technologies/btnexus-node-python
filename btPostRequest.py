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
    def __init__(self, intent, params, accessToken, url, callback=None, errBack=None):
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
        :param errBack: callback to handle errors that prevent that the response can be handled by the callback. takes one argument which is the exception - This is needed for the threaded send() otherwise exceptions can't be handled
        :type errBack: function pointer
        """

        # check if slash in the end
        if not url.endswith("/"):
            url += "/"
        url += "api"
        
        params['api'] = {'version':'5.0', 'intent':intent}
        self.headers = {'content-type': 'application/json', 'blackout-token': accessToken}
        # print("Headers: {}".format(self.headers))
        # print("Payload: {}".format(params))
        super(BTPostRequest, self).__init__(url, params, callback, errBack)

    def send(self, blocking=False, **kwargs):
        """
        sending the request and executing the callback or errBack

        :param blocking: decides if the call is blocking or threaded
        :type blocking: Boolean
        :param kwargs: keyword arguments for the requests.post call see https://2.python-requests.org//en/v2.5.3/api/ - `headers` cant be customized for a btPostRequest because it is already used internally
        """

        super(BTPostRequest, self).send(blocking=blocking, headers=self.headers, **kwargs)
