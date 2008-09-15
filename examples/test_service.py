#!/usr/bin/evn python

import sys
import os
import logging
import time
from threading import Thread

import locate

class MyService(Thread):
    def __init__(self, port):
        Thread.__init__(self)
        self.log = logging.getLogger(self.__class__.__name__)
                
        self.port = port
        self.dummy_services = []
        self.running = True

        locate.register(self, port)
        
        locate.listen_for_register(DummyService, self._dummy_service_registered)
        locate.listen_for_unregister(DummyService, self._dummy_service_unregistered)

    def run(self):
        while self.running:
            self.log.debug("MyService: Dummy Services: %s" % str(self.dummy_services))
            time.sleep(1)

    def stop(self):
        locate.unregister(self)
        self.running = False
        
    def _dummy_service_registered(self, *args, **kwds):
        self.log.info("Dummy Service Added: %s - %s" % (str(args), str(kwds)))
        
    def _dummy_service_unregistered(self, *args, **kwds):
        self.log.info("Dummy Service Removed: %s - %s" % (str(args), str(kwds)))


class DummyService(Thread):
    def __init__(self, port):
        Thread.__init__(self)
        self.log = logging.getLogger(self.__class__.__name__)
        
        self.port = port
        self.running = True
        locate.register(self, port)

    def run(self):
        while self.running:
            self.log.debug("Running")
            time.sleep(0.5)
            
    def stop(self):
        self.log.debug("Stopping")
        self.running = False

def main(args=sys.argv):
    logging.basicConfig(level=logging.DEBUG)

    my_service    = MyService(1234)
    dummy_service = DummyService(1235)

    my_service.start()
    time.sleep(1)
    dummy_service.start()
    time.sleep(1)
    dummy_service.stop()
    time.sleep(1)
    my_service.stop()

if __name__ == '__main__':
    sys.exit(main(sys.argv))