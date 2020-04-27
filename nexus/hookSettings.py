'''Description of the module'''
# System imports
import json
# 3rd Party imports
# local imports
# end file header
__author__      = 'Adrian Lubitz'
__copyright__   = 'Copyright (c)2017, Blackout Technologies'

class HookSettings(dict):
    """
    A dict, that triggers a callback if update() is called and the content changes
    """
    def __init__(self, jsonFilePath, callback):
        self.callback = callback
        with open(jsonFilePath) as jsonFile:
            data = json.load(jsonFile)
            settings = {}
            for setting in data:
                settings[setting] = setting["default"]
        super(HookSettings, self).__init__(settings)
    
    def update(self, dict):
        if dict != self:
            super(HookSettings, self).update(dict)
            self.callback(self)

if __name__ == '__main__':
    pass