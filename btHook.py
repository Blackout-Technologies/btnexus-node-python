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

class Hook(Node):
    """
    Blackout Nexus hook. Base class for all hooks
    """
    def __init__(self, connectHash = None):
        """
        Constructor for the hook.
        extracting all important infos from the connectHash
        (either given via environment variable as parameter, CONNECT_HASH or in the .btnexusrc)
        """
        #get connectHash
        if connectHash == None:
            if "CONNECT_HASH" in os.environ:
                connectHash = os.environ["CONNECT_HASH"]
            else:
                with open(".btnexusrc") as btnexusrc:
                    connectHash = btnexusrc.read()

        #extract config
        self.config = json.loads(base64.b64decode(connectHash))

        #call super constructor with axon and token set
        token = self.config["token"]
        host = urlsplit(self.config["host"]).netloc
        if not host:
            host = self.config["host"] # backwardscompatibility
        print("HOST: {}".format(host))
        print("TOKEN: {}".format(token))
        super(Hook, self).__init__(token, host)
        self.connect()


    def onConnected(self):
        """
        Setup all Callbacks
        """

        # Join complete
        #TODO: does it make sense to put group and topic to the same name? - would suggest group as 'hook' and topic as self.config["id"]
        self.subscribe(self.config["id"], 'hookChat', self._onMessage, "onMessage") 

        #TODO: why?
        self.subscribe(self.config["id"], self.config["id"], self.state)
        self.readyState = "ready"
        self.state()
        self.onReady()



    def state(self):
        self.publish(self.config["id"], self.config["id"], 'state', {
            'hookId': self.config["id"],
            'state': self.readyState
        })

    def _onMessage(self, **kwargs):#originalTxt, intent, language, entities, slots, branchName, originalMsg):
        """
        React on a message forwarded to the hook.
        TODO: what are captions?

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
        :param originalMsg: The original message sent from the btNexus (TODO: is it?)
        :type originalMsg: Message(TODO: is it?)
        """
        # print("1. {}".format(originalTxt))
        # print("2. {}".format(intent))
        # print("3. {}".format(language))
        # print("4. {}".format(entities))
        # print("5. {}".format(slots))
        # print("6. {}".format(branchName))
        # print("7. {}".format(originalMsg))

        self.onMessage(originalTxt=kwargs["text"]["original"], 
                        intent=kwargs["intent"], 
                        language=kwargs["language"], 
                        entities=kwargs["entities"], 
                        slots=kwargs["slots"], 
                        branchName=kwargs["branch"]["name"], 
                        peer=kwargs)

    def onMessage(self, originalTxt, intent, language, entities, slots, branchName, peer):
        """
        Overload for your custum hook! - it needs to trigger say
        """
        pass
        self.say(peer, originalTxt + " SELBER!")#TODO:remove!

    def say(self, peer, message):
        """
        publishes the hooks response.

        :param originalTxt: the original text
        :type originalTxt: String
        """
        print("say: {}".format(message))
        peer["message"] = message
        self.publish(peer["personalityId"], 'chat', 'hookResponse', peer)

    #     peer.info.message = message;
    #     this.node.publish(peer.info.personalityId, 'chat', {
    #         hookResponse: peer.info
    #     });
    # }




    def onReady(self):
        """
        Do whatever the hook should do
        """
        pass

if __name__ == "__main__":
    h = Hook()
    print (h.config)#TODO: remove
