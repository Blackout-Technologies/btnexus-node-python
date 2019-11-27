'''Description of the module'''
# System imports
# 3rd Party imports
import socketio
# local imports
# end file header
__author__      = 'Adrian Lubitz'
__copyright__   = 'Copyright (c)2017, Blackout Technologies'


# standard Python
sio = socketio.Client()

@sio.event
def connect():
    print("I'm connected!")

sio.connect('ws://zamojin.blackout.ai:9100/')
sio.wait()