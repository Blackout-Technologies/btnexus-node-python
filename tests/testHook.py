'''Tests for the Hook'''
# System imports
import unittest
import time, os
import logging
import inspect



# 3rd Party imports
from btHook import Hook
import timeout_decorator

# local imports
from reconnectUtils import ShakyInternet

# end file header
__author__      = 'Adrian Lubitz'
__copyright__   = 'Copyright (c)2017, Blackout Technologies'

moduleName = 'TESTS'
logger = logging.getLogger(moduleName)
logger.setLevel(Hook.NEXUSINFO)
# create file handler which logs even debug messages
fh = logging.StreamHandler()
fh.setLevel(Hook.NEXUSINFO)
formatter = logging.Formatter('%(asctime)s - [%(levelname)s]: %(message)s') 
fh.setFormatter(formatter)
logger.addHandler(fh)

class ExampleHook(Hook):
    '''
    Hook for testing
    '''
    def onConnected(self):
        self.disconnect() # disconnects after successfully connecting

class TestHook(unittest.TestCase):
    '''Tests for the Hook'''
    shakyInternet = ShakyInternet()


    def setUp(self):
        self.shakyInternet.start()
        #if file exists use it otherwise use envVar from CI/CD as file and if nothing raise exception
        local_rc = os.path.join(os.path.dirname(os.path.realpath(os.path.abspath(inspect.getfile(self.__class__)))), '.btnexusrc_hook')
        if os.path.isfile(local_rc):
            print("using local btnexusrc file")
            self.rc_path = local_rc
        elif "HOOKRC" in os.environ:
            print("using env var HOOKRC")
            self.rc_path = os.environ['HOOKRC']
        else:
            raise Exception("No valid btnexusrc")

    def tearDown(self):
        self.shakyInternet.stop()
        time.sleep(2)
    
    @timeout_decorator.timeout(120, use_signals=False)
    def test_connect(self):
        '''
        test to initialize a Hook
        '''
        
        print('TESTING THE HOOK')
        h = ExampleHook(packagePath='packageHook.json', rcPath=self.rc_path, logger=logger) #TODO: Need the correct .btnexusrc here - the CONNECTHASH in env is for TestIntegration
        h.connect()
        # TODO: nothing here until I have a hook for testing in dev5
        
if __name__ == "__main__":
    unittest.main()
