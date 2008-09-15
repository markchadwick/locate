import pybonjour
import select
import logging
from threading import Thread

class BonjourPresenseDaemon(Thread):
    def __init__(self, instance, port, callback=None, timeout=1, name='Locate'):
        Thread.__init__(self)
        
        self.instance = instance
        self.port = port
        self.callback = callback
        self.timeout = timeout
        
        self.name = name
        self.reg_type = self.__class__.instance_to_ref(instance)
        
        self.running = True

    @classmethod
    def instance_to_ref(self, instance):
        return "_%s._tcp" % (instance.__class__.__name__)

    def run(self):
        sd_ref = pybonjour.DNSServiceRegister(
                    name=self.name,
                    regtype=self.reg_type,
                    port=self.port,
                    callBack=self._service_registered_callback)
        try:
            while self.running:
                ready = select.select([sd_ref], [], [], self.timeout)
                if sd_ref in ready[0]:
                    pybonjour.DNSServiceProcessResult(sd_ref)
        finally:
            sd_ref.close()

    def stop(self):
        self.running = False
        
    def _service_registered_callback(self, *args, **kwds):
        if self.callback is not None:
            self.callback(*args, **kwds)

class BonjourMonitorDaemon(Thread):
    pass
    