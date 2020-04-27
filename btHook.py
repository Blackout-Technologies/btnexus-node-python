"""Blackout Nexus hook. Base class for all hooks"""
# System imports
import os
import base64
import json
import sys
import inspect
import warnings
if sys.version_info.major == 2:
    from urlparse import urlsplit
else:
    from urllib.parse import urlsplit

# 3rd Party imports
from btNode import Node # have it like this so it will still be possible to seperate it into its own package

# local imports

from nexus.btCaptions import BTCaptions
from nexus.hookSettings import HookSettings


# end file header
__author__      = "Adrian Lubitz"
__copyright__   = "Copyright (c)2017, Blackout Technologies"


class Hook(Node):
    """
    Blackout Nexus hook. Base class for all hooks
    """
    def __init__(self, settingsPath=None, **kwargs):
        """
        Constructor for the hook.
        extracting all important infos from the connectHash
        (either given as parameter, via environment variable CONNECT_HASH or in the .btnexusrc(prioritized in this order))
        """
        super(Hook, self).__init__(**kwargs)
        captionsPath = os.path.join(os.path.dirname(os.path.realpath(os.path.abspath(inspect.getfile(self.__class__)))), 'captions.json')
        self.captions = BTCaptions(captionsPath) # TODO: add some docstring to be visibile in the docu
        if not settingsPath:
            settingsPath = os.path.join(os.path.dirname(os.path.realpath(os.path.abspath(inspect.getfile(self.__class__)))), 'settings.json')
        with open(settingsPath) as jsonFile:
            data = json.load(jsonFile)
            self.defaultSettings = {}
            for setting in data:
                self.defaultSettings[setting] = data[setting]["default"]

    def getDefaultSettings(self):
        """
        Returns the default settings for the hook from the settings.json file - these can be used for local debugging. 
        In production hooks the settings will be transmitted in onMessage
        """
        return self.defaultSettings

    # def onSettingsUpdated(self):
    #     """
    #     Is called when settings are updated/changed from the instance UI
    #     This needs to be overloaded.
    #     """
    #     if self.debug:
    #         self.logger.warning("Hook is an abstract super class you need to overwrite onSettingsUpdated.")

    def getCaption(self, lang, key):
        """
        Returns a phrase from the captions file. If a list of phrases is given in the captions file one is chosen randomly. If only a String is given it returns this. 

        :param lang: the requested language
        :type lang: String
        :param key: key for a specific phrase
        :type key: String
        """
        return self.captions.getPhrase(lang, key)


    def _onConnected(self):
        """
        Setup all Callbacks
        """
        self.memory.addEvent(self.memoryData)
        # Join complete
        self.subscribe(self.config["id"], 'hookChat', self._onMessage, "hookRequest") 

        self.subscribe(self.config["id"], "state", self.state)
        self.readyState = "ready"
        self.state()
        super(Hook, self)._onConnected()


    def state(self):
        """
        publish the state of the hook
        """
        self.publish(self.config["id"], self.config["id"], 'state', {
            'hookId': self.config["id"],
            'state': self.readyState
        })

    def _onMessage(self, **kwargs):
        """
        Forwards the correct params to onMessage.
        This method is just for internal use.
        """     
        self.onMessage(originalTxt=kwargs["text"] if 'text' in kwargs else None, 
                        intent=kwargs["intent"] if 'intent' in kwargs else None, 
                        language=kwargs["language"] if 'language' in kwargs else None, 
                        entities=kwargs["entities"] if 'entities' in kwargs else None, 
                        slots=kwargs["slots"] if 'slots' in kwargs else None, 
                        branchName=kwargs["branch"] if 'branch' in kwargs else None, 
                        peer=kwargs['sessionId'] if 'sessionId' in kwargs else None, 
                        settings=kwargs['settings'] if 'settings' in kwargs else None)
        

    def onMessage(self, originalTxt, intent, language, entities, slots, branchName, peer, settings):
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
        :type peer: String
        :param settings: settings for this hook made in the instance
        :type settings: dict
        
        """
        self.say(peer, {'answer':"Hook needs to overload onMessage"})  # if not overloaded this is what your hook will say

    def say(self, peer, message): 
        """
        publishes the hooks response.

        :param message: the message dict with at least the field 'answer'
        :type message: dict
        :param peer: the peer object handed from onMessage
        :type peer: Object
        """
        # peer["message"] = message
        # self.publish(group=self.config['id'], topic=peer, funcName='answer', params= {"Hello": "world"}) #TODO: this is not the way it should be - params should be the whole message with answr, hyperrefs...
        
        if type(message) == str:
            message = {'answer':message}
        self.publish(group=self.config['id'], topic=peer, funcName='hookResponse', params=message)

    def _setUp(self):
        """
        Register the hook in the system
        """
        self.memoryData = {
                'service': "hook",
                'context': self.config['id'],
                'version': self.version  
                }
        super(Hook, self)._setUp()
        

    def _onDisconnected(self):
        """
        Unregister the hook and send exit state
        """
        self.memory.removeEvent(self.memoryData)
        self.readyState = 'exit'
        # self.state() # TODO: this cant work - how should the state be sent if the Hook is no longer connected...?
        super(Hook, self)._onDisconnected()

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
        self.data.save(key, value, callback)

    def load(self, key, callback=None):
        """
        load a value to a specific key in the NexusData Api

        :param key: the key to which the value should be saved
        :type key: String
        :param callback: callback to handle the api response
        :type callback: function pointer
        """
        self.data.load(key, callback)
        
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

        self.data.put(key, value, callback)
        

if __name__ == "__main__":
    h = Hook(test="TestParam")