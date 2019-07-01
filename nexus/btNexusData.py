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

class BTNexusData():
    """Data in the Nexus Network."""
    def __init__(self, url, token, hookId):
        """
        initialize variables for the BTPostRequests
        """
        self.url = url
        self.token = token
        self.hookId = hookId

    def save(self, key, value, callback=None):
        data = {"hookId": self.hookId, "key": key, "value": value}
        BTPostRequest("hookDataSave", data, self.token, self.url, callback).send()


    def load(self, key, callback=None):
        data = {"hookId": self.hookId, "key": key}
        BTPostRequest("hookDataLoad", data, self.token, self.url, callback).send()
    
    def put(self, key, value, callback=None):
        """This for arrays of data"""
        def _putCallback(response):
            val = []
            if "value" in response:
                if "append" in dir(response["value"]):
                    val = response["value"]
                
            val.append(value)
            self.save(key, val, callback)
        
        self._putCallback = _putCallback
        self.load(key, self._putCallback)


    
