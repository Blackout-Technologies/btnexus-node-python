"""A post request with a callback for the response"""
# System imports

import json
import threading
import requests

# 3rd Party imports

# local imports

# end file header
__author__      = "Adrian Lubitz"
__copyright__   = "Copyright (c)2017, Blackout Technologies"

class PostRequest():
    """
    A post request with a callback for the response
    """
    def __init__(self, url, data, callback=None, headers=None):
        """
        setting up the request.

        :param url: the url to send the request to
        :type url: String
        :param data: the data which should be send
        :type data: dict
        :param callback: the callback which handles the response
        :type callback: function pointer
        """
        
        # check if slash in the end
        if not url.endswith("/"):
            url += "/"
        url += "api"

        self.url = url
        self.data = json.dumps(data)
        self.callback = callback
        self.headers = headers

    def _send(self):
        """
        sending the request and trigger the callback when response is ready - this is blocking
        """
        r = requests.post(self.url, data=self.data, headers=self.headers)
        content =json.loads(r.content)
        try:
            r.raise_for_status()
        except Exception as e:
            print (content["error"])
            raise (e)
        if self.callback:
            self.callback(r.json())

    def send(self):
        """
        sending the request in a thread and trigger the callback when response is ready
        """
        threading.Thread(target=self._send).start()


if __name__ == "__main__":
    import os
    token = os.environ["TOKEN"]
    axon = os.environ["AXON_HOST"]
    print ("URL: {}".format(axon))
    print ("Token: {}".format(token))