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

class BTNexusData(object):
    """Data in the Nexus Network."""
    def __init__(self, url, token, hookId):
        """
        initialize variables for the BTPostRequests

        :param url: the url of the api
        :type url: String
        :param token: the access token for the api call
        :type token: String
        :param hookId: ID of the hook
        :type hookId: String
        """
        self.url = url
        self.token = token
        self.hookId = hookId

    def save(self, key, value, callback=None):
        """
        save a value to a specific key in the NexusData Api

        :param key: the key to which the value should be saved
        :type key: String
        :param value: the object which should be saved
        :type value: Object
        :param callback: callback to handle the api response
        :type callback: function pointer
        """
        data = {"hookId": self.hookId, "key": key, "value": value}
        BTPostRequest("hookDataSave", data, self.token, self.url, callback).send()


    def load(self, key, callback=None):
        """
        load a value to a specific key in the NexusData Api

        :param key: the key to which the value should be saved
        :type key: String
        :param callback: callback to handle the api response
        :type callback: function pointer
        """
        data = {"hookId": self.hookId, "key": key}
        BTPostRequest("hookDataLoad", data, self.token, self.url, callback).send()
    
    def put(self, key, value, callback=None):
        """
        add a value to a specific key in the NexusData Api - the value must be a list otherwise it will be overwritten

        :param key: the key to which the value should be saved
        :type key: String
        :param value: the object which should be saved
        :type value: Object
        :param callback: callback to handle the api response
        :type callback: function pointer
        """
        def _putCallback(response):
            val = []
            if "value" in response:
                if "append" in dir(response["value"]):
                    val = response["value"]
                
            val.append(value)
            self.save(key, val, callback)
        
        self._putCallback = _putCallback
        self.load(key, self._putCallback)


    
