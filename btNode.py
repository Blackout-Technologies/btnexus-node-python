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
from threading import Timer
import base64
import warnings



# 3rd Party imports


# local imports
from nexus.nexusConnector import *
from nexus.message import *
from nexus.btNexusMemory import BTNexusMemory
from nexus.btNexusData import BTNexusData

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

    def __init__(self, connectHash=None, packagePath=None, rcPath=None, logger=None, debug=None):
        """
        Constructor sets up the NexusConnector.

        :param token: AccessToken for the btNexus
        :type token: String
        :param axonURL: URL for the Axon(InstanceURL)
        :type axonURL: String
        :param debug: switch for debug messages
        :type debug: bool

        :param logger: a logger object to log to 
        :type logger: Logger
        :param personalityId: Id of your Personality
        :type personalityId: String
        :param integrationId: Id of the integration this Node belongs to
        :type integrationId: String
        """
        if connectHash == None:
            if "CONNECT_HASH" in os.environ:
                connectHash = os.environ["CONNECT_HASH"]
            else:
                rcPath = rcPath if rcPath else os.path.join(os.path.dirname(os.path.realpath(os.path.abspath(inspect.getfile(self.__class__)))), '.btnexusrc')
                with open(rcPath) as btnexusrc:
                    connectHash = btnexusrc.read()

        self.config = json.loads(base64.b64decode(connectHash))

        try:
            self.connectHashVersion = self.config['version']
        except KeyError:
            warnings.warn("You are using a deprecated version of the connect hash.", DeprecationWarning) #Apperently DeprecationWarnings are ignored for some reason


        
        packagePath = packagePath if packagePath else os.path.join(os.path.dirname(os.path.realpath(os.path.abspath(inspect.getfile(self.__class__)))), 'package.json')

        with open(packagePath) as jsonFile:
            self.package = json.load(jsonFile)



        self.version = self.package['version']

        self.memory = BTNexusMemory(self.config['host'], self.config['token'])
        self.data = BTNexusData(self.config['host'], self.config['token'], self.config['id'])
        
        self.disconnecting = False        
        
        if debug == None:
            if 'NEXUS_DEBUG' in os.environ:
                self.debug = True
            elif 'debug' in self.package:
                self.debug = self.package['debug']
            else:
                self.debug = False
        else:
            self.debug = debug
        
        self.nodeName = self.__class__.__name__
        # if not self.axonURL.endswith("/"):
        #     self.axonURL += "/"

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
                formatter = logging.Formatter('[NEXUS]%(name)s - %(asctime)s : %(message)s') # TODO: maybe also use levelname in a good way so that NEXUSINFO is not shown as
                formatter.format = Node.nexusFormat
                nexInfHandler.setFormatter(formatter)
                self.logger.addHandler(nexInfHandler)
            
        else: 
            self.logger = logger
        
        self.nexusConnector = NexusConnector(connectCallback=self._onConnected, parent=self, token=self.config['token'], axonURL=self.config['host'], applicationId=self.config['id'], applicationType=self.package['type'], debug=self.debug, logger=self.logger)

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

    def publish(self,group, topic, funcName, params, raises=True):
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
        :param raises: if set this raises a NexusNotConnectedException if not connected to the Nexus
        :type raises: boolean
        """
        try:
            self.nexusConnector.publish(group, topic, funcName, params)
        except NexusNotConnectedException as e:
            if raises:
                raise(e)

    def publishDebug(self, debug, raises=False):
        """
        Publish a Debug message on the btNexus if debug is active

        :param debug: A Message to send to the debug topic
        :type debug: String
        :param raises: if set this raises a NexusNotConnectedException if not connected to the Nexus
        :type raises: boolean
        """
        try:
            debug = "[{}]: {}".format(self.nodeName, debug) 
            self.nexusConnector.publishDebug(debug)
        except NexusNotConnectedException as e:
            if raises:
                raise(e)

    def publishWarning(self, warning, raises=False):
        """
        Publish a Warning message on the btNexus

        :param warning: A Message to send to the warning topic
        :type warning: String
        :param raises: if set this raises a NexusNotConnectedException if not connected to the Nexus
        :type raises: boolean        
        """
        try:
            warning = "[{}]: {}".format(self.nodeName, warning) 
            self.nexusConnector.publishWarning(warning)
        except NexusNotConnectedException as e:
            if raises:
                raise(e)

    def publishError(self, error, raises=False):
        """
        Publish a Error message on the btNexus

        :param error: A Message to send to the error topic
        :type error: String
        :param raises: if set this raises a NexusNotConnectedException if not connected to the Nexus
        :type raises: boolean        
        """
        try:
            error = "[{}]: {}".format(self.nodeName, error) 
            self.nexusConnector.publishError(error)
        except NexusNotConnectedException as e:
            if raises:
                raise(e)

    def write(self, error):
        """
        This forwards errors to the publishError function to make them visible in the btNexus

        :param error: A Message to send to the error topic
        :type error: String
        """
        self.publishError(error)

    def onError(self, error): # TODO: this needs to be implemented correctly
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
            self.logger.warning("Node is an abstract super class you need to overwrite onConnected.")
    def _onConnected(self):
        """This is used in classes that are base classes. It enables you to support the callback in a clean way without calling super. Therefore you need to call super here."""
        self.onConnected()

    def onDisconnected(self):
        """
        This will be executed after a the Node is disconnected from the btNexus - here Threads can be closed or other variables can be reset.
        """
        self.logger.log(self.NEXUSINFO, "[{}]: onDisconnected".format(self.nodeName))
    def _onDisconnected(self):
        """This is used in classes that are base classes. It enables you to support the callback in a clean way without calling super. Therefore you need to call super here."""
        self.onDisconnected()
    def setUp(self):
        """
        Implement this to handle the things, which should be done before the connection to nexus is established. This will also be called for reconnects.
        """
        self.logger.log(self.NEXUSINFO,"[{}]: setUp".format(self.nodeName))
    def _setUp(self):
        """This is used in classes that are base classes. It enables you to support the callback in a clean way without calling super. Therefore you need to call super here."""
        self.setUp()
    
    def isConnected(self):
        return self.nexusConnector.isConnected

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
        try:
            self._setUp() 
            self.nexusConnector.listen(**kwargs)
        except socketio.exceptions.ConnectionError as e: #reconnects on initial connect() if not connected to the internet
            timer = Timer(2.0, self.connect, kwargs=kwargs)
            timer.start() # This runs in a Thread and makes blocking=True invalid
            self.logger.error(str(e) + " - make sure you are connected to the Internet and the Axon on {} is running".format(self.config['host']))
            timer.join()

    def disconnect(self):
        """
        Closes the connection to the Axon
        """
        self.disconnecting = True
        self.nexusConnector.disconnect()

    def reconnect(self, **kwargs):
        self.nexusConnector.reconnect(**kwargs)

    def run(self):
        """
        DEPRECATED: Will be replaced with connect(). Is here for backwards compatibility.
        """
        if self.debug:
            self.logger.warning("You are using deprecated method run(). You should use connect()")
        self.connect()

if __name__ == '__main__':
    class Test(Node):
        def onConnected(self):
            print('Hi')
    
    test = Test(packagePath='./tests/packageIntegration.json')
    test.connect()
