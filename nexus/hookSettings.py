'''Description of the module'''
# System imports
# 3rd Party imports
# local imports
# end file header
__author__      = 'Adrian Lubitz'
__copyright__   = 'Copyright (c)2017, Blackout Technologies'

class HookSettings(dict):
    """
    A dict, that triggers a callback if update() is called and the content changes
    """
    def __init__(self, callback):
        self.callback = callback
        super(HookSettings, self).__init__()
    
    def update(self, dict):
        if dict != self:
            super(HookSettings, self).update(dict)
            self.callback(self)

if __name__ == '__main__':
    a = HookSettings(print)
    print(a)
    a.update({"a":["b"]})
    l = ["b"]
    a.update({"a":l})
    a.update(a)
    print(a)