"""Memory in the Nexus Network."""
# System imports
import os
import base64
import json
import sys


# 3rd Party imports
from btPostRequest import BTPostRequest

# local imports

# end file header
__author__      = "Adrian Lubitz"
__copyright__   = "Copyright (c)2017, Blackout Technologies"

class BTNexusMemory(object):
    """Memory in the Nexus Network."""
    def __init__(self, url, token):
        """
        initialize variables for the BTPostRequests

        :param url: the url of the api
        :type url: String
        :param token: the access token for the api call
        :type token: String
        """
        self.url = url
        self.token = token

    def addEvent(self, data, callback=None):
        """
        adding an Event 

        :param data: the data for the api call
        :type data: json
        :param callback: callback for the api call
        :type callback: function pointer
        """
        BTPostRequest("memoryDataRegister", data, self.token, self.url, callback).send()

    def removeEvent(self, data, callback=None):
        """
        removing an Event 

        :param data: the data for the api call
        :type data: json
        :param callback: callback for the api call
        :type callback: function pointer
        """
        BTPostRequest("memoryDataUnregister", data, self.token, self.url, callback).send()
