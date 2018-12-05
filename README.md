# Blackout Nexus Node for Python

![Blackout logo](https://www.blackout.ai/wp-content/uploads/2018/08/logo.png)

|||
|---|---|
|Author|Adrian Lubitz|
|Email|dev@blackout.ai|
|Latest stable version|3.0.0|
|Required Axon versions| >= 3.0.0|
|State|`Stable`|


# Introduction

The `nexus` by Blackout Technologies is a platform to create Digital Assistants and to connect them via the internet to multiple platforms. Those platforms can be websites, apps or even robots. The `nexus` consists of two major parts, first being the `btNexus` and second the nexusUi. The `btNexus` is the network that connects the A.I. with the nexusUi and the chosen interfaces. The nexusUi is the user interface, that allows the user to create their own A.I.-based Digital Assistant. Those Digital Assistants can be anything, support chatbots or even robot personalities.   
Every user has one or multiple nexusUi instances or short nexus instances, which means, it's their workspace. One nexusUi / nexus instance can host multiple personalities.

Every part of the `btNexus` is a Node. These Nodes can react on messages and send messages through the `btNexus`. To understand how Nodes work the following key concepts need to be clear.

## Nodes
Nodes are essentially little programs. It is not important in which language these programs are implemented.
More important is that they share `Messages` between them in certain `Groups` and `Topics`.
So every node has its very unique purpose. It reacts on `Messages` with a `Callback` which is subscribed to a `Group` and a `Topic`
and also sends `Messages` to the same and/or other `Group` and `Topic` to inform other `Nodes`, what is happening.

## Messages
`Messages` are the media of communication between `Nodes`.
A `Message` contains a name for a `Callback` and the corresponding parameters.
A `Message` is send on a specific `Group` and `Topic`, so only `Callbacks` that subscribed to this `Group` and `Topic` will react.

## Callbacks
`Callbacks` are functions which serves as the reaction to a `Message` on a specific `Topic` in a specific `Group`.
Every `Callback` returns a `Message` to the `btNexus` with the name of the origin `Callback` + `_response`. So a `Node` can also subscribe to the response of the `Message` send out.

## Topics & Groups
`Topics` and `Groups` help to organize `Messages`. A `Callback` can only be mapped to one `Group` and  `Topic`.


# Prerequisites

* Python installed
* Owner of a btNexus instance or a btNexus account
* Set the environment variables `AXON_HOST`, `TOKEN` and if you want `NEXUS_DEBUG`

# Install btnexus-node-python
## easiest solution

Right now you need to clone/download the repository and install it from the folder.
We are planing to upload the `btnexus-node-python` to PyPi.
We recommend using Anaconda (https://www.anaconda.com/), because you wont need `sudo` and you can simply use virtual environments.
If you are using Anaconda or any other virtual environments and pip(**recommended**) you can simply
```
pip install btnexus-node-python/
```

## workaround
If you cannot use pip for any reason, do the following:

Install the Python modules with
```
sudo easy_install .
```

If you are not `sudo` use the install.sh to install the modules to your home directory
```
./install.sh
```

If you can not use pip you also have to install six and pyyaml manually.

# Example Nodes
Following you will see an example of a Node which sends out the current minute
and second every five seconds.

```python
""""Example for a Node that sends out messages"""
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
        """
        print("[{}]: {}".format(self.__class__.__name__, returnValue))

    def mainLoop(self):
        """
        Sending currenct minute and second to the ListeningNode on the printMsg and fuse callback.
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
```
The ListeningNode and all further examples can be seen in the examples folder.


# Implement your own Node
First you need know the purpose of your Node.
Nodes should be small and serve only one purpose.
To implement your own Node you need to inherit from the Node class,
implement your callbacks and if you are actively doing something implement your
Threads, that for example read in sensor data. See the examples to get started ;)
Keep in mind, that you need to set the environment variables `AXON_HOST`, `TOKEN` and if you want `NEXUS_DEBUG`. If you are using Anaconda you can integrate those into your virtual environment(https://conda.io/docs/user-guide/tasks/manage-environments.html#saving-environment-variables).
