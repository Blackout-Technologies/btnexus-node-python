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
from btPostRequest import BTPostRequest

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
    

    def __init__(self, connectCallback, parent,  token,  axonURL, applicationId, applicationType, debug, logger, hostId, **kwargs):
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
        self.parent = parent
        self.parentName = self.parent.nodeName
        self.nodeId = None #str(uuid.uuid4())
        # self.protocol = "wss" 
        self.token = token
        self.axon = axonURL
        self.applicationId = applicationId
        self.applicationType = applicationType
        self.rootTopic = "ai.blackout."
        self.hostId = hostId

        if not '://' in self.axon:
            raise NoProtocolException(self.axon)

        self.debug = debug


        # self.wsConf = self.protocol + "://"+ str(self.axon)

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
            topic = msg["topic"].replace(self.rootTopic, "")
            callbackName = list(msg["payload"].keys())[0] # here we could also think about running more than one callback
            params = msg["payload"][callbackName]
            group = msg["group"]
            if callbackName in self.callbacks[group][topic].keys():
                Thread(target=self.executeCallback, args=(group, topic, callbackName, params)).start()
            else:
                error = NoCallbackFoundException("Callback {} doesn't exist in node {} on topic {} in group {}".format(callbackName, self.parentName, topic, group))
                self.logger.debug(str(error))
                return error
        except IndexError:
            self.publishError("ProtocolError: One key needs to be in payload field of message. Got {}".format(msg))
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
        self.publish(group=group, topic=topic, funcName=callbackName + "_response", params={"orignCall":callbackName ,"originParams":params, "returnValue": retVal})

    def setDebugMode(self, mode):
        """
        Activate/Deactivate the Debug 
        """
        self.debug = mode

    def listen(self, blocking = True, **kwargs): 
        """Start listening on Websocket communication"""
        self.listenKwargs = kwargs
        # SSLOPTS
        ssl_verify = not "DISABLE_SSL_VERIFY" in os.environ
        self.reconnection = kwargs['reconnection'] if 'reconnection' in kwargs else True
        self.sio = socketio.Client(ssl_verify=ssl_verify, logger=self.logger, **kwargs)
        self.defineCallbacks()
        socketioURL = self.axon + '?instance=' + self.hostId
        self.sio.connect(socketioURL, namespaces=["/{}".format(self.hostId)])
        if blocking:
            self.sio.wait() # This waits until disconnect

    def disconnect(self):
        """
        Closes the connection to the Axon
        """
        self.onDisconnected()
        self.sio.disconnect()

    def reconnect(self, **kwargs):
        self.disconnect()
        for arg in kwargs:
            self.listenKwargs[arg] = kwargs[arg] # overwrite kwargs given as parameter - otherwise take the ones from the connect
        self.listen(blocking=False, **self.listenKwargs) # a reconnect should never be blocking

    def join(self, group):
        """
        Join a specific group

        :param group: Name of the group
        :type group: String
        """
        if not group in self.callbacks:
            if self.isRegistered:
                join = Message(intent="join", group=group)
                self.sio.emit('btnexus-join', join.getJsonContent(), namespace="/{}".format(self.hostId))
                self.callbacks[group] # Because this is a defaultdict only trying to access the group creates a dafaultdict(dict) for this key
            else:
                self.logger.debug("[{}]: Couldn't join - not registered!".format(self.parentName))

    def leave(self, group):
        """
        leave a specific group

        :param group: Name of the group
        :type group: String
        """
        if self.isRegistered:
            leave = Message('leave', group=group)
            self.sio.emit('btnexus-leave', leave.getJsonContent(), namespace="/{}".format(self.hostId))
        else:
            self.logger.debug("[{}]: Couldn't leave - not registered!".format(self.parentName))

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
        self.join(group)
        if funcName == None:
            funcName = callback.__name__
        self.sio.on(self.rootTopic + topic, self.onMessage, namespace="/{}".format(self.hostId))
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

    def publish(self, group, topic, funcName, params):
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
        # Add the node id as a source to that this node does not receive its own
        # messages


        if type(params) == list or type(params) == dict:
            pass
        else:
            self.publishError("params needs to be a list of parameters or keywordDict. Is of type {}".format(str(type(params))))
            return
        self.join(group)
        info = Message(intent="publish", group=group, topic=self.rootTopic + topic)
        info["payload"] = {funcName:params}
        info["host"] = socket.gethostname()
        info['nodeId'] = self.nodeId
        if self.isConnected and self.isRegistered:
            self.sio.emit('btnexus-publish', info.getJsonContent(), namespace="/{}".format(self.hostId))
        else:
            raise NexusNotConnectedException()

    def publishDebug(self, debug):
        """
        Publish a Debug message on the btNexus if debug is active

        :param debug: A Message to send to the debug topic
        :type debug: String
        """
        if self.debug:
            self.logger.log(self.parent.NEXUSINFO, debug)
            self.publish('blackout-global', 'debug', 'debug', [debug])

    def publishWarning(self, warning):
        """
        Publish a Warning message on the btNexus

        :param warning: A Message to send to the warning topic
        :type warning: String
        """
        self.logger.warning(warning)
        self.publish('blackout-global', 'warning', 'warning', [warning])

    def publishError(self, error):
        """
        Publish a Error message on the btNexus

        :param error: A Message to send to the error topic
        :type error: String
        """
        self.logger.error(error)
        self.publish('blackout-global', 'error', 'error', [error])
    

    def onMessage(self, message):
        """
        React on a incoming Message and decide what to do.

        :param message: The message to react on
        :type message: String
        """
        msg = Message()
        msg.loadFromJson(message)

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
        self.parent._onDisconnected()
        if self.reconnection:
            if not self.parent.disconnecting:
                self.parent._setUp()

    def setSessionId(self, response):
        if response['success']:
            self.nodeId = self.registerData['nodeId'] 
            sessionId = response['sessionId']
            msg = Message("register")
            msg["sessionId"] = sessionId 
            msg["host"] = socket.gethostname()
            msg["ip"] = "127.0.0.1" #socket.gethostbyname(socket.gethostname())
            msg["id"] = self.nodeId
            msg["node"] = {}    #TODO: What should be in this field?
            self.sio.emit('btnexus-registration', msg.getJsonContent(), namespace="/{}".format(self.hostId))
        else:
            try:
                self.publishError('Error getting sessionId: {}\t - retrying in 2 seconds'.format(response['error']))
            except NexusNotConnectedException:
                pass # just log the error if not connected which is likely, because can only connect with sessionId
            except KeyError:
                self.publishError('SessionAccessRequest response in wrong format: {}'.format(response))
            except Exception as e:
                self.publishError(str(e))
            time.sleep(2)
            self.getSessionId()
    
    def getSessionId(self, error = None):
        params = {
                'applicationId': self.applicationId,
                'applicationType': self.applicationType
                }
        if error:
            try:
                self.publishError("Error getting the sessionId: {}".format(error))
            except NexusNotConnectedException:
                pass # only log if not connected
            time.sleep(2)
        BTPostRequest('applicationAccessRequest', params, accessToken=self.token, url=self.axon, callback=self.setSessionId, errBack=self.getSessionId).send() # TODO: add Errback 

    def defineCallbacks(self):
        @self.sio.event(namespace="/{}".format(self.hostId))
        def connect():
            self.logger.log(self.parent.NEXUSINFO, 'connection established')
            self.isConnected = True
        
        @self.sio.on('btnexus-registration', namespace="/{}".format(self.hostId))
        def register(data):
            self.registerData = data
            if data['api']['intent'] == 'requestRegistration':
                self.getSessionId() # TODO: add try! or Add the Errback!
            elif data['api']['intent'] == 'registrationResult':
                if data['success']:
                    self.isRegistered = True
                    self.__onConnected()
                else:
                    self.isRegistered = False
                    self.logger.error("[{}]: Failed to register to the axon: {}".format(self.parentName, data["error"]))                

        @self.sio.event(namespace="/{}".format(self.hostId))
        def connect_error():
            self.logger.log(self.parent.NEXUSINFO, "The connection failed!")

        @self.sio.event(namespace="/{}".format(self.hostId))
        def disconnect(reason=None):
            if reason:
                self.logger.log(self.parent.NEXUSINFO, "Disconnected due to '{}'".format(reason))
            self.onDisconnected()


        @self.sio.on('pong', namespace="/{}".format(self.hostId))
        def onPong(data):
            self.logger.info('[PONG]{}'.format(data))
        
        @self.sio.on('ping', namespace="/{}".format(self.hostId))
        def onPing(data):
            self.sio.emit('pong', {}, namespace="/{}".format(self.hostId))
            self.logger.info('[PING]: {}'.format(data))
