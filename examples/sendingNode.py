"""Example for a Node that sends out messages"""
# System imports
from threading import Thread
import datetime
import time
import os
# 3rd party imports
from btNode import Node

# local imports

class SendingNode(Node):
    """
    This Node shows how to implement an active Node which sends different Messages
    """
    def onConnected(self):
        """
        This will be executed after a the Node is succesfully connected to the btNexus
        Here you need to subscribe and set everything else up.

        :returns: None
        """
        self.shouldRun = True
        self.subscribe(group="exampleGroup",topic="example", callback=self.fuseTime_response) # Here we subscribe to the response of messages we send out to fuseTime
        self.thread = Thread(target=self.mainLoop)
        self.thread.start() # You want to leave this method so better start everything which is actively doing something in a thread.
    def fuseTime_response(self, orignCall ,originParams, returnValue):
        """
        Reacting to the fused Time with a print in a specific shape.
        responseCallbacks always have the following parameters.

        :param orignCall: The name of the orignCall
        :type orignCall: String
        :param originParams: The parameters given to the orignCall
        :type originParams: List or keywordDict
        :param returnValue: The returned Value from the orignCall
        :type returnValue: any
        :returns: None
        """
        print("[{}]: {}".format(self.__class__.__name__, returnValue))

    def mainLoop(self):
        """
        Sending currenct minute and second to the ListeningNode on the printMsg and fuse callback.

        :returns: Never
        """
        #Make sure the thread terminates, when reconnecting
        #otherwise onConnected will spawn another
        #and you will end up with n threads, where n is the number of connects
        while(self.shouldRun):
            now = datetime.datetime.now()
            self.publish(group="exampleGroup", topic="example", funcName="printTime", params=[now.minute, now.second])
            self.publish(group="exampleGroup", topic="example", funcName="fuseTime", params={"min":now.minute, "sec":now.second})
            time.sleep(5)

    def cleanUp(self):
        """
        Make sure the thread terminates, when reconnecting
        otherwise onConnected will spawn another
        and you will end up with n threads, where n is the number of connects
        """
        super(SendingNode, self).cleanUp()
        self.shouldRun = False
        try:
            self.thread.join()
        except AttributeError:
            pass # This only happens if onConnected was never called before - Node was never connected correctly and therefore closes the connection and calls the cleanUp


if( __name__ == "__main__" ):
    #Here you initialize your Node and run it.
    sendingNode = SendingNode() # CONNECT_HASH needs to be in .btnexusrc or environment variable CONNECT_HASH
    sendingNode.connect() # This call is blocking
