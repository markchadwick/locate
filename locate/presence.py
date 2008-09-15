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
        if isinstance(instance, type):
            presence_type = instance.__name__
        else:
            presence_type = instance.__class__.__name__
        return "_%s._tcp" % (presence_type)

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
    def __init__(self, monitor_class, callback):
        Thread.__init__(self)
        
        self._presence_type = BonjourPresenseDaemon.instance_to_ref(monitor_class)
        self._callback = callback
        self.running = True

    def run(self):
        browse_sd_ref = pybonjour.DNSServiceBrowse(
                            regtype=self._presence_type,
                            callBack=self._browse_event_callback)

        try:
            while self.running:
                ready = select.select([browse_sd_ref], [], [], 1)
                if browse_sd_ref in ready[0]:
                    pybonjour.DNSServiceProcessResult(browse_sd_ref)
        finally:
            browse_sd_ref.close()
            
    def stop(self):
        self.running = False
        

    def _browse_event_callback(self, sd_ref, flags, interface_index, error_code,
                                service_name, reg_type, reply_domain):
                                
        if error_code != pybonjour.kDNSServiceErr_NoError:
            return

        if not (flags & pybonjour.kDNSServiceFlagsAdd):
            print '*' * 60
            print 'Service removed'
            print service_name
            print reg_type
            print reply_domain
            print '*' * 60
            return

        resolve_sd_ref = pybonjour.DNSServiceResolve(
                            0,
                            interface_index,
                            service_name,
                            reg_type,
                            reply_domain,
                            self._service_registered_callback)

        self.target_resolved = False
        try:
            while not self.target_resolved:
                ready = select.select([resolve_sd_ref], [], [], 1)
                if resolve_sd_ref in ready[0]:
                    pybonjour.DNSServiceProcessResult(resolve_sd_ref)
        finally:
            self.target_resolved = False
            resolve_sd_ref.close()
    def _service_registered_callback(self, sd_ref, flags, interface_index,
                                    error_code, fullname, hosttarget, port,
                                    txt_record):
                                    
        if error_code == pybonjour.kDNSServiceErr_NoError:
            self.target_resolved = True
            self._callback(hosttarget, port)
        