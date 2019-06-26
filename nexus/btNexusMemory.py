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

class BTNexusMemory():
    """Memory in the Nexus Network."""
    def __init__(self, url, token):
        """
        initialize variables for the BTPostRequests
        """
        self.url = url
        self.token = token

    def addEvent(self, data, callback=None):
        """
        TODO: write
        """
        BTPostRequest("memoryDataRegister", data, self.token, self.url, callback).send()

    def removeEvent(self, data, callback=None):
        """
        TODO: write
        """
        BTPostRequest("memoryDataUnregister", data, self.token, self.url, callback).send()
