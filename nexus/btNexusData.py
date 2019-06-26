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
        pass #TODO: implement

    def load(self, key, callback=None):
        pass #TODO: implement
    
    def put(self, key, value, callback=None):
        pass #TODO: implement
