'''Description of the module'''
# System imports
import json
import random
import warnings
# 3rd Party imports
# local imports
# end file header
__author__      = 'Adrian Lubitz'
__copyright__   = 'Copyright (c)2017, Blackout Technologies'

class BTCaptions(dict):
    def __init__(self, jsonFilePath):
        with open(jsonFilePath) as jsonFile:
            # TODO: could implement some checks for format - every language needs to have the same keys -> KeyError
            captions = json.load(jsonFile)
            keyLists = []
            for language in captions:
                if language != "settings":
                    keyLists.append(captions[language].keys())
            union = set().union(*keyLists)
            intersection = set(keyLists[0]).intersection(*keyLists)
            if union != intersection:
                raise KeyError("Captions need to have the same keys for every language! Check your captions file.")
            self.update(captions)
    def getPhrase(self, lang, key):
        """
        Returns a phrase from the captions file. If a list of phrases is given in the captions file one is chosen randomly. If only a String is given it returns this. 

        :param lang: the requested language
        :type lang: String
        :param key: key for a specific phrase
        :type key: String
        """
        if isinstance(self[lang][key], str):
            warnings.warn("You are using a deprecated version of captions file. All phrases should be in an array!", DeprecationWarning)
            return self[lang][key]
        elif isinstance(self[lang][key], list):
            return random.choice(self[lang][key])



if __name__ == '__main__':
    a = BTCaptions('../examples/captions.json')
    print('Captions: {}'.format(a))
    print("a['en-US']['sayHi']: {}".format(a['en-US']['sayHi']))
    print("a.getPhrase('en-US', 'sayHi') : {}".format(a.getPhrase('en-US', 'sayHi')))
    print("a.getPhrase('de-DE', 'sayHi') : {}".format(a.getPhrase('de-DE', 'sayHi')))    