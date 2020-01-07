"""Messages that obey the blackout protocol, can use this class"""

# System imports
import json, time, copy, uuid, collections, yaml

# 3rd party imports

# end file header
__author__      = "Marc Fiedler"
__copyright__   = "Copyright (c)2017, Blackout Technologies"

class Message(object):
    """
        Protocol Message object
    """
    data = {}           # Local Data array
    valid = False       # Validation

    version = "5.0"   # Protocol version number

    def __init__(self, intent=None):
        """
            Construct, Initialize the message
        """
        self.data = {}
        self.valid = False

        if( intent != None ):
            # Create new Message
            self.data['api'] = {}
            self.data['api']['version'] = self.version
            self.data['api']['time'] = time.time()
            self.data['api']['intent'] = intent
            self.data['api']['id'] = str(uuid.uuid4())
            self.valid = True

    def loadFromJson(self, jsonData):
        """
            load from Json data
        """
        # Load existing message
        self.data = jsonData
        #self.validate() #TODO: commented out for the moment
        self.valid = True

    def loadFromJsonString(self, jsonData):
        """
            load from Json string data
        """
        # Load existing message
        self.data = yaml.safe_load(jsonData)
        # self.validate() #TODO: commented out for the moment
        self.valid = True


    def addAuthHeader(self, authType, authValue):
        """
            Add authentification header
        """
        authHeader = {}
        authHeader['type'] = authType
        authHeader['value'] = authValue

        self.data['api']['auth'] = authHeader

    def overwriteDefaultHeader(self, data):
        """
            Overwrite default behaviour. Used mostly in REST apis
        """
        self.data = data

    def validate(self):
        """
            Validate message content
        """

        protocolVersion = self.data['api']['version']
        # TODO should be fixed with semver, w/ down compatibility
        #if( protocolVersion != self.version ):
        #    # Version missmatch
        #    if( protocolVersion[0] != self.version[0]):
        #        # Major version missmatch
        #        raise Exception("Major version missmatch {} != {}".format(protocolVersion[0], self.version[0]))
        #        return
        #    else:
        #        raise Exception("Minor version missmatch")

        self.valid = True


    def stripHeader(self):
        """
            Strip the blackout protocol header from the dict
        """
        stripped = {}
        for key in self.data:
            if( key == "api" ):
                continue
            stripped[key] = self.data[key]
        return stripped

    def __getitem__(self, key):
        """
            Access item in local data storage
        """
        return self.data[key]

    def __setitem__(self, key, value):
        """
            Set local data storage
        """
        self.data[key] = value

    def getJsonContent(self, pretty=False):
        """
            Return local content as JSON string
        """
        # if( pretty ):
        #     return json.dumps(self.data, sort_keys = True, indent = 4, ensure_ascii = False)
        # else:
        #     return json.dumps(self.data)
        return json.dumps(self.data, ensure_ascii = True)
        # else:

    def info(self, text):
        print (text)

    def error(self, text):
        print (text)

    def keys(self):
        return list(self.data.keys())

    def __str__(self):
        return str(self.data)
