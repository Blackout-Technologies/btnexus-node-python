"""Messages that obey the blackout protocol, can use this class"""

# System imports
import os
import socket#, _thread
import time
import json, uuid
import traceback
import sys, io
import logging
from collections import defaultdict
import ssl
import certifi
from threading import Thread



# 3rd party imports
import socketio

# local imports
# from .btWebsocket import *
# # from websocket import *
from .message import Message
from .nexusExceptions import *

# end file header
__author__      = "Marc Fiedler, Gheorghe Lisca, Adrian Lubitz"
__copyright__   = "Copyright (c)2017, Blackout Technologies"


class NexusConnector(object):
    """The NexusConnector handles everything from connecting, subscibing and publishing messages in the btNexus"""
    version = "4.0"
    

    def __init__(self, connectCallback, parent,  token,  axonURL,  debug, logger):
        """
        Sets up all configurations.

        :param connectCallback: function pointer to the onConnected of the Node using this NexusConnector
        :type connectCallback: function pointer
        :param parent: The Node using this NexusConnector (also used for some logging stuff)
        :type parent: Node
        :param token: AccessToken for the btNexus
        :type token: String
        :param axonURL: URL for the Axon(InstanceURL)
        :type axonURL: String
        :param debug: switch for debug messages
        :type debug: bool
        :param logger: You can give a logger if you want otherwise the 'btNexus' Logger is used
        :type logger: logging.Logger
        """
        #Set env for certs if not set
        os.environ["WEBSOCKET_CLIENT_CA_BUNDLE"] = certifi.where()
        self.debugTopic = "ai.blackout.debug"
        self.warningTopic = "ai.blackout.warning"
        self.errorTopic = "ai.blackout.error"
        self.parent = parent
        self.parentName = self.parent.nodeName
        self.nodeId = None #str(uuid.uuid4())
        self.protocol = "wss" 
        self.token = token
        self.axon = axonURL
        self.debug = debug


        self.wsConf = self.protocol + "://"+ str(self.axon)

        self.logger = logger


        self.connectCallback = connectCallback
        self.callbacks = defaultdict(lambda: defaultdict(dict)) # saves every callback under a group and a topic, even if joining the group wasnt successufull(Messages will be filtered by the Axon)

        self.isConnected = False
        self.isRegistered = False


    def __onConnected(self):
        """
        Shadow function for the connectCallback
        """
        self.connectCallback()
        self.logger.log(self.parent.NEXUSINFO, "{} succesfully started :)".format(self.parentName))

    def callbackManager(self, msg):
        """
        Links the Message to the corrosponding Callback

        :param msg: Incoming Message from the btNexus
        :type msg: Message
        """
        try:
            topic = msg["topic"].replace("ai.blackout.", "")
            callbackName = list(msg["payload"].keys())[0]
            params = msg["payload"][callbackName]
            group = msg["group"]
            if callbackName in self.callbacks[group][topic].keys():
                Thread(target=self.executeCallback, args=(group, topic, callbackName, params)).start()
                #self.executeCallback(group, topic, callbackName, params)
            else:
                error = NoCallbackFoundException("Callback {} doesn't exist in node {} on topic {} in group {}".format(callbackName, self.parentName, topic, group))
                self.publishDebug(str(error))
                return error
        except Exception as e:
            error = NoCallbackFoundException(str(e))
            self.publishError(str(error))
            return error

    def executeCallback(self, group, topic, callbackName, params):
        """
        This executes the given callback with the given params and send the response

        :param group: Name of the group
        :type group: String
        :param topic: Name of the topic
        :type topic: String
        :param callbackName: Name of the callback
        :type callbackName: String
        :param params: the params for the callback either as list or keywordDict
        :type params: list or keywordDict
        """
        if type(params) == list:
            retVal = self.callbacks[group][topic][callbackName](*params)
        elif type(params) == dict:
            retVal = self.callbacks[group][topic][callbackName](**params)
        else:
            self.publishError("Parameters can either be given as a list or a keywordDict.")
            return

        reply = Message("publish")
        reply["payload"] = {callbackName + "_response":{"orignCall":callbackName ,"originParams":params, "returnValue": retVal}}
        reply["topic"] = "ai.blackout." + topic
        reply["group"] = group
        reply["host"] = socket.gethostname()
        self.publish(reply)

    def setDebugMode(self, mode):
        """
        Activate/Deactivate the Debug 
        """
        self.debug = mode

    def listen(self, **kwargs): # TODO: is it possible to use kwargs twice? - for init() and connect()?
        """Start listening on Websocket communication"""
        # SSLOPTS
        ssl_verify = not "DISABLE_SSL_VERIFY" in os.environ
        self.reconnect = kwargs['reconnection'] if 'reconnection' in kwargs else True
        self.sio = socketio.Client(ssl_verify=ssl_verify, logger=self.logger, **kwargs)
        self.defineCallbacks()
        _reconnect = True
        while(_reconnect):
            _reconnect = self.reconnect # Do While
            try:
                self.sio.connect(self.wsConf)
                self.sio.wait()
            except socketio.exceptions.ConnectionError as e:
                if self.reconnect:
                    self.logger.error(str(e) + " - make sure you are connected to the Internet and the Axon on {} is running".format(self.axon.split('/')[0]))
                    time.sleep(5)
                else:
                    raise e

    def disconnect(self):
        """
        Closes the connection to the Axon
        """
        self.onDisconnected()
        self.sio.disconnect()

    def join(self, group):
        """
        Join a specific group

        :param group: Name of the group
        :type group: String
        """
        join = Message("join")
        join["groupName"] = group
        self.publish(join)

    def leave(self, group):
        """
        leave a specific group

        :param group: Name of the group
        :type group: String
        """
        leave = Message('leave')
        leave["groupName"] = group
        self.publish(leave)

    def subscribe(self, group, topic, callback, funcName = None):
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
        if not self.isConnected:
            raise NexusNotConnectedException()
        if group not in self.callbacks:
            self.join(group)
        if topic not in self.callbacks[group]: #first subscribtion
            sub = Message("subscribe")
            sub["topic"] = "ai.blackout.{}".format(topic)
            self.publish(sub)
        if funcName == None:
            funcName = callback.__name__
        self.callbacks[group][topic][funcName] = callback

    def unsubscribe(self, group, topic):
        """
        unsubscribe from a group & topic

        :param group: Name of the group
        :type group: String
        :param topic: Name of the topic
        :type topic: String
        """
        self.callbacks[group][topic] = {}

    def publish(self, message):
        """
        Publish a message on the btNexus

        :param message: A Message to send into the btNexus
        :type message: Message
        """
        # Add the node id as a source to that this node does not receive its own
        # messages

        message['nodeId'] = self.nodeId
        if self.isConnected:
            self.sio.emit('message', message.getJsonContent())
        else:
            raise NexusNotConnectedException()

    def publishDebug(self, debug):
        """
        Publish a Debug message on the btNexus if debug is active

        :param debug: A Message to send to the debug topic
        :type debug: String
        """
        if self.debug:
            self.logger.debug(debug)
            deb = Message("publish")
            deb["group"] = "blackout-global"
            deb["topic"] = self.debugTopic
            deb["payload"] = {"debug":debug}
            self.publish(deb)


    def publishWarning(self, warning):
        """
        Publish a Warning message on the btNexus

        :param warning: A Message to send to the warning topic
        :type warning: String
        """
        self.logger.warning(warning)
        warn = Message("publish")
        warn["group"] = "blackout-global"
        warn["topic"] = self.warningTopic
        warn["payload"] = {"warning":warning}
        self.publish(warn)

    def publishError(self, error):
        """
        Publish a Error message on the btNexus

        :param error: A Message to send to the error topic
        :type error: String
        """
        self.logger.error(error)
        err = Message("publish")
        err["group"] = "blackout-global"
        err["topic"] = self.errorTopic
        err["payload"] = {"error":error}
        self.publish(err)

    def onMessage(self, message):
        """
        React on a incoming Message and decide what to do.

        :param message: The message to react on
        :type message: String
        """
        msg = Message()
        msg.loadFromJsonString(message)
        if( msg["api"]["intent"] == "registerSuccess" ):
            self.logger.log(self.parent.NEXUSINFO, "[{}]: Registered successfully".format(self.parentName))
            self.isRegistered = True
            self.__onConnected()
            #TODO: check here for versionmissmatch - just like in java
        elif ( msg["api"]["intent"] == "registerFailed" ):
            self.logger.log(self.parent.NEXUSINFO, "[{}]: Register failed with reason: {}".format(self.parentName, msg["reason"]))
        elif( msg["api"]["intent"] == "subscribeSuccess" ):
            self.logger.log(self.parent.NEXUSINFO, "[{}]: Subscribed to: {}".format(self.parentName, msg["topic"]))
        elif ( msg["api"]["intent"] == "subscribeFailed" ):
            self.logger.log(self.parent.NEXUSINFO, "[{}]: Failed to Subscribed to: {}".format(self.parentName, msg["topic"]))
        elif ( msg["api"]["intent"] == "joinSuccess" ):
            self.logger.log(self.parent.NEXUSINFO, "[{}]: Joined Group: {}".format(self.parentName, msg["groupName"]))
        elif ( msg["api"]["intent"] == "joinFailed" ):
            self.logger.log(self.parent.NEXUSINFO, "[{}]: Failed to join Group: {}".format(self.parentName, msg["groupName"]))
        elif ( msg["api"]["intent"] == "leaveSuccess" ):
            self.logger.log(self.parent.NEXUSINFO, "[{}]: Left Group: {}".format(self.parentName, msg["groupName"]))
        elif ( msg["api"]["intent"] == "leaveFailed" ):
            self.logger.log(self.parent.NEXUSINFO, "[{}]: Failed to leave Group: {}".format(self.parentName, msg["groupName"]))
        elif ( msg["api"]["intent"] == "unsubscribeSuccess" ):
            self.logger.log(self.parent.NEXUSINFO, "[{}]: Unsubscribed from topic: {}".format(self.parentName, msg["topic"]))
        elif ( msg["api"]["intent"] == "unsubscribeFailed" ):
            self.logger.log(self.parent.NEXUSINFO, "[{}]: Failed to unsubscribe from topic: {}".format(self.parentName, msg["topic"]))
        else:
            # Interaction is only allowed with registered nodes
            if( self.isRegistered ):
                try:
                    # Call topic callback with this message
                    self.callbackManager(msg)
                except Exception:
                    self.publishError(traceback.format_exc())

    def onDisconnected(self):
        self.callbacks = defaultdict(lambda: defaultdict(dict))
        self.isConnected = False
        self.isRegistered = False
        self.logger.log(self.parent.NEXUSINFO, "Connection closed")
        self.parent.onDisconnected()
        if self.reconnect:
            self.parent.setUp()

    def defineCallbacks(self):
        @self.sio.event
        def connect():
            self.logger.log(self.parent.NEXUSINFO, 'connection established')
            self.isConnected = True
            self.sio.emit('ping', {})
        
        @self.sio.on('btnexus-registration')
        def register(data):
            self.nodeId = data['nodeId']
            msg = Message("register")
            msg["token"] = self.token 
            msg["host"] = socket.gethostname()
            msg["ip"] = "127.0.0.1" #socket.gethostbyname(socket.gethostname())
            msg["id"] = self.nodeId
            msg["node"] = {}    #TODO: What should be in this field?
            self.publish(msg)
        
        @self.sio.on('message')
        def onMessage(data):
            self.onMessage(data)

        @self.sio.event
        def connect_error():
            self.logger.log(self.parent.NEXUSINFO, "The connection failed!")

        @self.sio.event
        def disconnect():
            self.onDisconnected()
        
        # @self.sio.event
        # def reconnect():
        #     pass


        @self.sio.on('pong')
        def onPong(data):
            self.logger.info('[PONG]{}'.format(data))
        
        @self.sio.on('ping')
        def onPing(data):
            self.sio.emit('pong', {})
            self.logger.info('[PING]: {}'.format(data))
