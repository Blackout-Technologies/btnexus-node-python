"""
Example for a Hook that responds with Hello World
"""
# System imports

# 3rd party imports
from btHook import Hook

# local imports

class TestHook(Hook):
    """
    Example for a Hook that responds with Hello World
    """
    def onReady(self, **kwargs):
        """
        set up the API
        """
        print("Hook is ready")

    def onMessage(self, originalTxt, intent, language, entities, slots, branchName, peer):
        """
        respond
        """
        message = "Hello world from my TestHook"
        self.say(peer, message)

if __name__ == "__main__":
    h = TestHook() # setup the .btnexusrc in your project

