"""Blackout Nexus hook. Base class for all hooks"""
# System imports
import os
import base64
import json
import sys
if sys.version_info.major == 2:
    from urlparse import urlsplit
else:
    from urllib.parse import urlsplit

# 3rd Party imports
from btNode import Node # have it like this so it will still be possible to seperate it into its own package

# local imports
from nexus.btNexusMemory import BTNexusMemory
from nexus.btNexusData import BTNexusData


# end file header
__author__      = "Adrian Lubitz"
__copyright__   = "Copyright (c)2017, Blackout Technologies"
__version__     = "0.6.3"


class Hook(Node):
    """
    Blackout Nexus hook. Base class for all hooks
    """
    def __init__(self, connectHash = None, **kwargs):
        """
        Constructor for the hook.
        extracting all important infos from the connectHash
        (either given via environment variable as parameter, CONNECT_HASH or in the .btnexusrc(priritized in this order))
        """
        #get connectHash
        self.initKwargs = kwargs
        if connectHash == None:
            if "CONNECT_HASH" in os.environ:
                connectHash = os.environ["CONNECT_HASH"]
            else:
                with open(".btnexusrc") as btnexusrc:
                    connectHash = btnexusrc.read()

        #extract config
        self.config = json.loads(base64.b64decode(connectHash))

        #call super constructor with axon and token set
        self.token = self.config["token"]
        self.host = urlsplit(self.config["host"]).netloc
        if not self.host:
            self.host = self.config["host"] # backwardscompatibility

        self.memory = BTNexusMemory("https://" + self.host, self.token)
        self.data = BTNexusData("https://" + self.host, self.token, self.config['id'])
        super(Hook, self).__init__(self.token, self.host)
        self.onInit(**kwargs)
        self.connect()


    def onConnected(self):
        """
        Setup all Callbacks
        """
        
        self.memory.addEvent(self.memoryData)
        # Join complete
        self.subscribe(self.config["id"], 'hookChat', self._onMessage, "onMessage") 

        self.subscribe(self.config["id"], "state", self.state)
        self.readyState = "ready"
        self.state()

        self.onReady(**self.initKwargs)



    def state(self):
        self.publish(self.config["id"], self.config["id"], 'state', {
            'hookId': self.config["id"],
            'state': self.readyState
        })

    def _onMessage(self, **kwargs):
        """
        Forwards the correct params to onMessage
        """

        self.onMessage(originalTxt=kwargs["text"]["original"], 
                        intent=kwargs["intent"], 
                        language=kwargs["language"], 
                        entities=kwargs["entities"], 
                        slots=kwargs["slots"], 
                        branchName=kwargs["branch"]["name"], 
                        peer=kwargs)#TODO: what is needed peer? only needs infos to indentify message origin

    def onMessage(self, originalTxt, intent, language, entities, slots, branchName, peer):
        """
        Overload for your custum hook! - it needs to trigger say

        
        React on a message forwarded to the hook.

        :param originalTxt: the original text
        :type originalTxt: String
        :param intent: the classified intent
        :type intent: String
        :param language: the (classified) language
        :type language: String
        :param entities: List of used entities
        :type entities: List of (String)
        :param slots: List of used slots
        :type slots: List of (String)
        :param branchName: Name of the Branch
        :type branchName: String
        :param peer: param to indentify message origin
        :type peer: dict
        
        """
        pass
        self.say(peer, "Hook needs to overload onMessage")

    def say(self, peer, message):
        """
        publishes the hooks response.

        :param originalTxt: the original text
        :type originalTxt: String
        """
        peer["message"] = {'answer':message}
        self.publish(peer["personalityId"], 'chat', 'hookResponse', peer)



    def onReady(self, **kwargs):
        """
        Initilize what you need after the hook connected - you can pass kwargs in the constructor to use them here
        """
        if kwargs:
            print("onReady with params: {}".format(kwargs))
    
    def onInit(self, **kwargs):
        """
        Initilize what you need after the hook connected - you can pass kwargs in the constructor to use them here
        """
        if kwargs:
            print("onInit with params: {}".format(kwargs))


    def setUp(self):
        self.memoryData = {
                'service': "hook",
                'context': self.config['id'],
                'version': __version__
                }
        

    def cleanUp(self):
        self.memory.removeEvent(self.memoryData)

        

if __name__ == "__main__":
    h = Hook(test="TestParam")