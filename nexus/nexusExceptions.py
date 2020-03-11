""" NexusExceptions are implemented here"""

class NexusNotConnectedException(Exception):
    """ NexusNotConnectedException is raised whenever someone trys to publish stuff although the nexus is not connected yet"""
    def __init__(self):
        super(NexusNotConnectedException, self).__init__("Not connected to the nexus! To publish a message you need to be connected first!")

class NoCallbackFoundException(Exception):
    """ There is no Callback on this group/topic/funcName"""
    def __init__(self, e):
        """
        This can adds a specific Text to the exception, why there is no callback.
        """
        super(NoCallbackFoundException, self).__init__(str(e))

class NoProtocolException(Exception):
    """ There is no protocol for the host"""
    def __init__(self, host):
        super(NoProtocolException, self).__init__("No protocol given for host {}. You must provide http or https as protocol".format(host))

class RequestError(Exception):
    """ The Request couldnt be handled """
    def __init__(self, originalParams, exception, content):
        super(RequestError, self).__init__("Request {} caused {} with {}".format(originalParams, exception, content))