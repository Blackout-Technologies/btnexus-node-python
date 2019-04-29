"""Blackout Nexus node. Base class for all personality core parts"""

# System imports
import time
import json
import socket
import sys
from collections import defaultdict
import inspect
import os

# 3rd Party imports


# local imports
from nexus.nexusConnector import *
from nexus.message import *

# end file header
__author__      = "Marc Fiedler"
__copyright__   = "Copyright (c)2017, Blackout Technologies"

class Node(object):
    """Blackout Nexus node"""

    def __init__(self, token=None,  axonURL=None,  debug=None):
        """
        Constructor sets up the NexusConnector.

        :param token: AccessToken for the btNexus
        :type token: String
        :param axonURL: URL for the Axon(InstanceURL)
        :type axonURL: String
        :param debug: switch for debug messages
        :type debug: bool
        """
        if token == None:
            token = os.environ["TOKEN"]
        if axonURL == None:
            axonURL = os.environ["AXON_HOST"]
        if debug == None:
            self.debug = "NEXUS_DEBUG" in os.environ

        self.nodeName = self.__class__.__name__
        if not axonURL.endswith("/"):
            axonURL += "/"
        axonURL += self.nodeName
        self.nexusConnector = NexusConnector(self.onConnected, self, token, axonURL, self.debug)

    def linkModule(self, module,group, topic):
        """
        EXPERIMENTAL
        Link a python object to the messaging service
        This makes every method of the object accessable as callbacks over the btNexus

        :param module: the module to be linked
        :type module: Object
        :param group: The group the callbacks should subscribe to
        :type group: String
        :param topic: The topic on callbacks should subscribe to
        :type topic: String
        """
        # Construct a callback
        #module = ALProxy(moduleName).session().service(moduleName)
        for func in module.__dict__:
            self.subscribe(group, topic, module.__dict__[func], func)

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
            print("You are using deprecated method nodeConnected(). You should use onConnected()")
        self.nodeConnected()

    def onDisconnected(self):
        """
        This will be executed after a the Node is disconnected from the btNexus
        If not implemented the Node tries to reconnect
        """
        pass #TODO: use setup and cleanup here
        self.cleanUp()
        self.setUp()
        self.nexusConnector = NexusConnector.copyNexusForReconnect(self.nexusConnector) #here
        time.sleep(1)
        self.nexusConnector.listen()

    def setUp(self):
        """
        Implement this to handle the things, which should be done before the connection to nexus is established.
        """
        print("[{}]: setUp".format(self.nodeName))

    def cleanUp(self):
        """
        Implement this to handle the things, which should be when you disconnect the node.
        """
        print("[{}]: cleanUp".format(self.nodeName))

    def connect(self):
        """
        Runs this node and listen forever
        This is a blocking call
        """
        self.setUp()
        self.nexusConnector.listen()

    def run(self):
        """
        DEPRECATED: Will be replaced with connect(). Is here for backwards compatibility.
        """
        if self.debug:
            print("You are using deprecated method run(). You should use connect()")
        self.connect()
