"""Example for a Node that listens to incoming messages"""
# System imports
import os
# 3rd party imports
from btNode import Node

# local imports

class ListeningNode(Node):
    """
    This Node shows how to subscribe to different Messages
    """
    def onConnected(self):
        """
        This will be executed after a the Node is succesfully connected to the btNexus
        Here you need to subscribe and set everything else up.

        :returns: None
        """
        self.subscribe(group="exampleGroup",topic="example", callback=self.printTime)
        self.subscribe(group="exampleGroup",topic="example", callback=self.fuseTime)

    def printTime(self, min, sec):
        """
        printing the time for the purpose of this example

        :param min: The minutes
        :type min: int
        :param sec: The seconds
        :type sec: int
        :returns: None
        """
        print("[{}]: {} || {}".format(self.__class__.__name__, min, sec))

    def fuseTime(self, min, sec):
        """
        Fusing the time into one String for the purpose of this example

        :param min: The minutes
        :type min: int
        :param sec: The seconds
        :type sec: int
        :returns: The fused time as a String
        """
        fuse = str(min) + ":" + str(sec) #Do your calculations
        return fuse


if( __name__ == "__main__" ):
    #Here you initialize your Node and run it.
    listeningNode = ListeningNode() # CONNECT_HASH needs to be in .btnexusrc or environment variable CONNECT_HASH
    listeningNode.connect() # This call is blocking
