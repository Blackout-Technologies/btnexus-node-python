"""Example for a Node that sends out messages"""
# System imports
from threading import Thread
import datetime
import time

# 3rd party imports
from btNode import Node

# local imports

class SendingNode(Node):
    """
    This Node shows how to implement an active Node which sends different Messages
    """
    def nodeConnected(self):
        """
        This will be executed after a the Node is succesfully connected to the btNexus
        Here you need to subscribe and set everything else up.

        :returns: None
        """
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
        while(True):
            now = datetime.datetime.now()
            self.publish(group="exampleGroup", topic="example", funcName="printTime", params=[now.minute, now.second])
            self.publish(group="exampleGroup", topic="example", funcName="fuseTime", params={"min":now.minute, "sec":now.second})
            time.sleep(5)

if( __name__ == "__main__" ):
    #Here you initialize your Node and run it.
    sendingNode = SendingNode()
    sendingNode.run() # This call is blocking
