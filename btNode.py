"""Blackout Nexus node. Base class for all personality core parts"""

# System imports
import time
import json
import socket
import sys
from collections import defaultdict
import inspect
import os
from inspect import getmembers, isroutine


# 3rd Party imports


# local imports
from nexus.nexusConnector import *
from nexus.message import *

# end file header
__author__      = "Marc Fiedler"
__copyright__   = "Copyright (c)2017, Blackout Technologies"

class Node(object):
    """Blackout Nexus node"""
    NEXUSINFO = 21 #: Logging level for nexus messages
    """Logging level for nexus messages"""

    @classmethod
    def nexusFormat(cls, record):
        if record.levelno == cls.NEXUSINFO:
            record.levelname = 'NEXUSINFO'   
        return '[{}] {} - {} : {}'.format(record.levelname, record.name, record.created, record.msg)

    def __init__(self, token=None,  axonURL=None,  debug=None, logger=None):
        """
        Constructor sets up the NexusConnector.

        :param token: AccessToken for the btNexus
        :type token: String
        :param axonURL: URL for the Axon(InstanceURL)
        :type axonURL: String
        :param debug: switch for debug messages
        :type debug: bool
        """
        self.token = token
        if self.token == None:
            self.token = os.environ["TOKEN"]
        self.axonURL = axonURL
        if self.axonURL == None:
            self.axonURL = os.environ["AXON_HOST"]
        if debug == None:
            self.debug = "NEXUS_DEBUG" in os.environ
        else:
            self.debug = debug

        self.nodeName = self.__class__.__name__
        if not self.axonURL.endswith("/"):
            self.axonURL += "/"

        if not logger:
            self.logger = logging.getLogger('btNexus.{}'.format(self.nodeName))
            if self.debug:
                self.logger.setLevel(logging.DEBUG)
                # INFO Handler
                infHandler = logging.StreamHandler()
                infHandler.setLevel(logging.NOTSET)
                formatter = logging.Formatter('[%(levelname)s]%(name)s - %(asctime)s : %(message)s')
                infHandler.setFormatter(formatter)
                self.logger.addHandler(infHandler)
            else:
                self.logger.setLevel(logging.INFO)
                # NexusInfo Handler
                nexInfHandler = logging.StreamHandler()
                nexInfHandler.setLevel(self.NEXUSINFO)
                formatter = logging.Formatter()#'[NEXUS]%(name)s - %(asctime)s : %(message)s') # TODO: maybe also use levelname in a good way so that NEXUSINFO is not shown as
                formatter.format = Node.nexusFormat
                nexInfHandler.setFormatter(formatter)
                self.logger.addHandler(nexInfHandler)
            
        else: 
            self.logger = logger
        
        self.nexusConnector = NexusConnector(self.onConnected, self, self.token, self.axonURL + self.nodeName, self.debug, self.logger)

    def linkModule(self, module,group, topic):
        """
        EXPERIMENTAL
        Link a python module to the messaging service
        This makes every routine of the module accessable as callbacks over the btNexus
        the routines are checked with inspect.isroutine()

        :param module: the module to be linked
        :type module: Object
        :param group: The group the callbacks should subscribe to
        :type group: String
        :param topic: The topic on callbacks should subscribe to
        :type topic: String
        """
        # Construct a callback
        #module = ALProxy(moduleName).session().service(moduleName)
        funcs = [o for o in getmembers(module) if isroutine(o[1]) and not o[0].startswith('__')] # contains all functions if it is a module and all methods if it is an object except for the ones starting with a double underscore
        # tuples of the name and the function
        for funcName, func in funcs:
            self.subscribe(group, topic, func, funcName)
            

    def subscribe(self, group, topic, callback, funcName=None):
        """
        Subscribe to a group & topic with a callback

        :param group: Name of the group
        :type group: String
        :param topic: Name of the topic
        :type topic: String
        :param callback: function pointer to the callback
        :type callback: function pointer
        :param funcName: Name of the function. If not set this is the name of the function in the implementation(needed if you want to link a function to a different name)
        :type funcName: String
        """
        self.nexusConnector.subscribe(group, topic, callback, funcName = funcName)

    def publish(self,group, topic, funcName, params):
        """
        publishes a Message with the payload(funcName and params) to a topic.

        :param group: Name of the group
        :type group: String
        :param topic: Name of the topic
        :type topic: String
        :param funcName: Name of the function.
        :type funcName: String
        :param params: The parameters for the callback
        :type params: List or keywordDict
        """
        if type(topic) != str:
            self.publishError("Topic needs to be a String. Is of type {}".format(type(topic)))
            return
        if type(funcName) != str:
            self.publishError("FuncName needs to be a String. Is of type {}".format(type(funcName)))
            return
        if type(params) == list or type(params) == dict:
            pass
        else:
            self.publishError("params needs to be a list of parameters or keywordDict. Is of type {}".format(str(type(params))))
            return

        info = Message("publish")
        info["topic"] = "ai.blackout." + topic
        info["payload"] = {funcName:params}
        info["host"] = socket.gethostname()
        info["group"] = group
        self.nexusConnector.publish(info)

    def publishDebug(self, debug):
        """
        Publish a Debug message on the btNexus if debug is active

        :param debug: A Message to send to the debug topic
        :type debug: String
        """
        debug = "Class: " + self.__class__.__name__ + " " + debug.__class__.__name__ + ": " + str(debug)
        self.nexusConnector.publishDebug(debug)

    def publishWarning(self, warning):
        """
        Publish a Warning message on the btNexus

        :param warning: A Message to send to the warning topic
        :type warning: String
        """
        warning = "Class: " + self.__class__.__name__ + " " + warning.__class__.__name__ + ": " + str(warning)
        self.nexusConnector.publishWarning(warning)

    def publishError(self, error):
        """
        Publish a Error message on the btNexus

        :param error: A Message to send to the error topic
        :type error: String
        """
        error = "Class: " + self.__class__.__name__ + " " + error.__class__.__name__ + ": " + str(error)
        self.nexusConnector.publishError(error)

    def write(self, error):
        """
        This forwards errors to the publishError function to make them visible in the btNexus

        :param error: A Message to send to the error topic
        :type error: String
        """
        self.publishError(error)

    def onError(self, error):
        """
        Handling of Errors. If not overloaded it just forwards the error to the nexusConnector which just prints and publishes it if possible
        """
        self.nexusConnector.onError(None, "[{}] Error: {}".format(self.nodeName, error))

    def onConnected(self):
        """
        Is called when this node was connected
        This needs to be overloaded to subscribe to messages.
        """
        if self.debug:
            self.logger.warning("You are using deprecated method nodeConnected(). You should use onConnected()")
        self.nodeConnected()

    def onDisconnected(self):
        """
        This will be executed after a the Node is disconnected from the btNexus - here Threads can be closed or other variables can be reset.
        """
        self.logger.log(self.NEXUSINFO, "[{}]: onDisconnected".format(self.nodeName))

    def setUp(self):
        """
        Implement this to handle the things, which should be done before the connection to nexus is established. This will also be called for reconnects.
        """
        self.logger.log(self.NEXUSINFO,"[{}]: setUp".format(self.nodeName))

    # Can be handled by onDisconnected
    # def cleanUp(self):
    #     """
    #     Implement this to handle the things, which should be done when you disconnect the node.
    #     """
    #     self.logger.info("[{}]: cleanUp".format(self.nodeName))

    def connect(self, **kwargs): 
        """
        Runs this node and listen forever
        This is a blocking call
        Uses the kwargs for the socketio.Client see https://python-socketio.readthedocs.io/en/latest/api.html
        """
        self.setUp() 
        self.nexusConnector.listen(**kwargs)

    def disconnect(self):
        """
        Closes the connection to the Axon
        """
        self.nexusConnector.disconnect()

    def run(self):
        """
        DEPRECATED: Will be replaced with connect(). Is here for backwards compatibility.
        """
        if self.debug:
            self.logger.warning("You are using deprecated method run(). You should use connect()")
        self.connect()
